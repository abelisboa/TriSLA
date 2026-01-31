"""
System-Aware XAI - TriSLA v3.9.3
Explicação causal do sistema físico (distinta do ML-XAI)

Este módulo gera explicações causais baseadas em métricas reais do sistema,
permitindo responder "Por que este SLA foi RENEG?" de forma explícita.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def generate_causal_explanation(
    sla_id: str,
    decision: str,
    domain_compliance: Dict[str, Any],
    output_dir: str = "evidencias_resultados_v3.9.3/20_system_xai"
) -> Dict[str, Any]:
    """
    Gera explicação causal do sistema físico
    
    Args:
        sla_id: ID do SLA
        decision: Decisão tomada (ACCEPT, RENEG, REJECT)
        domain_compliance: Resultado de compute_all_domains_compliance()
        output_dir: Diretório de saída
    
    Returns:
        Explicação causal
    """
    bottleneck_domain = domain_compliance.get("bottleneck_domain", "unknown")
    domain_data = domain_compliance.get(bottleneck_domain, {})
    
    bottleneck_metric = domain_data.get("bottleneck_metric")
    bottleneck_value = domain_data.get("bottleneck_value")
    threshold_used = domain_data.get("threshold_used")
    
    explanation = {
        "sla_id": sla_id,
        "decision": decision,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "causal_explanation": {
            "bottleneck_domain": bottleneck_domain.upper(),
            "metric": bottleneck_metric,
            "observed": bottleneck_value,
            "threshold": threshold_used,
            "domain_compliance": domain_data.get("compliance", 0.0),
            "sla_compliance": domain_compliance.get("sla_compliance", 0.0)
        },
        "domain_compliances": {
            "ran": domain_compliance.get("ran", {}).get("compliance", 0.0),
            "transport": domain_compliance.get("transport", {}).get("compliance", 0.0),
            "core": domain_compliance.get("core", {}).get("compliance", 0.0)
        }
    }
    
    # Salvar explicação em arquivo
    os.makedirs(output_dir, exist_ok=True)
    filename = f"system_xai_{sla_id}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(explanation, f, indent=2)
        logger.info(f"✅ Explicação causal salva: {filepath}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar explicação causal: {e}")
    
    return explanation


def emit_kafka_event(
    explanation: Dict[str, Any],
    kafka_producer = None,
    topic: str = "trisla-system-xai-events"
) -> bool:
    """
    Emite evento Kafka para observabilidade (S29)
    
    Args:
        explanation: Explicação causal gerada
        kafka_producer: Producer Kafka (opcional)
        topic: Tópico Kafka
    
    Returns:
        True se evento foi emitido, False caso contrário
    """
    if kafka_producer is None:
        # Tentar importar e criar producer
        try:
            from kafka import KafkaProducer
            import json as json_lib
            
            kafka_brokers = os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS",
                "localhost:29092,kafka:9092"
            ).split(",")
            
            producer = KafkaProducer(
                bootstrap_servers=kafka_brokers,
                value_serializer=lambda v: json_lib.dumps(v).encode('utf-8')
            )
        except Exception as e:
            logger.warning(f"⚠️ Kafka não disponível para eventos S29: {e}")
            return False
    else:
        producer = kafka_producer
    
    try:
        # Emitir evento
        producer.send(topic, value=explanation)
        producer.flush()
        logger.info(f"✅ Evento Kafka S29 emitido: {topic}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao emitir evento Kafka S29: {e}")
        return False

