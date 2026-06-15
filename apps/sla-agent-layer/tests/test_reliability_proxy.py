"""Sprint 8D — reliability proxy unit tests."""
from __future__ import annotations

from domain_compliance import compute_domain_compliance
from reliability_proxy import reliability_pct_from_packet_loss


def test_reliability_formula_examples():
    assert reliability_pct_from_packet_loss(0.0) == 100.0
    assert reliability_pct_from_packet_loss(0.1) == 99.9
    assert reliability_pct_from_packet_loss(1.0) == 99.0


def test_ran_reliability_from_pct_alias():
    out = compute_domain_compliance(
        "ran",
        {"reliability_pct": 100.0, "latency_ms": 1.0},
        "URLLC",
    )
    rows = {r["metric"]: r for r in out["metric_explainability"]}
    assert rows["reliability"]["status"] == "PASS"
    assert rows["reliability"]["observed"] == 100.0
    assert rows["reliability"].get("measurement_kind") == "TRANSPORT_DELIVERY_RELIABILITY_PROXY"
