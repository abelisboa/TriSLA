"""SLA-Agent ingest success statuses for portal lifecycle composition (Sprint 5N3)."""
from __future__ import annotations

from typing import FrozenSet

SLA_AGENT_SUCCESS_STATUSES: FrozenSet[str] = frozenset(
    {"OK", "OK_WITH_SLO", "OK_WITH_ASSURANCE"}
)


def is_sla_agent_ingest_success(status: str | None) -> bool:
    return bool(status) and status in SLA_AGENT_SUCCESS_STATUSES
