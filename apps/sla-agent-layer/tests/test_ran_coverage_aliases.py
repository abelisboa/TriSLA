"""Sprint 9D — RAN explainability aliases (jitter←transport, cpu←PRB)."""
from __future__ import annotations

from domain_compliance import compute_all_domains_compliance, compute_domain_compliance


def _ran_rows(out: dict) -> dict:
    rows = out.get("metric_explainability") or []
    return {r["metric"]: r for r in rows}


def test_case_a_jitter_from_transport_fallback():
    """transport.jitter_ms only → RAN jitter observed."""
    out = compute_all_domains_compliance(
        metrics_ran={"latency_ms": 5.0, "reliability": 100.0},
        metrics_transport={"jitter_ms": 0.4},
        metrics_core={"cpu": 0.01, "memory": 0.01},
        slice_type="URLLC",
    )
    jitter = _ran_rows(out["ran"])["jitter_ms"]
    assert jitter["status"] != "MISSING"
    assert jitter["observed"] == 0.4
    assert jitter.get("source") == "telemetry_snapshot.transport"
    assert "transport.jitter_ms" in (jitter.get("measurement_note") or "")


def test_case_b_prb_as_cpu_utilization():
    """prb_utilization → RAN cpu_utilization observed."""
    out = compute_domain_compliance(
        "ran",
        {"prb_utilization": 45.0, "latency_ms": 5.0},
        "URLLC",
    )
    cpu = _ran_rows(out)["cpu_utilization"]
    assert cpu["status"] != "MISSING"
    assert cpu["observed"] == 45.0
    assert "PRB" in (cpu.get("measurement_note") or "")


def test_case_c_missing_when_absent():
    out = compute_domain_compliance("ran", {}, "URLLC")
    rows = _ran_rows(out)
    assert rows["jitter_ms"]["status"] == "MISSING"
    assert rows["cpu_utilization"]["status"] == "MISSING"


def test_urllc_four_kpis_non_missing_with_full_snapshot():
    out = compute_all_domains_compliance(
        metrics_ran={
            "latency_ms": 5.6,
            "reliability": 100.0,
            "prb_utilization": 12.0,
        },
        metrics_transport={"jitter_ms": 0.42, "packet_loss": 0.0},
        metrics_core={"cpu": 0.001, "memory": 0.009, "availability": 80.0},
        slice_type="URLLC",
    )
    rows = _ran_rows(out["ran"])
    for key in ("latency_ms", "jitter_ms", "reliability", "cpu_utilization"):
        assert rows[key]["status"] != "MISSING", key
