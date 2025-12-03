"""
Unit Tests - Decision Engine RuleEngine
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
DE_SRC = BASE_DIR / "apps" / "decision-engine" / "src"
sys.path.insert(0, str(DE_SRC))

from rule_engine import RuleEngine


@pytest.fixture
def rule_engine():
    """Fixture para criar RuleEngine"""
    return RuleEngine()


@pytest.mark.asyncio
async def test_rule_engine_high_risk_reject(rule_engine):
    """Testa regra: risco alto → REJECT"""
    context = {
        "risk_level": "high",
        "risk_score": 0.8,
        "sla_compliance": 0.95
    }
    
    result = await rule_engine.evaluate(context)
    
    assert result is not None
    assert result["action"] == "REJECT"
    assert "rule-001" in result.get("matched_rules", [])


@pytest.mark.asyncio
async def test_rule_engine_low_sla_compliance_reject(rule_engine):
    """Testa regra: SLA compliance baixo → REJECT"""
    context = {
        "risk_level": "medium",
        "risk_score": 0.5,
        "sla_compliance": 0.85  # < 0.9
    }
    
    result = await rule_engine.evaluate(context)
    
    assert result is not None
    assert result["action"] == "REJECT"
    assert "rule-002" in result.get("matched_rules", [])


@pytest.mark.asyncio
async def test_rule_engine_medium_risk_renegotiate(rule_engine):
    """Testa regra: risco médio → RENEGOTIATE"""
    context = {
        "risk_level": "medium",
        "risk_score": 0.5,
        "sla_compliance": 0.95
    }
    
    result = await rule_engine.evaluate(context)
    
    assert result is not None
    assert result["action"] == "RENEGOTIATE"
    assert "rule-003" in result.get("matched_rules", [])


@pytest.mark.asyncio
async def test_rule_engine_high_sla_compliance_accept(rule_engine):
    """Testa regra: SLA compliance alto → ACCEPT"""
    context = {
        "risk_level": "low",
        "risk_score": 0.3,
        "sla_compliance": 0.98  # >= 0.95
    }
    
    result = await rule_engine.evaluate(context)
    
    assert result is not None
    assert result["action"] == "ACCEPT"
    assert "rule-004" in result.get("matched_rules", [])


@pytest.mark.asyncio
async def test_rule_engine_default_accept(rule_engine):
    """Testa comportamento padrão: ACCEPT quando nenhuma regra match"""
    context = {
        "risk_level": "low",
        "risk_score": 0.2,
        "sla_compliance": 0.92  # Entre 0.9 e 0.95
    }
    
    result = await rule_engine.evaluate(context)
    
    assert result is not None
    assert result["action"] == "ACCEPT"
    assert "No rules matched" in result.get("reasoning", "")


@pytest.mark.asyncio
async def test_rule_engine_thresholds(rule_engine):
    """Testa que thresholds estão carregados"""
    assert rule_engine.thresholds is not None
    assert "latency_max" in rule_engine.thresholds
    assert "throughput_min" in rule_engine.thresholds
    assert "packet_loss_max" in rule_engine.thresholds
    assert "sla_compliance_min" in rule_engine.thresholds


@pytest.mark.asyncio
async def test_rule_engine_rules_loaded(rule_engine):
    """Testa que regras estão carregadas"""
    assert rule_engine.rules is not None
    assert len(rule_engine.rules) > 0
    assert all("id" in rule for rule in rule_engine.rules)
    assert all("condition" in rule for rule in rule_engine.rules)
    assert all("action" in rule for rule in rule_engine.rules)
    assert all("priority" in rule for rule in rule_engine.rules)

