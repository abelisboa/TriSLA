"""TRISLA_09: slice-aware multidomain admission helpers (isolated module; stdlib only)."""

def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _normalize_ratio(value, limit):
    value = _safe_float(value)
    limit = max(_safe_float(limit), 1e-9)
    return max(0.0, min(1.0, value / limit))


# PHASE 11 (PR-3) — Defesa em profundidade contra mismatch de unidade.
# Os campos `cpu_utilization` e `memory_utilization` são contratualmente
# percentuais 0..100 (vide TELEMETRY_UNITS_V2 PR-1). Valores muito acima
# de 100 indicam input em escala errada (ex.: bytes, cores-segundo, …)
# e historicamente saturavam `core_risk=1.0` silenciosamente.
# Este sanity-check **não mascara** o erro — registra flags e neutraliza
# o input em vez de penalizar a decisão.
_PERCENT_SANITY_UPPER = 100.0
_PERCENT_HARD_UPPER = 1000.0  # acima disso classificamos como provável "bytes/raw"


def _percent_or_degraded(value, field_label, mismatch_flags):
    """Retorna `(value_safe, was_degraded: bool)`.

    Semântica:
      - `None`/erro de parsing → `(0.0, False)` (mantém comportamento de
        `_safe_float` legado; PR-3 não muda missing→saturate).
      - `0 ≤ v ≤ 100`           → `(v, False)`.
      - `100 < v ≤ 1000`         → clamp para 100 + flag `OUT_OF_RANGE`
                                   (provável escala 0..1000 ou ruído).
      - `v > 1000`               → `(None, True)` + flags
                                   `unit_mismatch_detected`,
                                   `fallback_normalization_applied`.
        `None` sinaliza ao caller para tratar como missing (não saturar).
    """
    if value is None:
        return 0.0, False
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0, False
    if v < 0:
        mismatch_flags.setdefault("reason_codes_advisory", []).append(
            f"INPUT_NEGATIVE_{field_label.upper()}"
        )
        return 0.0, False
    if v <= _PERCENT_SANITY_UPPER:
        return v, False
    if v <= _PERCENT_HARD_UPPER:
        mismatch_flags.setdefault("reason_codes_advisory", []).append(
            f"INPUT_OUT_OF_RANGE_{field_label.upper()}"
        )
        return _PERCENT_SANITY_UPPER, False
    # Suspect: bytes or raw counter → degrade safely.
    mismatch_flags["memory_unit_mismatch_detected"] = True
    mismatch_flags["fallback_normalization_applied"] = True
    mismatch_flags.setdefault("reason_codes_advisory", []).append(
        f"INPUT_UNIT_MISMATCH_{field_label.upper()}"
    )
    mismatch_flags.setdefault("degraded_inputs", []).append(
        {"field": field_label, "observed_value": v,
         "policy_upper": _PERCENT_SANITY_UPPER}
    )
    return None, True


def _prb_percent(raw):
    """Normalize PRB to 0..100 (telemetry may be percent or 0..1 fraction)."""
    v = _safe_float(raw, 0.0)
    if 0.0 <= v <= 1.0:
        return v * 100.0
    return v


