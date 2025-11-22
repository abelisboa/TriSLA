"""
Unit Tests - SLA-Agent Layer
Testes unitários para agentes autônomos (RAN, Transport, Core)
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Adicionar src ao path
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from agent_ran import AgentRAN
from agent_transport import AgentTransport
from agent_core import AgentCore
from slo_evaluator import SLOEvaluator, SLOStatus
from kafka_producer import EventProducer


class TestAgentRAN:
    """Testes do Agent RAN"""
    
    @pytest.fixture
    def mock_nasp_client(self):
        """Mock do NASP Client"""
        client = AsyncMock()
        client.get_ran_metrics = AsyncMock(return_value={
            "latency": 12.5,
            "throughput": 850.0,
            "prb_allocation": 0.75,
            "packet_loss": 0.001,
            "jitter": 2.3
        })
        client.execute_ran_action = AsyncMock(return_value={
            "success": True,
            "executed": True
        })
        return client
    
    @pytest.fixture
    def mock_event_producer(self):
        """Mock do Event Producer"""
        producer = AsyncMock()
        producer.send_i06_event = AsyncMock(return_value=True)
        producer.send_i07_action_result = AsyncMock(return_value=True)
        return producer
    
    @pytest.mark.asyncio
    async def test_collect_metrics_real(self, mock_nasp_client, mock_event_producer):
        """Testa coleta de métricas reais do NASP"""
        agent = AgentRAN(nasp_client=mock_nasp_client, event_producer=mock_event_producer)
        metrics = await agent.collect_metrics()
        
        assert metrics["domain"] == "RAN"
        assert metrics["source"] == "nasp_ran_real"
        assert "latency" in metrics
        assert "throughput" in metrics
        assert metrics["latency"] == 12.5
    
    @pytest.mark.asyncio
    async def test_execute_action_real(self, mock_nasp_client, mock_event_producer):
        """Testa execução de ação real via NASP"""
        agent = AgentRAN(nasp_client=mock_nasp_client, event_producer=mock_event_producer)
        action = {"type": "ADJUST_PRB", "parameters": {"prb": 0.8}}
        
        result = await agent.execute_action(action)
        
        assert result["domain"] == "RAN"
        assert result["executed"] is True
        assert result["action_type"] == "ADJUST_PRB"
        # Verificar que evento I-07 foi publicado
        mock_event_producer.send_i07_action_result.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_slos_and_publish_i06(self, mock_nasp_client, mock_event_producer):
        """Testa avaliação de SLOs e publicação de eventos I-06"""
        agent = AgentRAN(nasp_client=mock_nasp_client, event_producer=mock_event_producer)
        
        # Métricas que violam SLO (latência alta)
        metrics = {
            "latency": 25.0,  # Violado (target: 10ms)
            "throughput": 850.0,
            "prb_allocation": 0.75,
            "packet_loss": 0.001,
            "jitter": 2.3
        }
        
        evaluation = await agent.evaluate_slos(metrics)
        
        assert evaluation["status"] in [SLOStatus.RISK, SLOStatus.VIOLATED]
        # Verificar que evento I-06 foi publicado para violação
        if evaluation["status"] == SLOStatus.VIOLATED:
            mock_event_producer.send_i06_event.assert_called()


class TestAgentTransport:
    """Testes do Agent Transport"""
    
    @pytest.fixture
    def mock_nasp_client(self):
        """Mock do NASP Client"""
        client = AsyncMock()
        client.get_transport_metrics = AsyncMock(return_value={
            "bandwidth": 100.0,
            "latency": 5.0,
            "packet_loss": 0.0001,
            "jitter": 2.0
        })
        return client
    
    @pytest.fixture
    def mock_event_producer(self):
        """Mock do Event Producer"""
        producer = AsyncMock()
        producer.send_i06_event = AsyncMock(return_value=True)
        producer.send_i07_action_result = AsyncMock(return_value=True)
        return producer
    
    @pytest.mark.asyncio
    async def test_collect_metrics_real(self, mock_nasp_client, mock_event_producer):
        """Testa coleta de métricas reais do Transport"""
        agent = AgentTransport(nasp_client=mock_nasp_client, event_producer=mock_event_producer)
        metrics = await agent.collect_metrics()
        
        assert metrics["domain"] == "Transport"
        assert metrics["source"] == "nasp_transport_real"
        assert "bandwidth" in metrics
        assert "latency" in metrics


class TestAgentCore:
    """Testes do Agent Core"""
    
    @pytest.fixture
    def mock_nasp_client(self):
        """Mock do NASP Client"""
        client = AsyncMock()
        client.get_core_metrics = AsyncMock(return_value={
            "cpu_utilization": 0.65,
            "memory_utilization": 0.75,
            "request_latency": 45.0,
            "throughput": 9500.0
        })
        return client
    
    @pytest.fixture
    def mock_event_producer(self):
        """Mock do Event Producer"""
        producer = AsyncMock()
        producer.send_i06_event = AsyncMock(return_value=True)
        producer.send_i07_action_result = AsyncMock(return_value=True)
        return producer
    
    @pytest.mark.asyncio
    async def test_collect_metrics_real(self, mock_nasp_client, mock_event_producer):
        """Testa coleta de métricas reais do Core"""
        agent = AgentCore(nasp_client=mock_nasp_client, event_producer=mock_event_producer)
        metrics = await agent.collect_metrics()
        
        assert metrics["domain"] == "Core"
        assert metrics["source"] == "nasp_core_real"
        assert "cpu_utilization" in metrics
        assert "memory_utilization" in metrics


class TestSLOEvaluator:
    """Testes do SLO Evaluator"""
    
    def test_evaluate_ok(self):
        """Testa avaliação de SLO em OK"""
        config = {
            "domain": "RAN",
            "slos": [
                {
                    "name": "latency",
                    "target": 10.0,
                    "unit": "ms",
                    "operator": "<=",
                    "risk_threshold": 0.8
                }
            ]
        }
        evaluator = SLOEvaluator(config)
        
        metrics = {"latency": 8.0}  # Dentro do target
        result = evaluator.evaluate(metrics)
        
        assert result["status"] == SLOStatus.OK
        assert result["compliance_rate"] == 1.0
    
    def test_evaluate_violated(self):
        """Testa avaliação de SLO violado"""
        config = {
            "domain": "RAN",
            "slos": [
                {
                    "name": "latency",
                    "target": 10.0,
                    "unit": "ms",
                    "operator": "<=",
                    "risk_threshold": 0.8
                }
            ]
        }
        evaluator = SLOEvaluator(config)
        
        metrics = {"latency": 15.0}  # Violado
        result = evaluator.evaluate(metrics)
        
        assert result["status"] == SLOStatus.VIOLATED
        assert "latency" in result["violations"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

