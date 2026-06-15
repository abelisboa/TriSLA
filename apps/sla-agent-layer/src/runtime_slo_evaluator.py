"""
Runtime SLO Evaluator — Sprint 5M4 closed-loop observation.

Deterministic comparison of contract v2 telemetry_snapshot against SLA requirements
and slice-aware domain thresholds. No ML inference; no autonomous remediation.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from domain_compliance import build_domain_explainability, compute_all_domains_compliance

ASSURANCE_COMPLIANT = "COMPLIANT"
ASSURANCE_WARNING = "WARNING"
ASSURANCE_AT_RISK = "AT_RISK"
ASSURANCE_VIOLATED = "VIOLATED"

_VALID_STATES = {
    ASSURANCE_COMPLIANT,
    ASSURANCE_WARNING,
    ASSURANCE_AT_RISK,
    ASSURANCE_VIOLATED,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pick_num(obj: Optional[Dict[str, Any]], *keys: str) -> Optional[float]:
    if not isinstance(obj, dict):
        return None
    for key in keys:
        val = obj.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                continue
    return None


def parse_sla_numeric(value: Any) -> Optional[float]:
    """Parse SLA requirement values like '10ms', '100Mbps', or raw numbers."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if not text:
        return None
    match = re.match(r"^([\d.]+)\s*(ms|mbps|gbps|percent|%|s)?$", text)
    if not match:
        try:
            return float(text)
        except ValueError:
            return None
    num = float(match.group(1))
    unit = match.group(2) or ""
    if unit in ("percent", "%") and num > 1.0:
        return num / 100.0
    return num


def _service_profile_violations(
    telemetry_snapshot: Dict[str, Any],
    sla_requirements: Optional[Dict[str, Any]],
) -> Tuple[List[str], List[str]]:
    """Return (violations, warnings) for service-profile KPIs."""
    violations: List[str] = []
    warnings: List[str] = []
    if not isinstance(sla_requirements, dict):
        return violations, warnings

    ran = telemetry_snapshot.get("ran") if isinstance(telemetry_snapshot.get("ran"), dict) else {}
    transport = (
        telemetry_snapshot.get("transport")
        if isinstance(telemetry_snapshot.get("transport"), dict)
        else {}
    )

    req_latency = parse_sla_numeric(
        sla_requirements.get("latency")
        or sla_requirements.get("latencia_maxima_ms")
        or sla_requirements.get("latency_ms")
    )
    obs_latency = _pick_num(ran, "latency_ms", "latency") or _pick_num(
        transport, "rtt_ms", "rtt", "latency_ms", "latency"
    )
    if req_latency is not None and obs_latency is not None:
        if obs_latency > req_latency:
            violations.append("service_profile.latency")
        elif obs_latency > req_latency * 0.85:
            warnings.append("service_profile.latency")

    req_throughput = parse_sla_numeric(
        sla_requirements.get("throughput") or sla_requirements.get("throughput_mbps")
    )
    obs_throughput = _pick_num(transport, "throughput_mbps", "throughput")
    if req_throughput is not None and obs_throughput is not None:
        if obs_throughput < req_throughput:
            violations.append("service_profile.throughput")
        elif obs_throughput < req_throughput * 1.15:
            warnings.append("service_profile.throughput")

    req_reliability = parse_sla_numeric(
        sla_requirements.get("reliability")
        or sla_requirements.get("availability")
        or sla_requirements.get("confiabilidade_percent")
    )
    obs_reliability = _pick_num(ran, "reliability") or _pick_num(
        telemetry_snapshot.get("core") if isinstance(telemetry_snapshot.get("core"), dict) else {},
        "availability",
    )
    if req_reliability is not None and obs_reliability is not None:
        if obs_reliability < req_reliability:
            violations.append("service_profile.reliability")
        elif obs_reliability < req_reliability * 1.0001:
            warnings.append("service_profile.reliability")

    return violations, warnings


def _state_from_compliance(
    sla_compliance: float,
    violations: List[str],
    warnings: List[str],
) -> str:
    if violations:
        if sla_compliance < 0.50 or len(violations) >= 2:
            return ASSURANCE_VIOLATED
        return ASSURANCE_AT_RISK
    if sla_compliance >= 0.85 and not warnings:
        return ASSURANCE_COMPLIANT
    if sla_compliance >= 0.70 or warnings:
        return ASSURANCE_WARNING
    if sla_compliance >= 0.50:
        return ASSURANCE_AT_RISK
    return ASSURANCE_VIOLATED


