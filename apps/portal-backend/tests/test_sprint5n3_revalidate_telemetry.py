"""Sprint 5N3 — revalidate telemetry fallback tests."""
import pytest

from src.services.sla_revalidate_telemetry import (
    count_populated_fields,
    snapshot_field_gaps,
    snapshot_is_complete,
    enrich_revalidate_with_local_collect,
)
from src.schemas.sla import SLARevalidateTelemetryRequest, SLARevalidateTelemetryResponse


COMPLETE = {
    "telemetry_contract_version": "v2",
    "ran": {"prb_utilization": 0.0, "latency": 5.0, "latency_ms": 5.0},
    "transport": {"rtt": 5.0, "jitter": 1.0, "rtt_ms": 5.0, "jitter_ms": 1.0},
    "core": {"cpu": 0.01, "memory": 0.02, "cpu_utilization": 0.01, "memory_bytes": 0.02},
}

NULL_SNAP = {
    "telemetry_contract_version": "v2",
    "ran": {"prb_utilization": None, "latency": None},
    "transport": {"rtt": None, "jitter": None},
    "core": {"cpu": None, "memory": None},
}


def test_snapshot_complete_detection():
    assert snapshot_is_complete(COMPLETE)
    assert not snapshot_is_complete(NULL_SNAP)


def test_snapshot_field_gaps_partial():
    partial = {
        "ran": {"prb_utilization": 0.0, "latency": 5.0},
        "transport": {"rtt": None, "jitter": None},
        "core": {"cpu": None, "memory": None},
    }
    gaps = snapshot_field_gaps(partial)
    assert "transport.rtt" in gaps
    assert count_populated_fields(partial) == 2


@pytest.mark.asyncio
async def test_enrich_replaces_null_with_local_collect():
    request = SLARevalidateTelemetryRequest(
        intent_id="test-intent",
        reference_telemetry_snapshot=COMPLETE,
    )
    response = SLARevalidateTelemetryResponse(
        intent_id="test-intent",
        execution_id_revalidation="rev-1",
        telemetry_snapshot_atual=NULL_SNAP,
        timestamps_utc={},
        drift_summary={"compared": True, "deltas": []},
        revalidation_status="INCOMPLETE",
        temporal_correlation={},
        metadata={"delegated_to_sla_agent": True},
    )

    async def fake_collect(_eid, _ts):
        return dict(COMPLETE), 1.0

    def fake_drift(ref, cur):
        return {"deltas": [{"path": "ran.latency", "reference": 5.0, "current": 5.0, "delta": 0.0}], "fields_compared": 1}

    def fake_remediation(**kwargs):
        return {"recommendation": "ok"}

    enriched = await enrich_revalidate_with_local_collect(
        request,
        response,
        collect_fn=fake_collect,
        drift_fn=fake_drift,
        remediation_fn=fake_remediation,
    )

    assert enriched.revalidation_status == "OK"
    assert enriched.telemetry_snapshot_atual["ran"]["latency"] == 5.0
    assert enriched.metadata.get("local_collect_fallback") is True
    assert "runtime_assurance" not in enriched.metadata


@pytest.mark.asyncio
async def test_enrich_skips_when_already_complete():
    request = SLARevalidateTelemetryRequest(intent_id="test-intent")
    response = SLARevalidateTelemetryResponse(
        intent_id="test-intent",
        execution_id_revalidation="rev-1",
        telemetry_snapshot_atual=COMPLETE,
        timestamps_utc={},
        drift_summary={},
        revalidation_status="OK",
        temporal_correlation={},
        metadata={},
    )

    async def should_not_run(*_a, **_k):
        raise AssertionError("collect should not run")

    enriched = await enrich_revalidate_with_local_collect(
        request,
        response,
        collect_fn=should_not_run,
        drift_fn=lambda r, c: {},
        remediation_fn=lambda **k: {},
    )
    assert enriched.revalidation_status == "OK"
