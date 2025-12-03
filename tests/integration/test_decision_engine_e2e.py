"""
E2E Tests - Decision Engine (SEM → ML → DE → Decision)
"""

import pytest
import sys
import os
import asyncio
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


@pytest.mark.asyncio
async def test_e2e_urllc_low_risk_accept(decision_service):
    """Testa E2E: URLLC com baixo risco → ACCEPT"""
    intent = SLAIntent(
        intent_id="test-e2e-urllc-001",
        tenant_id="test-tenant",
        service_type=SliceType.URLLC,
        sla_requirements={
            "latency": "5ms",
            "throughput": "100Mbps",
            "reliability": 0.999
        }
    )
    
    ml_prediction = MLPrediction(
        risk_score=0.2,
        risk_level=RiskLevel.LOW,
        confidence=0.9,
        explanation="Risk level low (score: 0.20). Principal fator: reliability (37.9%).",
        timestamp="2025-01-27T00:00:00Z"
    )
    
    decision_input = DecisionInput(
        intent=intent,
        nest=None,
        ml_prediction=ml_prediction,
        context={}
    )
    
    result = await decision_service.process_decision_from_input(decision_input)
    
    assert result is not None
    assert result.intent_id == "test-e2e-urllc-001"
    assert result.action.value in ["AC", "RENEG", "REJ"]
    assert result.ml_risk_score == 0.2
    assert result.ml_risk_level == RiskLevel.LOW
    assert result.domains is not None
    assert len(result.domains) > 0


@pytest.mark.asyncio
async def test_e2e_embb_high_risk_reject(decision_service):
    """Testa E2E: eMBB com alto risco → REJECT"""
    intent = SLAIntent(
        intent_id="test-e2e-embb-001",
        tenant_id="test-tenant",
        service_type=SliceType.EMBB,
        sla_requirements={
            "latency": "50ms",
            "throughput": "100Mbps",
            "reliability": 0.99
        }
    )
    
    ml_prediction = MLPrediction(
        risk_score=0.8,
        risk_level=RiskLevel.HIGH,
        confidence=0.85,
        explanation="Risk level high (score: 0.80). Principal fator: latency (12.1%).",
        timestamp="2025-01-27T00:00:00Z"
    )
    
    decision_input = DecisionInput(
        intent=intent,
        nest=None,
        ml_prediction=ml_prediction,
        context={}
    )
    
    result = await decision_service.process_decision_from_input(decision_input)
    
    assert result is not None
    assert result.intent_id == "test-e2e-embb-001"
    # Alto risco deve resultar em REJECT
    assert result.action.value in ["REJ", "RENEG"]
    assert result.ml_risk_score == 0.8
    assert result.ml_risk_level == RiskLevel.HIGH


@pytest.mark.asyncio
async def test_e2e_mmtc_medium_risk_renegotiate(decision_service):
    """Testa E2E: mMTC com risco médio → RENEGOTIATE"""
    intent = SLAIntent(
        intent_id="test-e2e-mmtc-001",
        tenant_id="test-tenant",
        service_type=SliceType.MMTC,
        sla_requirements={
            "latency": "1000ms",
            "throughput": "10Mbps",
            "reliability": 0.9
        }
    )
    
    ml_prediction = MLPrediction(
        risk_score=0.5,
        risk_level=RiskLevel.MEDIUM,
        confidence=0.8,
        explanation="Risk level medium (score: 0.50). Principal fator: throughput (9.0%).",
        timestamp="2025-01-27T00:00:00Z"
    )
    
    decision_input = DecisionInput(
        intent=intent,
        nest=None,
        ml_prediction=ml_prediction,
        context={}
    )
    
    result = await decision_service.process_decision_from_input(decision_input)
    
    assert result is not None
    assert result.intent_id == "test-e2e-mmtc-001"
    # Risco médio deve resultar em RENEGOTIATE
    assert result.action.value in ["RENEG", "AC", "REJ"]
    assert result.ml_risk_score == 0.5
    assert result.ml_risk_level == RiskLevel.MEDIUM


@pytest.mark.asyncio
async def test_e2e_performance(decision_service):
    """Testa performance do fluxo E2E (< 1s)"""
    import time
    
    intent = SLAIntent(
        intent_id="test-e2e-performance",
        service_type=SliceType.EMBB,
        sla_requirements={
            "latency": "50ms",
            "throughput": "100Mbps",
            "reliability": 0.99
        }
    )
    
    ml_prediction = MLPrediction(
        risk_score=0.3,
        risk_level=RiskLevel.LOW,
        confidence=0.9,
        explanation="Risk level low",
        timestamp="2025-01-27T00:00:00Z"
    )
    
    decision_input = DecisionInput(
        intent=intent,
        nest=None,
        ml_prediction=ml_prediction,
        context={}
    )
    
    start_time = time.time()
    result = await decision_service.process_decision_from_input(decision_input)
    end_time = time.time()
    
    elapsed_time = (end_time - start_time) * 1000  # Converter para ms
    
    assert result is not None
    # Performance deve ser < 1000ms (1s)
    assert elapsed_time < 1000, f"Fluxo E2E levou {elapsed_time:.2f}ms (esperado < 1000ms)"

