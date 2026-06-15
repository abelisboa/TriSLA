"""ACT-TN-002 dry-run orchestration (Authorize → Execute → Verify → Rollback)."""
from __future__ import annotations

from datetime import datetime, timezone

from actuation.metrics import (
    TRISLA_TRANSPORT_DRYRUN_SUCCESS_TOTAL,
    TRISLA_TRANSPORT_DRYRUN_TOTAL,
    TRISLA_TRANSPORT_DRYRUN_VERIFY_TOTAL,
)
from actuation.models import (
    ActuationAuditResponse,
    ActuationRecord,
    AuthorizationState,
    ExecutionState,
    VerifyState,
)
from actuation.onos_get import onos_topology_snapshot
from actuation.transport_dryrun import (
    ACT_TN_002,
    build_dryrun_payload,
    build_rollback_metadata,
    validate_payload,
)
from actuation.verify import VERIFY_ACTION, build_verify_audit_entry

TN002_REQUIRED_AUTH = AuthorizationState.AUTH_OPERATOR


def is_tn002(record: ActuationRecord) -> bool:
    return record.request.action_type == ACT_TN_002


def enforce_tn002_authorization(new_state: AuthorizationState) -> AuthorizationState:
    """ACT-TN-002 requires AUTH_OPERATOR; anything else → AUTH_DENIED."""
    if new_state == TN002_REQUIRED_AUTH:
        return TN002_REQUIRED_AUTH
    return AuthorizationState.AUTH_DENIED


def execute_tn002_dryrun(
    record: ActuationRecord,
    executed_by: str,
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    req = record.request
    if req.authorization_state != TN002_REQUIRED_AUTH:
        raise ValueError("ACT-TN-002 requires AUTH_OPERATOR authorization")

    now = datetime.now(timezone.utc)
    payload = build_dryrun_payload(req.intent_id, req.nsi_id, req.metadata)
    valid, msg = validate_payload(payload)
    if not valid:
        raise ValueError(f"payload validation failed: {msg}")

    TRISLA_TRANSPORT_DRYRUN_TOTAL.labels(action_type=ACT_TN_002).inc()

    req.execution_state = ExecutionState.EXECUTING
    req.executing_at = now
    record.governance["executed_by"] = executed_by
    record.governance["execution_mode"] = "tn002_dryrun_no_onos_post"
    record.governance["onos_mutation"] = False
    record.governance["intent_payload"] = payload.model_dump()
    record.governance["onos_shape"] = payload.to_onos_shape()

    topology = onos_topology_snapshot()
    record.governance["onos_get_validation"] = topology

    if simulate_failure:
        req.execution_state = ExecutionState.FAILED
        req.executed_at = datetime.now(timezone.utc)
        record.updated_at = req.executed_at
        return ActuationAuditResponse(status="failed", request=req, message="tn002_dryrun_simulated_failure")

    req.execution_state = ExecutionState.SUCCEEDED
    req.executed_at = datetime.now(timezone.utc)
    req.domain_mutation = False
    req.executed = False
    record.governance["dryrun_validated"] = True
    record.updated_at = req.executed_at

    TRISLA_TRANSPORT_DRYRUN_SUCCESS_TOTAL.labels(action_type=ACT_TN_002).inc()

    return ActuationAuditResponse(
        status="executed",
        request=req,
        message="tn002_dryrun_no_onos_mutation",
    )


def verify_tn002_dryrun(
    record: ActuationRecord,
    verified_by: str,
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    req = record.request
    if req.execution_state != ExecutionState.SUCCEEDED:
        raise ValueError(f"cannot verify TN-002: execution state {req.execution_state.value}")

    passed = not simulate_failure
    req.verify_state = VerifyState.PASSED if passed else VerifyState.FAILED
    req.verified_at = datetime.now(timezone.utc)
    record.governance["verify"] = build_verify_audit_entry(
        req.intent_id,
        req.nsi_id,
        req.request_id,
        passed=passed,
        verified_by=verified_by,
    )
    record.governance["verify"]["tn002"] = True
    record.updated_at = req.verified_at

    TRISLA_TRANSPORT_DRYRUN_VERIFY_TOTAL.labels(
        verify_state=req.verify_state.value,
    ).inc()

    return ActuationAuditResponse(
        status="verified" if passed else "verify_failed",
        request=req,
        message=f"{VERIFY_ACTION}_tn002_dryrun_registered",
    )


def rollback_tn002_dryrun(
    record: ActuationRecord,
    rolled_back_by: str,
    reason: str | None = None,
) -> ActuationAuditResponse:
    from uuid import uuid4

    req = record.request
    if req.execution_state not in (ExecutionState.SUCCEEDED, ExecutionState.FAILED):
        raise ValueError(f"cannot rollback TN-002: execution state {req.execution_state.value}")

    payload_data = record.governance.get("intent_payload") or {}
    from actuation.transport_dryrun import OnosIntentDryRunPayload

    try:
        payload = OnosIntentDryRunPayload.model_validate(payload_data)
        rollback_meta = build_rollback_metadata(payload)
    except Exception:
        rollback_meta = {"rollback_mode": "metadata_only", "onos_delete_forbidden": True}

    req.execution_state = ExecutionState.ROLLED_BACK
    req.rollback_reference = str(uuid4())
    req.rolled_back_at = datetime.now(timezone.utc)
    record.governance["rolled_back_by"] = rolled_back_by
    if reason:
        record.governance["rollback_reason"] = reason
    record.governance["rollback"] = rollback_meta
    record.governance["onos_mutation"] = False
    record.updated_at = req.rolled_back_at

    return ActuationAuditResponse(status="rolled_back", request=req, message="tn002_rollback_metadata_only")
