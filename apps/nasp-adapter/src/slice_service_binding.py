"""
Slice Service Binding (O6) — SSOT de mapeamento NSI/NSSI TriSLA → parâmetros 5G/O-RAN.

Enriquecimento seguro (metadata/annotations/spec.nssai). Não invoca NSSF/AMF/SMF/UPF/ONOS.
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

MAPPING_ANNOTATION_KEY = "trisla.io/slice-service-binding"
MAPPING_VERSION = "ssb-v1"
BINDING_PHASE = "METADATA_ONLY"

_DEFAULT_PROFILES: Dict[str, Dict[str, Any]] = {
    "URLLC": {
        "slice_type": "URLLC",
        "sst": 1,
        "sd": "000001",
        "dnn": "urllc",
    },
    "EMBB": {
        "slice_type": "eMBB",
        "sst": 1,
        "sd": "000002",
        "dnn": "embb",
    },
    "MMTC": {
        "slice_type": "mMTC",
        "sst": 1,
        "sd": "000003",
        "dnn": "mmtc",
    },
}


def _env_bool(name: str, default: bool = True) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def slice_service_binding_enabled() -> bool:
    if "SLICE_SERVICE_BINDING_ENABLED" in os.environ:
        return _env_bool("SLICE_SERVICE_BINDING_ENABLED", True)
    return _env_bool("E2E_5G_MAPPING_ENABLED", True)


def _config_path() -> Path:
    override = os.getenv("SLICE_SERVICE_BINDING_CONFIG") or os.getenv("E2E_5G_MAPPING_CONFIG")
    if override:
        return Path(override)
    base = Path(__file__).resolve().parent.parent / "config"
    json_path = base / "slice_service_binding_ssot.json"
    if json_path.is_file():
        return json_path
    return base / "slice_service_binding_ssot.yaml"


def _normalize_profile(service_profile: Optional[str]) -> str:
    sp = (service_profile or "eMBB").strip()
    upper = sp.upper()
    if upper == "URLLC":
        return "URLLC"
    if upper in ("MMTC", "MMTC"):
        return "mMTC"
    return "eMBB"


def _service_refs(core_ns: str, transport_ns: str, ran_ns: str) -> Dict[str, str]:
    return {
        "nssf_ref": f"nssf-nnssf.{core_ns}.svc.cluster.local:80",
        "amf_ref": f"amf-namf.{core_ns}.svc.cluster.local:80",
        "smf_ref": f"smf-nsmf.{core_ns}.svc.cluster.local:80",
        "upf_ref": f"upf-service.{core_ns}.svc.cluster.local:8805",
        "ran_ref": f"ueransim-gnb.{ran_ns}.svc.cluster.local",
        "transport_ref": f"onos.{transport_ns}.svc.cluster.local:8181",
    }


@lru_cache(maxsize=1)
def load_mapping_config() -> Dict[str, Any]:
    path = _config_path()
    if not path.is_file():
        logger.warning("[SSB] mapping config not found at %s — using embedded defaults", path)
        core_ns = os.getenv("NASP_FREE5GC_NAMESPACE", "ns-1274485")
        transport_ns = os.getenv("SSB_TRANSPORT_NAMESPACE", os.getenv("E2E_TRANSPORT_NAMESPACE", "nasp-transport"))
        ran_ns = os.getenv("SSB_RAN_NAMESPACE", os.getenv("E2E_RAN_NAMESPACE", "ueransim"))
        refs = _service_refs(core_ns, transport_ns, ran_ns)
        profiles = {}
        for key, base in _DEFAULT_PROFILES.items():
            norm = "URLLC" if key == "URLLC" else ("mMTC" if key == "MMTC" else "eMBB")
            profiles[norm] = {**base, **refs}
        return {
            "mapping_version": MAPPING_VERSION,
            "core_namespace": core_ns,
            "profiles": profiles,
        }

    try:
        with open(path, encoding="utf-8") as f:
            if path.suffix.lower() in (".yaml", ".yml"):
                import yaml  # type: ignore

                data = yaml.safe_load(f) or {}
            else:
                data = json.load(f)
        if not isinstance(data, dict) or "profiles" not in data:
            raise ValueError("invalid mapping config shape")
        return data
    except Exception as exc:
        logger.error("[SSB] failed to load %s: %s — using embedded defaults", path, exc)

    core_ns = os.getenv("NASP_FREE5GC_NAMESPACE", "ns-1274485")
    transport_ns = os.getenv("SSB_TRANSPORT_NAMESPACE", os.getenv("E2E_TRANSPORT_NAMESPACE", "nasp-transport"))
    ran_ns = os.getenv("SSB_RAN_NAMESPACE", os.getenv("E2E_RAN_NAMESPACE", "ueransim"))
    refs = _service_refs(core_ns, transport_ns, ran_ns)
    profiles: Dict[str, Dict[str, Any]] = {}
    for key, base in _DEFAULT_PROFILES.items():
        norm = "URLLC" if key == "URLLC" else ("mMTC" if key == "MMTC" else "eMBB")
        profiles[norm] = {**base, **refs}
    return {
        "mapping_version": MAPPING_VERSION,
        "core_namespace": core_ns,
        "profiles": profiles,
    }


def resolve_slice_service_binding(
    *,
    service_profile: Optional[str],
    nsi_id: Optional[str] = None,
    nest_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    override_nssai: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Resolve SSOT slice service binding para um NSI. Retorna dict serializável (annotation/response).
    override_nssai: se caller já enviou nssai explícito, preserva sst/sd quando válidos.
    """
    cfg = load_mapping_config()
    norm = _normalize_profile(service_profile)
    profiles = cfg.get("profiles") or {}
    profile_row = profiles.get(norm) or profiles.get(norm.upper()) or profiles.get("eMBB") or {}

    sst = int(profile_row.get("sst", 1))
    sd = str(profile_row.get("sd", "000002"))
    dnn = str(profile_row.get("dnn", "embb"))

    if isinstance(override_nssai, dict):
        if override_nssai.get("sst") is not None:
            sst = int(override_nssai["sst"])
        if override_nssai.get("sd"):
            sd = str(override_nssai["sd"]).replace("0x", "").upper().zfill(6)[:6]

    resolved_nest = nest_id or nsi_id

    binding: Dict[str, Any] = {
        "mapping_version": cfg.get("mapping_version", MAPPING_VERSION),
        "binding_phase": BINDING_PHASE,
        "nest_id": resolved_nest,
        "nsi_id": nsi_id,
        "tenant_id": tenant_id or "default",
        "slice_type": profile_row.get("slice_type", norm),
        "sst": sst,
        "sd": sd,
        "dnn": dnn,
        "nssai": {"sst": sst, "sd": sd},
        "nssf_ref": profile_row.get("nssf_ref"),
        "amf_ref": profile_row.get("amf_ref"),
        "smf_ref": profile_row.get("smf_ref"),
        "upf_ref": profile_row.get("upf_ref"),
        "ran_ref": profile_row.get("ran_ref"),
        "transport_ref": profile_row.get("transport_ref"),
        "nssi_domain_refs": {
            "ran": profile_row.get("ran_ref"),
            "transport": profile_row.get("transport_ref"),
            "core": profile_row.get("amf_ref"),
        },
        "integration_flags": {
            "nssf_integrated": False,
            "amf_integrated": False,
            "smf_integrated": False,
            "upf_integrated": False,
            "ran_integrated": False,
            "onos_integrated": False,
        },
    }
    return binding


def enrich_nsi_spec(nsi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriquece nsi_spec in-place com nssai SSOT e campo _sliceServiceBinding (interno ao adapter).
    No-op quando SLICE_SERVICE_BINDING_ENABLED=false.
    """
    if not slice_service_binding_enabled():
        return nsi_spec

    binding = resolve_slice_service_binding(
        service_profile=nsi_spec.get("serviceProfile") or nsi_spec.get("service_type"),
        nsi_id=nsi_spec.get("nsiId"),
        nest_id=nsi_spec.get("nestId") or nsi_spec.get("nest_id"),
        tenant_id=nsi_spec.get("tenantId") or nsi_spec.get("tenant_id"),
        override_nssai=nsi_spec.get("nssai"),
    )
    nsi_spec["nssai"] = dict(binding["nssai"])
    nsi_spec["_sliceServiceBinding"] = binding
    return nsi_spec


def mapping_annotation_value(binding: Dict[str, Any]) -> str:
    return json.dumps(binding, separators=(",", ":"), sort_keys=True)


def parse_mapping_annotation(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
