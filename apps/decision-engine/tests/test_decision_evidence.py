"""Decision evidence quantitative records."""
from decision_evidence import build_decision_evidence_from_context, build_prb_hard_gate_evidence


def test_prb_hard_renegotiate_evidence():
    ev = build_prb_hard_gate_evidence(
        prb_raw=27.65,
        threshold_percent=25.0,
        rule="PRB_HARD_RENEGOTIATE_THRESHOLD",
    )
    assert ev["metric"] == "prb_utilization"
    assert ev["observed"] == 27.65
    assert ev["threshold"] == 25.0
    assert ev["delta"] == 2.65
    assert ev["rule"] == "PRB_HARD_RENEGOTIATE_THRESHOLD"


def test_build_from_context_prb_gate():
    evidence = build_decision_evidence_from_context(
        reasoning="PRB_HARD_RENEGOTIATE_THRESHOLD",
        decision_source="PRB_HARD_RENEGOTIATE_THRESHOLD",
        xai_bundle={
            "ran_prb_utilization_input": 27.65,
            "hard_prb_thresholds": {"renegotiate": 25, "reject": 95},
        },
        context={"telemetry_snapshot": {"ran": {"prb_utilization": 27.65}}},
    )
    assert len(evidence) == 1
    assert evidence[0]["delta"] == 2.65
