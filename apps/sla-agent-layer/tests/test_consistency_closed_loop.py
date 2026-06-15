"""Phase Next — consistency and remediation simulation."""
from runtime_slo_evaluator import evaluate_runtime_assurance


def test_admission_vs_runtime_compliance_split():
    out = evaluate_runtime_assurance(
        telemetry_snapshot={
            "ran": {"prb_utilization": 27.65, "latency_ms": 5.0},
            "transport": {"jitter_ms": 0.4},
            "core": {"cpu": 0.01},
        },
        admission_compliance=0.39,
        admission_decision="RENEGOTIATE",
        slice_type="URLLC",
    )
    ra = out["runtime_assurance"]
    assert ra["admission_compliance"] == 0.39
    assert ra["runtime_compliance"] is not None
    assert ra["admission_compliance_percent"] == 39.0
    assert ra["operational_status"] == "PENDING_RENEGOTIATION"


def test_governance_clarity_renegotiate():
    out = evaluate_runtime_assurance(
        telemetry_snapshot={"ran": {"prb_utilization": 10.0}, "transport": {}, "core": {}},
        admission_decision="RENEGOTIATE",
        bc_status="SKIPPED",
        slice_type="URLLC",
    )
    gc = out["runtime_assurance"]["governance_clarity"]
    assert gc["governance_event"]["status"] == "Recorded"
    assert gc["blockchain_registration"]["executed"] is False


def test_remediation_simulation_prb():
    out = evaluate_runtime_assurance(
        telemetry_snapshot={
            "ran": {"prb_utilization": 30.0, "latency_ms": 5.0},
            "transport": {"jitter_ms": 0.2},
            "core": {"cpu": 0.01},
        },
        slice_type="URLLC",
        enable_remediation_simulation=True,
    )
    ra = out["runtime_assurance"]
    assert ra["closed_loop"]["act"] is True
    assert len(ra["remediation_attempts"]) >= 1
    assert ra["remediation_attempts"][0]["action"] == "adjust_prb_policy"


def test_telemetry_fidelity_mismatch():
    out = evaluate_runtime_assurance(
        telemetry_snapshot={"ran": {"prb_utilization": 0.0}, "transport": {}, "core": {}},
        admission_telemetry_snapshot={"ran": {"prb_utilization": 27.65}, "transport": {}, "core": {}},
        slice_type="URLLC",
    )
    fid = out["runtime_assurance"]["telemetry_fidelity"]
    assert fid["consistent"] is False
    assert fid["mismatch_count"] >= 1
