"""
Kafka Consumer - SLA-Agent Layer
Consome ações do Decision Engine via I-05
"""

from kafka import KafkaConsumer
import json
from typing import List
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class ActionConsumer:
    """Consome ações de I-05"""
    
    def __init__(self, agents: List):
        self.agents = agents
        self.consumer = KafkaConsumer(
            'trisla-i05-actions',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='sla-agents-consumer'
        )
    
    async def consume_and_execute(self):
        """Consome ação e executa nos agentes"""
        with tracer.start_as_current_span("consume_i05") as span:
            # Em produção, consumir continuamente
            # for message in self.consumer:
            #     action = message.value
            #     domain = action.get("domain")
            #     agent = self._get_agent(domain)
            #     return await agent.execute_action(action)
            pass
    
    def _get_agent(self, domain: str):
        """Retorna agente pelo domínio"""
        for agent in self.agents:
            if agent.domain.lower() == domain.lower():
                return agent
        return None

