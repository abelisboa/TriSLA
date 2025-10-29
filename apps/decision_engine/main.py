#!/usr/bin/env python3
"""
TriSLA Decision Engine Central
Implementa o motor de decisão central que orquestra respostas dos módulos SEM-, ML- e BC-
Conforme especificado na FASE 4 da dissertação
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import logging
import json
from datetime import datetime
from enum import Enum
import httpx

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecisionStatus(Enum):
    """Status possíveis para uma decisão"""
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    RENEGOTIATE = "RENEGOTIATE"
    PENDING = "PENDING"

class DecisionRequest(BaseModel):
    """Requisição de decisão do Decision Engine"""
    slice_id: str
    requirements: Dict[str, Any]
    semantic_analysis: Optional[Dict[str, Any]] = None
    ml_prediction: Optional[Dict[str, Any]] = None
    blockchain_status: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class DecisionResponse(BaseModel):
    """Resposta de decisão do Decision Engine"""
    decision: DecisionStatus
    justification: str
    confidence: float
    actions: List[Dict[str, Any]]
    timestamp: datetime
    slice_id: str

class PolicyRule(BaseModel):
    """Regra de política SLA-aware"""
    name: str
    condition: str
    action: DecisionStatus
    priority: int
    description: str

class DecisionEngine:
    """Motor de decisão central da TriSLA"""
    
    def __init__(self):
        self.policies = self._load_default_policies()
        self.logger = logging.getLogger(__name__)
        self.decision_history = []
        
        # Configurações dos módulos
        self.sem_nsmf_url = "http://sem-nsmf:8080"
        self.ml_nsmf_url = "http://ml-nsmf:8080"
        self.bc_nssmf_url = "http://bc-nssmf:8080"
        self.nasp_api_url = "http://nasp-api:8080"
    
    def _load_default_policies(self) -> List[PolicyRule]:
        """Carregar políticas SLA-aware padrão"""
        return [
            PolicyRule(
                name="URLLC_Latency_Critical",
                condition="requirements.latency <= 10 and requirements.reliability >= 99.9",
                action=DecisionStatus.ACCEPT,
                priority=1,
                description="Aceitar requisições URLLC com latência crítica"
            ),
            PolicyRule(
                name="eMBB_Bandwidth_High",
                condition="requirements.bandwidth >= 1000 and requirements.latency <= 50",
                action=DecisionStatus.ACCEPT,
                priority=2,
                description="Aceitar requisições eMBB com alta largura de banda"
            ),
            PolicyRule(
                name="mMTC_Massive_Connections",
                condition="requirements.connections >= 10000 and requirements.latency <= 100",
                action=DecisionStatus.ACCEPT,
                priority=3,
                description="Aceitar requisições mMTC com conexões massivas"
            ),
            PolicyRule(
                name="Resource_Constraint",
                condition="ml_prediction.resource_availability < 0.5",
                action=DecisionStatus.REJECT,
                priority=4,
                description="Rejeitar quando recursos insuficientes"
            ),
            PolicyRule(
                name="Blockchain_Validation_Failed",
                condition="blockchain_status.valid == False",
                action=DecisionStatus.REJECT,
                priority=5,
                description="Rejeitar quando validação blockchain falha"
            ),
            PolicyRule(
                name="Semantic_Ambiguity",
                condition="semantic_analysis.confidence < 0.7",
                action=DecisionStatus.RENEGOTIATE,
                priority=6,
                description="Renegociar quando análise semântica é ambígua"
            )
        ]
    
    async def make_decision(self, request: DecisionRequest) -> DecisionResponse:
        """
        Tomar decisão baseada em políticas SLA-aware
        Orquestra respostas dos módulos SEM-, ML- e BC-
        """
        try:
            self.logger.info(f"Iniciando processo de decisão para slice {request.slice_id}")
            
            # 1. Coletar análises dos módulos se não fornecidas
            if not request.semantic_analysis:
                request.semantic_analysis = await self._get_semantic_analysis(request)
            
            if not request.ml_prediction:
                request.ml_prediction = await self._get_ml_prediction(request)
            
            if not request.blockchain_status:
                request.blockchain_status = await self._get_blockchain_status(request)
            
            # 2. Aplicar políticas de decisão
            decision_result = await self._apply_policies(request)
            
            # 3. Gerar ações baseadas na decisão
            actions = await self._generate_actions(decision_result, request)
            
            # 4. Criar resposta
            response = DecisionResponse(
                decision=decision_result["decision"],
                justification=decision_result["justification"],
                confidence=decision_result["confidence"],
                actions=actions,
                timestamp=datetime.now(),
                slice_id=request.slice_id
            )
            
            # 5. Registrar decisão
            self.decision_history.append(response)
            
            self.logger.info(f"Decisão tomada: {response.decision.value} para slice {request.slice_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Erro no processo de decisão: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    
    async def _get_semantic_analysis(self, request: DecisionRequest) -> Dict[str, Any]:
        """Obter análise semântica do SEM-NSMF"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sem_nsmf_url}/api/v1/analyze",
                    json={"requirements": request.requirements}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.warning(f"Erro ao obter análise semântica: {str(e)}")
            return {"confidence": 0.5, "analysis": "Análise semântica não disponível"}
    
    async def _get_ml_prediction(self, request: DecisionRequest) -> Dict[str, Any]:
        """Obter predição do ML-NSMF"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ml_nsmf_url}/api/v1/predict",
                    json={"requirements": request.requirements}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.warning(f"Erro ao obter predição ML: {str(e)}")
            return {"resource_availability": 0.5, "prediction": "Predição ML não disponível"}
    
    async def _get_blockchain_status(self, request: DecisionRequest) -> Dict[str, Any]:
        """Obter status do BC-NSSMF"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bc_nssmf_url}/api/v1/validate",
                    json={"slice_id": request.slice_id, "requirements": request.requirements}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.warning(f"Erro ao obter status blockchain: {str(e)}")
            return {"valid": True, "status": "Validação blockchain não disponível"}
    
    async def _apply_policies(self, request: DecisionRequest) -> Dict[str, Any]:
        """Aplicar políticas SLA-aware para tomar decisão"""
        # Ordenar políticas por prioridade
        sorted_policies = sorted(self.policies, key=lambda x: x.priority)
        
        for policy in sorted_policies:
            if self._evaluate_condition(policy.condition, request):
                return {
                    "decision": policy.action,
                    "justification": f"Política aplicada: {policy.name} - {policy.description}",
                    "confidence": 0.9,
                    "policy": policy.name
                }
        
        # Decisão padrão se nenhuma política se aplicar
        return {
            "decision": DecisionStatus.ACCEPT,
            "justification": "Nenhuma política específica aplicada, aceitando por padrão",
            "confidence": 0.5,
            "policy": "default"
        }
    
    def _evaluate_condition(self, condition: str, request: DecisionRequest) -> bool:
        """Avaliar condição de política (implementação simplificada)"""
        try:
            # Implementação simplificada - em produção usar um motor de regras mais robusto
            context = {
                "requirements": request.requirements,
                "semantic_analysis": request.semantic_analysis or {},
                "ml_prediction": request.ml_prediction or {},
                "blockchain_status": request.blockchain_status or {}
            }
            
            # Avaliar condições básicas
            if "requirements.latency <= 10" in condition:
                return request.requirements.get("latency", 0) <= 10
            elif "requirements.bandwidth >= 1000" in condition:
                return request.requirements.get("bandwidth", 0) >= 1000
            elif "requirements.connections >= 10000" in condition:
                return request.requirements.get("connections", 0) >= 10000
            elif "ml_prediction.resource_availability < 0.5" in condition:
                return (request.ml_prediction or {}).get("resource_availability", 1.0) < 0.5
            elif "blockchain_status.valid == False" in condition:
                return (request.blockchain_status or {}).get("valid", True) == False
            elif "semantic_analysis.confidence < 0.7" in condition:
                return (request.semantic_analysis or {}).get("confidence", 1.0) < 0.7
            
            return False
        except Exception as e:
            self.logger.error(f"Erro ao avaliar condição {condition}: {str(e)}")
            return False
    
    async def _generate_actions(self, decision_result: Dict[str, Any], request: DecisionRequest) -> List[Dict[str, Any]]:
        """Gerar ações baseadas na decisão tomada"""
        actions = []
        
        if decision_result["decision"] == DecisionStatus.ACCEPT:
            actions.extend([
                {
                    "type": "activate_slice",
                    "slice_id": request.slice_id,
                    "parameters": request.requirements,
                    "description": "Ativar slice no NASP"
                },
                {
                    "type": "register_contract",
                    "slice_id": request.slice_id,
                    "description": "Registrar contrato no blockchain"
                },
                {
                    "type": "start_monitoring",
                    "slice_id": request.slice_id,
                    "description": "Iniciar monitoramento SLA"
                }
            ])
        elif decision_result["decision"] == DecisionStatus.REJECT:
            actions.extend([
                {
                    "type": "notify_rejection",
                    "slice_id": request.slice_id,
                    "reason": decision_result["justification"],
                    "description": "Notificar rejeição ao usuário"
                }
            ])
        elif decision_result["decision"] == DecisionStatus.RENEGOTIATE:
            actions.extend([
                {
                    "type": "request_clarification",
                    "slice_id": request.slice_id,
                    "reason": decision_result["justification"],
                    "description": "Solicitar esclarecimentos do usuário"
                }
            ])
        
        return actions
    
    async def get_decision_history(self, limit: int = 100) -> List[DecisionResponse]:
        """Obter histórico de decisões"""
        return self.decision_history[-limit:]
    
    async def get_policies(self) -> List[PolicyRule]:
        """Obter políticas ativas"""
        return self.policies

# Inicializar aplicação FastAPI
app = FastAPI(
    title="TriSLA Decision Engine",
    description="Motor de decisão central da arquitetura TriSLA",
    version="1.0.0"
)

# Instanciar Decision Engine
decision_engine = DecisionEngine()

@app.get("/api/v1/health")
async def health_check():
    """Health check do Decision Engine"""
    return {
        "status": "healthy",
        "service": "decision-engine",
        "timestamp": datetime.now().isoformat(),
        "policies_count": len(decision_engine.policies)
    }

@app.post("/api/v1/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest):
    """Endpoint principal para tomada de decisões"""
    return await decision_engine.make_decision(request)

@app.get("/api/v1/history")
async def get_history(limit: int = 100):
    """Obter histórico de decisões"""
    return await decision_engine.get_decision_history(limit)

@app.get("/api/v1/policies")
async def get_policies():
    """Obter políticas ativas"""
    return await decision_engine.get_policies()

@app.post("/api/v1/policies")
async def add_policy(policy: PolicyRule):
    """Adicionar nova política"""
    decision_engine.policies.append(policy)
    return {"message": "Política adicionada com sucesso"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
