"""Runtime shadow decision simulation for PM-4 (Phase 40).

Mirrors Decision Engine threshold + classifier refinement semantics without
importing the full DE stack. Production decisions use ACTIVE path only.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

ML_REFINEMENT_CONFIDENCE = 0.6

SLICE_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "URLLC": {"accept": 0.48, "renegotiate": 0.72},
    "eMBB": {"accept": 0.56, "renegotiate": 0.78},
    "mMTC": {"accept": 0.54, "renegotiate": 0.76},
}
DEFAULT_THRESHOLDS = {"accept": 0.55, "renegotiate": 0.75}


def _slice_key(slice_type: Optional[str]) -> str:
    s = (slice_type or "eMBB").strip().upper()
    if s == "URLLC":
        return "URLLC"
    if s in ("EMBB", "EMB"):
        return "eMBB"
    if s == "MMTC":
        return "mMTC"
    return "eMBB"


def threshold_decision(risk: float, slice_type: Optional[str]) -> str:
    key = _slice_key(slice_type)
    row = SLICE_THRESHOLDS.get(key, DEFAULT_THRESHOLDS)
    t_accept = float(row["accept"])
    t_reneg = float(row["renegotiate"])
    if risk < t_accept:
        return "ACCEPT"
    if risk < t_reneg:
        return "RENEGOTIATE"
    return "REJECT"


def _risk_for_decision(prediction: Dict[str, Any]) -> float:
    adj = prediction.get("slice_adjusted_risk_score")
    if adj is not None:
        return float(adj)
    return float(prediction.get("risk_score") or 0.5)


def simulate_de_action(
    prediction: Dict[str, Any],
    *,
    slice_type: Optional[str],
    authority: str,
) -> Dict[str, Any]:
    """
    Simulate DE action from ML prediction.

    authority: 'active_production' (threshold only) | 'shadow_candidate' (hybrid)
    """
    risk = _risk_for_decision(prediction)
    threshold_action = threshold_decision(risk, slice_type)
    cls_str = prediction.get("predicted_decision_class")
    cls_conf = float(
        prediction.get("confidence_score")
        or prediction.get("classifier_confidence")
        or 0.0
    )
    classifier_loaded = bool(prediction.get("classifier_loaded"))

    if authority == "active_production":
        final_action = threshold_action
        decision_mode = "threshold"
        decision_source = "active_production_threshold"
    else:
        use_classifier = (
            classifier_loaded
            and cls_str
            and str(cls_str).strip()
            and cls_conf >= ML_REFINEMENT_CONFIDENCE
        )
        if use_classifier:
            final_action = str(cls_str).strip().upper()
            decision_mode = "classification"
            decision_source = "shadow_candidate_classifier"
        else:
            final_action = threshold_action
            decision_mode = "threshold"
            decision_source = "shadow_candidate_threshold"

    return {
        "action": final_action,
        "decision_mode": decision_mode,
        "decision_source": decision_source,
        "threshold_action": threshold_action,
        "risk_for_decision": risk,
        "classifier_loaded": classifier_loaded,
        "predicted_decision_class": cls_str,
        "classifier_confidence": cls_conf if classifier_loaded else None,
        "authority": authority,
    }


def compute_action_flip(
    active_action: Dict[str, Any],
    shadow_action: Dict[str, Any],
) -> Dict[str, Any]:
    flip = active_action["action"] != shadow_action["action"]
    return {
        "active_action": active_action["action"],
        "shadow_action": shadow_action["action"],
        "flip": flip,
        "active_decision_mode": active_action["decision_mode"],
        "shadow_decision_mode": shadow_action["decision_mode"],
    }
