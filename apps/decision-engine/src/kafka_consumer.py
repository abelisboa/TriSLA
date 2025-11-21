"""
Kafka Consumer - Decision Engine
Consome I-01 (metadados), I-02 (NEST), I-03 (previsões ML)
"""

from kafka import KafkaConsumer
import json
from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class DecisionConsumer:
    """Consome mensagens de I-01, I-02, I-03"""
    
    def __init__(self, decision_maker):
        self.decision_maker = decision_maker
        self.consumer_i01 = KafkaConsumer(
            'trisla-i01-metadata',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='decision-engine-i01'
        )
        self.consumer_i03 = KafkaConsumer(
            'trisla-ml-predictions',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='decision-engine-i03'
        )
    
    async def consume_i01_metadata(self) -> Dict[str, Any]:
        """Consome metadados de I-01 (SEM-CSMF)"""
        with tracer.start_as_current_span("consume_i01") as span:
            # Em produção, consumir continuamente
            # for message in self.consumer_i01:
            #     return message.value
            
            # Exemplo
            return {
                "interface": "I-01",
                "source": "sem-csmf",
                "intent_id": "intent-001",
                "metadata": {}
            }
    
    async def consume_i03_predictions(self) -> Dict[str, Any]:
        """Consome previsões de I-03 (ML-NSMF)"""
        with tracer.start_as_current_span("consume_i03") as span:
            # Em produção, consumir continuamente
            # for message in self.consumer_i03:
            #     return message.value
            
            # Exemplo
            return {
                "interface": "I-03",
                "source": "ml-nsmf",
                "prediction": {
                    "risk_level": "medium",
                    "risk_score": 0.6
                }
            }

