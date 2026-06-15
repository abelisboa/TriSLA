"""
Transport compliance policy — Sprint 7E (POST-S7D).

`bandwidth` / throughput KPIs in telemetry reflect instantaneous N6 dataplane
throughput (bps→Mbps), not provisioned capacity. POLICY D (flow-aware): score
throughput only when user-plane traffic is present; idle → N/A (excluded from min).
"""

from __future__ import annotations

import os

# Exported for explainability and tests
TRANSPORT_POLICY_ID = "FLOW_AWARE"
TRANSPORT_POLICY_VERSION = "7E"

# Mbps at or below this value ⇒ no active flow (lab idle / no iperf on N6 anchor)
THROUGHPUT_IDLE_EPSILON_MBPS = float(
    os.getenv("TRANSPORT_THROUGHPUT_IDLE_EPSILON_MBPS", "0.001")
)

# Metrics sourced from instantaneous throughput proxies (Sprint 7D lineage)
FLOW_AWARE_THROUGHPUT_METRICS = frozenset(
    {
        "bandwidth",
        "throughput_dl_mbps",
        "throughput_ul_mbps",
    }
)

EXPLAINABILITY_MEASUREMENT_NOTE = (
    "Observed value is instantaneous dataplane throughput (Mbps), not provisioned "
    "capacity. When no user-plane traffic is detected, this KPI is not scored (N/A)."
)


def is_flow_aware_throughput_metric(metric_name: str) -> bool:
    return metric_name in FLOW_AWARE_THROUGHPUT_METRICS


def is_idle_throughput(observed_mbps: float, epsilon: float | None = None) -> bool:
    eps = THROUGHPUT_IDLE_EPSILON_MBPS if epsilon is None else epsilon
    return observed_mbps <= eps


def should_skip_throughput_scoring(domain: str, metric_name: str, observed_mbps: float) -> bool:
    """True when POLICY D applies: idle throughput must not be scored as capacity FAIL."""
    if domain.lower() != "transport":
        return False
    if not is_flow_aware_throughput_metric(metric_name):
        return False
    return is_idle_throughput(observed_mbps)
