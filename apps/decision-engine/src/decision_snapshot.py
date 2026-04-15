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
    intent = context.get("intent")
    nest = context.get("nest")
    ml_prediction = context.get("ml_prediction")
    resources = context.get("resources", {})

    # Determinar slice_type
    slice_type = "UNKNOWN"
    if intent and hasattr(intent, "service_type"):
        slice_type = (
            intent.service_type.value if isinstance(intent.service_type, SliceType) else str(intent.service_type)
        )
    elif intent and isinstance(intent, dict):
        slice_type = intent.get("service_type", "UNKNOWN")

    meta = decision_result.metadata if isinstance(decision_result.metadata, dict) else {}
    adj_risk = meta.get("slice_adjusted_risk_score")
    raw_risk = meta.get("raw_risk_score")
    if adj_risk is None and ml_prediction is not None:
        adj_risk = getattr(ml_prediction, "slice_adjusted_risk_score", None)
    if raw_risk is None and ml_prediction is not None:
        raw_risk = getattr(ml_prediction, "raw_risk_score", None)

    effective_risk = adj_risk if adj_risk is not None else decision_result.ml_risk_score
    # Calcular SLA compliance (baseado no risco efetivo)
    sla_compliance = 1.0 - effective_risk if effective_risk is not None else 0.95

    # Construir snapshot por domínio
    domains_snapshot = {}

    # RAN Domain
    ran_metrics = {
        "latency_ms": None,
        "throughput_mbps": None,
        "reliability": None,
        "status": "unknown",
    }
    if decision_result.domains and "RAN" in decision_result.domains:
        if intent and hasattr(intent, "sla_requirements"):
            sla_reqs = (
                intent.sla_requirements
                if hasattr(intent.sla_requirements, "__iter__") and not isinstance(intent.sla_requirements, str)
                else {}
            )
            if isinstance(sla_reqs, dict):
                if "latency" in sla_reqs:
                    latency_str = str(sla_reqs["latency"]).replace("ms", "").strip()
                    try:
                        ran_metrics["latency_ms"] = float(latency_str)
                    except (ValueError, TypeError):
                        pass
                if "throughput" in sla_reqs:
                    throughput_str = str(sla_reqs["throughput"]).replace("Mbps", "").replace("Gbps", "000").strip()
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
        "status": "unknown",
    }
    if decision_result.domains and ("Transport" in decision_result.domains or "Transporte" in decision_result.domains):
        if intent and hasattr(intent, "sla_requirements"):
            sla_reqs = (
                intent.sla_requirements
                if hasattr(intent.sla_requirements, "__iter__") and not isinstance(intent.sla_requirements, str)
                else {}
            )
            if isinstance(sla_reqs, dict):
                if "latency" in sla_reqs:
                    latency_str = str(sla_reqs["latency"]).replace("ms", "").strip()
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
        "status": "unknown",
    }
    if decision_result.domains and "Core" in decision_result.domains:
        if intent and hasattr(intent, "sla_requirements"):
            sla_reqs = (
                intent.sla_requirements
                if hasattr(intent.sla_requirements, "__iter__") and not isinstance(intent.sla_requirements, str)
                else {}
            )
            if isinstance(sla_reqs, dict):
                if "latency" in sla_reqs:
                    latency_str = str(sla_reqs["latency"]).replace("ms", "").strip()
                    try:
                        core_metrics["latency_ms"] = float(latency_str)
                    except (ValueError, TypeError):
                        pass
        core_metrics["status"] = "evaluated"
    domains_snapshot["Core"] = core_metrics

    # Identificar bottleneck domain
    bottleneck_domain = meta.get("dominant_domain")
    bottleneck_metric = None

    if bottleneck_domain is None and (
        decision_result.action == DecisionAction.RENEGOTIATE or decision_result.action == DecisionAction.REJECT
    ):
        reasoning_lower = (decision_result.reasoning or "").lower()
        if "transport" in reasoning_lower or "transporte" in reasoning_lower:
            bottleneck_domain = "Transport"
            if "latency" in reasoning_lower:
                bottleneck_metric = "latency_ms"
        elif "ran" in reasoning_lower:
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
        "raw_risk_score": raw_risk,
        "slice_adjusted_risk_score": adj_risk,
        "thresholds_used": meta.get("thresholds_used"),
        "top_factors": meta.get("top_factors"),
        "decision_explanation": meta.get("decision_explanation"),
        "decision_explanation_plain": meta.get("decision_explanation_plain"),
        "dominant_domain": meta.get("dominant_domain"),
        "predicted_decision_class": meta.get("predicted_decision_class"),
        "classifier_confidence": meta.get("confidence_score"),
        "threshold_decision": meta.get("threshold_decision"),
        "final_decision": meta.get("final_decision"),
        "decision_divergence": meta.get("decision_divergence"),
        "decision_mode": meta.get("decision_mode"),
        "ml_risk_level": decision_result.ml_risk_level.value if decision_result.ml_risk_level else None,
        "ml_confidence": decision_result.confidence,
        "ml_prediction_latency_ms": (
            (decision_result.metadata or {}).get("ml_prediction_latency_ms")
            if isinstance(decision_result.metadata, dict)
            else None
        ),
        "decision_duration_ms": (
            (decision_result.metadata or {}).get("decision_duration_ms")
            if isinstance(decision_result.metadata, dict)
            else None
        ),
        "confidence": decision_result.confidence,
        "reasoning": decision_result.reasoning,
        "decision_score": meta.get("decision_score"),
        "decision_band": meta.get("decision_band"),
        "contributing_factors": meta.get("contributing_factors"),
        "reason_codes": meta.get("reason_codes"),
        "normalized_inputs": meta.get("normalized_inputs"),
        "decision_policy_version": meta.get("decision_policy_version"),
        "slice_profile_used": meta.get("slice_profile_used"),
    }

    return snapshot
