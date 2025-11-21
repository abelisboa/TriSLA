"""
Decision Maker - Decision Engine
Toma decisões baseadas em regras e contexto
"""

from typing import Dict, Any
from enum import Enum
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rule_engine import RuleEngine

tracer = trace.get_tracer(__name__)


class DecisionAction(str, Enum):
    """Ações possíveis"""
    ACCEPT = "AC"  # Accept
    RENEGOTIATE = "RENEG"  # Renegotiate
    REJECT = "REJ"  # Reject


class DecisionMaker:
    """Faz decisões baseadas em regras e contexto"""
    
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
    
    async def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Toma decisão baseada em contexto"""
        with tracer.start_as_current_span("decide") as span:
            # Aplicar regras
            rules_result = await self.rule_engine.evaluate(context)
            
            # Determinar ação
            action = self._determine_action(rules_result, context)
            
            decision = {
                "decision_id": f"dec-{context.get('intent_id', 'unknown')}",
                "action": action.value,
                "reasoning": rules_result.get("reasoning"),
                "confidence": rules_result.get("confidence", 0.8),
                "timestamp": self._get_timestamp()
            }
            
            span.set_attribute("decision.action", action.value)
            return decision
    
    def _determine_action(self, rules_result: Dict[str, Any], context: Dict[str, Any]) -> DecisionAction:
        """Determina ação baseada em regras"""
        risk_level = context.get("risk_level", "medium")
        sla_compliance = context.get("sla_compliance", 0.95)
        
        if risk_level == "high" or sla_compliance < 0.9:
            return DecisionAction.REJECT
        elif risk_level == "medium" or sla_compliance < 0.95:
            return DecisionAction.RENEGOTIATE
        else:
            return DecisionAction.ACCEPT
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

