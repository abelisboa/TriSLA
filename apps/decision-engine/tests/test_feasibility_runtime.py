"""Unit checks for feasibility runtime activation (portal parity)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from feasibility_runtime import (  # noqa: E402
    compute_feasibility_score,
    compute_resource_pressure_v1,
    derive_feasibility_from_snapshot,
    derive_resource_pressure_from_snapshot,
)


def test_resource_pressure_v1_bounded():
    snap = {
        "ran": {"prb_utilization": 50},
        "transport": {"rtt_ms": 10},
        "core": {"cpu_utilization": 40},
    }
    rp = compute_resource_pressure_v1(snap["ran"], snap["transport"], snap["core"])
    assert rp is not None
    assert 0.0 <= rp <= 1.0


def test_feasibility_formula_monotone_in_risk():
    rp = 0.5
    f_low = compute_feasibility_score(0.2, rp)
    f_high = compute_feasibility_score(0.8, rp)
    assert f_low > f_high


def test_derive_from_snapshot():
    snap = {
        "ran": {"prb_utilization": 30},
        "transport": {"rtt_ms": 5},
        "core": {"cpu_utilization": 20},
    }
    feas, rp, src = derive_feasibility_from_snapshot(snap, 0.4)
    assert src == "sla_viability_derived"
    assert feas is not None and rp is not None
    assert 0.0 <= feas <= 1.0
    assert abs(feas - compute_feasibility_score(0.4, rp)) < 1e-9


def test_disabled_env():
    os.environ["TRISLA_FEASIBILITY_RUNTIME_ENABLED"] = "false"
    try:
        feas, _, src = derive_feasibility_from_snapshot(
            {"ran": {"prb_utilization": 1}}, 0.5
        )
        assert feas is None and src == "disabled"
    finally:
        os.environ.pop("TRISLA_FEASIBILITY_RUNTIME_ENABLED", None)


def test_headroom_pressure_derived():
    snap = {
        "ran": {"prb_utilization": 50},
        "transport": {"rtt_ms": 10},
        "core": {"cpu_utilization": 40},
    }
    rp, src = derive_resource_pressure_from_snapshot(snap)
    assert src == "resource_pressure_v1_derived"
    assert rp is not None and 0.0 <= rp <= 1.0


def test_headroom_goodness_inverse_pressure():
    snap = {"ran": {"prb_utilization": 80}, "transport": {"rtt_ms": 40}, "core": {"cpu_utilization": 60}}
    rp, _ = derive_resource_pressure_from_snapshot(snap)
    g_head = 1.0 - rp
    assert 0.0 <= g_head <= 1.0
