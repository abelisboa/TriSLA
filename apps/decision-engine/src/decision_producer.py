"""
Decision Producer - Fallback Dummy Implementation
Provides no-op methods when Kafka is disabled
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DummyProducer:
    """Dummy producer that logs operations but does nothing"""
    
    def __init__(self):
        logger.info("DummyProducer initialized (Kafka disabled)")
    
    async def send_to_bc_nssmf(self, decision: Dict[str, Any]) -> None:
        """No-op: log but don't send to BC-NSSMF"""
        logger.info(f"DummyProducer.send_to_bc_nssmf called (no-op): decision_id={decision.get('id', 'unknown')}")
        return None
    
    async def send_to_sla_agents(self, decision: Dict[str, Any]) -> None:
        """No-op: log but don't send to SLA Agents"""
        logger.info(f"DummyProducer.send_to_sla_agents called (no-op): decision_id={decision.get('id', 'unknown')}")
        return None
