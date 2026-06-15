"""
E2E-O5C — Transport Binding Adapter (read-only ONOS REST observation).

Follows TRANSPORT_CONTRACT_SSOT_V1. Never blocks NSI instantiation.
GET-only toward ONOS — no POST/PUT/DELETE.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

TRANSPORT_BINDING_ANNOTATION_KEY = "trisla.io/transport-binding"
ADAPTER_VERSION = "transport-binding-v1"
CONTRACT_VERSION = "TRANSPORT_CONTRACT_SSOT_V1"
BINDING_STATUS_OBSERVED = "OBSERVED"
BINDING_STATUS_FAILED = "FAILED"
BINDING_PHASE_TRANSPORT_OBSERVED = "TRANSPORT_OBSERVED"

CTRL_HEALTH_HEALTHY = "HEALTHY"
CTRL_HEALTH_DEGRADED = "DEGRADED"
CTRL_HEALTH_UNREACHABLE = "UNREACHABLE"
CTRL_HEALTH_UNKNOWN = "UNKNOWN"

TOPO_EMPTY = "EMPTY"
TOPO_PARTIAL = "PARTIAL"
TOPO_CONNECTED = "CONNECTED"
TOPO_UNKNOWN = "UNKNOWN"

FRESHNESS_FRESH = "FRESH"
FRESHNESS_STALE = "STALE"
FRESHNESS_FAILED = "FAILED"
FRESHNESS_UNKNOWN = "UNKNOWN"


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def transport_binding_enabled() -> bool:
    return _env_bool("TRANSPORT_BINDING_ENABLED", False)


def _config_path() -> Path:
    override = os.getenv("TRANSPORT_BINDING_CONFIG")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "config" / "transport_binding_ssot.yaml"


@lru_cache(maxsize=1)
def load_transport_binding_config() -> Dict[str, Any]:
    path = _config_path()
    if not path.is_file():
        return {}
    try:
        import yaml

        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning("[TRANSPORT-BIND] config load failed: %s", exc)
        return {}


def _onos_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return cfg.get("onos") or {}


def _lab(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return cfg.get("lab") or {}


def _rest_url(cfg: Dict[str, Any]) -> str:
    onos = _onos_cfg(cfg)
    env_name = onos.get("rest_url_env", "ONOS_REST_URL")
    return os.getenv(env_name, onos.get("rest_url", "http://onos.nasp-transport.svc.cluster.local:8181")).rstrip("/")


def _rest_auth(cfg: Dict[str, Any]) -> Tuple[str, str]:
    onos = _onos_cfg(cfg)
    env_name = onos.get("auth_env", "ONOS_REST_AUTH")
    raw = os.getenv(env_name, "onos:rocks")
    if ":" in raw:
        user, pwd = raw.split(":", 1)
        return user, pwd
    return "onos", raw


def _rest_timeout(cfg: Dict[str, Any]) -> float:
    return float(_onos_cfg(cfg).get("rest_timeout_seconds", 10))


def onos_get_json(
    path: str,
    *,
    cfg: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
    auth: Optional[Tuple[str, str]] = None,
) -> Tuple[Optional[Any], Optional[str], float]:
    """GET-only ONOS REST. Returns (json_body, error_code, latency_ms)."""
    cfg = cfg or load_transport_binding_config()
    url = f"{(base_url or _rest_url(cfg)).rstrip('/')}{path}"
    user, pwd = auth or _rest_auth(cfg)
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    req = Request(url, method="GET", headers={"Authorization": f"Basic {token}", "Accept": "application/json"})
    start = time.monotonic()
    try:
        with urlopen(req, timeout=_rest_timeout(cfg)) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            latency_ms = (time.monotonic() - start) * 1000.0
            if not body.strip():
                return {}, None, latency_ms
            return json.loads(body), None, latency_ms
    except HTTPError as exc:
        latency_ms = (time.monotonic() - start) * 1000.0
        if exc.code in (401, 403):
            return None, "ONOS_AUTH_FAILED", latency_ms
        return None, f"ONOS_HTTP_{exc.code}", latency_ms
    except URLError:
        latency_ms = (time.monotonic() - start) * 1000.0
        return None, "ONOS_REST_UNREACHABLE", latency_ms
    except Exception:
        latency_ms = (time.monotonic() - start) * 1000.0
        return None, "ONOS_REST_ERROR", latency_ms


def _list_len(payload: Any, *keys: str) -> int:
    if payload is None:
        return 0
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in keys:
            val = payload.get(key)
            if isinstance(val, list):
                return len(val)
        if "count" in payload and isinstance(payload["count"], int):
            return payload["count"]
    return 0


def parse_intents(payload: Any) -> List[Dict[str, Any]]:
    items: List[Any] = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("intents") or []
    out: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "id": str(item.get("id") or item.get("intentId") or ""),
                "type": item.get("type") or item.get("intentType"),
                "app_id": item.get("appId") or item.get("app_id"),
                "state": item.get("state") or item.get("intentState"),
            }
        )
    return out


def parse_onos_snapshot(
    *,
    devices: Any = None,
    links: Any = None,
    hosts: Any = None,
    flows: Any = None,
    intents: Any = None,
    rest_error: Optional[str] = None,
    rest_latency_ms: float = 0.0,
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = cfg or load_transport_binding_config()
    lab = _lab(cfg)
    device_count = _list_len(devices, "devices")
    link_count = _list_len(links, "links")
    host_count = _list_len(hosts, "hosts")
    flow_count = _list_len(flows, "flows")
    intents_observed = parse_intents(intents)
    intent_count = len(intents_observed)

    failed_intents = sum(1 for i in intents_observed if str(i.get("state", "")).upper() == "FAILED")
    dominant_intent_state = None
    if intents_observed:
        states = [str(i.get("state") or "") for i in intents_observed]
        if all(s.upper() == "FAILED" for s in states if s):
            dominant_intent_state = "FAILED"
        elif any(s.upper() == "FAILED" for s in states):
            dominant_intent_state = "FAILED"
        else:
            dominant_intent_state = states[0] or None

    if device_count == 0 and link_count == 0:
        topology_health = TOPO_EMPTY
        lab_topology_empty = bool(lab.get("lab_topology_empty", True))
    elif device_count > 0 and link_count == 0:
        topology_health = TOPO_PARTIAL
        lab_topology_empty = False
    elif device_count > 0 and link_count > 0:
        topology_health = TOPO_CONNECTED
        lab_topology_empty = False
    else:
        topology_health = TOPO_UNKNOWN
        lab_topology_empty = False

    controller_reachable = rest_error is None
    if not controller_reachable:
        controller_health = CTRL_HEALTH_UNREACHABLE
    elif topology_health == TOPO_EMPTY and (failed_intents > 0 or intent_count > 0):
        controller_health = CTRL_HEALTH_DEGRADED
    elif controller_reachable:
        controller_health = CTRL_HEALTH_HEALTHY if failed_intents == 0 else CTRL_HEALTH_DEGRADED
    else:
        controller_health = CTRL_HEALTH_UNKNOWN

    return {
        "device_count": device_count,
        "link_count": link_count,
        "host_count": host_count,
        "flow_count": flow_count,
        "intent_count": intent_count,
        "failed_intents": failed_intents,
        "intents_observed": intents_observed,
        "dominant_intent_state": dominant_intent_state,
        "topology_health": topology_health,
        "topology_state": topology_health,
        "lab_topology_empty": lab_topology_empty,
        "controller_reachable": controller_reachable,
        "controller_health": controller_health,
        "rest_error": rest_error,
        "rest_latency_ms": round(rest_latency_ms, 2),
        "onos_version": lab.get("onos_version", "2.7.0"),
    }


def compute_freshness_status(
    snapshot: Dict[str, Any],
    *,
    cfg: Optional[Dict[str, Any]] = None,
) -> str:
    if snapshot.get("rest_error"):
        return FRESHNESS_FAILED
    if not snapshot.get("controller_reachable"):
        return FRESHNESS_FAILED
    return FRESHNESS_FRESH


def fetch_onos_controller_snapshot(
    cfg: Optional[Dict[str, Any]] = None,
    *,
    inject: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Fetch ONOS REST inventory (GET-only). inject= for tests."""
    cfg = cfg or load_transport_binding_config()
    if inject is not None:
        return parse_onos_snapshot(cfg=cfg, **inject)

    latencies: List[float] = []
    rest_error: Optional[str] = None

    def _get(path: str) -> Any:
        nonlocal rest_error
        data, err, lat = onos_get_json(path, cfg=cfg)
        latencies.append(lat)
        if err and rest_error is None:
            rest_error = err
        return data

    devices = _get("/onos/v1/devices")
    links = _get("/onos/v1/links")
    hosts = _get("/onos/v1/hosts")
    flows = _get("/onos/v1/flows")
    intents = _get("/onos/v1/intents")

    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    snap = parse_onos_snapshot(
        devices=devices,
        links=links,
        hosts=hosts,
        flows=flows,
        intents=intents,
        rest_error=rest_error,
        rest_latency_ms=avg_lat,
        cfg=cfg,
    )
    snap["observation_source"] = "onos_rest"
    return snap


