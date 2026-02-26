"""
Domain Compliance Calculator - TriSLA v3.9.3
Cálculo explícito de compliance por domínio (RAN, Transport, Core)

Este módulo calcula compliance por domínio sem alterar a lógica decisória existente.
Apenas expõe causalidade que já existe, mas estava implícita.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# Thresholds por tipo de slice (alinhado com decision_engine.py)
SLICE_THRESHOLDS = {
    "URLLC": {
        "ran": {
            "latency_ms": 20.0,  # < 20ms aceitável
            "jitter_ms": 5.0,    # < 5ms aceitável
            "reliability": 99.9,  # > 99.9% ideal
            "cpu_utilization": 70.0  # < 70% ideal
        },
        "transport": {
            "packet_loss": 0.1,   # < 0.1% ideal
            "bandwidth": 100.0    # > 100 Mbps ideal
        },
        "core": {
            "cpu": 80.0,          # < 80% ideal
            "memory": 80.0,       # < 80% ideal
            "availability": 99.0  # > 99% ideal
        }
    },
    "EMBB": {
        "ran": {
            "cpu_utilization": 70.0
        },
        "transport": {
            "throughput_dl_mbps": 100.0,  # > 100 Mbps ideal
            "throughput_ul_mbps": 50.0,   # > 50 Mbps ideal
            "packet_loss": 0.1,           # < 0.1% ideal
            "bandwidth": 100.0
        },
        "core": {
            "cpu": 80.0,
            "memory": 80.0
        }
    },
    "MMTC": {
        "ran": {
            "cpu_utilization": 70.0
        },
        "transport": {
            "bandwidth": 50.0
        },
        "core": {
            "attach_success_rate": 95.0,  # > 95% ideal
            "event_throughput": 1000.0,   # > 1000 events/s ideal
            "availability": 99.0,         # > 99% ideal
            "cpu": 80.0,
            "memory": 80.0
        }
    }
}


def compute_metric_compliance(
    metric_name: str,
    observed_value: float,
    threshold: float,
    metric_type: str = "auto"
) -> float:
    """
    Calcula compliance de uma métrica individual
    
    Args:
        metric_name: Nome da métrica
        observed_value: Valor observado
        threshold: Threshold de referência
        metric_type: Tipo de métrica ("lower_is_better", "higher_is_better", "auto")
    
    Returns:
        Score de compliance (0.0 a 1.0)
    """
    if observed_value is None or threshold is None:
        return 0.0
    
    # Determinar tipo automaticamente se não especificado
    if metric_type == "auto":
        lower_is_better = [
            "latency", "latency_ms", "jitter", "jitter_ms",
            "packet_loss", "packet_loss_percent", "cpu_utilization",
            "cpu", "memory", "session_setup_time"
        ]
        metric_type = "lower_is_better" if any(m in metric_name.lower() for m in lower_is_better) else "higher_is_better"
    
    if metric_type == "lower_is_better":
        # Para métricas onde menor é melhor (latency, jitter, packet_loss, cpu)
        if threshold == 0:
            return 1.0 if observed_value == 0 else 0.0
        compliance = max(0.0, 1.0 - (observed_value / threshold))
        return min(1.0, compliance)
    else:
        # Para métricas onde maior é melhor (throughput, reliability, availability)
        if threshold == 0:
            return 0.0
        compliance = min(1.0, observed_value / threshold)
        return max(0.0, compliance)


def compute_domain_compliance(
    domain: str,
    metrics: Dict[str, Any],
    slice_type: str,
    sla_requirements: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calcula compliance explícito por domínio
    
    Args:
        domain: Domínio ("ran", "transport", "core")
        metrics: Métricas coletadas do domínio
        slice_type: Tipo de slice (URLLC, EMBB, MMTC)
        sla_requirements: Requisitos específicos do SLA (opcional)
    
    Returns:
        {
            "domain": "ran",
            "compliance": 0.75,
            "metrics_compliance": {
                "latency_ms": 0.8,
                "jitter_ms": 0.9,
                "reliability": 0.7
            },
            "bottleneck_metric": "reliability",
            "bottleneck_value": 99.5
        }
    """
    slice_type_upper = slice_type.upper()
    threshold_config = SLICE_THRESHOLDS.get(slice_type_upper, SLICE_THRESHOLDS["EMBB"])
    domain_config = threshold_config.get(domain.lower(), {})
    
    metrics_compliance = {}
    compliance_scores = []
    
    # Calcular compliance para cada métrica relevante
    for metric_name, threshold in domain_config.items():
        # Tentar diferentes variações do nome da métrica
        observed_value = None
        
        # Mapear nomes de métricas
        metric_mappings = {
            "latency_ms": ["latency_ms", "latency", "nasp_ran_latency_ms"],
            "jitter_ms": ["jitter_ms", "jitter", "nasp_ran_jitter_ms"],
            "reliability": ["reliability", "nasp_ran_reliability_percent"],
            "cpu_utilization": ["cpu_utilization", "cpu", "nasp_ran_cpu"],
            "throughput_dl_mbps": ["throughput_dl_mbps", "throughput_dl", "nasp_tn_throughput_dl_mbps"],
            "throughput_ul_mbps": ["throughput_ul_mbps", "throughput_ul", "nasp_tn_throughput_ul_mbps"],
            "packet_loss": ["packet_loss", "packet_loss_percent", "nasp_tn_packet_loss_percent"],
            "bandwidth": ["bandwidth", "nasp_tn_bandwidth"],
            "cpu": ["cpu", "cpu_utilization", "nasp_core_cpu"],
            "memory": ["memory", "memory_utilization", "nasp_core_memory"],
            "availability": ["availability", "availability_percent", "nasp_core_availability_percent"],
            "attach_success_rate": ["attach_success_rate", "nasp_core_attach_success_rate_percent"],
            "event_throughput": ["event_throughput", "nasp_core_event_throughput"],
            "session_setup_time": ["session_setup_time", "session_setup_time_ms", "nasp_core_session_setup_time_ms"]
        }
        
        # Buscar valor observado
        if metric_name in metric_mappings:
            for variant in metric_mappings[metric_name]:
                if variant in metrics:
                    observed_value = metrics[variant]
                    break
        
        if observed_value is None:
            # Tentar nome direto
            observed_value = metrics.get(metric_name)
        
        if observed_value is not None:
            compliance = compute_metric_compliance(metric_name, observed_value, threshold)
            metrics_compliance[metric_name] = compliance
            compliance_scores.append(compliance)
    
    # Compliance do domínio = mínimo de todas as métricas (gargalo)
    domain_compliance = min(compliance_scores) if compliance_scores else 0.0
    
    # Identificar gargalo (métrica com menor compliance)
    bottleneck_metric = None
    bottleneck_value = None
    if metrics_compliance:
        bottleneck_metric = min(metrics_compliance.items(), key=lambda x: x[1])[0]
        # Buscar valor observado da métrica gargalo
        for variant in metric_mappings.get(bottleneck_metric, [bottleneck_metric]):
            if variant in metrics:
                bottleneck_value = metrics[variant]
                break
        if bottleneck_value is None:
            bottleneck_value = metrics.get(bottleneck_metric)
    
    return {
        "domain": domain.lower(),
        "compliance": domain_compliance,
        "metrics_compliance": metrics_compliance,
        "bottleneck_metric": bottleneck_metric,
        "bottleneck_value": bottleneck_value,
        "threshold_used": domain_config.get(bottleneck_metric) if bottleneck_metric else None
    }


