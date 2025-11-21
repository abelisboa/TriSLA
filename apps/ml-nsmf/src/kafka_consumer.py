"""
Kafka Consumer - ML-NSMF
Consome métricas do NASP
"""

from kafka import KafkaConsumer
import json
from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class MetricsConsumer:
    """Consome métricas do NASP via Kafka"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            'nasp-metrics',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='ml-nsmf-consumer'
        )
    
    async def consume_metrics(self) -> Dict[str, Any]:
        """Consome métricas do NASP"""
        with tracer.start_as_current_span("consume_metrics") as span:
            # Em produção, consumir continuamente
            # for message in self.consumer:
            #     yield message.value
            
            # Exemplo de métricas
            metrics = {
                "latency": 12.5,
                "throughput": 850.0,
                "packet_loss": 0.001,
                "jitter": 2.3,
                "timestamp": self._get_timestamp()
            }
            
            span.set_attribute("metrics.source", "nasp")
            return metrics
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

