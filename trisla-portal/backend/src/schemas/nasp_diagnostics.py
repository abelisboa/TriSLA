"""
Schemas para diagnóstico de saúde dos serviços NASP.
"""
from pydantic import BaseModel
from typing import Optional


class NASPModuleStatus(BaseModel):
    """Status de um módulo NASP individual"""
    reachable: bool
    latency_ms: Optional[float] = None
    detail: Optional[str] = None
    status_code: Optional[int] = None
    rpc_connected: Optional[bool] = None  # Apenas para BC-NSSMF


class NASPDiagnosticsResponse(BaseModel):
    """Resposta completa do diagnóstico NASP"""
    sem_csmf: NASPModuleStatus
    ml_nsmf: NASPModuleStatus
    decision: NASPModuleStatus
    bc_nssmf: NASPModuleStatus
    sla_agent: NASPModuleStatus



