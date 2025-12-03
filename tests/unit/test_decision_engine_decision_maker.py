"""
Unit Tests - Decision Engine DecisionMaker
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
DE_SRC = BASE_DIR / "apps" / "decision-engine" / "src"
sys.path.insert(0, str(DE_SRC))

from decision_maker import DecisionMaker, DecisionAction
from rule_engine import RuleEngine


@pytest.fixture
def decision_maker():
    """Fixture para criar DecisionMaker"""
    rule_engine = RuleEngine()
    return DecisionMaker(rule_engine)


@pytest.mark.asyncio
async def test_decision_maker_reject_high_risk(decision_maker):
    """Testa decisão REJECT para risco alto"""
    context = {
        "intent_id": "test-intent-001",
        "risk_level": "high",
        "risk_score": 0.8,
        "sla_compliance": 0.95
    }
    
    decision = await decision_maker.decide(context)
    
    assert decision is not None
    assert decision["action"] == DecisionAction.REJECT.value
    assert decision["decision_id"] == "dec-test-intent-001"
    assert "reasoning" in decision
    assert "confidence" in decision
    assert "timestamp" in decision


@pytest.mark.asyncio
async def test_decision_maker_renegotiate_medium_risk(decision_maker):
    """Testa decisão RENEGOTIATE para risco médio"""
    context = {
        "intent_id": "test-intent-002",
        "risk_level": "medium",
        "risk_score": 0.5,
        "sla_compliance": 0.95
    }
    
    decision = await decision_maker.decide(context)
    
    assert decision is not None
    assert decision["action"] == DecisionAction.RENEGOTIATE.value
    assert decision["decision_id"] == "dec-test-intent-002"


@pytest.mark.asyncio
async def test_decision_maker_accept_low_risk(decision_maker):
    """Testa decisão ACCEPT para risco baixo"""
    context = {
        "intent_id": "test-intent-003",
        "risk_level": "low",
        "risk_score": 0.2,
        "sla_compliance": 0.98
    }
    
    decision = await decision_maker.decide(context)
    
    assert decision is not None
    assert decision["action"] == DecisionAction.ACCEPT.value
    assert decision["decision_id"] == "dec-test-intent-003"


@pytest.mark.asyncio
async def test_decision_maker_reject_low_sla_compliance(decision_maker):
    """Testa decisão REJECT para SLA compliance baixo"""
    context = {
        "intent_id": "test-intent-004",
        "risk_level": "medium",
        "risk_score": 0.5,
        "sla_compliance": 0.85  # < 0.9
    }
    
    decision = await decision_maker.decide(context)
    
    assert decision is not None
    assert decision["action"] == DecisionAction.REJECT.value


@pytest.mark.asyncio
async def test_decision_maker_renegotiate_medium_sla_compliance(decision_maker):
    """Testa decisão RENEGOTIATE para SLA compliance médio"""
    context = {
        "intent_id": "test-intent-005",
        "risk_level": "low",
        "risk_score": 0.3,
        "sla_compliance": 0.92  # Entre 0.9 e 0.95
    }
    
    decision = await decision_maker.decide(context)
    
    assert decision is not None
    assert decision["action"] == DecisionAction.RENEGOTIATE.value


@pytest.mark.asyncio
async def test_decision_maker_confidence(decision_maker):
    """Testa que confidence está presente e no range válido"""
    context = {
        "intent_id": "test-intent-006",
        "risk_level": "low",
        "risk_score": 0.2,
        "sla_compliance": 0.98
    }
    
    decision = await decision_maker.decide(context)
    
    assert "confidence" in decision
    assert 0.0 <= decision["confidence"] <= 1.0