def _recommendation_for_state(
    state: str,
    violations: List[str],
    warnings: List[str],
    bottleneck_domain: Optional[str],
    drift_detected: bool,
) -> str:
    if state == ASSURANCE_COMPLIANT and not drift_detected:
        return "Runtime metrics within SLA targets; continue periodic observation."
    parts: List[str] = []
    if drift_detected:
        parts.append("Telemetry drift detected versus reference snapshot")
    if violations:
        parts.append(f"violations: {', '.join(violations)}")
    if warnings:
        parts.append(f"warnings: {', '.join(warnings)}")
    if bottleneck_domain:
        parts.append(f"review {bottleneck_domain} domain")
    if state == ASSURANCE_WARNING:
        return "Monitor " + "; ".join(parts) if parts else "Monitor approaching SLA limits."
    if state == ASSURANCE_AT_RISK:
        return "Investigate " + "; ".join(parts) if parts else "Investigate SLA risk indicators."
    return "Escalate " + "; ".join(parts) if parts else "Escalate SLA violation for operator review."


def detect_drift(
    reference: Optional[Dict[str, Any]],
    current: Dict[str, Any],
    *,
    prb_threshold: float = 5.0,
    latency_threshold: float = 2.0,
    rtt_threshold: float = 1.0,
    jitter_threshold: float = 1.0,
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Deterministic drift detection between reference and current snapshots."""
    if not isinstance(reference, dict) or not reference:
        return False, []

    indicators: List[Dict[str, Any]] = []

    def compare(path: str, ref_val: Optional[float], cur_val: Optional[float], lim: float) -> None:
        if ref_val is None or cur_val is None:
            return
        delta = cur_val - ref_val
        if abs(delta) > lim:
            indicators.append(
                {"path": path, "reference": ref_val, "current": cur_val, "delta": delta}
            )

    ran_r = reference.get("ran") if isinstance(reference.get("ran"), dict) else {}
    ran_c = current.get("ran") if isinstance(current.get("ran"), dict) else {}
    tr_r = reference.get("transport") if isinstance(reference.get("transport"), dict) else {}
    tr_c = current.get("transport") if isinstance(current.get("transport"), dict) else {}
    co_r = reference.get("core") if isinstance(reference.get("core"), dict) else {}
    co_c = current.get("core") if isinstance(current.get("core"), dict) else {}

    compare(
        "ran.prb_utilization",
        _pick_num(ran_r, "prb_utilization"),
        _pick_num(ran_c, "prb_utilization"),
        prb_threshold,
    )
    compare(
        "ran.latency",
        _pick_num(ran_r, "latency_ms", "latency"),
        _pick_num(ran_c, "latency_ms", "latency"),
        latency_threshold,
    )
    compare(
        "transport.rtt",
        _pick_num(tr_r, "rtt_ms", "rtt"),
        _pick_num(tr_c, "rtt_ms", "rtt"),
        rtt_threshold,
    )
    compare(
        "transport.jitter",
        _pick_num(tr_r, "jitter_ms", "jitter"),
        _pick_num(tr_c, "jitter_ms", "jitter"),
        jitter_threshold,
    )
    compare(
        "core.cpu",
        _pick_num(co_r, "cpu", "cpu_utilization"),
        _pick_num(co_c, "cpu", "cpu_utilization"),
        0.05,
    )

    return len(indicators) > 0, indicators


def _effective_sla_compliance(compliance: Dict[str, Any], snap: Dict[str, Any]) -> float:
    """Use domain scores when present; neutral score when telemetry exists but no threshold matched."""
    scores: List[float] = []
    for domain in ("ran", "transport", "core"):
        block = compliance.get(domain) if isinstance(compliance.get(domain), dict) else {}
        score = block.get("compliance")
        domain_data = snap.get(domain) if isinstance(snap.get(domain), dict) else {}
        if isinstance(score, (int, float)) and score > 0:
            scores.append(float(score))
        elif domain_data:
            scores.append(1.0)
    return min(scores) if scores else 0.0


def evaluate_runtime_assurance(
    *,
    telemetry_snapshot: Optional[Dict[str, Any]],
    sla_requirements: Optional[Dict[str, Any]] = None,
    slice_type: str = "EMBB",
    reference_telemetry_snapshot: Optional[Dict[str, Any]] = None,
    previous_state: Optional[str] = None,
    intent_id: Optional[str] = None,
    nest_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate runtime assurance from telemetry snapshot and SLA requirements.

    Returns dict with runtime_assurance block and optional runtime_governance_event.
    """
    evaluated_at = _utc_now()
    snap = telemetry_snapshot if isinstance(telemetry_snapshot, dict) else {}

    ran = snap.get("ran") if isinstance(snap.get("ran"), dict) else {}
    transport = snap.get("transport") if isinstance(snap.get("transport"), dict) else {}
    core = snap.get("core") if isinstance(snap.get("core"), dict) else {}

    if not ran and not transport and not core:
        assurance = {
            "state": ASSURANCE_AT_RISK,
            "violations": ["telemetry_snapshot.empty"],
            "warnings": [],
            "drift_detected": False,
            "drift_indicators": [],
            "recommendation": "Telemetry snapshot unavailable; revalidation required.",
            "assurance_state": ASSURANCE_AT_RISK,
            "last_evaluation": evaluated_at,
            "slice_type": slice_type,
            "sla_compliance": 0.0,
            "bottleneck_domain": None,
        }
        return {
            "runtime_assurance": assurance,
            "runtime_assurance_evaluated": True,
            "runtime_governance_event": None,
        }

    compliance = compute_all_domains_compliance(
        metrics_ran=ran,
        metrics_transport=transport,
        metrics_core=core,
        slice_type=slice_type.upper(),
        sla_requirements=sla_requirements,
    )
    sla_compliance = _effective_sla_compliance(compliance, snap)
    sp_violations, sp_warnings = _service_profile_violations(snap, sla_requirements)
    violations = list(sp_violations)
    warnings = list(sp_warnings)

    drift_detected, drift_indicators = detect_drift(reference_telemetry_snapshot, snap)
    if drift_detected and not violations:
        warnings.append("telemetry.drift")

    state = _state_from_compliance(
        sla_compliance,
        violations,
        warnings,
    )
    recommendation = _recommendation_for_state(
        state,
        violations,
        warnings,
        compliance.get("bottleneck_domain"),
        drift_detected,
    )

    assurance = {
        "state": state,
        "violations": violations,
        "warnings": warnings,
        "drift_detected": drift_detected,
        "drift_indicators": drift_indicators,
        "recommendation": recommendation,
        "assurance_state": state,
        "last_evaluation": evaluated_at,
        "slice_type": slice_type.upper(),
        "sla_compliance": sla_compliance,
        "bottleneck_domain": compliance.get("bottleneck_domain"),
        "domain_compliance": {
            "ran": (compliance.get("ran") or {}).get("compliance"),
            "transport": (compliance.get("transport") or {}).get("compliance"),
            "core": (compliance.get("core") or {}).get("compliance"),
        },
        "domain_explainability": build_domain_explainability(compliance),
    }

    governance_event = None
    prev = previous_state if previous_state in _VALID_STATES else None
    if prev and prev != state:
        governance_event = build_runtime_governance_event(
            intent_id=intent_id,
            nest_id=nest_id,
            previous_state=prev,
            new_state=state,
            recommendation=recommendation,
            violations=violations,
            drift_detected=drift_detected,
        )

    return {
        "runtime_assurance": assurance,
        "runtime_assurance_evaluated": True,
        "runtime_governance_event": governance_event,
    }


def build_runtime_governance_event(
    *,
    intent_id: Optional[str],
    nest_id: Optional[str],
    previous_state: str,
    new_state: str,
    recommendation: str,
    violations: List[str],
    drift_detected: bool,
) -> Dict[str, Any]:
    """Additive runtime governance event — does not alter blockchain registration."""
    event_id = f"ge_runtime_{uuid.uuid4().hex[:32]}"
    return {
        "governance_event_id": event_id,
        "event_type": "RUNTIME_ASSURANCE",
        "event_category": "runtime_assurance_state_change",
        "event_state": new_state,
        "previous_state": previous_state,
        "intent_id": intent_id,
        "nest_id": nest_id,
        "timestamp": _utc_now(),
        "source": "sla-agent-layer",
        "authority": "sla-agent-runtime-assurance",
        "recommendation": recommendation,
        "violations": list(violations),
        "drift_detected": drift_detected,
        "blockchain_scope": "none",
        "note": "Observational runtime governance event; no on-chain registration.",
    }
