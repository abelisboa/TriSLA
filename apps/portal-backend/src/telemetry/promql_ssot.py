"""
Single source of truth for PromQL strings (portal-backend).

PR-02 (PROMPT_36): centralize queries; env TELEMETRY_PROMQL_* still overrides in collector.
Do not change query semantics here without E2E validation.
"""

from __future__ import annotations

import os
from typing import Dict

# Telemetry snapshot (query_range) — keys match TELEMETRY_PROMQL_* suffixes.
PROMQL_SSOT: Dict[str, str] = {
    "RAN_PRB": "avg(trisla_ran_prb_utilization)",
    "RAN_LATENCY": "avg(trisla_ran_latency_ms)",
    "TRANSPORT_RTT": (
        'max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000'
    ),
    # Range spread of probe RTT (seconds → ms). stddev_over_time often returned empty on short windows;
    # max−min over 1m matches operational variability and populates transport.jitter in snapshots.
    "TRANSPORT_JITTER": (
        '(max_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]) - '
        'min_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m])) * 1000'
    ),
    # Core (PR-03): alvo documental = container_* escopado ao namespace Free5GC (ex.: ns-1274485
    # neste cluster; não confundir com nome literal "free5gc"). Só substituir estas strings
    # quando Prometheus expuser séries (validação instant query não vazia — PROMPT_38).
    # NOTE:
    # Default process_* metrics are deprecated for production use.
    # Core-scoped container metrics must be provided via TELEMETRY_PROMQL_CORE_*.
    "CORE_CPU": os.getenv(
        "TELEMETRY_PROMQL_CORE_CPU",
        "sum(rate(process_cpu_seconds_total[1m]))",
    ),
    "CORE_MEMORY": os.getenv(
        "TELEMETRY_PROMQL_CORE_MEMORY",
        "sum(process_resident_memory_bytes)",
    ),
}

# Referência para cutover futuro (não usado pelo collector enquanto vazio no Prometheus):
CORE_CPU_FALLBACK = "sum(rate(process_cpu_seconds_total[1m]))"
CORE_MEMORY_FALLBACK = "sum(process_resident_memory_bytes)"
CORE_CPU_SCOPED_FREE5GC_STACK = (
    'sum(rate(container_cpu_usage_seconds_total{namespace="ns-1274485"}[1m]))'
)
CORE_MEMORY_SCOPED_FREE5GC_STACK = (
    'sum(container_memory_working_set_bytes{namespace="ns-1274485"})'
)

# GET /api/v1/prometheus/summary — instant queries (observability index; not telemetry_snapshot).
PROMQL_SUMMARY: Dict[str, str] = {
    "throughput_mbps": (
        '8 * (sum(rate(container_network_receive_bytes_total{namespace="ns-1274485",pod=~"rantester.*"}[1m])) + '
        'sum(rate(container_network_transmit_bytes_total{namespace="ns-1274485",pod=~"rantester.*"}[1m]))) / 1000000'
    ),
    "transport_latency_ms": (
        'max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000'
    ),
    "sessions": (
        'sum(kube_pod_status_phase{namespace="ns-1274485",phase="Running",pod=~"(rantester.*|amf.*|smf.*|upf.*)"})'
    ),
    "cluster_cpu_percent": (
        'sum(rate(container_cpu_usage_seconds_total{namespace="trisla"}[1m]))/'
        'sum(rate(node_cpu_seconds_total[1m]))*100'
    ),
    "ran_prb_instant": "trisla_ran_prb_utilization",
}
