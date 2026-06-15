"""Status endpoint runtime gating."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from src.services.admission_decision import resolve_admission_decision
from src.services.sla_status_assurance import resolve_status_runtime_assurance
from src.services.sla_status_telemetry import resolve_status_telemetry_snapshot


def test_assurance_skipped_when_runtime_disabled():
    sem = {"metadata": {"final_decision": "REJECT"}, "intent_id": "x"}
    with patch("src.services.sla_status_assurance.httpx.Client") as mock_client:
        ra = resolve_status_runtime_assurance(
            sem,
            telemetry_snapshot={"ran": {"prb_utilization": 0}},
            runtime_lifecycle_enabled=False,
        )
        assert ra is None
        mock_client.assert_not_called()


def test_telemetry_admission_only_when_disabled():
    sem = {
        "metadata": {
            "final_decision": "REJECT",
            "telemetry_snapshot": {"ran": {"prb_utilization": 59.7}},
        }
    }
    snap = resolve_status_telemetry_snapshot(
        sem,
        collected_snapshot={"ran": {"prb_utilization": 0}},
        runtime_lifecycle_enabled=False,
    )
    assert snap["ran"]["prb_utilization"] == 59.7


@pytest.mark.asyncio
async def test_revalidate_gate_reject():
    from src.routers import sla as sla_router

    request = type("R", (), {"intent_id": "test-intent", "model_dump": lambda self, **k: {"intent_id": "test-intent"}})()

    with patch.object(
        sla_router.nasp_service,
        "get_sla_status",
        AsyncMock(return_value={"metadata": {"final_decision": "REJECT"}}),
    ):
        with pytest.raises(HTTPException) as exc:
            await sla_router.revalidate_telemetry(request)
        assert exc.value.status_code == 409
        assert "non-accepted" in exc.value.detail.lower()
