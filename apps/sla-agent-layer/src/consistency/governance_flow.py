"""Governance event vs blockchain registration clarity."""
from __future__ import annotations

from typing import Any, Dict, Optional


def build_governance_clarity(
    *,
    admission_decision: Optional[str],
    bc_status: Optional[str] = None,
    governance_event_id: Optional[str] = None,
) -> Dict[str, Any]:
    decision = (admission_decision or "").strip().upper()
    is_accept = decision in ("AC", "ACCEPT", "")
    bc_committed = (bc_status or "").upper() in ("COMMITTED", "CONFIRMED", "REGISTERED")

    governance_event: Dict[str, Any] = {
        "label": "Governance Event",
        "status": "Recorded",
        "event_type": "Decision Recorded",
        "governance_event_id": governance_event_id,
    }

    if is_accept and bc_committed:
        blockchain = {
            "label": "Blockchain Registration",
            "status": "Executed",
            "executed": True,
            "bc_status": bc_status,
        }
    elif is_accept:
        blockchain = {
            "label": "Blockchain Registration",
            "status": "Pending or failed",
            "executed": False,
            "bc_status": bc_status or "NOT_COMMITTED",
            "reason": "ACCEPT without on-chain commit",
        }
    else:
        blockchain = {
            "label": "Blockchain Registration",
            "status": "Not executed",
            "executed": False,
            "reason": f"Decision {admission_decision or 'UNKNOWN'}",
        }

    return {
        "governance_event": governance_event,
        "blockchain_registration": blockchain,
    }
