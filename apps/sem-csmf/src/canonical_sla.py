"""
GSMA / TriSLA FASE 2 — canonicalização aditiva do pedido SLA (SEM-CSMF).

Função pura: não altera thresholds, pesos nem contratos legados.
O envelope legado (template_id + form_values) é preservado em `legacy_input`.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, Optional


def _parse_latency_ms(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*ms$", s, re.I)
    if m:
        return float(m.group(1))
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)$", s)
    if m:
        return float(m.group(1))
    return None


def _parse_throughput_mbps(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*mbps$", s, re.I)
    if m:
        return float(m.group(1))
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*gbps$", s, re.I)
    if m:
        return float(m.group(1)) * 1000.0
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)$", s)
    if m:
        return float(m.group(1))
    return None


def _coerce_float(val: Any) -> Optional[float]:
    if val is None or isinstance(val, bool):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _first(d: Dict[str, Any], keys: tuple[str, ...]) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _looks_native_canonical(d: Any) -> bool:
    if not isinstance(d, dict):
        return False
    if "slice_service_type" not in d:
        return False
    return (
        isinstance(d.get("service_requirements"), dict)
        and isinstance(d.get("semantic_context"), dict)
        and isinstance(d.get("legacy_input"), dict)
    )


def _empty_service_requirements() -> Dict[str, Any]:
    return {
        "latency_ms": None,
        "throughput_mbps": None,
        "availability": None,
        "device_density": None,
        "mobility_support": None,
    }


def _empty_semantic_context() -> Dict[str, Any]:
    return {
        "service_description": None,
        "business_criticality": None,
        "security_profile": None,
        "service_continuity": None,
        "edge_processing": None,
    }


def _normalize_top_level(src: Dict[str, Any]) -> Dict[str, Any]:
    """Garante chaves do contrato FASE 2 sem sobrescrever valores já canónicos."""
    out = copy.deepcopy(src)
    out.setdefault("slice_service_type", None)
    out.setdefault("sst", None)
    out.setdefault("sd", None)
    sr = out.get("service_requirements")
    if not isinstance(sr, dict):
        sr = {}
    base = _empty_service_requirements()
    base.update(sr)
    out["service_requirements"] = base
    sc = out.get("semantic_context")
    if not isinstance(sc, dict):
        sc = {}
    sb = _empty_semantic_context()
    sb.update(sc)
    out["semantic_context"] = sb
    li = out.get("legacy_input")
    if not isinstance(li, dict):
        li = {}
    out["legacy_input"] = {
        "template_id": li.get("template_id"),
        "form_values": li.get("form_values") if isinstance(li.get("form_values"), dict) else {},
    }
    return out


def _build_legacy_input(sla: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    tid = _first(sla, ("template_id",)) or _first(payload, ("template_id",))
    nested_fv = sla.get("form_values")
    if isinstance(nested_fv, dict):
        fv = copy.deepcopy(nested_fv)
    else:
        fv = {k: copy.deepcopy(v) for k, v in sla.items() if k != "template_id"}
    return {"template_id": tid, "form_values": fv}


def _derive_service_requirements(sla: Dict[str, Any]) -> Dict[str, Any]:
    lat = _parse_latency_ms(
        _first(
            sla,
            (
                "latency_ms",
                "latency",
                "latencia_maxima_ms",
                "max_latency_ms",
            ),
        )
    )
    tp = _parse_throughput_mbps(
        _first(
            sla,
            (
                "throughput_mbps",
                "throughput",
                "bandwidth",
                "bandwidth_mbps",
            ),
        )
    )
    avail = _coerce_float(
        _first(
            sla,
            (
                "availability",
                "availability_target",
                "disponibilidade_percent",
                "confiabilidade_percent",
            ),
        )
    )
    if avail is None:
        avail = _coerce_float(sla.get("reliability"))
    dev = _first(sla, ("device_density", "expected_devices", "device_count"))
    dev_n = _coerce_float(dev)
    if dev_n is not None and dev_n == int(dev_n):
        dev_out: Any = int(dev_n)
    else:
        dev_out = dev_n if dev_n is not None else dev

    mob = _first(sla, ("mobility_support", "mobility_profile", "mobility"))
    if mob is not None and not isinstance(mob, str):
        mob = str(mob)

    return {
        "latency_ms": lat,
        "throughput_mbps": tp,
        "availability": avail,
        "device_density": dev_out,
        "mobility_support": mob,
    }


def _derive_semantic_context(sla: Dict[str, Any]) -> Dict[str, Any]:
    desc = _first(sla, ("service_description", "intent_summary", "original_text"))
    crit = _first(
        sla,
        ("business_criticality", "priority", "business_priority", "criticality"),
    )
    if crit is not None and not isinstance(crit, str):
        crit = str(crit)
    sec = _first(sla, ("security_profile", "security_level", "security"))
    if sec is not None and not isinstance(sec, str):
        sec = str(sec)
    cont = _first(
        sla,
        ("service_continuity", "continuity", "continuity_requirement"),
    )
    if cont is not None and not isinstance(cont, str):
        cont = str(cont)
    edge = _first(
        sla,
        ("edge_processing", "edge_computing", "edge_requirement"),
    )
    if edge is not None and not isinstance(edge, str):
        edge = str(edge)
    return {
        "service_description": desc if isinstance(desc, str) else (str(desc) if desc is not None else None),
        "business_criticality": crit,
        "security_profile": sec,
        "service_continuity": cont,
        "edge_processing": edge,
    }


def _sla_plane(sla: Dict[str, Any]) -> Dict[str, Any]:
    """Une `form_values` ao plano para derivar métricas (compatível com nest do Portal)."""
    nested = sla.get("form_values")
    if isinstance(nested, dict):
        plane = {k: v for k, v in sla.items() if k != "form_values"}
        plane = {**plane, **nested}
        return plane
    return sla


def canonicalize_sla_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produz visão canónica aditiva do pedido SLA.

    `payload` típico (POST /api/v1/intents):
      - service_type: "eMBB" | "URLLC" | "mMTC"
      - sla_requirements: dict (legado plano ou com form_values aninhado)
      - metadata (opcional): pode conter sst/sd
    """
    if not isinstance(payload, dict):
        payload = {}

    if _looks_native_canonical(payload):
        return _normalize_top_level(payload)

    sla = payload.get("sla_requirements")
    if isinstance(sla, dict) and _looks_native_canonical(sla):
        merged = dict(sla)
        if payload.get("service_type") and not merged.get("slice_service_type"):
            merged["slice_service_type"] = payload.get("service_type")
        return _normalize_top_level(merged)

    if not isinstance(sla, dict):
        sla = {}

    plane = _sla_plane(sla)

    meta = payload.get("metadata")
    if not isinstance(meta, dict):
        meta = {}

    slice_st = (
        payload.get("service_type")
        or payload.get("slice_service_type")
        or plane.get("slice_service_type")
        or plane.get("sla_type")
        or plane.get("type")
    )
    sst = _first(meta, ("sst", "slice_sst")) or plane.get("sst")
    sd = _first(meta, ("sd", "slice_sd")) or plane.get("sd")
    if sst is not None and not isinstance(sst, (int, float)):
        try:
            sst = int(sst)
        except (TypeError, ValueError):
            sst = None
    if sd is not None and not isinstance(sd, str):
        sd = str(sd)

    svc_req = _derive_service_requirements(plane)
    sem_ctx = _derive_semantic_context(plane)
    legacy = _build_legacy_input(sla, payload)

    return {
        "slice_service_type": slice_st,
        "sst": sst,
        "sd": sd,
        "service_requirements": svc_req,
        "semantic_context": sem_ctx,
        "legacy_input": legacy,
    }
