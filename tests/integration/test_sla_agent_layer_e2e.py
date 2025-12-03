"""
E2E Tests - SLA-Agent Layer (Decision Engine → Agents → Actions)
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
finally:
    os.chdir(original_cwd)


@pytest.fixture
def mock_nasp_client():
    """Fixture para criar NASPClient mock"""
    client = Mock()
    client.get_ran_metrics = AsyncMock(return_value={"cpu": 50.0, "memory": 60.0, "throughput": 1.2})
    client.get_transport_metrics = AsyncMock(return_value={"bandwidth": 10.5, "latency": 5.2})
    client.get_core_metrics = AsyncMock(return_value={"cpu_utilization": 0.5, "memory_utilization": 0.6})
    client.execute_ran_action = AsyncMock(return_value={"success": True, "executed": True})
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
async def test_e2e_decision_to_agents(coordinator):
    """Testa E2E: Decision Engine → Agents → Actions"""
    # Simular decisão do Decision Engine
    decision = {
        "type": "ADJUST_RESOURCES",
        "parameters": {"resource_level": 0.8},
        "domains": ["RAN", "Transport"]
    }
    
    # Coordenar ação
    result = await coordinator.coordinate_action(decision, target_domains=decision["domains"])
    
    assert result is not None
    assert result["total_count"] == 2
    assert "success_rate" in result


@pytest.mark.asyncio
async def test_e2e_federated_policy_execution(coordinator):
    """Testa E2E: Execução de política federada"""
    policy = {
        "name": "e2e-policy",
        "priority": "high",
        "actions": [
            {
                "domain": "RAN",
                "action": {"type": "ADJUST_PRB", "parameters": {"prb_allocation": 0.7}}
            },
            {
                "domain": "Transport",
                "action": {"type": "ADJUST_BANDWIDTH", "parameters": {"bandwidth": 100}},
                "depends_on": ["RAN"]
            }
        ]
    }
    
    result = await coordinator.apply_federated_policy(policy)
    
    assert result is not None
    assert result["policy_name"] == "e2e-policy"
    assert len(result["results"]) == 2


@pytest.mark.asyncio
async def test_e2e_performance(coordinator):
    """Testa performance do fluxo E2E"""
    import time
    
    action = {
        "type": "COLLECT_METRICS",
        "parameters": {}
    }
    
    start_time = time.time()
    result = await coordinator.collect_all_metrics()
    end_time = time.time()
    
    elapsed_time = (end_time - start_time) * 1000  # Converter para ms
    
    assert result is not None
    # Performance deve ser < 1000ms (1s)
    assert elapsed_time < 1000, f"Fluxo E2E levou {elapsed_time:.2f}ms (esperado < 1000ms)"

