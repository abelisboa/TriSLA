"""Resolve telemetry_snapshot for GET /sla/status (Sprint 5M2)."""
from __future__ import annotations

from typing import Any, Dict, Optional


def resolve_status_telemetry_snapshot(
    sem_result: Dict[str, Any],
    collected_snapshot: Optional[Dict[str, Any]],
    *,
    runtime_lifecycle_enabled: bool = True,
) -> Optional[Dict[str, Any]]:
    """Resolve telemetry for GET /sla/status.

    When runtime lifecycle is disabled (non-ACCEPT), return admission snapshot only.
    When enabled, prefer live collected metrics; fall back to SEM-persisted snapshot.
    """
    md = sem_result.get("metadata")
    sem_ts: Optional[Dict[str, Any]] = None
    if isinstance(md, dict):
        ts = md.get("telemetry_snapshot")
        if isinstance(ts, dict) and ts:
            sem_ts = ts

    if not runtime_lifecycle_enabled:
        return sem_ts

    if isinstance(collected_snapshot, dict) and collected_snapshot:
        return collected_snapshot
    return sem_ts
