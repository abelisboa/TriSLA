"""
Modelos Pydantic - Decision Engine
Modelos para entrada/saída de decisões alinhados com SEM-CSMF, ML-NSMF e BC-NSSMF
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime, timezone


class SliceType(str, Enum):
    """Tipos de network slice conforme arquitetura TriSLA"""
    EMBB = "eMBB"  # Enhanced Mobile Broadband
    URLLC = "URLLC"  # Ultra-Reliable Low-Latency Communications
    MMTC = "mMTC"  # massive Machine-Type Communications


class SLARequirement(BaseModel):
    """Requisitos de SLA individual"""
    name: str
    value: float
    threshold: float
    unit: Optional[str] = None


class DecisionAction(str, Enum):
    """Ações possíveis do Decision Engine"""
    ACCEPT = "AC"  # Accept - SLA aceito
    RENEGOTIATE = "RENEG"  # Renegotiate - Necessita renegociação
    REJECT = "REJ"  # Reject - SLA rejeitado


class RiskLevel(str, Enum):
    """Níveis de risco do ML-NSMF"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SLAIntent(BaseModel):
    """
    Intent de SLA recebido do SEM-CSMF (via I-01)
    Representa o intent semanticamente enriquecido
    """
    intent_id: str
    tenant_id: Optional[str] = None
    service_type: SliceType
    sla_requirements: Dict[str, Any]
    nest_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NestSubset(BaseModel):
    """
    Subconjunto do NEST (Network Slice Template)
    Usado como entrada técnica para o Decision Engine
    """
    nest_id: str
    intent_id: str
    network_slices: List[Dict[str, Any]]
    resources: Dict[str, Any]
    status: str
    metadata: Optional[Dict[str, Any]] = None


class MLPrediction(BaseModel):
    """
    Previsão do ML-NSMF (Interface I-05)
    """
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Score de risco (0-1)")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    features_importance: Optional[Dict[str, float]] = None
    explanation: Optional[str] = None
    timestamp: str


class DecisionInput(BaseModel):
    """
    Entrada agregada para o Decision Engine
    Combina dados do SEM-CSMF (NEST) e ML-NSMF (previsão)
    """
    intent: SLAIntent
    nest: Optional[NestSubset] = None
    ml_prediction: Optional[MLPrediction] = None
    context: Optional[Dict[str, Any]] = None


class DecisionResult(BaseModel):
    """
    Resultado da decisão do Decision Engine
    Alinhado com a arquitetura TriSLA (Capítulos 4, 5, 6)
    """
    decision_id: str = Field(..., description="ID único da decisão")
    intent_id: str
    nest_id: Optional[str] = None
    
    action: DecisionAction = Field(..., description="Ação decidida: AC/RENEG/REJ")
    
    reasoning: str = Field(..., description="Justificativa da decisão")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança na decisão")
    
    # Dados do ML
    ml_risk_score: Optional[float] = None
    ml_risk_level: Optional[RiskLevel] = None
    
    # SLOs relevantes
    slos: Optional[List[SLARequirement]] = None
    
    # Domínios afetados (RAN/Transporte/Core)
    domains: Optional[List[str]] = None
    
    # Metadados
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "dec-001",
                "intent_id": "intent-001",
                "nest_id": "nest-001",
                "action": "AC",
                "reasoning": "SLA URLLC com latência 10ms aceito. ML prevê risco baixo (0.2)",
                "confidence": 0.95,
                "ml_risk_score": 0.2,
                "ml_risk_level": "low",
                "slos": [
                    {"name": "latency", "value": 10, "threshold": 10, "unit": "ms"},
                    {"name": "reliability", "value": 0.999, "threshold": 0.999, "unit": "ratio"}
                ],
                "domains": ["RAN", "Transporte", "Core"]
            }
        }


class DecisionStatus(BaseModel):
    """Status de uma decisão"""
    decision_id: str
    intent_id: str
    action: DecisionAction
    status: str  # pending, completed, failed
    blockchain_tx_hash: Optional[str] = None
    timestamp: str

