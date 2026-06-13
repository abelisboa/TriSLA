"""Admission compliance propagation — read existing decision metadata only (portal view)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.services.sla_explainability import enrich_runtime_assurance_explainability


def _normalize_pct(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    v = float(value)
    if v > 1.0:
        return round(v, 4)
    return round(v * 100.0, 2)


def admission_compliance_from_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[float]:
    """
    Extract admission-time compliance (0–1) from decision metadata already on the payload.
    Mirrors Decision Engine field precedence; does not compute new scores.
    """
    if not isinstance(metadata, dict):
        return None
    snap = metadata.get("decision_snapshot")
    if isinstance(snap, dict):
        sc = snap.get("sla_compliance")
        if isinstance(sc, (int, float)):
            v = float(sc)
            return v / 100.0 if v > 1.0 else v
    ds = metadata.get("decision_score")
    if isinstance(ds, (int, float)):
        return float(ds)
    final = (metadata.get("decision_snapshot") or {}).get("final_score")
    if isinstance(final, (int, float)):
        return float(final)
    risk = metadata.get("ran_aware_final_risk")
    if isinstance(risk, (int, float)):
        return max(0.0, 1.0 - float(risk))
    return None


def wire_admission_compliance_fields(metadata: Dict[str, Any]) -> None:
    """
    Propagate admission/runtime compliance split onto metadata and runtime_assurance.
    Uses existing decision metadata and sla_compliance from runtime assurance only.
    """
    if not isinstance(metadata, dict):
        return

    admission = admission_compliance_from_metadata(metadata)
    if admission is not None:
        metadata["admission_compliance"] = admission
        metadata["admission_compliance_percent"] = _normalize_pct(admission)

    ra = metadata.get("runtime_assurance")
    if not isinstance(ra, dict):
        ra = {}
        metadata["runtime_assurance"] = ra

    runtime = ra.get("sla_compliance")
    if isinstance(runtime, (int, float)):
        ra["runtime_compliance"] = float(runtime)
        ra["runtime_compliance_percent"] = _normalize_pct(float(runtime))

    if admission is not None:
        ra["admission_compliance"] = admission
        ra["admission_compliance_percent"] = _normalize_pct(admission)


def enrich_status_runtime_assurance(
    metadata: Optional[Dict[str, Any]],
    runtime_assurance: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Merge admission/runtime compliance labels into status runtime_assurance."""
    if not isinstance(runtime_assurance, dict):
        return runtime_assurance
    merged = dict(runtime_assurance)
    md = metadata if isinstance(metadata, dict) else {}

    admission = admission_compliance_from_metadata(md)
    if admission is None and isinstance(md.get("admission_compliance"), (int, float)):
        admission = float(md["admission_compliance"])
    if admission is not None:
        merged["admission_compliance"] = admission
        merged["admission_compliance_percent"] = _normalize_pct(admission)

    runtime = merged.get("sla_compliance")
    if isinstance(runtime, (int, float)):
        merged["runtime_compliance"] = float(runtime)
        merged["runtime_compliance_percent"] = _normalize_pct(float(runtime))

    return enrich_runtime_assurance_explainability(merged)
