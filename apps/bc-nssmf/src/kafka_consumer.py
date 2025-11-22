"""
Kafka Consumer - BC-NSSMF
Consome decisões do Decision Engine via I-04 e registra SLAs na blockchain Ethereum permissionada (GoQuorum/Besu)

Conforme dissertação TriSLA:
- Recebe decisões do Decision Engine
- Registra SLAs no contrato Solidity em Ethereum permissionado (GoQuorum/Besu)
- Rastreabilidade das cláusulas via eventos Solidity
"""

import sys
import os
import json
import hashlib
from typing import Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from opentelemetry import trace
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service import BCService
from oracle import MetricsOracle
from config import BCConfig

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class DecisionConsumer:
    """
    Consome decisões de I-04 (Decision Engine) e registra SLAs na blockchain
    
    IMPORTANTE: Todas as operações são executadas na blockchain Ethereum permissionada (GoQuorum/Besu),
    nunca em simulação Python.
    """
    
    def __init__(
        self,
        bc_service: Optional[BCService] = None,
        metrics_oracle: Optional[MetricsOracle] = None,
        bootstrap_servers: list = None
    ):
        """
        Inicializa consumer Kafka
        
        Args:
            bc_service: Serviço blockchain (padrão: cria novo)
            metrics_oracle: Oracle de métricas (padrão: cria novo)
            bootstrap_servers: Servidores Kafka (padrão: kafka:9092)
        """
        self.bc_service = bc_service or BCService()
        self.metrics_oracle = metrics_oracle or MetricsOracle()
        
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:29092,kafka:9092"
        ).split(",")
        
        # Consumer para I-04 (Decision Engine decisions)
        self.consumer = None
        self._create_consumer()
        
        # Flag para controle de loop
        self.running = False
    
    def _create_consumer(self):
        """Cria consumer Kafka para tópico I-04"""
        try:
            self.consumer = KafkaConsumer(
                'trisla-i04-decisions',
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='bc-nssmf-i04-consumer',
                auto_offset_reset='latest',
                enable_auto_commit=True,
                consumer_timeout_ms=1000
            )
            logger.info(f"✅ Consumer I-04 criado para tópico: trisla-i04-decisions")
        except Exception as e:
            logger.error(f"❌ Erro ao criar consumer I-04: {e}")
            self.consumer = None
    
    async def consume_and_execute(self) -> Optional[Dict[str, Any]]:
        """
        Consome decisão de I-04 e registra SLA na blockchain Ethereum permissionada (GoQuorum/Besu)
        
        IMPORTANTE: Esta operação registra o SLA no contrato Solidity real, não em simulação.
        
        Returns:
            Dicionário com resultado do registro (transaction_hash, sla_id) ou None
        """
        with tracer.start_as_current_span("consume_i04_and_register") as span:
            span.set_attribute("blockchain.type", "Ethereum Permissionado (GoQuorum/Besu)")
            
            if self.consumer is None:
                logger.warning("⚠️ Consumer I-04 não disponível")
                return None
            
            try:
                # Consumir mensagem (timeout de 1s)
                message = next(self.consumer, None)
                
                if message is None:
                    return None
                
                decision_data = message.value
                
                span.set_attribute("kafka.topic", message.topic)
                span.set_attribute("kafka.partition", message.partition)
                span.set_attribute("kafka.offset", message.offset)
                span.set_attribute("decision.action", decision_data.get("decision", {}).get("action", "unknown"))
                
                logger.info(f"✅ Mensagem I-04 recebida: intent_id={decision_data.get('decision', {}).get('intent_id', 'unknown')}")
                
                # Validar estrutura da mensagem
                if not self._validate_decision(decision_data):
                    logger.warning("⚠️ Mensagem I-04 inválida, ignorando")
                    return None
                
                # Extrair dados da decisão
                decision = decision_data.get("decision", {})
                intent_id = decision.get("intent_id")
                nest_id = decision.get("nest_id")
                action = decision.get("action")
                
                # Apenas registrar SLAs aceitos (AC)
                if action not in ["AC", "ACCEPT"]:
                    logger.info(f"ℹ️ Decisão {action} não requer registro em blockchain")
                    return {
                        "action": action,
                        "registered": False,
                        "reason": "Decision not accepted"
                    }
                
                # Obter métricas reais do Oracle (NASP Adapter)
                metrics = await self.metrics_oracle.get_metrics()
                
                # Preparar dados para registro no contrato Solidity
                customer = decision.get("intent_id", intent_id)  # Usar intent_id como customer
                service_name = nest_id or f"service-{intent_id}"
                
                # Gerar hash do SLA (baseado na decisão e métricas)
                sla_hash = self._hash_decision(decision, metrics)
                
                # Extrair SLOs da decisão
                slos = self._extract_slos(decision)
                
                # Registrar SLA no contrato Solidity em Ethereum permissionado (GoQuorum/Besu)
                result = self.bc_service.register_sla(
                    customer=customer,
                    service_name=service_name,
                    sla_hash=sla_hash,
                    slos=slos
                )
                
                logger.info(
                    f"✅ SLA registrado na blockchain Ethereum permissionada (GoQuorum/Besu): "
                    f"TX={result.get('transaction_hash')}, SLA_ID={result.get('sla_id')}"
                )
                
                span.set_attribute("blockchain.tx_hash", result.get("transaction_hash"))
                span.set_attribute("blockchain.sla_id", result.get("sla_id"))
                span.set_attribute("blockchain.status", "success")
                
                return {
                    "action": action,
                    "registered": True,
                    "transaction_hash": result.get("transaction_hash"),
                    "sla_id": result.get("sla_id"),
                    "block_number": result.get("block_number"),
                    "contract_address": result.get("contract_address"),
                    "blockchain_type": "Ethereum Permissionado (GoQuorum/Besu)"
                }
                
            except StopIteration:
                # Timeout - nenhuma mensagem disponível
                return None
            except KafkaError as e:
                span.record_exception(e)
                logger.error(f"❌ Erro ao consumir I-04: {e}")
                return None
            except Exception as e:
                span.record_exception(e)
                logger.error(f"❌ Erro inesperado ao processar I-04: {e}", exc_info=True)
                return None
    
    def _validate_decision(self, decision_data: Dict[str, Any]) -> bool:
        """Valida estrutura da mensagem de decisão"""
        if not isinstance(decision_data, dict):
            return False
        
        decision = decision_data.get("decision", {})
        if not isinstance(decision, dict):
            return False
        
        # Verificar campos obrigatórios
        required_fields = ["intent_id", "action"]
        return all(field in decision for field in required_fields)
    
    def _hash_decision(self, decision: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """
        Gera hash do SLA baseado na decisão e métricas
        
        Returns:
            Hash em formato hex (64 caracteres)
        """
        # Criar string representativa do SLA
        sla_string = json.dumps({
            "intent_id": decision.get("intent_id"),
            "nest_id": decision.get("nest_id"),
            "action": decision.get("action"),
            "slos": decision.get("slos", []),
            "metrics": {
                "latency": metrics.get("latency"),
                "throughput": metrics.get("throughput"),
                "reliability": metrics.get("reliability")
            }
        }, sort_keys=True)
        
        # Gerar hash SHA-256
        hash_obj = hashlib.sha256(sla_string.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _extract_slos(self, decision: Dict[str, Any]) -> list:
        """
        Extrai SLOs da decisão para formato do contrato Solidity
        
        Returns:
            Lista de SLOs no formato: [{"name": str, "value": int, "threshold": int}, ...]
        """
        slos = decision.get("slos", [])
        
        if not slos:
            # Se não há SLOs explícitos, criar baseado em metadata
            slos = []
            metadata = decision.get("metadata", {})
            
            # Adicionar SLOs padrão se disponíveis
            if "latency" in metadata:
                slos.append({
                    "name": "latency",
                    "value": int(metadata["latency"] * 1000),  # Converter ms para int
                    "threshold": int(metadata.get("latency_threshold", metadata["latency"]) * 1000)
                })
        
        # Garantir formato correto
        formatted_slos = []
        for slo in slos:
            if isinstance(slo, dict):
                formatted_slos.append({
                    "name": str(slo.get("name", "unknown")),
                    "value": int(slo.get("value", 0)),
                    "threshold": int(slo.get("threshold", slo.get("value", 0)))
                })
        
        return formatted_slos
    
    async def start_consuming_loop(self):
        """
        Inicia loop contínuo de consumo de mensagens I-04
        Registra SLAs na blockchain Ethereum permissionada (GoQuorum/Besu) automaticamente
        """
        self.running = True
        logger.info("🔄 Iniciando loop de consumo I-04...")
        
        while self.running:
            try:
                # Consumir e processar mensagem
                result = await self.consume_and_execute()
                
                if result and result.get("registered"):
                    logger.info(
                        f"✅ SLA registrado: TX={result.get('transaction_hash')}, "
                        f"SLA_ID={result.get('sla_id')}"
                    )
                
                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de consumo: {e}", exc_info=True)
                await asyncio.sleep(1)  # Delay maior em caso de erro
    
    def stop_consuming(self):
        """Para o loop de consumo"""
        self.running = False
        logger.info("🛑 Parando loop de consumo I-04...")
    
    def close(self):
        """Fecha consumer"""
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("✅ Consumer I-04 fechado")
            except Exception as e:
                logger.error(f"❌ Erro ao fechar consumer: {e}")
            self.consumer = None
