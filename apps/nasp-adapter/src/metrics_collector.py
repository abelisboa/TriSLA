"""
Metrics Collector - NASP Adapter
Coleta métricas reais do NASP
"""

from typing import Dict, Any
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nasp_client import NASPClient

tracer = trace.get_tracer(__name__)


class MetricsCollector:
    """Coleta métricas reais do NASP"""
    
    def __init__(self, nasp_client: NASPClient):
        self.nasp_client = nasp_client
    
    async def collect_all(self) -> Dict[str, Any]:
        """Coleta todas as métricas do NASP"""
        with tracer.start_as_current_span("collect_all_nasp_metrics") as span:
            # ⚠️ PRODUÇÃO REAL: Coleta real de métricas dos serviços descobertos
            all_metrics = {
                "ran": {},
                "transport": {},
                "core": {},
                "timestamp": self._get_timestamp(),
                "source": "nasp_real"
            }
            
            # Coletar métricas RAN (srsenb)
            try:
                all_metrics["ran"] = await self.nasp_client.get_ran_metrics()
            except Exception as e:
                all_metrics["ran"] = {"error": str(e)}
            
            # Coletar métricas Transport (UPF)
            try:
                all_metrics["transport"] = await self.nasp_client.get_transport_metrics()
            except Exception as e:
                all_metrics["transport"] = {"error": str(e)}
            
            # Coletar métricas Core (UPF, AMF, SMF)
            try:
                core_metrics = await self.nasp_client.get_core_metrics()
                all_metrics["core"] = {
                    "upf": core_metrics,
                    "amf_endpoint": self.nasp_client.core_amf_endpoint,
                    "smf_endpoint": self.nasp_client.core_smf_endpoint
                }
            except Exception as e:
                all_metrics["core"] = {"error": str(e)}
            
            span.set_attribute("metrics.domains", "ran,transport,core")
            span.set_attribute("metrics.source", "nasp_real")
            span.set_attribute("metrics.ran_endpoint", self.nasp_client.ran_endpoint)
            span.set_attribute("metrics.core_endpoint", self.nasp_client.core_endpoint)
            
            return all_metrics
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

