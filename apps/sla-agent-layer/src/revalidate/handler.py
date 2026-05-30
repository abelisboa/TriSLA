"""
Handler de /api/v1/agent/revalidate-telemetry (sla-agent path).

Lógica idêntica à do endpoint /api/v1/sla/revalidate-telemetry no Portal Backend
(`apps/portal-backend/src/routers/sla.py:874`). Diferenças mínimas e marcadas:

1. Adiciona `metadata.processed_by_sla_agent = True` para evidência de delegação
   (não substitui nenhum campo existente).
2. Preserva todos os campos do contrato JSON do backend.
3. Não chama NASP, BC, Decision Engine ou Kafka.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from .collector import collect_domain_metrics_async
from .drift import _minimal_telemetry_drift, _snapshot_missing_fields
from .remediation import _build_remediation_evidence_p2
from .schemas import SLARevalidateTelemetryRequest, SLARevalidateTelemetryResponse

logger = logging.getLogger(__name__)


async def revalidate_telemetry_handler(
    request: SLARevalidateTelemetryRequest,
) -> SLARevalidateTelemetryResponse:
    intent_id = request.intent_id
    trace = request.temporal_intent_trace if isinstance(request.temporal_intent_trace, dict) else None
    temporal_correlation: Dict[str, Any] = {
        "intent_id_requested": intent_id,
        "temporal_intent_trace_present": trace is not None,
    }
    if trace:
        tid = trace.get("intent_id")
        temporal_correlation["intent_id_match"] = tid is not None and str(tid) == intent_id
        temporal_correlation["trace_execution_id"] = trace.get("execution_id")
        temporal_correlation["trace_temporal_version"] = trace.get("temporal_trace_version")
        ts_tr = trace.get("timestamps_utc")
        if isinstance(ts_tr, dict):
            temporal_correlation["prior_telemetry_post_at"] = ts_tr.get("telemetry_post_snapshot")
    if request.correlation_execution_id:
        cex = str(request.correlation_execution_id).strip()
        temporal_correlation["correlation_execution_id"] = cex
        tex = trace.get("execution_id") if trace else None
        if tex is not None:
            temporal_correlation["execution_id_match"] = str(tex) == cex
        else:
            temporal_correlation["execution_id_match"] = None

    execution_id_rev = str(uuid.uuid4())
    collected_at = datetime.now(timezone.utc).isoformat()
    telemetry_snapshot_atual, _tel_ms = await collect_domain_metrics_async(
        execution_id_rev,
        collected_at,
    )

    ref = request.reference_telemetry_snapshot
    if isinstance(ref, dict) and ref:
        drift_summary: Dict[str, Any] = {
            "compared": True,
            **_minimal_telemetry_drift(ref, telemetry_snapshot_atual),
        }
    else:
        drift_summary = {
            "compared": False,
            "reason": "no_reference_telemetry_snapshot",
            "note": "Opcional: enviar metadata.telemetry_snapshot do submit anterior para deltas numéricos.",
        }

    gaps = _snapshot_missing_fields(telemetry_snapshot_atual)
    revalidation_status = "OK" if len(gaps) == 0 else "INCOMPLETE"

    timestamps_utc = {
        "revalidation_collected": telemetry_snapshot_atual.get("timestamp") or collected_at,
        "revalidation_requested_wall": collected_at,
        "prior_telemetry_post_from_trace": temporal_correlation.get("prior_telemetry_post_at"),
    }

    remediation = _build_remediation_evidence_p2(
        drift_summary=drift_summary,
        reference=ref if isinstance(ref, dict) else None,
        current=telemetry_snapshot_atual,
        revalidation_status=revalidation_status,
    )
    metadata_out: Dict[str, Any] = {
        "remediation_evidence": remediation,
        "processed_by_sla_agent": True,
    }

    try:
        from runtime_slo_evaluator import evaluate_runtime_assurance
        from runtime_assurance_store import get_previous_state, set_state

        assurance_result = evaluate_runtime_assurance(
            telemetry_snapshot=telemetry_snapshot_atual,
            sla_requirements=request.sla_requirements
            if isinstance(getattr(request, "sla_requirements", None), dict)
            else None,
            slice_type=str(getattr(request, "slice_type", None) or "EMBB"),
            reference_telemetry_snapshot=ref if isinstance(ref, dict) else None,
            previous_state=get_previous_state(intent_id),
            intent_id=intent_id,
            nest_id=getattr(request, "nest_id", None),
        )
        metadata_out["runtime_assurance"] = assurance_result.get("runtime_assurance")
        metadata_out["runtime_assurance_evaluated"] = True
        new_state = (assurance_result.get("runtime_assurance") or {}).get("state")
        if new_state:
            set_state(intent_id, str(new_state))
        if assurance_result.get("runtime_governance_event"):
            metadata_out["runtime_governance_event"] = assurance_result[
                "runtime_governance_event"
            ]
    except Exception as exc:
        logger.warning("[SLA_AGENT_REVALIDATE] runtime_assurance skipped: %s", exc)
        metadata_out["runtime_assurance_evaluated"] = False

    logger.info(
        "[SLA_AGENT_REVALIDATE] intent_id=%s execution_id_rev=%s status=%s",
        intent_id,
        execution_id_rev,
        revalidation_status,
    )

    return SLARevalidateTelemetryResponse(
        intent_id=intent_id,
        execution_id_revalidation=execution_id_rev,
        telemetry_snapshot_atual=telemetry_snapshot_atual,
        timestamps_utc=timestamps_utc,
        drift_summary=drift_summary,
        revalidation_status=revalidation_status,
        temporal_correlation=temporal_correlation,
        metadata=metadata_out,
    )
