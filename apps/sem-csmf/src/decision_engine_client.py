"""
HTTP Client - SEM-CSMF
Cliente para comunicação HTTP com Decision Engine (Interface I-01)
Substitui comunicação gRPC por HTTP REST
"""

import os
import requests
from typing import Dict, Any, Optional
from opentelemetry import trace
import logging

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Decision Engine HTTP endpoint
DECISION_ENGINE_URL = os.getenv(
    "DECISION_ENGINE_URL",
    "http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate"
)

# Configuração de timeout
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10.0"))  # segundos


class DecisionEngineHTTPClient:
    """Cliente HTTP para Decision Engine (Interface I-01)"""
    
    def __init__(self):
        self.base_url = DECISION_ENGINE_URL
        logger.info(f"Decision Engine HTTP Client inicializado: {self.base_url}")
    
    async def send_nest_metadata(
        self,
        intent_id: str,
        nest_id: str,
        tenant_id: Optional[str],
        service_type: str,
        sla_requirements: Dict[str, Any],
        nest_status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envia metadados de NEST para Decision Engine via HTTP POST
        
        Payload esperado pelo Decision Engine:
        {
            "intent_id": str,
            "nest_id": str,
            "tenant_id": str,
            "service_type": str,
            "sla_requirements": dict,
            "nest_status": str,
            "metadata": dict (opcional)
        }
        """
        with tracer.start_as_current_span("send_nest_metadata_http") as span:
            span.set_attribute("intent.id", intent_id)
            span.set_attribute("nest.id", nest_id)
            span.set_attribute("decision_engine.url", self.base_url)
            
            try:
                # Montar payload conforme contrato do Decision Engine
                payload = {
                    "intent_id": intent_id,
                    "nest_id": nest_id,
                    "tenant_id": tenant_id or "",
                    "service_type": service_type,
                    "sla_requirements": sla_requirements,
                    "nest_status": nest_status,
                }
                
                # Adicionar metadata se fornecido
                if metadata:
                    payload["metadata"] = metadata
                
                logger.info(
                    f"Enviando NEST metadata para Decision Engine: "
                    f"intent_id={intent_id}, nest_id={nest_id}"
                )
                
                # Fazer requisição HTTP POST
                # FIX: nunca enviar 'decision' como input ao Decision Engine

                if isinstance(payload, dict):

                    payload.pop('decision', None)

                response = requests.post(
                    self.base_url,
                    json=payload,
                    timeout=HTTP_TIMEOUT,
                    headers={"Content-Type": "application/json"}
                )
                
                # Verificar status HTTP
                response.raise_for_status()
                
                # Parsear resposta JSON
                result = response.json()
                
                # Normalizar resposta para compatibilidade com código existente
                decision_response = {
                    "success": result.get("success", True),
                    "decision_id": result.get("decision_id"),
                    "message": result.get("message", "Decision processed successfully"),
                    "status_code": result.get("status_code", 200)
                }
                
                if decision_response.get("decision_id"):
                    span.set_attribute("decision.id", decision_response.get("decision_id"))
                span.set_attribute("decision.success", decision_response.get("success", False))
                span.set_attribute("http.status_code", response.status_code)
                
                logger.info(
                    f"Resposta do Decision Engine: success={decision_response.get('success')}, "
                    f"decision_id={decision_response.get('decision_id')}"
                )
                
                return decision_response
                
            except requests.exceptions.Timeout as e:
                error_msg = f"Timeout ao comunicar com Decision Engine: {str(e)}"
                logger.error(error_msg)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                span.set_attribute("http.error", "timeout")
                
                return {
                    "success": False,
                    "decision_id": None,
                    "message": error_msg,
                    "status_code": 504
                }
                
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Erro de conexão com Decision Engine: {str(e)}"
                logger.error(error_msg)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                span.set_attribute("http.error", "connection_error")
                
                return {
                    "success": False,
                    "decision_id": None,
                    "message": error_msg,
                    "status_code": 503
                }
                
            except requests.exceptions.HTTPError as e:
                error_msg = f"Erro HTTP ao comunicar com Decision Engine: {str(e)}"
                logger.error(error_msg)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                span.set_attribute("http.status_code", e.response.status_code if hasattr(e, 'response') else 500)
                
                return {
                    "success": False,
                    "decision_id": None,
                    "message": error_msg,
                    "status_code": e.response.status_code if hasattr(e, 'response') else 500
                }
                
            except Exception as e:
                error_msg = f"Erro inesperado ao comunicar com Decision Engine: {str(e)}"
                logger.error(error_msg, exc_info=True)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                
                return {
                    "success": False,
                    "decision_id": None,
                    "message": error_msg,
                    "status_code": 500
                }
    
    async def get_decision_status(self, decision_id: str, intent_id: str) -> Optional[Dict[str, Any]]:
        """
        Consulta status de decisão (se o Decision Engine expor endpoint para isso)
        Por enquanto, retorna None pois o endpoint pode não estar disponível
        """
        logger.debug("get_decision_status não é necessário para HTTP client (status via /evaluate)")
        return None
    
    def close(self):
        """Método de compatibilidade (não necessário para HTTP, mas mantido para compatibilidade)"""
        logger.debug("HTTP client close() chamado (no-op para HTTP)")


# Alias para compatibilidade com código existente
DecisionEngineClient = DecisionEngineHTTPClient
DecisionEngineClientWithRetry = DecisionEngineHTTPClient

