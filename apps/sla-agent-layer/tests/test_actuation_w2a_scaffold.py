"""O8C W2A governance execution scaffold tests (synthetic, no domain mutation)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuation.models import (
    ActuationRequestIn,
    AuthorizationState,
    ExecutionState,
    RiskLevel,
    VerifyState,
)
from actuation.service import (
    authorize_actuation,
    execute_actuation,
    expire_actuation,
    rollback_actuation,
    submit_actuation_request,
    verify_actuation,
)
from actuation.store import load_record


@pytest.fixture(autouse=True)
def audit_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTUATION_AUDIT_STORE_PATH", str(tmp_path))
    monkeypatch.setenv("ACTUATION_REQUEST_TTL_SECONDS", "300")
    monkeypatch.setenv("ACTUATION_AUTHORIZATION_TIMEOUT_SECONDS", "300")
    monkeypatch.setenv("ACTUATION_EXECUTION_TIMEOUT_SECONDS", "120")
    yield tmp_path


def _controlled_request(action_type="ACT-TN-002", domain="TRANSPORT"):
    return submit_actuation_request(
        ActuationRequestIn(
            intent_id="intent-w2a",
            nsi_id="nsi-w2a",
            action_type=action_type,
            action_domain=domain,
            risk_level=RiskLevel.CONTROLLED,
            requested_by="w2a_test",
        )
    )


def test_safe_lifecycle_execute_verify_rollback():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="safe-1",
            nsi_id="nsi-1",
            action_type="ACT-GOV-004",
            action_domain="GOV",
            risk_level=RiskLevel.SAFE,
        )
    )
    assert resp.request.authorization_state == AuthorizationState.AUTH_POLICY

    exe = execute_actuation(resp.request.request_id)
    assert exe.request.execution_state == ExecutionState.SUCCEEDED
    assert exe.request.domain_mutation is False
    assert exe.request.executed is False

    ver = verify_actuation(resp.request.request_id)
    assert ver.request.verify_state == VerifyState.PASSED
    assert ver.message.endswith("_registered_no_assurance_mutation")

    rb = rollback_actuation(resp.request.request_id, reason="w2a test")
    assert rb.request.execution_state == ExecutionState.ROLLED_BACK
    assert rb.request.rollback_reference is not None


def test_controlled_authorize_execute_verify():
    resp = _controlled_request()
    assert resp.request.authorization_state == AuthorizationState.AUTH_PENDING

    auth = authorize_actuation(
        resp.request.request_id,
        AuthorizationState.AUTH_OPERATOR,
        authorized_by="operator@test",
    )
    assert auth.request.authorization_state == AuthorizationState.AUTH_OPERATOR

    exe = execute_actuation(resp.request.request_id)
    assert exe.request.execution_state == ExecutionState.SUCCEEDED

    ver = verify_actuation(resp.request.request_id)
    assert ver.request.verify_state == VerifyState.PASSED

    stored = load_record(resp.request.request_id)
    assert stored.governance.get("verify", {}).get("verify_action") == "ACT-ASSUR-002"
    assert stored.governance.get("verify", {}).get("assurance_mutated") is False


def test_high_risk_denied_cannot_execute():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="hr-1",
            action_type="ACT-RAN-002",
            action_domain="RAN",
            risk_level=RiskLevel.HIGH_RISK,
        )
    )
    assert resp.request.authorization_state == AuthorizationState.AUTH_DENIED
    with pytest.raises(ValueError, match="denied"):
        execute_actuation(resp.request.request_id)


def test_execute_simulate_failure():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="fail-1",
            action_type="ACT-GOV-004",
            action_domain="GOV",
            risk_level=RiskLevel.SAFE,
        )
    )
    exe = execute_actuation(resp.request.request_id, simulate_failure=True)
    assert exe.request.execution_state == ExecutionState.FAILED


def test_verify_simulate_failure():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="vfail-1",
            action_type="ACT-GOV-004",
            action_domain="GOV",
            risk_level=RiskLevel.SAFE,
        )
    )
    execute_actuation(resp.request.request_id)
    ver = verify_actuation(resp.request.request_id, simulate_failure=True)
    assert ver.request.verify_state == VerifyState.FAILED


def test_expire_pending_authorization_force():
    resp = _controlled_request()
    results = expire_actuation(request_id=resp.request.request_id, force=True)
    assert len(results) == 1
    assert results[0].request.authorization_state == AuthorizationState.AUTH_EXPIRED


def test_audit_trail_fields():
    resp = _controlled_request()
    authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_OPERATOR)
    execute_actuation(resp.request.request_id)
    verify_actuation(resp.request.request_id)

    stored = load_record(resp.request.request_id)
    req = stored.request
    assert req.intent_id == "intent-w2a"
    assert req.nsi_id == "nsi-w2a"
    assert req.action_type == "ACT-TN-002"
    assert req.risk_level == RiskLevel.CONTROLLED
    assert req.authorization_state == AuthorizationState.AUTH_OPERATOR
    assert req.execution_state == ExecutionState.SUCCEEDED
    assert req.verify_state == VerifyState.PASSED
    assert req.contract_version == "o8b-v1"
    assert stored.governance.get("scaffold") == "W2B"


def test_no_domain_mutation_throughout_lifecycle():
    resp = submit_actuation_request(
        ActuationRequestIn(
            intent_id="ndm-1",
            action_type="ACT-GOV-004",
            action_domain="GOV",
            risk_level=RiskLevel.SAFE,
        )
    )
    execute_actuation(resp.request.request_id)
    stored = load_record(resp.request.request_id)
    assert stored.request.domain_mutation is False
    assert stored.request.executed is False
    assert stored.governance.get("execution_mode") == "scaffold_no_domain_mutation"
