"""
Kafka Producer - ML-NSMF
Envia previsões para Decision Engine via I-03
"""

from kafka import KafkaProducer
import json
from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class PredictionProducer:
    """Produz previsões para Decision Engine via Kafka (I-03)"""
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
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
            
            # Enviar para tópico Kafka
            self.producer.send('trisla-ml-predictions', value=message)
            self.producer.flush()
            
            span.set_attribute("kafka.topic", "trisla-ml-predictions")
            span.set_attribute("prediction.risk_level", prediction.get("risk_level"))
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

