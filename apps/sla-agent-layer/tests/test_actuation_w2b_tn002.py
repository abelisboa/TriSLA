"""O8C W2B ACT-TN-002 ONOS intent dry-run tests (no ONOS POST)."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuation.models import ActuationRequestIn, AuthorizationState, ExecutionState, RiskLevel, VerifyState
from actuation.service import (
    authorize_actuation,
    execute_actuation,
    rollback_actuation,
    submit_actuation_request,
    verify_actuation,
)
from actuation.store import load_record
from actuation.transport_dryrun import ACT_TN_002, build_dryrun_payload, validate_payload


@pytest.fixture(autouse=True)
def audit_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTUATION_AUDIT_STORE_PATH", str(tmp_path))
    monkeypatch.setenv("CLOSED_LOOP_TRANSPORT_DRYRUN_ENABLED", "true")
    yield tmp_path


@pytest.fixture
def mock_onos():
    with patch("actuation.tn002.onos_topology_snapshot") as m:
        m.return_value = {"onos_mutation": False, "method": "GET", "devices": {"count": 2}}
        yield m


def _tn002_request(**kwargs):
    defaults = {
        "intent_id": "intent-tn002",
        "nsi_id": "nsi-13",
        "action_type": ACT_TN_002,
        "action_domain": "TRANSPORT",
        "risk_level": RiskLevel.CONTROLLED,
        "metadata": {"src": "00:00:00:00:00:01", "dst": "00:00:00:00:00:02", "bandwidth": "500Mbps"},
    }
    defaults.update(kwargs)
    return submit_actuation_request(ActuationRequestIn(**defaults))


def test_payload_model_validates():
    p = build_dryrun_payload("i1", "nsi1", {"src": "a", "dst": "b"})
    ok, msg = validate_payload(p)
    assert ok is True
    assert msg == "valid"
    assert p.dry_run is True
    assert p.to_onos_shape()["dryRun"] is True
    assert p.to_onos_shape()["trisla"]["onos_post_forbidden"] is True


def test_tn002_submit_pending(mock_onos):
    resp = _tn002_request()
    assert resp.request.authorization_state == AuthorizationState.AUTH_PENDING
    assert resp.request.action_type == ACT_TN_002


def test_tn002_auth_policy_denied(mock_onos):
    resp = _tn002_request()
    auth = authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_POLICY)
    assert auth.request.authorization_state == AuthorizationState.AUTH_DENIED


def test_tn002_auth_operator_required(mock_onos):
    resp = _tn002_request()
    with pytest.raises(ValueError, match="AUTH_OPERATOR"):
        execute_actuation(resp.request.request_id)


def test_tn002_full_lifecycle(mock_onos):
    resp = _tn002_request()
    authorize_actuation(
        resp.request.request_id,
        AuthorizationState.AUTH_OPERATOR,
        authorized_by="operator@test",
    )
    exe = execute_actuation(resp.request.request_id)
    assert exe.request.execution_state == ExecutionState.SUCCEEDED
    assert exe.message == "tn002_dryrun_no_onos_mutation"
    assert exe.request.domain_mutation is False

    ver = verify_actuation(resp.request.request_id)
    assert ver.request.verify_state == VerifyState.PASSED

    rb = rollback_actuation(resp.request.request_id, reason="w2b test")
    assert rb.request.execution_state == ExecutionState.ROLLED_BACK

    stored = load_record(resp.request.request_id)
    assert stored.governance.get("onos_mutation") is False
    assert stored.governance.get("intent_payload", {}).get("dry_run") is True
    assert stored.governance.get("onos_get_validation", {}).get("method") == "GET"
    assert "intent_payload" in stored.governance
    assert stored.governance.get("rollback", {}).get("onos_delete_forbidden") is True


def test_tn002_no_onos_post_in_governance(mock_onos):
    resp = _tn002_request()
    authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_OPERATOR)
    execute_actuation(resp.request.request_id)
    stored = load_record(resp.request.request_id)
    assert stored.governance.get("execution_mode") == "tn002_dryrun_no_onos_post"
    shape = stored.governance.get("onos_shape", {})
    assert shape.get("trisla", {}).get("onos_post_forbidden") is True
