"""Unified operational status from admission decision."""
from __future__ import annotations

from typing import Optional


def derive_operational_status(admission_decision: Optional[str]) -> str:
    """
    Map admission decision to operational status.

    ACCEPT → ACTIVE
    RENEGOTIATE → PENDING_RENEGOTIATION
    REJECT → TERMINATED
    """
    if not admission_decision:
        return "ACTIVE"
    d = str(admission_decision).strip().upper()
    if d in ("AC", "ACCEPT"):
        return "ACTIVE"
    if d in ("RENEG", "RENEGOTIATE"):
        return "PENDING_RENEGOTIATION"
    if d in ("REJ", "REJECT"):
        return "TERMINATED"
    return "ACTIVE"


def assurance_state_for_decision(
    admission_decision: Optional[str],
    compliance_state: str,
) -> str:
    """
  When admission is not ACCEPT, operational status overrides generic ACTIVE assurance.
    """
    op = derive_operational_status(admission_decision)
    if op == "PENDING_RENEGOTIATION":
        return "PENDING_RENEGOTIATION"
    if op == "TERMINATED":
        return "TERMINATED"
    return compliance_state