def compute_all_domains_compliance(
    metrics_ran: Dict[str, Any],
    metrics_transport: Dict[str, Any],
    metrics_core: Dict[str, Any],
    slice_type: str,
    sla_requirements: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calcula compliance para todos os domínios
    
    Args:
        metrics_ran: Métricas do RAN
        metrics_transport: Métricas do Transport
        metrics_core: Métricas do Core
        slice_type: Tipo de slice
        sla_requirements: Requisitos específicos do SLA
    
    Returns:
        {
            "ran": {...},
            "transport": {...},
            "core": {...},
            "sla_compliance": 0.75,  # min(ran, transport, core)
            "bottleneck_domain": "ran"
        }
    """
    compliance_ran = compute_domain_compliance("ran", metrics_ran, slice_type, sla_requirements)
    compliance_transport = compute_domain_compliance("transport", metrics_transport, slice_type, sla_requirements)
    compliance_core = compute_domain_compliance("core", metrics_core, slice_type, sla_requirements)
    
    # SLA compliance global = mínimo dos domínios (gargalo)
    sla_compliance = min(
        compliance_ran["compliance"],
        compliance_transport["compliance"],
        compliance_core["compliance"]
    )
    
    # Identificar domínio gargalo
    domain_compliances = {
        "ran": compliance_ran["compliance"],
        "transport": compliance_transport["compliance"],
        "core": compliance_core["compliance"]
    }
    bottleneck_domain = min(domain_compliances.items(), key=lambda x: x[1])[0]
    
    return {
        "ran": compliance_ran,
        "transport": compliance_transport,
        "core": compliance_core,
        "sla_compliance": sla_compliance,
        "bottleneck_domain": bottleneck_domain
    }
