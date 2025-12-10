import pytest
import httpx
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from src.main import app

# Test client
@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Test data fixtures
@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        "tenant_id": "tenant-001",
        "intent_id": "intent-001",
        "nest_id": "nest-001",
        "decision_id": "decision-001",
        "sla_requirements": {
            "latency": {"max": "10ms"},
            "throughput": {"min": "100Mbps"},
            "reliability": 0.99999
        },
        "domains": ["RAN", "Transport", "Core"],
        "metadata": {
            "service_type": "URLLC",
            "priority": "high"
        }
    }

@pytest.fixture
def sample_sla_pln_data():
    """Sample SLA PLN data for testing"""
    return {
        "intent_text": "Preciso de um slice URLLC com latência máxima de 10ms e throughput mínimo de 100Mbps",
        "tenant_id": "tenant-001"
    }

@pytest.fixture
def sample_batch_data():
    """Sample batch SLA data for testing"""
    return [
        {
            "tenant_id": "tenant-001",
            "intent_text": "Slice URLLC com latência 10ms",
            "service_type": "URLLC"
        },
        {
            "tenant_id": "tenant-002",
            "intent_text": "Slice eMBB para streaming",
            "service_type": "eMBB"
        }
    ]







