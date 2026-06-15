"""Optional hooks from runtime assurance into actuation audit (no domain mutation)."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from actuation.models import ActuationRequestIn, RiskLevel
from actuation.service import submit_actuation_request


def audit_enabled() -> bool:
    return os.getenv("CLOSED_LOOP_ACTUATION_AUDIT_ENABLED", "false").lower() == "true"


def maybe_audit_violation(
    intent_id: str,
    nsi_id: str,
    assurance_payload: Dict[str, Any],
    decision_reference: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if not audit_enabled():
        return None
    state = (assurance_payload or {}).get("state") or (assurance_payload or {}).get("runtime_assurance_status")
    if str(state).upper() not in ("VIOLATED", "4", "RUNTIME_VIOLATED"):
        return None
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id=intent_id or "unknown",
            nsi_id=nsi_id or "unknown",
            action_type="ACT-ASSUR-004",
            action_domain="ASSUR",
            risk_level=RiskLevel.SAFE,
            requested_by="runtime_assurance",
            decision_reference=decision_reference,
            correlation_reference=str(assurance_payload.get("governance_event_id") or ""),
            metadata={"assurance_state": str(state)},
        )
    )
    return resp.model_dump(mode="json")
