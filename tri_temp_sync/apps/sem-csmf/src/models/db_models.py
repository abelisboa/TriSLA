"""
Database Models - SEM-CSMF
Modelos SQLAlchemy para persistência
"""

from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base
from models.nest import NetworkSliceStatus


class IntentModel(Base):
    """Modelo de Intent no banco de dados"""
    __tablename__ = "intents"
    
    intent_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, nullable=True)
    service_type = Column(String, nullable=False)  # eMBB, URLLC, mMTC
    sla_requirements = Column(JSON, nullable=False)  # Armazena como JSON
    extra_metadata = Column(JSON, nullable=True)  # Renomeado de metadata para evitar conflito
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento com NESTs
    nests = relationship("NESTModel", back_populates="intent", cascade="all, delete-orphan")

# Alias para compatibilidade
IntentDB = IntentModel


class NESTModel(Base):
    """Modelo de NEST no banco de dados"""
    __tablename__ = "nests"
    
    nest_id = Column(String, primary_key=True, index=True)
    intent_id = Column(String, ForeignKey("intents.intent_id"), nullable=False)
    gst_id = Column(String, nullable=True)
    status = Column(String, nullable=False)  # generated, active, inactive, failed
    gst_data = Column(JSON, nullable=True)  # Armazena dados do GST
    extra_metadata = Column(JSON, nullable=True)  # Renomeado de metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    intent = relationship("IntentModel", back_populates="nests")
    network_slices = relationship("NetworkSliceModel", back_populates="nest", cascade="all, delete-orphan")

# Alias para compatibilidade
NESTDB = NESTModel


class NetworkSliceModel(Base):
    """Modelo de Network Slice no banco de dados"""
    __tablename__ = "network_slices"
    
    slice_id = Column(String, primary_key=True, index=True)
    nest_id = Column(String, ForeignKey("nests.nest_id"), nullable=False)
    slice_type = Column(String, nullable=False)  # eMBB, URLLC, mMTC
    resources = Column(JSON, nullable=False)  # Armazena recursos como JSON
    status = Column(String, nullable=False)  # generated, active, inactive, failed
    extra_metadata = Column(JSON, nullable=True)  # Renomeado de metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento
    nest = relationship("NESTModel", back_populates="network_slices")

# Alias para compatibilidade
NetworkSliceDB = NetworkSliceModel
