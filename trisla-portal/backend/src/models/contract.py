from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.models.database import Base
from src.schemas.contracts import (
    ContractStatus,
    ViolationType,
    Severity,
    ViolationStatus,
    RenegotiationReason,
    RenegotiationStatus,
    PenaltyType,
    PenaltyStatus,
)


class ContractModel(Base):
    __tablename__ = "contracts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    intent_id = Column(String, nullable=False)
    nest_id = Column(String, nullable=False)
    decision_id = Column(String, nullable=False)
    blockchain_tx_hash = Column(String, nullable=True)
    status = Column(SQLEnum(ContractStatus), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    sla_requirements = Column(JSON, nullable=False)
    domains = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    activated_at = Column(DateTime, nullable=True)
    terminated_at = Column(DateTime, nullable=True)
    contract_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (SQLAlchemy reserved word)

    violations = relationship("ViolationModel", back_populates="contract", cascade="all, delete-orphan")
    renegotiations = relationship("RenegotiationModel", back_populates="contract", cascade="all, delete-orphan")
    penalties = relationship("PenaltyModel", back_populates="contract", cascade="all, delete-orphan")


class ViolationModel(Base):
    __tablename__ = "violations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    violation_type = Column(SQLEnum(ViolationType), nullable=False)
    metric_name = Column(String, nullable=False)
    expected_value = Column(JSON, nullable=True)
    actual_value = Column(JSON, nullable=True)
    severity = Column(SQLEnum(Severity), nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(ViolationStatus), nullable=False, index=True)

    contract = relationship("ContractModel", back_populates="violations")
    penalties = relationship("PenaltyModel", back_populates="violation", cascade="all, delete-orphan")


class RenegotiationModel(Base):
    __tablename__ = "renegotiations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_version = Column(Integer, nullable=False)
    new_version = Column(Integer, nullable=False)
    reason = Column(SQLEnum(RenegotiationReason), nullable=False)
    changes = Column(JSON, nullable=False)
    status = Column(SQLEnum(RenegotiationStatus), nullable=False, index=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    requested_by = Column(String, nullable=False)

    contract = relationship("ContractModel", back_populates="renegotiations")


class PenaltyModel(Base):
    __tablename__ = "penalties"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    violation_id = Column(String, ForeignKey("violations.id", ondelete="CASCADE"), nullable=False, index=True)
    penalty_type = Column(SQLEnum(PenaltyType), nullable=False)
    amount = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(PenaltyStatus), nullable=False)

    contract = relationship("ContractModel", back_populates="penalties")
    violation = relationship("ViolationModel", back_populates="penalties")