def fetch_controller_pod_meta(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = cfg or load_transport_binding_config()
    onos = _onos_cfg(cfg)
    ns = onos.get("namespace", "nasp-transport")
    label = onos.get("pod_label", "app=onos")
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
            return {}
        pod = pods.items[0]
        return {
            "controller_pod": pod.metadata.name,
            "controller_pod_ip": pod.status.pod_ip,
        }
    except Exception as exc:
        logger.warning("[TRANSPORT-BIND] K8s pod fetch failed: %s", exc)
        return {}


def resolve_transport_ref(slice_service_binding: Optional[Dict[str, Any]], cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = cfg or load_transport_binding_config()
    lab = _lab(cfg)
    if isinstance(slice_service_binding, dict):
        ref = slice_service_binding.get("transport_ref")
        if ref:
            return str(ref)
    return str(lab.get("transport_ref", "onos.nasp-transport.svc.cluster.local:8181"))


def build_transport_binding_annotation(
    snapshot: Dict[str, Any],
    *,
    transport_ref: str,
    correlation_status: str = "UNKNOWN",
    freshness_status: Optional[str] = None,
    slice_context: str = "CONTEXT_A",
    transport_correlated: bool = False,
) -> Dict[str, Any]:
    cfg = load_transport_binding_config()
    lab = _lab(cfg)
    now = datetime.now(timezone.utc).isoformat()
    fs = freshness_status or compute_freshness_status(snapshot, cfg=cfg)
    binding_status = BINDING_STATUS_OBSERVED if fs == FRESHNESS_FRESH else BINDING_STATUS_FAILED

    return {
        "contract_version": CONTRACT_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "binding_status": binding_status,
        "controller": "onos",
        "observation_timestamp": now,
        "observation_source": snapshot.get("observation_source", "onos_rest"),
        "transport_ref": transport_ref,
        "onos_rest_url": _rest_url(cfg),
        "onos_version": snapshot.get("onos_version") or lab.get("onos_version"),
        "controller_reachable": snapshot.get("controller_reachable", False),
        "controller_health": snapshot.get("controller_health", CTRL_HEALTH_UNKNOWN),
        "topology_health": snapshot.get("topology_health", TOPO_UNKNOWN),
        "topology_state": snapshot.get("topology_state") or snapshot.get("topology_health", TOPO_UNKNOWN),
        "lab_topology_empty": snapshot.get("lab_topology_empty", False),
        "device_count": snapshot.get("device_count", 0),
        "devices_count": snapshot.get("device_count", 0),
        "link_count": snapshot.get("link_count", 0),
        "links_count": snapshot.get("link_count", 0),
        "host_count": snapshot.get("host_count", 0),
        "flow_count": snapshot.get("flow_count", 0),
        "flows_count": snapshot.get("flow_count", 0),
        "intent_count": snapshot.get("intent_count", 0),
        "intents_count": snapshot.get("intent_count", 0),
        "failed_intents": snapshot.get("failed_intents", 0),
        "dominant_intent_state": snapshot.get("dominant_intent_state"),
        "intent_state": snapshot.get("dominant_intent_state"),
        "intents_observed": snapshot.get("intents_observed") or [],
        "rest_latency_ms": snapshot.get("rest_latency_ms"),
        "freshness_source": "onos_rest",
        "freshness_status": fs,
        "freshness_timestamp": now,
        "slice_context": slice_context,
        "correlation_status": correlation_status,
        "transport_correlated": transport_correlated,
        "transport_binding_status": binding_status,
    }


def observe_transport_binding(
    slice_service_binding: Dict[str, Any],
    *,
    snapshot_inject: Optional[Dict[str, Any]] = None,
    correlation_status: str = "UNKNOWN",
) -> Dict[str, Any]:
    if not transport_binding_enabled():
        return {"skipped": True, "transport_binding_annotation": None}

    cfg = load_transport_binding_config()
    transport_ref = resolve_transport_ref(slice_service_binding, cfg)

    if snapshot_inject is not None:
        snapshot = fetch_onos_controller_snapshot(cfg, inject=snapshot_inject)
    else:
        snapshot = fetch_onos_controller_snapshot(cfg)

    pod_meta = fetch_controller_pod_meta(cfg)
    snapshot.update({k: v for k, v in pod_meta.items() if v})

    fs = compute_freshness_status(snapshot, cfg=cfg)
    if snapshot.get("rest_error"):
        ann = {
            "contract_version": CONTRACT_VERSION,
            "adapter_version": ADAPTER_VERSION,
            "binding_status": BINDING_STATUS_FAILED,
            "controller": "onos",
            "observation_timestamp": datetime.now(timezone.utc).isoformat(),
            "error": snapshot.get("rest_error"),
            "transport_ref": transport_ref,
            "freshness_status": FRESHNESS_FAILED,
            "freshness_source": "onos_rest",
            "correlation_status": correlation_status,
            "transport_binding_status": BINDING_STATUS_FAILED,
        }
        return {
            "skipped": False,
            "success": False,
            "snapshot": snapshot,
            "transport_binding_annotation": transport_binding_annotation_value(ann),
            "transport_binding": ann,
        }

    ann = build_transport_binding_annotation(
        snapshot,
        transport_ref=transport_ref,
        correlation_status=correlation_status,
        freshness_status=fs,
    )
    return {
        "skipped": False,
        "success": True,
        "snapshot": snapshot,
        "transport_binding_annotation": transport_binding_annotation_value(ann),
        "transport_binding": ann,
    }


def transport_binding_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def parse_transport_binding_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def apply_transport_to_binding(binding: Dict[str, Any], transport_result: Dict[str, Any]) -> Dict[str, Any]:
    binding = dict(binding)
    flags = dict(binding.get("integration_flags") or {})
    if transport_result.get("success"):
        binding["binding_phase"] = BINDING_PHASE_TRANSPORT_OBSERVED
        flags["onos_integrated"] = True
    else:
        flags["onos_integrated"] = False
    binding["integration_flags"] = flags
    if transport_result.get("transport_binding"):
        binding["transport_binding"] = transport_result["transport_binding"]
    return binding
