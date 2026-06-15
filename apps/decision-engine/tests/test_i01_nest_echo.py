"""Wave 3A G3-C — SLAEvaluateInput nest parse + echo-only contract."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from i01_nest_echo import echo_inbound_nest  # noqa: E402
from models import (  # noqa: E402
    DecisionAction,
    DecisionInput,
    DecisionResult,
    SLAIntent,
    SLAEvaluateInput,
    SliceType,
)
from nest_input_resolver import (  # noqa: E402
    extract_inbound_nest,
    resolve_nest_for_evaluate,
)


def _baseline_intent() -> dict:
    return {
        "intent_id": "intent-wave3a-echo",
        "tenant_id": "tenant-test",
        "service_type": "eMBB",
        "sla_requirements": {"latency": "50ms", "throughput": "100Mbps"},
    }


def _sample_nest_body() -> dict:
    return {
        "nest_id": "nest-intent-wave3a-echo",
        "intent_id": "intent-wave3a-echo",
        "status": "generated",
        "network_slices": [
            {
                "slice_id": "slice-intent-wave3a-echo-001",
                "slice_type": "eMBB",
                "resources": {
                    "cpu": "4",
                    "memory": "8Gi",
                    "bandwidth": "1Gbps",
                    "feasibility_score": 0.88,
                },
                "status": "generated",
            }
        ],
        "gst_id": "gst-intent-wave3a-echo",
    }


def test_sla_evaluate_input_accepts_nest_body():
    payload = SLAEvaluateInput(
        intent_id="intent-wave3a-echo",
        nest_id="nest-intent-wave3a-echo",
        intent=_baseline_intent(),
        nest=_sample_nest_body(),
    )
    assert payload.nest is not None
    assert len(payload.nest["network_slices"]) == 1


def test_sla_evaluate_input_backward_compatible_without_nest():
    payload = SLAEvaluateInput(
        intent_id="intent-wave3a-echo",
        nest_id="nest-intent-wave3a-echo",
        intent=_baseline_intent(),
    )
    assert payload.nest is None


def test_echo_inbound_nest_preserves_network_slices():
    inbound = _sample_nest_body()
    result = DecisionResult(
        decision_id="dec-wave3a",
        intent_id="intent-wave3a-echo",
        action=DecisionAction.ACCEPT,
        reasoning="test",
        confidence=0.9,
        metadata={"decision_mode": "threshold"},
    )
    echo_inbound_nest(result, inbound)
    echoed = (result.metadata or {}).get("inbound_nest") or {}
    assert echoed["network_slices"][0]["slice_type"] == "eMBB"
    assert echoed["gst_id"] == "gst-intent-wave3a-echo"
    assert result.metadata["decision_mode"] == "threshold"


def test_echo_nest_does_not_mutate_when_absent():
    result = DecisionResult(
        decision_id="dec-wave3a",
        intent_id="intent-wave3a-echo",
        action=DecisionAction.ACCEPT,
        reasoning="test",
        confidence=0.9,
        metadata={},
    )
    echo_inbound_nest(result, None)
    assert "inbound_nest" not in (result.metadata or {})


def test_resolve_nest_ignores_body_for_decision_echo_only():
    """Inbound nest body must not populate DecisionInput.nest slices/resources."""
    sla_input = SLAEvaluateInput(
        intent_id="intent-wave3a-echo",
        nest_id="nest-intent-wave3a-echo",
        intent=_baseline_intent(),
        nest=_sample_nest_body(),
    )
    decision_nest = resolve_nest_for_evaluate(sla_input)
    assert decision_nest is not None
    assert decision_nest.nest_id == "nest-intent-wave3a-echo"
    assert decision_nest.network_slices == []
    assert decision_nest.resources == {}


def test_extract_inbound_nest_returns_body():
    sla_input = SLAEvaluateInput(
        intent_id="intent-wave3a-echo",
        nest_id="nest-intent-wave3a-echo",
        intent=_baseline_intent(),
        nest=_sample_nest_body(),
    )
    inbound = extract_inbound_nest(sla_input)
    assert inbound is not None
    assert inbound["network_slices"][0]["resources"]["bandwidth"] == "1Gbps"


def test_decision_input_unchanged_with_nest_on_wire():
    """Regression: nest body on wire must not alter minimal DecisionInput nest."""
    sla_without = SLAEvaluateInput(
        intent_id="intent-wave3a-echo",
        nest_id="nest-intent-wave3a-echo",
        intent=_baseline_intent(),
    )
    sla_with = SLAEvaluateInput(
        intent_id="intent-wave3a-echo",
        nest_id="nest-intent-wave3a-echo",
        intent=_baseline_intent(),
        nest=_sample_nest_body(),
    )
    nest_without = resolve_nest_for_evaluate(sla_without)
    nest_with = resolve_nest_for_evaluate(sla_with)
    assert nest_without.model_dump() == nest_with.model_dump()


def test_decision_input_intent_not_fed_from_nest_body():
    sla_input = SLAEvaluateInput(
        intent_id="intent-wave3a-echo",
        nest_id="nest-intent-wave3a-echo",
        intent=_baseline_intent(),
        nest=_sample_nest_body(),
    )
    intent = SLAIntent(
        intent_id=sla_input.intent["intent_id"],
        tenant_id=sla_input.intent.get("tenant_id"),
        service_type=SliceType(sla_input.intent["service_type"]),
        sla_requirements=sla_input.intent.get("sla_requirements", {}),
    )
    decision_input = DecisionInput(
        intent=intent,
        nest=resolve_nest_for_evaluate(sla_input),
        context=sla_input.context,
    )
    assert decision_input.intent.metadata is None
    assert decision_input.nest.network_slices == []
