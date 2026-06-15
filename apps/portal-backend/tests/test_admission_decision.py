"""Tests for runtime lifecycle gating — admission decision resolution."""
from src.services.admission_decision import (
    resolve_admission_context,
    resolve_admission_decision,
    resolve_runtime_lifecycle_enabled,
)


def test_resolve_from_final_decision():
    sem = {"metadata": {"final_decision": "REJECT"}}
    assert resolve_admission_decision(sem) == "REJECT"
    assert resolve_runtime_lifecycle_enabled(sem) is False


def test_resolve_from_sla_lifecycle_renegotiate():
    sem = {"metadata": {"sla_lifecycle": {"DECIDED_RENEGOTIATE": "2026-01-01T00:00:00Z"}}}
    assert resolve_admission_decision(sem) == "RENEGOTIATE"


def test_accept_enables_runtime():
    sem = {"metadata": {"final_decision": "ACCEPT", "telemetry_snapshot": {"ran": {"prb_utilization": 10}}}}
    decision, enabled, snap = resolve_admission_context(sem)
    assert decision == "ACCEPT"
    assert enabled is True
    assert snap == {"ran": {"prb_utilization": 10}}


def test_reject_returns_admission_snapshot_only():
    sem = {
        "metadata": {
            "final_decision": "REJECT",
            "telemetry_snapshot": {"ran": {"prb_utilization": 59.7}},
        }
    }
    _, enabled, snap = resolve_admission_context(sem)
    assert enabled is False
    assert snap["ran"]["prb_utilization"] == 59.7
