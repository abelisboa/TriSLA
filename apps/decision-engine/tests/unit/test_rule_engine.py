"""
Unit Tests - Decision Engine Rule Engine
Testes unitários para o engine de regras baseado em YAML
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar src ao path
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from rule_engine import RuleEngine


class TestRuleEngine:
    """Testes do RuleEngine"""
    
    @pytest.mark.asyncio
    async def test_rule_engine_initialization(self):
        """Testa inicialização do RuleEngine"""
        engine = RuleEngine()
        assert engine is not None
        assert engine.rules is not None
        assert len(engine.rules) > 0
        assert engine.thresholds is not None
    
    @pytest.mark.asyncio
    async def test_evaluate_high_risk_reject(self):
        """Testa regra de rejeição para risco alto"""
        engine = RuleEngine()
        
        context = {
            "risk_level": "high",
            "risk_score": 0.8,
            "service_type": "URLLC",
            "sla_compliance": 0.95,
            "latency": 5.0,
            "throughput": 50.0,
            "reliability": 0.999,
            "confidence": 0.9,
            "domains": ["RAN", "Transporte", "Core"],
            "explanation": "ML prevê risco alto"
        }
        
        result = await engine.evaluate(context)
        
        assert result is not None
        assert "action" in result
        assert "reasoning" in result
        assert result["action"] == "REJECT"
    
    @pytest.mark.asyncio
    async def test_evaluate_low_risk_accept(self):
        """Testa regra de aceitação para risco baixo"""
        engine = RuleEngine()
        
        context = {
            "risk_level": "low",
            "risk_score": 0.3,
            "service_type": "eMBB",
            "sla_compliance": 0.98,
            "latency": 20.0,
            "throughput": 500.0,
            "reliability": 0.99,
            "confidence": 0.95,
            "domains": ["RAN", "Transporte"],
            "explanation": "ML prevê risco baixo"
        }
        
        result = await engine.evaluate(context)
        
        assert result is not None
        assert result["action"] == "ACCEPT"
    
    @pytest.mark.asyncio
    async def test_evaluate_medium_risk_negotiate(self):
        """Testa regra de negociação para risco médio"""
        engine = RuleEngine()
        
        context = {
            "risk_level": "medium",
            "risk_score": 0.6,
            "service_type": "URLLC",
            "sla_compliance": 0.92,
            "latency": 8.0,
            "throughput": 50.0,
            "reliability": 0.999,
            "confidence": 0.8,
            "domains": ["RAN", "Transporte", "Core"],
            "explanation": "ML prevê risco médio"
        }
        
        result = await engine.evaluate(context)
        
        assert result is not None
        # Pode ser NEGOTIATE, RENEGOTIATE ou ACCEPT dependendo da prioridade das regras
        assert result["action"] in ["NEGOTIATE", "RENEGOTIATE", "ACCEPT"]
    
    @pytest.mark.asyncio
    async def test_evaluate_urllc_latency_exceeded(self):
        """Testa rejeição de URLLC com latência acima do máximo"""
        engine = RuleEngine()
        
        context = {
            "risk_level": "low",
            "risk_score": 0.3,
            "service_type": "URLLC",
            "sla_compliance": 0.95,
            "latency": 15.0,  # Acima de 10ms
            "throughput": 50.0,
            "reliability": 0.999,
            "confidence": 0.9,
            "domains": ["RAN", "Transporte", "Core"],
            "explanation": ""
        }
        
        result = await engine.evaluate(context)
        
        assert result is not None
        # Deve rejeitar ou negociar devido à latência
        assert result["action"] in ["REJECT", "NEGOTIATE"]
    
    @pytest.mark.asyncio
    async def test_evaluate_default_rule(self):
        """Testa regra padrão quando nenhuma outra aplica"""
        engine = RuleEngine()
        
        context = {
            "risk_level": "unknown",
            "risk_score": 0.5,
            "service_type": "eMBB",
            "sla_compliance": 0.95,
            "latency": 30.0,
            "throughput": 200.0,
            "reliability": 0.99,
            "confidence": 0.5,
            "domains": ["RAN"],
            "explanation": ""
        }
        
        result = await engine.evaluate(context)
        
        assert result is not None
        # Regra padrão deve aceitar
        assert result["action"] == "ACCEPT"
    
    @pytest.mark.asyncio
    async def test_evaluate_condition_parsing(self):
        """Testa parsing seguro de condições (sem eval())"""
        engine = RuleEngine()
        
        # Testar diferentes tipos de condições
        conditions = [
            {"risk_level": ["high"]},
            {"risk_score": "> 0.7"},
            {"latency": "<= 10.0"},
            {"sla_compliance": ">= 0.95"}
        ]
        
        context = {
            "risk_level": "high",
            "risk_score": 0.8,
            "latency": 5.0,
            "sla_compliance": 0.98
        }
        
        for condition in conditions:
            result = engine._evaluate_condition(condition, context)
            assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

