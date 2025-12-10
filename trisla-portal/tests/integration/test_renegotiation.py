import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.integration
@pytest.mark.contracts
class TestRenegotiation:
    """Integration tests for contract renegotiation"""
    
    async def test_get_renegotiations(self, async_client: AsyncClient):
        """Test getting contract renegotiations"""
        # First create a contract
        contract_data = {
            "tenant_id": "tenant-001",
            "intent_id": "intent-001",
            "nest_id": "nest-001",
            "decision_id": "decision-001",
            "sla_requirements": {"latency": {"max": "10ms"}},
            "domains": ["RAN"],
            "metadata": {"service_type": "URLLC"}
        }
        
        create_response = await async_client.post(
            "/api/v1/contracts",
            json=contract_data
        )
        
        if create_response.status_code == 200:
            contract_id = create_response.json()["id"]
            
            # Get renegotiations
            response = await async_client.get(
                f"/api/v1/contracts/{contract_id}/renegotiations"
            )
            assert response.status_code == 200
            renegotiations = response.json()
            assert isinstance(renegotiations, list)







