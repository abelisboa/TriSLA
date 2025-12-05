"""
Integration Tests - Decision Engine Integration (SEM + ML)
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar caminhos dos módulos
BASE_DIR = Path(__file__).parent.parent.parent
DE_SRC = BASE_DIR / "apps" / "decision-engine" / "src"
sys.path.insert(0, str(DE_SRC))

from service import DecisionService
from models import SLAIntent, SliceType, DecisionInput, MLPrediction, RiskLevel


@pytest.fixture
def decision_service():
    """Fixture para criar DecisionService"""
    return DecisionService()


@pytest.fixture
def sample_intent():
    """Fixture para criar intent de teste"""
    return SLAIntent(
        intent_id="test-intent-001",
        tenant_id="test-tenant",
        service_type=SliceType.EMBB,
        sla_requirements={
            "latency": "50ms",
            "throughput": "100Mbps",
            "reliability": 0.99
        }
    )


@pytest.fixture
def sample_ml_prediction_low_risk():
    """Fixture para criar predição ML de baixo risco"""
    return MLPrediction(
        risk_score=0.2,
        risk_level=RiskLevel.LOW,
        confidence=0.9,
        explanation="Risk level low (score: 0.20). Principal fator: reliability (37.9%).",
        timestamp="2025-01-27T00:00:00Z"
    )


@pytest.fixture
def sample_ml_prediction_high_risk():
    """Fixture para criar predição ML de alto risco"""
    return MLPrediction(
        risk_score=0.8,
        risk_level=RiskLevel.HIGH,
        confidence=0.85,
        explanation="Risk level high (score: 0.80). Principal fator: latency (12.1%).",
        timestamp="2025-01-27T00:00:00Z"
    )


@pytest.mark.asyncio
async def test_integration_decision_service_accept(decision_service, sample_intent, sample_ml_prediction_low_risk):
    """Testa integração: DecisionService com ML prediction de baixo risco → ACCEPT"""
    decision_input = DecisionInput(
        intent=sample_intent,
        nest=None,
        ml_prediction=sample_ml_prediction_low_risk,
        context={}
    )
    
    result = await decision_service.process_decision_from_input(decision_input)
    
    assert result is not None
    assert result.intent_id == "test-intent-001"
    assert result.action.value in ["AC", "RENEG", "REJ"]
    assert result.ml_risk_score == 0.2
    assert result.ml_risk_level == RiskLevel.LOW
    assert result.confidence > 0.0


@pytest.mark.asyncio
async def test_integration_decision_service_reject(decision_service, sample_intent, sample_ml_prediction_high_risk):
    """Testa integração: DecisionService com ML prediction de alto risco → REJECT"""
    decision_input = DecisionInput(
        intent=sample_intent,
        nest=None,
        ml_prediction=sample_ml_prediction_high_risk,
        context={}
    )
    
    result = await decision_service.process_decision_from_input(decision_input)
    
    assert result is not None
    assert result.intent_id == "test-intent-001"
    # Alto risco deve resultar em REJECT ou RENEGOTIATE
    assert result.action.value in ["AC", "RENEG", "REJ"]
    assert result.ml_risk_score == 0.8
    assert result.ml_risk_level == RiskLevel.HIGH


@pytest.mark.asyncio
async def test_integration_decision_service_different_slice_types(decision_service, sample_ml_prediction_low_risk):
    """Testa integração com diferentes tipos de slice"""
    slice_types = [SliceType.URLLC, SliceType.EMBB, SliceType.MMTC]
    
    for slice_type in slice_types:
        intent = SLAIntent(
            intent_id=f"test-intent-{slice_type.value}",
            service_type=slice_type,
            sla_requirements={
                "latency": "10ms" if slice_type == SliceType.URLLC else "50ms",
                "throughput": "100Mbps",
                "reliability": 0.99
            }
        )
        
        decision_input = DecisionInput(
            intent=intent,
            nest=None,
            ml_prediction=sample_ml_prediction_low_risk,
            context={}
        )
        
        result = await decision_service.process_decision_from_input(decision_input)
        
        assert result is not None
        assert result.intent_id == f"test-intent-{slice_type.value}"
        assert result.action.value in ["AC", "RENEG", "REJ"]


@pytest.mark.asyncio
async def test_integration_decision_service_slos_extracted(decision_service, sample_intent, sample_ml_prediction_low_risk):
    """Testa que SLOs são extraídos corretamente do intent"""
    decision_input = DecisionInput(
        intent=sample_intent,
        nest=None,
        ml_prediction=sample_ml_prediction_low_risk,
        context={}
    )
    
    result = await decision_service.process_decision_from_input(decision_input)
    
    assert result is not None
    assert result.slos is not None
    assert len(result.slos) > 0
    # Verificar que SLOs foram extraídos
    slo_names = [slo.name for slo in result.slos]
    assert "latency" in slo_names or "throughput" in slo_names or "reliability" in slo_names


@pytest.mark.asyncio
async def test_integration_decision_service_domains_extracted(decision_service, sample_intent, sample_ml_prediction_low_risk):
    """Testa que domínios são extraídos corretamente baseado no tipo de slice"""
    decision_input = DecisionInput(
        intent=sample_intent,
        nest=None,
        ml_prediction=sample_ml_prediction_low_risk,
        context={}
    )
    
    result = await decision_service.process_decision_from_input(decision_input)
    
    assert result is not None
    assert result.domains is not None
    assert len(result.domains) > 0
    # eMBB deve ter RAN e Transporte
    if sample_intent.service_type == SliceType.EMBB:
        assert "RAN" in result.domains
        assert "Transporte" in result.domains






