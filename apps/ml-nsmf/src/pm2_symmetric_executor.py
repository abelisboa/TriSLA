"""PM-2 symmetric classifier validation executor (Phase 39).

Both ACTIVE and CANDIDATE paths load the same classifier (MR-003) and apply
v7_calibrated risk authority — offline batch only, not wired to production.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dual_load_config import DualLoadConfig
from model_loader import resolve_active_bundle, resolve_candidate_bundle, validate_bundle
from offline_replay_config import OfflineReplayConfig
from prediction_pipeline import build_active_prediction
from predictor import RiskPredictor
from replay_parity import aggregate_parity_results, compute_vector_parity, jaccard
from replay_snapshot import build_replay_snapshot, metrics_from_snapshot
from replay_telemetry_gate import run_telemetry_consistency_gate

logger = logging.getLogger(__name__)


class PM2ValidationError(RuntimeError):
    """Raised when PM-2 symmetric validation fails."""


def _load_vectors(golden_vectors_path: str, max_vectors: int = 0) -> List[Dict[str, Any]]:
    with Path(golden_vectors_path).open(encoding="utf-8") as f:
        doc = json.load(f)
    vectors = list(doc.get("vectors") or [])
    if max_vectors > 0:
        vectors = vectors[:max_vectors]
    return vectors


def build_symmetric_predictors(
    dual_config: DualLoadConfig,
) -> Tuple[RiskPredictor, RiskPredictor, str]:
    """Build ACTIVE and CANDIDATE predictors both with classifier loaded (PM-2)."""
    active_spec = resolve_active_bundle(dual_config)
    cand_spec = resolve_candidate_bundle(dual_config)
    active_val = validate_bundle(active_spec)
    cand_val = validate_bundle(cand_spec)
    if not active_val.valid:
        raise PM2ValidationError(f"ACTIVE invalid: {active_val.errors}")
    if not cand_val.valid:
        raise PM2ValidationError(f"CANDIDATE invalid: {cand_val.errors}")
    if not cand_spec.classifier_path:
        raise PM2ValidationError("CANDIDATE classifier path required for PM-2")

    classifier_path = cand_spec.classifier_path
    active = RiskPredictor(
        model_path=active_spec.model_path,
        scaler_path=active_spec.scaler_path,
        pin_paths=True,
        role="active",
        load_classifier=True,
        classifier_path=classifier_path,
    )
    candidate = RiskPredictor(
        model_path=cand_spec.model_path,
        scaler_path=cand_spec.scaler_path,
        pin_paths=True,
        role="candidate",
        load_classifier=True,
        classifier_path=classifier_path,
    )
    return active, candidate, classifier_path


def _authority_check(prediction: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "classifier_loaded": bool(prediction.get("classifier_loaded")),
        "risk_formula": prediction.get("risk_formula"),
        "predicted_decision_class": prediction.get("predicted_decision_class"),
    }


def _probability_parity(
    active_probs: Dict[str, float],
    candidate_probs: Dict[str, float],
) -> Dict[str, Any]:
    classes = sorted(set(active_probs) | set(candidate_probs))
    deltas = {c: abs(float(active_probs.get(c, 0)) - float(candidate_probs.get(c, 0))) for c in classes}
    l1 = sum(deltas.values())
    return {
        "active_probabilities": active_probs,
        "candidate_probabilities": candidate_probs,
        "per_class_abs_delta": deltas,
        "l1_distance": l1,
        "max_abs_delta": max(deltas.values()) if deltas else 0.0,
    }


def compute_pm2_vector_parity(
    *,
    vector_id: str,
    active_prediction: Dict[str, Any],
    active_explanation: Dict[str, Any],
    candidate_prediction: Dict[str, Any],
    candidate_explanation: Dict[str, Any],
    active_latency_ms: Optional[float],
    candidate_latency_ms: Optional[float],
    telemetry_gate_passed: bool,
) -> Dict[str, Any]:
    base = compute_vector_parity(
        vector_id=vector_id,
        active_prediction=active_prediction,
        active_explanation=active_explanation,
        candidate_prediction=candidate_prediction,
        candidate_explanation=candidate_explanation,
        active_latency_ms=active_latency_ms,
        candidate_latency_ms=candidate_latency_ms,
        telemetry_gate_passed=telemetry_gate_passed,
    )
    a_probs = active_prediction.get("class_probabilities") or {}
    c_probs = candidate_prediction.get("class_probabilities") or {}
    a_class = active_prediction.get("predicted_decision_class")
    c_class = candidate_prediction.get("predicted_decision_class")

    base["pm2"] = {
        "authority": {
            "active": _authority_check(active_prediction),
            "candidate": _authority_check(candidate_prediction),
            "symmetric_classifier": (
                active_prediction.get("classifier_loaded")
                and candidate_prediction.get("classifier_loaded")
            ),
        },
        "probability_parity": _probability_parity(a_probs, c_probs),
        "decision_class_parity": {
            "active": a_class,
            "candidate": c_class,
            "match": a_class == c_class,
        },
        "confidence_parity_classifier": {
            "active": float(active_prediction.get("confidence_score") or 0),
            "candidate": float(candidate_prediction.get("confidence_score") or 0),
            "abs_delta": abs(
                float(active_prediction.get("confidence_score") or 0)
                - float(candidate_prediction.get("confidence_score") or 0)
            ),
        },
    }
    return base


def aggregate_pm2_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    base = aggregate_parity_results(results)
    if not results:
        return {**base, "pm2": {"vector_count": 0}}

    n = len(results)
    prob_l1 = [r["pm2"]["probability_parity"]["l1_distance"] for r in results]
    prob_max = [r["pm2"]["probability_parity"]["max_abs_delta"] for r in results]
    class_match = sum(1 for r in results if r["pm2"]["decision_class_parity"]["match"])
    conf_deltas = [r["pm2"]["confidence_parity_classifier"]["abs_delta"] for r in results]
    sym_ok = sum(
        1 for r in results if r["pm2"]["authority"]["symmetric_classifier"]
    )
    per_class: Dict[str, List[float]] = {}
    for r in results:
        for cls, delta in r["pm2"]["probability_parity"]["per_class_abs_delta"].items():
            per_class.setdefault(cls, []).append(delta)

    thresholds = {
        "risk_mean_abs_delta_max": 0.05,
        "risk_parity_rate_min": 0.99,
        "confidence_mean_abs_delta_max": 0.10,
        "decision_class_agreement_min": 0.99,
        "probability_l1_mean_max": 0.01,
    }

    risk_mean = base["prediction_parity"]["mean_abs_delta"]
    risk_parity = base["prediction_parity"]["parity_rate"]
    conf_mean = sum(conf_deltas) / n
    class_rate = class_match / n
    prob_l1_mean = sum(prob_l1) / n

    gates = {
        "PM2-1_authority_symmetric": sym_ok == n,
        "PM2-2_probability_stability": prob_l1_mean <= thresholds["probability_l1_mean_max"],
        "PM2-3_class_consistency": class_rate >= thresholds["decision_class_agreement_min"],
        "PM2-4_confidence_consistency": conf_mean <= thresholds["confidence_mean_abs_delta_max"],
        "PM2-5_risk_parity": risk_parity >= thresholds["risk_parity_rate_min"]
        and risk_mean <= thresholds["risk_mean_abs_delta_max"],
        "PM2-6_explainability": (
            base["dominant_domain_parity"]["match_rate"] >= 0.95
            and base["top3_factor_parity"]["mean_jaccard"] >= 0.70
        ),
    }

    base["pm2"] = {
        "parity_method": "PM-2",
        "symmetric_classifier_loaded": sym_ok == n,
        "authority_validation_rate": sym_ok / n,
        "probability_parity": {
            "l1_mean": prob_l1_mean,
            "l1_p99": sorted(prob_l1)[max(0, int(n * 0.99) - 1)],
            "max_delta_mean": sum(prob_max) / n,
            "per_class_mean_delta": {k: sum(v) / len(v) for k, v in per_class.items()},
        },
        "decision_class_agreement_rate": class_rate,
        "confidence_classifier_mean_abs_delta": conf_mean,
        "thresholds": thresholds,
        "gates": gates,
        "gates_pass_count": sum(1 for v in gates.values() if v),
        "gates_total": len(gates),
    }
    return base


def execute_pm2_vector(
    *,
    active_predictor: RiskPredictor,
    candidate_predictor: RiskPredictor,
    vector: Dict[str, Any],
    run_id: str,
    golden_artifact_id: str = "golden_vectors_v1",
) -> Dict[str, Any]:
    vector_id = vector["vector_id"]
    metrics = dict(vector.get("metrics") or {})
    snapshot = build_replay_snapshot(
        vector_id=vector_id,
        metrics=metrics,
        run_id=run_id,
        golden_artifact_id=golden_artifact_id,
        origin=vector.get("origin"),
    )
    shared_metrics = metrics_from_snapshot(snapshot)
    gate = run_telemetry_consistency_gate(snapshot, snapshot)
    if not gate.passed:
        raise PM2ValidationError(f"telemetry gate failed for {vector_id}: {gate.mismatches}")

    t0 = time.perf_counter()
    active_pred, active_expl, _ = build_active_prediction(active_predictor, shared_metrics)
    active_ms = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    cand_pred, cand_expl, _ = build_active_prediction(candidate_predictor, shared_metrics)
    cand_ms = (time.perf_counter() - t1) * 1000.0

    parity = compute_pm2_vector_parity(
        vector_id=vector_id,
        active_prediction=active_pred,
        active_explanation=active_expl,
        candidate_prediction=cand_pred,
        candidate_explanation=cand_expl,
        active_latency_ms=active_ms,
        candidate_latency_ms=cand_ms,
        telemetry_gate_passed=gate.passed,
    )

    return {
        "vector_id": vector_id,
        "slice_type": vector.get("slice_type"),
        "parity_method": "PM-2",
        "snapshot": {
            "snapshot_id": snapshot["snapshot_id"],
            "snapshot_checksum": snapshot["snapshot_checksum"],
        },
        "telemetry_gate": gate.to_dict(),
        "active": {
            "bundle_role": "ACTIVE",
            "prediction": active_pred,
            "explanation": active_expl,
            "latency_ms": active_ms,
        },
        "candidate": {
            "bundle_role": "CANDIDATE",
            "prediction": cand_pred,
            "explanation": cand_expl,
            "latency_ms": cand_ms,
        },
        "parity": parity,
        "success": True,
    }


def execute_pm2_validation(
    config: OfflineReplayConfig,
    dual_config: Optional[DualLoadConfig] = None,
) -> Dict[str, Any]:
    """Run PM-2 symmetric classifier validation over golden vectors."""
    dual = (dual_config or DualLoadConfig.from_env()).dev_paths_if_missing()
    dual = DualLoadConfig(
        dual_load_enabled=True,
        active_model_path=dual.active_model_path,
        active_scaler_path=dual.active_scaler_path,
        candidate_bundle_id=dual.candidate_bundle_id,
        candidate_root=dual.candidate_root,
        golden_vectors_path=dual.golden_vectors_path,
        shadow_validation_enabled=False,
    )

    active_spec = resolve_active_bundle(dual)
    cand_spec = resolve_candidate_bundle(dual)
    active_predictor, candidate_predictor, classifier_path = build_symmetric_predictors(dual)

    vectors = _load_vectors(config.golden_vectors_path, config.max_vectors)
    if not vectors:
        raise PM2ValidationError("no golden vectors for PM-2 validation")

    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    for vec in vectors:
        try:
            results.append(
                execute_pm2_vector(
                    active_predictor=active_predictor,
                    candidate_predictor=candidate_predictor,
                    vector=vec,
                    run_id=config.run_id,
                )
            )
        except Exception as exc:
            logger.exception("[PM2] vector %s failed", vec.get("vector_id"))
            errors.append({"vector_id": vec.get("vector_id"), "error": str(exc)})

    parity_summary = aggregate_pm2_results([r["parity"] for r in results])
    gate_pass_count = sum(1 for r in results if r["telemetry_gate"]["passed"])

    manifest = {
        "record_type": "pm2_symmetric_validation_manifest",
        "schema_version": "1.0.0",
        "phase": "39",
        "parity_method": "PM-2",
        "run_id": config.run_id,
        "status": "COMPLETED" if not errors else "COMPLETED_WITH_ERRORS",
        "runtime_shadow": False,
        "production_replay": False,
        "symmetric_classifier_loaded": True,
        "classifier_path": classifier_path,
        "active_bundle_id": active_spec.bundle_id,
        "candidate_bundle_id": cand_spec.bundle_id,
        "golden_artifact_id": "golden_vectors_v1",
        "vector_count_executed": len(results),
        "vector_count_failed": len(errors),
        "snapshot_window_policy": config.snapshot_window_policy,
        "telemetry_consistency_gate": {
            "gate": "REPLAY_TELEMETRY_CONSISTENCY_GATE",
            "passed": gate_pass_count == len(results) and len(results) > 0,
            "pass_count": gate_pass_count,
            "total": len(results),
        },
        "parity_summary": parity_summary,
    }

    return {
        "run_id": config.run_id,
        "execution_manifest": manifest,
        "vector_results": results,
        "errors": errors,
        "parity_summary": parity_summary,
        "classifier_path": classifier_path,
        "active_bundle_id": active_spec.bundle_id,
        "candidate_bundle_id": cand_spec.bundle_id,
    }
