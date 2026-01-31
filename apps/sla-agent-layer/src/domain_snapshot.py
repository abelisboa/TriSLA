"""
Domain Causal Snapshot - TriSLA v3.9.3
Cria snapshot causal por domínio antes da decisão final

Este módulo coleta métricas de todos os domínios e salva snapshot
para permitir explicação causal de decisões SLA.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def create_domain_snapshot(
    sla_id: str,
    metrics_ran: Dict[str, Any],
    metrics_transport: Dict[str, Any],
    metrics_core: Dict[str, Any],
    output_dir: str = "evidencias_resultados_v3.9.3/19_domain_causal_snapshots"
) -> Dict[str, Any]:
    """
    Cria snapshot causal por domínio
    
    Args:
        sla_id: ID do SLA
        metrics_ran: Métricas do RAN
        metrics_transport: Métricas do Transport
        metrics_core: Métricas do Core
        output_dir: Diretório de saída
    
    Returns:
        Snapshot criado
    """
    snapshot = {
        "sla_id": sla_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "domains": {
            "ran": metrics_ran,
            "transport": metrics_transport,
            "core": metrics_core
        }
    }
    
    # Salvar snapshot em arquivo
    os.makedirs(output_dir, exist_ok=True)
    filename = f"domain_snapshot_{sla_id}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        logger.info(f"✅ Snapshot causal salvo: {filepath}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar snapshot: {e}")
    
    return snapshot
