"""
Kafka Consumer - BC-NSSMF
Consome decisões do Decision Engine via I-04
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kafka import KafkaConsumer
import json
from typing import Dict, Any
from opentelemetry import trace

from smart_contracts import SmartContractExecutor
from oracle import MetricsOracle

tracer = trace.get_tracer(__name__)


class DecisionConsumer:
    """Consome decisões de I-04"""
    
    def __init__(self, contract_executor: SmartContractExecutor, metrics_oracle: MetricsOracle):
        self.contract_executor = contract_executor
        self.metrics_oracle = metrics_oracle
        self.consumer = KafkaConsumer(
            'trisla-i04-decisions',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='bc-nssmf-consumer'
        )
    
    async def consume_and_execute(self) -> Dict[str, Any]:
        """Consome decisão e executa smart contract"""
        with tracer.start_as_current_span("consume_i04") as span:
            # Em produção, consumir continuamente
            # for message in self.consumer:
            #     decision = message.value
            #     metrics = await self.metrics_oracle.get_metrics()
            #     return await self.contract_executor.execute(decision, metrics)
            
            # Exemplo
            decision = {
                "action": "AC",
                "contract_data": {"type": "LatencyGuard", "max_latency": 100}
            }
            metrics = await self.metrics_oracle.get_metrics()
            return await self.contract_executor.execute(decision.get("contract_data", {}), metrics)

