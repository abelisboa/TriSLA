"""Assurance guard when revalidate telemetry is incomplete (Sprint 5N3)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


ASSURANCE_INCOMPLETE = "INCOMPLETE"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_incomplete_assurance(
    *,
    intent_id: Optional[str] = None,
    slice_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Return INCOMPLETE assurance — never COMPLIANT/WARNING/AT_RISK/VIOLATED on null telemetry."""
    return {
        "state": ASSURANCE_INCOMPLETE,
        "assurance_state": ASSURANCE_INCOMPLETE,
        "violations": [],
        "warnings": ["telemetry.incomplete"],
        "drift_detected": False,
        "drift_indicators": [],
        "recommendation": "Telemetry incomplete; revalidation required before assurance evaluation.",
        "last_evaluation": _utc_now(),
        "slice_type": slice_type,
        "sla_compliance": None,
        "bottleneck_domain": None,
        "intent_id": intent_id,
    }
