"""
Quantitative decision evidence for explainability consistency (Phase Next).

Builds structured records: metric, observed, threshold, delta, rule.
Does not alter decision outcomes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_metric_evidence(
    *,
    metric: str,
    observed: Any,
    threshold: Any,
    rule: str,
    unit: Optional[str] = None,
) -> Dict[str, Any]:
    obs = _to_float(observed)
    thr = _to_float(threshold)
    delta = None
    if obs is not None and thr is not None:
        delta = round(obs - thr, 4)
    row: Dict[str, Any] = {
        "metric": metric,
        "observed": obs if obs is not None else observed,
        "threshold": thr if thr is not None else threshold,
        "delta": delta,
        "rule": rule,
    }
    if unit:
        row["unit"] = unit
    return row


def build_prb_hard_gate_evidence(
    *,
    prb_raw: Any,
    threshold_percent: float,
    rule: str,
) -> Dict[str, Any]:
    obs = _to_float(prb_raw)
    thr = float(threshold_percent)
    if obs is not None and obs <= 1.0:
        obs_display = round(obs * 100.0, 4)
    elif obs is not None:
        obs_display = round(obs, 4)
    else:
        obs_display = None
    return build_metric_evidence(
        metric="prb_utilization",
        observed=obs_display,
        threshold=thr,
        rule=rule,
        unit="%",
    )


def build_decision_evidence_from_context(
    *,
    reasoning: str,
    decision_source: Optional[str],
    xai_bundle: Optional[Dict[str, Any]],
    context: Optional[Dict[str, Any]],
    hard_prb_thresholds: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Assemble decision_evidence list for metadata / API consumers."""
    evidence: List[Dict[str, Any]] = []
    bundle = xai_bundle if isinstance(xai_bundle, dict) else {}
    rule = decision_source or reasoning or "DECISION_RULE"

    prb_raw = bundle.get("ran_prb_utilization_input")
    if prb_raw is None and isinstance(context, dict):
        ts = context.get("telemetry_snapshot") or {}
        prb_raw = (ts.get("ran") or {}).get("prb_utilization")

    thresholds = hard_prb_thresholds or bundle.get("hard_prb_thresholds") or {}
    if "PRB_HARD" in (rule or "") or "PRB_HARD" in (reasoning or ""):
        if "REJECT" in (rule or reasoning or ""):
            thr = thresholds.get("reject", 95.0)
        else:
            thr = thresholds.get("renegotiate", 85.0)
        if thr <= 1.0:
            thr = thr * 100.0
        evidence.append(
            build_prb_hard_gate_evidence(
                prb_raw=prb_raw,
                threshold_percent=float(thr),
                rule=rule if rule else reasoning,
            )
        )
        return evidence

    if prb_raw is not None:
        evidence.append(
            build_metric_evidence(
                metric="prb_utilization",
                observed=prb_raw,
                threshold=thresholds.get("renegotiate", 85.0),
                rule=rule,
                unit="%",
            )
        )
    return evidence


def attach_decision_evidence_metadata(
    metadata: Dict[str, Any],
    *,
    reasoning: str,
    xai_bundle: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Wire decision_evidence into metadata (P3 — metadata only, no decision logic)."""
    bundle = xai_bundle if isinstance(xai_bundle, dict) else metadata
    thresholds = None
    decision_source = None
    if isinstance(bundle, dict):
        raw_thr = bundle.get("hard_prb_thresholds")
        if isinstance(raw_thr, dict):
            thresholds = raw_thr
        decision_source = bundle.get("decision_source")
    metadata["decision_evidence"] = build_decision_evidence_from_context(
        reasoning=reasoning or "",
        decision_source=decision_source,
        xai_bundle=bundle if isinstance(bundle, dict) else None,
        context=context,
        hard_prb_thresholds=thresholds,
    )


def admission_compliance_from_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[float]:
    """Extract admission-time compliance (0–1 or 0–100) from decision metadata."""
    if not isinstance(metadata, dict):
        return None
    snap = metadata.get("decision_snapshot")
    if isinstance(snap, dict):
        sc = snap.get("sla_compliance")
        if isinstance(sc, (int, float)):
            v = float(sc)
            return v / 100.0 if v > 1.0 else v
    ds = metadata.get("decision_score")
    if isinstance(ds, (int, float)):
        return float(ds)
    final = (metadata.get("decision_snapshot") or {}).get("final_score")
    if isinstance(final, (int, float)):
        return float(final)
    risk = metadata.get("ran_aware_final_risk")
    if isinstance(risk, (int, float)):
        return max(0.0, 1.0 - float(risk))
    return None
