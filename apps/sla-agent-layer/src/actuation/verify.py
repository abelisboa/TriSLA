"""O8C W2A verify hook — ACT-ASSUR-002 registration only (no assurance mutation)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

VERIFY_ACTION = "ACT-ASSUR-002"
VERIFY_ENDPOINT = "/api/v1/agent/revalidate-telemetry"


def build_verify_audit_entry(
    intent_id: str,
    nsi_id: str,
    request_id: str,
    *,
    passed: bool,
    verified_by: str,
) -> Dict[str, Any]:
    """Register verify attempt metadata without altering assurance logic."""
    return {
        "verify_action": VERIFY_ACTION,
        "verify_endpoint": VERIFY_ENDPOINT,
        "verify_mode": "register_only",
        "intent_id": intent_id,
        "nsi_id": nsi_id,
        "request_id": request_id,
        "verify_result": "PASSED" if passed else "FAILED",
        "verified_by": verified_by,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "assurance_mutated": False,
    }
