"""
Kafka Producer - ML-NSMF
Envia previsões para Decision Engine via I-03
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


class PredictionProducer:
    """Produz previsões para Decision Engine via Kafka (I-03) - opcional"""
    
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
    
    async def send_prediction(self, prediction: Dict[str, Any], explanation: Dict[str, Any]):
        """Envia previsão para Decision Engine via I-03"""
        with tracer.start_as_current_span("send_prediction_i03") as span:
            message = {
                "interface": "I-03",
                "source": "ml-nsmf",
                "destination": "decision-engine",
                "prediction": prediction,
                "explanation": explanation,
                "timestamp": self._get_timestamp()
            }
            
            if self.producer is None:
                logger.debug(
                    "Kafka não disponível - previsão não enviada via I-03. "
                    "Mensagem: %s",
                    message
                )
                span.set_attribute("kafka.enabled", False)
                span.set_attribute("kafka.topic", "trisla-ml-predictions")
                span.set_attribute("prediction.risk_level", prediction.get("risk_level"))
                return
            
            try:
                # Enviar para tópico Kafka
                self.producer.send('trisla-ml-predictions', value=message)
                self.producer.flush()
                
                span.set_attribute("kafka.enabled", True)
                span.set_attribute("kafka.topic", "trisla-ml-predictions")
                span.set_attribute("prediction.risk_level", prediction.get("risk_level"))
            except Exception as e:
                logger.error("Erro ao enviar previsão via Kafka: %s", e)
                span.record_exception(e)
                span.set_attribute("kafka.enabled", False)
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

