"""
Decision Producer - Fallback quando Kafka está desabilitado
EC.7 Fix - DummyProducer para evitar AttributeError
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DummyProducer:
    """Producer dummy que apenas loga operações (no-op)"""
    
    def __init__(self):
        logger.info("DummyProducer inicializado (Kafka desabilitado)")
    
    async def send_to_bc_nssmf(self, decision: Dict[str, Any]) -> None:
        """Envia decisão para BC-NSSMF (no-op quando Kafka desabilitado)"""
        logger.warning(
            f"DummyProducer: send_to_bc_nssmf chamado (Kafka desabilitado). "\n            f"Decision: {decision.get('id', 'N/A')}"
        )
        return None
    
    async def send_to_ml_nsmf(self, data: Dict[str, Any]) -> None:
        """Envia dados para ML-NSMF (no-op quando Kafka desabilitado)"""
        logger.warning(
            f"DummyProducer: send_to_ml_nsmf chamado (Kafka desabilitado). "\n            f"Data: {data.get('intent_id', 'N/A')}"
        )
        return None
    
    async def send_to_sla_agents(self, decision: Dict[str, Any]) -> None:
        """Envia decisão para SLA-Agents (no-op quando Kafka desabilitado)"""
        logger.warning(
            f"DummyProducer: send_to_sla_agents chamado (Kafka desabilitado). "\n            f"Decision: {decision.get('id', 'N/A')}"
        )
        return None


class KafkaProducer:
    """Producer real para Kafka (implementação futura)"""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        logger.info(f"KafkaProducer inicializado: {bootstrap_servers}")
        # TODO: Implementar conexão real com Kafka
    
    async def send_to_bc_nssmf(self, decision: Dict[str, Any]) -> None:
        """Envia decisão para BC-NSSMF via Kafka"""
        logger.info(f"KafkaProducer: Enviando decisão para BC-NSSMF: {decision.get('id', 'N/A')}")
        # TODO: Implementar envio real
        return None
    
    async def send_to_ml_nsmf(self, data: Dict[str, Any]) -> None:
        """Envia dados para ML-NSMF via Kafka"""
        logger.info(f"KafkaProducer: Enviando dados para ML-NSMF: {data.get('intent_id', 'N/A')}")
        # TODO: Implementar envio real
        return None
    
    async def send_to_sla_agents(self, decision: Dict[str, Any]) -> None:
        """Envia decisão para SLA-Agents via Kafka"""
        logger.info(f"KafkaProducer: Enviando decisão para SLA-Agents: {decision.get('id', 'N/A')}")
        # TODO: Implementar envio real
        return None
