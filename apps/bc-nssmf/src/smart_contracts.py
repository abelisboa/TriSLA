"""
Smart Contracts - BC-NSSMF
LatencyGuard, ThroughputGuard, Adaptive Contracts
"""

from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class SmartContractExecutor:
    """Executa smart contracts"""
    
    def __init__(self):
        self.contracts = {
            "LatencyGuard": self._latency_guard,
            "ThroughputGuard": self._throughput_guard,
            "AdaptiveContract": self._adaptive_contract
        }
    
    async def execute(self, contract_data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Executa smart contract"""
        with tracer.start_as_current_span("execute_smart_contract") as span:
            contract_type = contract_data.get("type", "AdaptiveContract")
            contract_func = self.contracts.get(contract_type)
            
            if not contract_func:
                raise ValueError(f"Contract type {contract_type} not found")
            
            result = await contract_func(contract_data, metrics)
            
            span.set_attribute("contract.type", contract_type)
            span.set_attribute("contract.executed", True)
            
            return result
    
    async def _latency_guard(self, contract: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """LatencyGuard - Valida latência"""
        max_latency = contract.get("max_latency", 100)
        current_latency = metrics.get("latency", 0)
        
        violated = current_latency > max_latency
        
        return {
            "contract_type": "LatencyGuard",
            "violated": violated,
            "current": current_latency,
            "threshold": max_latency
        }
    
    async def _throughput_guard(self, contract: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """ThroughputGuard - Valida throughput"""
        min_throughput = contract.get("min_throughput", 50)
        current_throughput = metrics.get("throughput", 0)
        
        violated = current_throughput < min_throughput
        
        return {
            "contract_type": "ThroughputGuard",
            "violated": violated,
            "current": current_throughput,
            "threshold": min_throughput
        }
    
    async def _adaptive_contract(self, contract: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptive Contract - Contrato adaptativo"""
        # Lógica adaptativa baseada em métricas
        return {
            "contract_type": "AdaptiveContract",
            "status": "active",
            "metrics": metrics
        }

