"""Sprint 5N4_2 — RAN throughput PromQL alignment (Monitoring summary)."""

from src.telemetry.promql_ssot import PROMQL_SUMMARY


def test_summary_throughput_uses_ran_exporter_not_rantester():
    q = PROMQL_SUMMARY["throughput_mbps"]
    assert "trisla_ran_ue_proxy_throughput_bps" in q
    assert 'job="trisla-ran-ue-upf-proxy"' in q
    assert "rantester" not in q
    assert "container_network_" not in q


def test_summary_throughput_does_not_multiply_by_eight():
    q = PROMQL_SUMMARY["throughput_mbps"]
    assert "* 8" not in q
    assert "/ 1000000" in q


def test_bps_to_mbps_conversion_examples():
    """Metric is bps; summary field is Mbps (divide by 1e6 only)."""

    def bps_to_mbps(bps: float) -> float:
        return bps / 1_000_000

    assert bps_to_mbps(0) == 0.0
    assert bps_to_mbps(10_000_000) == 10.0
    assert bps_to_mbps(100_000_000) == 100.0
