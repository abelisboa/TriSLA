"""
Kafka Producer com Retry Logic - Decision Engine
Producer com retry automático para falhas temporárias (Kafka opcional)
"""

import os
import logging
from typing import Dict, Any, Optional
from opentelemetry import trace
import asyncio

try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError, KafkaTimeoutError, NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaProducer = None
    KafkaError = Exception
    KafkaTimeoutError = Exception
    NoBrokersAvailable = Exception

import json

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Configuração de retry
MAX_RETRIES = int(os.getenv("KAFKA_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("KAFKA_RETRY_DELAY", "1.0"))
RETRY_BACKOFF = float(os.getenv("KAFKA_RETRY_BACKOFF", "2.0"))


class DecisionProducerWithRetry:
    """Produz decisões para I-04 e I-05 com retry (Kafka opcional)"""
    
    def __init__(self, bootstrap_servers: list = None):
        kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        kafka_brokers = os.getenv("KAFKA_BROKERS", "").strip()
        
        if bootstrap_servers:
            self.bootstrap_servers = bootstrap_servers
        elif kafka_brokers:
            self.bootstrap_servers = kafka_brokers.split(",")
        else:
            self.bootstrap_servers = []
        
        self.producer: Optional[KafkaProducer] = None
        self.enabled = False
        
        if not KAFKA_AVAILABLE:
            logger.info(
                "Kafka não disponível (biblioteca não instalada). "
                "DecisionProducerWithRetry em modo offline."
            )
            return
        
        if not kafka_enabled or not self.bootstrap_servers:
            logger.info(
                "Kafka desabilitado (KAFKA_ENABLED=%s, bootstrap_servers=%s). "
                "DecisionProducerWithRetry em modo offline.",
                kafka_enabled,
                self.bootstrap_servers,
            )
            return
        
        self.enabled = True
        self._create_producer()
    
    def _create_producer(self):
        """Cria ou recria o producer"""
        if not self.enabled:
            return
        
        try:
            if self.producer:
                try:
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
            logger.info("Kafka Producer criado com sucesso")
        except NoBrokersAvailable:
            logger.warning(
                "Kafka brokers não disponíveis. "
                "DecisionProducerWithRetry em modo offline."
            )
            self.producer = None
            self.enabled = False
        except Exception as e:
            logger.warning(
                "Erro ao criar Kafka Producer: %s. "
                "DecisionProducerWithRetry em modo offline.",
                e,
            )
            self.producer = None
            self.enabled = False
    
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
            
            if not self.enabled or self.producer is None:
                logger.debug(
                    "Kafka não disponível - mensagem não enviada. "
                    "Topic: %s, Value: %s",
                    topic,
                    value
                )
                span.set_attribute("kafka.enabled", False)
                span.set_attribute("retry.success", False)
                return False
            
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
    
    async def publish_decision_event(
        self,
        snapshot: Dict[str, Any],
        system_xai: Dict[str, Any],
        decision_result: Dict[str, Any]
    ) -> bool:
        """
        Publica evento completo de decisão no tópico trisla-decision-events.
        
        Este método publica snapshot causal + System-Aware XAI para observabilidade
        externa e auditoria posterior (S31.1).
        
        Args:
            snapshot: Snapshot causal da decisão (de decision_snapshot.py)
            system_xai: Explicação System-Aware XAI (de system_xai.py)
            decision_result: Resultado da decisão completo
            
        Returns:
            True se publicado com sucesso, False caso contrário
        """
        # Verificar se está habilitado via env var
        decision_events_enabled = os.getenv("DECISION_EVENTS_ENABLED", "true").lower() == "true"
        decision_events_topic = os.getenv("DECISION_EVENTS_TOPIC", "trisla-decision-events")
        
        if not decision_events_enabled:
            logger.debug(f"Decision events publishing disabled (DECISION_EVENTS_ENABLED=false)")
            return False
        
        with tracer.start_as_current_span("publish_decision_event") as span:
            span.set_attribute("kafka.topic", decision_events_topic)
            span.set_attribute("decision.sla_id", snapshot.get("sla_id", "unknown"))
            span.set_attribute("decision.action", snapshot.get("decision", "unknown"))
            
            # Construir payload completo
            event_payload = {
                "sla_id": snapshot.get("sla_id"),
                "intent_id": decision_result.get("intent_id") or snapshot.get("sla_id"),
                "nest_id": decision_result.get("nest_id"),
                "decision": snapshot.get("decision"),
                "slice_type": snapshot.get("slice_type"),
                "timestamp_utc": snapshot.get("timestamp_utc") or self._get_timestamp(),
                "snapshot": snapshot,
                "system_xai": system_xai,
                "decision_metadata": {
                    "decision_id": snapshot.get("decision_id"),
                    "confidence": snapshot.get("confidence"),
                    "ml_risk_score": snapshot.get("ml_risk_score"),
                    "ml_risk_level": snapshot.get("ml_risk_level"),
                    "reasoning": snapshot.get("reasoning")
                }
            }
            
            # Garantir que timestamp_utc está presente
            if not event_payload.get("timestamp_utc"):
                event_payload["timestamp_utc"] = self._get_timestamp()
            
            try:
                success = await self.send_with_retry(
                    decision_events_topic,
                    event_payload,
                    key=snapshot.get("sla_id") or snapshot.get("decision_id")
                )
                
                if success:
                    logger.info(
                        f"[S31.1] ✅ Decision event published to {decision_events_topic}: "
                        f"sla_id={snapshot.get('sla_id')}, decision={snapshot.get('decision')}"
                    )
                    span.set_attribute("publish.success", True)
                else:
                    logger.warning(
                        f"[S31.1] ⚠️ Failed to publish decision event to {decision_events_topic}"
                    )
                    span.set_attribute("publish.success", False)
                
                return success
                
            except Exception as e:
                logger.exception(f"[S31.1] ❌ Error publishing decision event: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("publish.success", False)
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

