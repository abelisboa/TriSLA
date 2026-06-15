"""Wave 1 G3-A — SLAEvaluateInput metadata parse + echo-only contract."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from i01_metadata_echo import echo_inbound_metadata  # noqa: E402
from models import (  # noqa: E402
    DecisionAction,
    DecisionInput,
    DecisionResult,
    SLAIntent,
    SLAEvaluateInput,
    SliceType,
)


def _baseline_intent() -> dict:
    return {
        "intent_id": "intent-wave1-echo",
        "tenant_id": "tenant-test",
        "service_type": "URLLC",
        "sla_requirements": {"latency": "10ms", "reliability": 0.999},
    }


def test_sla_evaluate_input_accepts_metadata():
    payload = SLAEvaluateInput(
        intent_id="intent-wave1-echo",
        nest_id="nest-intent-wave1-echo",
        intent=_baseline_intent(),
        metadata={"canonical_sla": {"service_requirements": []}, "trace_id": "t-1"},
    )
    assert payload.metadata is not None
    assert payload.metadata["trace_id"] == "t-1"
    assert "canonical_sla" in payload.metadata


def test_sla_evaluate_input_backward_compatible_without_metadata():
    payload = SLAEvaluateInput(
        intent_id="intent-wave1-echo",
        intent=_baseline_intent(),
    )
    assert payload.metadata is None


def test_echo_inbound_metadata_preserves_canonical_sla():
    inbound = {
        "canonical_sla": {"service_requirements": [{"kpi": "latency", "value": "10ms"}]},
        "trace_id": "trace-abc",
    }
    result = DecisionResult(
        decision_id="dec-test",
        intent_id="intent-wave1-echo",
        action=DecisionAction.ACCEPT,
        reasoning="test",
        confidence=0.9,
        metadata={"decision_mode": "threshold"},
    )
    echo_inbound_metadata(result, inbound)
    echoed = (result.metadata or {}).get("inbound_metadata") or {}
    assert echoed["canonical_sla"]["service_requirements"][0]["kpi"] == "latency"
    assert echoed["trace_id"] == "trace-abc"
    assert result.metadata["decision_mode"] == "threshold"


def test_echo_does_not_mutate_when_metadata_absent():
    result = DecisionResult(
        decision_id="dec-test",
        intent_id="intent-wave1-echo",
        action=DecisionAction.ACCEPT,
        reasoning="test",
        confidence=0.9,
        metadata={"governance_event": {"nest_id": "nest-x"}},
    )
    echo_inbound_metadata(result, None)
    assert "inbound_metadata" not in (result.metadata or {})


def test_decision_input_intent_not_fed_from_root_metadata():
    """Root metadata must not be copied into SLAIntent.metadata (rule side-effect guard)."""
    sla_input = SLAEvaluateInput(
        intent_id="intent-wave1-echo",
        nest_id="nest-intent-wave1-echo",
        intent=_baseline_intent(),
        metadata={"resource_pressure": 0.95, "semantic_priority": "critical"},
    )
    intent = SLAIntent(
        intent_id=sla_input.intent["intent_id"],
        tenant_id=sla_input.intent.get("tenant_id"),
        service_type=SliceType(sla_input.intent["service_type"]),
        sla_requirements=sla_input.intent.get("sla_requirements", {}),
    )
    decision_input = DecisionInput(intent=intent, context=sla_input.context)
    assert decision_input.intent.metadata is None


def test_sem_shaped_payload_retains_metadata_fields():
    """SEM HTTP payload shape — metadata no longer stripped at Pydantic ingress."""
    body = {
        "intent_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "nest_id": "nest-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "intent": {
            "intent_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "tenant_id": "tenant-1",
            "service_type": "URLLC",
            "sla_requirements": {"latency": "10ms", "reliability": 0.999},
        },
        "metadata": {
            "canonical_sla": {"version": "2.0", "service_requirements": []},
            "trace_id": "sem-trace-001",
            "timestamp": "2026-06-12T20:00:00Z",
        },
        "telemetry_snapshot": {"ran": {"prb_utilization": 0.42}},
        "context": {"telemetry_features": {"prb_current": 0.42}},
    }
    parsed = SLAEvaluateInput.model_validate(body)
    assert parsed.metadata["canonical_sla"]["version"] == "2.0"
    assert parsed.metadata["trace_id"] == "sem-trace-001"
    assert parsed.telemetry_snapshot["ran"]["prb_utilization"] == 0.42
