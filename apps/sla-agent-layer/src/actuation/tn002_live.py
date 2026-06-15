"""ACT-TN-002 LIVE execution path (POST/DELETE ONOS — gated by TN002_LIVE_ENABLED)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Tuple
from uuid import uuid4

from actuation.metrics import (
    TRISLA_TRANSPORT_LIVE_ROLLBACK_TOTAL,
    TRISLA_TRANSPORT_LIVE_TOTAL,
    TRISLA_TRANSPORT_LIVE_TOPOLOGY_DENIED_TOTAL,
)
from actuation.models import (
    ActuationAuditResponse,
    ActuationRecord,
    AuthorizationState,
    ExecutionState,
    VerifyState,
)
from actuation.onos_delete import delete_intent
from actuation.onos_post import get_intent, post_intent
from actuation.topology_gate import TOPOLOGY_NOT_READY, is_topology_ready
from actuation.transport_dryrun import ACT_TN_002, build_dryrun_payload, validate_payload
from actuation.verify import VERIFY_ACTION, build_verify_audit_entry


class TopologyNotReadyError(Exception):
    def __init__(self, snapshot: dict):
        self.snapshot = snapshot
        super().__init__(TOPOLOGY_NOT_READY)


def tn002_live_enabled() -> bool:
    return os.getenv("TN002_LIVE_ENABLED", "false").lower() in ("1", "true", "yes", "on")


def tn002_live_dryrun_fallback() -> bool:
    return os.getenv("TN002_LIVE_DRYRUN_FALLBACK", "true").lower() in ("1", "true", "yes", "on")


def is_tn002_live_record(record: ActuationRecord) -> bool:
    return record.governance.get("execution_mode") == "tn002_live_onos_post"


def build_live_onos_body(record: ActuationRecord) -> dict:
    """ONOS PointToPointIntent body for live POST (only when flag enabled)."""
    req = record.request
    payload = build_dryrun_payload(req.intent_id, req.nsi_id, req.metadata)
    shape = payload.to_onos_shape()
    shape["dryRun"] = False
    shape["trisla"] = {
        "mode": "tn002_live",
        "request_id": req.request_id,
        "intent_id": req.intent_id,
        "nsi_id": req.nsi_id,
    }
    return shape


def assert_topology_ready() -> dict:
    ready, snap = is_topology_ready()
    if not ready:
        TRISLA_TRANSPORT_LIVE_TOPOLOGY_DENIED_TOTAL.inc()
        raise TopologyNotReadyError(snap)
    return snap


def execute_tn002_live(
    record: ActuationRecord,
    executed_by: str,
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    req = record.request
    if req.authorization_state != AuthorizationState.AUTH_OPERATOR:
        raise ValueError("ACT-TN-002 LIVE requires AUTH_OPERATOR authorization")

    if not tn002_live_enabled():
        raise ValueError("TN002_LIVE_ENABLED=false — use dry-run path")

    now = datetime.now(timezone.utc)
    topology = assert_topology_ready()

    payload = build_dryrun_payload(req.intent_id, req.nsi_id, req.metadata)
    valid, msg = validate_payload(payload)
    if not valid:
        raise ValueError(f"payload validation failed: {msg}")

    TRISLA_TRANSPORT_LIVE_TOTAL.labels(action_type=ACT_TN_002).inc()

    req.execution_state = ExecutionState.EXECUTING
    req.executing_at = now
    record.governance["executed_by"] = executed_by
    record.governance["execution_mode"] = "tn002_live_onos_post"
    record.governance["topology_gate"] = topology

    if simulate_failure:
        req.execution_state = ExecutionState.FAILED
        req.executed_at = datetime.now(timezone.utc)
        record.updated_at = req.executed_at
        record.governance["onos_mutation"] = False
        return ActuationAuditResponse(status="failed", request=req, message="tn002_live_simulated_failure")

    onos_body = build_live_onos_body(record)
    record.governance["onos_post_body"] = onos_body

    intent_key, resp, err, post_audit = post_intent(onos_body)
    record.governance["onos_post_audit"] = post_audit

    if err or not intent_key:
        req.execution_state = ExecutionState.FAILED
        req.executed_at = datetime.now(timezone.utc)
        record.governance["onos_mutation"] = False
        record.governance["onos_post_error"] = err
        record.updated_at = req.executed_at
        return ActuationAuditResponse(
            status="failed",
            request=req,
            message=f"tn002_live_post_failed:{err}",
        )

    req.execution_state = ExecutionState.SUCCEEDED
    req.executed_at = datetime.now(timezone.utc)
    req.domain_mutation = True
    req.executed = True
    record.governance["onos_intent_key"] = intent_key
    record.governance["onos_post_response"] = resp
    record.governance["onos_mutation"] = True
    record.updated_at = req.executed_at

    return ActuationAuditResponse(
        status="executed",
        request=req,
        message="tn002_live_onos_intent_created",
    )


def verify_tn002_live(
    record: ActuationRecord,
    verified_by: str,
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    req = record.request
    if req.execution_state != ExecutionState.SUCCEEDED:
        raise ValueError(f"cannot verify TN-002 LIVE: execution state {req.execution_state.value}")

    intent_key = record.governance.get("onos_intent_key")
    get_data, get_err, get_audit = (None, None, {})
    if intent_key and not simulate_failure:
        get_data, get_err, get_audit = get_intent(str(intent_key))

    passed = not simulate_failure and get_err is None
    req.verify_state = VerifyState.PASSED if passed else VerifyState.FAILED
    req.verified_at = datetime.now(timezone.utc)
    record.governance["verify"] = build_verify_audit_entry(
        req.intent_id,
        req.nsi_id,
        req.request_id,
        passed=passed,
        verified_by=verified_by,
    )
    record.governance["verify"]["tn002_live"] = True
    record.governance["onos_get_verify_audit"] = get_audit
    record.governance["onos_get_verify_data"] = get_data
    record.updated_at = req.verified_at

    return ActuationAuditResponse(
        status="verified" if passed else "verify_failed",
        request=req,
        message=f"{VERIFY_ACTION}_tn002_live_registered",
    )


def rollback_tn002_live(
    record: ActuationRecord,
    rolled_back_by: str,
    reason: str | None = None,
) -> ActuationAuditResponse:
    req = record.request
    if req.execution_state not in (ExecutionState.SUCCEEDED, ExecutionState.FAILED):
        raise ValueError(f"cannot rollback TN-002 LIVE: execution state {req.execution_state.value}")

    intent_key = record.governance.get("onos_intent_key")
    rollback_ref = str(uuid4())
    delete_ok = False
    delete_err = None
    delete_audit: dict = {}

    if intent_key:
        delete_ok, delete_err, delete_audit = delete_intent(str(intent_key))
        TRISLA_TRANSPORT_LIVE_ROLLBACK_TOTAL.labels(action_type=ACT_TN_002).inc()

    req.execution_state = ExecutionState.ROLLED_BACK
    req.rollback_reference = rollback_ref
    req.rolled_back_at = datetime.now(timezone.utc)
    record.governance["rolled_back_by"] = rolled_back_by
    if reason:
        record.governance["rollback_reason"] = reason
    record.governance["rollback"] = {
        "rollback_mode": "onos_delete",
        "onos_intent_key": intent_key,
        "delete_ok": delete_ok,
        "delete_error": delete_err,
        "rollback_reference": rollback_ref,
        "rollback_status": "SUCCEEDED" if delete_ok else "FAILED",
        "rollback_timestamp": req.rolled_back_at.isoformat(),
    }
    record.governance["onos_delete_audit"] = delete_audit
    record.updated_at = req.rolled_back_at

    status = "rolled_back" if delete_ok or not intent_key else "rollback_failed"
    return ActuationAuditResponse(status=status, request=req, message="tn002_live_onos_delete")
