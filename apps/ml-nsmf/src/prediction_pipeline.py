"""Active-model prediction pipeline — sole authority for DE responses (Phase 32)."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from predictor import RiskPredictor
from slice_risk_adjustment import compute_slice_adjusted_risk


def _risk_level_from_score(risk: float) -> str:
    if risk > 0.7:
        return "high"
    if risk > 0.4:
        return "medium"
    return "low"


def build_active_prediction(
    predictor: RiskPredictor,
    metrics: dict,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Build production prediction + explanation from ACTIVE predictor only.
    Returns (prediction, explanation, adj_bundle).
    """
    normalized = predictor.normalize(metrics)
    prediction = predictor.predict(normalized)
    clf_out = predictor.predict_decision_class(metrics)
    prediction["predicted_decision_class"] = clf_out.get("predicted_decision_class")
    prediction["classifier_confidence"] = float(clf_out.get("confidence_score") or 0.0)
    prediction["confidence_score"] = float(clf_out.get("confidence_score") or 0.0)
    prediction["classifier_loaded"] = bool(clf_out.get("classifier_loaded", False))
    class_probs = clf_out.get("class_probabilities") or {}
    prediction["class_probabilities"] = class_probs

    p_reneg = float(class_probs.get("RENEGOTIATE", 0.0))
    p_reject = float(class_probs.get("REJECT", 0.0))
    risk_multiclass = min(1.0, (0.5 * p_reneg) + (1.0 * p_reject))
    risk_from_regression = float(prediction.get("risk_score", 0.5))
    raw_risk = (
        float(risk_multiclass)
        if prediction.get("classifier_loaded")
        else risk_from_regression
    )
    prediction["risk_score_regression"] = risk_from_regression
    prediction["risk_formula"] = "v7_calibrated"
    adj_bundle = compute_slice_adjusted_risk(raw_risk, metrics)
    prediction["raw_risk_score"] = adj_bundle["raw_risk_score"]
    prediction["slice_adjusted_risk_score"] = adj_bundle["slice_adjusted_risk_score"]
    prediction["risk_score"] = raw_risk
    prediction["risk_level"] = _risk_level_from_score(adj_bundle["slice_adjusted_risk_score"])
    prediction["slice_domain_xai"] = {
        "dominant_domain": adj_bundle["dominant_domain"],
        "top_factors": adj_bundle["top_factors"],
        "domain_contribution": adj_bundle.get("domain_contribution", {}),
    }

    explanation = predictor.explain(prediction, normalized)
    explanation["raw_risk_score"] = adj_bundle["raw_risk_score"]
    explanation["slice_adjusted_risk_score"] = adj_bundle["slice_adjusted_risk_score"]
    explanation["dominant_domain"] = adj_bundle["dominant_domain"]
    explanation["top_factors"] = adj_bundle["top_factors"]
    if explanation.get("reasoning"):
        explanation["reasoning"] = (
            f"{explanation['reasoning']} | adjusted_risk={adj_bundle['slice_adjusted_risk_score']:.3f} "
            f"dominant_domain={adj_bundle['dominant_domain']}"
        )

    return prediction, explanation, adj_bundle


def format_predict_response(prediction: Dict[str, Any], explanation: Dict[str, Any]) -> Dict[str, Any]:
    """HTTP response schema for Decision Engine — active path only."""
    return {
        "latency_ms": prediction.get("prediction_latency_ms"),
        "prediction": prediction,
        "explanation": explanation,
    }
