"""
E2E-O4C — RAN access correlation and freshness engine.

Follows RAN_CONTRACT_SSOT_V1. Does not modify O1C/O2C/O3C adapter logic.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ran_binding_adapter import (
    BINDING_PHASE_RAN_OBSERVED,
    RAN_BINDING_ANNOTATION_KEY,
    apply_ran_to_binding,
    load_ran_binding_config,
    observe_ran_binding,
    parse_ran_binding_annotation,
    ran_binding_annotation_value,
    ran_binding_enabled,
)

logger = logging.getLogger(__name__)

BINDING_PHASE_ACCESS_CORRELATED = "ACCESS_CORRELATED"

FRESHNESS_FRESH = "FRESH"
FRESHNESS_STALE = "STALE"
FRESHNESS_MISSING = "MISSING"


def _join_keys_match(
    *,
    ran_obs: Optional[Dict[str, Any]],
    amf_binding: Optional[Dict[str, Any]],
    smf_binding: Optional[Dict[str, Any]],
    upf_binding: Optional[Dict[str, Any]],
    pdu_summary: Optional[Dict[str, Any]],
) -> bool:
    supi = (ran_obs or {}).get("supi") or (amf_binding or {}).get("supi")
    if not supi:
        return False
    amf_supi = (amf_binding or {}).get("supi") or (amf_binding or {}).get("supi_observed")
    if amf_supi and amf_supi != supi:
        return False
    smf_supi = (smf_binding or {}).get("supi")
    if smf_supi and smf_supi != supi:
        return False

    session_id = str((ran_obs or {}).get("session_id") or "")
    smf_sid = str((smf_binding or {}).get("session_id") or (smf_binding or {}).get("pdu_session_id") or "")
    pdu_sid = str((pdu_summary or {}).get("session_id") or "")
    if session_id and smf_sid and session_id != smf_sid:
        return False
    if session_id and pdu_sid and session_id != pdu_sid:
        return False

    dnn = (ran_obs or {}).get("dnn") or (smf_binding or {}).get("dnn") or (pdu_summary or {}).get("dnn")
    if not dnn:
        return True
    smf_dnn = (smf_binding or {}).get("dnn")
    if smf_dnn and smf_dnn != dnn:
        return False
    return True


def enrich_pdu_summary_with_ran(
    *,
    prior_summary: Optional[Dict[str, Any]],
    ran_binding: Optional[Dict[str, Any]],
    upf_binding: Optional[Dict[str, Any]],
    smf_binding: Optional[Dict[str, Any]],
    correlation_status: str,
    freshness_source: str,
) -> Dict[str, Any]:
    summary = dict(prior_summary or {})
    now = datetime.now(timezone.utc).isoformat()
    ran = ran_binding or {}

    summary.update(
        {
            "gnb_id": ran.get("gnb_id") or summary.get("gnb_id"),
            "ran_ue_ngap_id": ran.get("ran_ue_ngap_id") or summary.get("ran_ue_ngap_id"),
            "amf_ue_ngap_id": ran.get("amf_ue_ngap_id") or summary.get("amf_ue_ngap_id"),
            "serving_snssai": ran.get("serving_snssai") or summary.get("serving_snssai"),
            "registration_state_snapshot": ran.get("registration_state_snapshot")
            or summary.get("registration_state_snapshot"),
            "freshness_timestamp": now,
            "freshness_source": freshness_source,
            "correlation_status": correlation_status,
            "access_correlated": bool(ran.get("gnb_id") and ran.get("ran_ue_ngap_id")),
        }
    )
    if upf_binding:
        summary.setdefault("fresh_ue_ip", upf_binding.get("ue_ip_observed"))
        summary.setdefault("upf_gtpu_addr", upf_binding.get("upf_gtpu_addr"))
    if smf_binding:
        summary.setdefault("selected_upf", smf_binding.get("selected_upf"))
    return {k: v for k, v in summary.items() if v is not None}


def _resolve_binding_phase(
    *,
    binding: Dict[str, Any],
    ran_success: bool,
    access_correlated: bool,
) -> str:
    if not ran_success:
        return str(binding.get("binding_phase", "METADATA_ONLY"))
    if access_correlated:
        return BINDING_PHASE_ACCESS_CORRELATED
    return BINDING_PHASE_RAN_OBSERVED


def run_ran_access_binding(
    slice_service_binding: Dict[str, Any],
    *,
    nssf_selection: Optional[Dict[str, Any]] = None,
    amf_binding: Optional[Dict[str, Any]] = None,
    smf_binding: Optional[Dict[str, Any]] = None,
    upf_binding: Optional[Dict[str, Any]] = None,
    pdu_session_summary: Optional[Dict[str, Any]] = None,
    amf_log_text: Optional[str] = None,
    gnb_log_text: Optional[str] = None,
) -> Dict[str, Any]:
    """O4C orchestration: RAN observe + access correlation (non-blocking)."""
    if not ran_binding_enabled():
        return {
            "skipped": True,
            "binding": dict(slice_service_binding),
            "ran_binding_annotation": None,
            "pdu_session_summary_annotation": None,
        }

    binding = dict(slice_service_binding)
    cfg = load_ran_binding_config()
    correlation_status = str(
        binding.get("correlation_status")
        or (pdu_session_summary or {}).get("correlation_status")
        or (smf_binding or {}).get("correlation_status")
        or (upf_binding or {}).get("correlation_status")
        or "UNKNOWN"
    )

    target_supi = None
    if amf_binding:
        target_supi = amf_binding.get("supi") or amf_binding.get("supi_observed")
    if not target_supi and smf_binding:
        target_supi = smf_binding.get("supi")
    if not target_supi:
        target_supi = (cfg.get("lab") or {}).get("default_supi")

    ran_result = observe_ran_binding(
        binding,
        amf_log_text=amf_log_text,
        gnb_log_text=gnb_log_text,
        correlation_status=correlation_status,
        target_supi=target_supi,
    )

    if ran_result.get("skipped"):
        return {
            "skipped": True,
            "binding": binding,
            "ran_binding_annotation": None,
            "pdu_session_summary_annotation": None,
        }

    ran_obs = ran_result.get("observation")
    prior_phase = binding.get("binding_phase", "")

    if ran_result.get("success") and isinstance(ran_obs, dict):
        binding = apply_ran_to_binding(binding, ran_result)

    user_plane_ok = prior_phase in (
        "USER_PLANE_CORRELATED",
        BINDING_PHASE_ACCESS_CORRELATED,
        BINDING_PHASE_RAN_OBSERVED,
    )
    if not user_plane_ok and smf_binding and amf_binding and upf_binding:
        user_plane_ok = True

    keys_ok = _join_keys_match(
        ran_obs=ran_obs if isinstance(ran_obs, dict) else None,
        amf_binding=amf_binding,
        smf_binding=smf_binding,
        upf_binding=upf_binding,
        pdu_summary=pdu_session_summary,
    )
    access_correlated = bool(
        ran_result.get("success")
        and user_plane_ok
        and keys_ok
        and isinstance(ran_obs, dict)
        and ran_obs.get("gnb_id")
        and ran_obs.get("ran_ue_ngap_id") is not None
    )

    binding["binding_phase"] = _resolve_binding_phase(
        binding=binding,
        ran_success=bool(ran_result.get("success")),
        access_correlated=access_correlated,
    )
    binding["correlation_status"] = correlation_status

    freshness_source = "amf"
    if ran_result.get("ran_binding") and isinstance(ran_result["ran_binding"], dict):
        ran_ann = dict(ran_result["ran_binding"])
        ran_ann["correlation_status"] = correlation_status
        ran_ann["freshness_source"] = freshness_source
        if access_correlated:
            ran_ann["access_correlated"] = True
        ran_result["ran_binding"] = ran_ann
        ran_result["ran_binding_annotation"] = ran_binding_annotation_value(ran_ann)

    summary = enrich_pdu_summary_with_ran(
        prior_summary=pdu_session_summary,
        ran_binding=ran_result.get("ran_binding"),
        upf_binding=upf_binding,
        smf_binding=smf_binding,
        correlation_status=correlation_status,
        freshness_source=freshness_source,
    )
    binding["pdu_session_summary"] = summary

    return {
        "skipped": False,
        "binding": binding,
        "correlation_status": correlation_status,
        "access_correlated": access_correlated,
        "ran_binding_annotation": ran_result.get("ran_binding_annotation"),
        "pdu_session_summary_annotation": json.dumps(summary, separators=(",", ":"), sort_keys=True),
        "ran_result": ran_result,
    }


def pdu_session_summary_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)
