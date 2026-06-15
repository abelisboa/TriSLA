"""Governance authorization + W2A execution scaffold (persistence only, no domain mutation)."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from actuation.metrics import (
    TRISLA_ACTUATION_AUTHORIZED_TOTAL,
    TRISLA_ACTUATION_BY_DOMAIN,
    TRISLA_ACTUATION_DENIED_TOTAL,
    TRISLA_ACTUATION_EXECUTING_GAUGE,
    TRISLA_ACTUATION_EXECUTING_TOTAL,
    TRISLA_ACTUATION_EXPIRED_TOTAL,
    TRISLA_ACTUATION_FAILED_TOTAL,
    TRISLA_ACTUATION_PENDING_TOTAL,
    TRISLA_ACTUATION_REQUESTS_TOTAL,
    TRISLA_ACTUATION_ROLLBACK_TOTAL,
    TRISLA_ACTUATION_SUCCEEDED_TOTAL,
    TRISLA_ACTUATION_VERIFY_TOTAL,
)
from actuation.models import (
    ActuationAuditResponse,
    ActuationRecord,
    ActuationRequest,
    ActuationRequestIn,
    AuthorizationState,
    ExecutionState,
    RiskLevel,
    VerifyState,
)
from actuation.store import count_executing, count_pending, list_recent, load_record, save_record
from actuation.ttl import (
    get_ttl_config,
    is_authorization_expired,
    is_execution_expired,
    is_request_expired,
)
from actuation.transport_dryrun import ACT_TN_002
from actuation.admission_throttle_store import ACT_ORCH_005
from actuation.orch005 import (
    enforce_orch005_authorization,
    execute_orch005,
    is_orch005,
    rollback_orch005,
    verify_orch005,
)
from actuation.tn002 import (
    enforce_tn002_authorization,
    execute_tn002_dryrun,
    is_tn002,
    rollback_tn002_dryrun,
    verify_tn002_dryrun,
)
from actuation.tn002_live import (
    TopologyNotReadyError,
    execute_tn002_live,
    is_tn002_live_record,
    rollback_tn002_live,
    tn002_live_dryrun_fallback,
    tn002_live_enabled,
    verify_tn002_live,
)
from actuation.topology_gate import TOPOLOGY_NOT_READY
from actuation.verify import VERIFY_ACTION, build_verify_audit_entry

_SAFE_AUTO_ACTIONS = frozenset(
    {
        "ACT-GOV-004",
        "ACT-ASSUR-001",
        "ACT-ASSUR-002",
        "ACT-ASSUR-003",
        "ACT-ASSUR-004",
        "ACT-GOV-003",
        "ACT-INTEL-001",
    }
)

_AUTHORIZED_STATES = frozenset(
    {
        AuthorizationState.AUTH_POLICY,
        AuthorizationState.AUTH_OPERATOR,
        AuthorizationState.AUTH_GOVERNANCE,
    }
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _initial_authorization(action_type: str, risk_level: RiskLevel) -> AuthorizationState:
    if action_type == ACT_ORCH_005:
        return AuthorizationState.AUTH_PENDING
    if risk_level == RiskLevel.HIGH_RISK:
        return AuthorizationState.AUTH_DENIED
    if risk_level == RiskLevel.SAFE and action_type in _SAFE_AUTO_ACTIONS:
        return AuthorizationState.AUTH_POLICY
    if risk_level == RiskLevel.CONTROLLED:
        return AuthorizationState.AUTH_PENDING
    if risk_level == RiskLevel.SAFE:
        return AuthorizationState.AUTH_POLICY
    return AuthorizationState.AUTH_PENDING


def _touch_gauges() -> None:
    TRISLA_ACTUATION_PENDING_TOTAL.set(count_pending())
    TRISLA_ACTUATION_EXECUTING_GAUGE.set(count_executing())


def _record_auth_metrics(req: ActuationRequest) -> None:
    TRISLA_ACTUATION_BY_DOMAIN.labels(
        action_domain=req.action_domain,
        authorization_state=req.authorization_state.value,
    ).inc()
    if req.authorization_state in _AUTHORIZED_STATES:
        TRISLA_ACTUATION_AUTHORIZED_TOTAL.labels(
            authorization_state=req.authorization_state.value,
            action_domain=req.action_domain,
        ).inc()
    if req.authorization_state == AuthorizationState.AUTH_DENIED:
        TRISLA_ACTUATION_DENIED_TOTAL.labels(
            action_type=req.action_type,
            action_domain=req.action_domain,
        ).inc()
    if req.authorization_state == AuthorizationState.AUTH_EXPIRED:
        TRISLA_ACTUATION_EXPIRED_TOTAL.labels(
            action_domain=req.action_domain,
            expire_reason="authorization_timeout",
        ).inc()
    _touch_gauges()


def _record_execution_metrics(req: ActuationRequest) -> None:
    labels = {"action_type": req.action_type, "action_domain": req.action_domain}
    if req.execution_state == ExecutionState.EXECUTING:
        TRISLA_ACTUATION_EXECUTING_TOTAL.labels(**labels).inc()
    elif req.execution_state == ExecutionState.SUCCEEDED:
        TRISLA_ACTUATION_SUCCEEDED_TOTAL.labels(**labels).inc()
    elif req.execution_state == ExecutionState.FAILED:
        TRISLA_ACTUATION_FAILED_TOTAL.labels(**labels).inc()
    elif req.execution_state == ExecutionState.ROLLED_BACK:
        TRISLA_ACTUATION_ROLLBACK_TOTAL.labels(action_domain=req.action_domain).inc()
    elif req.execution_state == ExecutionState.EXPIRED:
        TRISLA_ACTUATION_EXPIRED_TOTAL.labels(
            action_domain=req.action_domain,
            expire_reason="execution_timeout",
        ).inc()
    _touch_gauges()


def _record_verify_metrics(req: ActuationRequest) -> None:
    TRISLA_ACTUATION_VERIFY_TOTAL.labels(
        verify_state=req.verify_state.value,
        action_domain=req.action_domain,
    ).inc()


def _transport_dryrun_enabled() -> bool:
    import os

    return os.getenv("CLOSED_LOOP_TRANSPORT_DRYRUN_ENABLED", "true").lower() in ("1", "true", "yes", "on")


def _execute_tn002(
    record: ActuationRecord,
    executed_by: str,
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    if tn002_live_enabled():
        try:
            return execute_tn002_live(record, executed_by, simulate_failure=simulate_failure)
        except TopologyNotReadyError as exc:
            req = record.request
            req.authorization_state = AuthorizationState.AUTH_DENIED
            record.governance["topology_gate_denied"] = exc.snapshot
            record.updated_at = _now()
            return ActuationAuditResponse(status="denied", request=req, message=TOPOLOGY_NOT_READY)
    if _transport_dryrun_enabled() and tn002_live_dryrun_fallback():
        return execute_tn002_dryrun(record, executed_by, simulate_failure=simulate_failure)
    raise ValueError("ACT-TN-002 dry-run disabled")


def _base_governance(req: ActuationRequest) -> dict:
    return {
        "decision_reference": req.decision_reference,
        "correlation_reference": req.correlation_reference,
        "audit_only": True,
        "scaffold": "W2A",
        "domain_mutation": False,
    }


def submit_actuation_request(body: ActuationRequestIn) -> ActuationAuditResponse:
    req = ActuationRequest(**body.model_dump())
    req.authorization_state = _initial_authorization(req.action_type, req.risk_level)
    req.domain_mutation = False
    req.executed = False

    if req.authorization_state in _AUTHORIZED_STATES:
        req.authorized_at = _now()

    TRISLA_ACTUATION_REQUESTS_TOTAL.labels(
        action_type=req.action_type,
        action_domain=req.action_domain,
        risk_level=req.risk_level.value,
    ).inc()

    record = ActuationRecord(request=req, governance=_base_governance(req))
    if req.action_type == ACT_TN_002:
        record.governance["scaffold"] = "W2B"
        record.governance["action"] = ACT_TN_002
    if req.action_type == ACT_ORCH_005:
        record.governance["scaffold"] = "W3"
        record.governance["action"] = ACT_ORCH_005
    save_record(record)
    _record_auth_metrics(req)

    return ActuationAuditResponse(status="submitted", request=req)


def authorize_actuation(
    request_id: str,
    new_state: AuthorizationState,
    authorized_by: str = "operator",
    reason: str | None = None,
) -> ActuationAuditResponse:
    record = load_record(request_id)
    if not record:
        raise KeyError(f"request_id not found: {request_id}")

    previous = record.request.authorization_state
    if is_tn002(record):
        new_state = enforce_tn002_authorization(new_state)
    if is_orch005(record):
        new_state = enforce_orch005_authorization(new_state)
    record.request.authorization_state = new_state
    if new_state in _AUTHORIZED_STATES:
        record.request.authorized_at = _now()
    record.updated_at = _now()
    record.governance["authorized_by"] = authorized_by
    if reason:
        record.governance["authorization_reason"] = reason
    record.governance["previous_authorization_state"] = previous.value

    save_record(record)
    _record_auth_metrics(record.request)

    return ActuationAuditResponse(status="authorized", request=record.request)


def execute_actuation(
    request_id: str,
    executed_by: str = "sla-agent-layer",
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    record = load_record(request_id)
    if not record:
        raise KeyError(f"request_id not found: {request_id}")

    req = record.request
    if req.action_type == ACT_TN_002:
        resp = _execute_tn002(record, executed_by, simulate_failure=simulate_failure)
        save_record(record)
        _record_execution_metrics(record.request)
        return resp

    if req.action_type == ACT_ORCH_005:
        resp = execute_orch005(record, executed_by, simulate_failure=simulate_failure)
        save_record(record)
        _record_execution_metrics(record.request)
        return resp

    if req.authorization_state == AuthorizationState.AUTH_DENIED:
        raise ValueError("cannot execute: authorization denied")
    if req.authorization_state == AuthorizationState.AUTH_EXPIRED:
        raise ValueError("cannot execute: authorization expired")
    if not req.is_authorized_for_execute():
        raise ValueError(f"cannot execute: authorization state {req.authorization_state.value}")
    if req.execution_state not in (ExecutionState.NONE, ExecutionState.EXPIRED):
        raise ValueError(f"cannot execute: execution state {req.execution_state.value}")

    now = _now()
    req.execution_state = ExecutionState.EXECUTING
    req.executing_at = now
    record.governance["executed_by"] = executed_by
    record.governance["execution_mode"] = "scaffold_no_domain_mutation"
    record.updated_at = now
    save_record(record)
    _record_execution_metrics(req)

    if simulate_failure:
        req.execution_state = ExecutionState.FAILED
        req.executed_at = _now()
    else:
        req.execution_state = ExecutionState.SUCCEEDED
        req.executed_at = _now()

    req.domain_mutation = False
    req.executed = False
    record.updated_at = _now()
    save_record(record)
    _record_execution_metrics(req)

    status = "failed" if simulate_failure else "executed"
    return ActuationAuditResponse(status=status, request=req)


def verify_actuation(
    request_id: str,
    verified_by: str = "sla-agent-layer",
    simulate_failure: bool = False,
) -> ActuationAuditResponse:
    record = load_record(request_id)
    if not record:
        raise KeyError(f"request_id not found: {request_id}")

    req = record.request
    if is_tn002(record):
        if is_tn002_live_record(record):
            resp = verify_tn002_live(record, verified_by, simulate_failure=simulate_failure)
        else:
            resp = verify_tn002_dryrun(record, verified_by, simulate_failure=simulate_failure)
        save_record(record)
        _record_verify_metrics(record.request)
        return resp

    if is_orch005(record):
        resp = verify_orch005(record, verified_by, simulate_failure=simulate_failure)
        save_record(record)
        _record_verify_metrics(record.request)
        return resp

    if req.execution_state != ExecutionState.SUCCEEDED:
        raise ValueError(f"cannot verify: execution state {req.execution_state.value}")

    passed = not simulate_failure
    req.verify_state = VerifyState.PASSED if passed else VerifyState.FAILED
    req.verified_at = _now()
    record.governance["verify"] = build_verify_audit_entry(
        req.intent_id,
        req.nsi_id,
        req.request_id,
        passed=passed,
        verified_by=verified_by,
    )
    record.updated_at = _now()
    save_record(record)
    _record_verify_metrics(req)

    return ActuationAuditResponse(
        status="verified" if passed else "verify_failed",
        request=req,
        message=f"{VERIFY_ACTION}_registered_no_assurance_mutation",
    )


def rollback_actuation(
    request_id: str,
    rolled_back_by: str = "operator",
    reason: str | None = None,
) -> ActuationAuditResponse:
    record = load_record(request_id)
    if not record:
        raise KeyError(f"request_id not found: {request_id}")

    req = record.request
    if is_tn002(record):
        if is_tn002_live_record(record):
            resp = rollback_tn002_live(record, rolled_back_by, reason=reason)
        else:
            resp = rollback_tn002_dryrun(record, rolled_back_by, reason=reason)
        save_record(record)
        _record_execution_metrics(record.request)
        return resp

    if is_orch005(record):
        resp = rollback_orch005(record, rolled_back_by, reason=reason)
        save_record(record)
        _record_execution_metrics(record.request)
        return resp

    if req.execution_state not in (ExecutionState.SUCCEEDED, ExecutionState.FAILED):
        raise ValueError(f"cannot rollback: execution state {req.execution_state.value}")

    req.execution_state = ExecutionState.ROLLED_BACK
    req.rollback_reference = str(uuid4())
    req.rolled_back_at = _now()
    record.governance["rolled_back_by"] = rolled_back_by
    if reason:
        record.governance["rollback_reason"] = reason
    record.governance["rollback_mode"] = "metadata_only"
    record.updated_at = _now()
    save_record(record)
    _record_execution_metrics(req)

    return ActuationAuditResponse(status="rolled_back", request=req)


def expire_actuation(request_id: str | None = None, force: bool = False) -> list[ActuationAuditResponse]:
    cfg = get_ttl_config()
    targets = [load_record(request_id)] if request_id else list_recent(500)
    results: list[ActuationAuditResponse] = []

    for record in targets:
        if not record:
            continue
        req = record.request
        expired = False
        reason = ""

        if req.execution_state == ExecutionState.EXECUTING and req.executing_at:
            if force or is_execution_expired(req.executing_at, cfg):
                req.execution_state = ExecutionState.EXPIRED
                reason = "execution_timeout"
                expired = True
        elif req.authorization_state == AuthorizationState.AUTH_PENDING:
            if force or is_authorization_expired(req.created_at, cfg):
                req.authorization_state = AuthorizationState.AUTH_EXPIRED
                reason = "authorization_timeout"
                expired = True
        elif req.execution_state == ExecutionState.NONE and req.authorization_state in _AUTHORIZED_STATES:
            if force or is_request_expired(req.created_at, cfg):
                req.execution_state = ExecutionState.EXPIRED
                reason = "request_expiration"
                expired = True

        if expired:
            req.expired_at = _now()
            record.governance["expire_reason"] = reason
            record.updated_at = _now()
            save_record(record)
            if reason == "authorization_timeout":
                _record_auth_metrics(req)
            else:
                _record_execution_metrics(req)
            results.append(ActuationAuditResponse(status="expired", request=req))

    return results


def get_record(request_id: str) -> ActuationRecord | None:
    return load_record(request_id)
