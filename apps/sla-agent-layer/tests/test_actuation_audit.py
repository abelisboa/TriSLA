"""O8C Wave 1 actuation audit pipeline tests."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuation.models import ActuationRequestIn, AuthorizationState, RiskLevel
from actuation.service import authorize_actuation, submit_actuation_request
from actuation.store import list_recent, load_record


@pytest.fixture(autouse=True)
def audit_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTUATION_AUDIT_STORE_PATH", str(tmp_path))
    yield tmp_path


def test_submit_safe_act_gov_004_auto_policy():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="intent-1",
            nsi_id="nsi-1",
            action_type="ACT-GOV-004",
            action_domain="GOV",
            risk_level=RiskLevel.SAFE,
            requested_by="test",
        )
    )
    assert resp.request.authorization_state == AuthorizationState.AUTH_POLICY
    assert resp.request.domain_mutation is False
    assert resp.request.executed is False
    assert resp.request.contract_version == "o8b-v1"


def test_submit_high_risk_denied():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="intent-2",
            nsi_id="nsi-2",
            action_type="ACT-RAN-002",
            action_domain="RAN",
            risk_level=RiskLevel.HIGH_RISK,
            requested_by="test",
        )
    )
    assert resp.request.authorization_state == AuthorizationState.AUTH_DENIED


def test_authorize_operator_transition():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="intent-3",
            nsi_id="nsi-3",
            action_type="ACT-ORCH-005",
            action_domain="ORCH",
            risk_level=RiskLevel.CONTROLLED,
            requested_by="test",
        )
    )
    assert resp.request.authorization_state == AuthorizationState.AUTH_PENDING
    auth = authorize_actuation(
        resp.request.request_id,
        AuthorizationState.AUTH_OPERATOR,
        authorized_by="operator@test",
        reason="wave1 test",
    )
    assert auth.request.authorization_state == AuthorizationState.AUTH_OPERATOR
    stored = load_record(resp.request.request_id)
    assert stored is not None
    assert stored.governance.get("authorized_by") == "operator@test"


def test_persistence_roundtrip():
    submit_actuation_request(
        ActuationRequestIn(
            intent_id="i",
            action_type="ACT-ASSUR-004",
            action_domain="ASSUR",
            risk_level=RiskLevel.SAFE,
        )
    )
    records = list_recent()
    assert len(records) >= 1
    assert records[0].governance.get("audit_only") is True


def test_no_domain_mutation_flag():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="i",
            action_type="ACT-GOV-004",
            action_domain="GOV",
            risk_level=RiskLevel.SAFE,
        )
    )
    assert resp.message == "scaffold_no_domain_mutation"
