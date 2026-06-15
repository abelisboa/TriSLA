"""RC-P19-006 — admission compliance propagation from decision metadata."""
from src.services.admission_compliance import (
    admission_compliance_from_metadata,
    enrich_status_runtime_assurance,
    wire_admission_compliance_fields,
)


def test_admission_compliance_from_decision_score():
    md = {"decision_score": 0.8273991794623657}
    assert admission_compliance_from_metadata(md) == 0.8273991794623657


def test_admission_compliance_from_ran_aware_risk():
    md = {"ran_aware_final_risk": 0.25}
    assert admission_compliance_from_metadata(md) == 0.75


def test_wire_admission_compliance_fields():
    metadata = {
        "decision_score": 0.81,
        "runtime_assurance": {"sla_compliance": 0.6943562, "state": "AT_RISK"},
    }
    wire_admission_compliance_fields(metadata)
    assert metadata["admission_compliance"] == 0.81
    assert metadata["admission_compliance_percent"] == 81.0
    ra = metadata["runtime_assurance"]
    assert ra["admission_compliance"] == 0.81
    assert ra["runtime_compliance"] == 0.6943562
    assert ra["runtime_compliance_percent"] == 69.44


def test_enrich_status_runtime_assurance():
    md = {"decision_score": 0.82}
    ra = enrich_status_runtime_assurance(
        md,
        {"sla_compliance": 0.71, "state": "WARNING"},
    )
    assert ra["admission_compliance_percent"] == 82.0
    assert ra["runtime_compliance_percent"] == 71.0
    assert ra["sla_compliance"] == 0.71
