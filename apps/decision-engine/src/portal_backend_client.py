"""
Cliente Portal Backend - Decision Engine
Notifica Portal Backend sobre decisões REJECT
"""

import httpx
from typing import Dict, Any, Optional
from opentelemetry import trace
import logging

from config import config
from models import DecisionResult, DecisionAction

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class PortalBackendClient:
    """
    Cliente para comunicação com Portal Backend
    Notifica sobre decisões REJECT para informar o usuário
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=15.0)
    
    async def notify_decision_rejection(self, decision_result: DecisionResult) -> Optional[Dict[str, Any]]:
        """
        Notifica Portal Backend sobre decisão REJECT
        
        Args:
            decision_result: Resultado da decisão com action=REJECT
        
        Returns:
            Resultado da notificação ou None em caso de erro
        """
        with tracer.start_as_current_span("notify_decision_rejection") as span:
            span.set_attribute("decision.id", decision_result.decision_id)
            span.set_attribute("decision.action", decision_result.action.value)
            span.set_attribute("intent.id", decision_result.intent_id)
            
            # Só notificar se decisão for REJECT
            if decision_result.action != DecisionAction.REJECT:
                span.set_attribute("portal.skip_reason", "Decision not REJECT")
                return None
            
            try:
                # Preparar notificação
                notification = {
                    "decision_id": decision_result.decision_id,
                    "intent_id": decision_result.intent_id,
                    "action": decision_result.action.value,
                    "reasoning": decision_result.reasoning,
                    "ml_risk_score": decision_result.ml_risk_score,
                    "ml_risk_level": decision_result.ml_risk_level.value if decision_result.ml_risk_level else None,
                    "timestamp": decision_result.timestamp
                }
                
                logger.info(f"Notificando Portal Backend sobre REJECT: decision_id={decision_result.decision_id}")
                
                # Chamar endpoint do Portal Backend (assumindo endpoint /api/v1/slas/decisions)
                # Se não existir, criar endpoint ou usar endpoint genérico
                response = await self.http_client.post(
                    f"{config.portal_backend_url}/api/v1/slas/decisions",
                    json=notification
                )
                response.raise_for_status()
                
                result = response.json()
                
                span.set_attribute("portal.notified", True)
                logger.info(f"✅ Portal Backend notificado sobre REJECT: {result}")
                
                return result
                
            except httpx.HTTPError as e:
                # Não falhar se Portal Backend não estiver disponível
                logger.warning(f"⚠️ Portal Backend não disponível para notificação: {e}")
                span.set_attribute("portal.notified", False)
                span.set_attribute("portal.error", str(e))
                return None
            except Exception as e:
                logger.warning(f"⚠️ Erro ao notificar Portal Backend: {e}")
                span.set_attribute("portal.notified", False)
                span.set_attribute("portal.error", str(e))
                return None
    
    async def close(self):
        """Fecha conexão HTTP"""
        await self.http_client.aclose()

