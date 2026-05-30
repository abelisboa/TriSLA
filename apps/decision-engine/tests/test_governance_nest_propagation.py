"""M1 — governance_event.nest_id propagation from sla_input.nest_id."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lifecycle_authority import enrich_lifecycle_governance_metadata  # noqa: E402
from models import (  # noqa: E402
    DecisionAction,
    DecisionInput,
    DecisionResult,
    SLAIntent,
    SLAEvaluateInput,
    SliceType,
)
from nest_input_resolver import resolve_nest_for_evaluate  # noqa: E402


def _sla_evaluate(service_type: str, intent_id: str, nest_id: str) -> SLAEvaluateInput:
    return SLAEvaluateInput(
        intent_id=intent_id,
        nest_id=nest_id,
        intent={
            "intent_id": intent_id,
            "tenant_id": "trisla-5m1-test",
            "service_type": service_type,
            "sla_requirements": {"latency": "10ms", "reliability": 0.99},
        },
        nest=None,
        context={},
    )


def _decision_input_from_evaluate(sla_input: SLAEvaluateInput) -> DecisionInput:
    intent_raw = sla_input.intent
    intent = SLAIntent(
        intent_id=intent_raw["intent_id"],
        tenant_id=intent_raw.get("tenant_id"),
        service_type=SliceType(intent_raw["service_type"]),
        sla_requirements=intent_raw.get("sla_requirements", {}),
    )
    return DecisionInput(
        intent=intent,
        nest=resolve_nest_for_evaluate(sla_input),
        context=sla_input.context,
    )


def _governance_nest_id_for(service_type: str, intent_id: str, nest_id: str) -> str:
    sla_input = _sla_evaluate(service_type, intent_id, nest_id)
    decision_input = _decision_input_from_evaluate(sla_input)
    result = DecisionResult(
        decision_id=f"dec-{intent_id}",
        intent_id=intent_id,
        nest_id=nest_id,
        action=DecisionAction.ACCEPT,
        reasoning="test",
        confidence=0.5,
        ml_risk_score=0.4,
        metadata={"decision_mode": "decision_score", "decision_score": 0.82},
    )
    enrich_lifecycle_governance_metadata(result, decision_input)
    gov = (result.metadata or {}).get("governance_event") or {}
    return gov.get("nest_id")


def test_resolve_nest_from_top_level_nest_id_only():
    intent_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    nest_id = f"nest-{intent_id}"
    sla_input = _sla_evaluate("URLLC", intent_id, nest_id)
    nest = resolve_nest_for_evaluate(sla_input)
    assert nest is not None
    assert nest.nest_id == nest_id
    assert nest.intent_id == intent_id


def test_resolve_nest_prefers_explicit_nest_dict():
    intent_id = "11111111-2222-3333-4444-555555555555"
    nest_id = f"nest-{intent_id}"
    sla_input = SLAEvaluateInput(
        intent_id=intent_id,
        nest_id="nest-should-not-win",
        intent={"intent_id": intent_id, "service_type": "eMBB", "sla_requirements": {}},
        nest={
            "nest_id": nest_id,
            "intent_id": intent_id,
            "network_slices": [],
            "resources": {},
            "status": "generated",
        },
    )
    nest = resolve_nest_for_evaluate(sla_input)
    assert nest is not None
    assert nest.nest_id == nest_id


def test_governance_event_nest_id_urllc():
    intent_id = "2c9869d1-dde8-47ca-a760-e4c0af6aefa5"
    nest_id = f"nest-{intent_id}"
    assert _governance_nest_id_for("URLLC", intent_id, nest_id) == nest_id


def test_governance_event_nest_id_embb():
    intent_id = "084e9760-8673-4b8b-8043-cc6f7081abc8"
    nest_id = f"nest-{intent_id}"
    assert _governance_nest_id_for("eMBB", intent_id, nest_id) == nest_id


def test_governance_event_nest_id_mmtc():
    intent_id = "6144d04e-acf4-48bb-8a19-f14925393f76"
    nest_id = f"nest-{intent_id}"
    assert _governance_nest_id_for("mMTC", intent_id, nest_id) == nest_id


def test_lifecycle_event_nest_id_matches_governance():
    intent_id = "6c286fc7-c748-45e4-a14b-c1a34128bca4"
    nest_id = f"nest-{intent_id}"
    sla_input = _sla_evaluate("eMBB", intent_id, nest_id)
    decision_input = _decision_input_from_evaluate(sla_input)
    result = DecisionResult(
        decision_id=f"dec-{intent_id}",
        intent_id=intent_id,
        nest_id=nest_id,
        action=DecisionAction.ACCEPT,
        reasoning="test",
        confidence=0.5,
        metadata={},
    )
    enrich_lifecycle_governance_metadata(result, decision_input)
    md = result.metadata or {}
    assert md["governance_event"]["nest_id"] == nest_id
    assert md["lifecycle_event"]["nest_id"] == nest_id


def test_no_nest_id_yields_null_governance_nest():
    intent_id = "00000000-0000-0000-0000-000000000001"
    sla_input = SLAEvaluateInput(
        intent_id=intent_id,
        nest_id=None,
        intent={"intent_id": intent_id, "service_type": "URLLC", "sla_requirements": {}},
        nest=None,
    )
    assert resolve_nest_for_evaluate(sla_input) is None
