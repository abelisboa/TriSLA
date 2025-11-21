"""
Serviço de Decisão - Decision Engine
Camada de serviço que expõe a lógica do DecisionEngine via API
"""

from typing import Optional, Dict, Any
from opentelemetry import trace

from engine import DecisionEngine
from models import DecisionResult, DecisionInput

tracer = trace.get_tracer(__name__)


class DecisionService:
    """
    Serviço que expõe funcionalidades do Decision Engine
    Usado por rotas REST e gRPC
    """
    
    def __init__(self):
        self.engine = DecisionEngine()
    
    async def process_decision(
        self,
        intent_id: str,
        nest_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DecisionResult:
        """
        Processa decisão para um intent/NEST
        
        Args:
            intent_id: ID do intent
            nest_id: ID do NEST (opcional)
            context: Contexto adicional
        
        Returns:
            DecisionResult com ação e justificativa
        """
        with tracer.start_as_current_span("service_process_decision") as span:
            span.set_attribute("intent.id", intent_id)
            if nest_id:
                span.set_attribute("nest.id", nest_id)
            
            result = await self.engine.decide(intent_id, nest_id, context)
            
            span.set_attribute("decision.action", result.action.value)
            span.set_attribute("decision.confidence", result.confidence)
            
            return result
    
    async def process_decision_from_input(
        self,
        decision_input: DecisionInput
    ) -> DecisionResult:
        """
        Processa decisão a partir de DecisionInput completo
        
        Útil quando os dados já estão disponíveis (evita buscar do SEM-CSMF)
        """
        with tracer.start_as_current_span("service_process_decision_from_input") as span:
            span.set_attribute("intent.id", decision_input.intent.intent_id)
            
            # Se já temos ML prediction, usar diretamente
            if decision_input.ml_prediction:
                ml_prediction = decision_input.ml_prediction
            else:
                # Obter previsão do ML
                ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
                decision_input.ml_prediction = ml_prediction
            
            # Aplicar regras
            action, reasoning, slos, domains = self.engine._apply_decision_rules(
                decision_input.intent,
                decision_input.nest,
                ml_prediction,
                decision_input.context
            )
            
            decision_id = f"dec-{decision_input.intent.intent_id}"
            
            result = DecisionResult(
                decision_id=decision_id,
                intent_id=decision_input.intent.intent_id,
                nest_id=decision_input.nest.nest_id if decision_input.nest else None,
                action=action,
                reasoning=reasoning,
                confidence=ml_prediction.confidence,
                ml_risk_score=ml_prediction.risk_score,
                ml_risk_level=ml_prediction.risk_level,
                slos=slos,
                domains=domains
            )
            
            # Registrar no blockchain se aceito
            if action.value == "AC":
                blockchain_tx_hash = await self.engine.bc_client.register_sla_on_chain(result)
                if blockchain_tx_hash:
                    result.metadata = result.metadata or {}
                    result.metadata["blockchain_tx_hash"] = blockchain_tx_hash
            
            return result
    
    async def close(self):
        """Fecha recursos do serviço"""
        await self.engine.close()

