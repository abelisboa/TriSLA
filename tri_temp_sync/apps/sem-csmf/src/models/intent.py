"""
Modelos de Intent para SEM-CSMF
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class SliceType(str, Enum):
    """Tipos de network slice"""
    EMBB = "eMBB"  # Enhanced Mobile Broadband
    URLLC = "URLLC"  # Ultra-Reliable Low-Latency Communications
    MMTC = "mMTC"  # massive Machine-Type Communications


class SLARequirements(BaseModel):
    """Requisitos de SLA"""
    latency: Optional[str] = Field(None, description="Latência máxima (ex: 10ms)")
    throughput: Optional[str] = Field(None, description="Throughput mínimo (ex: 100Mbps)")
    reliability: Optional[float] = Field(None, description="Confiabilidade (ex: 0.999)")
    jitter: Optional[str] = Field(None, description="Jitter máximo (ex: 5ms)")
    coverage: Optional[str] = Field(None, description="Cobertura (ex: Urban, Rural)")


class Intent(BaseModel):
    """Modelo de Intent"""
    intent_id: str = Field(..., description="ID único do intent")
    tenant_id: Optional[str] = Field(None, description="ID do tenant")
    service_type: SliceType = Field(..., description="Tipo de serviço/slice")
    sla_requirements: SLARequirements = Field(..., description="Requisitos de SLA")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent_id": "intent-001",
                "tenant_id": "tenant-001",
                "service_type": "eMBB",
                "sla_requirements": {
                    "latency": "10ms",
                    "throughput": "100Mbps",
                    "reliability": 0.999,
                    "coverage": "Urban"
                }
            }
        }


class IntentResponse(BaseModel):
    """Resposta de criação de intent"""
    intent_id: str
    status: str
    nest_id: Optional[str] = None
    message: str

