"""Resolve telemetry_snapshot for GET /sla/status (Sprint 5M2)."""
from __future__ import annotations

from typing import Any, Dict, Optional


def resolve_status_telemetry_snapshot(
    sem_result: Dict[str, Any],
    collected_snapshot: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Prefer SEM-persisted snapshot; otherwise use live collect output."""
    md = sem_result.get("metadata")
    if isinstance(md, dict):
        ts = md.get("telemetry_snapshot")
        if isinstance(ts, dict) and ts:
            return ts
    if isinstance(collected_snapshot, dict) and collected_snapshot:
        return collected_snapshot
    return None
