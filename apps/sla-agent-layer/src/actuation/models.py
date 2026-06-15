"""O8C actuation models (contract o8b-v1, W2A execution scaffold)."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

CONTRACT_VERSION = "o8b-v1"


class AuthorizationState(str, Enum):
    AUTH_PENDING = "AUTH_PENDING"
    AUTH_POLICY = "AUTH_POLICY"
    AUTH_OPERATOR = "AUTH_OPERATOR"
    AUTH_GOVERNANCE = "AUTH_GOVERNANCE"
    AUTH_DENIED = "AUTH_DENIED"
    AUTH_EXPIRED = "AUTH_EXPIRED"


class ExecutionState(str, Enum):
    NONE = "NONE"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    EXPIRED = "EXPIRED"


class VerifyState(str, Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    CONTROLLED = "CONTROLLED"
    HIGH_RISK = "HIGH_RISK"


_AUTHORIZED_FOR_EXECUTE = frozenset(
    {
        AuthorizationState.AUTH_POLICY,
        AuthorizationState.AUTH_OPERATOR,
        AuthorizationState.AUTH_GOVERNANCE,
    }
)


class ActuationRequestIn(BaseModel):
    intent_id: str
    nsi_id: str = "unknown"
    action_type: str
    action_domain: str
    risk_level: RiskLevel = RiskLevel.SAFE
    requested_by: str = "sla-agent-layer"
    decision_reference: Optional[str] = None
    correlation_reference: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ActuationRequest(ActuationRequestIn):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    authorization_state: AuthorizationState = AuthorizationState.AUTH_PENDING
    execution_state: ExecutionState = ExecutionState.NONE
    verify_state: VerifyState = VerifyState.NONE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    authorized_at: Optional[datetime] = None
    executing_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    rollback_reference: Optional[str] = None
    contract_version: str = CONTRACT_VERSION
    domain_mutation: bool = False
    executed: bool = False

    def is_authorized_for_execute(self) -> bool:
        return self.authorization_state in _AUTHORIZED_FOR_EXECUTE


class ActuationRecord(BaseModel):
    request: ActuationRequest
    governance: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthorizeRequest(BaseModel):
    request_id: str
    authorization_state: AuthorizationState
    authorized_by: str = "operator"
    reason: Optional[str] = None


class ExecuteRequest(BaseModel):
    request_id: str
    executed_by: str = "sla-agent-layer"
    simulate_failure: bool = False


class VerifyRequest(BaseModel):
    request_id: str
    verified_by: str = "sla-agent-layer"
    simulate_failure: bool = False


class RollbackRequest(BaseModel):
    request_id: str
    rolled_back_by: str = "operator"
    reason: Optional[str] = None


class ExpireRequest(BaseModel):
    request_id: Optional[str] = None
    force: bool = False


class ActuationAuditResponse(BaseModel):
    status: str
    request: ActuationRequest
    message: str = "scaffold_no_domain_mutation"
