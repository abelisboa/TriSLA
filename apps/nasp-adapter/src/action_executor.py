"
Action Executor - NASP Adapter
Executa ações reais no NASP (proxy HTTP ou CRD-first)
"

from typing import Dict, Any, Optional
from opentelemetry import trace
import httpx

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nasp_client import NASPClient
from crd_executor import CRDExecutor

tracer = trace.get_tracer(__name__)


class ActionExecutor:
    "Executa ações reais no NASP (tenta proxy HTTP, fallback para CRD)"
    
    def __init__(self, nasp_client: NASPClient):
        self.nasp_client = nasp_client
        self.crd_executor = CRDExecutor(namespace=os.getenv("NAMESPACE", "trisla"))
        self.use_crd_first = os.getenv("NASP_EXECUTION_MODE", "auto").lower() == "crd"
        self.proxy_enabled = os.getenv("NASP_PROXY_ENABLED", "true").lower() == "true"
    
    async def execute(self, action: Dict[str, Any], sla_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        "Executa ação real no NASP (proxy HTTP ou CRD-first)"
        with tracer.start_as_current_span("execute_nasp_action") as span:
            action_type = action.get("type")
            domain = action.get("domain", "ran")
            
            span.set_attribute("action.domain", domain)
            span.set_attribute("action.type", action_type)
            
            # Modo CRD-first forçado
            if self.use_crd_first or not self.proxy_enabled:
                print(f"🔧 CRD-FIRST mode: creating NSI/NSSI via CRD for {domain}")
                try:
                    result = await self.crd_executor.execute_action(action, sla_data)
                    span.set_attribute("action.executed", True)
                    span.set_attribute("action.method", "crd")
                    return result
                except Exception as e:
                    span.record_exception(e)
                    print(f"❌ CRD-FIRST failed: {e}")
                    raise
            
            # Modo auto: tentar proxy primeiro, fallback para CRD
            try:
                # Tentar proxy HTTP
                if domain == "ran":
                    result = await self.nasp_client.execute_ran_action(action)
                elif domain == "transport":
                    # Implementar para transport
                    result = {"domain": "transport", "executed": True, "method": "proxy"}
                elif domain == "core":
                    # Implementar para core
                    result = {"domain": "core", "executed": True, "method": "proxy"}
                else:
                    raise ValueError(f"Unknown domain: {domain}")
                
                span.set_attribute("action.executed", True)
                span.set_attribute("action.method", "proxy")
                return result
                
            except (httpx.ConnectError, httpx.TimeoutException, ConnectionRefusedError) as e:
                # Proxy não disponível - fallback para CRD
                print(f"⚠️ Proxy unreachable for {domain}, falling back to CRD-FIRST: {e}")
                span.set_attribute("proxy.unreachable", True)
                span.record_exception(e)
                
                try:
                    result = await self.crd_executor.execute_action(action, sla_data)
                    result["fallback_reason"] = "proxy_unreachable"
                    span.set_attribute("action.executed", True)
                    span.set_attribute("action.method", "crd_fallback")
                    return result
                except Exception as crd_error:
                    span.record_exception(crd_error)
                    print(f"❌ Both proxy and CRD failed: proxy={e}, crd={crd_error}")
                    raise Exception(f"Proxy unreachable ({e}) and CRD failed ({crd_error})") from crd_error
            
            except Exception as e:
                # Outro erro do proxy - não fazer fallback automático
                span.record_exception(e)
                print(f"❌ Proxy error (not connection): {e}")
                raise
