"""
Semantic SLA requirement resolution — Sprint 5K.

Fill missing KPI fields only. Priority:
  explicit → ontology → GST → NEST → null

Internal traceability via semantic_sources dict (not exposed in public API).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

# KPI fields resolved by this module
SEMANTIC_KPI_FIELDS = (
    "latency",
    "throughput",
    "reliability",
    "availability",
    "coverage",
    "device_density",
    "jitter",
)

# Fallback aligned to apps/sem-csmf/src/ontology/trisla.ttl :SliceType individuals
_ONTOLOGY_FALLBACK: Dict[str, Dict[str, Any]] = {
    "URLLC": {
        "latency": "10ms",
        "throughput": "100Mbps",
        "reliability": 0.99999,
    },
    "eMBB": {
        "latency": "50ms",
        "throughput": "1000Mbps",
        "reliability": 0.99,
    },
    "mMTC": {
        "latency": "1000ms",
        "throughput": "0.1Mbps",
        "reliability": 0.9,
        "device_density": 1000000,
    },
}

_SLICE_INDIVIDUAL = {
    "URLLC": "URLLC_Type",
    "eMBB": "eMBB_Type",
    "mMTC": "mMTC_Type",
}


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _format_latency_ms(ms: float) -> str:
    if ms == int(ms):
        return f"{int(ms)}ms"
    return f"{ms}ms"


def _format_throughput_mbps(mbps: float) -> str:
    if mbps == int(mbps):
        return f"{int(mbps)}Mbps"
    return f"{mbps}Mbps"


def _first_attr(individual: Any, name: str) -> Any:
    val = getattr(individual, name, None)
    if val is None:
        return None
    if isinstance(val, list):
        return val[0] if val else None
    return val


def extract_ontology_kpis(
    slice_type: str,
    ontology_loader: Any = None,
) -> Dict[str, Any]:
    """Read :SliceType KPI literals from OWL or static fallback."""
    kpis: Dict[str, Any] = {}
    individual_name = _SLICE_INDIVIDUAL.get(slice_type)
    if ontology_loader is not None and individual_name:
        try:
            individual = ontology_loader.get_individual(individual_name)
            lat = _first_attr(individual, "hasLatency")
            if lat is not None:
                kpis["latency"] = _format_latency_ms(float(lat))
            tp = _first_attr(individual, "hasThroughput")
            if tp is not None:
                kpis["throughput"] = _format_throughput_mbps(float(tp))
            rel = _first_attr(individual, "hasReliability")
            if rel is not None:
                kpis["reliability"] = float(rel)
            dens = _first_attr(individual, "hasDeviceDensity")
            if dens is not None:
                kpis["device_density"] = int(float(dens))
        except (ValueError, TypeError, AttributeError):
            pass

    fallback = _ONTOLOGY_FALLBACK.get(slice_type, {})
    for key, val in fallback.items():
        kpis.setdefault(key, val)

    if "reliability" in kpis and "availability" not in kpis:
        kpis["availability"] = kpis["reliability"]

    return kpis


def extract_gst_kpis(gst: Dict[str, Any]) -> Dict[str, Any]:
    """Extract KPI candidates from GST template qos/sla."""
    kpis: Dict[str, Any] = {}
    template = gst.get("template") or {}
    qos = template.get("qos") or {}
    sla = template.get("sla") or gst.get("sla_requirements") or {}

    if not _is_missing(sla.get("latency")):
        kpis["latency"] = sla["latency"]
    elif not _is_missing(qos.get("latency")):
        kpis["latency"] = qos["latency"]

    if not _is_missing(sla.get("throughput")):
        kpis["throughput"] = sla["throughput"]
    elif not _is_missing(qos.get("guaranteed_bitrate")):
        kpis["throughput"] = qos["guaranteed_bitrate"]
    elif not _is_missing(qos.get("maximum_bitrate")):
        kpis["throughput"] = qos["maximum_bitrate"]
    elif not _is_missing(qos.get("data_rate")):
        kpis["throughput"] = qos["data_rate"]

    if not _is_missing(sla.get("reliability")):
        kpis["reliability"] = sla["reliability"]
    elif not _is_missing(qos.get("reliability")):
        rel = qos["reliability"]
        try:
            kpis["reliability"] = float(rel)
        except (TypeError, ValueError):
            kpis["reliability"] = rel

    if not _is_missing(sla.get("coverage")):
        kpis["coverage"] = sla["coverage"]

    if not _is_missing(qos.get("device_density")):
        raw = str(qos["device_density"])
        digits = raw.replace("/km²", "").replace("/km2", "").strip()
        try:
            kpis["device_density"] = int(float(digits))
        except ValueError:
            kpis["device_density"] = qos["device_density"]

    if "reliability" in kpis and "availability" not in kpis:
        kpis["availability"] = kpis["reliability"]

    return kpis


def extract_nest_kpis(nest: Any) -> Dict[str, Any]:
    """Extract KPI candidates from primary NEST network slice resources."""
    kpis: Dict[str, Any] = {}
    if nest is None:
        return kpis

    slices = []
    if hasattr(nest, "network_slices"):
        slices = nest.network_slices or []
    elif isinstance(nest, dict):
        slices = nest.get("network_slices") or []

    if not slices:
        return kpis

    primary = slices[0]
    resources = (
        primary.resources
        if hasattr(primary, "resources")
        else (primary.get("resources") if isinstance(primary, dict) else {})
    ) or {}

    if not _is_missing(resources.get("latency")):
        kpis["latency"] = resources["latency"]
    if not _is_missing(resources.get("bandwidth")):
        kpis["throughput"] = resources["bandwidth"]
    if not _is_missing(resources.get("reliability")):
        rel = resources["reliability"]
        try:
            kpis["reliability"] = float(rel)
        except (TypeError, ValueError):
            kpis["reliability"] = rel
    if not _is_missing(resources.get("device_density")):
        raw = str(resources["device_density"])
        digits = raw.replace("/km²", "").replace("/km2", "").strip()
        try:
            kpis["device_density"] = int(float(digits))
        except ValueError:
            kpis["device_density"] = resources["device_density"]

    coverage_area = resources.get("coverageArea") or {}
    if isinstance(coverage_area, dict) and not _is_missing(coverage_area.get("areaType")):
        kpis["coverage"] = coverage_area["areaType"]

    slice_profile = resources.get("sliceProfile") or {}
    if isinstance(slice_profile, dict):
        max_ues = slice_profile.get("maxNumberOfUEs")
        if not _is_missing(max_ues):
            kpis.setdefault("device_density", max_ues)

    qos_chars = resources.get("qosCharacteristics") or {}
    if isinstance(qos_chars, dict):
        pdb = qos_chars.get("packetDelayBudget")
        if not _is_missing(pdb) and "latency" not in kpis:
            kpis["latency"] = _format_latency_ms(float(pdb))
        gbr = qos_chars.get("guaranteedBitRate")
        if not _is_missing(gbr) and "throughput" not in kpis:
            kpis["throughput"] = _format_throughput_mbps(float(gbr))

    if "reliability" in kpis and "availability" not in kpis:
        kpis["availability"] = kpis["reliability"]

    return kpis


def resolve_semantic_value(
    field: str,
    explicit_value: Any,
    ontology_kpis: Dict[str, Any],
    gst_kpis: Dict[str, Any],
    nest_kpis: Dict[str, Any],
) -> Tuple[Any, str]:
    """
    Resolve one KPI field. Returns (value, semantic_source).
    semantic_source ∈ {explicit, ontology, gst, nest, missing}
    """
    if not _is_missing(explicit_value):
        return explicit_value, "explicit"

    for source, bucket in (
        ("ontology", ontology_kpis),
        ("gst", gst_kpis),
        ("nest", nest_kpis),
    ):
        candidate = bucket.get(field)
        if not _is_missing(candidate):
            return candidate, source

    return explicit_value, "missing"


def fill_sla_requirements_semantic(
    sla: Dict[str, Any],
    slice_type: str,
    *,
    ontology_loader: Any = None,
    gst: Optional[Dict[str, Any]] = None,
    nest: Any = None,
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Fill missing SLA requirement fields without overwriting explicit values.

    Returns (filled_sla_dict, semantic_sources_per_field).
    """
    ontology_kpis = extract_ontology_kpis(slice_type, ontology_loader)
    gst_kpis = extract_gst_kpis(gst or {})
    nest_kpis = extract_nest_kpis(nest)

    filled = dict(sla or {})
    sources: Dict[str, str] = {}

    for field in SEMANTIC_KPI_FIELDS:
        value, source = resolve_semantic_value(
            field,
            filled.get(field),
            ontology_kpis,
            gst_kpis,
            nest_kpis,
        )
        if source != "missing":
            filled[field] = value
        sources[field] = source

    return filled, sources


def apply_semantic_fill_to_intent_sla(
    intent_sla_dict: Dict[str, Any],
    slice_type: str,
    *,
    ontology_loader: Any = None,
    gst: Optional[Dict[str, Any]] = None,
    nest: Any = None,
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Convenience wrapper used by main.py interpret/intents paths."""
    return fill_sla_requirements_semantic(
        intent_sla_dict,
        slice_type,
        ontology_loader=ontology_loader,
        gst=gst,
        nest=nest,
    )
