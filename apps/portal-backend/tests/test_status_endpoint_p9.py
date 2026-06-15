"""P9 — GET /api/v1/sla/status/{id} operational fix."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _sem_payload(
    slice_type: str,
    *,
    decision: str = "ACCEPT",
    intent_id: str = "intent-p9-test",
) -> dict:
    return {
        "status": "ACTIVE",
        "tenant_id": "p9-tenant",
        "intent_id": intent_id,
        "nest_id": f"nest-{intent_id}",
        "service_type": slice_type,
        "sla_requirements": {"slice_type": slice_type, "type": slice_type},
        "metadata": {
            "final_decision": decision,
            "decision_band": decision,
            "bc_status": "COMMITTED",
            "tx_hash": "0xabc123",
            "block_number": 5615000,
            "decision_evidence": [
                {"metric": "prb_utilization", "observed": 0.1, "threshold": 0.25, "rule": "decision_score_mode"}
            ],
            "telemetry_snapshot": {
                "ran": {"prb_utilization": 59.7},
                "transport": {"rtt_ms": 5.0},
                "core": {"cpu_utilization": 0.01},
            },
        },
    }


@patch("src.routers.sla.collect_domain_metrics_async", new_callable=AsyncMock)
@patch("src.routers.sla.nasp_service.get_sla_status", new_callable=AsyncMock)
def test_t1_status_endpoint_http_200(mock_get_status, mock_collect, client):
    mock_get_status.return_value = _sem_payload("URLLC")
    mock_collect.return_value = ({"ran": {"prb_utilization": 0.2}}, 12.0)
    resp = client.get("/api/v1/sla/status/intent-p9-test")
    assert resp.status_code == 200


@pytest.mark.parametrize("slice_type", ["URLLC", "eMBB", "mMTC"])
@patch("src.routers.sla.collect_domain_metrics_async", new_callable=AsyncMock)
@patch("src.routers.sla.nasp_service.get_sla_status", new_callable=AsyncMock)
def test_t2_t4_slice_status(mock_get_status, mock_collect, client, slice_type):
    intent_id = f"intent-p9-{slice_type.lower()}"
    mock_get_status.return_value = _sem_payload(slice_type, intent_id=intent_id)
    mock_collect.return_value = ({"ran": {"prb_utilization": 0.15}}, 10.0)
    resp = client.get(f"/api/v1/sla/status/{intent_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["sla_id"] == intent_id
    assert body.get("sla_requirements") == {"slice_type": slice_type, "type": slice_type}


@patch("src.routers.sla.collect_domain_metrics_async", new_callable=AsyncMock)
@patch("src.routers.sla.nasp_service.get_sla_status", new_callable=AsyncMock)
def test_t5_runtime_lifecycle_enabled(mock_get_status, mock_collect, client):
    mock_get_status.return_value = _sem_payload("URLLC", decision="ACCEPT")
    mock_collect.return_value = ({"ran": {"prb_utilization": 0.2}}, 8.0)
    resp = client.get("/api/v1/sla/status/intent-p9-test")
    assert resp.status_code == 200
    assert resp.json()["runtime_lifecycle_enabled"] is True


@patch("src.routers.sla.nasp_service.get_sla_status", new_callable=AsyncMock)
def test_t5_runtime_lifecycle_disabled_on_reject(mock_get_status, client):
    mock_get_status.return_value = _sem_payload("URLLC", decision="REJECT")
    resp = client.get("/api/v1/sla/status/intent-p9-test")
    assert resp.status_code == 200
    assert resp.json()["runtime_lifecycle_enabled"] is False


@patch("src.routers.sla.collect_domain_metrics_async", new_callable=AsyncMock)
@patch("src.routers.sla.nasp_service.get_sla_status", new_callable=AsyncMock)
def test_t6_governance_fields(mock_get_status, mock_collect, client):
    mock_get_status.return_value = _sem_payload("eMBB")
    mock_collect.return_value = ({"ran": {"prb_utilization": 0.1}}, 5.0)
    resp = client.get("/api/v1/sla/status/intent-p9-test")
    assert resp.status_code == 200
    op = resp.json()["operational_summary"]
    assert op["bc_status"] == "COMMITTED"
    assert op["tx_hash"] == "0xabc123"
    assert op["block_number"] == 5615000


@patch("src.routers.sla.collect_domain_metrics_async", new_callable=AsyncMock)
@patch("src.routers.sla.nasp_service.get_sla_status", new_callable=AsyncMock)
def test_t7_decision_evidence(mock_get_status, mock_collect, client):
    mock_get_status.return_value = _sem_payload("mMTC")
    mock_collect.return_value = ({"ran": {"prb_utilization": 0.05}}, 5.0)
    resp = client.get("/api/v1/sla/status/intent-p9-test")
    assert resp.status_code == 200
    evidence = resp.json()["admission_decision_evidence"]
    assert isinstance(evidence, list)
    assert len(evidence) >= 1
