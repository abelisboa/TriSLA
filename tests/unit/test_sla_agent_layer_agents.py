"""
Unit Tests - SLA-Agent Layer Agents
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
    from slo_evaluator import SLOEvaluator, SLOStatus
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
def agent_ran(mock_nasp_client):
    """Fixture para criar AgentRAN"""
    with patch.dict(os.environ, {"BC_ENABLED": "false"}):
        return AgentRAN(nasp_client=mock_nasp_client)


@pytest.fixture
def agent_transport(mock_nasp_client):
    """Fixture para criar AgentTransport"""
    with patch.dict(os.environ, {"BC_ENABLED": "false"}):
        return AgentTransport(nasp_client=mock_nasp_client)


@pytest.fixture
def agent_core(mock_nasp_client):
    """Fixture para criar AgentCore"""
    with patch.dict(os.environ, {"BC_ENABLED": "false"}):
        return AgentCore(nasp_client=mock_nasp_client)


@pytest.mark.asyncio
async def test_agent_ran_collect_metrics(agent_ran):
    """Testa coleta de métricas RAN"""
    metrics = await agent_ran.collect_metrics()
    
    assert metrics is not None
    assert metrics["domain"] == "RAN"
    assert "agent_id" in metrics
    assert "timestamp" in metrics


@pytest.mark.asyncio
async def test_agent_ran_execute_action(agent_ran):
    """Testa execução de ação RAN"""
    action = {
        "type": "ADJUST_PRB",
        "parameters": {"prb_allocation": 0.7}
    }
    
    result = await agent_ran.execute_action(action)
    
    assert result is not None
    assert result["domain"] == "RAN"
    assert "action_type" in result
    assert "executed" in result


@pytest.mark.asyncio
async def test_agent_ran_evaluate_slos(agent_ran):
    """Testa avaliação de SLOs RAN"""
    metrics = await agent_ran.collect_metrics()
    evaluation = await agent_ran.evaluate_slos(metrics)
    
    assert evaluation is not None
    assert "status" in evaluation
    assert "compliance_rate" in evaluation
    assert evaluation["status"] in [SLOStatus.OK, SLOStatus.RISK, SLOStatus.VIOLATED]


@pytest.mark.asyncio
async def test_agent_transport_collect_metrics(agent_transport):
    """Testa coleta de métricas Transport"""
    metrics = await agent_transport.collect_metrics()
    
    assert metrics is not None
    assert metrics["domain"] == "Transport"
    assert "agent_id" in metrics


@pytest.mark.asyncio
async def test_agent_core_collect_metrics(agent_core):
    """Testa coleta de métricas Core"""
    metrics = await agent_core.collect_metrics()
    
    assert metrics is not None
    assert metrics["domain"] == "Core"
    assert "agent_id" in metrics


def test_agent_ran_is_healthy(agent_ran):
    """Testa health check do AgentRAN"""
    assert agent_ran.is_healthy() is True  # Mock client disponível


def test_agent_transport_is_healthy(agent_transport):
    """Testa health check do AgentTransport"""
    assert agent_transport.is_healthy() is True


def test_agent_core_is_healthy(agent_core):
    """Testa health check do AgentCore"""
    assert agent_core.is_healthy() is True

