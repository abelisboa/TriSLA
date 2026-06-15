"""Sprint 8B — availability proxy unit tests."""
from __future__ import annotations

from domain_compliance import compute_domain_compliance


def test_core_availability_from_pct_alias():
    out = compute_domain_compliance(
        "core",
        {"availability_pct": 100.0, "cpu": 1.0, "memory": 1.0},
        "URLLC",
    )
    rows = {r["metric"]: r for r in out["metric_explainability"]}
    assert rows["availability"]["status"] == "PASS"
    assert rows["availability"]["observed"] == 100.0
    assert rows["availability"].get("measurement_kind") == "OPERATIONAL_AVAILABILITY_PROXY"
