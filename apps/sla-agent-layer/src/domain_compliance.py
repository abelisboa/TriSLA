"""
Domain Compliance Calculator - TriSLA v3.9.3
Cálculo explícito de compliance por domínio (RAN, Transport, Core)

Este módulo calcula compliance por domínio sem alterar a lógica decisória existente.
Apenas expõe causalidade que já existe, mas estava implícita.
Sprint 6C — metric_explainability export (additive).
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

from availability_proxy import AVAILABILITY_PROXY_KIND, AVAILABILITY_PROXY_NOTE
from reliability_proxy import (
    RELIABILITY_PROXY_KIND,
    RELIABILITY_PROXY_NOTE,
    reliability_pct_from_packet_loss,
)
from transport_policy import (
    EXPLAINABILITY_MEASUREMENT_NOTE,
    TRANSPORT_POLICY_ID,
    should_skip_throughput_scoring,
)

logger = logging.getLogger(__name__)

COMPLIANCE_BAND = 0.85

# Thresholds por tipo de slice (alinhado com decision_engine.py)
SLICE_THRESHOLDS = {
    "URLLC": {
        "ran": {
            "latency_ms": 20.0,
            "jitter_ms": 5.0,
            "reliability": 99.9,
            "cpu_utilization": 70.0,
        },
        "transport": {
            "packet_loss": 0.1,
            "bandwidth": 100.0,
        },
        "core": {
            "cpu": 80.0,
            "memory": 80.0,
            "availability": 99.0,
        },
    },
    "EMBB": {
        "ran": {
            "cpu_utilization": 70.0,
        },
        "transport": {
            "throughput_dl_mbps": 100.0,
            "throughput_ul_mbps": 50.0,
            "packet_loss": 0.1,
            "bandwidth": 100.0,
        },
        "core": {
            "cpu": 80.0,
            "memory": 80.0,
        },
    },
    "MMTC": {
        "ran": {
            "cpu_utilization": 70.0,
        },
        "transport": {
            "bandwidth": 50.0,
        },
        "core": {
            "attach_success_rate": 95.0,
            "event_throughput": 1000.0,
            "availability": 99.0,
            "cpu": 80.0,
            "memory": 80.0,
        },
    },
}

METRIC_MAPPINGS: Dict[str, List[str]] = {
    "latency_ms": ["latency_ms", "latency", "nasp_ran_latency_ms"],
    "jitter_ms": ["jitter_ms", "jitter", "nasp_ran_jitter_ms"],
    "reliability": ["reliability", "reliability_pct", "nasp_ran_reliability_percent"],
    "cpu_utilization": ["cpu_utilization", "cpu", "nasp_ran_cpu"],
    "throughput_dl_mbps": ["throughput_dl_mbps", "throughput_dl", "nasp_tn_throughput_dl_mbps"],
    "throughput_ul_mbps": ["throughput_ul_mbps", "throughput_ul", "nasp_tn_throughput_ul_mbps"],
    "packet_loss": ["packet_loss", "packet_loss_pct", "packet_loss_percent", "nasp_tn_packet_loss_percent"],
    "bandwidth": ["bandwidth", "bandwidth_mbps", "nasp_tn_bandwidth"],
    "cpu": ["cpu", "cpu_utilization", "nasp_core_cpu"],
    "memory": ["memory", "memory_bytes", "memory_utilization", "nasp_core_memory"],
    "availability": ["availability", "availability_pct", "availability_percent", "nasp_core_availability_percent"],
    "attach_success_rate": ["attach_success_rate", "nasp_core_attach_success_rate_percent"],
    "event_throughput": ["event_throughput", "nasp_core_event_throughput"],
    "session_setup_time": ["session_setup_time", "session_setup_time_ms", "nasp_core_session_setup_time_ms"],
}


def compute_metric_compliance(
    metric_name: str,
    observed_value: float,
    threshold: float,
    metric_type: str = "auto",
) -> float:
    """Calcula compliance de uma métrica individual (0.0 a 1.0)."""
    if observed_value is None or threshold is None:
        return 0.0

    if metric_type == "auto":
        lower_is_better = [
            "latency",
            "latency_ms",
            "jitter",
            "jitter_ms",
            "packet_loss",
            "packet_loss_percent",
            "cpu_utilization",
            "cpu",
            "memory",
            "session_setup_time",
        ]
        metric_type = (
            "lower_is_better"
            if any(m in metric_name.lower() for m in lower_is_better)
            else "higher_is_better"
        )

    if metric_type == "lower_is_better":
        if threshold == 0:
            return 1.0 if observed_value == 0 else 0.0
        compliance = max(0.0, 1.0 - (observed_value / threshold))
        return min(1.0, compliance)

    if threshold == 0:
        return 0.0
    compliance = min(1.0, observed_value / threshold)
    return max(0.0, compliance)


def _pick_from_metrics(metrics: Dict[str, Any], variants: List[str]) -> Optional[float]:
    if not isinstance(metrics, dict):
        return None
    for key in variants:
        if key in metrics and metrics[key] is not None:
            try:
                return float(metrics[key])
            except (TypeError, ValueError):
                continue
    return None


def _resolve_observed(
    domain: str,
    metric_name: str,
    metrics: Dict[str, Any],
    transport_metrics: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[float], str, Dict[str, Any]]:
    """
    Resolve observed value and explainability source metadata.
    Returns (observed, source, extra_fields).
    """
    domain_l = domain.lower()
    source = f"telemetry_snapshot.{domain_l}"
    extra: Dict[str, Any] = {}

    variants = METRIC_MAPPINGS.get(metric_name, [metric_name])
    observed = _pick_from_metrics(metrics, variants)

    if domain_l == "ran" and metric_name == "reliability" and observed is not None:
        if _pick_from_metrics(metrics, ["reliability_pct"]) is not None and _pick_from_metrics(
            metrics, ["reliability"]
        ) is None:
            extra["measurement_kind"] = RELIABILITY_PROXY_KIND
            extra["measurement_note"] = RELIABILITY_PROXY_NOTE

    if domain_l == "ran" and metric_name == "jitter_ms" and observed is None and transport_metrics:
        observed = _pick_from_metrics(transport_metrics, ["jitter_ms", "jitter"])
        if observed is not None:
            source = "telemetry_snapshot.transport"
            extra["measurement_note"] = "Observed via transport.jitter_ms fallback (Sprint 9D alias)."

    if domain_l == "ran" and metric_name == "cpu_utilization" and observed is None:
        prb = _pick_from_metrics(metrics, ["prb_utilization"])
        if prb is not None:
            observed = prb
            extra["measurement_note"] = (
                "RAN cpu_utilization observed via PRB/prb_utilization alias (Sprint 9D)."
            )

    if domain_l == "ran" and metric_name == "reliability" and observed is None and transport_metrics:
        packet_loss = _pick_from_metrics(
            transport_metrics, ["packet_loss_pct", "packet_loss", "packet_loss_percent"]
        )
        if packet_loss is not None:
            observed = reliability_pct_from_packet_loss(packet_loss)
            source = "telemetry_snapshot.ran"
            extra["measurement_kind"] = RELIABILITY_PROXY_KIND
            extra["measurement_note"] = RELIABILITY_PROXY_NOTE

    if domain_l == "core" and metric_name == "availability" and observed is not None:
        if _pick_from_metrics(metrics, ["availability_pct"]) is not None:
            extra["measurement_kind"] = AVAILABILITY_PROXY_KIND
            extra["measurement_note"] = AVAILABILITY_PROXY_NOTE

    return observed, source, extra


def _status_for_row(observed: Optional[float], compliance_score: Optional[float], is_na: bool) -> str:
    if is_na:
        return "N/A"
    if observed is None:
        return "MISSING"
    if compliance_score is None:
        return "MISSING"
    if compliance_score >= COMPLIANCE_BAND:
        return "PASS"
    return "FAIL"


def _build_explainability_row(
    domain: str,
    metric_name: str,
    threshold: float,
    metrics: Dict[str, Any],
    transport_metrics: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Optional[float], bool]:
    """Build one metric_explainability row; return (row, score_for_domain_min, is_na)."""
    observed, source, extra = _resolve_observed(domain, metric_name, metrics, transport_metrics)

    is_na = False
    compliance_score: Optional[float] = None
    row: Dict[str, Any] = {
        "metric": metric_name,
        "observed": observed,
        "threshold": threshold,
        "compliance_score": None,
        "status": "MISSING",
        "source": source,
    }
    row.update(extra)

    if observed is not None:
        if should_skip_throughput_scoring(domain, metric_name, observed):
            is_na = True
            row["status"] = "N/A"
            row["compliance_score"] = None
            row["policy"] = TRANSPORT_POLICY_ID
            row["measurement_semantics"] = "instantaneous_throughput_mbps"
            row["policy_reason"] = "No active user-plane traffic; throughput not evaluated as capacity"
            if "measurement_note" not in row:
                row["measurement_note"] = EXPLAINABILITY_MEASUREMENT_NOTE
            return row, None, True

        compliance_score = compute_metric_compliance(metric_name, observed, threshold)
        row["compliance_score"] = compliance_score
        row["status"] = _status_for_row(observed, compliance_score, False)
    else:
        row["status"] = "MISSING"

    return row, compliance_score, is_na


def compute_domain_compliance(
    domain: str,
    metrics: Dict[str, Any],
    slice_type: str,
    sla_requirements: Optional[Dict[str, Any]] = None,
    transport_metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calcula compliance explícito por domínio e exporta metric_explainability (Sprint 6C).
    """
    slice_type_upper = slice_type.upper()
    threshold_config = SLICE_THRESHOLDS.get(slice_type_upper, SLICE_THRESHOLDS["EMBB"])
    domain_config = threshold_config.get(domain.lower(), {})

    metrics_compliance: Dict[str, float] = {}
    compliance_scores: List[float] = []
    metric_explainability: List[Dict[str, Any]] = []
    has_na = False

    for metric_name, threshold in domain_config.items():
        row, score, is_na = _build_explainability_row(
            domain, metric_name, threshold, metrics, transport_metrics
        )
        metric_explainability.append(row)
        if is_na:
            has_na = True
            continue
        if score is None:
            continue
        metrics_compliance[metric_name] = score
        compliance_scores.append(score)

    if compliance_scores:
        domain_compliance = min(compliance_scores)
    elif has_na:
        domain_compliance = 1.0
    else:
        domain_compliance = 0.0

    bottleneck_metric = None
    bottleneck_value = None
    if metrics_compliance:
        bottleneck_metric = min(metrics_compliance.items(), key=lambda x: x[1])[0]
        observed, _, _ = _resolve_observed(
            domain, bottleneck_metric, metrics, transport_metrics
        )
        bottleneck_value = observed

    return {
        "domain": domain.lower(),
        "compliance": domain_compliance,
        "metrics_compliance": metrics_compliance,
        "metric_explainability": metric_explainability,
        "bottleneck_metric": bottleneck_metric,
        "bottleneck_value": bottleneck_value,
        "threshold_used": domain_config.get(bottleneck_metric) if bottleneck_metric else None,
    }


