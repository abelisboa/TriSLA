from pydantic import BaseModel
from typing import Optional, Dict, Any


class XAIExplainRequest(BaseModel):
    prediction_id: Optional[str] = None
    decision_id: Optional[str] = None


class XAIExplanation(BaseModel):
    explanation_id: str
    type: str  # ml_prediction, decision
    prediction_id: Optional[str] = None
    decision_id: Optional[str] = None
    method: str  # SHAP, LIME, fallback
    viability_score: Optional[float] = None
    recommendation: Optional[str] = None
    features_importance: Dict[str, float]
    shap_values: Optional[Dict[str, float]] = None
    reasoning: str
    visualizations: Optional[Dict[str, Any]] = None






