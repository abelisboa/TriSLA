import pytest
from httpx import AsyncClient
from src.models.database import Base, engine, SessionLocal
from src.models.contract import ContractModel


@pytest.mark.integration
@pytest.mark.contracts
class TestContractsAPI:
    """Integration tests for Contracts API"""
    
    @pytest.fixture(autouse=True)
    async def setup_db(self):
        """Setup test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    async def test_create_contract(self, async_client: AsyncClient, sample_contract_data):
        """Test creating a contract"""
        response = await async_client.post(
            "/api/v1/contracts",
            json=sample_contract_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == sample_contract_data["tenant_id"]
        assert data["status"] == "CREATED"
    
    async def test_get_contract(self, async_client: AsyncClient, sample_contract_data):
        """Test getting a contract"""
        # Create contract first
        create_response = await async_client.post(
            "/api/v1/contracts",
            json=sample_contract_data
        )
        contract_id = create_response.json()["id"]
        
        # Get contract
        response = await async_client.get(f"/api/v1/contracts/{contract_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contract_id
    
    async def test_list_contracts(self, async_client: AsyncClient, sample_contract_data):
        """Test listing contracts"""
        # Create a contract
        await async_client.post("/api/v1/contracts", json=sample_contract_data)
        
        # List contracts
        response = await async_client.get("/api/v1/contracts")
        assert response.status_code == 200
        contracts = response.json()
        assert isinstance(contracts, list)
        assert len(contracts) > 0
    
    async def test_get_contract_violations(self, async_client: AsyncClient, sample_contract_data):
        """Test getting contract violations"""
        # Create contract
        create_response = await async_client.post(
            "/api/v1/contracts",
            json=sample_contract_data
        )
        contract_id = create_response.json()["id"]
        
        # Get violations (should be empty initially)
        response = await async_client.get(f"/api/v1/contracts/{contract_id}/violations")
        assert response.status_code == 200
        violations = response.json()
        assert isinstance(violations, list)







