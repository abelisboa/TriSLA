"""
Decision Persistence - Decision Engine
Persiste snapshots e explicações de decisões
FASE 3 - PROMPT_S30
"""

import os
import json
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def persist_decision_evidence(sla_id: str, snapshot: Dict[str, Any], explanation: Dict[str, Any]) -> bool:
    """
    Persiste snapshot e explicação da decisão em disco.
    
    Args:
        sla_id: ID do SLA/intent
        snapshot: Snapshot da decisão
        explanation: Explicação System-Aware XAI
        
    Returns:
        True se persistido com sucesso, False caso contrário
    """
    try:
        BASE_DIR = os.getenv("TRISLA_EVIDENCE_DIR", "/tmp/trisla_evidence")
        SNAP_DIR = os.path.join(BASE_DIR, "21_decision_engine_snapshots")
        
        os.makedirs(SNAP_DIR, exist_ok=True)
        
        logger.info(f"[S30] Persisting decision evidence in {SNAP_DIR}")
        
        # Salvar snapshot
        snapshot_file = os.path.join(SNAP_DIR, f"decision_{sla_id}.json")
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        # Salvar explicação
        explanation_file = os.path.join(SNAP_DIR, f"explanation_{sla_id}.json")
        with open(explanation_file, 'w', encoding='utf-8') as f:
            json.dump(explanation, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[S30] Persisted decision evidence for SLA {sla_id}")
        return True
        
    except Exception as e:
        logger.exception("[S30] Failed to persist decision evidence")
        return False
