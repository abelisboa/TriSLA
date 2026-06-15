"""
E2E-O1C — NSSF Adapter: slice_service_binding → Nnssf_NSSelection v1.

Follows NSSF_CONTRACT_SSOT_V1. Never blocks NSI instantiation on failure.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)

NSSF_SELECTION_ANNOTATION_KEY = "trisla.io/nssf-selection"
ADAPTER_VERSION = "nssf-adapter-v1"
BINDING_PHASE_METADATA = "METADATA_ONLY"
BINDING_PHASE_NSSF_SELECTED = "NSSF_SELECTED"

_selection_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def nssf_adapter_enabled() -> bool:
    return _env_bool("NSSF_ADAPTER_ENABLED", False)


def _config_path() -> Path:
    override = os.getenv("NSSF_ADAPTER_CONFIG")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "config" / "nssf_adapter_ssot.yaml"


@lru_cache(maxsize=1)
def load_adapter_config() -> Dict[str, Any]:
    path = _config_path()
    if not path.is_file():
        logger.warning("[NSSF] adapter config not found at %s — using embedded defaults", path)
        return _embedded_defaults()
    try:
        import yaml  # type: ignore

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError("invalid nssf adapter config")
        return data
    except Exception as exc:
        logger.error("[NSSF] failed to load %s: %s — embedded defaults", path, exc)
        return _embedded_defaults()


def _embedded_defaults() -> Dict[str, Any]:
    core_ns = os.getenv("NASP_FREE5GC_NAMESPACE", "ns-1274485")
    return {
        "contract_version": "NSSF_CONTRACT_SSOT_V1",
        "nssf": {
            "base_url": f"http://nssf-nnssf.{core_ns}.svc.cluster.local:80",
            "nf_type": "AMF",
            "amf_nf_id": "",
            "nrf_discovery_url": f"http://nrf-nnrf.{core_ns}.svc.cluster.local:8000/nnrf-nfm/v1/nf-instances",
            "selection_path": "/nnssf-nsselection/v1/network-slice-information",
            "selection_type": "PDU_SESSION",
            "roaming_indication": "NON_ROAMING",
        },
        "sd_map": {
            "URLLC": {"sd_trisla": "000001", "sd_nssf": "1"},
            "eMBB": {"sd_trisla": "000002", "sd_nssf": "2"},
            "mMTC": {"sd_trisla": "000003", "sd_nssf": "3"},
        },
        "dnn_map": {"urllc": "internet", "embb": "internet", "mmtc": "internet"},
        "lab_unified": {"enabled_env": "NSSF_LAB_UNIFIED_SLICE", "sd_nssf": "010203"},
        "fallback": {"max_retries": 2, "retry_delay_seconds": 0.5, "cache_ttl_seconds": 300},
        "timeouts": {"connect_seconds": 2, "read_seconds": 5},
    }


def _lab_unified_enabled(cfg: Dict[str, Any]) -> bool:
    env_name = (cfg.get("lab_unified") or {}).get("enabled_env", "NSSF_LAB_UNIFIED_SLICE")
    return _env_bool(env_name, False)


def sd_trisla_to_nssf(
    *,
    sd_trisla: str,
    slice_type: Optional[str],
    cfg: Optional[Dict[str, Any]] = None,
) -> str:
    cfg = cfg or load_adapter_config()
    if _lab_unified_enabled(cfg):
        return str((cfg.get("lab_unified") or {}).get("sd_nssf", "010203"))

    sd_map = cfg.get("sd_map") or {}
    if slice_type and slice_type in sd_map:
        return str(sd_map[slice_type].get("sd_nssf", sd_map[slice_type].get("sd_trisla", sd_trisla)))

    norm = (slice_type or "").strip()
    for key, row in sd_map.items():
        if key.upper() == norm.upper() or key == norm:
            return str(row.get("sd_nssf", sd_trisla))

    for row in sd_map.values():
        if str(row.get("sd_trisla")) == sd_trisla:
            return str(row.get("sd_nssf", sd_trisla))

    return sd_trisla.lstrip("0") or sd_trisla


def resolve_smf_dnn(dnn_trisla: str, cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = cfg or load_adapter_config()
    dnn_map = cfg.get("dnn_map") or {}
    return str(dnn_map.get(dnn_trisla.lower(), dnn_map.get(dnn_trisla, "internet")))


def resolve_nssf_base_url(binding: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    ref = binding.get("nssf_ref") or (cfg.get("nssf") or {}).get("base_url", "")
    if not ref:
        return str((cfg.get("nssf") or {}).get("base_url", ""))
    if ref.startswith("http://") or ref.startswith("https://"):
        return ref.rstrip("/")
    return f"http://{ref}".rstrip("/")


def resolve_amf_nf_id(cfg: Dict[str, Any]) -> Optional[str]:
    env_id = os.getenv("NSSF_AMF_NF_ID", "").strip()
    if env_id:
        return env_id
    cfg_id = str((cfg.get("nssf") or {}).get("amf_nf_id") or "").strip()
    if cfg_id:
        return cfg_id
    return _discover_amf_nf_id(cfg)


def _httpx_timeout(cfg: Dict[str, Any]) -> httpx.Timeout:
    timeouts = cfg.get("timeouts") or {}
    read = float(timeouts.get("read_seconds", 5))
    connect = float(timeouts.get("connect_seconds", 2))
    return httpx.Timeout(connect=connect, read=read, write=read, pool=connect)


def _discover_amf_nf_id(cfg: Dict[str, Any]) -> Optional[str]:
    nrf_url = (cfg.get("nssf") or {}).get("nrf_discovery_url")
    if not nrf_url:
        return None
    try:
        with httpx.Client(timeout=_httpx_timeout(cfg)) as client:
            resp = client.get(f"{nrf_url.rstrip('/')}", params={"nf-type": "AMF", "limit": 1})
            resp.raise_for_status()
            data = resp.json()
            items = (data.get("_link") or {}).get("item") or []
            if not items:
                return None
            href = items[0].get("href", "")
            return href.rstrip("/").split("/")[-1] if href else None
    except Exception as exc:
        logger.warning("[NSSF] AMF nf-id NRF discovery failed: %s", exc)
        return None


def build_pdu_session_query_payload(sst: int, sd_nssf: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    roaming = (cfg.get("nssf") or {}).get("roaming_indication", "NON_ROAMING")
    return {
        "sNssai": {"sst": int(sst), "sd": str(sd_nssf)},
        "roamingIndication": roaming,
    }


def build_selection_url(
    *,
    base_url: str,
    nf_type: str,
    nf_id: str,
    pdu_payload: Dict[str, Any],
    cfg: Dict[str, Any],
) -> str:
    path = (cfg.get("nssf") or {}).get("selection_path", "/nnssf-nsselection/v1/network-slice-information")
    encoded_slice = quote(json.dumps(pdu_payload, separators=(",", ":")), safe="")
    return (
        f"{base_url.rstrip('/')}{path}"
        f"?nf-type={quote(str(nf_type))}"
        f"&nf-id={quote(str(nf_id))}"
        f"&slice-info-request-for-pdu-session={encoded_slice}"
    )


def parse_nssf_response(body: Any, http_status: int) -> Dict[str, Any]:
    if http_status == 404:
        return {"selection_status": "FAILED", "http_status": 404, "nsiInformation": None, "error": "HTTP 404"}

    if not isinstance(body, dict):
        return {"selection_status": "FAILED", "http_status": http_status, "nsiInformation": None}

    nsi_info = body.get("nsiInformation")
    if isinstance(nsi_info, dict) and nsi_info.get("nsiId"):
        return {
            "selection_status": "SUCCESS",
            "http_status": http_status,
            "nsiInformation": {
                "nsiId": str(nsi_info.get("nsiId")),
                "nrfId": nsi_info.get("nrfId"),
            },
        }

    if body == {} or not body:
        return {"selection_status": "FAILED", "http_status": http_status, "nsiInformation": None, "error": "NO_MATCH"}

    return {"selection_status": "FAILED", "http_status": http_status, "nsiInformation": None, "raw": body}


def _cache_get(key: str, cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    entry = _selection_cache.get(key)
    if not entry:
        return None
    expires, value = entry
    if time.time() > expires:
        _selection_cache.pop(key, None)
        return None
    return dict(value)


def _cache_set(key: str, value: Dict[str, Any], cfg: Dict[str, Any]) -> None:
    if value.get("selection_status") != "SUCCESS":
        return
    ttl = int((cfg.get("fallback") or {}).get("cache_ttl_seconds", 300))
    _selection_cache[key] = (time.time() + ttl, dict(value))


def _http_get_selection(url: str, cfg: Dict[str, Any]) -> Tuple[int, Any]:
    with httpx.Client(timeout=_httpx_timeout(cfg)) as client:
        resp = client.get(url)
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return resp.status_code, body


def select_nssf_slice(
    slice_service_binding: Dict[str, Any],
    *,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    if not nssf_adapter_enabled():
        return {
            "binding": dict(slice_service_binding),
            "nssf_selection_annotation": None,
            "skipped": True,
        }

    cfg = load_adapter_config()
    binding = dict(slice_service_binding)
    sst = int(binding.get("sst") or binding.get("nssai", {}).get("sst", 1))
    sd_trisla = str(binding.get("sd") or binding.get("nssai", {}).get("sd", "000002"))
    slice_type = binding.get("slice_type") or binding.get("serviceProfile")
    dnn_trisla = str(binding.get("dnn", "embb"))

    sd_nssf = sd_trisla_to_nssf(sd_trisla=sd_trisla, slice_type=slice_type, cfg=cfg)
    binding["smf_dnn_resolved"] = resolve_smf_dnn(dnn_trisla, cfg)

    cache_key = f"{sst}:{sd_nssf}"
    if not force_refresh:
        cached = _cache_get(cache_key, cfg)
        if cached:
            return _apply_selection_to_binding(binding, cached, cfg, from_cache=True)

    nf_id = resolve_amf_nf_id(cfg)
    if not nf_id:
        return _failed_result(binding, "AMF_NF_ID_UNAVAILABLE", cfg, sd_nssf=sd_nssf, sst=sst)

    nf_type = (cfg.get("nssf") or {}).get("nf_type", "AMF")
    base_url = resolve_nssf_base_url(binding, cfg)
    pdu_payload = build_pdu_session_query_payload(sst, sd_nssf, cfg)
    url = build_selection_url(
        base_url=base_url,
        nf_type=nf_type,
        nf_id=nf_id,
        pdu_payload=pdu_payload,
        cfg=cfg,
    )

    max_retries = int((cfg.get("fallback") or {}).get("max_retries", 2))
    delay = float((cfg.get("fallback") or {}).get("retry_delay_seconds", 0.5))
    last_error = "UNKNOWN"

    for attempt in range(max_retries + 1):
        try:
            http_status, body = _http_get_selection(url, cfg)
            parsed = parse_nssf_response(body, http_status)
            if parsed.get("selection_status") == "SUCCESS":
                parsed["requested_snssai"] = {"sst": sst, "sd": sd_nssf}
                parsed["selection_type"] = "PDU_SESSION"
                parsed["selected_at"] = datetime.now(timezone.utc).isoformat()
                parsed["adapter_version"] = ADAPTER_VERSION
                parsed["nssf_ref_used"] = base_url
                _cache_set(cache_key, parsed, cfg)
                return _apply_selection_to_binding(binding, parsed, cfg)

            last_error = parsed.get("error") or "NO_MATCH"

            if not _lab_unified_enabled(cfg):
                lab_sd = str((cfg.get("lab_unified") or {}).get("sd_nssf", "010203"))
                if sd_nssf != lab_sd:
                    pdu_payload = build_pdu_session_query_payload(sst, lab_sd, cfg)
                    url = build_selection_url(
                        base_url=base_url,
                        nf_type=nf_type,
                        nf_id=nf_id,
                        pdu_payload=pdu_payload,
                        cfg=cfg,
                    )
                    http_status, body = _http_get_selection(url, cfg)
                    parsed = parse_nssf_response(body, http_status)
                    if parsed.get("selection_status") == "SUCCESS":
                        parsed["requested_snssai"] = {"sst": sst, "sd": lab_sd}
                        parsed["selection_type"] = "PDU_SESSION"
                        parsed["selected_at"] = datetime.now(timezone.utc).isoformat()
                        parsed["adapter_version"] = ADAPTER_VERSION
                        parsed["nssf_ref_used"] = base_url
                        parsed["fallback_reason"] = "lab_unified_retry"
                        _cache_set(f"{sst}:{lab_sd}", parsed, cfg)
                        return _apply_selection_to_binding(binding, parsed, cfg)

            if http_status == 404:
                break
        except httpx.TimeoutException:
            last_error = "TIMEOUT"
        except httpx.ConnectError:
            last_error = "CONNECTION_ERROR"
        except Exception as exc:
            last_error = str(exc)
            logger.warning("[NSSF] selection attempt %s failed: %s", attempt, exc)

        if attempt < max_retries:
            time.sleep(delay)

    return _failed_result(binding, last_error, cfg, sd_nssf=sd_nssf, sst=sst)


def _failed_result(
    binding: Dict[str, Any],
    error: str,
    cfg: Dict[str, Any],
    *,
    sd_nssf: Optional[str] = None,
    sst: Optional[int] = None,
) -> Dict[str, Any]:
    binding = dict(binding)
    binding["binding_phase"] = BINDING_PHASE_METADATA
    flags = dict(binding.get("integration_flags") or {})
    flags["nssf_integrated"] = False
    binding["integration_flags"] = flags
    selection: Dict[str, Any] = {
        "selection_status": "FAILED",
        "error": error,
        "selected_at": datetime.now(timezone.utc).isoformat(),
        "adapter_version": ADAPTER_VERSION,
    }
    if sd_nssf is not None and sst is not None:
        selection["requested_snssai"] = {"sst": sst, "sd": sd_nssf}
    binding["nssf_selection"] = selection
    ann_payload = {
        "selection_status": "FAILED",
        "selection_timestamp": selection["selected_at"],
        "adapter_version": ADAPTER_VERSION,
        "error": error,
    }
    return {
        "binding": binding,
        "nssf_selection_annotation": nssf_selection_annotation_value(ann_payload),
        "skipped": False,
    }


def _apply_selection_to_binding(
    binding: Dict[str, Any],
    selection: Dict[str, Any],
    cfg: Dict[str, Any],
    *,
    from_cache: bool = False,
) -> Dict[str, Any]:
    binding = dict(binding)
    sel = dict(selection)
    if from_cache:
        sel["from_cache"] = True

    flags = dict(binding.get("integration_flags") or {})
    if sel.get("selection_status") == "SUCCESS":
        binding["binding_phase"] = BINDING_PHASE_NSSF_SELECTED
        flags["nssf_integrated"] = True
    else:
        binding["binding_phase"] = BINDING_PHASE_METADATA
        flags["nssf_integrated"] = False
    binding["integration_flags"] = flags
    binding["nssf_selection"] = sel

    nsi_info = sel.get("nsiInformation") or {}
    ann_payload: Dict[str, Any] = {
        "selection_status": sel.get("selection_status", "FAILED"),
        "selection_timestamp": sel.get("selected_at"),
        "adapter_version": ADAPTER_VERSION,
    }
    if nsi_info.get("nsiId"):
        ann_payload["nsiId"] = str(nsi_info["nsiId"])
    if nsi_info.get("nrfId"):
        ann_payload["nrfId"] = nsi_info["nrfId"]
    if sel.get("error"):
        ann_payload["error"] = sel["error"]

    return {
        "binding": binding,
        "nssf_selection_annotation": nssf_selection_annotation_value(ann_payload),
        "skipped": False,
    }


def nssf_selection_annotation_value(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def parse_nssf_selection_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
