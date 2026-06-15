"""ACT-ORCH-005 — Controlled admission throttle (first real domain action)."""
from __future__ import annotations

from datetime import datetime, timezone

from actuation.admission_throttle_store import (
    ACT_ORCH_005,
    apply_restored,
    apply_throttled,
    load_throttle,
)
from actuation.metrics import (
    TRISLA_ADMISSION_RESTORE_TOTAL,
    TRISLA_ADMISSION_THROTTLE_STATE,
    TRISLA_ADMISSION_THROTTLE_TOTAL,
    TRISLA_ADMISSION_THROTTLE_VERIFY_TOTAL,
)
from actuation.models import (
    ActuationAuditResponse,
    ActuationRecord,
    AuthorizationState,
    ExecutionState,
    VerifyState,
)
from actuation.verify import VERIFY_ACTION, build_verify_audit_entry

_ORCH005_ALLOWED_AUTH = frozenset(
    {
        AuthorizationState.AUTH_OPERATOR,
        AuthorizationState.AUTH_GOVERNANCE,
    }
)


def is_orch005(record: ActuationRecord) -> bool:
    return record.request.action_type == ACT_ORCH_005


def enforce_orch005_authorization(new_state: AuthorizationState) -> AuthorizationState:
    if new_state in _ORCH005_ALLOWED_AUTH:
        return new_state
    return AuthorizationState.AUTH_DENIED


def execute_orch005(
    record: ActuationRecord,
    executed_by: str,
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    req = record.request
    if req.authorization_state not in _ORCH005_ALLOWED_AUTH:
        raise ValueError("ACT-ORCH-005 requires AUTH_OPERATOR or AUTH_GOVERNANCE")

    now = datetime.now(timezone.utc)
    req.execution_state = ExecutionState.EXECUTING
    req.executing_at = now
    record.governance["executed_by"] = executed_by
    record.governance["execution_mode"] = "orch005_admission_throttle"
    record.governance["scaffold"] = "W3"
    record.updated_at = now

    if simulate_failure:
        req.execution_state = ExecutionState.FAILED
        req.executed_at = datetime.now(timezone.utc)
        return ActuationAuditResponse(status="failed", request=req, message="orch005_simulated_failure")

    throttle_rec = apply_throttled(
        reason=record.governance.get("authorization_reason") or "ACT-ORCH-005 execute",
        actor=executed_by,
        authorization_state=req.authorization_state.value,
        request_id=req.request_id,
    )

    req.execution_state = ExecutionState.SUCCEEDED
    req.executed_at = datetime.now(timezone.utc)
    req.domain_mutation = True
    req.executed = True
    record.governance["throttle"] = throttle_rec.model_dump(mode="json")
    record.governance["domain"] = "ORCHESTRATION"
    record.governance["real_domain_action"] = True
    record.updated_at = req.executed_at

    TRISLA_ADMISSION_THROTTLE_TOTAL.labels(action_type=ACT_ORCH_005).inc()
    TRISLA_ADMISSION_THROTTLE_STATE.set(1)

    return ActuationAuditResponse(
        status="executed",
        request=req,
        message="orch005_throttled_admission_gate_active",
    )


def verify_orch005(
    record: ActuationRecord,
    verified_by: str,
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    req = record.request
    if req.execution_state != ExecutionState.SUCCEEDED:
        raise ValueError(f"cannot verify ORCH-005: execution state {req.execution_state.value}")

    passed = not simulate_failure and load_throttle().state.value == "THROTTLED"
    req.verify_state = VerifyState.PASSED if passed else VerifyState.FAILED
    req.verified_at = datetime.now(timezone.utc)
    record.governance["verify"] = build_verify_audit_entry(
        req.intent_id,
        req.nsi_id,
        req.request_id,
        passed=passed,
        verified_by=verified_by,
    )
    record.governance["verify"]["orch005"] = True
    record.governance["verify"]["throttle_state_at_verify"] = load_throttle().state.value
    record.updated_at = req.verified_at

    TRISLA_ADMISSION_THROTTLE_VERIFY_TOTAL.labels(
        verify_state=req.verify_state.value,
    ).inc()

    return ActuationAuditResponse(
        status="verified" if passed else "verify_failed",
        request=req,
        message=f"{VERIFY_ACTION}_orch005_registered",
    )


def rollback_orch005(
    record: ActuationRecord,
    rolled_back_by: str,
    reason: str | None = None,
) -> ActuationAuditResponse:
    from uuid import uuid4

    req = record.request
    if req.execution_state not in (ExecutionState.SUCCEEDED, ExecutionState.FAILED):
        raise ValueError(f"cannot rollback ORCH-005: execution state {req.execution_state.value}")

    throttle_rec = apply_restored(
        actor=rolled_back_by,
        reason=reason or "ACT-ORCH-005 rollback",
        request_id=req.request_id,
    )

    req.execution_state = ExecutionState.ROLLED_BACK
    req.rollback_reference = str(uuid4())
    req.rolled_back_at = datetime.now(timezone.utc)
    record.governance["rolled_back_by"] = rolled_back_by
    if reason:
        record.governance["rollback_reason"] = reason
    record.governance["rollback"] = throttle_rec.model_dump(mode="json")
    record.governance["throttle_restored"] = True
    record.updated_at = req.rolled_back_at

    TRISLA_ADMISSION_RESTORE_TOTAL.labels(action_type=ACT_ORCH_005).inc()
    TRISLA_ADMISSION_THROTTLE_STATE.set(0)

    return ActuationAuditResponse(
        status="rolled_back",
        request=req,
        message="orch005_throttle_restored_admission_gate_open",
    )
