import pytest
from src.schemas.xai import XAIExplanation, XAIExplainRequest


@pytest.mark.unit
@pytest.mark.xai
class TestXAISchemas:
    """Test XAI schemas"""
    
    def test_xai_explanation_schema(self):
        """Test XAIExplanation schema"""
        explanation = XAIExplanation(
            explanation_id="expl-001",
            type="ml_prediction",
            prediction_id="pred-001",
            method="SHAP",
            viability_score=0.87,
            recommendation="ACCEPT",
            features_importance={
                "latency": 0.40,
                "throughput": 0.30,
                "reliability": 0.20,
                "jitter": 0.10
            },
            shap_values={
                "latency": 0.15,
                "throughput": 0.10
            },
            reasoning="Viabilidade 0.87 (ACCEPT). Feature mais importante: latency."
        )
        assert explanation.method == "SHAP"
        assert explanation.viability_score == 0.87
        assert "latency" in explanation.features_importance
    
    def test_xai_explain_request(self):
        """Test XAIExplainRequest schema"""
        request = XAIExplainRequest(prediction_id="pred-001")
        assert request.prediction_id == "pred-001"
        assert request.decision_id is None
        
        request2 = XAIExplainRequest(decision_id="decision-001")
        assert request2.decision_id == "decision-001"
        assert request2.prediction_id is None







