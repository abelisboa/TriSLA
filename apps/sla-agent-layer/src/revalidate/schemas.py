"""
Schemas para /api/v1/agent/revalidate-telemetry no SLA-Agent.

Cópia 1:1 de apps/portal-backend/src/schemas/sla.py (classes SLARevalidateTelemetry*).
Mantida idêntica para garantir zero-diff de contrato JSON em FASE 2.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any


class SLARevalidateTelemetryRequest(BaseModel):
    """P1: revalidação temporal — só telemetria; sem NASP/BC/decision."""

    intent_id: str
    temporal_intent_trace: Optional[Dict[str, Any]] = None
    correlation_execution_id: Optional[str] = None
    reference_telemetry_snapshot: Optional[Dict[str, Any]] = None
    sla_requirements: Optional[Dict[str, Any]] = None
    slice_type: Optional[str] = None
    nest_id: Optional[str] = None

    @field_validator("intent_id")
    @classmethod
    def _strip_intent(cls, v: str) -> str:
        if not v or not str(v).strip():
            raise ValueError("intent_id obrigatório")
        return str(v).strip()


class SLARevalidateTelemetryResponse(BaseModel):
    """Resposta mínima P1 — alinhado ao plano temporal."""

    intent_id: str
    execution_id_revalidation: str
    telemetry_snapshot_atual: Dict[str, Any]
    timestamps_utc: Dict[str, Any]
    drift_summary: Dict[str, Any]
    revalidation_status: str  # OK | INCOMPLETE
    temporal_correlation: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
