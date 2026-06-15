"""
E2E-O2C — AMF/SMF correlation engine (CONTEXT_A vs CONTEXT_B).

Follows AMF_SMF_CONTRACT_SSOT_V1. Never merges nsiId 11/12/13 with 22.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from amf_binding_adapter import (
    AMF_BINDING_ANNOTATION_KEY,
    BINDING_PHASE_AMF_OBSERVED,
    amf_binding_enabled,
    apply_amf_to_binding,
    observe_amf_binding,
    parse_amf_binding_annotation,
)
from smf_binding_adapter import (
    BINDING_PHASE_SMF_OBSERVED,
    SMF_BINDING_ANNOTATION_KEY,
    SMF_BINDING_ANNOTATION_KEY,
    apply_smf_to_binding,
    observe_smf_binding,
    parse_smf_binding_annotation,
    smf_binding_enabled,
)
from amf_binding_adapter import load_binding_config

logger = logging.getLogger(__name__)

PDU_SESSION_SUMMARY_ANNOTATION_KEY = "trisla.io/pdu-session-summary"
BINDING_PHASE_PDU_CORRELATED = "PDU_CORRELATED"

CORRELATION_DIRECT = "DIRECT"
CORRELATION_CONTEXT_SPLIT = "CONTEXT_SPLIT"
CORRELATION_UNKNOWN = "UNKNOWN"


def compute_correlation_status(
    *,
    slice_service_binding: Dict[str, Any],
    nssf_selection: Optional[Dict[str, Any]],
    amf_obs: Optional[Dict[str, Any]],
    smf_obs: Optional[Dict[str, Any]],
    cfg: Optional[Dict[str, Any]] = None,
) -> str:
    cfg = cfg or load_binding_config()
    if not amf_obs or not smf_obs:
        return CORRELATION_UNKNOWN

    orch_nsi_id = str((nssf_selection or {}).get("nsiId") or "")
    orch_ids = set(str(x) for x in (cfg.get("correlation") or {}).get("orchestration_nsi_ids", ["11", "12", "13"]))
    user_plane_id = str((cfg.get("lab") or {}).get("user_plane_nsi_id", "22"))

    dnn_expected = slice_service_binding.get("smf_dnn_resolved") or "internet"
    dnn_amf = amf_obs.get("dnn_observed") or amf_obs.get("dnn")
    dnn_smf = smf_obs.get("dnn") or smf_obs.get("dnn_observed")

    sst_ssb = int(slice_service_binding.get("sst") or 1)
    snssai_amf = amf_obs.get("serving_snssai") or {}
    sst_amf = int(snssai_amf.get("sst") or 0)

    supi_amf = amf_obs.get("supi_observed") or amf_obs.get("supi")
    supi_smf = smf_obs.get("supi")
    pdu_amf = amf_obs.get("pdu_session_id")
    pdu_smf = smf_obs.get("pdu_session_id")
    if pdu_smf is None and smf_obs.get("session_id"):
        try:
            pdu_smf = int(smf_obs["session_id"])
        except (TypeError, ValueError):
            pdu_smf = None

    dnn_ok = str(dnn_amf or dnn_smf or "") == str(dnn_expected)
    sst_ok = sst_amf == sst_ssb or sst_amf == 0
    supi_ok = not supi_amf or not supi_smf or supi_amf == supi_smf
    pdu_ok = pdu_amf is None or pdu_smf is None or pdu_amf == pdu_smf

    if not (dnn_ok and sst_ok and supi_ok and pdu_ok):
        return CORRELATION_UNKNOWN

    if orch_nsi_id and orch_nsi_id in orch_ids and orch_nsi_id != user_plane_id:
        sd_trisla = str(slice_service_binding.get("sd", ""))
        sd_observed = str(snssai_amf.get("sd", ""))
        if sd_trisla and sd_observed and sd_trisla.lstrip("0") != sd_observed.lstrip("0"):
            if sd_observed.lower() not in (sd_trisla.lower(), sd_trisla.lstrip("0")):
                return CORRELATION_CONTEXT_SPLIT

    if orch_nsi_id and orch_nsi_id in orch_ids and orch_nsi_id != user_plane_id:
        return CORRELATION_CONTEXT_SPLIT

    return CORRELATION_DIRECT


def build_pdu_session_summary(
    *,
    amf_binding: Optional[Dict[str, Any]],
    smf_binding: Optional[Dict[str, Any]],
    nssf_selection: Optional[Dict[str, Any]],
    correlation_status: str,
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = cfg or load_binding_config()
    lab = cfg.get("lab") or {}
    session_id = ""
    if smf_binding:
        session_id = str(smf_binding.get("session_id") or smf_binding.get("pdu_session_id") or "")
    if not session_id and amf_binding:
        session_id = str(amf_binding.get("pdu_session_id") or "")

    return {
        "contract_version": "1.0",
        "observation_timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "ue_ip": (smf_binding or {}).get("ue_ip"),
        "dnn": (smf_binding or {}).get("dnn") or (amf_binding or {}).get("dnn_observed") or lab.get("dnn"),
        "upf": (smf_binding or {}).get("selected_upf"),
        "upf_n4_addr": (smf_binding or {}).get("upf_n4_addr"),
        "supi": (smf_binding or {}).get("supi") or (amf_binding or {}).get("supi"),
        "orchestration_nsi_id": (nssf_selection or {}).get("nsiId"),
        "user_plane_nsi_id": lab.get("user_plane_nsi_id", "22"),
        "correlation_status": correlation_status,
    }


def pdu_session_summary_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def parse_pdu_session_summary_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def run_amf_smf_binding(
    slice_service_binding: Dict[str, Any],
    *,
    nssf_selection: Optional[Dict[str, Any]] = None,
    amf_log_text: Optional[str] = None,
    smf_log_text: Optional[str] = None,
) -> Dict[str, Any]:
    """Orchestrate AMF + SMF observation and correlation (non-blocking)."""
    if not amf_binding_enabled() and not smf_binding_enabled():
        return {
            "skipped": True,
            "binding": dict(slice_service_binding),
            "amf_binding_annotation": None,
            "smf_binding_annotation": None,
            "pdu_session_summary_annotation": None,
        }

    binding = dict(slice_service_binding)
    cfg = load_binding_config()

    amf_result: Dict[str, Any] = {"skipped": True, "success": False}
    smf_result: Dict[str, Any] = {"skipped": True, "success": False}

    if amf_binding_enabled():
        amf_result = observe_amf_binding(binding, log_text=amf_log_text, correlation_status=CORRELATION_UNKNOWN)
        if amf_result.get("success"):
            binding = apply_amf_to_binding(binding, amf_result)

    if smf_binding_enabled():
        smf_result = observe_smf_binding(binding, log_text=smf_log_text, correlation_status=CORRELATION_UNKNOWN)
        if smf_result.get("success"):
            binding = apply_smf_to_binding(binding, smf_result)

    amf_obs = amf_result.get("amf_binding") or amf_result.get("observation")
    smf_obs = smf_result.get("smf_binding") or smf_result.get("observation")

    correlation_status = compute_correlation_status(
        slice_service_binding=binding,
        nssf_selection=nssf_selection,
        amf_obs=amf_obs if isinstance(amf_obs, dict) else None,
        smf_obs=smf_obs if isinstance(smf_obs, dict) else None,
        cfg=cfg,
    )

    if amf_result.get("amf_binding"):
        amf_result["amf_binding"]["correlation_status"] = correlation_status
        amf_result["amf_binding_annotation"] = json.dumps(
            amf_result["amf_binding"], separators=(",", ":"), sort_keys=True
        )
    if smf_result.get("smf_binding"):
        smf_result["smf_binding"]["correlation_status"] = correlation_status
        smf_result["smf_binding_annotation"] = json.dumps(
            smf_result["smf_binding"], separators=(",", ":"), sort_keys=True
        )

    summary = build_pdu_session_summary(
        amf_binding=amf_result.get("amf_binding"),
        smf_binding=smf_result.get("smf_binding"),
        nssf_selection=nssf_selection,
        correlation_status=correlation_status,
        cfg=cfg,
    )
    binding["correlation_status"] = correlation_status

    if (
        amf_result.get("success")
        and smf_result.get("success")
        and correlation_status in (CORRELATION_DIRECT, CORRELATION_CONTEXT_SPLIT)
    ):
        binding["binding_phase"] = BINDING_PHASE_PDU_CORRELATED
        binding["pdu_session_summary"] = summary
    elif smf_result.get("success"):
        binding["binding_phase"] = BINDING_PHASE_SMF_OBSERVED
    elif amf_result.get("success"):
        binding["binding_phase"] = BINDING_PHASE_AMF_OBSERVED

    return {
        "skipped": False,
        "binding": binding,
        "correlation_status": correlation_status,
        "amf_binding_annotation": amf_result.get("amf_binding_annotation"),
        "smf_binding_annotation": smf_result.get("smf_binding_annotation"),
        "pdu_session_summary_annotation": pdu_session_summary_annotation_value(summary),
        "amf_result": amf_result,
        "smf_result": smf_result,
    }
