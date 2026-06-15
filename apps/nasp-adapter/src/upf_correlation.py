"""
E2E-O3C — User plane correlation and freshness engine.

Follows UPF_CONTRACT_SSOT_V1. Does not modify O2C AMF/SMF adapter logic.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from upf_binding_adapter import (
    BINDING_PHASE_UPF_OBSERVED,
    UPF_BINDING_ANNOTATION_KEY,
    apply_upf_to_binding,
    load_upf_binding_config,
    observe_upf_binding,
    parse_upf_binding_annotation,
    upf_binding_annotation_value,
    upf_binding_enabled,
)

logger = logging.getLogger(__name__)

BINDING_PHASE_USER_PLANE_CORRELATED = "USER_PLANE_CORRELATED"

FRESHNESS_FRESH = "FRESH"
FRESHNESS_STALE = "STALE"


def _pick_ue_ip(
    *,
    upf_obs: Optional[Dict[str, Any]],
    smf_binding: Optional[Dict[str, Any]],
    amf_binding: Optional[Dict[str, Any]],
    prior_ue_ip: Optional[str],
    cfg: Dict[str, Any],
) -> tuple[Optional[str], str]:
    priority = (cfg.get("freshness") or {}).get("ue_ip_source_priority") or ["upf", "smf", "amf"]
    sources: Dict[str, Optional[str]] = {
        "upf": (upf_obs or {}).get("ue_ip_observed"),
        "smf": (smf_binding or {}).get("ue_ip"),
        "amf": None,
    }
    for key in priority:
        val = sources.get(key)
        if val:
            return val, key
    if prior_ue_ip:
        return prior_ue_ip, "nsi"
    return None, "none"


def resolve_session_state(
    *,
    upf_obs: Optional[Dict[str, Any]],
    smf_binding: Optional[Dict[str, Any]],
) -> str:
    if upf_obs:
        if upf_obs.get("pfcp_session_deleted") and not upf_obs.get("pfcp_session_established"):
            return "RELEASED"
        if upf_obs.get("session_state"):
            return str(upf_obs["session_state"])
    if smf_binding and smf_binding.get("session_state"):
        return str(smf_binding["session_state"])
    return "ACTIVE"


def build_enriched_pdu_summary(
    *,
    prior_summary: Optional[Dict[str, Any]],
    upf_binding: Optional[Dict[str, Any]],
    smf_binding: Optional[Dict[str, Any]],
    amf_binding: Optional[Dict[str, Any]],
    nssf_selection: Optional[Dict[str, Any]],
    correlation_status: str,
    fresh_ue_ip: Optional[str],
    freshness_source: str,
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = cfg or load_upf_binding_config()
    lab = cfg.get("lab") or {}
    base = dict(prior_summary or {})

    upf_node = (upf_binding or {}).get("upf_node_name") or (smf_binding or {}).get("selected_upf") or "UPF"
    n4 = (upf_binding or {}).get("upf_n4_addr") or (smf_binding or {}).get("upf_n4_addr")
    gtpu = (upf_binding or {}).get("upf_gtpu_addr")
    n6 = (upf_binding or {}).get("upf_n6_addr")
    session_id = (
        (upf_binding or {}).get("session_id")
        or (smf_binding or {}).get("session_id")
        or base.get("session_id")
        or ""
    )
    now = datetime.now(timezone.utc).isoformat()
    session_state = resolve_session_state(
        upf_obs=upf_binding,
        smf_binding=smf_binding,
    )

    summary = {
        "contract_version": base.get("contract_version", "1.0"),
        "observation_timestamp": now,
        "session_id": str(session_id),
        "ue_ip": fresh_ue_ip or base.get("ue_ip"),
        "fresh_ue_ip": fresh_ue_ip,
        "dnn": (upf_binding or {}).get("dnn") or (smf_binding or {}).get("dnn") or base.get("dnn") or lab.get("dnn"),
        "upf": _sanitize_upf_name(upf_node),
        "upf_n4_addr": n4 or base.get("upf_n4_addr"),
        "upf_gtpu_addr": gtpu or base.get("upf_gtpu_addr"),
        "upf_n6_addr": n6 or base.get("upf_n6_addr"),
        "supi": (upf_binding or {}).get("supi") or (smf_binding or {}).get("supi") or base.get("supi"),
        "orchestration_nsi_id": (nssf_selection or {}).get("nsiId") or base.get("orchestration_nsi_id"),
        "user_plane_nsi_id": lab.get("user_plane_nsi_id", "22"),
        "correlation_status": correlation_status,
        "session_state": session_state,
        "pfcp_observed": bool((upf_binding or {}).get("pfcp_session_established")),
        "traffic_anchor": f"{_sanitize_upf_name(upf_node)}@{n4}" if n4 else None,
        "freshness_source": freshness_source,
        "freshness_timestamp": now,
    }
    return {k: v for k, v in summary.items() if v is not None}


def _sanitize_upf_name(name: Optional[str]) -> str:
    if not name:
        return "UPF"
    cleaned = str(name).split("\n")[0].strip()
    cleaned = cleaned.split("\x1b")[0].strip()
    return cleaned or "UPF"


def _resolve_binding_phase(
    *,
    binding: Dict[str, Any],
    upf_success: bool,
    o2c_correlated: bool,
) -> str:
    if not upf_success:
        return str(binding.get("binding_phase", "METADATA_ONLY"))

    flags = binding.get("integration_flags") or {}
    amf_ok = bool(flags.get("amf_integrated"))
    smf_ok = bool(flags.get("smf_integrated"))

    if upf_success and amf_ok and smf_ok and o2c_correlated:
        return BINDING_PHASE_USER_PLANE_CORRELATED
    if upf_success:
        return BINDING_PHASE_UPF_OBSERVED
    return str(binding.get("binding_phase", "METADATA_ONLY"))


def run_upf_user_plane_binding(
    slice_service_binding: Dict[str, Any],
    *,
    nssf_selection: Optional[Dict[str, Any]] = None,
    amf_binding: Optional[Dict[str, Any]] = None,
    smf_binding: Optional[Dict[str, Any]] = None,
    pdu_session_summary: Optional[Dict[str, Any]] = None,
    upf_log_text: Optional[str] = None,
) -> Dict[str, Any]:
    """O3C orchestration: UPF observe + freshness + enriched summary (non-blocking)."""
    if not upf_binding_enabled():
        return {
            "skipped": True,
            "binding": dict(slice_service_binding),
            "upf_binding_annotation": None,
            "pdu_session_summary_annotation": None,
        }

    binding = dict(slice_service_binding)
    cfg = load_upf_binding_config()
    correlation_status = str(
        binding.get("correlation_status")
        or (pdu_session_summary or {}).get("correlation_status")
        or (smf_binding or {}).get("correlation_status")
        or "UNKNOWN"
    )

    session_id = None
    if smf_binding:
        session_id = str(smf_binding.get("session_id") or smf_binding.get("pdu_session_id") or "") or None

    upf_result = observe_upf_binding(
        binding,
        log_text=upf_log_text,
        correlation_status=correlation_status,
        session_id=session_id,
    )

    if upf_result.get("skipped"):
        return {
            "skipped": True,
            "binding": binding,
            "upf_binding_annotation": None,
            "pdu_session_summary_annotation": None,
        }

    upf_obs = upf_result.get("observation")
    prior_phase = binding.get("binding_phase")
    if upf_result.get("success") and upf_obs:
        binding = apply_upf_to_binding(binding, upf_result)

    prior_ue = (pdu_session_summary or {}).get("ue_ip") or (pdu_session_summary or {}).get("fresh_ue_ip")
    fresh_ue_ip, freshness_source = _pick_ue_ip(
        upf_obs=upf_obs if isinstance(upf_obs, dict) else None,
        smf_binding=smf_binding,
        amf_binding=amf_binding,
        prior_ue_ip=prior_ue,
        cfg=cfg,
    )

    o2c_correlated = prior_phase in ("PDU_CORRELATED", BINDING_PHASE_USER_PLANE_CORRELATED)
    if not o2c_correlated and smf_binding and amf_binding:
        o2c_correlated = correlation_status in ("DIRECT", "CONTEXT_SPLIT")

    binding["binding_phase"] = _resolve_binding_phase(
        binding=binding,
        upf_success=bool(upf_result.get("success")),
        o2c_correlated=o2c_correlated,
    )
    binding["correlation_status"] = correlation_status

    if upf_result.get("upf_binding") and isinstance(upf_result["upf_binding"], dict):
        upf_ann = dict(upf_result["upf_binding"])
        upf_ann["correlation_status"] = correlation_status
        upf_ann["freshness_source"] = freshness_source
        upf_ann["freshness_status"] = FRESHNESS_FRESH if fresh_ue_ip else FRESHNESS_STALE
        upf_ann["freshness_timestamp"] = datetime.now(timezone.utc).isoformat()
        if fresh_ue_ip:
            upf_ann["ue_ip_observed"] = fresh_ue_ip
        upf_result["upf_binding"] = upf_ann
        upf_result["upf_binding_annotation"] = upf_binding_annotation_value(upf_ann)

    summary = build_enriched_pdu_summary(
        prior_summary=pdu_session_summary,
        upf_binding=upf_result.get("upf_binding"),
        smf_binding=smf_binding,
        amf_binding=amf_binding,
        nssf_selection=nssf_selection,
        correlation_status=correlation_status,
        fresh_ue_ip=fresh_ue_ip,
        freshness_source=freshness_source,
        cfg=cfg,
    )
    binding["pdu_session_summary"] = summary

    return {
        "skipped": False,
        "binding": binding,
        "correlation_status": correlation_status,
        "fresh_ue_ip": fresh_ue_ip,
        "freshness_source": freshness_source,
        "upf_binding_annotation": upf_result.get("upf_binding_annotation"),
        "pdu_session_summary_annotation": json.dumps(summary, separators=(",", ":"), sort_keys=True),
        "upf_result": upf_result,
    }


def pdu_session_summary_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)
