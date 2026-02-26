"""
Integration Tests - SLA-Agent Layer Integration
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Adicionar caminhos dos módulos
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
    from slo_evaluator import SLOEvaluator
finally:
    os.chdir(original_cwd)


@pytest.fixture
def mock_nasp_client():
    """Fixture para criar NASPClient mock"""
    client = Mock()
    client.get_ran_metrics = AsyncMock(return_value={"cpu": 50.0, "memory": 60.0, "throughput": 1.2})
    client.get_transport_metrics = AsyncMock(return_value={"bandwidth": 10.5, "latency": 5.2})
    client.get_core_metrics = AsyncMock(return_value={"cpu_utilization": 0.5, "memory_utilization": 0.6})
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
async def test_integration_agents_coordination(coordinator):
    """Testa coordenação entre agentes"""
    action = {
        "type": "ADJUST_RESOURCES",
        "parameters": {"resource_level": 0.8}
    }
    
    result = await coordinator.coordinate_action(action)
    
    assert result is not None
    assert result["total_count"] == 3  # RAN, Transport, Core
    assert "success_rate" in result


@pytest.mark.asyncio
async def test_integration_federated_policy(coordinator):
    """Testa política federada"""
    policy = {
        "name": "multi-domain-policy",
        "priority": "high",
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
    assert result["policy_name"] == "multi-domain-policy"
    assert len(result["results"]) == 2


@pytest.mark.asyncio
async def test_integration_slo_evaluation_flow(agents):
    """Testa fluxo completo de avaliação de SLOs"""
    # Coletar métricas
    ran_metrics = await agents[0].collect_metrics()
    transport_metrics = await agents[1].collect_metrics()
    core_metrics = await agents[2].collect_metrics()
    
    # Avaliar SLOs
    ran_evaluation = await agents[0].evaluate_slos(ran_metrics)
    transport_evaluation = await agents[1].evaluate_slos(transport_metrics)
    core_evaluation = await agents[2].evaluate_slos(core_metrics)
    
    # Verificar resultados
    assert ran_evaluation is not None
    assert transport_evaluation is not None
    assert core_evaluation is not None
    assert "compliance_rate" in ran_evaluation
    assert "compliance_rate" in transport_evaluation
    assert "compliance_rate" in core_evaluation






