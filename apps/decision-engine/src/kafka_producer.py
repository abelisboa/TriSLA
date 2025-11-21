"""
Kafka Producer - Decision Engine
Envia decisões via I-04 (BC-NSSMF) e I-05 (SLA-Agents)
"""

from kafka import KafkaProducer
import json
from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class DecisionProducer:
    """Produz decisões para I-04 e I-05"""
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
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
            
            self.producer.send('trisla-i04-decisions', value=message)
            self.producer.flush()
            
            span.set_attribute("kafka.topic", "trisla-i04-decisions")
            span.set_attribute("decision.action", decision.get("action"))
    
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
            
            self.producer.send('trisla-i05-actions', value=message)
            self.producer.flush()
            
            span.set_attribute("kafka.topic", "trisla-i05-actions")
            span.set_attribute("decision.action", decision.get("action"))
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

