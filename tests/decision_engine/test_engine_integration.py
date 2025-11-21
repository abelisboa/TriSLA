"""
Testes de Integração - Decision Engine
Testa fluxo completo com mocks de SEM-CSMF, ML-NSMF e BC-NSSMF
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Adicionar caminho do Decision Engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/decision-engine/src"))

from models import DecisionResult, DecisionAction, SliceType, RiskLevel
from service import DecisionService
from engine import DecisionEngine


class TestDecisionEngineIntegration:
    """Testes de integração do Decision Engine"""
    
    @pytest.mark.asyncio
    @patch('apps.decision_engine.src.engine.SEMClient')
    @patch('apps.decision_engine.src.engine.MLClient')
    @patch('apps.decision_engine.src.engine.BCClient')
    async def test_full_decision_flow_accept(self, mock_bc_class, mock_ml_class, mock_sem_class):
        """Teste: Fluxo completo de decisão com mock de todos os componentes"""
        
        # Mock SEM Client
        mock_sem = mock_sem_class.return_value
        mock_sem.fetch_semantic_sla = AsyncMock(return_value=Mock(
            intent_id="intent-001",
            service_type=SliceType.URLLC,
            sla_requirements={"latency": "10ms", "reliability": 0.999},
            nest_id="nest-001"
        ))
        mock_sem.fetch_nest_by_intent_id = AsyncMock(return_value=Mock(
            nest_id="nest-001",
            intent_id="intent-001",
            network_slices=[],
            resources={"cpu": "2"},
            status="generated"
        ))
        mock_sem.close = AsyncMock()
        
        # Mock ML Client
        mock_ml = mock_ml_class.return_value
        mock_ml.predict_viability = AsyncMock(return_value=Mock(
            risk_score=0.2,
            risk_level=RiskLevel.LOW,
            confidence=0.9,
            explanation="Risco baixo"
        ))
        mock_ml.close = AsyncMock()
        
        # Mock BC Client
        mock_bc = mock_bc_class.return_value
        mock_bc.register_sla_on_chain = AsyncMock(return_value="0x1234567890abcdef")
        mock_bc._initialize = Mock()  # Não executar inicialização real
        
        # Criar engine
        engine = DecisionEngine()
        
        # Executar decisão
        result = await engine.decide("intent-001", "nest-001")
        
        # Verificar resultado
        assert isinstance(result, DecisionResult)
        assert result.action == DecisionAction.ACCEPT
        assert result.intent_id == "intent-001"
        assert result.ml_risk_score == 0.2
        assert result.ml_risk_level == RiskLevel.LOW
        
        # Verificar que BC foi chamado
        mock_bc.register_sla_on_chain.assert_called_once()
        
        # Limpar
        await engine.close()
    
    @pytest.mark.asyncio
    @patch('apps.decision_engine.src.service.DecisionEngine')
    async def test_service_process_decision(self, mock_engine_class):
        """Teste: Serviço processa decisão corretamente"""
        
        # Mock Engine
        mock_engine = mock_engine_class.return_value
        mock_engine.decide = AsyncMock(return_value=DecisionResult(
            decision_id="dec-001",
            intent_id="intent-001",
            action=DecisionAction.ACCEPT,
            reasoning="Aceito",
            confidence=0.9
        ))
        mock_engine.close = AsyncMock()
        
        # Criar serviço
        service = DecisionService()
        
        # Processar decisão
        result = await service.process_decision("intent-001")
        
        # Verificar
        assert result.action == DecisionAction.ACCEPT
        assert result.intent_id == "intent-001"
        
        # Limpar
        await service.close()

