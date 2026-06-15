"""Offline replay parity metrics (Phase 35)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set


def _top3_factors(prediction: Dict[str, Any], explanation: Dict[str, Any]) -> List[str]:
    xai = prediction.get("slice_domain_xai") or {}
    factors = xai.get("top_factors") or explanation.get("top_factors") or []
    out: List[str] = []
    for item in factors[:3]:
        if isinstance(item, dict):
            out.append(str(item.get("factor") or item.get("name") or item))
        else:
            out.append(str(item))
    return out


def jaccard(a: List[str], b: List[str]) -> float:
    sa: Set[str] = set(a)
    sb: Set[str] = set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def compute_vector_parity(
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
    a_risk = float(active_prediction.get("risk_score") or 0.0)
    c_risk = float(candidate_prediction.get("risk_score") or 0.0)
    a_conf = float(
        active_prediction.get("confidence_score")
        or active_prediction.get("classifier_confidence")
        or active_prediction.get("confidence")
        or 0.0
    )
    c_conf = float(
        candidate_prediction.get("confidence_score")
        or candidate_prediction.get("classifier_confidence")
        or candidate_prediction.get("confidence")
        or 0.0
    )
    a_dom = (active_prediction.get("slice_domain_xai") or {}).get("dominant_domain") or active_explanation.get("dominant_domain")
    c_dom = (candidate_prediction.get("slice_domain_xai") or {}).get("dominant_domain") or candidate_explanation.get("dominant_domain")
    a_top3 = _top3_factors(active_prediction, active_explanation)
    c_top3 = _top3_factors(candidate_prediction, candidate_explanation)

    risk_delta = abs(a_risk - c_risk)
    conf_delta = abs(a_conf - c_conf)
    top3_jaccard = jaccard(a_top3, c_top3)
    dominant_domain_match = a_dom == c_dom

    return {
        "vector_id": vector_id,
        "prediction_parity": {
            "active_risk_score": a_risk,
            "candidate_risk_score": c_risk,
            "abs_delta": risk_delta,
        },
        "confidence_parity": {
            "active_confidence": a_conf,
            "candidate_confidence": c_conf,
            "abs_delta": conf_delta,
        },
        "top3_factor_parity": {
            "active_top3": a_top3,
            "candidate_top3": c_top3,
            "jaccard": top3_jaccard,
        },
        "dominant_domain_parity": {
            "active": a_dom,
            "candidate": c_dom,
            "match": dominant_domain_match,
        },
        "latency_ms": {
            "active": active_latency_ms,
            "candidate": candidate_latency_ms,
        },
        "telemetry_consistency": telemetry_gate_passed,
        "execution_success": True,
    }


def aggregate_parity_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not results:
        return {"vector_count": 0, "execution_success_rate": 0.0}

    n = len(results)
    risk_deltas = [r["prediction_parity"]["abs_delta"] for r in results]
    conf_deltas = [r["confidence_parity"]["abs_delta"] for r in results]
    top3_j = [r["top3_factor_parity"]["jaccard"] for r in results]
    dom_match = sum(1 for r in results if r["dominant_domain_parity"]["match"])
    tel_ok = sum(1 for r in results if r["telemetry_consistency"])
    lat_a = [r["latency_ms"]["active"] for r in results if r["latency_ms"]["active"] is not None]
    lat_c = [r["latency_ms"]["candidate"] for r in results if r["latency_ms"]["candidate"] is not None]

    return {
        "vector_count": n,
        "execution_success_rate": 1.0,
        "telemetry_consistency_rate": tel_ok / n,
        "prediction_parity": {
            "mean_abs_delta": sum(risk_deltas) / n,
            "p99_abs_delta": sorted(risk_deltas)[max(0, int(n * 0.99) - 1)],
            "parity_rate": sum(1 for d in risk_deltas if d <= 0.05) / n,
        },
        "confidence_parity": {
            "mean_abs_delta": sum(conf_deltas) / n,
        },
        "top3_factor_parity": {
            "mean_jaccard": sum(top3_j) / n,
        },
        "dominant_domain_parity": {
            "match_rate": dom_match / n,
        },
        "latency_ms": {
            "active_mean": sum(lat_a) / len(lat_a) if lat_a else None,
            "candidate_mean": sum(lat_c) / len(lat_c) if lat_c else None,
        },
    }
