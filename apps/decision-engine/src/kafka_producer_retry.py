"""
Kafka Producer com Retry Logic - Decision Engine
Producer com retry automático para falhas temporárias
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
import json
from typing import Dict, Any
from opentelemetry import trace
import logging
import asyncio
import os

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Configuração de retry
MAX_RETRIES = int(os.getenv("KAFKA_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("KAFKA_RETRY_DELAY", "1.0"))
RETRY_BACKOFF = float(os.getenv("KAFKA_RETRY_BACKOFF", "2.0"))


class DecisionProducerWithRetry:
    """Produz decisões para I-04 e I-05 com retry"""
    
    def __init__(self, bootstrap_servers: list):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._create_producer()
    
    def _create_producer(self):
        """Cria ou recria o producer"""
        try:
            if self.producer:
                self.producer.close()
        except:
            pass
        
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=MAX_RETRIES,
            acks='all',
            max_in_flight_requests_per_connection=1,
            enable_idempotence=True
        )
    
    async def send_with_retry(
        self,
        topic: str,
        value: Dict[str, Any],
        key: str = None
    ) -> bool:
        """Envia mensagem com retry"""
        with tracer.start_as_current_span("kafka_send_retry") as span:
            span.set_attribute("kafka.topic", topic)
            span.set_attribute("retry.max_attempts", MAX_RETRIES)
            
            last_exception = None
            
            for attempt in range(MAX_RETRIES):
                try:
                    future = self.producer.send(
                        topic,
                        value=value,
                        key=key.encode('utf-8') if key else None
                    )
                    
                    # Aguardar confirmação (timeout de 10s)
                    record_metadata = future.get(timeout=10)
                    
                    span.set_attribute("kafka.partition", record_metadata.partition)
                    span.set_attribute("kafka.offset", record_metadata.offset)
                    span.set_attribute("retry.success", True)
                    span.set_attribute("retry.attempts", attempt + 1)
                    
                    return True
                    
                except (KafkaError, KafkaTimeoutError) as e:
                    last_exception = e
                    logger.warning(
                        f"Tentativa {attempt + 1}/{MAX_RETRIES} falhou ao enviar para {topic}: {e}"
                    )
                    
                    if attempt < MAX_RETRIES - 1:
                        delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
                        await asyncio.sleep(delay)
                        
                        # Recriar producer se necessário
                        try:
                            self._create_producer()
                        except Exception as create_error:
                            logger.error(f"Erro ao recriar producer: {create_error}")
                    else:
                        span.record_exception(e)
                        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                        span.set_attribute("retry.success", False)
                        logger.error(f"Todas as {MAX_RETRIES} tentativas falharam")
                        return False
                        
                except Exception as e:
                    last_exception = e
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    logger.error(f"Erro inesperado: {e}")
                    return False
            
            return False
    
    async def send_to_bc_nssmf(self, decision: Dict[str, Any]):
        """Envia decisão para BC-NSSMF via I-04 com retry"""
        with tracer.start_as_current_span("send_i04_retry") as span:
            message = {
                "interface": "I-04",
                "source": "decision-engine",
                "destination": "bc-nssmf",
                "decision": decision,
                "timestamp": self._get_timestamp()
            }
            
            success = await self.send_with_retry('trisla-i04-decisions', message)
            span.set_attribute("decision.action", decision.get("action"))
            span.set_attribute("send.success", success)
    
    async def send_to_sla_agents(self, decision: Dict[str, Any]):
        """Envia decisão para SLA-Agents via I-05 com retry"""
        with tracer.start_as_current_span("send_i05_retry") as span:
            message = {
                "interface": "I-05",
                "source": "decision-engine",
                "destination": "sla-agents",
                "decision": decision,
                "timestamp": self._get_timestamp()
            }
            
            success = await self.send_with_retry('trisla-i05-actions', message)
            span.set_attribute("decision.action", decision.get("action"))
            span.set_attribute("send.success", success)
    
    def flush(self):
        """Força envio de todas as mensagens pendentes"""
        if self.producer:
            self.producer.flush()
    
    def close(self):
        """Fecha o producer"""
        if self.producer:
            try:
                self.producer.close()
            except:
                pass
            self.producer = None
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

