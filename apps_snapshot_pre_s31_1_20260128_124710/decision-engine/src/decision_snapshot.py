"""
Decision Snapshot - Decision Engine
Constrói snapshot completo e determinístico da decisão
FASE 1 - PROMPT_S30
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from models import DecisionResult, DecisionAction, SliceType

def build_decision_snapshot(context: Dict[str, Any], decision_result: DecisionResult) -> Dict[str, Any]:
    """
    Constrói snapshot completo e determinístico da decisão.
    
    Args:
        context: Contexto da decisão (intent, nest, ml_prediction, etc.)
        decision_result: Resultado da decisão
        
    Returns:
        Snapshot estruturado com todos os dados necessários
    """
    
    # Extrair dados do contexto
    intent = context.get('intent')
    nest = context.get('nest')
    ml_prediction = context.get('ml_prediction')
    resources = context.get('resources', {})
    
    # Determinar slice_type
    slice_type = "UNKNOWN"
    if intent and hasattr(intent, 'service_type'):
        slice_type = intent.service_type.value if isinstance(intent.service_type, SliceType) else str(intent.service_type)
    elif intent and isinstance(intent, dict):
        slice_type = intent.get('service_type', 'UNKNOWN')
    
    # Calcular SLA compliance (baseado no risk_score invertido)
    sla_compliance = 1.0 - decision_result.ml_risk_score if decision_result.ml_risk_score else 0.95
    
    # Construir snapshot por domínio
    domains_snapshot = {}
    
    # RAN Domain
    ran_metrics = {
        "latency_ms""": None,
        "throughput_mbps": None,
        "reliability": None,
        "status": "unknown"
    }
    if decision_result.domains and "RAN" in decision_result.domains:
        # Extrair métricas do intent ou nest
        if intent and hasattr(intent, 'sla_requirements'):
            sla_reqs = intent.sla_requirements if hasattr(intent.sla_requirements, '__iter__') and not isinstance(intent.sla_requirements, str) else {}
            if isinstance(sla_reqs, dict):
                if "latency" in sla_reqs:
                    latency_str = str(sla_reqs["latency"]).replace("ms", ).strip()
                    try:
                        ran_metrics["latency_ms"] = float(latency_str)
                    except (ValueError, TypeError):
                        pass
                if "throughput" in sla_reqs:
                    throughput_str = str(sla_reqs["throughput"]).replace("Mbps", ).replace("Gbps", 000).strip()
                    try:
                        ran_metrics["throughput_mbps"] = float(throughput_str)
                    except (ValueError, TypeError):
                        pass
                if "reliability" in sla_reqs:
                    try:
                        ran_metrics["reliability"] = float(sla_reqs["reliability"])
                    except (ValueError, TypeError):
                        pass
        ran_metrics["status"] = "evaluated"
    domains_snapshot["RAN"] = ran_metrics
    
    # Transport Domain
    transport_metrics = {
        "latency_ms": None,
        "bandwidth_mbps": None,
        "jitter_ms": None,
        "status": "unknown"
    }
    if decision_result.domains and "Transport" in decision_result.domains:
        # Similar extraction for "transport"
        if intent and hasattr(intent, 'sla_requirements'):
            sla_reqs = intent.sla_requirements if hasattr(intent.sla_requirements, '__iter__') and not isinstance(intent.sla_requirements, str) else {}
            if isinstance(sla_reqs, dict):
                if "latency" in sla_reqs:
                    latency_str = str(sla_reqs["latency"]).replace("ms", ).strip()
                    try:
                        transport_metrics["latency_ms"] = float(latency_str)
                    except (ValueError, TypeError):
                        pass
        transport_metrics["status"] = "evaluated"
    domains_snapshot["Transport"] = transport_metrics
    
    # Core Domain
    core_metrics = {
        "latency_ms": None,
        "throughput_mbps": None,
        "availability": None,
        "status": "unknown"
    }
    if decision_result.domains and "Core" in decision_result.domains:
        # Similar extraction for "core"
        if intent and hasattr(intent, 'sla_requirements'):
            sla_reqs = intent.sla_requirements if hasattr(intent.sla_requirements, '__iter__') and not isinstance(intent.sla_requirements, str) else {}
            if isinstance(sla_reqs, dict):
                if "latency" in sla_reqs:
                    latency_str = str(sla_reqs["latency"]).replace("ms", ).strip()
                    try:
                        core_metrics["latency_ms"] = float(latency_str)
                    except (ValueError, TypeError):
                        pass
        core_metrics["status"] = "evaluated"
    domains_snapshot["Core"] = core_metrics
    
    # Identificar bottleneck domain
    bottleneck_domain = None
    bottleneck_metric = None
    
    if decision_result.action == DecisionAction.RENEGOTIATE or decision_result.action == DecisionAction.REJECT:
        # Identificar domínio com maior problema baseado na reasoning
        reasoning_lower = decision_result.reasoning.lower()
        if "transport" in reasoning_lower or "transporte" in reasoning_lower:
            bottleneck_domain = "Transport"
            if "latency" in reasoning_lower:
                bottleneck_metric = "latency_ms"
        elif "ran" in reasoning_lower or "RAN" in reasoning_lower:
            bottleneck_domain = "RAN"
            if "latency" in reasoning_lower:
                bottleneck_metric = "latency_ms"
            elif "throughput" in reasoning_lower:
                bottleneck_metric = "throughput_mbps"
        elif "core" in reasoning_lower:
            bottleneck_domain = "Core"
            if "latency" in reasoning_lower:
                bottleneck_metric = "latency_ms"
    
    # Construir snapshot final
    snapshot = {
        "sla_id": decision_result.intent_id,
        "decision": decision_result.action.value,
        "slice_type": slice_type,
        "sla_compliance": round(sla_compliance, 2),
        "domains": domains_snapshot,
        "bottleneck_domain": bottleneck_domain,
        "bottleneck_metric": bottleneck_metric,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "decision_id": decision_result.decision_id,
        "ml_risk_score": decision_result.ml_risk_score,
        "ml_risk_level": decision_result.ml_risk_level.value if decision_result.ml_risk_level else None,
        "confidence": decision_result.confidence,
        "reasoning": decision_result.reasoning
    }
    
    return snapshot
