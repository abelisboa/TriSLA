"""
Testes Unitários - Decision Engine
Testa funções de decisão pura sem I/O externo
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Adicionar caminho do Decision Engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/decision-engine/src"))

from models import (
    DecisionInput, DecisionResult, DecisionAction,
    SLAIntent, NestSubset, MLPrediction, RiskLevel, SliceType, SLARequirement
)
from engine import DecisionEngine


class TestDecisionEngine:
    """Testes do motor de decisão"""
    
    @pytest.mark.asyncio
    async def test_decision_urllc_low_risk_accept(self):
        """Teste: SLA URLLC com risco baixo deve ser ACEITO"""
        engine = DecisionEngine()
        
        # Criar intent URLLC
        intent = SLAIntent(
            intent_id="intent-urllc-001",
            tenant_id="tenant-001",
            service_type=SliceType.URLLC,
            sla_requirements={
                "latency": "10ms",
                "reliability": 0.999
            }
        )
        
        # Criar NEST
        nest = NestSubset(
            nest_id="nest-001",
            intent_id="intent-urllc-001",
            network_slices=[],
            resources={"cpu": "2", "memory": "4Gi"},
            status="generated"
        )
        
        # Previsão ML com risco baixo
        ml_prediction = MLPrediction(
            risk_score=0.2,
            risk_level=RiskLevel.LOW,
            confidence=0.9,
            explanation="URLLC viável"
        )
        
        decision_input = DecisionInput(
            intent=intent,
            nest=nest,
            ml_prediction=ml_prediction
        )
        
        # Aplicar regras
        action, reasoning, slos, domains = engine._apply_decision_rules(
            intent, nest, ml_prediction, None
        )
        
        assert action == DecisionAction.ACCEPT
        assert "URLLC" in reasoning
        assert "RAN" in domains
        assert "Transporte" in domains
        assert "Core" in domains
    
    @pytest.mark.asyncio
    async def test_decision_high_risk_reject(self):
        """Teste: SLA com risco alto deve ser REJEITADO"""
        engine = DecisionEngine()
        
        intent = SLAIntent(
            intent_id="intent-001",
            tenant_id="tenant-001",
            service_type=SliceType.EMBB,
            sla_requirements={"latency": "5ms"}
        )
        
        nest = NestSubset(
            nest_id="nest-001",
            intent_id="intent-001",
            network_slices=[],
            resources={},
            status="generated"
        )
        
        # Previsão ML com risco alto
        ml_prediction = MLPrediction(
            risk_score=0.8,
            risk_level=RiskLevel.HIGH,
            confidence=0.9,
            explanation="Risco alto detectado"
        )
        
        # Aplicar regras
        action, reasoning, slos, domains = engine._apply_decision_rules(
            intent, nest, ml_prediction, None
        )
        
        assert action == DecisionAction.REJECT
        assert "ALTO" in reasoning.upper() or "HIGH" in reasoning.upper()
    
    @pytest.mark.asyncio
    async def test_decision_medium_risk_renegotiate(self):
        """Teste: SLA com risco médio deve requerer RENEGOCIAÇÃO"""
        engine = DecisionEngine()
        
        intent = SLAIntent(
            intent_id="intent-001",
            tenant_id="tenant-001",
            service_type=SliceType.EMBB,
            sla_requirements={"throughput": "100Mbps"}
        )
        
        nest = NestSubset(
            nest_id="nest-001",
            intent_id="intent-001",
            network_slices=[],
            resources={},
            status="generated"
        )
        
        # Previsão ML com risco médio
        ml_prediction = MLPrediction(
            risk_score=0.5,
            risk_level=RiskLevel.MEDIUM,
            confidence=0.8,
            explanation="Risco médio"
        )
        
        # Aplicar regras
        action, reasoning, slos, domains = engine._apply_decision_rules(
            intent, nest, ml_prediction, None
        )
        
        assert action == DecisionAction.RENEGOTIATE
        assert "renegociação" in reasoning.lower() or "renegotiate" in reasoning.lower()
    
    def test_extract_slos_from_intent(self):
        """Teste: Extração de SLOs do intent"""
        engine = DecisionEngine()
        
        intent = SLAIntent(
            intent_id="intent-001",
            service_type=SliceType.URLLC,
            sla_requirements={
                "latency": "10ms",
                "reliability": 0.999,
                "throughput": "100Mbps"
            }
        )
        
        action, reasoning, slos, domains = engine._apply_decision_rules(
            intent, None, MLPrediction(
                risk_score=0.3,
                risk_level=RiskLevel.LOW,
                confidence=0.9
            ), None
        )
        
        # Verificar que SLOs foram extraídos
        assert len(slos) >= 1
        assert any(slo.name == "latency" for slo in slos)
        assert any(slo.name == "reliability" for slo in slos)