def _infer_slice_type(payload):
    """Infer slice_type from explicit fields or SLA requirements."""
    if not isinstance(payload, dict):
        return "embb"

    for key in ("slice_type", "service_type", "slice", "sst_name"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            s = val.strip().lower()
            if "urllc" in s:
                return "urllc"
            if "mmtc" in s or "miot" in s:
                return "mmtc"
            if "embb" in s or "emmb" in s:
                return "embb"

    form = payload.get("form_values") or payload.get("requirements") or {}
    latency = _safe_float(form.get("latency") or form.get("latency_ms"), 999)
    reliability = _safe_float(form.get("reliability"), 0)
    throughput = _safe_float(form.get("throughput") or form.get("throughput_mbps"), 0)
    devices = _safe_float(form.get("device_count") or form.get("devices"), 0)

    if latency <= 10 and reliability >= 99.99:
        return "urllc"
    if devices >= 500:
        return "mmtc"
    if throughput >= 100:
        return "embb"
    return "embb"


SLICE_POLICY = {
    "urllc": {
        "weights": {"ran": 0.30, "transport": 0.40, "core": 0.15, "sla": 0.15},
        "rtt_reject_ms": 20,
        "rtt_renegotiate_ms": 10,
        "jitter_reject_ms": 10,
        "jitter_renegotiate_ms": 5,
        "core_cpu_reject": 90,
        "core_cpu_renegotiate": 75,
        "core_mem_reject": 90,
        "core_mem_renegotiate": 75,
        "prb_reject": 85,
        "prb_renegotiate": 70,
    },
    "embb": {
        "weights": {"ran": 0.40, "transport": 0.20, "core": 0.20, "sla": 0.20},
        "rtt_reject_ms": 80,
        "rtt_renegotiate_ms": 50,
        "jitter_reject_ms": 40,
        "jitter_renegotiate_ms": 25,
        "core_cpu_reject": 90,
        "core_cpu_renegotiate": 80,
        "core_mem_reject": 90,
        "core_mem_renegotiate": 80,
        "prb_reject": 85,
        "prb_renegotiate": 75,
    },
    "mmtc": {
        "weights": {"ran": 0.20, "transport": 0.15, "core": 0.40, "sla": 0.25},
        "rtt_reject_ms": 200,
        "rtt_renegotiate_ms": 120,
        "jitter_reject_ms": 80,
        "jitter_renegotiate_ms": 50,
        "core_cpu_reject": 85,
        "core_cpu_renegotiate": 70,
        "core_mem_reject": 85,
        "core_mem_renegotiate": 70,
        "prb_reject": 90,
        "prb_renegotiate": 80,
    },
}


def compute_slice_aware_multidomain_decision(
    payload,
    telemetry_snapshot,
    ml_risk=0.0,
    *,
    skip_prb_critical_gate: bool = False,
):
    """Return decision package using slice-aware RAN/Transport/Core gates.

    When skip_prb_critical_gate is True, PRB is only used in ran_risk weighting (caller
    already applied env HARD_PRB gates). Use from DecisionEngine after hard PRB checks.
    """
    slice_type = _infer_slice_type(payload)
    policy = SLICE_POLICY.get(slice_type, SLICE_POLICY["embb"])
    weights = policy["weights"]

    telemetry_snapshot = telemetry_snapshot or {}
    ran = telemetry_snapshot.get("ran") or {}
    transport = telemetry_snapshot.get("transport") or {}
    core = telemetry_snapshot.get("core") or {}
    form = (payload or {}).get("form_values") or (payload or {}).get("requirements") or {}

    prb = _prb_percent(ran.get("prb_utilization") or ran.get("prb") or ran.get("ran_prb_utilization"))
    rtt = _safe_float(transport.get("rtt") or transport.get("latency") or transport.get("latency_ms"), 0)
    jitter = _safe_float(transport.get("jitter") or transport.get("jitter_ms"), 0)
    # PHASE 11 (PR-3) — Sanity-check de unidade. Os campos cpu/memory são
    # contratualmente % (0..100); valores muito acima indicam mismatch e
    # devem ser tratados como missing em vez de saturar `core_risk=1.0`.
    mismatch_flags: dict = {}
    cpu_raw = core.get("cpu_utilization") if core.get("cpu_utilization") is not None else core.get("cpu")
    mem_raw = core.get("memory_utilization") if core.get("memory_utilization") is not None else core.get("memory")
    cpu_safe, cpu_degraded = _percent_or_degraded(cpu_raw, "cpu", mismatch_flags)
    mem_safe, mem_degraded = _percent_or_degraded(mem_raw, "mem", mismatch_flags)
    # Para `_normalize_ratio`/gates: substituir None por 0 (missing seguro).
    cpu = cpu_safe if cpu_safe is not None else 0.0
    mem = mem_safe if mem_safe is not None else 0.0

    latency_req = _safe_float(form.get("latency") or form.get("latency_ms"), 0)
    reliability_req = _safe_float(form.get("reliability"), 0)
    throughput_req = _safe_float(form.get("throughput") or form.get("throughput_mbps"), 0)
    devices_req = _safe_float(form.get("device_count") or form.get("devices"), 0)

    reason_codes = []

    # Critical gates by slice type (PRB: optional when engine already applied HARD_PRB)
    if not skip_prb_critical_gate and prb >= policy["prb_reject"]:
        reason_codes.append(f"{slice_type.upper()}_RAN_PRB_REJECT")
        return {
            "decision": "REJECT",
            "decision_score": 0.0,
            "slice_type": slice_type,
            "reason_codes": reason_codes,
            "multidomain_risk": 1.0,
        }

    if rtt >= policy["rtt_reject_ms"] and slice_type == "urllc":
        reason_codes.append("URLLC_TRANSPORT_RTT_REJECT")
        return {
            "decision": "REJECT",
            "decision_score": 0.0,
            "slice_type": slice_type,
            "reason_codes": reason_codes,
            "multidomain_risk": 1.0,
        }

    if jitter >= policy["jitter_reject_ms"] and slice_type == "urllc":
        reason_codes.append("URLLC_TRANSPORT_JITTER_REJECT")
        return {
            "decision": "REJECT",
            "decision_score": 0.0,
            "slice_type": slice_type,
            "reason_codes": reason_codes,
            "multidomain_risk": 1.0,
        }

    # PHASE 11 (PR-3) — Hard gate só pode disparar se a unidade for confiável.
    # Se cpu/mem chegaram degraded (mismatch detectado), tratamos como missing
    # e NÃO acionamos REJECT silencioso — em vez disso, sinalizamos advisory.
    cpu_gate_trusted = not cpu_degraded
    mem_gate_trusted = not mem_degraded
    if slice_type == "mmtc" and (
        (cpu_gate_trusted and cpu >= policy["core_cpu_reject"])
        or (mem_gate_trusted and mem >= policy["core_mem_reject"])
    ):
        reason_codes.append("MMTC_CORE_CAPACITY_REJECT")
        out = {
            "decision": "REJECT",
            "decision_score": 0.0,
            "slice_type": slice_type,
            "reason_codes": reason_codes,
            "multidomain_risk": 1.0,
        }
        if mismatch_flags:
            out.update(mismatch_flags)
        return out

    ran_risk = _normalize_ratio(prb, policy["prb_reject"])
    transport_risk = max(
        _normalize_ratio(rtt, policy["rtt_reject_ms"]),
        _normalize_ratio(jitter, policy["jitter_reject_ms"]),
    )
    core_risk = max(
        _normalize_ratio(cpu, policy["core_cpu_reject"]),
        _normalize_ratio(mem, policy["core_mem_reject"]),
    )

    # SLA demand risk by type
    if slice_type == "urllc":
        sla_risk = max(
            _normalize_ratio(max(0, 10 - latency_req), 10) if latency_req else 0,
            _normalize_ratio(max(0, reliability_req - 99.99), 0.01) if reliability_req else 0,
        )
    elif slice_type == "mmtc":
        sla_risk = _normalize_ratio(devices_req, 1000)
    else:
        sla_risk = _normalize_ratio(throughput_req, 500)

    multidomain_risk = (
        weights["ran"] * ran_risk +
        weights["transport"] * transport_risk +
        weights["core"] * core_risk +
        weights["sla"] * sla_risk
    )

    # incorporate ML risk as refinement
    ml_risk = _safe_float(ml_risk, 0)
    final_risk = min(1.0, 0.80 * multidomain_risk + 0.20 * ml_risk)
    decision_score = max(0.0, 1.0 - final_risk)

    if not skip_prb_critical_gate and prb >= policy["prb_renegotiate"]:
        reason_codes.append(f"{slice_type.upper()}_RAN_PRB_RENEGOTIATE")
    if rtt >= policy["rtt_renegotiate_ms"]:
        reason_codes.append(f"{slice_type.upper()}_TRANSPORT_RTT_RENEGOTIATE")
    if jitter >= policy["jitter_renegotiate_ms"]:
        reason_codes.append(f"{slice_type.upper()}_TRANSPORT_JITTER_RENEGOTIATE")
    # PHASE 11 (PR-3) — core gate só com unidade confiável; degraded vira advisory.
    if (cpu_gate_trusted and cpu >= policy["core_cpu_renegotiate"]) or (
        mem_gate_trusted and mem >= policy["core_mem_renegotiate"]
    ):
        reason_codes.append(f"{slice_type.upper()}_CORE_RENEGOTIATE")

    if final_risk >= 0.75:
        decision = "REJECT"
        reason_codes.append(f"{slice_type.upper()}_MULTIDOMAIN_RISK_REJECT")
    elif final_risk >= 0.55 or reason_codes:
        decision = "RENEGOTIATE"
        if not reason_codes:
            reason_codes.append(f"{slice_type.upper()}_MULTIDOMAIN_RISK_RENEGOTIATE")
    else:
        decision = "ACCEPT"
        reason_codes.append(f"{slice_type.upper()}_MULTIDOMAIN_FEASIBLE")

    out = {
        "decision": decision,
        "decision_score": round(decision_score, 6),
        "slice_type": slice_type,
        "reason_codes": reason_codes,
        "ran_risk": round(ran_risk, 6),
        "transport_risk": round(transport_risk, 6),
        "core_risk": round(core_risk, 6),
        "sla_risk": round(sla_risk, 6),
        "multidomain_risk": round(multidomain_risk, 6),
        "final_risk": round(final_risk, 6),
    }
    # PHASE 11 (PR-3) — flags de defesa propagadas no resultado para
    # observabilidade (não mascaram, apenas registram).
    if mismatch_flags:
        out.update(mismatch_flags)
    return out
