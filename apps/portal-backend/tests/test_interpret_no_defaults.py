"""P1 — interpret endpoint must not inject slice-type technical_parameter defaults."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app

URLLC_FULL_SEM = {
    "intent_id": "intent-urllc-full",
    "service_type": "URLLC",
    "technical_parameters": {
        "latency_maxima_ms": 5,
        "disponibilidade_percent": 99.999,
        "confiabilidade_percent": 99.999,
        "numero_dispositivos": 50,
    },
    "sla_requirements": {"latency": "5ms", "reliability": 0.99999},
}

DEFAULT_INJECTION_KEYS = {
    "latency_maxima_ms",
    "disponibilidade_percent",
    "confiabilidade_percent",
    "throughput_min_dl_mbps",
    "throughput_min_ul_mbps",
    "numero_dispositivos",
}


@pytest.fixture
def client():
    return TestClient(app)


def _interpret(client, intent_text: str, tenant_id: str = "tenant-p1"):
    return client.post(
        "/api/v1/sla/interpret",
        json={"intent_text": intent_text, "tenant_id": tenant_id},
    )


@patch("src.routers.sla.nasp_service.call_sem_csmf", new_callable=AsyncMock)
def test_t1_urllc_full_parameters_preserved(mock_sem, client):
    """T1: URLLC with complete SEM params — no alteration."""
    mock_sem.return_value = dict(URLLC_FULL_SEM)
    response = _interpret(client, "URLLC industrial control with 5ms latency")
    assert response.status_code == 200
    body = response.json()
    assert body["technical_parameters"] == URLLC_FULL_SEM["technical_parameters"]
    assert body["technical_parameters_status"] == "PROVIDED"
    assert body["technical_parameters"]["latency_maxima_ms"] == 5
    assert body["technical_parameters"]["latency_maxima_ms"] != 10


@patch("src.routers.sla.nasp_service.call_sem_csmf", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "service_type,intent_text",
    [
        ("URLLC", "URLLC minimal intent without numeric parameters"),
        ("eMBB", "eMBB video streaming without numeric parameters"),
        ("mMTC", "mMTC sensor network without numeric parameters"),
    ],
)
def test_t2_t3_t4_no_defaults_when_sem_empty(mock_sem, client, service_type, intent_text):
    """T2–T4: Empty SEM technical_parameters — no catalog defaults injected."""
    mock_sem.return_value = {
        "intent_id": f"intent-{service_type.lower()}-empty",
        "service_type": service_type,
        "technical_parameters": {},
        "sla_requirements": {},
    }
    response = _interpret(client, intent_text)
    assert response.status_code == 200
    body = response.json()
    assert body["technical_parameters"] == {}
    assert body["technical_parameters_status"] == "NOT_PROVIDED"
    tech = body["technical_parameters"]
    assert tech.get("latency_maxima_ms") != 10
    assert tech.get("throughput_min_dl_mbps") != 100
    assert tech.get("numero_dispositivos") != 1000
    for key in DEFAULT_INJECTION_KEYS:
        assert key not in tech


@patch("src.routers.sla.nasp_service.call_sem_csmf", new_callable=AsyncMock)
def test_t5_payload_preservation_sem_to_frontend(mock_sem, client):
    """T5: Raw SEM payload fields preserved through backend interpret response."""
    sem_payload = {
        "intent_id": "intent-preserve-001",
        "service_type": "URLLC",
        "nest_id": "nest-preserve-001",
        "technical_parameters": {"latency_maxima_ms": 8},
        "sla_requirements": {"latency": "8ms"},
        "created_at": "2026-06-13T06:30:00Z",
    }
    mock_sem.return_value = dict(sem_payload)
    response = _interpret(client, "URLLC preserve test")
    assert response.status_code == 200
    body = response.json()
    assert body["technical_parameters"] == sem_payload["technical_parameters"]
    assert body["sla_requirements"]["latency"] == "8ms"
    assert body["nest_id"] == "nest-preserve-001"
    assert body["intent_id"] == sem_payload["intent_id"]


@patch("src.routers.sla.nasp_service.call_sem_csmf", new_callable=AsyncMock)
def test_sem_null_technical_parameters_propagates_not_provided(mock_sem, client):
    """SEM explicit null → empty object + NOT_PROVIDED status."""
    mock_sem.return_value = {
        "intent_id": "intent-null-tech",
        "service_type": "URLLC",
        "technical_parameters": None,
        "sla_requirements": {},
    }
    response = _interpret(client, "URLLC null tech params")
    assert response.status_code == 200
    body = response.json()
    assert body["technical_parameters"] == {}
    assert body["technical_parameters_status"] == "NOT_PROVIDED"
