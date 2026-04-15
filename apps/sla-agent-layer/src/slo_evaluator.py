"""
SLO Evaluator - SLA-Agent Layer
Avalia métricas contra SLOs configurados por domínio
"""

from typing import Dict, Any, List, Optional
from opentelemetry import trace
import logging

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class SLOStatus:
    """Status de compliance de SLO"""
    OK = "OK"
    RISK = "RISK"
    VIOLATED = "VIOLATED"


class SLOEvaluator:
    """
    Avaliador de SLOs (Service Level Objectives)
    
    Avalia métricas coletadas contra SLOs configurados e determina:
    - OK: Métrica dentro do target
    - RISK: Métrica próxima do limite (threshold de risco)
    - VIOLATED: Métrica violou o target
    """
    
    def __init__(self, slo_config: Dict[str, Any]):
        """
        Inicializa avaliador com configuração de SLOs
        
        Args:
            slo_config: Configuração de SLOs no formato:
                {
                    "domain": "RAN",
                    "slos": [
                        {
                            "name": "latency",
                            "target": 10.0,
                            "unit": "ms",
                            "risk_threshold": 0.8,  # 80% do target = risco
                            "operator": "<="  # <= para latência (menor é melhor)
                        },
                        ...
                    ]
                }
        """
        self.domain = slo_config.get("domain", "UNKNOWN")
        self.slos = slo_config.get("slos", [])
        self.risk_threshold_default = 0.8  # 80% do target = risco
    
    def evaluate(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia métricas contra SLOs configurados
        
        Args:
            metrics: Dicionário com métricas coletadas (ex: {"latency": 12.5, "throughput": 850.0})
        
        Returns:
            {
                "status": "OK" | "RISK" | "VIOLATED",
                "domain": "RAN",
                "slos": [
                    {
                        "name": "latency",
                        "target": 10.0,
                        "current": 12.5,
                        "unit": "ms",
                        "status": "VIOLATED",
                        "compliance": False
                    },
                    ...
                ],
                "compliance_rate": 0.67,  # 2 de 3 SLOs em compliance
                "violations": ["latency"],
                "risks": []
            }
        """
        with tracer.start_as_current_span("evaluate_slos") as span:
            span.set_attribute("slo.domain", self.domain)
            span.set_attribute("slo.count", len(self.slos))
            
            evaluated_slos = []
            violations = []
            risks = []
            compliant_count = 0
            
            for slo_config in self.slos:
                slo_name = slo_config.get("name")
                slo_target = slo_config.get("target")
                slo_unit = slo_config.get("unit", "")
                slo_operator = slo_config.get("operator", "<=")  # <= para latência, >= para throughput
                risk_threshold = slo_config.get("risk_threshold", self.risk_threshold_default)
                
                # Obter valor atual da métrica
                current_value = metrics.get(slo_name)
                
                if current_value is None:
                    logger.warning(f"⚠️ Métrica '{slo_name}' não encontrada para domínio {self.domain}")
                    evaluated_slos.append({
                        "name": slo_name,
                        "target": slo_target,
                        "current": None,
                        "unit": slo_unit,
                        "status": "UNKNOWN",
                        "compliance": False
                    })
                    continue
                
                # Avaliar status
                status, compliance = self._evaluate_single_slo(
                    current_value=current_value,
                    target=slo_target,
                    operator=slo_operator,
                    risk_threshold=risk_threshold
                )
                
                if status == SLOStatus.VIOLATED:
                    violations.append(slo_name)
                elif status == SLOStatus.RISK:
                    risks.append(slo_name)
                
                if compliance:
                    compliant_count += 1
                
                evaluated_slos.append({
                    "name": slo_name,
                    "target": slo_target,
                    "current": current_value,
                    "unit": slo_unit,
                    "status": status,
                    "compliance": compliance
                })
            
            # Calcular compliance rate
            compliance_rate = compliant_count / len(self.slos) if self.slos else 0.0
            
            # Determinar status geral
            if violations:
                overall_status = SLOStatus.VIOLATED
            elif risks:
                overall_status = SLOStatus.RISK
            else:
                overall_status = SLOStatus.OK
            
            span.set_attribute("slo.overall_status", overall_status)
            span.set_attribute("slo.compliance_rate", compliance_rate)
            span.set_attribute("slo.violations_count", len(violations))
            span.set_attribute("slo.risks_count", len(risks))
            
            return {
                "status": overall_status,
                "domain": self.domain,
                "slos": evaluated_slos,
                "compliance_rate": compliance_rate,
                "violations": violations,
                "risks": risks,
                "timestamp": self._get_timestamp()
            }
    
    def _evaluate_single_slo(
        self,
        current_value: float,
        target: float,
        operator: str,
        risk_threshold: float
    ) -> tuple[str, bool]:
        """
        Avalia um único SLO
        
        Args:
            current_value: Valor atual da métrica
            target: Valor target do SLO
            operator: Operador de comparação ("<=", ">=", "==")
            risk_threshold: Threshold de risco (ex: 0.8 = 80% do target)
        
        Returns:
            (status, compliance) onde status é "OK"|"RISK"|"VIOLATED" e compliance é bool
        """
        if operator == "<=":
            # Para latência, jitter, packet_loss: menor é melhor
            if current_value <= target:
                return (SLOStatus.OK, True)
            elif current_value <= target / risk_threshold:
                return (SLOStatus.RISK, False)
            else:
                return (SLOStatus.VIOLATED, False)
        
        elif operator == ">=":
            # Para throughput, reliability: maior é melhor
            if current_value >= target:
                return (SLOStatus.OK, True)
            elif current_value >= target * risk_threshold:
                return (SLOStatus.RISK, False)
            else:
                return (SLOStatus.VIOLATED, False)
        
        elif operator == "==":
            # Para valores exatos (menos comum)
            tolerance = target * (1 - risk_threshold)
            if abs(current_value - target) <= tolerance:
                return (SLOStatus.OK, True)
            elif abs(current_value - target) <= tolerance * 2:
                return (SLOStatus.RISK, False)
            else:
                return (SLOStatus.VIOLATED, False)
        
        else:
            logger.warning(f"⚠️ Operador desconhecido: {operator}, usando <= como padrão")
            if current_value <= target:
                return (SLOStatus.OK, True)
            else:
                return (SLOStatus.VIOLATED, False)
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

