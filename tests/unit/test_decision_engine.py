"""
Unit Tests - Decision Engine
"""

import pytest
import sys
from pathlib import Path

# Adiciona os diretórios src ao path (diretórios com hífen não podem ser importados diretamente)
BASE_DIR = Path(__file__).parent.parent.parent
DECISION_ENGINE_SRC = BASE_DIR / "apps" / "decision-engine" / "src"
sys.path.insert(0, str(DECISION_ENGINE_SRC))

from decision_maker import DecisionMaker, DecisionAction
from rule_engine import RuleEngine


class TestDecisionMaker:
    """Testes do DecisionMaker"""
    
    @pytest.mark.asyncio
    async def test_decide_accept(self):
        """Testa decisão ACCEPT"""
        rule_engine = RuleEngine()
        maker = DecisionMaker(rule_engine)
        
        context = {
            "risk_level": "low",
            "sla_compliance": 0.98
        }
        
        decision = await maker.decide(context)
        assert decision["action"] == DecisionAction.ACCEPT.value
    
    @pytest.mark.asyncio
    async def test_decide_reject(self):
        """Testa decisão REJECT"""
        rule_engine = RuleEngine()
        maker = DecisionMaker(rule_engine)
        
        context = {
            "risk_level": "high",
            "sla_compliance": 0.85
        }
        
        decision = await maker.decide(context)
        assert decision["action"] == DecisionAction.REJECT.value


class TestRuleEngine:
    """Testes do RuleEngine"""
    
    @pytest.mark.asyncio
    async def test_evaluate_rules(self):
        """Testa avaliação de regras"""
        engine = RuleEngine()
        context = {
            "risk_level": "medium",
            "sla_compliance": 0.95
        }
        
        result = await engine.evaluate(context)
        assert result["action"] in ["ACCEPT", "RENEGOTIATE", "REJECT"]

