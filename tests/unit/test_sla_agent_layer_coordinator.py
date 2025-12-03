"""
Unit Tests - SLA-Agent Layer AgentCoordinator
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
SLA_SRC = BASE_DIR / "apps" / "sla-agent-layer" / "src"
sys.path.insert(0, str(SLA_SRC))

# Mudar para o diretório do módulo para resolver imports relativos
original_cwd = os.getcwd()
os.chdir(str(SLA_SRC))

try:
    from agent_ran import AgentRAN
    from agent_transport import AgentTransport
    from agent_core import AgentCore
    from agent_coordinator import AgentCoordinator
finally:
    os.chdir(original_cwd)


@pytest.fixture
def mock_nasp_client():
    """Fixture para criar NASPClient mock"""
    client = Mock()
    client.get_ran_metrics = AsyncMock(return_value={"cpu": 50.0, "memory": 60.0})
    client.get_transport_metrics = AsyncMock(return_value={"bandwidth": 10.5})
    client.get_core_metrics = AsyncMock(return_value={"cpu_utilization": 0.5})
    client.execute_ran_action = AsyncMock(return_value={"success": True})
    return client


@pytest.fixture
def agents(mock_nasp_client):
    """Fixture para criar lista de agentes"""
    with patch.dict(os.environ, {"BC_ENABLED": "false"}):
        return [
            AgentRAN(nasp_client=mock_nasp_client),
            AgentTransport(nasp_client=mock_nasp_client),
            AgentCore(nasp_client=mock_nasp_client)
        ]


@pytest.fixture
def coordinator(agents):
    """Fixture para criar AgentCoordinator"""
    return AgentCoordinator(agents)


@pytest.mark.asyncio
async def test_coordinator_coordinate_action(coordinator):
    """Testa coordenação de ação"""
    action = {
        "type": "ADJUST_RESOURCES",
        "parameters": {"resource_level": 0.8}
    }
    
    result = await coordinator.coordinate_action(action, target_domains=["RAN", "Transport"])
    
    assert result is not None
    assert "action_type" in result
    assert "results" in result
    assert "executed_count" in result
    assert "success_rate" in result


@pytest.mark.asyncio
async def test_coordinator_collect_all_metrics(coordinator):
    """Testa coleta de métricas de todos os agentes"""
    metrics = await coordinator.collect_all_metrics()
    
    assert metrics is not None
    assert "domains" in metrics
    assert "total_domains" in metrics
    assert metrics["total_domains"] == 3


@pytest.mark.asyncio
async def test_coordinator_evaluate_all_slos(coordinator):
    """Testa avaliação de SLOs de todos os agentes"""
    evaluation = await coordinator.evaluate_all_slos()
    
    assert evaluation is not None
    assert "evaluations" in evaluation
    assert "overall_compliance" in evaluation
    assert 0.0 <= evaluation["overall_compliance"] <= 1.0


@pytest.mark.asyncio
async def test_coordinator_apply_federated_policy(coordinator):
    """Testa aplicação de política federada"""
    policy = {
        "name": "test-policy",
        "priority": "high",
        "domains": ["RAN", "Transport"],
        "actions": [
            {
                "domain": "RAN",
                "action": {"type": "ADJUST_PRB", "parameters": {}}
            },
            {
                "domain": "Transport",
                "action": {"type": "ADJUST_BANDWIDTH", "parameters": {}}
            }
        ]
    }
    
    result = await coordinator.apply_federated_policy(policy)
    
    assert result is not None
    assert result["policy_name"] == "test-policy"
    assert "results" in result
    assert "success_rate" in result

