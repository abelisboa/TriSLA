"""
Kafka Producer - SLA-Agent Layer
Publica eventos I-06 (violações/riscos) e I-07 (resultado de ações)
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
from opentelemetry import trace
import asyncio

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Configuração de retry
MAX_RETRIES = int(os.getenv("KAFKA_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("KAFKA_RETRY_DELAY", "1.0"))
RETRY_BACKOFF = float(os.getenv("KAFKA_RETRY_BACKOFF", "2.0"))


class EventProducer:
    """
    Producer Kafka para eventos I-06 e I-07
    
    I-06: Eventos de violação/risco de SLO
    I-07: Resultado de ações executadas
    """
    
    def __init__(self, bootstrap_servers: list = None):
        """
        Inicializa producer Kafka
        
        Args:
            bootstrap_servers: Lista de servidores Kafka (padrão: kafka:9092)
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:29092,kafka:9092"
        ).split(",")
        
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
    
    async def send_i06_event(
        self,
        domain: str,
        agent_id: str,
        status: str,
        slo: Dict[str, Any],
        slice_id: Optional[str] = None,
        sla_id: Optional[str] = None
    ) -> bool:
        """
        Publica evento I-06 (violação/risco de SLO)
        
        Args:
            domain: Domínio (RAN, Transport, Core)
            agent_id: ID do agente
            status: Status (OK, RISK, VIOLATED)
            slo: Dicionário com informações do SLO
            slice_id: ID do slice (opcional)
            sla_id: ID do SLA (opcional)
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        with tracer.start_as_current_span("send_i06_event") as span:
            message = {
                "interface": "I-06",
                "domain": domain,
                "agent_id": agent_id,
                "slice_id": slice_id,
                "sla_id": sla_id,
                "status": status,
                "slo": slo,
                "timestamp": self._get_timestamp()
            }
            
            topic = "trisla-i06-agent-events"
            key = f"{domain}-{agent_id}"
            
            span.set_attribute("kafka.topic", topic)
            span.set_attribute("event.domain", domain)
            span.set_attribute("event.status", status)
            
            return await self._send_with_retry(topic, message, key)
    
    async def send_i07_action_result(
        self,
        domain: str,
        agent_id: str,
        action: Dict[str, Any],
        result: Dict[str, Any]
    ) -> bool:
        """
        Publica evento I-07 (resultado de ação executada)
        
        Args:
            domain: Domínio (RAN, Transport, Core)
            agent_id: ID do agente
            action: Dicionário com ação executada
            result: Dicionário com resultado da execução
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        with tracer.start_as_current_span("send_i07_action_result") as span:
            message = {
                "interface": "I-07",
                "domain": domain,
                "agent_id": agent_id,
                "action": action,
                "result": result,
                "timestamp": self._get_timestamp()
            }
            
            topic = "trisla-i07-agent-actions"
            key = f"{domain}-{agent_id}"
            
            span.set_attribute("kafka.topic", topic)
            span.set_attribute("action.domain", domain)
            span.set_attribute("action.executed", result.get("executed", False))
            
            return await self._send_with_retry(topic, message, key)
    
    async def _send_with_retry(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """Envia mensagem com retry"""
        last_exception = None
        
        for attempt in range(MAX_RETRIES):
            try:
                future = self.producer.send(
                    topic,
                    value=value,
                    key=key.encode('utf-8') if key else None
                )
                
                record_metadata = future.get(timeout=10)
                
                logger.info(
                    f"✅ Evento enviado: topic={topic}, partition={record_metadata.partition}, "
                    f"offset={record_metadata.offset}"
                )
                
                return True
                
            except (KafkaError, KafkaTimeoutError) as e:
                last_exception = e
                logger.warning(
                    f"⚠️ Tentativa {attempt + 1}/{MAX_RETRIES} falhou ao enviar para {topic}: {e}"
                )
                
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
                    await asyncio.sleep(delay)
                    
                    try:
                        self._create_producer()
                    except Exception as create_error:
                        logger.error(f"❌ Erro ao recriar producer: {create_error}")
                else:
                    logger.error(f"❌ Todas as {MAX_RETRIES} tentativas falharam")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                return False
        
        return False
    
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

