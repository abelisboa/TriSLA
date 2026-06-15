"""
E2E-O5C — Transport correlation and freshness engine.

Follows TRANSPORT_CONTRACT_SSOT_V1. Does not modify O1C–O4C adapter logic.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from transport_binding_adapter import (
    BINDING_PHASE_TRANSPORT_OBSERVED,
    TRANSPORT_BINDING_ANNOTATION_KEY,
    apply_transport_to_binding,
    build_transport_binding_annotation,
    load_transport_binding_config,
    observe_transport_binding,
    transport_binding_annotation_value,
    transport_binding_enabled,
)

logger = logging.getLogger(__name__)

BINDING_PHASE_ACCESS_CORRELATED = "ACCESS_CORRELATED"
BINDING_PHASE_TRANSPORT_CORRELATED = "TRANSPORT_CORRELATED"


def _prior_chain_ok(binding: Dict[str, Any]) -> bool:
    phase = str(binding.get("binding_phase", ""))
    ok_phases = {
        BINDING_PHASE_ACCESS_CORRELATED,
        BINDING_PHASE_TRANSPORT_OBSERVED,
        BINDING_PHASE_TRANSPORT_CORRELATED,
        "RAN_OBSERVED",
        "USER_PLANE_CORRELATED",
    }
    if phase in ok_phases:
        return True
    flags = binding.get("integration_flags") or {}
    return bool(
        flags.get("ran_integrated")
        and flags.get("upf_integrated")
        and flags.get("amf_integrated")
        and flags.get("smf_integrated")
    )


def _join_keys_consistent(
    *,
    pdu_summary: Optional[Dict[str, Any]],
    ran_binding: Optional[Dict[str, Any]],
    amf_binding: Optional[Dict[str, Any]],
    smf_binding: Optional[Dict[str, Any]],
) -> bool:
    supi = (pdu_summary or {}).get("supi") or (ran_binding or {}).get("supi") or (amf_binding or {}).get("supi")
    if not supi:
        return True
    for src in (ran_binding, amf_binding, smf_binding):
        if not src:
            continue
        other = src.get("supi") or src.get("supi_observed")
        if other and other != supi:
            return False
    session_id = str((pdu_summary or {}).get("session_id") or (ran_binding or {}).get("session_id") or "")
    smf_sid = str((smf_binding or {}).get("session_id") or (smf_binding or {}).get("pdu_session_id") or "")
    if session_id and smf_sid and session_id != smf_sid:
        return False
    return True


def enrich_pdu_summary_with_transport(
    *,
    prior_summary: Optional[Dict[str, Any]],
    transport_binding: Optional[Dict[str, Any]],
    correlation_status: str,
    freshness_source: str = "onos_rest",
) -> Dict[str, Any]:
    summary = dict(prior_summary or {})
    now = datetime.now(timezone.utc).isoformat()
    tb = transport_binding or {}

    summary.update(
        {
            "transport_ref": tb.get("transport_ref") or summary.get("transport_ref"),
            "transport_binding_status": tb.get("transport_binding_status") or tb.get("binding_status"),
            "controller_health": tb.get("controller_health") or summary.get("controller_health"),
            "topology_state": tb.get("topology_state") or tb.get("topology_health") or summary.get("topology_state"),
            "topology_health": tb.get("topology_health") or summary.get("topology_health"),
            "intent_state": tb.get("intent_state") or tb.get("dominant_intent_state") or summary.get("intent_state"),
            "flow_count": tb.get("flow_count", summary.get("flow_count")),
            "device_count": tb.get("device_count", summary.get("device_count")),
            "controller_reachable": tb.get("controller_reachable", summary.get("controller_reachable")),
            "freshness_timestamp": now,
            "freshness_source": freshness_source,
            "correlation_status": correlation_status,
            "transport_correlated": bool(tb.get("transport_correlated")),
        }
    )
    return {k: v for k, v in summary.items() if v is not None}


def _resolve_binding_phase(
    *,
    binding: Dict[str, Any],
    transport_success: bool,
    transport_correlated: bool,
) -> str:
    if not transport_success:
        return str(binding.get("binding_phase", "METADATA_ONLY"))
    if transport_correlated:
        return BINDING_PHASE_TRANSPORT_CORRELATED
    return BINDING_PHASE_TRANSPORT_OBSERVED


def run_transport_binding(
    slice_service_binding: Dict[str, Any],
    *,
    nssf_selection: Optional[Dict[str, Any]] = None,
    amf_binding: Optional[Dict[str, Any]] = None,
    smf_binding: Optional[Dict[str, Any]] = None,
    upf_binding: Optional[Dict[str, Any]] = None,
    ran_binding: Optional[Dict[str, Any]] = None,
    pdu_session_summary: Optional[Dict[str, Any]] = None,
    snapshot_inject: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """O5C orchestration: ONOS observe + transport correlation (non-blocking)."""
    if not transport_binding_enabled():
        return {
            "skipped": True,
            "binding": dict(slice_service_binding),
            "transport_binding_annotation": None,
            "pdu_session_summary_annotation": None,
        }

    binding = dict(slice_service_binding)
    cfg = load_transport_binding_config()
    correlation_status = str(
        binding.get("correlation_status")
        or (pdu_session_summary or {}).get("correlation_status")
        or (ran_binding or {}).get("correlation_status")
        or (smf_binding or {}).get("correlation_status")
        or (upf_binding or {}).get("correlation_status")
        or "UNKNOWN"
    )

    transport_result = observe_transport_binding(
        binding,
        snapshot_inject=snapshot_inject,
        correlation_status=correlation_status,
    )

    if transport_result.get("skipped"):
        return {
            "skipped": True,
            "binding": binding,
            "transport_binding_annotation": None,
            "pdu_session_summary_annotation": None,
        }

    prior_phase = binding.get("binding_phase", "")
    prior_flags = dict(binding.get("integration_flags") or {})

    chain_ok = _prior_chain_ok(
        {"binding_phase": prior_phase, "integration_flags": prior_flags}
    ) or prior_phase in (
        BINDING_PHASE_ACCESS_CORRELATED,
        "RAN_OBSERVED",
        "USER_PLANE_CORRELATED",
    )
    keys_ok = _join_keys_consistent(
        pdu_summary=pdu_session_summary,
        ran_binding=ran_binding,
        amf_binding=amf_binding,
        smf_binding=smf_binding,
    )

    if transport_result.get("success"):
        binding = apply_transport_to_binding(binding, transport_result)

    controller_ok = bool((transport_result.get("transport_binding") or {}).get("controller_reachable"))

    transport_correlated = bool(
        transport_result.get("success")
        and chain_ok
        and keys_ok
        and controller_ok
    )

    binding["binding_phase"] = _resolve_binding_phase(
        binding=binding,
        transport_success=bool(transport_result.get("success")),
        transport_correlated=transport_correlated,
    )
    binding["correlation_status"] = correlation_status

    if transport_result.get("transport_binding") and isinstance(transport_result["transport_binding"], dict):
        tb_ann = dict(transport_result["transport_binding"])
        tb_ann["correlation_status"] = correlation_status
        tb_ann["transport_correlated"] = transport_correlated
        if transport_correlated:
            tb_ann["multidomain_correlated"] = True
        transport_result["transport_binding"] = tb_ann
        transport_result["transport_binding_annotation"] = transport_binding_annotation_value(tb_ann)

    summary = enrich_pdu_summary_with_transport(
        prior_summary=pdu_session_summary,
        transport_binding=transport_result.get("transport_binding"),
        correlation_status=correlation_status,
        freshness_source="onos_rest",
    )
    binding["pdu_session_summary"] = summary

    return {
        "skipped": False,
        "binding": binding,
        "correlation_status": correlation_status,
        "transport_correlated": transport_correlated,
        "transport_binding_annotation": transport_result.get("transport_binding_annotation"),
        "pdu_session_summary_annotation": json.dumps(summary, separators=(",", ":"), sort_keys=True),
        "transport_result": transport_result,
    }


def pdu_session_summary_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)
