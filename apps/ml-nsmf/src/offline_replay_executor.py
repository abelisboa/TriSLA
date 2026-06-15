"""Offline replay executor — ACTIVE + CANDIDATE on shared snapshot (Phase 35)."""

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
from replay_parity import aggregate_parity_results, compute_vector_parity
from replay_snapshot import build_replay_snapshot, metrics_from_snapshot
from replay_telemetry_gate import run_telemetry_consistency_gate

logger = logging.getLogger(__name__)


class OfflineReplayExecutionError(RuntimeError):
    """Raised when offline replay execution fails."""


def _load_all_vectors(golden_vectors_path: str, max_vectors: int = 0) -> List[Dict[str, Any]]:
    path = Path(golden_vectors_path)
    with path.open(encoding="utf-8") as f:
        doc = json.load(f)
    vectors = list(doc.get("vectors") or [])
    if max_vectors > 0:
        vectors = vectors[:max_vectors]
    return vectors


def _build_predictors(dual_config: DualLoadConfig) -> Tuple[RiskPredictor, RiskPredictor]:
    active_spec = resolve_active_bundle(dual_config)
    cand_spec = resolve_candidate_bundle(dual_config)
    active_val = validate_bundle(active_spec)
    cand_val = validate_bundle(cand_spec)
    if not active_val.valid:
        raise OfflineReplayExecutionError(f"ACTIVE invalid: {active_val.errors}")
    if not cand_val.valid:
        raise OfflineReplayExecutionError(f"CANDIDATE invalid: {cand_val.errors}")

    active = RiskPredictor(
        model_path=active_spec.model_path,
        scaler_path=active_spec.scaler_path,
        pin_paths=True,
        role="active",
        load_classifier=False,
    )
    candidate = RiskPredictor(
        model_path=cand_spec.model_path,
        scaler_path=cand_spec.scaler_path,
        pin_paths=True,
        role="candidate",
        load_classifier=True,
        classifier_path=cand_spec.classifier_path,
    )
    return active, candidate


def execute_single_vector(
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
    active_snapshot = snapshot
    candidate_snapshot = snapshot

    gate = run_telemetry_consistency_gate(active_snapshot, candidate_snapshot)
    if not gate.passed:
        raise OfflineReplayExecutionError(
            f"telemetry gate failed for {vector_id}: {gate.mismatches}"
        )

    t0 = time.perf_counter()
    active_pred, active_expl, _ = build_active_prediction(active_predictor, shared_metrics)
    active_ms = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    cand_pred, cand_expl, _ = build_active_prediction(candidate_predictor, shared_metrics)
    cand_ms = (time.perf_counter() - t1) * 1000.0

    parity = compute_vector_parity(
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
        "snapshot": {
            "snapshot_id": snapshot["snapshot_id"],
            "snapshot_timestamp": snapshot["snapshot_timestamp"],
            "snapshot_checksum": snapshot["snapshot_checksum"],
            "snapshot_window": snapshot["snapshot_window"],
            "snapshot_source": snapshot["snapshot_source"],
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


def execute_offline_replay(
    config: OfflineReplayConfig,
    dual_config: Optional[DualLoadConfig] = None,
) -> Dict[str, Any]:
    """Run offline replay over golden vectors — not wired to production predict."""
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
    active_predictor, candidate_predictor = _build_predictors(dual)

    vectors = _load_all_vectors(config.golden_vectors_path, config.max_vectors)
    if not vectors:
        raise OfflineReplayExecutionError("no golden vectors to replay")

    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    for vec in vectors:
        try:
            results.append(
                execute_single_vector(
                    active_predictor=active_predictor,
                    candidate_predictor=candidate_predictor,
                    vector=vec,
                    run_id=config.run_id,
                )
            )
        except Exception as exc:
            logger.exception("[OFFLINE_REPLAY] vector %s failed", vec.get("vector_id"))
            errors.append({"vector_id": vec.get("vector_id"), "error": str(exc)})

    parity_summary = aggregate_parity_results([r["parity"] for r in results])
    gate_pass_count = sum(1 for r in results if r["telemetry_gate"]["passed"])
    gate_total = len(results)

    execution_manifest = {
        "record_type": "offline_replay_execution_manifest",
        "schema_version": "1.0.0",
        "phase": "35",
        "run_id": config.run_id,
        "status": "COMPLETED" if not errors else "COMPLETED_WITH_ERRORS",
        "replay_execution": True,
        "runtime_shadow": False,
        "active_bundle_id": active_spec.bundle_id,
        "candidate_bundle_id": cand_spec.bundle_id,
        "golden_artifact_id": "golden_vectors_v1",
        "vector_count_executed": len(results),
        "vector_count_failed": len(errors),
        "snapshot_window_policy": "[t-1s,t]",
        "snapshot_window_step": "1s",
        "telemetry_consistency_gate": {
            "gate": "REPLAY_TELEMETRY_CONSISTENCY_GATE",
            "passed": gate_pass_count == gate_total and gate_total > 0,
            "pass_count": gate_pass_count,
            "total": gate_total,
        },
        "parity_summary": parity_summary,
    }

    return {
        "run_id": config.run_id,
        "execution_manifest": execution_manifest,
        "vector_results": results,
        "errors": errors,
        "parity_summary": parity_summary,
        "active_bundle_id": active_spec.bundle_id,
        "candidate_bundle_id": cand_spec.bundle_id,
    }
