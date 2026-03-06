"""
Modelos Pydantic do SLA-aware conforme Capítulo 6 da dissertação
Estrutura formal do SLA para registro no BC-NSSMF
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class SLO(BaseModel):
    """
    Service Level Objective (SLO)
    Conforme Capítulo 6 - SLOs numéricos válidos
    """
    name: str = Field(..., description="Nome do SLO (ex: latency, throughput, reliability)")
    value: int = Field(..., ge=0, description="Valor numérico do SLO")
    threshold: int = Field(..., ge=0, description="Threshold numérico do SLO")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "latency",
                "value": 10,
                "threshold": 20
            }
        }


class SLAAware(BaseModel):
    """
    Estrutura SLA-aware completa conforme Capítulo 6
    Preparada para registro no BC-NSSMF
    """
    slaHash: str = Field(..., description="Hash SHA-256 do SLA (bytes32)")
    customer: str = Field(..., description="ID do tenant/customer")
    serviceName: str = Field(..., description="Nome do serviço (ex: SLA-{sla_id})")
    intent_id: str = Field(..., description="ID do intent do SEM-CSMF")
    nest_id: Optional[str] = Field(None, description="ID do NEST gerado")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros técnicos do SLA")
    slos: List[SLO] = Field(..., min_length=1, description="Lista de SLOs numéricos válidos")
    decision: str = Field(..., description="Decisão: ACCEPT ou REJECT")
    justification: Optional[str] = Field(None, description="Justificativa da decisão")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Timestamp ISO8601")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados adicionais")
    
    class Config:
        json_schema_extra = {
            "example": {
                "slaHash": "0x1234567890abcdef...",
                "customer": "tenant-001",
                "serviceName": "SLA-001",
                "intent_id": "intent-001",
                "nest_id": "nest-001",
                "parameters": {
                    "slice_type": "URLLC",
                    "latency_max": 10
                },
                "slos": [
                    {"name": "latency", "value": 10, "threshold": 20},
                    {"name": "reliability", "value": 99999, "threshold": 99999}
                ],
                "decision": "ACCEPT",
                "justification": "SLA aceito com base em análise de recursos",
                "timestamp": "2025-01-15T10:00:00Z"
            }
        }


class SLARequestBC(BaseModel):
    """
    Request para registro no BC-NSSMF
    Conforme API do BC-NSSMF: POST /bc/register
    """
    customer: str
    serviceName: str
    slaHash: str
    slos: List[SLO]
