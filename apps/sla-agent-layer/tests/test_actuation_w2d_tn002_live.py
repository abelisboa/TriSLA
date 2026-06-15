"""ACT-TN-002 LIVE infrastructure tests (no real ONOS mutation)."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuation.failed_intent_cleanup import audit_failed_intents, cleanup_failed_intent, cleanup_enabled
from actuation.models import ActuationRequestIn, AuthorizationState, ExecutionState, RiskLevel, VerifyState
from actuation.onos_delete import delete_intent
from actuation.onos_post import get_intent, post_intent
from actuation.onos_rest import onos_request
from actuation.service import (
    authorize_actuation,
    execute_actuation,
    rollback_actuation,
    submit_actuation_request,
    verify_actuation,
)
from actuation.store import load_record
from actuation.topology_gate import TOPOLOGY_NOT_READY, is_topology_ready, topology_counts
from actuation.transport_dryrun import ACT_TN_002
from actuation.tn002_live import (
    execute_tn002_live,
    rollback_tn002_live,
    tn002_live_enabled,
    verify_tn002_live,
)


@pytest.fixture(autouse=True)
def audit_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTUATION_AUDIT_STORE_PATH", str(tmp_path))
    monkeypatch.setenv("CLOSED_LOOP_TRANSPORT_DRYRUN_ENABLED", "true")
    monkeypatch.setenv("TN002_LIVE_ENABLED", "false")
    monkeypatch.setenv("TN002_LIVE_DRYRUN_FALLBACK", "true")
    monkeypatch.setenv("TN002_FAILED_INTENT_CLEANUP_ENABLED", "false")
    yield tmp_path


@pytest.fixture
def mock_onos():
    with patch("actuation.tn002.onos_topology_snapshot") as m:
        m.return_value = {"onos_mutation": False, "method": "GET", "devices": {"count": 2}}
        yield m


def _tn002_request(**kwargs):
    defaults = {
        "intent_id": "intent-tn002-live",
        "nsi_id": "nsi-13",
        "action_type": ACT_TN_002,
        "action_domain": "TRANSPORT",
        "risk_level": RiskLevel.CONTROLLED,
        "metadata": {"src": "00:00:00:00:00:01", "dst": "00:00:00:00:00:02", "bandwidth": "500Mbps"},
    }
    defaults.update(kwargs)
    return submit_actuation_request(ActuationRequestIn(**defaults))


def test_tn002_live_flag_default_off():
    assert tn002_live_enabled() is False


def test_onos_post_client(mock_onos):
    with patch("actuation.onos_post.onos_request") as m:
        m.return_value = ({"intent": {"id": "0x999"}}, None, {"ok": True})
        key, _, err, audit = post_intent({"type": "PointToPointIntent"})
        assert err is None
        assert key == "0x999"
        assert audit["operation"] == "post_intent"


def test_onos_delete_client(mock_onos):
    with patch("actuation.onos_delete.onos_request") as m:
        m.return_value = ({}, None, {"ok": True})
        ok, err, audit = delete_intent("0x999")
        assert ok is True
        assert err is None
        assert audit["operation"] == "delete_intent"


def test_onos_request_timeout_retry():
    with patch("actuation.onos_rest.urlopen") as m:
        from urllib.error import URLError

        m.side_effect = URLError("timeout")
        _, err, audit = onos_request("GET", "/onos/v1/devices", retries=1)
        assert err == "ONOS_REST_UNREACHABLE"
        assert audit["attempts"] == 2


def test_topology_gate_not_ready():
    ready, snap = is_topology_ready({"devices": 0, "links": 0, "hosts": 0})
    assert ready is False
    assert snap["gate"] == TOPOLOGY_NOT_READY


def test_topology_gate_ready():
    ready, snap = is_topology_ready({"devices": 2, "links": 1, "hosts": 3})
    assert ready is True
    assert snap["gate"] == "TOPOLOGY_READY"


def test_topology_gate_denies_execute(monkeypatch, mock_onos):
    monkeypatch.setenv("TN002_LIVE_ENABLED", "true")
    with patch("actuation.tn002_live.is_topology_ready") as m:
        m.return_value = (False, {"devices": 0, "links": 0, "hosts": 0, "gate": TOPOLOGY_NOT_READY})
        resp = _tn002_request()
        authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_OPERATOR)
        out = execute_actuation(resp.request.request_id)
        assert out.status == "denied"
        assert out.message == TOPOLOGY_NOT_READY
        assert out.request.authorization_state == AuthorizationState.AUTH_DENIED


def test_tn002_live_execute_requires_auth_operator(monkeypatch, mock_onos):
    monkeypatch.setenv("TN002_LIVE_ENABLED", "true")
    with patch("actuation.tn002_live.is_topology_ready") as topo:
        topo.return_value = (True, {"devices": 1, "links": 1, "hosts": 1})
        resp = _tn002_request()
        with pytest.raises(ValueError, match="AUTH_OPERATOR"):
            execute_actuation(resp.request.request_id)


def test_tn002_live_full_lifecycle_mocked(monkeypatch, mock_onos):
    monkeypatch.setenv("TN002_LIVE_ENABLED", "true")
    with patch("actuation.tn002_live.is_topology_ready") as topo:
        topo.return_value = (True, {"devices": 1, "links": 1, "hosts": 1})
        with patch("actuation.tn002_live.post_intent") as post:
            post.return_value = ("0xabc", {"intent": {"id": "0xabc"}}, None, {"ok": True})
            with patch("actuation.tn002_live.get_intent") as get:
                get.return_value = ({"intent": {"id": "0xabc", "state": "INSTALLED"}}, None, {})
                with patch("actuation.tn002_live.delete_intent") as delete:
                    delete.return_value = (True, None, {"deleted": True})

                    resp = _tn002_request()
                    authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_OPERATOR)
                    exe = execute_actuation(resp.request.request_id)
                    assert exe.status == "executed"
                    assert exe.message == "tn002_live_onos_intent_created"
                    assert exe.request.domain_mutation is True

                    ver = verify_actuation(resp.request.request_id)
                    assert ver.request.verify_state == VerifyState.PASSED

                    rb = rollback_actuation(resp.request.request_id, reason="w2d test")
                    assert rb.request.execution_state == ExecutionState.ROLLED_BACK

                    stored = load_record(resp.request.request_id)
                    assert stored.governance["rollback"]["rollback_mode"] == "onos_delete"
                    assert stored.governance["rollback"]["rollback_status"] == "SUCCEEDED"
                    assert stored.governance["rollback"]["rollback_reference"]
                    assert stored.governance["rollback"]["rollback_timestamp"]


def test_tn002_live_rollback_metadata(monkeypatch):
    from actuation.models import ActuationRecord, ActuationRequest

    req = ActuationRequest(
        intent_id="i1",
        nsi_id="nsi1",
        action_type=ACT_TN_002,
        action_domain="TRANSPORT",
        risk_level=RiskLevel.CONTROLLED,
        authorization_state=AuthorizationState.AUTH_OPERATOR,
        execution_state=ExecutionState.SUCCEEDED,
    )
    record = ActuationRecord(
        request=req,
        governance={"onos_intent_key": "0xabc", "execution_mode": "tn002_live_onos_post"},
    )
    with patch("actuation.tn002_live.delete_intent") as delete:
        delete.return_value = (True, None, {})
        rb = rollback_tn002_live(record, "tester")
        assert rb.request.rollback_reference
        assert record.governance["rollback"]["rollback_status"] == "SUCCEEDED"


def test_failed_intent_audit_no_mutation():
    with patch("actuation.failed_intent_cleanup.list_intents") as m:
        m.return_value = (
            {"intents": [{"id": "0x288", "state": "FAILED", "appId": "org.onosproject.cli"}]},
            None,
            {},
        )
        failed, audit = audit_failed_intents()
        assert len(failed) == 1
        assert failed[0]["id"] == "0x288"


def test_failed_intent_cleanup_skipped_when_disabled():
    ok, env = cleanup_failed_intent("0x288")
    assert ok is False
    assert env["skipped"] == "TN002_FAILED_INTENT_CLEANUP_ENABLED=false"
    assert cleanup_enabled() is False


def test_flag_off_uses_dryrun_path(mock_onos):
    resp = _tn002_request()
    authorize_actuation(resp.request.request_id, AuthorizationState.AUTH_OPERATOR)
    exe = execute_actuation(resp.request.request_id)
    assert exe.message == "tn002_dryrun_no_onos_mutation"
    stored = load_record(resp.request.request_id)
    assert stored.governance.get("onos_mutation") is False
