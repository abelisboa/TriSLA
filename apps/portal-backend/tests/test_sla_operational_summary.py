"""Tests for operational summary builder — Sprint 5N."""
from src.services.sla_operational_summary import build_operational_summary


def test_build_operational_summary_active_intent():
    sem = {
        "intent_id": "abc",
        "status": "ACTIVE",
        "nest_id": "nest-abc",
        "metadata": {
            "status": "ACTIVE",
            "final_decision": "ACCEPT",
            "telemetry_snapshot": {"ran": {}},
        },
    }
    out = build_operational_summary(sem)
    assert out["lifecycle_status_label"] == "In Operation"
    assert out["semantic_validation"] == "Passed"
    assert out["nest_generated"] == "Yes"
    assert out["semantic_fill"] == "Applied"
