"""
Kafka Producer - Decision Engine
Envia decisões via I-04 (BC-NSSMF) e I-05 (SLA-Agents) - opcional
"""

import os
import logging
from typing import Dict, Any, Optional
from opentelemetry import trace

try:
    from kafka import KafkaProducer
    from kafka.errors import NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaProducer = None
    NoBrokersAvailable = Exception

import json

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class DecisionProducer:
    """Produz decisões para I-04 e I-05 (Kafka opcional)"""
    
    def __init__(self):
        kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        kafka_brokers = os.getenv("KAFKA_BROKERS", "").strip()
        
        self.producer: Optional[KafkaProducer] = None
        
        if not KAFKA_AVAILABLE:
            logger.info(
                "Kafka não disponível (biblioteca não instalada). "
                "Iniciando em modo offline."
            )
            return
        
        if not kafka_enabled or not kafka_brokers:
            logger.info(
                "Kafka desabilitado (KAFKA_ENABLED=%s, KAFKA_BROKERS='%s'). "
                "Iniciando em modo offline.",
                kafka_enabled,
                kafka_brokers,
            )
            return
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_brokers.split(","),
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Conectado ao Kafka em %s", kafka_brokers)
        except NoBrokersAvailable:
            logger.warning(
                "Kafka brokers não disponíveis em '%s'. "
                "Continuando em modo offline.",
                kafka_brokers,
            )
            self.producer = None
        except Exception as e:
            logger.warning(
                "Erro ao conectar ao Kafka: %s. Continuando em modo offline.",
                e,
            )
            self.producer = None
    
    async def send_to_bc_nssmf(self, decision: Dict[str, Any]):
        """Envia decisão para BC-NSSMF via I-04"""
        with tracer.start_as_current_span("send_i04") as span:
            message = {
                "interface": "I-04",
                "source": "decision-engine",
                "destination": "bc-nssmf",
                "decision": decision,
                "timestamp": self._get_timestamp()
            }
            
            if self.producer is None:
                logger.debug(
                    "Kafka não disponível - decisão não enviada via I-04. "
                    "Mensagem: %s",
                    message
                )
                span.set_attribute("kafka.enabled", False)
                span.set_attribute("kafka.topic", "trisla-i04-decisions")
                span.set_attribute("decision.action", decision.get("action"))
                return
            
            try:
                self.producer.send('trisla-i04-decisions', value=message)
                self.producer.flush()
                span.set_attribute("kafka.enabled", True)
                span.set_attribute("kafka.topic", "trisla-i04-decisions")
                span.set_attribute("decision.action", decision.get("action"))
            except Exception as e:
                logger.error("Erro ao enviar decisão via Kafka: %s", e)
                span.record_exception(e)
                span.set_attribute("kafka.enabled", False)
    
    async def send_to_sla_agents(self, decision: Dict[str, Any]):
        """Envia decisão para SLA-Agents via I-05"""
        with tracer.start_as_current_span("send_i05") as span:
            message = {
                "interface": "I-05",
                "source": "decision-engine",
                "destination": "sla-agents",
                "decision": decision,
                "timestamp": self._get_timestamp()
            }
            
            if self.producer is None:
                logger.debug(
                    "Kafka não disponível - decisão não enviada via I-05. "
                    "Mensagem: %s",
                    message
                )
                span.set_attribute("kafka.enabled", False)
                span.set_attribute("kafka.topic", "trisla-i05-actions")
                span.set_attribute("decision.action", decision.get("action"))
                return
            
            try:
                self.producer.send('trisla-i05-actions', value=message)
                self.producer.flush()
                span.set_attribute("kafka.enabled", True)
                span.set_attribute("kafka.topic", "trisla-i05-actions")
                span.set_attribute("decision.action", decision.get("action"))
            except Exception as e:
                logger.error("Erro ao enviar decisão via Kafka: %s", e)
                span.record_exception(e)
                span.set_attribute("kafka.enabled", False)
    
    async def send_decision_event(self, decision_result: Dict[str, Any]):
        """
        FASE 5 (C5): Publicar evento estruturado de decisão no tópico trisla-decision-events
        
        Evento estruturado contém:
        - decision_id
        - sla_id (intent_id)
        - decision (action)
        - timestamps (t_submit, t_decision)
        """
        with tracer.start_as_current_span("send_decision_event") as span:
            # Extrair timestamps do metadata
            metadata = decision_result.get("metadata", {})
            timestamps = {
                "t_submit": metadata.get("t_submit"),
                "t_decision": metadata.get("t_decision"),
                "t_event": self._get_timestamp()
            }
            
            event = {
                "decision_id": decision_result.get("decision_id"),
                "sla_id": decision_result.get("intent_id"),
                "decision": decision_result.get("action"),
                "timestamps": timestamps,
                "confidence": decision_result.get("confidence"),
                "ml_risk_score": decision_result.get("ml_risk_score"),
                "ml_risk_level": decision_result.get("ml_risk_level"),
                "reasoning": decision_result.get("reasoning")
            }
            
            if self.producer is None:
                logger.debug(
                    "Kafka não disponível - evento de decisão não publicado. "
                    "Evento: %s",
                    event
                )
                span.set_attribute("kafka.enabled", False)
                span.set_attribute("kafka.topic", "trisla-decision-events")
                return
            
            try:
                self.producer.send('trisla-decision-events', value=event)
                self.producer.flush()
                logger.info(f"✅ Evento de decisão publicado: decision_id={event['decision_id']}, action={event['decision']}")
                span.set_attribute("kafka.enabled", True)
                span.set_attribute("kafka.topic", "trisla-decision-events")
                span.set_attribute("decision.action", event["decision"])
            except Exception as e:
                logger.error("Erro ao publicar evento de decisão via Kafka: %s", e)
                span.record_exception(e)
                span.set_attribute("kafka.enabled", False)
    
    def _get_timestamp(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

