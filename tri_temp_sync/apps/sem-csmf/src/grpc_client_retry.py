"""
gRPC Client com Retry Logic - SEM-CSMF
Cliente para comunicação I-01 com Decision Engine com retry automático
"""

import grpc
import os
import asyncio
from typing import Dict, Any, Optional
from opentelemetry import trace
import time
import logging

import sys
# Adicionar caminho do proto ao sys.path
proto_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto', 'proto')
if proto_path not in sys.path:
    sys.path.insert(0, proto_path)

# Importar diretamente do diretório proto/proto
import i01_interface_pb2
import i01_interface_pb2_grpc

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Decision Engine gRPC endpoint
DECISION_ENGINE_GRPC = os.getenv(
    "DECISION_ENGINE_GRPC",
    "localhost:50051"
)

# Configuração de retry
MAX_RETRIES = int(os.getenv("GRPC_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("GRPC_RETRY_DELAY", "1.0"))  # segundos
RETRY_BACKOFF = float(os.getenv("GRPC_RETRY_BACKOFF", "2.0"))  # multiplicador
TIMEOUT = float(os.getenv("GRPC_TIMEOUT", "10.0"))  # segundos

# Códigos gRPC que devem ser retentados
RETRYABLE_STATUS_CODES = {
    grpc.StatusCode.UNAVAILABLE,
    grpc.StatusCode.DEADLINE_EXCEEDED,
    grpc.StatusCode.RESOURCE_EXHAUSTED,
    grpc.StatusCode.ABORTED,
    grpc.StatusCode.INTERNAL,
}


class DecisionEngineClientWithRetry:
    """Cliente gRPC para Decision Engine (Interface I-01) com retry logic"""
    
    def __init__(self):
        self.channel = None
        self.stub = None
    
    def _get_channel(self):
        """Obtém ou cria canal gRPC"""
        if self.channel is None or self._is_channel_ready():
            try:
                if self.channel:
                    self.channel.close()
            except:
                pass
            self.channel = grpc.insecure_channel(DECISION_ENGINE_GRPC)
            self.stub = i01_interface_pb2_grpc.DecisionEngineServiceStub(self.channel)
        return self.stub
    
    def _is_channel_ready(self) -> bool:
        """Verifica se o canal está pronto"""
        if self.channel is None:
            return False
        try:
            state = self.channel.get_state()
            return state == grpc.ChannelConnectivity.READY
        except:
            return False
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """Executa função com retry e backoff exponencial"""
        last_exception = None
        
        for attempt in range(MAX_RETRIES):
            try:
                return await func(*args, **kwargs)
            except grpc.RpcError as e:
                last_exception = e
                status_code = e.code()
                
                # Verificar se é um erro retentável
                if status_code not in RETRYABLE_STATUS_CODES:
                    logger.error(f"Erro não retentável: {status_code}")
                    raise
                
                # Se não é a última tentativa, aguardar e tentar novamente
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
                    logger.warning(
                        f"Tentativa {attempt + 1}/{MAX_RETRIES} falhou com {status_code}. "
                        f"Reagendando em {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    
                    # Recriar canal se necessário
                    if not self._is_channel_ready():
                        logger.info("Recriando canal gRPC...")
                        self._get_channel()
                else:
                    logger.error(f"Todas as {MAX_RETRIES} tentativas falharam")
                    raise
            except Exception as e:
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
                    logger.warning(
                        f"Erro inesperado na tentativa {attempt + 1}/{MAX_RETRIES}: {e}. "
                        f"Reagendando em {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    raise
        
        # Se chegou aqui, todas as tentativas falharam
        raise last_exception
    
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
        Envia metadados de NEST para Decision Engine via I-01 com retry
        """
        with tracer.start_as_current_span("send_nest_metadata_grpc_retry") as span:
            span.set_attribute("intent.id", intent_id)
            span.set_attribute("nest.id", nest_id)
            span.set_attribute("retry.max_attempts", MAX_RETRIES)
            
            async def _send_request():
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
                response = stub.SendNESTMetadata(request, timeout=TIMEOUT)
                return response
            
            try:
                response = await self._retry_with_backoff(_send_request)
                
                span.set_attribute("decision.id", response.decision_id)
                span.set_attribute("decision.success", response.success)
                span.set_attribute("retry.success", True)
                
                return {
                    "success": response.success,
                    "decision_id": response.decision_id,
                    "message": response.message,
                    "status_code": response.status_code
                }
                
            except grpc.RpcError as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("retry.success", False)
                span.set_attribute("retry.final_error", str(e.code()))
                
                return {
                    "success": False,
                    "decision_id": None,
                    "message": f"Erro ao comunicar com Decision Engine após {MAX_RETRIES} tentativas: {str(e)}",
                    "status_code": e.code().value[0] if hasattr(e.code(), 'value') else 500
                }
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("retry.success", False)
                
                return {
                    "success": False,
                    "decision_id": None,
                    "message": f"Erro inesperado após {MAX_RETRIES} tentativas: {str(e)}",
                    "status_code": 500
                }
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual em ISO format"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def close(self):
        """Fecha o canal gRPC"""
        if self.channel:
            try:
                self.channel.close()
            except:
                pass
            self.channel = None
            self.stub = None

