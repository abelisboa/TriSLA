"""Observability PromQL defaults — Sprint 5C summary CPU + TN-I1 probe alignment."""

from src.telemetry.promql_ssot import (
    CLUSTER_CPU_PERCENT_SUMMARY,
    PROMQL_SSOT,
    PROMQL_SUMMARY,
    TN_I1_JITTER_DEFAULT,
    TN_I1_LATENCY_DEFAULT,
)


def test_summary_cpu_uses_container_share_not_node_cpu():
    assert PROMQL_SUMMARY["cluster_cpu_percent"] == CLUSTER_CPU_PERCENT_SUMMARY
    assert "node_cpu_seconds_total" not in CLUSTER_CPU_PERCENT_SUMMARY
    assert "container_cpu_usage_seconds_total" in CLUSTER_CPU_PERCENT_SUMMARY
    assert 'namespace="trisla"' in CLUSTER_CPU_PERCENT_SUMMARY


def test_summary_transport_latency_matches_ssot_probe():
    assert PROMQL_SUMMARY["transport_latency_ms"] == PROMQL_SSOT["TRANSPORT_RTT"]
    assert "probe_duration_seconds" in PROMQL_SUMMARY["transport_latency_ms"]


def test_tn_i1_defaults_use_probe_ssot_not_phantom_metrics():
    assert TN_I1_LATENCY_DEFAULT == PROMQL_SSOT["TRANSPORT_RTT"]
    assert TN_I1_JITTER_DEFAULT == PROMQL_SSOT["TRANSPORT_JITTER"]
    assert "trisla_transport_jitter_ms" not in TN_I1_JITTER_DEFAULT
    assert "trisla_transport_latency_ms" not in TN_I1_LATENCY_DEFAULT
    assert "probe_duration_seconds" in TN_I1_JITTER_DEFAULT
    assert "probe_duration_seconds" in TN_I1_LATENCY_DEFAULT
