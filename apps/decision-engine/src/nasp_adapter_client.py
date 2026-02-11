"""
Cliente NASP Adapter - Decision Engine
Integração com NASP Adapter via HTTP REST (Interface I-07)
Encaminha decisões ACCEPT para criação real de slice no NASP
"""

import httpx
from typing import Dict, Any, Optional
from opentelemetry import trace
import logging

from config import config
from models import DecisionResult, DecisionAction

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class NASPAdapterClient:
    """
    Cliente para comunicação com NASP Adapter (Interface I-07)
    Encaminha decisões ACCEPT para execução real no NASP
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def check_3gpp_gate(self, slice_type: str = "eMBB", tenant_id: str = "default") -> Dict[str, Any]:
        """
        Chama GET ou POST /api/v1/3gpp/gate no NASP Adapter (PROMPT_S3GPP_GATE_v1.0).
        Retorna {"gate": "PASS"|"FAIL", "reasons": [...], "checks": {...}, "timestamp": "..."}.
        """
        try:
            response = await self.http_client.post(
                f"{config.nasp_adapter_url}/api/v1/3gpp/gate",
                json={"slice_type": slice_type, "tenantId": tenant_id},
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.warning(f"3GPP Gate request failed: {e}")
            return {"gate": "FAIL", "reasons": [f"gate_request_error:{e}"], "checks": {}, "timestamp": ""}
    
    async def execute_slice_creation(self, decision_result: DecisionResult) -> Optional[Dict[str, Any]]:
        """
        Executa criação de slice no NASP após decisão ACCEPT
        
        Args:
            decision_result: Resultado da decisão com action=ACCEPT
        
        Returns:
            Resultado da execução ou None em caso de erro
        """
        with tracer.start_as_current_span("execute_slice_creation_nasp") as span:
            span.set_attribute("decision.id", decision_result.decision_id)
            span.set_attribute("decision.action", decision_result.action.value)
            span.set_attribute("intent.id", decision_result.intent_id)
            
            # Só executar se decisão for ACCEPT
            if decision_result.action != DecisionAction.ACCEPT:
                span.set_attribute("nasp.skip_reason", "Decision not ACCEPT")
                logger.info(f"Pulando execução NASP - decisão não é ACCEPT: {decision_result.action.value}")
                return None
            
            try:
                # FASE C3-B3: Preparar especificação NSI para instanciação real
                import uuid
                nsi_id = f"nsi-{decision_result.intent_id[:8]}-{uuid.uuid4().hex[:6]}"
                
                # Extrair service_type do metadata ou inferir do intent
                service_type = decision_result.metadata.get("service_type") if decision_result.metadata else None
                if not service_type and decision_result.intent_id:
                    # Tentar inferir do intent_id ou usar padrão
                    service_type = "eMBB"  # Default
                
                # Converter SLOs para formato SLA
                sla = {}
                if decision_result.slos:
                    for slo in decision_result.slos:
                        if slo.name == "latency":
                            sla["latency"] = {"max_ms": int(slo.value)}
                        elif slo.name == "reliability":
                            sla["reliability"] = {"min": float(slo.value)}
                        elif slo.name == "availability":
                            sla["availability"] = {"min": float(slo.value)}
                        elif slo.name == "throughput":
                            sla["throughput"] = {"min_mbps": int(slo.value)}
                
                # Mapear service_type para SST (3GPP)
                sst_map = {"URLLC": 1, "eMBB": 2, "mMTC": 3}
                sst = sst_map.get(service_type, 2)
                
                # Preparar especificação NSI
                nsi_spec = {
                    "nsiId": nsi_id,
                    "tenantId": decision_result.metadata.get("tenant_id", "default") if decision_result.metadata else "default",
                    "serviceProfile": service_type or "eMBB",
                    "nssai": {
                        "sst": sst
                    },
                    "sla": sla
                }
                
                logger.info(f"🔷 [NSI] Instanciando NSI: {nsi_id} (serviceProfile={service_type})")
                
                # Chamar endpoint de instanciação NSI do NASP Adapter
                response = await self.http_client.post(
                    f"{config.nasp_adapter_url}/api/v1/nsi/instantiate",
                    json=nsi_spec
                )
                response.raise_for_status()
                
                result = response.json()
                
                span.set_attribute("nasp.action.executed", True)
                span.set_attribute("nasp.action.result", str(result.get("executed", False)))
                logger.info(f"✅ Ação executada no NASP: {result}")
                
                return result
                
            except httpx.HTTPError as e:
                logger.error(f"❌ Erro HTTP ao chamar NASP Adapter: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("nasp.error", str(e))
                return None
            except Exception as e:
                logger.error(f"❌ Erro inesperado ao chamar NASP Adapter: {e}", exc_info=True)
                span.record_exception(e)
                span.set_attribute("nasp.error", str(e))
                return None
    
    async def close(self):
        """Fecha conexão HTTP"""
        await self.http_client.aclose()

