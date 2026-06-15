"""Sprint 7E — transport flow-aware policy unit tests."""
from __future__ import annotations

from domain_compliance import compute_domain_compliance
from transport_policy import (
    TRANSPORT_POLICY_ID,
    is_idle_throughput,
    should_skip_throughput_scoring,
)


class TestTransportPolicyHelpers:
    def test_idle_throughput_at_zero(self):
        assert is_idle_throughput(0.0) is True
        assert is_idle_throughput(0.0005) is True
        assert is_idle_throughput(0.002) is False

    def test_skip_only_transport_bandwidth_idle(self):
        assert should_skip_throughput_scoring("transport", "bandwidth", 0.0) is True
        assert should_skip_throughput_scoring("transport", "packet_loss", 0.0) is False
        assert should_skip_throughput_scoring("ran", "bandwidth", 0.0) is False
        assert should_skip_throughput_scoring("transport", "bandwidth", 20.0) is False


class TestTransportDomainCompliancePolicyD:
    def test_urllc_idle_bandwidth_na_transport_not_zero(self):
        out = compute_domain_compliance(
            "transport",
            {"packet_loss": 0.0, "bandwidth": 0.0, "bandwidth_mbps": 0.0},
            "URLLC",
        )
        assert out["compliance"] == 1.0
        rows = {r["metric"]: r for r in out["metric_explainability"]}
        assert rows["packet_loss"]["status"] == "PASS"
        assert rows["bandwidth"]["status"] == "N/A"
        assert rows["bandwidth"]["policy"] == TRANSPORT_POLICY_ID
        assert rows["bandwidth"]["compliance_score"] is None

    def test_urllc_active_bandwidth_fail_below_threshold(self):
        out = compute_domain_compliance(
            "transport",
            {"packet_loss": 0.0, "bandwidth": 20.0},
            "URLLC",
        )
        assert out["compliance"] == 0.2
        rows = {r["metric"]: r for r in out["metric_explainability"]}
        assert rows["bandwidth"]["status"] == "FAIL"
        assert rows["bandwidth"]["compliance_score"] == 0.2

    def test_mmtc_idle_only_bandwidth_na_domain_not_zero(self):
        out = compute_domain_compliance(
            "transport",
            {"bandwidth": 0.0},
            "MMTC",
        )
        assert out["compliance"] == 1.0

    def test_urllc_active_bandwidth_pass_above_threshold(self):
        out = compute_domain_compliance(
            "transport",
            {"packet_loss": 0.0, "bandwidth": 120.0},
            "URLLC",
        )
        assert out["compliance"] == 1.0
        rows = {r["metric"]: r for r in out["metric_explainability"]}
        assert rows["bandwidth"]["status"] == "PASS"
