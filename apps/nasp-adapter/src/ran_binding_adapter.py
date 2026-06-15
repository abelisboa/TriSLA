"""
E2E-O4C — RAN Binding Adapter (read-only AMF NGAP / UERANSIM log observation).

Follows RAN_CONTRACT_SSOT_V1. Never blocks NSI instantiation.
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

RAN_BINDING_ANNOTATION_KEY = "trisla.io/ran-binding"
ADAPTER_VERSION = "ran-binding-v1"
CONTRACT_VERSION = "RAN_CONTRACT_SSOT_V1"
BINDING_STATUS_OBSERVED = "OBSERVED"
BINDING_STATUS_FAILED = "FAILED"
BINDING_PHASE_RAN_OBSERVED = "RAN_OBSERVED"

NG_HEALTH_HEALTHY = "HEALTHY"
NG_HEALTH_DEGRADED = "DEGRADED"
NG_HEALTH_UNKNOWN = "UNKNOWN"

_RE_GNB_ID = re.compile(r"GNbID:\s*([0-9a-fA-F]+)", re.I)
_RE_PLMN = re.compile(r"Mcc:(\d+)\s+Mnc:(\d+)", re.I)
_RE_RAN_UE_NGAP = re.compile(r"RAN UE NGAP ID:\s*(\d+)", re.I)
_RE_AMF_UE_NGAP = re.compile(r"AMF_UE_NGAP_ID:(\d+)", re.I)
_RE_SUPI = re.compile(r"\[SUPI:(imsi-\d+)\]", re.I)
_RE_SERVING_SNSSAI = re.compile(
    r"ServingSnssai:\s*&?\{Sst:(\d+)\s+Sd:([0-9a-fA-F]+)\}", re.I
)
_RE_SELECT_SMF = re.compile(
    r"Select SMF \[snssai:\s*\{Sst:(\d+)\s+Sd:([0-9a-fA-F]+)\},\s*dnn:\s*(\w+)\]", re.I
)
_RE_SM_CONTEXT = re.compile(r"create smContext\[pduSessionID:\s*(\d+)\]\s*Success", re.I)
_RE_NG_SETUP = re.compile(r"Handle NG Setup request|NG Setup procedure is successful", re.I)
_RE_SCTP_LOST = re.compile(r"SCTP_COMM_LOST|Association terminated for AMF", re.I)
_RE_LOG_TS = re.compile(r"^(\d{4}-\d{2}-\d{2}T[\d:.]+Z)")


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def ran_binding_enabled() -> bool:
    return _env_bool("RAN_BINDING_ENABLED", False)


def _config_path() -> Path:
    override = os.getenv("RAN_BINDING_CONFIG")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "config" / "ran_binding_ssot.yaml"


@lru_cache(maxsize=1)
def load_ran_binding_config() -> Dict[str, Any]:
    path = _config_path()
    if not path.is_file():
        return {}
    try:
        import yaml

        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning("[RAN-BIND] config load failed: %s", exc)
        return {}


def _core_namespace(cfg: Dict[str, Any]) -> str:
    amf_cfg = cfg.get("amf") or {}
    env_name = amf_cfg.get("core_namespace_env", "NASP_FREE5GC_NAMESPACE")
    return os.getenv(env_name, amf_cfg.get("core_namespace", "ns-1274485"))


def _ran_namespace(cfg: Dict[str, Any]) -> str:
    uer_cfg = cfg.get("ueransim") or {}
    env_name = uer_cfg.get("ran_namespace_env", "GATE_3GPP_UERANSIM_NAMESPACE")
    return os.getenv(env_name, uer_cfg.get("ran_namespace", "ueransim"))


def _lab(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return cfg.get("lab") or {}


def _strip_ansi(line: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", line)


def parse_gnb_health_log(log_text: str) -> str:
    if not log_text:
        return NG_HEALTH_UNKNOWN
    if _RE_SCTP_LOST.search(log_text.splitlines()[-1] if log_text else ""):
        return NG_HEALTH_DEGRADED
    lines = log_text.splitlines()
    for line in reversed(lines[-50:]):
        if _RE_SCTP_LOST.search(line):
            return NG_HEALTH_DEGRADED
        if _RE_NG_SETUP.search(line):
            return NG_HEALTH_HEALTHY
    return NG_HEALTH_UNKNOWN


def parse_amf_ran_log_lines(
    log_text: str,
    *,
    target_supi: Optional[str] = None,
    cfg: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Parse AMF logs for RAN/NGAP context; prefer observations matching target_supi."""
    if not log_text or not log_text.strip():
        return None

    cfg = cfg or load_ran_binding_config()
    lab = _lab(cfg)
    target_supi = target_supi or lab.get("default_supi")

    gnb_id: Optional[str] = None
    plmn: Optional[Dict[str, str]] = None
    ran_ue_ngap_id: Optional[int] = None
    amf_ue_ngap_id: Optional[int] = None
    supi: Optional[str] = None
    serving: Optional[Dict[str, Any]] = None
    dnn: Optional[str] = None
    session_id: Optional[int] = None
    ng_setup_seen = False
    sctp_lost = False
    gnb_sctp_ip: Optional[str] = None
    last_ts: Optional[str] = None

    supi_observations: List[Dict[str, Any]] = []

    for raw_line in log_text.splitlines():
        line = _strip_ansi(raw_line)
        ts_m = _RE_LOG_TS.match(line)
        line_ts = ts_m.group(1) if ts_m else None

        if _RE_NG_SETUP.search(line):
            ng_setup_seen = True
        if _RE_SCTP_LOST.search(line):
            sctp_lost = True

        m = _RE_GNB_ID.search(line)
        if m:
            gnb_id = m.group(1)

        m = _RE_PLMN.search(line)
        if m:
            plmn = {"mcc": m.group(1), "mnc": m.group(2)}

        line_supi = None
        m = _RE_SUPI.search(line)
        if m:
            line_supi = m.group(1)
            supi = line_supi

        m = _RE_AMF_UE_NGAP.search(line)
        line_amf_ngap = int(m.group(1)) if m else None
        if line_amf_ngap is not None and line_supi:
            amf_ue_ngap_id = line_amf_ngap

        m = _RE_RAN_UE_NGAP.search(line)
        line_ran_ngap = int(m.group(1)) if m else None
        if line_ran_ngap is not None:
            ran_ue_ngap_id = line_ran_ngap

        m = _RE_SERVING_SNSSAI.search(line)
        if m:
            serving = {"sst": int(m.group(1)), "sd": m.group(2).lower()}

        m = _RE_SELECT_SMF.search(line)
        if m:
            serving = {"sst": int(m.group(1)), "sd": m.group(2).lower()}
            dnn = m.group(3)

        m = _RE_SM_CONTEXT.search(line)
        if m:
            session_id = int(m.group(1))

        if "SCTP Accept from:" in line or "[AMF] SCTP Accept from:" in line:
            ip_m = re.search(r"(\d+\.\d+\.\d+\.\d+):", line)
            if ip_m:
                gnb_sctp_ip = ip_m.group(1)

        if line_supi == target_supi or (target_supi and target_supi in line):
            obs = {
                "supi": line_supi or target_supi,
                "amf_ue_ngap_id": line_amf_ngap,
                "ran_ue_ngap_id": line_ran_ngap,
                "serving_snssai": serving,
                "dnn": dnn,
                "session_id": session_id,
                "timestamp": line_ts,
            }
            if any(v is not None for k, v in obs.items() if k != "timestamp"):
                supi_observations.append(obs)
            last_ts = line_ts or last_ts

    if target_supi and supi_observations:
        latest = supi_observations[-1]
        if latest.get("amf_ue_ngap_id") is not None:
            amf_ue_ngap_id = latest["amf_ue_ngap_id"]
        if latest.get("ran_ue_ngap_id") is not None:
            ran_ue_ngap_id = latest["ran_ue_ngap_id"]
        if latest.get("serving_snssai"):
            serving = latest["serving_snssai"]
        if latest.get("dnn"):
            dnn = latest["dnn"]
        if latest.get("session_id") is not None:
            session_id = latest["session_id"]
        supi = latest.get("supi") or target_supi

    if not gnb_id and not ran_ue_ngap_id and not amf_ue_ngap_id and not ng_setup_seen:
        return None

    if not gnb_id:
        gnb_id = lab.get("gnb_id")
    if not plmn:
        plmn = lab.get("plmn")
    if not supi:
        supi = target_supi

    if sctp_lost and not ng_setup_seen:
        ng_health = NG_HEALTH_DEGRADED
    elif ng_setup_seen and not sctp_lost:
        ng_health = NG_HEALTH_HEALTHY
    elif sctp_lost:
        ng_health = NG_HEALTH_DEGRADED
    else:
        ng_health = NG_HEALTH_UNKNOWN

    return {
        "gnb_id": gnb_id,
        "plmn": plmn,
        "ran_ue_ngap_id": ran_ue_ngap_id,
        "amf_ue_ngap_id": amf_ue_ngap_id,
        "supi": supi,
        "serving_snssai": serving,
        "dnn": dnn or lab.get("dnn"),
        "session_id": session_id,
        "gnb_sctp_ip": gnb_sctp_ip or lab.get("gnb_pod_ip"),
        "ng_association_health": ng_health,
        "ng_setup_observed": ng_setup_seen,
        "observation_source": "amf_ngap_log",
        "log_timestamp": last_ts,
    }


