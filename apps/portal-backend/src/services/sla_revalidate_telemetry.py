"""Revalidate telemetry helpers — local collect fallback (Sprint 5N3)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.schemas.sla import SLARevalidateTelemetryRequest, SLARevalidateTelemetryResponse


def snapshot_field_gaps(snapshot: dict) -> list[str]:
    """Missing required telemetry fields (same rules as sla router)."""
    missing: list[str] = []
    if not isinstance(snapshot, dict):
        return ["snapshot"]
    ran = snapshot.get("ran") if isinstance(snapshot.get("ran"), dict) else {}
    tr = snapshot.get("transport") if isinstance(snapshot.get("transport"), dict) else {}
    co = snapshot.get("core") if isinstance(snapshot.get("core"), dict) else {}

    if ran.get("prb_utilization") is None:
        missing.append("ran.prb_utilization")
    if ran.get("latency") is None and ran.get("latency_ms") is None:
        missing.append("ran.latency")
    if tr.get("rtt") is None and tr.get("rtt_ms") is None:
        missing.append("transport.rtt")
    if tr.get("jitter") is None and tr.get("jitter_ms") is None:
        missing.append("transport.jitter")
    cpu = co.get("cpu")
    if cpu is None:
        cpu = co.get("cpu_utilization")
    mem = co.get("memory")
    if mem is None:
        mem = co.get("memory_utilization")
    if mem is None:
        mem = co.get("memory_bytes")
    if cpu is None:
        missing.append("core.cpu")
    if mem is None:
        missing.append("core.memory")
    return missing


def snapshot_is_complete(snapshot: Optional[dict]) -> bool:
    if not isinstance(snapshot, dict):
        return False
    return len(snapshot_field_gaps(snapshot)) == 0


def snapshot_has_any_value(snapshot: Optional[dict]) -> bool:
    if not isinstance(snapshot, dict):
        return False
    return len(snapshot_field_gaps(snapshot)) < 6


def count_populated_fields(snapshot: Optional[dict]) -> int:
    if not isinstance(snapshot, dict):
        return 0
    return 6 - len(snapshot_field_gaps(snapshot))


async def enrich_revalidate_with_local_collect(
    request: SLARevalidateTelemetryRequest,
    response: SLARevalidateTelemetryResponse,
    *,
    collect_fn,
    drift_fn,
    remediation_fn,
) -> SLARevalidateTelemetryResponse:
    """
    When delegated SLA-Agent collect is incomplete, re-collect via portal-backend
    collector (same env/PromQL as submit pipeline).
    """
    atual = response.telemetry_snapshot_atual
    if snapshot_is_complete(atual if isinstance(atual, dict) else None):
        return response

    execution_id_rev = response.execution_id_revalidation or ""
    from datetime import datetime, timezone

    collected_at = datetime.now(timezone.utc).isoformat()
    local_snap, _tel_ms = await collect_fn(execution_id_rev or "revalidate-local", collected_at)

    if count_populated_fields(local_snap) <= count_populated_fields(
        atual if isinstance(atual, dict) else None
    ):
        return response

    ref = request.reference_telemetry_snapshot
    if isinstance(ref, dict) and ref:
        drift_summary: Dict[str, Any] = {
            "compared": True,
            **drift_fn(ref, local_snap),
        }
    else:
        drift_summary = dict(response.drift_summary or {})
        drift_summary.setdefault("compared", False)
        drift_summary.setdefault("reason", "no_reference_telemetry_snapshot")

    gaps = snapshot_field_gaps(local_snap)
    revalidation_status = "OK" if len(gaps) == 0 else "INCOMPLETE"

    meta = dict(response.metadata) if isinstance(response.metadata, dict) else {}
    meta["local_collect_fallback"] = True
    meta["local_collect_populated_fields"] = count_populated_fields(local_snap)
    meta.pop("runtime_assurance", None)
    meta.pop("runtime_governance_event", None)
    meta["runtime_assurance_evaluated"] = False

    remediation = remediation_fn(
        drift_summary=drift_summary,
        reference=ref if isinstance(ref, dict) else None,
        current=local_snap,
        revalidation_status=revalidation_status,
    )
    meta["remediation_evidence"] = remediation

    return response.model_copy(
        update={
            "telemetry_snapshot_atual": local_snap,
            "drift_summary": drift_summary,
            "revalidation_status": revalidation_status,
            "metadata": meta,
        }
    )
