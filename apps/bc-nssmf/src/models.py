from pydantic import BaseModel
from typing import List, Optional

# Schema final para /api/v1/register-sla
class SLO(BaseModel):
    name: str
    threshold: int  # threshold substitui value (schema final)

class SLARegisterRequest(BaseModel):
    sla_id: int
    customer: str
    service_name: str
    slos: List[SLO]

# Schema final para /api/v1/update-sla-status
class SLAStatusUpdateRequest(BaseModel):
    sla_id: int  # sla_id ao invés de slaId
    status: str  # status (string) ao invés de newStatus (int) - valores: "ACTIVE", "VIOLATED", etc.

# Schema final para /api/v1/execute-contract
class ContractExecuteRequest(BaseModel):
    operation: str  # "DEPLOY" ou "EXECUTE"
    function: Optional[str] = None  # obrigatório se operation="EXECUTE"
    args: Optional[List] = None  # obrigatório se operation="EXECUTE"

# Modelos legados (mantidos para compatibilidade interna se necessário)
class SLARequest(BaseModel):
    """Modelo legado - usar SLARegisterRequest no lugar"""
    customer: str
    serviceName: str
    slaHash: str
    slos: List[SLO]

class SLAStatusUpdate(BaseModel):
    """Modelo legado - usar SLAStatusUpdateRequest no lugar"""
    slaId: int
    newStatus: int
