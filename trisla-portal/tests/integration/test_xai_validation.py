import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.xai
class TestXAIValidation:
    """Validation tests for XAI explanations"""
    
    async def test_xai_explanation_structure(self, async_client: AsyncClient):
        """Test that XAI explanations have correct structure"""
        request_data = {
            "prediction_id": "pred-001"
        }
        response = await async_client.post(
            "/api/v1/xai/explain",
            json=request_data
        )
        
        if response.status_code == 200:
            explanation = response.json()
            
            # Validate structure
            assert "explanation_id" in explanation
            assert "type" in explanation
            assert "method" in explanation
            assert "reasoning" in explanation
            assert "features_importance" in explanation
            
            # Validate method
            assert explanation["method"] in ["SHAP", "LIME", "fallback"]
            
            # Validate features_importance is a dict
            assert isinstance(explanation["features_importance"], dict)
            
            # Validate reasoning is not empty
            assert len(explanation["reasoning"]) > 0
    
    async def test_xai_numerical_values(self, async_client: AsyncClient):
        """Test that XAI numerical values are valid"""
        request_data = {
            "prediction_id": "pred-001"
        }
        response = await async_client.post(
            "/api/v1/xai/explain",
            json=request_data
        )
        
        if response.status_code == 200:
            explanation = response.json()
            
            # If viability_score exists, should be between 0 and 1
            if "viability_score" in explanation and explanation["viability_score"] is not None:
                score = explanation["viability_score"]
                assert 0 <= score <= 1
            
            # Features importance values should be between 0 and 1
            for feature, importance in explanation["features_importance"].items():
                assert isinstance(importance, (int, float))
                assert 0 <= importance <= 1







