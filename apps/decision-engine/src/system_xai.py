"""
System-Aware XAI - Decision Engine
Explica decisões baseado no sistema físico, não apenas no modelo ML
FASE 2 - PROMPT_S30
"""

from typing import Dict, Any
from models import DecisionAction, DecisionResult

def explain_decision(snapshot: Dict[str, Any], decision_result: DecisionResult) -> Dict[str, Any]:
    """
    Explica a decisão baseado no sistema físico (domínios, métricas, bottlenecks).
    
    Esta é uma explicação System-Aware, não ML-XAI.
    Foca em causas físicas e estruturais da decisão.
    
    Args:
        snapshot: Snapshot da decisão (de decision_snapshot.py)
        decision_result: Resultado da decisão
        
    Returns:
        Explicação estruturada e determinística
    """
    
    decision = decision_result.action
    bottleneck_domain = snapshot.get("bottleneck_domain")
    bottleneck_metric = snapshot.get("bottleneck_metric")
    domains = snapshot.get("domains", {})
    sla_compliance = snapshot.get("sla_compliance", 0.95)
    
    explanation = {
        "decision": decision_result.action.value,
        "cause": None,
        "explanation": "",
        "system_aware": True,
        "domains_evaluated": list(domains.keys()) if domains else []
    }
    
    # ACCEPT: Todos os domínios atendem os requisitos
    if decision == DecisionAction.ACCEPT:
        explanation["cause"] = "ALL_DOMAINS_COMPLIANT"
        domains_str = ", ".join(explanation["domains_evaluated"])
        explanation["explanation"] = (
            f"Todos os domínios ({domains_str}) " +
            f"atendem os requisitos do SLA. Compliance: {sla_compliance:.2%}. " +
            f"Sistema viável para slice tipo {snapshot.get('slice_type', 'UNKNOWN')}."
        )
    
    # RENEG: Identificar domínio + métrica violada
    elif decision == DecisionAction.RENEGOTIATE:
        if bottleneck_domain and bottleneck_metric:
            # Extrair valor da métrica violada
            domain_data = domains.get(bottleneck_domain, {})
            metric_value = domain_data.get(bottleneck_metric)
            
            # Determinar threshold esperado baseado no slice_type
            slice_type = snapshot.get("slice_type", "").upper()
            threshold = None
            
            if bottleneck_metric == "latency_ms":
                if slice_type == "URLLC":
                    threshold = 10.0
                elif slice_type == "EMBB":
                    threshold = 20.0
                else:
                    threshold = 50.0
            elif bottleneck_metric == "throughput_mbps":
                threshold = 100.0  # Default
            
            # Construir explicação
            if metric_value is not None and threshold is not None:
                explanation["cause"] = f"{bottleneck_domain.upper()}_{bottleneck_metric.upper()}"
                explanation["explanation"] = (
                    f"{bottleneck_domain.capitalize()} {bottleneck_metric} excede threshold do SLA " +
                    f"({metric_value} > {threshold}). " +
                    f"Compliance atual: {sla_compliance:.2%}. " +
                    f"Requer renegociação de SLOs ou alocação de recursos adicionais."
                )
            else:
                explanation["cause"] = f"{bottleneck_domain.upper()}_VIOLATION"
                explanation["explanation"] = (
                    f"Domínio {bottleneck_domain} apresenta violação de requisitos. " +
                    f"Compliance: {sla_compliance:.2%}. " +
                    f"Requer renegociação."
                )
        else:
            # Fallback se não identificar bottleneck específico
            explanation["cause"] = "MEDIUM_RISK"
            domains_str = ", ".join(explanation["domains_evaluated"])
            explanation["explanation"] = (
                f"SLA requer renegociação. Compliance: {sla_compliance:.2%}. " +
                f"ML prevê risco médio. Domínios avaliados: {domains_str}."
            )
    
    # REJECT: Inviabilidade estrutural
    elif decision == DecisionAction.REJECT:
        if bottleneck_domain and bottleneck_metric:
            domain_data = domains.get(bottleneck_domain, {})
            metric_value = domain_data.get(bottleneck_metric)
            
            explanation["cause"] = f"{bottleneck_domain.upper()}_INFEASIBLE"
            explanation["explanation"] = (
                f"Inviabilidade estrutural no domínio {bottleneck_domain}. " +
                f"Métrica crítica {bottleneck_metric} não atende requisitos mínimos. " +
                f"Compliance: {sla_compliance:.2%}. " +
                f"SLA não pode ser atendido com os recursos disponíveis."
            )
        else:
            explanation["cause"] = "HIGH_RISK_INFEASIBLE"
            explanation["explanation"] = (
                f"SLA rejeitado por inviabilidade estrutural. " +
                f"Compliance: {sla_compliance:.2%}. " +
                f"ML prevê risco alto. Sistema não pode garantir requisitos do slice tipo {snapshot.get('slice_type', 'UNKNOWN')}."
            )
    
    else:
        # Fallback para decisões desconhecidas
        explanation["cause"] = "UNKNOWN"
        explanation["explanation"] = f"Decisão {decision.value} requer análise adicional."
    
    return explanation
