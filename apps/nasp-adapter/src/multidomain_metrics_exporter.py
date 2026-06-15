"""
O6 — Per-Slice Multidomain Metrics Export (read-only).

Polls NSI annotations (+ optional SEM intent metadata) and exposes Prometheus gauges.
Does not mutate binding, decision, BC, or SLA-Agent state.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from prometheus_client import Gauge, Info

logger = logging.getLogger(__name__)

_LABELS = ("intent_id", "nsi_id", "slice_type")

# --- Binding ---
TRISLA_BINDING_PHASE = Gauge(
    "trisla_binding_phase",
    "Binding phase code (see O6 SSOT inventory)",
    _LABELS,
)
TRISLA_NSSF_SELECTION_STATUS = Gauge(
    "trisla_nssf_selection_status",
    "NSSF selection status code",
    _LABELS,
)
TRISLA_AMF_BINDING_STATUS = Gauge(
    "trisla_amf_binding_status",
    "AMF binding status code",
    _LABELS,
)
TRISLA_SMF_BINDING_STATUS = Gauge(
    "trisla_smf_binding_status",
    "SMF binding status code",
    _LABELS,
)
TRISLA_UPF_BINDING_STATUS = Gauge(
    "trisla_upf_binding_status",
    "UPF binding status code",
    _LABELS,
)
TRISLA_RAN_BINDING_STATUS = Gauge(
    "trisla_ran_binding_status",
    "RAN binding status code",
    _LABELS,
)
TRISLA_TRANSPORT_BINDING_STATUS = Gauge(
    "trisla_transport_binding_status",
    "Transport binding status code",
    _LABELS,
)

# --- Decision ---
TRISLA_DECISION_SCORE = Gauge(
    "trisla_decision_score",
    "Decision Engine score [0,1]",
    _LABELS,
)
TRISLA_DECISION_STATUS = Gauge(
    "trisla_decision_status",
    "Decision status code (ACCEPT/RENEGOTIATE/REJECT/UNKNOWN)",
    _LABELS,
)
TRISLA_DECISION_CONFIDENCE = Gauge(
    "trisla_decision_confidence",
    "Decision confidence [0,1] when available",
    _LABELS,
)
TRISLA_DECISION_REASON = Info(
    "trisla_decision_reason",
    "Decision reason text (info metric)",
    _LABELS,
)

# --- Assurance ---
TRISLA_RUNTIME_ASSURANCE_STATUS = Gauge(
    "trisla_runtime_assurance_status",
    "Runtime assurance state code",
    _LABELS,
)
TRISLA_DOMAIN_COMPLIANCE = Gauge(
    "trisla_domain_compliance",
    "Domain compliance score [0,1]",
    _LABELS,
)
TRISLA_SLA_COMPLIANCE = Gauge(
    "trisla_sla_compliance",
    "SLA compliance score [0,1]",
    _LABELS,
)
TRISLA_VIOLATION_COUNT = Gauge(
    "trisla_violation_count",
    "Runtime assurance violation count",
    _LABELS,
)
TRISLA_DRIFT_COUNT = Gauge(
    "trisla_drift_count",
    "Runtime assurance drift event count",
    _LABELS,
)

# --- Blockchain ---
TRISLA_BLOCKCHAIN_COMMIT_STATUS = Gauge(
    "trisla_blockchain_commit_status",
    "Blockchain commit status code",
    _LABELS,
)
TRISLA_BLOCKCHAIN_BLOCK_NUMBER = Gauge(
    "trisla_blockchain_block_number",
    "Blockchain block number when committed",
    _LABELS,
)
TRISLA_BLOCKCHAIN_TX_PRESENT = Gauge(
    "trisla_blockchain_tx_present",
    "1 if governance tx hash present, else 0",
    _LABELS,
)
TRISLA_BLOCKCHAIN_GOVERNANCE_STATUS = Gauge(
    "trisla_blockchain_governance_status",
    "Governance registration status code",
    _LABELS,
)

# --- Transport (per-slice snapshot from transport-binding annotation) ---
TRISLA_TRANSPORT_CONTROLLER_HEALTH = Gauge(
    "trisla_transport_controller_health",
    "ONOS controller health code",
    _LABELS,
)
TRISLA_TRANSPORT_TOPOLOGY_STATE = Gauge(
    "trisla_transport_topology_state",
    "Transport topology state code",
    _LABELS,
)
TRISLA_TRANSPORT_DEVICES_COUNT = Gauge(
    "trisla_transport_devices_count",
    "ONOS devices count from last transport observation",
    _LABELS,
)
TRISLA_TRANSPORT_LINKS_COUNT = Gauge(
    "trisla_transport_links_count",
    "ONOS links count from last transport observation",
    _LABELS,
)
TRISLA_TRANSPORT_FLOWS_COUNT = Gauge(
    "trisla_transport_flows_count",
    "ONOS flows count from last transport observation",
    _LABELS,
)
TRISLA_TRANSPORT_FAILED_INTENTS = Gauge(
    "trisla_transport_failed_intents",
    "ONOS failed intents count from last transport observation",
    _LABELS,
)

_ALL_GAUGES: Tuple[Gauge, ...] = (
    TRISLA_BINDING_PHASE,
    TRISLA_NSSF_SELECTION_STATUS,
    TRISLA_AMF_BINDING_STATUS,
    TRISLA_SMF_BINDING_STATUS,
    TRISLA_UPF_BINDING_STATUS,
    TRISLA_RAN_BINDING_STATUS,
    TRISLA_TRANSPORT_BINDING_STATUS,
    TRISLA_DECISION_SCORE,
    TRISLA_DECISION_STATUS,
    TRISLA_DECISION_CONFIDENCE,
    TRISLA_RUNTIME_ASSURANCE_STATUS,
    TRISLA_DOMAIN_COMPLIANCE,
    TRISLA_SLA_COMPLIANCE,
    TRISLA_VIOLATION_COUNT,
    TRISLA_DRIFT_COUNT,
    TRISLA_BLOCKCHAIN_COMMIT_STATUS,
    TRISLA_BLOCKCHAIN_BLOCK_NUMBER,
    TRISLA_BLOCKCHAIN_TX_PRESENT,
    TRISLA_BLOCKCHAIN_GOVERNANCE_STATUS,
    TRISLA_TRANSPORT_CONTROLLER_HEALTH,
    TRISLA_TRANSPORT_TOPOLOGY_STATE,
    TRISLA_TRANSPORT_DEVICES_COUNT,
    TRISLA_TRANSPORT_LINKS_COUNT,
    TRISLA_TRANSPORT_FLOWS_COUNT,
    TRISLA_TRANSPORT_FAILED_INTENTS,
)

_BINDING_PHASE_CODES: Dict[str, float] = {
    "UNKNOWN": 0,
    "METADATA_ONLY": 1,
    "METADATA": 1,
    "NSSF_SELECTED": 2,
    "AMF_OBSERVED": 3,
    "SMF_OBSERVED": 4,
    "USER_PLANE_CORRELATED": 5,
    "ACCESS_CORRELATED": 6,
    "TRANSPORT_OBSERVED": 7,
    "TRANSPORT_CORRELATED": 8,
}

_GENERIC_STATUS_CODES: Dict[str, float] = {
    "UNKNOWN": 0,
    "SKIPPED": 0,
    "PENDING": 1,
    "SUCCESS": 2,
    "OBSERVED": 2,
    "COMMITTED": 2,
    "CONFIRMED": 2,
    "REGISTERED": 2,
    "COMPLIANT": 2,
    "WARNING": 3,
    "DEGRADED": 3,
    "DEGRADED_FALLBACK": 3,
    "AT_RISK": 3,
    "RENEGOTIATE": 3,
    "FAILED": 4,
    "REJECT": 4,
    "REJECTED": 4,
    "VIOLATED": 4,
    "ERROR": 4,
}

_DECISION_CODES: Dict[str, float] = {
    "UNKNOWN": 0,
    "ACCEPT": 1,
    "RENEGOTIATE": 2,
    "REJECT": 3,
}

_ASSURANCE_CODES: Dict[str, float] = {
    "UNKNOWN": 0,
    "COMPLIANT": 1,
    "WARNING": 2,
    "AT_RISK": 3,
    "VIOLATED": 4,
}

_CTRL_HEALTH_CODES: Dict[str, float] = {
    "UNKNOWN": 0,
    "HEALTHY": 1,
    "DEGRADED": 2,
    "UNREACHABLE": 3,
    "FAILED": 4,
}

_TOPOLOGY_CODES: Dict[str, float] = {
    "UNKNOWN": 0,
    "EMPTY": 1,
    "PARTIAL": 2,
    "DEGRADED": 3,
    "HEALTHY": 4,
    "OK": 4,
}


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def multidomain_metrics_export_enabled() -> bool:
    return _env_bool("MULTIDOMAIN_METRICS_EXPORT_ENABLED", False)


def _refresh_interval_seconds() -> int:
    try:
        return max(5, int(os.getenv("MULTIDOMAIN_METRICS_REFRESH_SECONDS", "30")))
    except ValueError:
        return 30


def _sem_base_url() -> str:
    return (
        os.getenv("SEM_CSMF_URL")
        or os.getenv("SEM_BASE_URL")
        or "http://trisla-sem-csmf.trisla.svc.cluster.local:8080"
    ).rstrip("/")


def _code(mapping: Dict[str, float], value: Optional[str], default: float = 0.0) -> float:
    if not value:
        return default
    key = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    return mapping.get(key, default)


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int:
    try:
        if value is None:
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def _nsi_identity(nsi: Dict[str, Any]) -> Tuple[str, str, str]:
    meta = nsi.get("metadata") or {}
    spec = nsi.get("spec") or {}
    nsi_id = (
        meta.get("name")
        or spec.get("nsiId")
        or spec.get("nsi_id")
        or "unknown"
    )
    intent_id = (
        spec.get("intentId")
        or spec.get("intent_id")
        or spec.get("nestId")
        or spec.get("nest_id")
        or nsi_id
    )
    slice_type = (
        spec.get("serviceProfile")
        or spec.get("service_profile")
        or spec.get("service_type")
        or meta.get("annotations", {}).get("trisla.io/service-profile")
        or "eMBB"
    )
    return str(intent_id), str(nsi_id), str(slice_type)


def _parse_json_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        val = json.loads(raw)
        return val if isinstance(val, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


_ANNOTATION_KEYS = {
    "ssb": "trisla.io/slice-service-binding",
    "nssf": "trisla.io/nssf-selection",
    "amf": "trisla.io/amf-binding",
    "smf": "trisla.io/smf-binding",
    "upf": "trisla.io/upf-binding",
    "ran": "trisla.io/ran-binding",
    "transport": "trisla.io/transport-binding",
    "pdu": "trisla.io/pdu-session-summary",
}


def _parse_nsi_annotations(nsi: Dict[str, Any]) -> Dict[str, Any]:
    ann = (nsi.get("metadata") or {}).get("annotations") or {}
    return {key: _parse_json_annotation(ann.get(ann_key)) for key, ann_key in _ANNOTATION_KEYS.items()}


def _sem_enrich_enabled() -> bool:
    return _env_bool("MULTIDOMAIN_METRICS_SEM_ENRICH_ENABLED", True)


def _sem_cache_ttl_seconds() -> int:
    try:
        return max(60, int(os.getenv("MULTIDOMAIN_METRICS_SEM_CACHE_TTL_SECONDS", "300")))
    except ValueError:
        return 300


def _has_binding_activity(parsed: Dict[str, Any]) -> bool:
    """True when at least one domain binding annotation is present."""
    for key in ("nssf", "amf", "smf", "upf", "ran", "transport"):
        if parsed.get(key):
            return True
    ssb = parsed.get("ssb") or {}
    phase = str(ssb.get("binding_phase") or "").upper()
    return phase not in ("", "UNKNOWN", "METADATA_ONLY", "METADATA")


_sem_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_sem_cache_lock = threading.Lock()


def _fetch_sem_metadata(intent_id: str) -> Dict[str, Any]:
    if not _sem_enrich_enabled() or not intent_id or intent_id == "unknown":
        return {}

    now = time.monotonic()
    with _sem_cache_lock:
        cached = _sem_cache.get(intent_id)
        if cached and (now - cached[0]) < _sem_cache_ttl_seconds():
            return dict(cached[1])

    url = f"{_sem_base_url()}/api/v1/intents/{intent_id}"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code != 200:
            meta: Dict[str, Any] = {}
        else:
            body = resp.json()
            meta = body.get("metadata") or body.get("extra_metadata") or {}
            meta = meta if isinstance(meta, dict) else {}
    except Exception as exc:
        logger.debug("[O6-METRICS] SEM fetch failed intent=%s: %s", intent_id, exc)
        meta = {}

    with _sem_cache_lock:
        _sem_cache[intent_id] = (now, meta)
        if len(_sem_cache) > 2000:
            oldest = sorted(_sem_cache.items(), key=lambda x: x[1][0])[:500]
            for key, _ in oldest:
                _sem_cache.pop(key, None)
    return dict(meta)


def _extract_decision_fields(sem_meta: Dict[str, Any]) -> Dict[str, Any]:
    decision = sem_meta.get("decision") or sem_meta.get("decision_status")
    reason = (
        sem_meta.get("reason")
        or sem_meta.get("justification")
        or sem_meta.get("decision_explanation")
        or ""
    )
    confidence = sem_meta.get("decision_confidence") or sem_meta.get("ml_confidence")
    return {
        "decision_score": _safe_float(sem_meta.get("decision_score")),
        "decision_status": decision,
        "decision_confidence": _safe_float(confidence),
        "decision_reason": str(reason)[:512] if reason else "",
    }


def _extract_assurance_fields(sem_meta: Dict[str, Any]) -> Dict[str, Any]:
    ra = sem_meta.get("runtime_assurance")
    if not isinstance(ra, dict):
        ra = {}
    violations = ra.get("violations")
    if not isinstance(violations, list):
        violations = []
    drift_events = ra.get("drift_events") or ra.get("drifts")
    drift_count = len(drift_events) if isinstance(drift_events, list) else _safe_int(ra.get("drift_count"))
    return {
        "runtime_assurance_status": ra.get("state") or sem_meta.get("runtime_assurance_status"),
        "domain_compliance": _safe_float(ra.get("domain_compliance") or sem_meta.get("domain_compliance")),
        "sla_compliance": _safe_float(ra.get("sla_compliance") or sem_meta.get("sla_compliance")),
        "violation_count": len(violations) if violations else _safe_int(ra.get("violation_count")),
        "drift_count": drift_count,
    }


def _extract_blockchain_fields(sem_meta: Dict[str, Any]) -> Dict[str, Any]:
    tx = (
        sem_meta.get("governance_registration_tx_hash")
        or sem_meta.get("blockchain_tx_hash")
        or sem_meta.get("tx_hash")
    )
    block_number = sem_meta.get("governance_registration_block_number") or sem_meta.get("block_number")
    bc_status = sem_meta.get("bc_status") or sem_meta.get("blockchain_status")
    gov_status = sem_meta.get("governance_registration_status")
    return {
        "blockchain_commit_status": bc_status,
        "blockchain_block_number": _safe_float(block_number),
        "blockchain_tx_present": 1.0 if tx else 0.0,
        "blockchain_governance_status": gov_status,
    }


def _binding_status_code(obj: Optional[Dict[str, Any]], *keys: str) -> float:
    if not isinstance(obj, dict):
        return 0.0
    for key in keys:
        val = obj.get(key)
        if val:
            return _code(_GENERIC_STATUS_CODES, str(val))
    return 0.0


def _build_slice_metrics(
    nsi: Dict[str, Any],
    *,
    sem_meta: Optional[Dict[str, Any]] = None,
    parsed: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    intent_id, nsi_id, slice_type = _nsi_identity(nsi)
    _ = (intent_id, nsi_id, slice_type)  # labels applied by caller

    parsed = parsed if parsed is not None else _parse_nsi_annotations(nsi)
    ssb = parsed.get("ssb") or {}
    nssf = parsed.get("nssf") or {}
    amf = parsed.get("amf") or {}
    smf = parsed.get("smf") or {}
    upf = parsed.get("upf") or {}
    ran = parsed.get("ran") or {}
    transport = parsed.get("transport") or {}

    binding_phase = ssb.get("binding_phase") or ssb.get("correlation_status")
    metrics: Dict[str, float] = {
        "binding_phase": _code(_BINDING_PHASE_CODES, str(binding_phase or "UNKNOWN")),
        "nssf_selection_status": _binding_status_code(nssf, "selection_status", "binding_status"),
        "amf_binding_status": _binding_status_code(amf, "binding_status"),
        "smf_binding_status": _binding_status_code(smf, "binding_status"),
        "upf_binding_status": _binding_status_code(upf, "binding_status"),
        "ran_binding_status": _binding_status_code(ran, "binding_status"),
        "transport_binding_status": _binding_status_code(
            transport, "transport_binding_status", "binding_status"
        ),
        "transport_controller_health": _code(
            _CTRL_HEALTH_CODES, str(transport.get("controller_health") or "UNKNOWN")
        ),
        "transport_topology_state": _code(
            _TOPOLOGY_CODES, str(transport.get("topology_state") or transport.get("topology_health") or "UNKNOWN")
        ),
        "transport_devices_count": float(_safe_int(transport.get("devices_count") or transport.get("device_count"))),
        "transport_links_count": float(_safe_int(transport.get("links_count") or transport.get("link_count"))),
        "transport_flows_count": float(_safe_int(transport.get("flows_count") or transport.get("flow_count"))),
        "transport_failed_intents": float(_safe_int(transport.get("failed_intents"))),
    }

    sem_meta = sem_meta or {}
    decision = _extract_decision_fields(sem_meta)
    assurance = _extract_assurance_fields(sem_meta)
    blockchain = _extract_blockchain_fields(sem_meta)

    metrics["decision_score"] = decision["decision_score"] if decision["decision_score"] is not None else 0.0
    metrics["decision_status"] = _code(_DECISION_CODES, str(decision["decision_status"] or "UNKNOWN"))
    metrics["decision_confidence"] = (
        decision["decision_confidence"] if decision["decision_confidence"] is not None else 0.0
    )
    metrics["runtime_assurance_status"] = _code(
        _ASSURANCE_CODES, str(assurance["runtime_assurance_status"] or "UNKNOWN")
    )
    metrics["domain_compliance"] = assurance["domain_compliance"] if assurance["domain_compliance"] is not None else 0.0
    metrics["sla_compliance"] = assurance["sla_compliance"] if assurance["sla_compliance"] is not None else 0.0
    metrics["violation_count"] = float(assurance["violation_count"])
    metrics["drift_count"] = float(assurance["drift_count"])
    metrics["blockchain_commit_status"] = _code(
        _GENERIC_STATUS_CODES, str(blockchain["blockchain_commit_status"] or "UNKNOWN")
    )
    metrics["blockchain_block_number"] = blockchain["blockchain_block_number"] or 0.0
    metrics["blockchain_tx_present"] = blockchain["blockchain_tx_present"]
    metrics["blockchain_governance_status"] = _code(
        _GENERIC_STATUS_CODES, str(blockchain["blockchain_governance_status"] or "UNKNOWN")
    )
    metrics["_decision_reason"] = decision["decision_reason"]  # type: ignore[assignment]
    return metrics


def _list_nsis_from_k8s(namespace: Optional[str] = None) -> List[Dict[str, Any]]:
    from kubernetes import client
    from controllers.k8s_auth import load_incluster_config_with_validation

    api_client, _, default_ns, _ = load_incluster_config_with_validation()
    ns = namespace or default_ns
    co = client.CustomObjectsApi(api_client=api_client)
    resp = co.list_namespaced_custom_object(
        group="trisla.io",
        version="v1",
        namespace=ns,
        plural="networksliceinstances",
    )
    items = resp.get("items") or []
    return [item for item in items if isinstance(item, dict)]


class MultidomainMetricsExporter:
    """Read-only exporter: refreshes Prometheus gauges from NSI + SEM metadata."""

    def __init__(
        self,
        *,
        list_nsis=None,
        fetch_sem=None,
    ):
        self._list_nsis = list_nsis or _list_nsis_from_k8s
        self._fetch_sem = fetch_sem or _fetch_sem_metadata
        self._lock = threading.Lock()
        self._active_labels: Set[Tuple[str, str, str]] = set()
        self._last_refresh_ok = False
        self._last_refresh_error: Optional[str] = None
        self._last_refresh_ts: Optional[str] = None

    @property
    def last_refresh_ok(self) -> bool:
        return self._last_refresh_ok

    @property
    def last_refresh_error(self) -> Optional[str]:
        return self._last_refresh_error

    def refresh(self, namespace: Optional[str] = None) -> int:
        """Poll NSIs and update gauges. Returns number of NSIs exported."""
        try:
            nsis = self._list_nsis(namespace)
        except Exception as exc:
            with self._lock:
                self._last_refresh_ok = False
                self._last_refresh_error = str(exc)
            logger.warning("[O6-METRICS] NSI list failed: %s", exc)
            return 0

        new_labels: Set[Tuple[str, str, str]] = set()
        exported = 0

        for nsi in nsis:
            intent_id, nsi_id, slice_type = _nsi_identity(nsi)
            label_tuple = (intent_id, nsi_id, slice_type)
            new_labels.add(label_tuple)

            parsed = _parse_nsi_annotations(nsi)
            sem_meta = self._fetch_sem(intent_id) if _has_binding_activity(parsed) else {}
            values = _build_slice_metrics(nsi, sem_meta=sem_meta, parsed=parsed)
            reason = str(values.pop("_decision_reason", "") or "")

            lbl = {"intent_id": intent_id, "nsi_id": nsi_id, "slice_type": slice_type}
            TRISLA_BINDING_PHASE.labels(**lbl).set(values["binding_phase"])
            TRISLA_NSSF_SELECTION_STATUS.labels(**lbl).set(values["nssf_selection_status"])
            TRISLA_AMF_BINDING_STATUS.labels(**lbl).set(values["amf_binding_status"])
            TRISLA_SMF_BINDING_STATUS.labels(**lbl).set(values["smf_binding_status"])
            TRISLA_UPF_BINDING_STATUS.labels(**lbl).set(values["upf_binding_status"])
            TRISLA_RAN_BINDING_STATUS.labels(**lbl).set(values["ran_binding_status"])
            TRISLA_TRANSPORT_BINDING_STATUS.labels(**lbl).set(values["transport_binding_status"])
            TRISLA_DECISION_SCORE.labels(**lbl).set(values["decision_score"])
            TRISLA_DECISION_STATUS.labels(**lbl).set(values["decision_status"])
            TRISLA_DECISION_CONFIDENCE.labels(**lbl).set(values["decision_confidence"])
            TRISLA_RUNTIME_ASSURANCE_STATUS.labels(**lbl).set(values["runtime_assurance_status"])
            TRISLA_DOMAIN_COMPLIANCE.labels(**lbl).set(values["domain_compliance"])
            TRISLA_SLA_COMPLIANCE.labels(**lbl).set(values["sla_compliance"])
            TRISLA_VIOLATION_COUNT.labels(**lbl).set(values["violation_count"])
            TRISLA_DRIFT_COUNT.labels(**lbl).set(values["drift_count"])
            TRISLA_BLOCKCHAIN_COMMIT_STATUS.labels(**lbl).set(values["blockchain_commit_status"])
            TRISLA_BLOCKCHAIN_BLOCK_NUMBER.labels(**lbl).set(values["blockchain_block_number"])
            TRISLA_BLOCKCHAIN_TX_PRESENT.labels(**lbl).set(values["blockchain_tx_present"])
            TRISLA_BLOCKCHAIN_GOVERNANCE_STATUS.labels(**lbl).set(values["blockchain_governance_status"])
            TRISLA_TRANSPORT_CONTROLLER_HEALTH.labels(**lbl).set(values["transport_controller_health"])
            TRISLA_TRANSPORT_TOPOLOGY_STATE.labels(**lbl).set(values["transport_topology_state"])
            TRISLA_TRANSPORT_DEVICES_COUNT.labels(**lbl).set(values["transport_devices_count"])
            TRISLA_TRANSPORT_LINKS_COUNT.labels(**lbl).set(values["transport_links_count"])
            TRISLA_TRANSPORT_FLOWS_COUNT.labels(**lbl).set(values["transport_flows_count"])
            TRISLA_TRANSPORT_FAILED_INTENTS.labels(**lbl).set(values["transport_failed_intents"])
            if reason:
                TRISLA_DECISION_REASON.labels(**lbl).info({"reason": reason})
            exported += 1

        self._remove_stale_labels(new_labels)

        from datetime import datetime, timezone

        with self._lock:
            self._active_labels = new_labels
            self._last_refresh_ok = True
            self._last_refresh_error = None
            self._last_refresh_ts = datetime.now(timezone.utc).isoformat()

        logger.info("[O6-METRICS] refreshed %d NSI(s)", exported)
        return exported

    def _remove_stale_labels(self, keep: Set[Tuple[str, str, str]]) -> None:
        stale = self._active_labels - keep
        for intent_id, nsi_id, slice_type in stale:
            lbl = {"intent_id": intent_id, "nsi_id": nsi_id, "slice_type": slice_type}
            for gauge in _ALL_GAUGES:
                try:
                    gauge.remove(*lbl.values())
                except KeyError:
                    pass
            try:
                TRISLA_DECISION_REASON.remove(*lbl.values())
            except KeyError:
                pass


_exporter: Optional[MultidomainMetricsExporter] = None
_refresh_thread: Optional[threading.Thread] = None


def get_multidomain_metrics_exporter() -> Optional[MultidomainMetricsExporter]:
    return _exporter


def start_multidomain_metrics_exporter() -> Optional[MultidomainMetricsExporter]:
    """Start background refresh when MULTIDOMAIN_METRICS_EXPORT_ENABLED=true."""
    global _exporter, _refresh_thread

    if not multidomain_metrics_export_enabled():
        logger.info("[O6-METRICS] export disabled (MULTIDOMAIN_METRICS_EXPORT_ENABLED=false)")
        return None

    if _exporter is not None:
        return _exporter

    _exporter = MultidomainMetricsExporter()
    interval = _refresh_interval_seconds()

    def _loop():
        while True:
            try:
                if _exporter is not None:
                    started = time.monotonic()
                    count = _exporter.refresh()
                    elapsed = time.monotonic() - started
                    logger.info("[O6-METRICS] refresh complete count=%d elapsed=%.1fs", count, elapsed)
            except Exception as exc:
                logger.warning("[O6-METRICS] refresh loop error: %s", exc)
            time.sleep(interval)

    _refresh_thread = threading.Thread(
        target=_loop,
        daemon=True,
        name="O6-Multidomain-Metrics",
    )
    _refresh_thread.start()
    # Kick off first refresh without waiting full interval
    threading.Thread(
        target=lambda: _exporter.refresh() if _exporter else None,
        daemon=True,
        name="O6-Multidomain-Metrics-Initial",
    ).start()
    logger.info("[O6-METRICS] exporter started (interval=%ss)", interval)
    return _exporter
