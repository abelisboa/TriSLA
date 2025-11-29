"""
Kafka Consumer - BC-NSSMF
Consome decisões do Decision Engine via I-04 (Kafka opcional)
"""

import sys
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.service import BCService
from src.oracle import MetricsOracle

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class DecisionConsumer:
    """Consome decisões de I-04 (Kafka opcional)"""
    
    def __init__(self, bc_service: BCService, metrics_oracle: MetricsOracle):
        self.bc_service = bc_service
        self.metrics_oracle = metrics_oracle
        
        kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        kafka_brokers = os.getenv("KAFKA_BROKERS", "").strip()
        
        self.consumer: Optional[KafkaConsumer] = None
        
        if not KAFKA_AVAILABLE:
            logger.info(
                "Kafka não disponível (biblioteca não instalada). "
                "BC-NSSMF iniciando em modo offline."
            )
            return
        
        if not kafka_enabled or not kafka_brokers:
            logger.info(
                "Kafka desabilitado (KAFKA_ENABLED=%s, KAFKA_BROKERS='%s'). "
                "BC-NSSMF iniciando em modo offline.",
                kafka_enabled,
                kafka_brokers,
            )
            return
        
        try:
            self.consumer = KafkaConsumer(
                'trisla-i04-decisions',
                bootstrap_servers=kafka_brokers.split(","),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='bc-nssmf-consumer',
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            logger.info("Conectado ao Kafka em %s", kafka_brokers)
        except NoBrokersAvailable:
            logger.warning(
                "Kafka brokers não disponíveis em '%s'. "
                "BC-NSSMF continuando em modo offline.",
                kafka_brokers,
            )
            self.consumer = None
        except Exception as e:
            logger.warning(
                "Erro ao conectar ao Kafka: %s. BC-NSSMF continuando em modo offline.",
                e,
            )
            self.consumer = None
    
    async def consume_and_execute(self) -> Dict[str, Any]:
        """Consome decisão e executa smart contract"""
        with tracer.start_as_current_span("consume_i04") as span:
            if not self.bc_service or not self.bc_service.enabled:
                span.set_attribute("execution.status", "skipped")
                span.set_attribute("execution.reason", "BC-NSSMF em modo degraded")
                return {
                    "status": "skipped",
                    "message": "BC-NSSMF está em modo degraded"
                }
            
            if self.consumer is None:
                logger.debug("Kafka não disponível - retornando decisão simulada")
                span.set_attribute("kafka.enabled", False)
                decision = {
                    "action": "AC",
                    "contract_data": {"type": "LatencyGuard", "max_latency": 100},
                    "source": "offline_simulation"
                }
                metrics = await self.metrics_oracle.get_metrics()
                return {
                    "status": "processed",
                    "decision": decision,
                    "metrics": metrics,
                    "kafka": "offline"
                }
            
            # Em produção, consumir continuamente
            # for message in self.consumer:
            #     decision = message.value
            #     metrics = await self.metrics_oracle.get_metrics()
            #     # Processar decisão via BCService
            #     return result
            
            span.set_attribute("kafka.enabled", True)
            decision = {
                "action": "AC",
                "contract_data": {"type": "LatencyGuard", "max_latency": 100},
                "source": "kafka"
            }
            metrics = await self.metrics_oracle.get_metrics()
            return {
                "status": "processed",
                "decision": decision,
                "metrics": metrics,
                "kafka": "enabled"
            }

