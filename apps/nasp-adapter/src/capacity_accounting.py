"""
Capacity Accounting (PROMPT_SMDCE_V2_CAPACITY_ACCOUNTING).
Ledger check: fetch multidomain metrics, capacity_effective, sum_reserved_active, delta = cost(), PASS/FAIL por domínio.
"""

import logging
from typing import Dict, Any, List, Optional

from opentelemetry import trace

from cost_model import cost

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Safety factor: capacity_effective = raw * (1 - SAFETY_FACTOR) ou raw - margin
CAPACITY_SAFETY_FACTOR = float(__import__("os").getenv("CAPACITY_SAFETY_FACTOR", "0.1"))


def _sum_reserved_by_domain(active_reservations: List[Dict[str, Any]]) -> Dict[str, int]:
    """Soma resourcesReserved (core, ran, transport) de todas as reservas ACTIVE."""
    out = {"core": 0, "ran": 0, "transport": 0}
    for item in active_reservations:
        spec = item.get("spec", {}) or {}
        rr = spec.get("resourcesReserved") or {}
        for k in out:
            out[k] += int(rr.get(k, 0))
    return out


def compute_capacity_effective(multidomain: Dict[str, Any]) -> Dict[str, float]:
    """
    Converte métricas multidomain em capacidade efetiva por domínio (após safety).
    Valores null/indisponíveis → uso de default conservador (ex.: 0 ou 1).
    """
    core = multidomain.get("core") or {}
    upf = (core.get("upf") if isinstance(core, dict) else None) or {}
    # Capacidade "bruta" simplificada: e.g. 100 - cpu_pct como headroom
    cpu = upf.get("cpu_pct")
    if cpu is None:
        cpu = 0.0
    try:
        cpu = float(cpu)
    except (TypeError, ValueError):
        cpu = 0.0
    core_effective = max(0, 100.0 - cpu) * (1 - CAPACITY_SAFETY_FACTOR)

    ran = multidomain.get("ran") or {}
    ue = (ran.get("ue") if isinstance(ran, dict) else None) or {}
    ue_count = ue.get("active_count")
    if ue_count is None:
        ue_count = 0
    try:
        ue_count = int(ue_count)
    except (TypeError, ValueError):
        ue_count = 0
    # Headroom RAN: e.g. 1000 - ue_count (escala arbitrária)
    ran_effective = max(0, 1000 - ue_count) * (1 - CAPACITY_SAFETY_FACTOR)

    transport = multidomain.get("transport") or {}
    rtt = transport.get("rtt_p95_ms") if isinstance(transport, dict) else None
    if rtt is None:
        rtt = 0.0
    try:
        rtt = float(rtt)
    except (TypeError, ValueError):
        rtt = 0.0
    # Headroom transport: menor RTT = mais capacidade
    transport_effective = max(0, 100.0 - min(rtt, 100)) * (1 - CAPACITY_SAFETY_FACTOR)

    return {"core": core_effective, "ran": ran_effective, "transport": transport_effective}


def ledger_check(
    multidomain: Dict[str, Any],
    active_reservations: List[Dict[str, Any]],
    slice_type: str,
    sla_requirements: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Decide PASS/FAIL por domínio.
    Retorna: {"pass": bool, "reasons": [...], "per_domain": {"core": "PASS"|"FAIL", ...}}.
    """
    with tracer.start_as_current_span("ledger_check") as span:
        capacity = compute_capacity_effective(multidomain)
        reserved = _sum_reserved_by_domain(active_reservations)
        delta = cost(slice_type, sla_requirements)

        reasons: List[str] = []
        per_domain: Dict[str, str] = {}
        for domain in ("core", "ran", "transport"):
            cap = capacity.get(domain, 0)
            res = reserved.get(domain, 0)
            inc = delta.get(domain, 1)
            headroom = cap - res
            if headroom < inc:
                per_domain[domain] = "FAIL"
                reasons.append(f"capacity_{domain}:headroom={headroom:.1f} need={inc}")
            else:
                per_domain[domain] = "PASS"

        pass_ = len(reasons) == 0
        span.set_attribute("ledger.pass", pass_)
        span.set_attribute("ledger.reasons_count", len(reasons))
        return {
            "pass": pass_,
            "reasons": reasons,
            "per_domain": per_domain,
            "capacity_effective": capacity,
            "reserved": reserved,
            "delta": delta,
        }
