"""
MDCE v1 — Multi-Domain Capacity Evaluation (PROMPT_SMDCE_V1_IMPLEMENTATION_v1.0).
Avalia capacidade multidomínio (Core, RAN, Transport) antes de ACCEPT.
Regras conservadoras: FAIL se limites excedidos; métrica indisponível para slice crítico (URLLC) pode FAIL por segurança.
"""

import os
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# Thresholds configuráveis (sanidade: reduzir para forçar FAIL)
MDCE_CPU_PCT_LIMIT = float(os.getenv("MDCE_CPU_PCT_LIMIT", "85.0"))
MDCE_MEM_PCT_LIMIT = float(os.getenv("MDCE_MEM_PCT_LIMIT", "85.0"))
MDCE_UE_COUNT_LIMIT = int(os.getenv("MDCE_UE_COUNT_LIMIT", "10000"))
MDCE_URLLC_RTT_BUDGET_MS = float(os.getenv("MDCE_URLLC_RTT_BUDGET_MS", "20.0"))


def evaluate(
    slice_type: str,
    sla_requirements: Dict[str, Any],
    metrics: Dict[str, Any],
) -> Tuple[str, List[str]]:
    """
    Avalia capacidade multidomínio (MDCE v1).
    
    Args:
        slice_type: URLLC | eMBB | mMTC
        sla_requirements: requisitos do SLA (ex.: latency, reliability)
        metrics: schema SSOT do GET /api/v1/metrics/multidomain (core.upf.*, ran.ue.*, transport.*)
    
    Returns:
        ("PASS" | "FAIL", list of reasons)
    """
    reasons: List[str] = []
    if MDCE_FORCE_FAIL:
        return ("FAIL", ["forced_fail_sanity"])
    slice_upper = (slice_type or "eMBB").strip().upper()
    if slice_upper == "EMBB":
        slice_upper = "eMBB"
    elif slice_upper == "URLLC":
        slice_upper = "URLLC"
    elif slice_upper == "MMTC":
        slice_upper = "mMTC"

    core = metrics.get("core") or {}
    upf = core.get("upf") or {}
    ran = metrics.get("ran") or {}
    ue = ran.get("ue") or {}
    transport = metrics.get("transport") or {}

    # Regra: FAIL se core.upf.cpu_pct > 85
    cpu_pct = upf.get("cpu_pct")
    if cpu_pct is not None:
        if cpu_pct > MDCE_CPU_PCT_LIMIT:
            reasons.append(f"core.upf.cpu_pct={cpu_pct} > {MDCE_CPU_PCT_LIMIT}")
    # Opcional: se URLLC e métrica crítica indisponível → FAIL por segurança (documentado)
    # else: não falhamos só por indisponibilidade para não bloquear demais

    # Regra: FAIL se core.upf.mem_pct > 85
    mem_pct = upf.get("mem_pct")
    if mem_pct is not None:
        if mem_pct > MDCE_MEM_PCT_LIMIT:
            reasons.append(f"core.upf.mem_pct={mem_pct} > {MDCE_MEM_PCT_LIMIT}")

    # Regra: FAIL se URLLC e transport.rtt_p95_ms > budget
    rtt_p95 = transport.get("rtt_p95_ms")
    if slice_upper == "URLLC" and rtt_p95 is not None:
        budget = sla_requirements.get("latency")
        if isinstance(budget, dict) and "max_ms" in budget:
            budget_ms = float(budget["max_ms"])
        elif isinstance(budget, (int, float)):
            budget_ms = float(budget)
        else:
            budget_ms = MDCE_URLLC_RTT_BUDGET_MS
        if rtt_p95 > budget_ms:
            reasons.append(f"URLLC transport.rtt_p95_ms={rtt_p95} > {budget_ms}")

    # Regra: FAIL se ran.ue.active_count > limite
    ue_count = ue.get("active_count")
    if ue_count is not None:
        if ue_count > MDCE_UE_COUNT_LIMIT:
            reasons.append(f"ran.ue.active_count={ue_count} > {MDCE_UE_COUNT_LIMIT}")

    if reasons:
        return ("FAIL", reasons)
    return ("PASS", [])
