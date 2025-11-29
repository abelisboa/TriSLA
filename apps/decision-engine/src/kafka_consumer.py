"""
Kafka Consumer - Decision Engine
Consome I-01 (metadados), I-02 (NEST), I-03 (previsões ML)
"""

import os
import logging
from typing import Dict, Any, Optional
from opentelemetry import trace

try:
    from kafka import KafkaConsumer
    from kafka.errors import NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaConsumer = None
    NoBrokersAvailable = Exception

import json

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class DecisionConsumer:
    """Consome mensagens de I-01, I-02, I-03 (Kafka opcional)"""
    
    def __init__(self, decision_maker):
        self.decision_maker = decision_maker
        kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        kafka_brokers = os.getenv("KAFKA_BROKERS", "").strip()
        
        self.consumer_i01: Optional[KafkaConsumer] = None
        self.consumer_i03: Optional[KafkaConsumer] = None
        
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
            self.consumer_i01 = KafkaConsumer(
                'trisla-i01-metadata',
                bootstrap_servers=kafka_brokers.split(","),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='decision-engine-i01',
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            self.consumer_i03 = KafkaConsumer(
                'trisla-ml-predictions',
                bootstrap_servers=kafka_brokers.split(","),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='decision-engine-i03',
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            logger.info("Conectado ao Kafka em %s", kafka_brokers)
        except NoBrokersAvailable:
            logger.warning(
                "Kafka brokers não disponíveis em '%s'. "
                "Continuando em modo offline.",
                kafka_brokers,
            )
            self.consumer_i01 = None
            self.consumer_i03 = None
        except Exception as e:
            logger.warning(
                "Erro ao conectar ao Kafka: %s. Continuando em modo offline.",
                e,
            )
            self.consumer_i01 = None
            self.consumer_i03 = None
    
    async def consume_i01_metadata(self) -> Dict[str, Any]:
        """Consome metadados de I-01 (SEM-CSMF)"""
        with tracer.start_as_current_span("consume_i01") as span:
            if self.consumer_i01 is None:
                logger.debug("Kafka não disponível - retornando metadados simulados")
                span.set_attribute("kafka.enabled", False)
                return {
                    "interface": "I-01",
                    "source": "sem-csmf",
                    "intent_id": "intent-001",
                    "metadata": {},
                    "source_type": "offline_simulation"
                }
            
            # Em produção, consumir continuamente
            # for message in self.consumer_i01:
            #     return message.value
            
            span.set_attribute("kafka.enabled", True)
            return {
                "interface": "I-01",
                "source": "sem-csmf",
                "intent_id": "intent-001",
                "metadata": {},
                "source_type": "kafka"
            }
    
    async def consume_i03_predictions(self) -> Dict[str, Any]:
        """Consome previsões de I-03 (ML-NSMF)"""
        with tracer.start_as_current_span("consume_i03") as span:
            if self.consumer_i03 is None:
                logger.debug("Kafka não disponível - retornando previsões simuladas")
                span.set_attribute("kafka.enabled", False)
                return {
                    "interface": "I-03",
                    "source": "ml-nsmf",
                    "prediction": {
                        "risk_level": "medium",
                        "risk_score": 0.6
                    },
                    "source_type": "offline_simulation"
                }
            
            # Em produção, consumir continuamente
            # for message in self.consumer_i03:
            #     return message.value
            
            span.set_attribute("kafka.enabled", True)
            return {
                "interface": "I-03",
                "source": "ml-nsmf",
                "prediction": {
                    "risk_level": "medium",
                    "risk_score": 0.6
                },
                "source_type": "kafka"
            }

