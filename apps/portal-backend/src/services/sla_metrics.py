"""SLA-aware derived metrics for scientific evaluation (metadata only; no decision impact)."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

# --- Policy V2 weights (sum = 1.0); adjust in one place only ---
W_PRB = 0.25
W_RAN_LAT = 0.15
W_RTT = 0.20
W_JITTER = 0.10
W_CPU = 0.20
W_MEM = 0.10

# --- Normalization ceilings (units explicit) ---
# PRB: already 0–100 %
MAX_RAN_LATENCY_MS = 20.0  # ms — referência para escala [0,1] da latência RAN
MAX_RTT_MS = 50.0  # ms
MAX_JITTER_MS = 20.0  # ms
MAX_CPU_PERCENT = 100.0  # % (valor numérico 0–100)
MEMORY_REF_BYTES = 16.0 * 1024**3  # 16 GiB — referência para memória Core


def _use_sla_v2() -> bool:
    return os.getenv("USE_SLA_V2", "false").lower() in ("1", "true", "yes", "on")


def safe_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def normalize(value, max_expected):
    """Scale a domain reading to [0, 1] using a reference maximum."""
    if value is None:
        return None
    try:
        v = float(value)
        if max_expected <= 0:
            return None
        return min(v / max_expected, 1.0)
    except (TypeError, ValueError):
        return None


def clamp01(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    try:
        v = float(value)
        return max(0.0, min(1.0, v))
    except (TypeError, ValueError):
        return None


def compute_resource_pressure(ran=None, transport=None, core=None):
    """
    V1 — inalterado semanticamente: PRB + RTT + CPU com pesos 0.4 / 0.3 / 0.3
    e renormalização quando termos faltam.
    """
    w_ran = 0.4
    w_transport = 0.3
    w_core = 0.3

    prb_norm = None
    rtt_norm = None
    cpu_norm = None

    if ran:
        prb_norm = normalize(ran.get("prb_utilization"), 100.0)

    if transport:
        rtt_raw = transport.get("rtt_ms")
        if rtt_raw is None:
            rtt_raw = transport.get("rtt")
        rtt_norm = normalize(rtt_raw, 200.0)

    if core:
        cpu_raw = core.get("cpu_utilization")
        if cpu_raw is None:
            cpu_raw = core.get("cpu_usage")
        if cpu_raw is None:
            cpu_raw = core.get("cpu")
        cpu_norm = normalize(cpu_raw, 100.0)

    weighted_sum = 0.0
    weight_total = 0.0

    if prb_norm is not None:
        weighted_sum += prb_norm * w_ran
        weight_total += w_ran

    if rtt_norm is not None:
        weighted_sum += rtt_norm * w_transport
        weight_total += w_transport

    if cpu_norm is not None:
        weighted_sum += cpu_norm * w_core
        weight_total += w_core

    if weight_total == 0.0:
        return None

    return weighted_sum / weight_total


def compute_resource_pressure_v2(snapshot: Optional[Dict[str, Any]]) -> Optional[float]:
    """
    V2 — contrato telemetria: usa até 6 dimensões com pesos W_*.
    Chaves preferenciais: latency_ms, rtt_ms, jitter_ms, cpu_utilization, memory_bytes;
    fallback para nomes legados (latency, rtt, jitter, cpu, memory).
    Termos ausentes são omitidos; pesos renormalizados sobre os disponíveis.
    """
    if not isinstance(snapshot, dict):
        return None
    ran = snapshot.get("ran") or {}
    tr = snapshot.get("transport") or {}
    co = snapshot.get("core") or {}

    prb = safe_float(ran.get("prb_utilization"))
    lat = safe_float(ran.get("latency_ms"))
    if lat is None:
        lat = safe_float(ran.get("latency"))

    rtt = safe_float(tr.get("rtt_ms"))
    if rtt is None:
        rtt = safe_float(tr.get("rtt"))

    jit = safe_float(tr.get("jitter_ms"))
    if jit is None:
        jit = safe_float(tr.get("jitter"))

    cpu = safe_float(co.get("cpu_utilization"))
    if cpu is None:
        cpu = safe_float(co.get("cpu"))

    mem = safe_float(co.get("memory_bytes"))
    if mem is None:
        mem = safe_float(co.get("memory"))

    prb_n = clamp01(prb / 100.0) if prb is not None else None
    lat_n = clamp01(lat / MAX_RAN_LATENCY_MS) if lat is not None else None
    rtt_n = clamp01(rtt / MAX_RTT_MS) if rtt is not None else None
    jit_n = clamp01(jit / MAX_JITTER_MS) if jit is not None else None
    cpu_n = clamp01(cpu / MAX_CPU_PERCENT) if cpu is not None else None
    mem_n = clamp01(mem / MEMORY_REF_BYTES) if mem is not None else None

    terms: List[Tuple[Optional[float], float]] = [
        (prb_n, W_PRB),
        (lat_n, W_RAN_LAT),
        (rtt_n, W_RTT),
        (jit_n, W_JITTER),
        (cpu_n, W_CPU),
        (mem_n, W_MEM),
    ]
    available = [(v, w) for v, w in terms if v is not None]
    if not available:
        return None
    w_tot = sum(w for _, w in available)
    if w_tot <= 0:
        return None
    return sum(v * w for v, w in available) / w_tot


def compute_sla_metrics(
    decision,
    ml_prediction,
    domains,
    telemetry_snapshot: Optional[Dict[str, Any]] = None,
):
    """Generate per-request SLA-aware metrics (proxies where runtime ground truth is absent)."""
    mp = ml_prediction if isinstance(ml_prediction, dict) else {}
    risk = safe_float(mp.get("risk_score"))
    confidence = safe_float(mp.get("confidence"))

    ran = (domains or {}).get("ran") or {}
    transport = (domains or {}).get("transport") or {}
    core = (domains or {}).get("core") or {}

    resource_pressure_v1 = compute_resource_pressure(ran, transport, core)
    resource_pressure_v2 = compute_resource_pressure_v2(telemetry_snapshot)

    use_v2 = _use_sla_v2()
    if use_v2 and resource_pressure_v2 is not None:
        resource_pressure = resource_pressure_v2
        sla_policy_version = "v2"
    elif use_v2 and resource_pressure_v2 is None:
        resource_pressure = resource_pressure_v1
        sla_policy_version = "v2_fallback_v1"
    else:
        resource_pressure = resource_pressure_v1
        sla_policy_version = "v1"

    sla_satisfaction = 1 if decision == "ACCEPT" else 0
    sla_violation = 1 if (decision == "ACCEPT" and risk is not None and risk > 0.7) else 0

    admission_confidence = confidence if confidence is not None else 0.5

    feasibility_score = None
    if risk is not None and resource_pressure is not None:
        feasibility_score = max(0.0, 1.0 - (risk + resource_pressure) / 2)

    return {
        "sla_satisfaction": sla_satisfaction,
        "sla_violation": sla_violation,
        "resource_pressure": resource_pressure,
        "resource_pressure_v1": resource_pressure_v1,
        "resource_pressure_v2": resource_pressure_v2,
        "sla_policy_version": sla_policy_version,
        "admission_confidence": admission_confidence,
        "feasibility_score": feasibility_score,
    }
