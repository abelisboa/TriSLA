"""Resolve admission decision from SEM intent payload (runtime gating SSOT)."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

_VALID = frozenset({"ACCEPT", "REJECT", "RENEGOTIATE"})
_ACTION_MAP = {
    "AC": "ACCEPT",
    "ACCEPT": "ACCEPT",
    "REJ": "REJECT",
    "REJECT": "REJECT",
    "RENEG": "RENEGOTIATE",
    "RENEGOTIATE": "RENEGOTIATE",
}


def _normalize_decision(value: Any) -> Optional[str]:
    if value is None:
        return None
    key = str(value).strip().upper()
    if key in _VALID:
        return key
    return _ACTION_MAP.get(key)


def resolve_admission_decision(sem_result: Dict[str, Any]) -> str:
    """
    Official admission decision for lifecycle gating.

    Priority:
    1. Persisted metadata.final_decision / decision / threshold_decision
    2. metadata.decision_band (when mapped)
    3. lifecycle markers (DECIDED_REJECT / DECIDED_RENEGOTIATE in sla_lifecycle)
    4. UNKNOWN (never infer from session or operational status)
    """
    md = sem_result.get("metadata") if isinstance(sem_result.get("metadata"), dict) else {}

    for key in ("final_decision", "decision", "threshold_decision", "admission_decision"):
        resolved = _normalize_decision(md.get(key))
        if resolved:
            return resolved

    band = _normalize_decision(md.get("decision_band"))
    if band:
        return band

    lifecycle = md.get("sla_lifecycle") if isinstance(md.get("sla_lifecycle"), dict) else {}
    if lifecycle.get("DECIDED_REJECT"):
        return "REJECT"
    if lifecycle.get("DECIDED_RENEGOTIATE"):
        return "RENEGOTIATE"
    if lifecycle.get("DECIDED_ACCEPT"):
        return "ACCEPT"

    return "UNKNOWN"


def resolve_runtime_lifecycle_enabled(
    sem_result: Dict[str, Any],
    admission_decision: Optional[str] = None,
) -> bool:
    """Runtime lifecycle is active only after ACCEPT."""
    decision = admission_decision or resolve_admission_decision(sem_result)
    return decision == "ACCEPT"


def admission_telemetry_snapshot(sem_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """T0 telemetry persisted at admission (never live-collected for non-ACCEPT)."""
    md = sem_result.get("metadata") if isinstance(sem_result.get("metadata"), dict) else {}
    ts = md.get("telemetry_snapshot")
    return ts if isinstance(ts, dict) and ts else None


def resolve_admission_context(
    sem_result: Dict[str, Any],
) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
    decision = resolve_admission_decision(sem_result)
    enabled = resolve_runtime_lifecycle_enabled(sem_result, decision)
    snap = admission_telemetry_snapshot(sem_result)
    return decision, enabled, snap
