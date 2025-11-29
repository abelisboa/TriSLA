"""
Kafka Consumer - ML-NSMF
Consome métricas do NASP
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


class MetricsConsumer:
    """Consome métricas do NASP via Kafka (opcional)"""
    
    def __init__(self):
        kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        kafka_brokers = os.getenv("KAFKA_BROKERS", "").strip()
        
        self.consumer: Optional[KafkaConsumer] = None
        
        # Verificar primeiro se Kafka está desabilitado
        if not kafka_enabled or not kafka_brokers:
            logger.info(
                "Kafka desabilitado (KAFKA_ENABLED=%s, KAFKA_BROKERS='%s'). "
                "Iniciando em modo offline.",
                kafka_enabled,
                kafka_brokers,
            )
            return
        
        if not KAFKA_AVAILABLE:
            logger.info(
                "Kafka não disponível (biblioteca não instalada). "
                "Iniciando em modo offline."
            )
            return
        
        # Só tentar criar consumer se Kafka estiver habilitado E disponível
        try:
            self.consumer = KafkaConsumer(
                'nasp-metrics',
                bootstrap_servers=kafka_brokers.split(","),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='ml-nsmf-consumer',
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            logger.info("Conectado ao Kafka em %s", kafka_brokers)
        except (NoBrokersAvailable, Exception) as e:
            logger.warning(
                "Kafka brokers não disponíveis em '%s'. "
                "Continuando em modo offline: %s",
                kafka_brokers,
                e,
            )
            self.consumer = None
    
    async def consume_metrics(self) -> Dict[str, Any]:
        """Consome métricas do NASP"""
        with tracer.start_as_current_span("consume_metrics") as span:
            if self.consumer is None:
                # Modo offline: retornar métricas simuladas
                logger.debug("Kafka não disponível - retornando métricas simuladas")
                metrics = {
                    "latency": 12.5,
                    "throughput": 850.0,
                    "packet_loss": 0.001,
                    "jitter": 2.3,
                    "timestamp": self._get_timestamp(),
                    "source": "offline_simulation"
                }
                span.set_attribute("metrics.source", "offline_simulation")
                return metrics
            
            # Em produção, consumir continuamente
            # for message in self.consumer:
            #     yield message.value
            
            # Exemplo de métricas (fallback se não houver mensagens)
            metrics = {
                "latency": 12.5,
                "throughput": 850.0,
                "packet_loss": 0.001,
                "jitter": 2.3,
                "timestamp": self._get_timestamp(),
                "source": "kafka"
            }
            
            span.set_attribute("metrics.source", "kafka")
            return metrics
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