def fetch_amf_logs(cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = cfg or load_ran_binding_config()
    ns = _core_namespace(cfg)
    amf_cfg = cfg.get("amf") or {}
    label = amf_cfg.get("pod_label", "nf=amf")
    tail = int(amf_cfg.get("log_tail_lines", 3000))
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
            return ""
        pod_name = pods.items[0].metadata.name
        return v1.read_namespaced_pod_log(name=pod_name, namespace=ns, tail_lines=tail)
    except Exception as exc:
        logger.warning("[RAN-BIND] AMF log fetch failed: %s", exc)
        return ""


def fetch_gnb_logs(cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = cfg or load_ran_binding_config()
    ns = _ran_namespace(cfg)
    uer_cfg = cfg.get("ueransim") or {}
    label = uer_cfg.get("pod_label", "app=ueransim-singlepod")
    container = uer_cfg.get("gnb_container", "gnb")
    tail = int(uer_cfg.get("log_tail_lines", 500))
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
            return ""
        pod_name = pods.items[0].metadata.name
        return v1.read_namespaced_pod_log(
            name=pod_name, namespace=ns, container=container, tail_lines=tail
        )
    except Exception as exc:
        logger.warning("[RAN-BIND] gNB log fetch failed: %s", exc)
        return ""


def build_ran_binding_annotation(
    observation: Dict[str, Any],
    *,
    correlation_status: str = "UNKNOWN",
    freshness_status: str = "FRESH",
    freshness_source: str = "amf",
    registration_state_snapshot: Optional[str] = None,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    lab = _lab(load_ran_binding_config())
    return {
        "contract_version": CONTRACT_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "binding_status": BINDING_STATUS_OBSERVED,
        "observation_timestamp": now,
        "observation_source": observation.get("observation_source", "amf_ngap_log"),
        "gnb_id": observation.get("gnb_id"),
        "plmn": observation.get("plmn"),
        "ran_ue_ngap_id": observation.get("ran_ue_ngap_id"),
        "amf_ue_ngap_id": observation.get("amf_ue_ngap_id"),
        "supi": observation.get("supi"),
        "serving_snssai": observation.get("serving_snssai"),
        "dnn": observation.get("dnn") or lab.get("dnn"),
        "session_id": str(observation.get("session_id") or ""),
        "ran_ref": lab.get("ran_ref"),
        "gnb_pod_ip": observation.get("gnb_sctp_ip") or lab.get("gnb_pod_ip"),
        "nci": lab.get("nci"),
        "tac": lab.get("tac"),
        "ng_association_health": observation.get("ng_association_health", NG_HEALTH_UNKNOWN),
        "registration_state_snapshot": registration_state_snapshot,
        "freshness_source": freshness_source,
        "freshness_status": freshness_status,
        "freshness_timestamp": now,
        "slice_context": "CONTEXT_B",
        "correlation_status": correlation_status,
    }


def observe_ran_binding(
    slice_service_binding: Dict[str, Any],
    *,
    amf_log_text: Optional[str] = None,
    gnb_log_text: Optional[str] = None,
    correlation_status: str = "UNKNOWN",
    target_supi: Optional[str] = None,
) -> Dict[str, Any]:
    if not ran_binding_enabled():
        return {"skipped": True, "ran_binding_annotation": None}

    cfg = load_ran_binding_config()
    lab = _lab(cfg)
    supi = target_supi or lab.get("default_supi")

    amf_text = amf_log_text if amf_log_text is not None else fetch_amf_logs(cfg)
    parsed = parse_amf_ran_log_lines(amf_text, target_supi=supi, cfg=cfg)

    gnb_text = gnb_log_text if gnb_log_text is not None else fetch_gnb_logs(cfg)
    gnb_health = parse_gnb_health_log(gnb_text)
    if parsed and gnb_health == NG_HEALTH_DEGRADED and parsed.get("ng_association_health") != NG_HEALTH_HEALTHY:
        parsed["ng_association_health"] = NG_HEALTH_DEGRADED

    if not parsed or not parsed.get("gnb_id"):
        ann = {
            "contract_version": CONTRACT_VERSION,
            "adapter_version": ADAPTER_VERSION,
            "binding_status": BINDING_STATUS_FAILED,
            "observation_timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "NO_RAN_OBSERVATION",
            "correlation_status": correlation_status,
            "freshness_status": "MISSING",
        }
        return {
            "skipped": False,
            "success": False,
            "observation": parsed,
            "ran_binding_annotation": ran_binding_annotation_value(ann),
        }

    freshness = "FRESH" if parsed.get("ran_ue_ngap_id") is not None else "STALE"
    if parsed.get("ng_association_health") == NG_HEALTH_DEGRADED:
        freshness = "STALE"

    ann = build_ran_binding_annotation(
        parsed,
        correlation_status=correlation_status,
        freshness_status=freshness,
        freshness_source="amf",
    )
    return {
        "skipped": False,
        "success": True,
        "observation": parsed,
        "ran_binding_annotation": ran_binding_annotation_value(ann),
        "ran_binding": ann,
    }


def ran_binding_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def parse_ran_binding_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def apply_ran_to_binding(binding: Dict[str, Any], ran_result: Dict[str, Any]) -> Dict[str, Any]:
    binding = dict(binding)
    flags = dict(binding.get("integration_flags") or {})
    if ran_result.get("success"):
        binding["binding_phase"] = BINDING_PHASE_RAN_OBSERVED
        flags["ran_integrated"] = True
    else:
        flags["ran_integrated"] = False
    binding["integration_flags"] = flags
    if ran_result.get("ran_binding"):
        binding["ran_binding"] = ran_result["ran_binding"]
    return binding
