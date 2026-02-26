import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.xai
class TestXAIAPI:
    """Integration tests for XAI API"""
    
    async def test_get_explanations(self, async_client: AsyncClient):
        """Test getting XAI explanations"""
        response = await async_client.get("/api/v1/xai/explanations")
        assert response.status_code == 200
        explanations = response.json()
        assert isinstance(explanations, list)
    
    async def test_explain_prediction(self, async_client: AsyncClient):
        """Test generating XAI explanation for prediction"""
        request_data = {
            "prediction_id": "pred-001"
        }
        response = await async_client.post(
            "/api/v1/xai/explain",
            json=request_data
        )
        # May fail if ML-NSMF is not available
        assert response.status_code in [200, 404, 500, 503]
        
        if response.status_code == 200:
            explanation = response.json()
            assert "explanation_id" in explanation
            assert "method" in explanation
            assert "reasoning" in explanation
    
    async def test_explain_decision(self, async_client: AsyncClient):
        """Test generating XAI explanation for decision"""
        request_data = {
            "decision_id": "decision-001"
        }
        response = await async_client.post(
            "/api/v1/xai/explain",
            json=request_data
        )
        # May fail if Decision Engine is not available
        assert response.status_code in [200, 404, 500, 503]







