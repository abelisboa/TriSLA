"""Unit tests for runtime_slo_evaluator — Sprint 5M4."""
from __future__ import annotations

import pytest

from runtime_assurance_store import clear_state, get_previous_state, set_state
from runtime_slo_evaluator import (
    ASSURANCE_AT_RISK,
    ASSURANCE_COMPLIANT,
    ASSURANCE_VIOLATED,
    ASSURANCE_WARNING,
    detect_drift,
    evaluate_runtime_assurance,
)


def _healthy_snapshot() -> dict:
    return {
        "telemetry_contract_version": "v2",
        "ran": {"prb_utilization": 0.05, "latency_ms": 1.5, "cpu_utilization": 5.0},
        "transport": {
            "rtt_ms": 1.5,
            "jitter_ms": 0.2,
            "throughput_mbps": 500.0,
            "packet_loss": 0.001,
            "bandwidth": 150.0,
        },
        "core": {"cpu_utilization": 5.0, "memory_utilization": 10.0, "cpu": 5.0, "memory": 10.0},
    }


def _warning_snapshot() -> dict:
    return {
        "telemetry_contract_version": "v2",
        "ran": {"prb_utilization": 0.55, "latency_ms": 17.0, "cpu_utilization": 55.0},
        "transport": {
            "rtt_ms": 7.5,
            "jitter_ms": 2.8,
            "throughput_mbps": 55.0,
            "packet_loss": 0.05,
            "bandwidth": 90.0,
        },
        "core": {"cpu_utilization": 55.0, "memory_utilization": 55.0, "cpu": 55.0, "memory": 55.0},
    }


def _at_risk_snapshot() -> dict:
    return {
        "telemetry_contract_version": "v2",
        "ran": {"prb_utilization": 0.75, "latency_ms": 52.0, "cpu_utilization": 68.0},
        "transport": {
            "rtt_ms": 52.0,
            "jitter_ms": 5.5,
            "throughput_mbps": 8.0,
            "packet_loss": 0.2,
            "bandwidth": 40.0,
        },
        "core": {"cpu_utilization": 78.0, "memory_utilization": 78.0, "cpu": 78.0, "memory": 78.0},
    }


def _violated_snapshot() -> dict:
    return {
        "telemetry_contract_version": "v2",
        "ran": {"prb_utilization": 0.95, "latency_ms": 50.0},
        "transport": {"rtt_ms": 30.0, "jitter_ms": 12.0, "throughput_mbps": 5.0},
        "core": {"cpu_utilization": 0.95, "memory_bytes": 0.95},
    }


URLLC_REQ = {"latency": "10ms", "throughput": "100Mbps", "reliability": 0.99999, "type": "URLLC"}
EMBB_REQ = {"latency": "20ms", "throughput": "50Mbps", "reliability": 0.99, "type": "EMBB"}
MMTC_REQ = {"latency": "50ms", "throughput": "10Mbps", "reliability": 0.95, "type": "MMTC"}
SMARTCITY_REQ = {"latency": "30ms", "throughput": "80Mbps", "reliability": 0.995, "type": "EMBB"}


class TestRuntimeSloEvaluator:
    def test_urllc_compliant(self):
        out = evaluate_runtime_assurance(
            telemetry_snapshot=_healthy_snapshot(),
            sla_requirements=URLLC_REQ,
            slice_type="URLLC",
            intent_id="test-urllc",
        )
        assert out["runtime_assurance"]["state"] == ASSURANCE_COMPLIANT
        assert out["runtime_assurance"]["drift_detected"] is False

    def test_embb_warning(self):
        out = evaluate_runtime_assurance(
            telemetry_snapshot=_warning_snapshot(),
            sla_requirements=EMBB_REQ,
            slice_type="EMBB",
            intent_id="test-embb",
        )
        assert out["runtime_assurance"]["state"] == ASSURANCE_WARNING

    def test_mmtc_at_risk(self):
        out = evaluate_runtime_assurance(
            telemetry_snapshot=_at_risk_snapshot(),
            sla_requirements=MMTC_REQ,
            slice_type="MMTC",
            intent_id="test-mmtc",
        )
        assert out["runtime_assurance"]["state"] in {
            ASSURANCE_AT_RISK,
            ASSURANCE_VIOLATED,
        }

    def test_smartcity_violated(self):
        out = evaluate_runtime_assurance(
            telemetry_snapshot=_violated_snapshot(),
            sla_requirements=SMARTCITY_REQ,
            slice_type="EMBB",
            intent_id="test-smartcity",
        )
        assert out["runtime_assurance"]["state"] == ASSURANCE_VIOLATED
        assert out["runtime_assurance"]["violations"]

    def test_drift_detection(self):
        ref = _healthy_snapshot()
        cur = _warning_snapshot()
        drift, indicators = detect_drift(ref, cur)
        assert drift is True
        assert len(indicators) > 0

    def test_governance_event_on_transition(self):
        clear_state("gov-test")
        set_state("gov-test", ASSURANCE_COMPLIANT)
        out = evaluate_runtime_assurance(
            telemetry_snapshot=_violated_snapshot(),
            sla_requirements=URLLC_REQ,
            slice_type="URLLC",
            previous_state=get_previous_state("gov-test"),
            intent_id="gov-test",
            nest_id="nest-gov-test",
        )
        assert out["runtime_governance_event"] is not None
        evt = out["runtime_governance_event"]
        assert evt["event_type"] == "RUNTIME_ASSURANCE"
        assert evt["previous_state"] == ASSURANCE_COMPLIANT
        assert evt["event_state"] == ASSURANCE_VIOLATED
        assert evt["blockchain_scope"] == "none"

    def test_empty_snapshot_at_risk(self):
        out = evaluate_runtime_assurance(
            telemetry_snapshot={},
            sla_requirements=URLLC_REQ,
            slice_type="URLLC",
        )
        assert out["runtime_assurance"]["state"] == ASSURANCE_AT_RISK

    def test_controlled_state_matrix(self):
        """Phase 8 controlled scenarios A–D."""
        scenarios = [
            (_healthy_snapshot(), ASSURANCE_COMPLIANT),
            (_warning_snapshot(), ASSURANCE_WARNING),
            (_at_risk_snapshot(), None),
            (_violated_snapshot(), ASSURANCE_VIOLATED),
        ]
        for snap, expected in scenarios:
            out = evaluate_runtime_assurance(
                telemetry_snapshot=snap,
                sla_requirements=EMBB_REQ,
                slice_type="EMBB",
            )
            state = out["runtime_assurance"]["state"]
            if expected:
                assert state == expected
            else:
                assert state in {
                    ASSURANCE_WARNING,
                    ASSURANCE_AT_RISK,
                    ASSURANCE_VIOLATED,
                }
