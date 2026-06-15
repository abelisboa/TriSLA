"""P3 — decision_evidence metadata wiring + scientific safety validation."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from decision_evidence import (  # noqa: E402
    attach_decision_evidence_metadata,
    build_decision_evidence_from_context,
)
from models import (  # noqa: E402
    DecisionAction,
    DecisionInput,
    MLPrediction,
    NestSubset,
    RiskLevel,
    SLAIntent,
    SliceType,
)
from service import DecisionService  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
FROZEN_DIR = (
    REPO_ROOT
    / "sprint5m1_governance_nest_propagation_20260530T200758Z"
    / "evidence"
)

MINIMAL_SNAPSHOT = {"sla_id": "test-intent", "decision": "AC", "timestamp_utc": "2026-06-13T09:00:00Z"}
MINIMAL_EXPLANATION = {"summary": "test"}


def _ml_prediction() -> MLPrediction:
    return MLPrediction(
        risk_score=0.4,
        risk_level=RiskLevel.MEDIUM,
        confidence=0.82,
        raw_risk_score=0.4,
        slice_adjusted_risk_score=0.4,
    )


def _decision_input(context: dict | None = None) -> DecisionInput:
    return DecisionInput(
        intent=SLAIntent(
            intent_id="test-intent-p3",
            service_type=SliceType.URLLC,
            sla_requirements={"latency": "5ms", "reliability": 0.99999},
        ),
        nest=NestSubset(
            nest_id="nest-test",
            intent_id="test-intent-p3",
            network_slices=[],
            resources={},
            status="active",
        ),
        ml_prediction=_ml_prediction(),
        context=context or {"telemetry_snapshot": {"ran": {"prb_utilization": 0.15}}},
    )


def _xai_accept() -> dict:
    return {
        "decision_score": 0.821,
        "decision_band": "ACCEPT",
        "final_decision": "ACCEPT",
        "decision_mode": "decision_score",
        "decision_source": "decision_score_mode",
        "ran_prb_utilization_input": 15.0,
        "hard_prb_thresholds": {"reject": 0.4, "renegotiate": 0.25},
    }


def _xai_reject() -> dict:
    return {
        "decision_score": 0.21,
        "decision_band": "REJECT",
        "final_decision": "REJECT",
        "decision_mode": "decision_score",
        "decision_source": "policy_hard_reject",
        "ran_prb_utilization_input": 42.0,
        "hard_prb_thresholds": {"reject": 0.4, "renegotiate": 0.25},
    }


def _xai_prb_gate() -> dict:
    return {
        "decision_score": 0.55,
        "decision_band": "RENEGOTIATE",
        "final_decision": "RENEGOTIATE",
        "decision_mode": "hard_prb_gate",
        "decision_source": "PRB_HARD_RENEGOTIATE_THRESHOLD",
        "ran_prb_utilization_input": 27.65,
        "hard_prb_thresholds": {"reject": 95.0, "renegotiate": 25.0},
    }


async def _run_service_with_xai(
    xai_bundle: dict,
    action: DecisionAction,
    reasoning: str,
) -> dict:
    service = DecisionService()
    decision_input = _decision_input()
    slos = []
    domains = ["RAN"]

    with patch.object(
        service.engine,
        "_apply_decision_rules",
        return_value=(action, reasoning, slos, domains, xai_bundle),
    ), patch(
        "service.build_decision_snapshot",
        return_value=MINIMAL_SNAPSHOT,
    ), patch(
        "service.explain_decision",
        return_value=MINIMAL_EXPLANATION,
    ), patch(
        "service.persist_decision_evidence",
        return_value=True,
    ), patch.object(
        service.engine.bc_client,
        "register_sla_on_chain",
        return_value=None,
    ):
        result = await service.process_decision_from_input(decision_input)

    return result.metadata or {}


@pytest.mark.asyncio
async def test_t1_accept_decision_evidence_present():
    md = await _run_service_with_xai(
        _xai_accept(),
        DecisionAction.ACCEPT,
        "decision_score=0.821 band=ACCEPT",
    )
    assert isinstance(md.get("decision_evidence"), list)
    assert len(md["decision_evidence"]) >= 1


@pytest.mark.asyncio
async def test_t2_reject_decision_evidence_present():
    md = await _run_service_with_xai(
        _xai_reject(),
        DecisionAction.REJECT,
        "policy_hard_reject",
    )
    assert isinstance(md.get("decision_evidence"), list)
    assert len(md["decision_evidence"]) >= 1


@pytest.mark.asyncio
async def test_t3_prb_gate_decision_evidence_present():
    md = await _run_service_with_xai(
        _xai_prb_gate(),
        DecisionAction.RENEGOTIATE,
        "PRB_HARD_RENEGOTIATE_THRESHOLD",
    )
    evidence = md.get("decision_evidence")
    assert isinstance(evidence, list) and len(evidence) == 1
    assert evidence[0]["metric"] == "prb_utilization"
    assert evidence[0]["rule"] == "PRB_HARD_RENEGOTIATE_THRESHOLD"


@pytest.mark.asyncio
async def test_t4_scientific_fields_unchanged():
    xai = _xai_accept()
    before_keys = {
        "decision_score": xai["decision_score"],
        "decision_band": xai["decision_band"],
        "final_decision": xai["final_decision"],
    }
    md = await _run_service_with_xai(
        xai,
        DecisionAction.ACCEPT,
        "decision_score=0.821 band=ACCEPT",
    )
    assert md.get("decision_score") == before_keys["decision_score"]
    assert md.get("decision_band") == before_keys["decision_band"]
    assert md.get("final_decision") == before_keys["final_decision"]


def test_v1_builder_side_effect_free():
    context = {
        "telemetry_snapshot": {"ran": {"prb_utilization": 27.65}},
        "decision_score": 0.82,
        "decision_band": "ACCEPT",
    }
    snapshot = {"sla_compliance": 0.41, "final_score": 0.82}
    context_copy = copy.deepcopy(context)
    snapshot_copy = copy.deepcopy(snapshot)
    xai = _xai_prb_gate()

    build_decision_evidence_from_context(
        reasoning="PRB_HARD_RENEGOTIATE_THRESHOLD",
        decision_source="PRB_HARD_RENEGOTIATE_THRESHOLD",
        xai_bundle=xai,
        context=context,
    )

    assert context == context_copy
    assert snapshot == snapshot_copy


def test_v2_metadata_size_increase_acceptable():
    metadata = copy.deepcopy(_xai_accept())
    metadata["decision_snapshot"] = MINIMAL_SNAPSHOT
    size_before = len(json.dumps(metadata, default=str))
    attach_decision_evidence_metadata(
        metadata,
        reasoning="decision_score=0.821",
        xai_bundle=_xai_accept(),
        context={"telemetry_snapshot": {"ran": {"prb_utilization": 0.15}}},
    )
    size_after = len(json.dumps(metadata, default=str))
    delta = size_after - size_before
    assert "decision_evidence" in metadata
    assert delta < 4096
    assert delta > 0


@pytest.mark.parametrize(
    "frozen_file",
    ["submit_urllc.json", "submit_embb.json", "submit_mmtc.json"],
)
def test_v3_backward_compatibility(frozen_file: str):
    path = FROZEN_DIR / frozen_file
    if not path.is_file():
        pytest.skip(f"missing frozen payload {frozen_file}")
    frozen = json.loads(path.read_text(encoding="utf-8"))
    metadata = copy.deepcopy(frozen.get("metadata") or {})
    scientific_before = {
        "decision": frozen.get("decision"),
        "decision_score": metadata.get("decision_score"),
        "decision_band": metadata.get("decision_band"),
        "final_decision": metadata.get("final_decision"),
    }
    keys_before = set(metadata.keys())

    attach_decision_evidence_metadata(
        metadata,
        reasoning=str(metadata.get("decision_explanation_plain") or ""),
        xai_bundle=metadata,
        context={"telemetry_snapshot": metadata.get("telemetry_snapshot")},
    )

    assert keys_before.issubset(set(metadata.keys()))
    assert metadata.get("decision_score") == scientific_before["decision_score"]
    assert metadata.get("decision_band") == scientific_before["decision_band"]
    assert metadata.get("final_decision") == scientific_before["final_decision"]
    assert frozen.get("decision") == scientific_before["decision"]
    assert isinstance(metadata.get("decision_evidence"), list)


def test_de_to_metadata_propagation_unit():
    metadata: dict = {}
    attach_decision_evidence_metadata(
        metadata,
        reasoning="PRB_HARD_RENEGOTIATE_THRESHOLD",
        xai_bundle=_xai_prb_gate(),
        context={"telemetry_snapshot": {"ran": {"prb_utilization": 27.65}}},
    )
    assert metadata["decision_evidence"][0]["metric"] == "prb_utilization"
