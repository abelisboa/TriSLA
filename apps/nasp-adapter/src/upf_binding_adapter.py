"""
E2E-O3C — UPF Binding Adapter (read-only log observation).

Follows UPF_CONTRACT_SSOT_V1. Never blocks NSI instantiation.
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

UPF_BINDING_ANNOTATION_KEY = "trisla.io/upf-binding"
ADAPTER_VERSION = "upf-binding-v1"
CONTRACT_VERSION = "UPF_CONTRACT_SSOT_V1"
BINDING_STATUS_OBSERVED = "OBSERVED"
BINDING_STATUS_FAILED = "FAILED"
BINDING_PHASE_UPF_OBSERVED = "UPF_OBSERVED"

_RE_UE_IP = re.compile(r"UE IP Address IPv4:\s*([\d.]+)", re.I)
_RE_FTEID = re.compile(r"F-TEID IPv4:\s*([\d.]+)", re.I)
_RE_GTPU_IP = re.compile(r"gtp5g get gtpu ip:\s*([\d.]+)", re.I)
_RE_TEID = re.compile(r"gtp5g get teid:\s*(\d+)", re.I)
_RE_PFCP_ESTAB = re.compile(r"Handle PFCP session establishment request", re.I)
_RE_PFCP_DEL = re.compile(r"Handle PFCP session deletion request", re.I)
_RE_LOG_TS = re.compile(r"^(\d{4}-\d{2}-\d{2}T[\d:.]+Z)")


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def upf_binding_enabled() -> bool:
    return _env_bool("UPF_BINDING_ENABLED", False)


def _config_path() -> Path:
    override = os.getenv("UPF_BINDING_CONFIG")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "config" / "upf_binding_ssot.yaml"


@lru_cache(maxsize=1)
def load_upf_binding_config() -> Dict[str, Any]:
    import yaml

    path = _config_path()
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def _core_namespace(cfg: Dict[str, Any]) -> str:
    upf_cfg = cfg.get("upf") or {}
    env_name = upf_cfg.get("core_namespace_env", "NASP_FREE5GC_NAMESPACE")
    return os.getenv(env_name, upf_cfg.get("core_namespace", "ns-1274485"))


def _lab(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return cfg.get("lab") or {}


def _strip_ansi(line: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", line)


def parse_upf_log_lines(log_text: str, *, cfg: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    if not log_text or not log_text.strip():
        return None

    cfg = cfg or load_upf_binding_config()
    lab = _lab(cfg)

    ue_ips: List[str] = []
    fteid_ips: List[str] = []
    gtpu_ips: List[str] = []
    teids: List[str] = []
    pfcp_established = False
    pfcp_deleted = False
    last_event_ts: Optional[str] = None

    for raw_line in log_text.splitlines():
        line = _strip_ansi(raw_line)
        ts_m = _RE_LOG_TS.match(line)
        line_ts = ts_m.group(1) if ts_m else None

        if _RE_PFCP_ESTAB.search(line):
            pfcp_established = True
            pfcp_deleted = False
            last_event_ts = line_ts or last_event_ts
        if _RE_PFCP_DEL.search(line):
            pfcp_deleted = True
            last_event_ts = line_ts or last_event_ts

        m = _RE_UE_IP.search(line)
        if m:
            ue_ips.append(m.group(1))
            last_event_ts = line_ts or last_event_ts
        m = _RE_FTEID.search(line)
        if m:
            fteid_ips.append(m.group(1))
        m = _RE_GTPU_IP.search(line)
        if m:
            gtpu_ips.append(m.group(1))
        m = _RE_TEID.search(line)
        if m:
            teids.append(m.group(1))

    if not ue_ips and not pfcp_established and not pfcp_deleted:
        return None

    ue_ip = ue_ips[-1] if ue_ips else None
    gtpu_addr = gtpu_ips[-1] if gtpu_ips else (fteid_ips[-1] if fteid_ips else lab.get("upf_gtpu_addr"))
    n4_addr = os.getenv("NASP_UPF_N4_ADDR", lab.get("upf_n4_addr", "10.233.75.38"))

    if pfcp_deleted and not pfcp_established:
        session_state = "RELEASED"
    elif ue_ip or pfcp_established:
        session_state = "ACTIVE"
    else:
        session_state = "PENDING"

    return {
        "upf_node_name": lab.get("upf_node_name", "UPF"),
        "upf_n4_addr": n4_addr,
        "upf_gtpu_addr": gtpu_addr,
        "upf_n6_addr": lab.get("upf_n6_addr"),
        "ue_ip_observed": ue_ip,
        "dnn": lab.get("dnn", "internet"),
        "supi": lab.get("default_supi"),
        "session_state": session_state,
        "pfcp_session_established": pfcp_established,
        "pfcp_session_deleted": pfcp_deleted and not pfcp_established,
        "pfcp_last_event_timestamp": last_event_ts,
        "gtpu_teid": teids[-1] if teids else None,
        "observation_source": "upf",
    }


def fetch_upf_logs(cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = cfg or load_upf_binding_config()
    ns = _core_namespace(cfg)
    upf_cfg = cfg.get("upf") or {}
    label = upf_cfg.get("pod_label", "nf=upf")
    tail = int(upf_cfg.get("log_tail_lines", 3000))
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
            logger.warning("[UPF-BIND] no UPF pods in %s", ns)
            return ""
        pod_name = pods.items[0].metadata.name
        return v1.read_namespaced_pod_log(name=pod_name, namespace=ns, tail_lines=tail)
    except Exception as exc:
        logger.warning("[UPF-BIND] log fetch failed: %s", exc)
        return ""


def build_upf_binding_annotation(
    observation: Dict[str, Any],
    *,
    correlation_status: str = "UNKNOWN",
    freshness_status: str = "FRESH",
    freshness_source: str = "upf",
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "contract_version": CONTRACT_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "binding_status": BINDING_STATUS_OBSERVED,
        "observation_timestamp": now,
        "observation_source": observation.get("observation_source", "upf"),
        "upf_node_name": observation.get("upf_node_name", "UPF"),
        "upf_n4_addr": observation.get("upf_n4_addr"),
        "upf_gtpu_addr": observation.get("upf_gtpu_addr"),
        "upf_n6_addr": observation.get("upf_n6_addr"),
        "ue_ip_observed": observation.get("ue_ip_observed"),
        "session_id": session_id or "",
        "supi": observation.get("supi"),
        "dnn": observation.get("dnn", "internet"),
        "session_state": observation.get("session_state"),
        "pfcp_session_established": observation.get("pfcp_session_established", False),
        "pfcp_session_deleted": observation.get("pfcp_session_deleted", False),
        "pfcp_last_event_timestamp": observation.get("pfcp_last_event_timestamp"),
        "freshness_status": freshness_status,
        "freshness_source": freshness_source,
        "freshness_timestamp": now,
        "gtpu_teid": observation.get("gtpu_teid"),
        "slice_context": "CONTEXT_B",
        "correlation_status": correlation_status,
    }


def observe_upf_binding(
    slice_service_binding: Dict[str, Any],
    *,
    log_text: Optional[str] = None,
    correlation_status: str = "UNKNOWN",
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not upf_binding_enabled():
        return {"skipped": True, "upf_binding_annotation": None}

    cfg = load_upf_binding_config()
    text = log_text if log_text is not None else fetch_upf_logs(cfg)
    parsed = parse_upf_log_lines(text, cfg=cfg)

    if not parsed:
        ann = {
            "contract_version": CONTRACT_VERSION,
            "adapter_version": ADAPTER_VERSION,
            "binding_status": BINDING_STATUS_FAILED,
            "observation_timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "NO_UPF_OBSERVATION",
            "correlation_status": correlation_status,
            "freshness_status": "STALE",
        }
        return {
            "skipped": False,
            "success": False,
            "observation": None,
            "upf_binding_annotation": upf_binding_annotation_value(ann),
        }

    ann = build_upf_binding_annotation(
        parsed,
        correlation_status=correlation_status,
        freshness_source="upf",
        session_id=session_id,
    )
    return {
        "skipped": False,
        "success": True,
        "observation": parsed,
        "upf_binding_annotation": upf_binding_annotation_value(ann),
        "upf_binding": ann,
    }


def upf_binding_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def parse_upf_binding_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def apply_upf_to_binding(binding: Dict[str, Any], upf_result: Dict[str, Any]) -> Dict[str, Any]:
    binding = dict(binding)
    flags = dict(binding.get("integration_flags") or {})
    if upf_result.get("success"):
        binding["binding_phase"] = BINDING_PHASE_UPF_OBSERVED
        flags["upf_integrated"] = True
    else:
        flags["upf_integrated"] = False
    binding["integration_flags"] = flags
    if upf_result.get("upf_binding"):
        binding["upf_binding"] = upf_result["upf_binding"]
    return binding
