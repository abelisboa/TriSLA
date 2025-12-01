"""
Rule Engine - Decision Engine
Engine de regras para tomada de decisão
"""

from typing import Dict, Any, List
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class RuleEngine:
    """Engine de regras com thresholds"""
    
    def __init__(self):
        self.rules = self._load_rules()
        self.thresholds = self._load_thresholds()
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """Carrega regras de decisão"""
        return [
            {
                "id": "rule-001",
                "condition": "risk_level == 'high'",
                "action": "REJECT",
                "priority": 1
            },
            {
                "id": "rule-002",
                "condition": "sla_compliance < 0.9",
                "action": "REJECT",
                "priority": 1
            },
            {
                "id": "rule-003",
                "condition": "risk_level == 'medium'",
                "action": "RENEGOTIATE",
                "priority": 2
            },
            {
                "id": "rule-004",
                "condition": "sla_compliance >= 0.95",
                "action": "ACCEPT",
                "priority": 3
            }
        ]
    
    def _load_thresholds(self) -> Dict[str, float]:
        """Carrega thresholds"""
        return {
            "latency_max": 100.0,  # ms
            "throughput_min": 50.0,  # Mbps
            "packet_loss_max": 0.01,  # 1%
            "sla_compliance_min": 0.95  # 95%
        }
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia contexto contra regras"""
        with tracer.start_as_current_span("evaluate_rules") as span:
            matched_rules = []
            
            for rule in sorted(self.rules, key=lambda x: x["priority"]):
                if self._evaluate_condition(rule["condition"], context):
                    matched_rules.append(rule)
                    break  # Primeira regra que match
            
            if matched_rules:
                rule = matched_rules[0]
                reasoning = f"Rule {rule['id']} matched: {rule['condition']}"
                action = rule["action"]
            else:
                reasoning = "No rules matched, default to ACCEPT"
                action = "ACCEPT"
            
            span.set_attribute("rules.matched", len(matched_rules))
            span.set_attribute("rules.action", action)
            
            return {
                "action": action,
                "reasoning": reasoning,
                "confidence": 0.9,
                "matched_rules": [r["id"] for r in matched_rules]
            }
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Avalia condição de regra (simplificado)"""
        # Em produção, usar engine de regras completo (ex: pyknow, rules engine)
        try:
            # Substituir variáveis no contexto
            for key, value in context.items():
                condition = condition.replace(key, str(value))
            
            # Avaliar (simplificado - em produção usar parser seguro)
            return eval(condition)
        except:
            return False

