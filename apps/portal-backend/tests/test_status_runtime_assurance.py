"""Portal backend tests for runtime assurance status binding — Sprint 5M4."""
from __future__ import annotations

from src.services.sla_status_assurance import resolve_status_runtime_assurance


def test_prefers_sem_metadata_runtime_assurance():
    sem = {
        "intent_id": "abc",
        "metadata": {
            "runtime_assurance": {
                "state": "COMPLIANT",
                "drift_detected": False,
                "recommendation": "OK",
                "last_evaluation": "2026-05-30T00:00:00+00:00",
            }
        },
    }
    ra = resolve_status_runtime_assurance(sem, telemetry_snapshot={"ran": {"latency_ms": 1}})
    assert ra is not None
    assert ra["state"] == "COMPLIANT"


def test_returns_none_without_sem_or_url(monkeypatch):
    monkeypatch.delenv("SLA_AGENT_PIPELINE_INGEST_URL", raising=False)
    monkeypatch.delenv("SLA_AGENT_RUNTIME_ASSURANCE_URL", raising=False)
    sem = {"intent_id": "abc", "metadata": {}}
    ra = resolve_status_runtime_assurance(sem, telemetry_snapshot={"ran": {"latency_ms": 1}})
    assert ra is None
