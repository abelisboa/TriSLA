from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any


class SLAInterpretRequest(BaseModel):
    """Request para interpretar PNL e enviar ao SEM-CSMF REAL - Payload minimalista"""
    intent: str
    tenant_id: Optional[str] = "default"


class SLASubmitRequest(BaseModel):
    """
    Request para enviar template técnico ao NASP (Decision Engine REAL)
    Conforme Capítulo 4 - Arquitetura TriSLA
    """
    template_id: str
    form_values: Dict[str, Any]
    tenant_id: str = "default"
    
    @field_validator('template_id')
    @classmethod
    def validate_template_id(cls, v: str) -> str:
        """Validar template_id"""
        if not v or not v.strip():
            raise ValueError('Template ID não pode ser vazio')
        return v.strip()
    
    @field_validator('form_values')
    @classmethod
    def validate_form_values(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validar e transformar form_values"""
        if not v:
            raise ValueError('Form values não podem ser vazios')
        
        # Transformar valores numéricos para formato correto
        form_values_corrigidos = {}
        for key, value in v.items():
            if value is None or value == "null" or value == "undefined":
                continue  # Pular valores inválidos
            if isinstance(value, (int, float)) and key in ['latency', 'latencia_maxima_ms']:
                # Garantir que latência seja string com unidade
                form_values_corrigidos[key] = f"{value}ms"
            elif isinstance(value, (int, float)) and key in ['reliability', 'availability', 'confiabilidade_percent', 'disponibilidade_percent']:
                # Garantir que percentuais estejam no formato correto
                form_values_corrigidos[key] = float(value)
            else:
                form_values_corrigidos[key] = value
        
        return form_values_corrigidos


class SLAStatusResponse(BaseModel):
    """Resposta com status do SLA (REAL do NASP)"""
    sla_id: str
    status: str
    tenant_id: str
    intent_id: Optional[str] = None
    nest_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SLAMetricsResponse(BaseModel):
    """
    Resposta padronizada com métricas REAIS do SLA (SLOs do NASP)
    Todos os campos vêm do NASP - SEM simulação
    """
    sla_id: str
    slice_status: Optional[str] = None  # ACTIVE | FAILED | PENDING | TERMINATED
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    throughput_ul: Optional[float] = None
    throughput_dl: Optional[float] = None
    packet_loss: Optional[float] = None
    availability: Optional[float] = None
    last_update: Optional[str] = None  # ISO8601
    # Campos adicionais para compatibilidade
    tenant_id: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class SLASubmitResponse(BaseModel):
    """
    Resposta padronizada para POST /api/v1/sla/submit
    Todos os campos vêm dos módulos reais - SEM simulação
    Resposta unificada do pipeline completo
    Conforme Capítulos 4, 5 e 6 da dissertação
    """
    # Campos principais unificados
    intent_id: Optional[str] = None
    service_type: Optional[str] = None
    sla_requirements: Optional[Dict[str, Any]] = None
    ml_prediction: Optional[Dict[str, Any]] = None
    decision: str  # ACCEPT | REJECT
    justification: Optional[str] = None
    reason: Optional[str] = None  # Alias para justification
    blockchain_tx_hash: Optional[str] = None
    tx_hash: Optional[str] = None  # Alias para blockchain_tx_hash
    sla_hash: Optional[str] = None  # Hash SHA-256 do SLA-aware (conforme Cap. 6)
    timestamp: Optional[str] = None  # ISO8601 - deve vir APENAS do Decision Engine
    status: str = "ok"  # ok | error
    
    # Campos auxiliares
    sla_id: Optional[str] = None
    nest_id: Optional[str] = None
    sem_csmf_status: str = "ERROR"  # OK | ERROR
    ml_nsmf_status: str = "ERROR"  # OK | ERROR
    bc_status: str = "ERROR"  # CONFIRMED | PENDING | ERROR
    sla_agent_status: str = "SKIPPED"  # OK | ERROR | SKIPPED
    block_number: Optional[int] = None

