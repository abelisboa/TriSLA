"""O8C W3 ACT-ORCH-005 controlled admission throttle tests."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuation.admission_throttle_store import (
    ACT_ORCH_005,
    ThrottleState,
    admission_allowed,
    apply_restored,
    gate_status,
    load_throttle,
)
from actuation.models import ActuationRequestIn, AuthorizationState, ExecutionState, RiskLevel, VerifyState
from actuation.service import (
    authorize_actuation,
    execute_actuation,
    rollback_actuation,
    submit_actuation_request,
    verify_actuation,
)
from actuation.store import load_record


@pytest.fixture(autouse=True)
def stores(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTUATION_AUDIT_STORE_PATH", str(tmp_path / "audit"))
    monkeypatch.setenv("ADMISSION_THROTTLE_STORE_PATH", str(tmp_path / "throttle"))
    yield tmp_path


def _submit_orch005():
    return submit_actuation_request(
        ActuationRequestIn(
            intent_id="intent-orch005",
            nsi_id="nsi-13",
            action_type=ACT_ORCH_005,
            action_domain="ORCHESTRATION",
            risk_level=RiskLevel.SAFE,
            requested_by="w3_test",
        )
    )


def test_gate_normal_by_default():
    assert admission_allowed() is True
    assert gate_status()["throttle_state"] == "NORMAL"


def test_auth_policy_denied_for_orch005():
    resp = _submit_orch005()
    assert resp.request.authorization_state == AuthorizationState.AUTH_PENDING
    auth = authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_POLICY)
    assert auth.request.authorization_state == AuthorizationState.AUTH_DENIED


def test_auth_governance_accepted():
    resp = _submit_orch005()
    auth = authorize_actuation(
        resp.request.request_id,
        AuthorizationState.AUTH_GOVERNANCE,
        authorized_by="governance@test",
    )
    assert auth.request.authorization_state == AuthorizationState.AUTH_GOVERNANCE


def test_full_lifecycle_throttle_restore():
    resp = _submit_orch005()
    authorize_actuation(
        resp.request.request_id,
        AuthorizationState.AUTH_OPERATOR,
        authorized_by="operator@test",
        reason="w3 load test",
    )
    assert admission_allowed() is True

    exe = execute_actuation(resp.request.request_id)
    assert exe.request.execution_state == ExecutionState.SUCCEEDED
    assert exe.request.domain_mutation is True
    assert exe.request.executed is True
    assert admission_allowed() is False
    assert load_throttle().state == ThrottleState.THROTTLED

    ver = verify_actuation(resp.request.request_id)
    assert ver.request.verify_state == VerifyState.PASSED

    rb = rollback_actuation(resp.request.request_id, reason="w3 restore")
    assert rb.request.execution_state == ExecutionState.ROLLED_BACK
    assert admission_allowed() is True
    assert load_throttle().state == ThrottleState.NORMAL


def test_rollback_restores_gate():
    apply_restored(actor="test", reason="reset", request_id="manual")
    assert gate_status()["admission_allowed"] is True


def test_real_domain_action_flags():
    resp = _submit_orch005()
    authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_OPERATOR)
    execute_actuation(resp.request.request_id)
    stored = load_record(resp.request.request_id)
    assert stored.governance.get("real_domain_action") is True
    assert stored.governance.get("scaffold") == "W3"
