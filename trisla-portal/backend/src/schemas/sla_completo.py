"""
Schemas Pydantic completos para SLA conforme dissertação
Capítulos 4, 5 e 6
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum


class CategoriaServico(str, Enum):
    """Categoria de serviço opcional"""
    URLLC = "URLLC"
    eMBB = "eMBB"
    mMTC = "mMBB"
    AUTO = "AUTO"


class TipoSlice(str, Enum):
    """Tipo de slice"""
    URLLC = "URLLC"
    eMBB = "eMBB"
    mMTC = "mMTC"


class Mobilidade(str, Enum):
    """Nível de mobilidade"""
    ESTATICO = "ESTATICO"
    PEDESTRE = "PEDESTRE"
    VEICULAR = "VEICULAR"
    ALTA = "ALTA"


class PrioridadeSLA(str, Enum):
    """Prioridade do SLA"""
    BRONZE = "BRONZE"
    PRATA = "PRATA"
    OURO = "OURO"
    PLATINA = "PLATINA"


class PenalidadeTipo(str, Enum):
    """Tipo de penalidade"""
    DESCONTO = "DESCONTO"
    REEMBOLSO = "REEMBOLSO"
    CREDITO = "CREDITO"


class Dominio(str, Enum):
    """Domínios de rede"""
    RAN = "RAN"
    TRANSPORTE = "TRANSPORTE"
    CORE = "CORE"


class SLAInterpretRequest(BaseModel):
    """
    ETAPA 1 - Intenção de SLA (PNL + Dados gerais)
    Conforme Capítulo 5 - SEM-CSMF
    """
    titulo_servico: str = Field(..., min_length=5, max_length=80, description="Título do serviço (5-80 caracteres)")
    descricao_intencao: str = Field(..., min_length=50, description="Descrição da intenção (mín. 50 caracteres)")
    categoria_servico_opcional: CategoriaServico = Field(default=CategoriaServico.AUTO, description="Categoria opcional")
    tenant_id: str = Field(default="default", description="ID do tenant")

    @field_validator('descricao_intencao')
    @classmethod
    def sanitize_intent(cls, v: str) -> str:
        """Sanitização leve de erros de digitação"""
        # Correções comuns
        corrections = {
            'cirugia': 'cirurgia',
            'vidiu': 'vídeo',
            '4k': '4K',
        }
        v_lower = v.lower()
        for wrong, correct in corrections.items():
            if wrong in v_lower:
                v = v.replace(wrong, correct)
        return v.strip()


class SLAParametrosTecnicos(BaseModel):
    """
    ETAPA 2 - Parâmetros Técnicos Sugeridos pelo SEM-CSMF (editáveis)
    Conforme Capítulo 4 - Arquitetura TriSLA
    """
    tipo_slice: TipoSlice = Field(..., description="Tipo de slice sugerido")
    latencia_maxima_ms: float = Field(..., ge=1, le=1000, description="Latência máxima em ms")
    disponibilidade_percent: float = Field(..., ge=95, le=99.999, description="Disponibilidade em %")
    confiabilidade_percent: float = Field(..., ge=95, le=99.999, description="Confiabilidade em %")
    throughput_min_dl_mbps: Optional[float] = Field(None, ge=1, description="Throughput mínimo DL (Mbps)")
    throughput_min_ul_mbps: Optional[float] = Field(None, ge=1, description="Throughput mínimo UL (Mbps)")
    numero_dispositivos: Optional[int] = Field(None, ge=1, description="Número de dispositivos")
    area_cobertura: Optional[str] = Field(None, description="Área de cobertura")
    mobilidade: Optional[Mobilidade] = Field(None, description="Nível de mobilidade")
    duracao_sla: Optional[str] = Field(None, description="Duração do SLA")

    @field_validator('latencia_maxima_ms')
    @classmethod
    def validate_latency_by_slice(cls, v: float, info) -> float:
        """Validar latência conforme tipo de slice"""
        tipo_slice = info.data.get('tipo_slice')
        if tipo_slice == TipoSlice.URLLC and v > 20:
            raise ValueError('URLLC: latência máxima deve ser ≤ 20ms')
        if tipo_slice == TipoSlice.eMBB and (v < 10 or v > 100):
            raise ValueError('eMBB: latência deve estar entre 10-100ms')
        if tipo_slice == TipoSlice.mMTC and (v < 50 or v > 1000):
            raise ValueError('mMTC: latência deve estar entre 50-1000ms')
        return v

    @field_validator('disponibilidade_percent')
    @classmethod
    def validate_availability_by_slice(cls, v: float, info) -> float:
        """Validar disponibilidade conforme tipo de slice"""
        tipo_slice = info.data.get('tipo_slice')
        if tipo_slice == TipoSlice.URLLC and v < 99.99:
            raise ValueError('URLLC: disponibilidade mínima é 99.99%')
        if tipo_slice == TipoSlice.eMBB and v < 99.9:
            raise ValueError('eMBB: disponibilidade mínima é 99.9%')
        if tipo_slice == TipoSlice.mMTC and v < 95:
            raise ValueError('mMTC: disponibilidade mínima é 95%')
        return v


class SLARequisitosNegocio(BaseModel):
    """
    ETAPA 3 - Requisitos de Negócio (Capítulo 6 — BC-NSSMF)
    """
    prioridade_sla: PrioridadeSLA = Field(..., description="Prioridade do SLA")
    penalidade_tipo: PenalidadeTipo = Field(..., description="Tipo de penalidade")
    penalidade_percent: float = Field(..., ge=0, le=100, description="Percentual de penalidade (0-100)")
    dominios_env: List[Dominio] = Field(..., min_length=1, description="Domínios envolvidos")
    aceite_termos: bool = Field(..., description="Aceite dos termos (obrigatório)")

    @field_validator('aceite_termos')
    @classmethod
    def validate_aceite_termos(cls, v: bool) -> bool:
        """Garantir que termos foram aceitos"""
        if not v:
            raise ValueError('É obrigatório aceitar os termos')
        return v


class SLASubmitRequestCompleto(BaseModel):
    """
    Request completo para POST /submit
    Combina as 3 etapas do formulário
    """
    # ETAPA 1
    titulo_servico: str
    descricao_intencao: str
    categoria_servico_opcional: CategoriaServico = CategoriaServico.AUTO
    tenant_id: str = "default"
    
    # ETAPA 2
    tipo_slice: TipoSlice
    latencia_maxima_ms: float
    disponibilidade_percent: float
    confiabilidade_percent: float
    throughput_min_dl_mbps: Optional[float] = None
    throughput_min_ul_mbps: Optional[float] = None
    numero_dispositivos: Optional[int] = None
    area_cobertura: Optional[str] = None
    mobilidade: Optional[Mobilidade] = None
    duracao_sla: Optional[str] = None
    
    # ETAPA 3
    prioridade_sla: PrioridadeSLA
    penalidade_tipo: PenalidadeTipo
    penalidade_percent: float
    dominios_env: List[Dominio]
    aceite_termos: bool

    def to_sla_aware_dict(self) -> Dict[str, Any]:
        """
        Converte para formato SLA-aware conforme dissertação
        Transforma valores para formato esperado pelos módulos
        """
        return {
            "intent_id": None,  # Será gerado pelo SEM-CSMF
            "tenant_id": self.tenant_id,
            "service_type": self.tipo_slice.value,
            "sla_requirements": {
                "latency": f"{self.latencia_maxima_ms}ms",
                "availability": f"{self.disponibilidade_percent}%",
                "reliability": f"{self.confiabilidade_percent}%",
                "throughput_dl": f"{self.throughput_min_dl_mbps or 0}Mbps",
                "throughput_ul": f"{self.throughput_min_ul_mbps or 0}Mbps",
                "device_count": self.numero_dispositivos,
                "coverage_area": self.area_cobertura,
                "mobility": self.mobilidade.value if self.mobilidade else None,
                "duration": self.duracao_sla
            },
            "business_requirements": {
                "priority": self.prioridade_sla.value,
                "penalty_type": self.penalidade_tipo.value,
                "penalty_percent": self.penalidade_percent,
                "domains": [d.value for d in self.dominios_env]
            }
        }

