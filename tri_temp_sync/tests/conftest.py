"""
Pytest Configuration
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_intent():
    """Fixture para intent de teste"""
    return {
        "intent_id": "test-intent-001",
        "tenant_id": "test-tenant",
        "service_type": "eMBB",
        "sla_requirements": {
            "latency": "10ms",
            "throughput": "100Mbps",
            "reliability": 0.999
        }
    }