def compute_all_domains_compliance(
    metrics_ran: Dict[str, Any],
    metrics_transport: Dict[str, Any],
    metrics_core: Dict[str, Any],
    slice_type: str,
    sla_requirements: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Calcula compliance para todos os domínios."""
    compliance_ran = compute_domain_compliance(
        "ran",
        metrics_ran,
        slice_type,
        sla_requirements,
        transport_metrics=metrics_transport,
    )
    compliance_transport = compute_domain_compliance(
        "transport",
        metrics_transport,
        slice_type,
        sla_requirements,
    )
    compliance_core = compute_domain_compliance(
        "core",
        metrics_core,
        slice_type,
        sla_requirements,
    )

    sla_compliance = min(
        compliance_ran["compliance"],
        compliance_transport["compliance"],
        compliance_core["compliance"],
    )

    domain_compliances = {
        "ran": compliance_ran["compliance"],
        "transport": compliance_transport["compliance"],
        "core": compliance_core["compliance"],
    }
    bottleneck_domain = min(domain_compliances.items(), key=lambda x: x[1])[0]

    return {
        "ran": compliance_ran,
        "transport": compliance_transport,
        "core": compliance_core,
        "sla_compliance": sla_compliance,
        "bottleneck_domain": bottleneck_domain,
    }


def build_domain_explainability(compliance: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Assemble portal-facing domain_explainability from domain compliance blocks."""
    return {
        "ran": list((compliance.get("ran") or {}).get("metric_explainability") or []),
        "transport": list((compliance.get("transport") or {}).get("metric_explainability") or []),
        "core": list((compliance.get("core") or {}).get("metric_explainability") or []),
    }
