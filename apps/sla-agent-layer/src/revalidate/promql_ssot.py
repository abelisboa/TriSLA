"""
Single source of truth for PromQL strings (sla-agent revalidate path).

Cópia 1:1 de apps/portal-backend/src/telemetry/promql_ssot.py.
Não alterar semântica de queries sem replicar a mesma mudança no backend.
"""

from __future__ import annotations

import os
from typing import Dict

_PACKET_LOSS_PCT_EXPR = (
    "("
    'sum(rate(container_network_receive_packets_dropped_total{namespace="ns-1274485"}[2m]))'
    '+ sum(rate(container_network_transmit_packets_dropped_total{namespace="ns-1274485"}[2m]))'
    ") / ("
    'sum(rate(container_network_receive_packets_total{namespace="ns-1274485"}[2m]))'
    '+ sum(rate(container_network_transmit_packets_total{namespace="ns-1274485"}[2m]))'
    ") * 100"
)

PROMQL_SSOT: Dict[str, str] = {
    "RAN_PRB": 'avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})',
    "RAN_LATENCY": "avg(trisla_ran_latency_ms)",
    "TRANSPORT_RTT": (
        'max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000'
    ),
    "TRANSPORT_JITTER": (
        '(max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]) - '
        'min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])) * 1000'
    ),
    "CORE_CPU": os.getenv(
        "TELEMETRY_PROMQL_CORE_CPU",
        "sum(rate(process_cpu_seconds_total[1m]))",
    ),
    "CORE_MEMORY": os.getenv(
        "TELEMETRY_PROMQL_CORE_MEMORY",
        "sum(process_resident_memory_bytes)",
    ),
    # Sprint 7C — validated Sprint 7B (trisla_ran_ue_proxy_throughput_bps → Mbps)
    "TRANSPORT_BANDWIDTH_MBPS": (
        'avg(trisla_ran_ue_proxy_throughput_bps{job="trisla-ran-ue-upf-proxy"}) / 1000000'
    ),
    # Sprint 7C — derived drop rate % (rx+tx) for free5GC dataplane namespace
    "TRANSPORT_PACKET_LOSS_PCT": _PACKET_LOSS_PCT_EXPR,
    # Sprint 8D — Transport Delivery Reliability Proxy (%): 100 - packet_loss_pct
    "RELIABILITY_PROXY_PCT": f"100 - ({_PACKET_LOSS_PCT_EXPR})",
    # Sprint 8B — Operational Availability Proxy (%): probe reachability + kube Available
    "CORE_AVAILABILITY_PCT": (
        "100 * ("
        '0.7 * avg(probe_success{job=~"probe/monitoring/trisla-.*"})'
        ' + 0.3 * ('
        'sum(kube_deployment_status_condition{namespace="trisla",condition="Available",status="true"})'
        " / "
        'count(kube_deployment_status_condition{namespace="trisla",condition="Available"})'
        ")"
        ")"
    ),
}
