"""
Rule Engine - Decision Engine
Engine de regras seguro baseado em YAML (sem eval())
"""

from typing import Dict, Any, List, Optional
from opentelemetry import trace
import os
import yaml
from asteval import Interpreter

tracer = trace.get_tracer(__name__)


class RuleEngine:
    """Engine de regras seguro com carregamento de YAML"""
    
    def __init__(self, rules_path: str = None):
        """
        Inicializa engine de regras
        
        Args:
            rules_path: Caminho para arquivo YAML de regras (padrão: config/decision_rules.yaml)
        """
        if rules_path is None:
            rules_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config",
                "decision_rules.yaml"
            )
        self.rules_path = rules_path
        self.rules = self._load_rules()
        self.thresholds = self._load_thresholds()
        self.asteval = Interpreter()  # Parser seguro para condições
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """Carrega regras de decisão do arquivo YAML"""
        try:
            if not os.path.exists(self.rules_path):
                print(f"⚠️ Arquivo de regras não encontrado: {self.rules_path}")
                print("   Usando regras padrão hardcoded como fallback")
                return self._get_default_rules()
            
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            rules = config.get("rules", [])
            print(f"✅ {len(rules)} regras carregadas de {self.rules_path}")
            return rules
            
        except Exception as e:
            print(f"❌ Erro ao carregar regras: {e}")
            print("   Usando regras padrão hardcoded como fallback")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> List[Dict[str, Any]]:
        """Retorna regras padrão como fallback"""
        return [
            {
                "id": "rule-default-reject-high-risk",
                "description": "Rejeita risco alto (fallback)",
                "condition": {"risk_level": ["high"]},
                "action": "REJECT",
                "priority": 1
            },
            {
                "id": "rule-default-accept-low-risk",
                "description": "Aceita risco baixo (fallback)",
                "condition": {"risk_level": ["low"]},
                "action": "ACCEPT",
                "priority": 10
            }
        ]
    
    def _load_thresholds(self) -> Dict[str, Any]:
        """Carrega thresholds do arquivo YAML"""
        try:
            if not os.path.exists(self.rules_path):
                return self._get_default_thresholds()
            
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            thresholds = config.get("thresholds", {})
            return thresholds
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar thresholds: {e}")
            return self._get_default_thresholds()
    
    def _get_default_thresholds(self) -> Dict[str, Any]:
        """Retorna thresholds padrão como fallback"""
        return {
            "latency_max": {"URLLC": 10.0, "eMBB": 50.0, "mMTC": 1000.0},
            "throughput_min": {"URLLC": 1.0, "eMBB": 100.0, "mMTC": 0.00016},
            "reliability_min": {"URLLC": 0.99999, "eMBB": 0.99, "mMTC": 0.9},
            "packet_loss_max": {"URLLC": 0.00001, "eMBB": 0.01, "mMTC": 0.1},
            "sla_compliance_min": 0.95
        }
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia contexto contra regras carregadas do YAML
        
        Args:
            context: Dicionário com contexto da decisão:
                - risk_level: "low", "medium", "high"
                - risk_score: float (0-1)
                - service_type: "URLLC", "eMBB", "mMTC"
                - sla_compliance: float (0-1)
                - latency: float (ms)
                - throughput: float (Mbps)
                - reliability: float (0-1)
                - confidence: float (0-1)
                - domains: List[str]
                - explanation: str
        
        Returns:
            Dicionário com ação, reasoning e matched_rules
        """
        with tracer.start_as_current_span("evaluate_rules") as span:
            span.set_attribute("rules.total", len(self.rules))
            span.set_attribute("context.risk_level", context.get("risk_level", "unknown"))
            span.set_attribute("context.service_type", context.get("service_type", "unknown"))
            
            matched_rules = []
            
            # Ordenar regras por prioridade (menor número = maior prioridade)
            sorted_rules = sorted(self.rules, key=lambda x: x.get("priority", 100))
            
            for rule in sorted_rules:
                if self._evaluate_condition(rule.get("condition", {}), context):
                    matched_rules.append(rule)
                    # Primeira regra que match (maior prioridade) vence
                    break
            
            if matched_rules:
                rule = matched_rules[0]
                reasoning = self._generate_reasoning(rule, context)
                action = rule.get("action", "ACCEPT")
            else:
                reasoning = "Nenhuma regra aplicou. Decisão padrão: ACCEPT"
                action = "ACCEPT"
            
            span.set_attribute("rules.matched", len(matched_rules))
            span.set_attribute("rules.action", action)
            if matched_rules:
                span.set_attribute("rules.matched_id", matched_rules[0].get("id"))
            
            return {
                "action": action,
                "reasoning": reasoning,
                "confidence": context.get("confidence", 0.8),
                "matched_rules": [r.get("id") for r in matched_rules],
                "rule_id": matched_rules[0].get("id") if matched_rules else None
            }
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Avalia condição de regra de forma SEGURA (sem eval())
        
        Args:
            condition: Dicionário com condições (ex: {"risk_level": ["high"], "risk_score": "> 0.7"})
            context: Contexto da decisão
        
        Returns:
            True se condição for satisfeita
        """
        try:
            # Condição especial: always = true
            if condition.get("always") is True:
                return True
            
            # Avaliar cada campo da condição
            for field, condition_value in condition.items():
                if field == "always":
                    continue
                
                context_value = context.get(field)
                
                # Se valor do contexto é None, condição falha
                if context_value is None:
                    return False
                
                # Se condição é lista (ex: risk_level: ["high", "medium"])
                if isinstance(condition_value, list):
                    if context_value not in condition_value:
                        return False
                
                # Se condição é string com operador (ex: "> 0.7", "<= 10.0")
                elif isinstance(condition_value, str):
                    if not self._evaluate_comparison(field, condition_value, context_value):
                        return False
                
                # Se condição é valor direto (ex: sla_compliance: 0.95)
                else:
                    if context_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao avaliar condição: {e}")
            return False
    
    def _evaluate_comparison(self, field: str, condition_str: str, context_value: Any) -> bool:
        """
        Avalia comparação de forma SEGURA usando asteval
        
        Args:
            field: Nome do campo
            condition_str: String com operador (ex: "> 0.7", "<= 10.0")
            context_value: Valor do contexto
        
        Returns:
            True se comparação for satisfeita
        """
        try:
            # Parsear operador e valor
            # Exemplos: "> 0.7", "<= 10.0", ">= 0.95", "< 0.4"
            import re
            
            # Padrão: operador + número
            match = re.match(r'([<>=!]+)\s*([\d.]+)', condition_str.strip())
            if not match:
                # Tentar como expressão completa
                # Criar expressão segura: context_value <operador> <valor>
                expr = f"{context_value} {condition_str}"
            else:
                operator = match.group(1)
                value = float(match.group(2))
                expr = f"{context_value} {operator} {value}"
            
            # Avaliar usando asteval (seguro)
            self.asteval.symtable = {"context_value": context_value}
            result = self.asteval(expr)
            
            return bool(result) if result is not None else False
            
        except Exception as e:
            print(f"⚠️ Erro ao avaliar comparação '{condition_str}': {e}")
            return False
    
    def _generate_reasoning(self, rule: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Gera reasoning baseado no template da regra
        
        Args:
            rule: Regra que foi aplicada
            context: Contexto da decisão
        
        Returns:
            String com reasoning formatado
        """
        template = rule.get("reasoning_template", "Regra {id} aplicada: {action}")
        
        # Substituir variáveis no template
        reasoning = template.format(
            id=rule.get("id", "unknown"),
            action=rule.get("action", "UNKNOWN"),
            service_type=context.get("service_type", "unknown"),
            risk_level=context.get("risk_level", "unknown"),
            risk_score=context.get("risk_score", 0.0),
            sla_compliance=context.get("sla_compliance", 0.0),
            latency=context.get("latency", 0.0),
            throughput=context.get("throughput", 0.0),
            confidence=context.get("confidence", 0.0),
            domains=", ".join(context.get("domains", [])),
            explanation=context.get("explanation", "")
        )
        
        return reasoning
