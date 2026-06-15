"""
Feasibility runtime activation — parity with portal-backend sla_metrics (V1 pressure + viability formula).
Does not alter weights, gates, or transport semantics.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple


def _feasibility_runtime_enabled() -> bool:
    return os.getenv("TRISLA_FEASIBILITY_RUNTIME_ENABLED", "true").lower() == "true"


def _headroom_runtime_enabled() -> bool:
    return os.getenv("TRISLA_RESOURCE_HEADROOM_RUNTIME_ENABLED", "true").lower() == "true"


def _safe_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _normalize(value: Any, max_expected: float) -> Optional[float]:
    v = _safe_float(value)
    if v is None or max_expected <= 0:
        return None
    return min(v / max_expected, 1.0)


def compute_resource_pressure_v1(
    ran: Optional[Dict[str, Any]] = None,
    transport: Optional[Dict[str, Any]] = None,
    core: Optional[Dict[str, Any]] = None,
) -> Optional[float]:
    """Same semantics as portal-backend `compute_resource_pressure` (V1)."""
    w_ran, w_transport, w_core = 0.4, 0.3, 0.3
    prb_norm = _normalize((ran or {}).get("prb_utilization"), 100.0) if ran else None
    rtt_raw = None
    if transport:
        rtt_raw = transport.get("rtt_ms")
        if rtt_raw is None:
            rtt_raw = transport.get("rtt")
    rtt_norm = _normalize(rtt_raw, 200.0) if transport else None
    cpu_raw = None
    if core:
        cpu_raw = core.get("cpu_utilization")
        if cpu_raw is None:
            cpu_raw = core.get("cpu_usage")
        if cpu_raw is None:
            cpu_raw = core.get("cpu")
    cpu_norm = _normalize(cpu_raw, 100.0) if core else None

    weighted_sum = 0.0
    weight_total = 0.0
    for val, w in ((prb_norm, w_ran), (rtt_norm, w_transport), (cpu_norm, w_core)):
        if val is not None:
            weighted_sum += val * w
            weight_total += w
    if weight_total <= 0:
        return None
    return weighted_sum / weight_total


def compute_feasibility_score(ml_risk: float, resource_pressure: float) -> float:
    """Portal parity: max(0, 1 - (risk + resource_pressure) / 2), clamped to [0,1]."""
    r = max(0.0, min(1.0, float(ml_risk)))
    p = max(0.0, min(1.0, float(resource_pressure)))
    return max(0.0, min(1.0, 1.0 - (r + p) / 2.0))


def derive_feasibility_from_snapshot(
    telemetry_snapshot: Optional[Dict[str, Any]],
    ml_risk: float,
) -> Tuple[Optional[float], Optional[float], str]:
    """
    Returns (feasibility_score, resource_pressure_used, source_label).
    resource_pressure is returned for audit only — not written to decision context.
    """
    if not _feasibility_runtime_enabled():
        return None, None, "disabled"
    if not isinstance(telemetry_snapshot, dict):
        return None, None, "missing_snapshot"
    ran = telemetry_snapshot.get("ran") or {}
    transport = telemetry_snapshot.get("transport") or {}
    core = telemetry_snapshot.get("core") or {}
    rp = compute_resource_pressure_v1(ran, transport, core)
    if rp is None:
        return None, None, "missing_pressure_inputs"
    feas = compute_feasibility_score(ml_risk, rp)
    return feas, rp, "sla_viability_derived"


def derive_resource_pressure_from_snapshot(
    telemetry_snapshot: Optional[Dict[str, Any]],
) -> Tuple[Optional[float], str]:
    """V1 multidomain pressure from real telemetry (portal parity)."""
    if not _headroom_runtime_enabled():
        return None, "disabled"
    if not isinstance(telemetry_snapshot, dict):
        return None, "missing_snapshot"
    ran = telemetry_snapshot.get("ran") or {}
    transport = telemetry_snapshot.get("transport") or {}
    core = telemetry_snapshot.get("core") or {}
    rp = compute_resource_pressure_v1(ran, transport, core)
    if rp is None:
        return None, "missing_pressure_inputs"
    return max(0.0, min(1.0, float(rp))), "resource_pressure_v1_derived"
