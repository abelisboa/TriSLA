"""
E2E-O2C — SMF Binding Adapter (read-only log observation).

Follows AMF_SMF_CONTRACT_SSOT_V1. Never blocks NSI instantiation.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

SMF_BINDING_ANNOTATION_KEY = "trisla.io/smf-binding"
ADAPTER_VERSION = "smf-binding-v1"
CONTRACT_VERSION = "1.0"
BINDING_STATUS_OBSERVED = "OBSERVED"
BINDING_STATUS_FAILED = "FAILED"
BINDING_PHASE_SMF_OBSERVED = "SMF_OBSERVED"

_RE_PDU_IP = re.compile(
    r"UE\[(imsi-\d+)\]\s+PDUSessionID\[(\d+)\]\s+IP\[([\d.]+)\]", re.I
)
_RE_SELECTED_UPF = re.compile(r"Selected UPF:\s*(\S+)", re.I)
_RE_SM_CONTEXT_POST = re.compile(
    r"POST\s+\|\s+/nsmf-pdusession/v1/sm-contexts(?:/([^|\s]+))?", re.I
)
_RE_CREATE_SM = re.compile(r"Receive Create SM Context Request", re.I)


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def smf_binding_enabled() -> bool:
    return _env_bool("SMF_BINDING_ENABLED", False)


def _config_path() -> Path:
    override = os.getenv("AMF_SMF_BINDING_CONFIG")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "config" / "amf_smf_binding_ssot.yaml"


@lru_cache(maxsize=1)
def load_binding_config() -> Dict[str, Any]:
    from amf_binding_adapter import load_binding_config as _load

    return _load()


def _core_namespace(cfg: Dict[str, Any]) -> str:
    smf_cfg = cfg.get("smf") or cfg.get("amf") or {}
    env_name = smf_cfg.get("core_namespace_env", "NASP_FREE5GC_NAMESPACE")
    return os.getenv(env_name, smf_cfg.get("core_namespace", "ns-1274485"))


def parse_smf_log_lines(log_text: str, *, cfg: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    if not log_text or not log_text.strip():
        return None

    cfg = cfg or load_binding_config()
    lab = cfg.get("lab") or {}
    supi: Optional[str] = None
    pdu_session_id: Optional[int] = None
    ue_ip: Optional[str] = None
    upf_node: Optional[str] = None
    sm_context_ref: Optional[str] = None
    create_seen = False

    for line in log_text.splitlines():
        if _RE_CREATE_SM.search(line):
            create_seen = True

        m = _RE_PDU_IP.search(line)
        if m:
            supi = m.group(1)
            pdu_session_id = int(m.group(2))
            ue_ip = m.group(3)

        m = _RE_SELECTED_UPF.search(line)
        if m:
            upf_node = m.group(1)

        m = _RE_SM_CONTEXT_POST.search(line)
        if m and m.group(1):
            sm_context_ref = m.group(1).strip()

    if not create_seen and pdu_session_id is None:
        return None

    snssai = lab.get("pdu_snssai") or {"sst": 1, "sd": "010203"}
    return {
        "supi": supi or lab.get("default_supi"),
        "pdu_session_id": pdu_session_id,
        "ue_ip": ue_ip,
        "upf_node": upf_node or "UPF",
        "upf_n4_addr": _default_upf_n4(cfg),
        "dnn": lab.get("dnn", "internet"),
        "snssai_observed": dict(snssai),
        "sm_context_ref": sm_context_ref,
        "session_state": "ACTIVE" if ue_ip else "PENDING",
    }


def _default_upf_n4(cfg: Dict[str, Any]) -> str:
    return os.getenv("NASP_UPF_N4_ADDR", "10.233.75.38")


def fetch_smf_logs(cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = cfg or load_binding_config()
    ns = _core_namespace(cfg)
    smf_cfg = cfg.get("smf") or {}
    label = smf_cfg.get("pod_label", "nf=smf")
    tail = int(smf_cfg.get("log_tail_lines", 3000))
    try:
        from kubernetes import client
        from kubernetes.config import load_incluster_config, load_kube_config

        try:
            load_incluster_config()
        except Exception:
            load_kube_config()

        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=ns, label_selector=label)
        if not pods.items:
            logger.warning("[SMF-BIND] no SMF pods in %s", ns)
            return ""
        pod_name = pods.items[0].metadata.name
        return v1.read_namespaced_pod_log(name=pod_name, namespace=ns, tail_lines=tail)
    except Exception as exc:
        logger.warning("[SMF-BIND] log fetch failed: %s", exc)
        return ""


def build_smf_binding_annotation(
    observation: Dict[str, Any],
    *,
    correlation_status: str = "UNKNOWN",
) -> Dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "binding_status": BINDING_STATUS_OBSERVED,
        "observation_timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": str(observation.get("pdu_session_id", "")),
        "dnn": observation.get("dnn", "internet"),
        "ue_ip": observation.get("ue_ip"),
        "selected_upf": observation.get("upf_node", "UPF"),
        "upf_n4_addr": observation.get("upf_n4_addr"),
        "supi": observation.get("supi"),
        "sm_context_ref": observation.get("sm_context_ref"),
        "snssai_observed": observation.get("snssai_observed"),
        "session_state": observation.get("session_state"),
        "correlation_status": correlation_status,
        "slice_context": "CONTEXT_B",
    }


def observe_smf_binding(
    slice_service_binding: Dict[str, Any],
    *,
    log_text: Optional[str] = None,
    correlation_status: str = "UNKNOWN",
) -> Dict[str, Any]:
    if not smf_binding_enabled():
        return {"skipped": True, "smf_binding_annotation": None}

    cfg = load_binding_config()
    text = log_text if log_text is not None else fetch_smf_logs(cfg)
    parsed = parse_smf_log_lines(text, cfg=cfg)

    if not parsed:
        ann = {
            "contract_version": CONTRACT_VERSION,
            "adapter_version": ADAPTER_VERSION,
            "binding_status": BINDING_STATUS_FAILED,
            "observation_timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "NO_SMF_OBSERVATION",
            "correlation_status": "UNKNOWN",
        }
        return {
            "skipped": False,
            "success": False,
            "observation": None,
            "smf_binding_annotation": smf_binding_annotation_value(ann),
        }

    ann = build_smf_binding_annotation(parsed, correlation_status=correlation_status)
    return {
        "skipped": False,
        "success": True,
        "observation": parsed,
        "smf_binding_annotation": smf_binding_annotation_value(ann),
        "smf_binding": ann,
    }


def smf_binding_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def parse_smf_binding_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def apply_smf_to_binding(binding: Dict[str, Any], smf_result: Dict[str, Any]) -> Dict[str, Any]:
    binding = dict(binding)
    flags = dict(binding.get("integration_flags") or {})
    if smf_result.get("success"):
        binding["binding_phase"] = BINDING_PHASE_SMF_OBSERVED
        flags["smf_integrated"] = True
    else:
        flags["smf_integrated"] = False
    binding["integration_flags"] = flags
    if smf_result.get("smf_binding"):
        binding["smf_binding"] = smf_result["smf_binding"]
    return binding
