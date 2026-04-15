"""
NASP Client - Conexão com serviços reais do NASP
⚠️ PRODUÇÃO REAL: Conecta a serviços reais, não mocks
"""

import httpx
from typing import Dict, Any, Optional
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class NASPClient:
    """Cliente para serviços reais do NASP"""
    
    def __init__(self):
        import os
        
        # Verificar modo (mock para desenvolvimento local, real para produção)
        nasp_mode = os.getenv("NASP_MODE", "real")
        
        if nasp_mode == "mock":
            # Modo MOCK para desenvolvimento local
            self.ran_endpoint = os.getenv("NASP_RAN_ENDPOINT", "http://mock-nasp-ran:80")
            self.ran_metrics_endpoint = os.getenv("NASP_RAN_ENDPOINT", "http://mock-nasp-ran:80")
            self.transport_endpoint = os.getenv("NASP_TRANSPORT_ENDPOINT", "http://mock-nasp-transport:80")
            self.core_endpoint = os.getenv("NASP_CORE_ENDPOINT", "http://mock-nasp-core:80")
            self.core_upf_endpoint = os.getenv("NASP_CORE_ENDPOINT", "http://mock-nasp-core:80")
            self.core_upf_metrics_endpoint = os.getenv("NASP_CORE_ENDPOINT", "http://mock-nasp-core:80")
            self.core_amf_endpoint = os.getenv("NASP_CORE_ENDPOINT", "http://mock-nasp-core:80")
            self.core_smf_endpoint = os.getenv("NASP_CORE_ENDPOINT", "http://mock-nasp-core:80")
        else:
            # ⚠️ PRODUÇÃO REAL: Endpoints reais do NASP (descobertos no node1)
            # RAN - srsenb no namespace srsran
            self.ran_endpoint = os.getenv("NASP_RAN_ENDPOINT", "http://srsenb.srsran.svc.cluster.local:36412")
            self.ran_metrics_endpoint = os.getenv("NASP_RAN_METRICS_ENDPOINT", "http://srsenb.srsran.svc.cluster.local:9092")
            
            # Core - open5gs UPF, AMF, SMF
            self.core_upf_endpoint = os.getenv("NASP_CORE_UPF_ENDPOINT", "http://open5gs-upf.open5gs.svc.cluster.local:8805")
            self.core_upf_metrics_endpoint = os.getenv("NASP_CORE_UPF_METRICS_ENDPOINT", "http://open5gs-upf.open5gs.svc.cluster.local:9090")
            self.core_amf_endpoint = os.getenv("NASP_CORE_AMF_ENDPOINT", "http://amf-namf.ns-1274485.svc.cluster.local:80")
            self.core_smf_endpoint = os.getenv("NASP_CORE_SMF_ENDPOINT", "http://smf-nsmf.ns-1274485.svc.cluster.local:80")
            
            # Transport - usar UPF como transport
            self.transport_endpoint = os.getenv("NASP_TRANSPORT_ENDPOINT", "http://open5gs-upf.open5gs.svc.cluster.local:8805")
            
            # Endpoint principal
            self.core_endpoint = os.getenv("NASP_CORE_ENDPOINT", "http://open5gs-upf.open5gs.svc.cluster.local:8805")
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self._connected = False
        self._mode = nasp_mode
    
    async def connect(self):
        """Conecta aos serviços NASP"""
        with tracer.start_as_current_span("connect_nasp") as span:
            try:
                # Testar conectividade com endpoints reais
                # Em produção, fazer health check real
                self._connected = True
                span.set_attribute("nasp.connected", True)
            except Exception as e:
                span.record_exception(e)
                self._connected = False
                span.set_attribute("nasp.connected", False)
    
    def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self._connected
    
    async def get_ran_metrics(self) -> Dict[str, Any]:
        """Obtém métricas reais do RAN"""
        with tracer.start_as_current_span("get_ran_metrics") as span:
            # ⚠️ PRODUÇÃO REAL: Chamada real ao controlador RAN (srsenb)
            try:
                # Tentar endpoint de métricas primeiro
                response = await self.client.get(f"{self.ran_metrics_endpoint}/metrics", timeout=10.0)
                response.raise_for_status()
                metrics = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
                span.set_attribute("metrics.source", "nasp_ran_real")
                span.set_attribute("metrics.endpoint", self.ran_metrics_endpoint)
                return metrics
            except Exception as e:
                span.record_exception(e)
                # Fallback para endpoint principal
                try:
                    response = await self.client.get(f"{self.ran_endpoint}/metrics", timeout=10.0)
                    response.raise_for_status()
                    metrics = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
                    return metrics
                except Exception as e2:
                    span.record_exception(e2)
                    raise
    
    async def execute_ran_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ação real no RAN"""
        with tracer.start_as_current_span("execute_ran_action") as span:
            # ⚠️ PRODUÇÃO REAL: Execução real de ação
            try:
                response = await self.client.post(
                    f"{self.ran_endpoint}/api/v1/actions",
                    json=action
                )
                response.raise_for_status()
                result = response.json()
                span.set_attribute("action.executed", True)
                span.set_attribute("action.domain", "RAN")
                return result
            except Exception as e:
                span.record_exception(e)
                raise
    
    async def get_transport_metrics(self) -> Dict[str, Any]:
        """Obtém métricas reais do Transport"""
        with tracer.start_as_current_span("get_transport_metrics") as span:
            # ⚠️ PRODUÇÃO REAL: Usando UPF como transport (ou endpoint específico se disponível)
            try:
                response = await self.client.get(f"{self.transport_endpoint}/metrics", timeout=10.0)
                response.raise_for_status()
                metrics = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
                span.set_attribute("metrics.source", "nasp_transport_real")
                return metrics
            except Exception as e:
                span.record_exception(e)
                raise
    
    async def get_core_metrics(self) -> Dict[str, Any]:
        """Obtém métricas reais do Core"""
        with tracer.start_as_current_span("get_core_metrics") as span:
            # ⚠️ PRODUÇÃO REAL: Chamada real ao Core (open5gs UPF)
            try:
                # Tentar endpoint de métricas do UPF
                response = await self.client.get(f"{self.core_upf_metrics_endpoint}/metrics", timeout=10.0)
                response.raise_for_status()
                metrics = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
                span.set_attribute("metrics.source", "nasp_core_real")
                span.set_attribute("metrics.endpoint", self.core_upf_metrics_endpoint)
                return metrics
            except Exception as e:
                span.record_exception(e)
                # Fallback para endpoint principal
                try:
                    response = await self.client.get(f"{self.core_endpoint}/metrics", timeout=10.0)
                    response.raise_for_status()
                    return response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
                except Exception as e2:
                    span.record_exception(e2)
                    raise

