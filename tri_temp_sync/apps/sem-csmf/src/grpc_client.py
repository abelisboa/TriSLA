"""
gRPC Client - SEM-CSMF
Cliente para comunicação I-01 com Decision Engine
"""

import grpc
import os
from typing import Dict, Any, Optional
from opentelemetry import trace

import sys
import os
# Adicionar caminho do proto ao sys.path
proto_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto', 'proto')
if proto_path not in sys.path:
    sys.path.insert(0, proto_path)

# Importar diretamente do diretório proto/proto
import i01_interface_pb2
import i01_interface_pb2_grpc

tracer = trace.get_tracer(__name__)

# Decision Engine gRPC endpoint
DECISION_ENGINE_GRPC = os.getenv(
    "DECISION_ENGINE_GRPC",
    "localhost:50051"  # Padrão para desenvolvimento local
)


class DecisionEngineClient:
    """Cliente gRPC para Decision Engine (Interface I-01)"""
    
    def __init__(self):
        self.channel = None
        self.stub = None
    
    def _get_channel(self):
        """Obtém ou cria canal gRPC"""
        if self.channel is None:
            self.channel = grpc.insecure_channel(DECISION_ENGINE_GRPC)
            self.stub = i01_interface_pb2_grpc.DecisionEngineServiceStub(self.channel)
        return self.stub
    
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
        Envia metadados de NEST para Decision Engine via I-01
        """
        with tracer.start_as_current_span("send_nest_metadata_grpc") as span:
            span.set_attribute("intent.id", intent_id)
            span.set_attribute("nest.id", nest_id)
            
            try:
                stub = self._get_channel()
                
                # Converter SLA requirements para map
                sla_map = {}
                for key, value in sla_requirements.items():
                    if value is not None:
                        sla_map[key] = str(value)
                
                # Converter metadata para map
                metadata_map = {}
                if metadata:
                    for key, value in metadata.items():
                        if value is not None:
                            metadata_map[key] = str(value)
                
                # Criar request
                request = i01_interface_pb2.NESTMetadataRequest(
                    intent_id=intent_id,
                    nest_id=nest_id,
                    tenant_id=tenant_id or "",
                    service_type=service_type,
                    sla_requirements=sla_map,
                    nest_status=nest_status,
                    timestamp=self._get_timestamp(),
                    metadata=metadata_map
                )
                
                # Enviar via gRPC
                response = stub.SendNESTMetadata(request, timeout=10.0)
                
                span.set_attribute("decision.id", response.decision_id)
                span.set_attribute("decision.success", response.success)
                
                return {
                    "success": response.success,
                    "decision_id": response.decision_id,
                    "message": response.message,
                    "status_code": response.status_code
                }
                
            except grpc.RpcError as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                # Em caso de erro, retornar resposta padrão (não bloquear o fluxo)
                return {
                    "success": False,
                    "decision_id": None,
                    "message": f"Erro ao comunicar com Decision Engine: {str(e)}",
                    "status_code": e.code().value[0] if hasattr(e.code(), 'value') else 500
                }
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return {
                    "success": False,
                    "decision_id": None,
                    "message": f"Erro inesperado: {str(e)}",
                    "status_code": 500
                }
    
    async def get_decision_status(self, decision_id: str, intent_id: str) -> Optional[Dict[str, Any]]:
        """Consulta status de decisão"""
        with tracer.start_as_current_span("get_decision_status_grpc") as span:
            try:
                stub = self._get_channel()
                request = i01_interface_pb2.DecisionStatusRequest(
                    decision_id=decision_id,
                    intent_id=intent_id
                )
                response = stub.GetDecisionStatus(request, timeout=10.0)
                
                return {
                    "decision_id": response.decision_id,
                    "intent_id": response.intent_id,
                    "decision": response.decision,
                    "reason": response.reason,
                    "timestamp": response.timestamp,
                    "details": dict(response.details)
                }
            except grpc.RpcError as e:
                span.record_exception(e)
                return None
            except Exception as e:
                span.record_exception(e)
                return None
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual em ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def close(self):
        """Fecha o canal gRPC"""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None

