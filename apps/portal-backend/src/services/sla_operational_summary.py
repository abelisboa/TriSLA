"""Operational summary for GET /sla/status (Sprint 5N — presentation layer only)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.services.admission_decision import resolve_admission_decision


def build_operational_summary(sem_result: Dict[str, Any]) -> Dict[str, Any]:
    """Derive operator-facing labels from existing SEM intent payload."""
    metadata = sem_result.get("metadata") if isinstance(sem_result.get("metadata"), dict) else {}
    status = str(sem_result.get("status") or metadata.get("status") or "unknown")
    nest_id = sem_result.get("nest_id") or metadata.get("nest_id")
    admission_decision = resolve_admission_decision(sem_result)

    lifecycle_label = "In Operation" if status.upper() == "ACTIVE" else status.replace("_", " ")

    ml_confidence = metadata.get("ml_confidence")
    if ml_confidence is None:
        ml_confidence = metadata.get("confidence_score")

    return {
        "lifecycle_status": status,
        "lifecycle_status_label": lifecycle_label,
        "admission_decision": admission_decision,
        "semantic_validation": "Passed" if admission_decision == "ACCEPT" else "Review required",
        "gst_generated": "Yes" if nest_id else "Not available",
        "nest_generated": "Yes" if nest_id else "Not available",
        "semantic_fill": "Applied" if metadata.get("telemetry_snapshot") else "Not available",
        "ml_confidence": ml_confidence,
        "decision_score": metadata.get("decision_score"),
        "bc_status": metadata.get("bc_status"),
        "tx_hash": metadata.get("tx_hash") or metadata.get("governance_registration_tx_hash"),
        "block_number": metadata.get("block_number")
        or metadata.get("governance_registration_block_number"),
        "governance_event_id": metadata.get("governance_event_id"),
    }
