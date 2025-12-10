from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ContractStatus(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    VIOLATED = "VIOLATED"
    RENEGOTIATED = "RENEGOTIATED"
    TERMINATED = "TERMINATED"


class SLARequirements(BaseModel):
    latency: Optional[Dict[str, Any]] = None
    throughput: Optional[Dict[str, Any]] = None
    reliability: Optional[float] = None
    availability: Optional[float] = None
    jitter: Optional[str] = None
    packet_loss: Optional[float] = None


class Contract(BaseModel):
    id: str
    tenant_id: str
    intent_id: str
    nest_id: str
    decision_id: str
    blockchain_tx_hash: Optional[str] = None
    status: ContractStatus
    version: int
    sla_requirements: SLARequirements
    domains: List[str]
    created_at: datetime
    activated_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None
    contract_metadata: Optional[Dict[str, Any]] = None  # Renamed from 'metadata' (SQLAlchemy reserved word)

    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    tenant_id: str
    intent_id: str
    nest_id: str
    decision_id: str
    blockchain_tx_hash: Optional[str] = None
    sla_requirements: SLARequirements
    domains: List[str]
    contract_metadata: Optional[Dict[str, Any]] = None  # Renamed from 'metadata' (SQLAlchemy reserved word)


class ContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    activated_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None


class ViolationType(str, Enum):
    LATENCY = "LATENCY"
    THROUGHPUT = "THROUGHPUT"
    RELIABILITY = "RELIABILITY"
    AVAILABILITY = "AVAILABILITY"
    JITTER = "JITTER"
    PACKET_LOSS = "PACKET_LOSS"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ViolationStatus(str, Enum):
    DETECTED = "DETECTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class Violation(BaseModel):
    id: str
    contract_id: str
    violation_type: ViolationType
    metric_name: str
    expected_value: Any
    actual_value: Any
    severity: Severity
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    status: ViolationStatus

    class Config:
        from_attributes = True


class RenegotiationReason(str, Enum):
    VIOLATION = "VIOLATION"
    TENANT_REQUEST = "TENANT_REQUEST"
    OPTIMIZATION = "OPTIMIZATION"


class RenegotiationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Renegotiation(BaseModel):
    id: str
    contract_id: str
    previous_version: int
    new_version: int
    reason: RenegotiationReason
    changes: Dict[str, Any]
    status: RenegotiationStatus
    requested_at: datetime
    completed_at: Optional[datetime] = None
    requested_by: str

    class Config:
        from_attributes = True


class PenaltyType(str, Enum):
    REFUND = "REFUND"
    CREDIT = "CREDIT"
    TERMINATION = "TERMINATION"


class PenaltyStatus(str, Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    WAIVED = "WAIVED"


class Penalty(BaseModel):
    id: str
    contract_id: str
    violation_id: str
    penalty_type: PenaltyType
    amount: Optional[float] = None
    percentage: Optional[float] = None
    applied_at: datetime
    status: PenaltyStatus

    class Config:
        from_attributes = True


