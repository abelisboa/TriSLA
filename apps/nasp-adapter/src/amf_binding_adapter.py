"""
E2E-O2C — AMF Binding Adapter (read-only log observation).

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
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

AMF_BINDING_ANNOTATION_KEY = "trisla.io/amf-binding"
ADAPTER_VERSION = "amf-binding-v1"
CONTRACT_VERSION = "1.0"
BINDING_STATUS_OBSERVED = "OBSERVED"
BINDING_STATUS_FAILED = "FAILED"
BINDING_PHASE_AMF_OBSERVED = "AMF_OBSERVED"

_RE_SERVING_SNSSAI = re.compile(
    r"ServingSnssai:\s*&?\{Sst:(\d+)\s+Sd:([0-9a-fA-F]+)\}", re.I
)
_RE_SELECT_SMF = re.compile(
    r"Select SMF \[snssai:\s*\{Sst:(\d+)\s+Sd:([0-9a-fA-F]+)\},\s*dnn:\s*(\w+)\]", re.I
)
_RE_SM_CONTEXT = re.compile(r"create smContext\[pduSessionID:\s*(\d+)\]\s*Success", re.I)
_RE_SUPI = re.compile(r"\[SUPI:(imsi-\d+)\]", re.I)
_RE_NGAP_ID = re.compile(r"AMF_UE_NGAP_ID:(\d+)", re.I)


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def amf_binding_enabled() -> bool:
    return _env_bool("AMF_BINDING_ENABLED", False)


def _config_path() -> Path:
    override = os.getenv("AMF_SMF_BINDING_CONFIG")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "config" / "amf_smf_binding_ssot.yaml"


@lru_cache(maxsize=1)
def load_binding_config() -> Dict[str, Any]:
    path = _config_path()
    if not path.is_file():
        return _embedded_defaults()
    try:
        import yaml  # type: ignore

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else _embedded_defaults()
    except Exception as exc:
        logger.warning("[AMF-BIND] config load failed: %s", exc)
        return _embedded_defaults()


def _embedded_defaults() -> Dict[str, Any]:
    core_ns = os.getenv("NASP_FREE5GC_NAMESPACE", "ns-1274485")
    return {
        "contract_version": "AMF_SMF_CONTRACT_SSOT_V1",
        "amf": {
            "nf_id": "095d920e-1782-4572-a1a0-7824c8393900",
            "core_namespace": core_ns,
            "pod_label": "nf=amf",
            "log_tail_lines": 3000,
        },
        "lab": {"default_supi": "imsi-208930000000001", "dnn": "internet"},
    }


def _core_namespace(cfg: Dict[str, Any]) -> str:
    amf_cfg = cfg.get("amf") or {}
    env_name = amf_cfg.get("core_namespace_env", "NASP_FREE5GC_NAMESPACE")
    return os.getenv(env_name, amf_cfg.get("core_namespace", "ns-1274485"))


def parse_amf_log_lines(log_text: str) -> Optional[Dict[str, Any]]:
    """Parse AMF logs; return latest complete observation or None."""
    if not log_text or not log_text.strip():
        return None

    serving: Optional[Dict[str, Any]] = None
    dnn: Optional[str] = None
    pdu_session_id: Optional[int] = None
    supi: Optional[str] = None
    amf_ue_ngap_id: Optional[int] = None
    sm_context_created = False
    smf_selected = False

    for line in log_text.splitlines():
        m = _RE_SUPI.search(line)
        if m:
            supi = m.group(1)

        m = _RE_NGAP_ID.search(line)
        if m:
            amf_ue_ngap_id = int(m.group(1))

        m = _RE_SERVING_SNSSAI.search(line)
        if m:
            serving = {"sst": int(m.group(1)), "sd": m.group(2).lower()}

        m = _RE_SELECT_SMF.search(line)
        if m:
            smf_selected = True
            serving = {"sst": int(m.group(1)), "sd": m.group(2).lower()}
            dnn = m.group(3)

        m = _RE_SM_CONTEXT.search(line)
        if m:
            sm_context_created = True
            pdu_session_id = int(m.group(1))

    if not serving and not sm_context_created and not smf_selected:
        return None

    return {
        "serving_snssai": serving,
        "dnn_observed": dnn,
        "pdu_session_id": pdu_session_id,
        "supi_observed": supi,
        "amf_ue_ngap_id": amf_ue_ngap_id,
        "sm_context_created": sm_context_created,
        "smf_selection_observed": smf_selected,
    }


def fetch_amf_logs(cfg: Optional[Dict[str, Any]] = None) -> str:
    """Fetch AMF pod logs via Kubernetes API (in-cluster)."""
    cfg = cfg or load_binding_config()
    ns = _core_namespace(cfg)
    label = (cfg.get("amf") or {}).get("pod_label", "nf=amf")
    tail = int((cfg.get("amf") or {}).get("log_tail_lines", 3000))
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
            logger.warning("[AMF-BIND] no AMF pods in %s", ns)
            return ""
        pod_name = pods.items[0].metadata.name
        return v1.read_namespaced_pod_log(name=pod_name, namespace=ns, tail_lines=tail)
    except Exception as exc:
        logger.warning("[AMF-BIND] log fetch failed: %s", exc)
        return ""


def build_amf_binding_annotation(
    observation: Dict[str, Any],
    *,
    slice_service_binding: Optional[Dict[str, Any]] = None,
    correlation_status: str = "UNKNOWN",
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = cfg or load_binding_config()
    amf_cfg = cfg.get("amf") or {}
    snssai = observation.get("serving_snssai") or {}
    smf_ref = (slice_service_binding or {}).get("smf_ref", "")

    return {
        "contract_version": CONTRACT_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "binding_status": BINDING_STATUS_OBSERVED,
        "observation_timestamp": datetime.now(timezone.utc).isoformat(),
        "amf_nf_id": amf_cfg.get("nf_id", ""),
        "supi": observation.get("supi_observed") or (cfg.get("lab") or {}).get("default_supi"),
        "serving_snssai": snssai,
        "dnn_observed": observation.get("dnn_observed") or (cfg.get("lab") or {}).get("dnn"),
        "selected_smf": smf_ref or "smf-nsmf",
        "pdu_session_id": observation.get("pdu_session_id"),
        "sm_context_created": bool(observation.get("sm_context_created")),
        "correlation_status": correlation_status,
        "slice_context": "CONTEXT_B",
    }


def observe_amf_binding(
    slice_service_binding: Dict[str, Any],
    *,
    log_text: Optional[str] = None,
    correlation_status: str = "UNKNOWN",
) -> Dict[str, Any]:
    if not amf_binding_enabled():
        return {"skipped": True, "amf_binding_annotation": None}

    cfg = load_binding_config()
    text = log_text if log_text is not None else fetch_amf_logs(cfg)
    parsed = parse_amf_log_lines(text)

    if not parsed:
        ann = {
            "contract_version": CONTRACT_VERSION,
            "adapter_version": ADAPTER_VERSION,
            "binding_status": BINDING_STATUS_FAILED,
            "observation_timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "NO_AMF_OBSERVATION",
            "correlation_status": "UNKNOWN",
        }
        return {
            "skipped": False,
            "success": False,
            "observation": None,
            "amf_binding_annotation": amf_binding_annotation_value(ann),
        }

    ann = build_amf_binding_annotation(
        parsed,
        slice_service_binding=slice_service_binding,
        correlation_status=correlation_status,
        cfg=cfg,
    )
    return {
        "skipped": False,
        "success": True,
        "observation": parsed,
        "amf_binding_annotation": amf_binding_annotation_value(ann),
        "amf_binding": ann,
    }


def amf_binding_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def parse_amf_binding_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def apply_amf_to_binding(binding: Dict[str, Any], amf_result: Dict[str, Any]) -> Dict[str, Any]:
    binding = dict(binding)
    flags = dict(binding.get("integration_flags") or {})
    if amf_result.get("success"):
        binding["binding_phase"] = BINDING_PHASE_AMF_OBSERVED
        flags["amf_integrated"] = True
    else:
        flags["amf_integrated"] = False
    binding["integration_flags"] = flags
    if amf_result.get("amf_binding"):
        binding["amf_binding"] = amf_result["amf_binding"]
    return binding
