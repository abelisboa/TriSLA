"""
Cliente SEM-CSMF - Decision Engine
Integração com SEM-CSMF via HTTP REST (fallback) ou gRPC (I-01)
"""

import httpx
import grpc
import os
import sys
from typing import Optional, Dict, Any
from opentelemetry import trace

# Adicionar caminho do proto
proto_path = os.path.join(os.path.dirname(__file__), 'proto', 'proto')
if proto_path not in sys.path:
    sys.path.insert(0, proto_path)

try:
    import i01_interface_pb2
    import i01_interface_pb2_grpc
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

from config import config
from models import SLAIntent, NestSubset

tracer = trace.get_tracer(__name__)


class SEMClient:
    """
    Cliente para comunicação com SEM-CSMF
    Suporta HTTP REST (fallback) e gRPC (I-01)
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self.grpc_channel = None
        self.grpc_stub = None
    
    async def fetch_nest_by_intent_id(self, intent_id: str) -> Optional[NestSubset]:
        """
        Busca NEST por intent_id do SEM-CSMF via HTTP REST
        Interface alternativa quando gRPC não está disponível
        """
        with tracer.start_as_current_span("fetch_nest_http") as span:
            span.set_attribute("intent.id", intent_id)
            
            try:
                # Tentar buscar via endpoint REST do SEM-CSMF
                response = await self.http_client.get(
                    f"{config.sem_csmf_http_url}/api/v1/nests/{intent_id}"
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Converter para NestSubset
                nest = NestSubset(
                    nest_id=data.get("nest_id", ""),
                    intent_id=intent_id,
                    network_slices=data.get("network_slices", []),
                    resources=data.get("resources", {}),
                    status=data.get("status", "generated"),
                    metadata=data.get("metadata")
                )
                
                span.set_attribute("nest.id", nest.nest_id)
                return nest
                
            except httpx.HTTPError as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return None
            except Exception as e:
                span.record_exception(e)
                return None
    
    async def fetch_semantic_sla(self, intent_id: str) -> Optional[SLAIntent]:
        """
        Busca intent semanticamente enriquecido do SEM-CSMF
        """
        with tracer.start_as_current_span("fetch_semantic_sla") as span:
            span.set_attribute("intent.id", intent_id)
            
            try:
                # Tentar buscar via endpoint REST
                response = await self.http_client.get(
                    f"{config.sem_csmf_http_url}/api/v1/intents/{intent_id}"
                )
                response.raise_for_status()
                
                data = response.json()
                
                from models import SliceType
                
                intent = SLAIntent(
                    intent_id=intent_id,
                    tenant_id=data.get("tenant_id"),
                    service_type=SliceType(data.get("service_type", "eMBB")),
                    sla_requirements=data.get("sla_requirements", {}),
                    nest_id=data.get("nest_id"),
                    metadata=data.get("metadata")
                )
                
                return intent
                
            except httpx.HTTPError as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return None
            except Exception as e:
                span.record_exception(e)
                return None
    
    def _get_grpc_stub(self):
        """Obtém ou cria stub gRPC"""
        if not GRPC_AVAILABLE:
            return None
        
        if self.grpc_channel is None:
            self.grpc_channel = grpc.insecure_channel(config.sem_csmf_grpc_endpoint)
            self.grpc_stub = i01_interface_pb2_grpc.DecisionEngineServiceStub(self.grpc_channel)
        
        return self.grpc_stub
    
    async def close(self):
        """Fecha conexões"""
        await self.http_client.aclose()
        if self.grpc_channel:
            self.grpc_channel.close()
            self.grpc_channel = None
            self.grpc_stub = None

