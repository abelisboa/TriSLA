"""
PROMPT_132 — decisão por score contínuo multiobjetivo (DECISION_SCORE_MODE).
Mais alto = mais favorável ao ACCEPT. Sem inventar métricas ausentes.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from models import DecisionAction, SLARequirement

DECISION_POLICY_VERSION = "v2_score_continuous"


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _uniq_reasons(codes: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _load_profiles() -> Dict[str, Any]:
    raw = os.getenv("DE_SLICE_WEIGHT_PROFILES", "").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def default_profile(slice_key: str) -> Dict[str, float]:
    sk = (slice_key or "eMBB").upper().replace("EMBB", "eMBB")
    accept_min = float(os.getenv("DECISION_SCORE_ACCEPT_MIN", "0.55"))
    reneg_min = float(os.getenv("DECISION_SCORE_RENEGOTIATE_MIN", "0.38"))
    if sk == "URLLC":
        return {
            "w_feas": 0.22,
            "w_prb": 0.22,
            "w_press": 0.18,
            "w_risk": 0.28,
            "w_sem": 0.12,
            "accept_min": accept_min,
            "reneg_min": reneg_min,
        }
    if sk == "MMTC":
        return {
            "w_feas": 0.18,
            "w_prb": 0.12,
            "w_press": 0.14,
            "w_risk": 0.22,
            "w_sem": 0.10,
            "accept_min": accept_min - 0.03,
            "reneg_min": reneg_min - 0.02,
        }
    return {
        "w_feas": 0.20,
        "w_prb": 0.18,
        "w_press": 0.16,
        "w_risk": 0.26,
        "w_sem": 0.12,
        "accept_min": accept_min,
        "reneg_min": reneg_min,
    }


def _get_profile(slice_key: str) -> Dict[str, float]:
    profiles = _load_profiles()
    sk = (slice_key or "eMBB").upper().replace("EMBB", "eMBB")
    if sk in profiles and isinstance(profiles[sk], dict):
        base = default_profile(sk)
        for k, v in profiles[sk].items():
            if isinstance(v, (int, float)):
                base[str(k)] = float(v)
        return base
    return default_profile(slice_key)


def _extract_feasibility(nest, context: Optional[dict]) -> Tuple[Optional[float], str]:
    if context and isinstance(context.get("feasibility_score"), (int, float)):
        try:
            return _clamp01(float(context["feasibility_score"])), "context"
        except (TypeError, ValueError):
            pass
    if nest is not None and hasattr(nest, "resources"):
        res = nest.resources or {}
        if isinstance(res, dict) and res:
            vals: List[float] = []
            for v in res.values():
                try:
                    fv = float(v)
                    if 0.0 <= fv <= 1.0:
                        vals.append(fv)
                except (TypeError, ValueError):
                    continue
            if vals:
                return _clamp01(sum(vals) / len(vals)), "nest_resources"
    return None, "missing"


def _extract_resource_pressure(intent, context: Optional[dict]) -> Tuple[Optional[float], str]:
    if context and context.get("resource_pressure") is not None:
        try:
            return _clamp01(float(context["resource_pressure"])), "context"
        except (TypeError, ValueError):
            pass
    tf = (context or {}).get("telemetry_features") if isinstance(context, dict) else None
    if isinstance(tf, dict) and tf.get("resource_pressure_band"):
        band = str(tf["resource_pressure_band"]).lower()
        mp = {"low": 0.25, "medium": 0.55, "high": 0.85}
        if band in mp:
            return mp[band], "telemetry_features_band"
    md = getattr(intent, "metadata", None) or {}
    if isinstance(md, dict) and md.get("resource_pressure") is not None:
        try:
            return _clamp01(float(md["resource_pressure"])), "intent_metadata"
        except (TypeError, ValueError):
            pass
    return None, "missing"


def _extract_semantic(intent) -> Tuple[Optional[float], str]:
    md = getattr(intent, "metadata", None) or {}
    if not isinstance(md, dict):
        return None, "missing"
    for key in ("semantic_priority", "semantic_criticality", "criticality"):
        if md.get(key) is not None:
            try:
                return _clamp01(float(md[key])), key
            except (TypeError, ValueError):
                pass
    return None, "missing"


def _action_to_label(a: DecisionAction) -> str:
    return {"AC": "ACCEPT", "RENEG": "RENEGOTIATE", "REJ": "REJECT"}[a.value]


def score_mode_decide(
    *,
    intent,
    nest,
    ml_prediction,
    context: Optional[dict],
    slos: List[SLARequirement],
    domains: List[str],
    raw_risk_score: float,
    slice_adjusted: float,
    final_risk: float,
    ran_prb_raw: Optional[Any],
    slice_label: str,
    transport_latency_input: Optional[Any],
    core_cpu_input: Optional[Any],
    core_memory_input: Optional[Any],
    prb_risk_alpha: float,
    top_factors: Optional[list],
    dom: str,
    cls_str: Optional[str],
    cls_conf: float,
    hard_prb_reject: float,
    hard_prb_reneg: float,
) -> Tuple[DecisionAction, str, List[SLARequirement], List[str], dict]:
    profile = _get_profile(slice_label)
    slice_profile_used = {
        "slice": slice_label,
        "weights": {k: profile[k] for k in ("w_feas", "w_prb", "w_press", "w_risk", "w_sem") if k in profile},
        "accept_min": profile.get("accept_min"),
        "reneg_min": profile.get("reneg_min"),
    }
    reason_codes: List[str] = []
    normalized_inputs: Dict[str, Any] = {"slice_profile": slice_profile_used}

    decision_source = "decision_score_mode"

    if ran_prb_raw is not None:
        try:
            pv_raw = float(ran_prb_raw)
            pv_norm = _clamp01(pv_raw / 100.0) if pv_raw > 1.0 else _clamp01(pv_raw)
            reneg_th = _clamp01(hard_prb_reneg / 100.0) if hard_prb_reneg > 1.0 else _clamp01(hard_prb_reneg)
            reject_th = _clamp01(hard_prb_reject / 100.0) if hard_prb_reject > 1.0 else _clamp01(hard_prb_reject)
            print("DEBUG_PRB_RAW:", pv_raw)
            print("DEBUG_PRB_NORMALIZED:", pv_norm)
            print("DEBUG_THRESHOLDS:", reneg_th, reject_th)
            if pv_norm >= reject_th:
                decision = DecisionAction.REJECT
                xai = _build_xai(
                    decision=decision,
                    decision_score=0.0,
                    decision_band="REJECT",
                    terms=[],
                    normalized_inputs=normalized_inputs,
                    reason_codes=_uniq_reasons(["policy_hard_reject"] + reason_codes),
                    raw_risk_score=raw_risk_score,
                    slice_adjusted=slice_adjusted,
                    final_risk=final_risk,
                    ran_prb_raw=ran_prb_raw,
                    transport_latency_input=transport_latency_input,
                    core_cpu_input=core_cpu_input,
                    core_memory_input=core_memory_input,
                    prb_risk_alpha=prb_risk_alpha,
                    top_factors=top_factors or [],
                    dom=dom,
                    cls_str=cls_str,
                    cls_conf=cls_conf,
                    decision_source="policy_hard_reject",
                    policy_governed=True,
                    thresholds_used={},
                    slice_label=slice_label,
                    hard_prb_thresholds={"reject": reject_th, "renegotiate": reneg_th},
                )
                reasoning = (
                    f"REJECT por política de PRB elevado (prb_norm={pv_norm:.3f} ≥ {reject_th:.3f}). "
                    f"Domínios: {', '.join(domains)}."
                )
                return decision, reasoning, slos, domains, xai
            if pv_norm >= reneg_th:
                decision = DecisionAction.RENEGOTIATE
                xai = _build_xai(
                    decision=decision,
                    decision_score=0.0,
                    decision_band="RENEGOTIATE",
                    terms=[],
                    normalized_inputs=normalized_inputs,
                    reason_codes=_uniq_reasons(["policy_hard_renegotiate"] + reason_codes),
                    raw_risk_score=raw_risk_score,
                    slice_adjusted=slice_adjusted,
                    final_risk=final_risk,
                    ran_prb_raw=ran_prb_raw,
                    transport_latency_input=transport_latency_input,
                    core_cpu_input=core_cpu_input,
                    core_memory_input=core_memory_input,
                    prb_risk_alpha=prb_risk_alpha,
                    top_factors=top_factors or [],
                    dom=dom,
                    cls_str=cls_str,
                    cls_conf=cls_conf,
                    decision_source="policy_hard_renegotiate",
                    policy_governed=True,
                    thresholds_used={},
                    slice_label=slice_label,
                    hard_prb_thresholds={"reject": reject_th, "renegotiate": reneg_th},
                )
                reasoning = (
                    f"RENEGOTIATE por política de PRB (prb_norm={pv_norm:.3f} ≥ {reneg_th:.3f}). "
                    f"Domínios: {', '.join(domains)}."
                )
                return decision, reasoning, slos, domains, xai
        except (TypeError, ValueError):
            pass

    g_prb: Optional[float] = None
    if ran_prb_raw is not None:
        try:
            pn = max(0.0, min(float(ran_prb_raw) / 100.0, 1.0))
            g_prb = 1.0 - pn
            normalized_inputs["prb_goodness"] = {
                "value": g_prb,
                "raw_prb": float(ran_prb_raw),
                "status": "present",
            }
        except (TypeError, ValueError):
            normalized_inputs["prb_goodness"] = {"value": None, "status": "missing"}
            reason_codes.append("INPUT_DEGRADED")
    else:
        normalized_inputs["prb_goodness"] = {"value": None, "status": "missing"}
        reason_codes.append("INPUT_DEGRADED")

    g_risk = _clamp01(1.0 - float(final_risk))
    normalized_inputs["risk_goodness"] = {
        "value": g_risk,
        "ran_aware_final_risk": final_risk,
        "status": "present",
    }

    feas, feas_src = _extract_feasibility(nest, context)
    normalized_inputs["feasibility"] = {"value": feas, "source": feas_src}
    if feas is None:
        reason_codes.append("INPUT_DEGRADED")

    press, press_src = _extract_resource_pressure(intent, context)
    g_press = (1.0 - press) if press is not None else None
    normalized_inputs["resource_pressure"] = {
        "value": press,
        "source": press_src,
        "pressure_inverse_goodness": g_press,
    }
    if press is None:
        reason_codes.append("INPUT_DEGRADED")

    sem, sem_src = _extract_semantic(intent)
    normalized_inputs["semantic"] = {"value": sem, "source": sem_src}
    if sem is None:
        g_sem = 0.55
        reason_codes.append("INPUT_DEGRADED")
    else:
        g_sem = sem

    w_feas = float(profile["w_feas"])
    w_prb = float(profile["w_prb"])
    w_press = float(profile["w_press"])
    w_risk = float(profile["w_risk"])
    w_sem = float(profile["w_sem"])

    terms: List[Dict[str, Any]] = []
    num = 0.0
    den = 0.0
    if feas is not None:
        c = w_feas * feas
        terms.append({"factor": "feasibility", "weight": w_feas, "input": feas, "contribution": c, "direction": "up"})
        num += c
        den += w_feas
    if g_prb is not None:
        c = w_prb * g_prb
        terms.append({"factor": "ran_prb_goodness", "weight": w_prb, "input": g_prb, "contribution": c, "direction": "up"})
        num += c
        den += w_prb
    if g_press is not None:
        c = w_press * g_press
        terms.append(
            {
                "factor": "resource_headroom",
                "weight": w_press,
                "input": g_press,
                "contribution": c,
                "direction": "up",
            }
        )
        num += c
        den += w_press
    c_risk = w_risk * g_risk
    terms.append({"factor": "risk_inverse", "weight": w_risk, "input": g_risk, "contribution": c_risk, "direction": "up"})
    num += c_risk
    den += w_risk
    c_sem = w_sem * g_sem
    terms.append({"factor": "semantic_priority", "weight": w_sem, "input": g_sem, "contribution": c_sem, "direction": "up"})
    num += c_sem
    den += w_sem

    if den <= 0:
        decision_score = 0.0
        decision = DecisionAction.REJECT
        decision_band = "REJECT"
        decision_source = "decision_score_degenerate"
    else:
        decision_score = _clamp01(num / den)
        accept_min = float(profile["accept_min"])
        reneg_min = float(profile["reneg_min"])
        strict = os.getenv("TELEMETRY_PRE_DECISION_STRICT", "false").lower() == "true"
        if strict and (ran_prb_raw is None):
            decision = DecisionAction.RENEGOTIATE
            decision_band = "RENEGOTIATE"
            decision_source = "telemetry_strict_missing_prb"
            reason_codes.append("TELEMETRY_STRICT_POLICY")
        elif strict and (feas is None and press is None):
            decision = DecisionAction.RENEGOTIATE
            decision_band = "RENEGOTIATE"
            decision_source = "telemetry_strict_missing_pressure_feasibility"
            reason_codes.append("TELEMETRY_STRICT_POLICY")
        elif decision_score >= accept_min:
            decision = DecisionAction.ACCEPT
            decision_band = "ACCEPT"
        elif decision_score >= reneg_min:
            decision = DecisionAction.RENEGOTIATE
            decision_band = "RENEGOTIATE"
        else:
            decision = DecisionAction.REJECT
            decision_band = "REJECT"

    reason_codes = _uniq_reasons(reason_codes)
    if decision_band == "ACCEPT" and cls_str and cls_conf >= float(
        os.getenv("ML_REFINEMENT_CONFIDENCE", "0.6")
    ):
        cls_u = str(cls_str).strip().upper()
        if cls_u == "REJECT" and os.getenv("ML_CAN_OVERRIDE_REJECT", "false").lower() != "true":
            decision = DecisionAction.RENEGOTIATE
            decision_band = "RENEGOTIATE"
            decision_source = "ml_refinement_safe_override_score"
            reason_codes.append("ML_REFINEMENT_SAFE")

    pos = ", ".join(t["factor"] for t in terms if t.get("contribution", 0) > 0 and t.get("direction") == "up")
    reasoning = (
        f"decision_score={decision_score:.3f} band={decision_band} profile={slice_label} "
        f"(fonte={decision_source}). Fatores principais: {pos or 'n/d'}. "
        f"Domínios: {', '.join(domains)}."
    )

    xai = _build_xai(
        decision=decision,
        decision_score=decision_score,
        decision_band=decision_band,
        terms=terms,
        normalized_inputs=normalized_inputs,
        reason_codes=reason_codes,
        raw_risk_score=raw_risk_score,
        slice_adjusted=slice_adjusted,
        final_risk=final_risk,
        ran_prb_raw=ran_prb_raw,
        transport_latency_input=transport_latency_input,
        core_cpu_input=core_cpu_input,
        core_memory_input=core_memory_input,
        prb_risk_alpha=prb_risk_alpha,
        top_factors=top_factors or [],
        dom=dom,
        cls_str=cls_str,
        cls_conf=cls_conf,
        decision_source=decision_source,
        policy_governed=False,
        thresholds_used={"accept_min": profile.get("accept_min"), "reneg_min": profile.get("reneg_min")},
        slice_label=slice_label,
        hard_prb_thresholds={"reject": hard_prb_reject, "renegotiate": hard_prb_reneg},
    )
    return decision, reasoning, slos, domains, xai


def _build_xai(
    *,
    decision: DecisionAction,
    decision_score: float,
    decision_band: str,
    terms: List[dict],
    normalized_inputs: dict,
    reason_codes: List[str],
    raw_risk_score: float,
    slice_adjusted: float,
    final_risk: float,
    ran_prb_raw: Optional[Any],
    transport_latency_input: Optional[Any],
    core_cpu_input: Optional[Any],
    core_memory_input: Optional[Any],
    prb_risk_alpha: float,
    top_factors: list,
    dom: str,
    cls_str: Optional[str],
    cls_conf: float,
    decision_source: str,
    policy_governed: bool,
    thresholds_used: dict,
    slice_label: str,
    hard_prb_thresholds: Optional[Dict[str, float]] = None,
) -> dict:
    final_label = _action_to_label(decision)
    hpt = hard_prb_thresholds or {}
    return {
        "raw_risk_score": raw_risk_score,
        "slice_adjusted_risk_score": slice_adjusted,
        "ran_prb_utilization_input": ran_prb_raw,
        "transport_latency_input": transport_latency_input,
        "transport_latency_ms_input": transport_latency_input,
        "core_cpu_input": core_cpu_input,
        "core_cpu_percent_input": core_cpu_input,
        "core_memory_input": core_memory_input,
        "ran_aware_final_risk": final_risk,
        "prb_risk_alpha": prb_risk_alpha,
        "predicted_decision_class": cls_str,
        "confidence_score": cls_conf,
        "threshold_decision": decision_band,
        "final_decision": final_label,
        "decision_divergence": False,
        "decision_mode": "decision_score",
        "thresholds_used": thresholds_used,
        "top_factors": top_factors,
        "dominant_domain": dom,
        "decision_explanation": f"score_mode score={decision_score:.4f} band={decision_band} source={decision_source}",
        "decision_explanation_plain": f"Score contínuo {decision_score:.2f} ({decision_band}) via {decision_source}.",
        "final_decision_confidence": float(cls_conf) if cls_conf else 0.0,
        "decision_source": decision_source,
        "policy_governed": policy_governed,
        "decision_score": decision_score,
        "decision_band": decision_band,
        "contributing_factors": terms,
        "reason_codes": reason_codes,
        "normalized_inputs": normalized_inputs,
        "decision_policy_version": DECISION_POLICY_VERSION,
        "slice_profile_used": slice_label,
        "hard_prb_thresholds": {
            "reject": hpt.get("reject"),
            "renegotiate": hpt.get("renegotiate"),
        },
    }
