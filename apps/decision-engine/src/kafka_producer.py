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
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

