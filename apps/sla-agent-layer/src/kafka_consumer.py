"""
Kafka Consumer - SLA-Agent Layer
Consome decisões do Decision Engine via I-05 e executa ações nos agentes.
PROMPT_SNASP_01: onDecision(ACCEPT) registra SLA no NASP via NASP Adapter.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from opentelemetry import trace
import asyncio
from datetime import datetime, timezone

try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError, NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaConsumer = None
    KafkaError = Exception
    NoBrokersAvailable = Exception

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class ActionConsumer:
    """
    Consumer Kafka para I-05 (decisões do Decision Engine)
    
    Recebe decisões e executa ações nos agentes apropriados
    """
    
    def __init__(
        self,
        agents: List,
        bootstrap_servers: list = None
    ):
        """
        Inicializa consumer Kafka (opcional)
        
        Args:
            agents: Lista de agentes (AgentRAN, AgentTransport, AgentCore)
            bootstrap_servers: Lista de servidores Kafka (padrão: kafka:9092)
        """
        self.agents = agents
        
        kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
        kafka_brokers = os.getenv("KAFKA_BROKERS", "").strip()
        
        if bootstrap_servers:
            self.bootstrap_servers = bootstrap_servers
        elif kafka_brokers:
            self.bootstrap_servers = kafka_brokers.split(",")
        else:
            self.bootstrap_servers = os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS",
                "localhost:29092,kafka:9092"
            ).split(",")
        
        self.consumer = None
        self.running = False
        self.enabled = False
        
        if not KAFKA_AVAILABLE:
            logger.info(
                "Kafka não disponível (biblioteca não instalada). "
                "SLA-Agent Layer iniciando em modo offline."
            )
            return
        
        if not kafka_enabled or not kafka_brokers:
            logger.info(
                "Kafka desabilitado (KAFKA_ENABLED=%s, KAFKA_BROKERS='%s'). "
                "SLA-Agent Layer iniciando em modo offline.",
                kafka_enabled,
                kafka_brokers,
            )
            return
        
        self.enabled = True
        self._create_consumer()
    
    def _create_consumer(self):
        """Cria consumer Kafka para tópico I-05"""
        if not self.enabled:
            return
        
        try:
            self.consumer = KafkaConsumer(
                'trisla-i05-actions',
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='sla-agents-i05-consumer',
                auto_offset_reset='latest',
                enable_auto_commit=True,
                consumer_timeout_ms=1000
            )
            logger.info(f"✅ Consumer I-05 criado para tópico: trisla-i05-actions")
        except NoBrokersAvailable:
            logger.warning(
                "Kafka brokers não disponíveis. "
                "SLA-Agent Layer continuando em modo offline."
            )
            self.consumer = None
            self.enabled = False
        except Exception as e:
            logger.warning(
                "Erro ao criar consumer I-05: %s. "
                "SLA-Agent Layer continuando em modo offline.",
                e
            )
            self.consumer = None
            self.enabled = False
    
    async def consume_and_execute(self) -> Optional[Dict[str, Any]]:
        """
        Consome decisão de I-05 e executa ação no agente apropriado
        
        Returns:
            Resultado da execução da ação ou None se não houver mensagem
        """
        with tracer.start_as_current_span("consume_i05_and_execute") as span:
            if self.consumer is None:
                logger.warning("⚠️ Consumer I-05 não disponível")
                return None
            
            try:
                # Consumir mensagem (timeout de 1s)
                message = next(self.consumer, None)
                
                if message is None:
                    return None
                
                message_data = message.value
                
                span.set_attribute("kafka.topic", message.topic)
                span.set_attribute("kafka.partition", message.partition)
                span.set_attribute("kafka.offset", message.offset)
                
                # Validar estrutura da mensagem
                if not self._validate_message(message_data):
                    logger.warning("⚠️ Mensagem I-05 inválida, ignorando")
                    return None
                
                # Extrair decisão
                decision = message_data.get("decision", {})
                action = decision.get("action")
                domain = decision.get("domain", "RAN")  # Padrão: RAN
                
                span.set_attribute("decision.action", action)
                span.set_attribute("decision.domain", domain)
                
                logger.info(
                    f"✅ Mensagem I-05 recebida: action={action}, domain={domain}"
                )
                
                # PROMPT_SNASP_01: onDecision(ACCEPT) → registrar SLA no NASP via NASP Adapter (idempotente, não bloqueante)
                if action == "ACCEPT":
                    await self._register_sla_in_nasp(message_data)
                
                # Obter agente apropriado (para ações corretivas I-06; ACCEPT não tem domínio)
                agent = self._get_agent(domain)
                
                if not agent:
                    logger.warning(f"⚠️ Agente não encontrado para domínio: {domain}")
                    return {
                        "error": f"Agent not found for domain: {domain}",
                        "domain": domain,
                        "action": action
                    }
                
                # Executar ação no agente
                # Se a decisão contém 'action', usar diretamente; senão, usar 'decision' como ação
                action_to_execute = decision.get("action", decision)
                result = await agent.execute_action(action_to_execute)
                
                logger.info(
                    f"✅ Ação executada: domain={domain}, action={action}, "
                    f"executed={result.get('executed', False)}"
                )
                
                span.set_attribute("action.executed", result.get("executed", False))
                
                return result
                
            except StopIteration:
                # Timeout - nenhuma mensagem disponível
                return None
            except KafkaError as e:
                span.record_exception(e)
                logger.error(f"❌ Erro ao consumir I-05: {e}")
                return None
            except Exception as e:
                span.record_exception(e)
                logger.error(f"❌ Erro inesperado ao processar I-05: {e}", exc_info=True)
                return None
    
    def _validate_message(self, message_data: Dict[str, Any]) -> bool:
        """Valida estrutura da mensagem I-05"""
        if not isinstance(message_data, dict):
            return False
        
        if message_data.get("interface") != "I-05":
            return False
        
        decision = message_data.get("decision", {})
        if not isinstance(decision, dict):
            return False
        
        # Verificar campos obrigatórios
        if "action" not in decision:
            return False
        
        return True
    
    def _s_nssai_for_slice_type(self, slice_type: str) -> Dict[str, Any]:
        """PROMPT_SNASP_02: mapeamento determinístico slice_type → S-NSSAI (SST/SD)."""
        st = (slice_type or "eMBB").strip().upper()
        if st == "URLLC":
            return {"sst": 1, "sd": "010203"}
        if st == "MMTC":
            return {"sst": 1, "sd": "445566"}
        return {"sst": 1, "sd": "112233"}  # eMBB default

    async def _register_sla_in_nasp(self, message_data: Dict[str, Any]) -> None:
        """
        Registra SLA no NASP via NASP Adapter (PROMPT_SNASP_01 + SNASP_02).
        Payload SSOT + NSI/NSSI/S-NSSAI (3GPP-O-RAN); enriquecimento após ACCEPT.
        Idempotente, não bloqueante, log estruturado.
        """
        decision = message_data.get("decision", {})
        sla_id = decision.get("intent_id") or decision.get("sla_id")
        if not sla_id:
            logger.warning("[NASP_REGISTER] intent_id/sla_id ausente na decisão ACCEPT, ignorando")
            return
        slice_type = (decision.get("metadata") or {}).get("service_type") or "eMBB"
        payload = {
            "sla_id": sla_id,
            "status": "ACTIVE",
            "slice_type": slice_type,
            "template": (decision.get("metadata") or {}).get("template") or "GST",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "trisla",
        }
        # PROMPT_SNASP_02: alinhamento 3GPP — NSI, NSSI, S-NSSAI (regras determinísticas)
        payload["service_intent"] = {"slice_type": slice_type}
        payload["s_nssai"] = self._s_nssai_for_slice_type(slice_type)
        payload["nsi"] = {"nsi_id": f"nsi-{sla_id}"}
        payload["nssi"] = {
            "ran": f"ran-nssi-{sla_id}",
            "transport": f"tn-nssi-{sla_id}",
            "core": f"cn-nssi-{sla_id}",
        }
        nasp_url = os.getenv("NASP_ADAPTER_URL", "http://trisla-nasp-adapter.trisla.svc.cluster.local:8085")
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(f"{nasp_url}/api/v1/sla/register", json=payload)
                r.raise_for_status()
                logger.info(f"[NASP_REGISTER] SLA registrado no NASP: {sla_id}")
        except Exception as e:
            logger.warning(f"[NASP_REGISTER] Falha ao registrar SLA no NASP (não bloqueante): {e}", exc_info=False)
    
    def _get_agent(self, domain: str):
        """Retorna agente pelo domínio"""
        for agent in self.agents:
            if agent.domain.lower() == domain.lower():
                return agent
        return None
    
    async def start_consuming_loop(self):
        """
        Inicia loop contínuo de consumo de mensagens I-05
        Executa ações automaticamente nos agentes
        """
        self.running = True
        logger.info("🔄 Iniciando loop de consumo I-05...")
        
        while self.running:
            try:
                # Consumir e processar mensagem
                result = await self.consume_and_execute()
                
                if result and result.get("executed"):
                    logger.info(
                        f"✅ Ação executada: domain={result.get('domain')}, "
                        f"action={result.get('action_type')}"
                    )
                
                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de consumo: {e}", exc_info=True)
                await asyncio.sleep(1)  # Delay maior em caso de erro
    
    def stop_consuming(self):
        """Para o loop de consumo"""
        self.running = False
        logger.info("🛑 Parando loop de consumo I-05...")
    
    def close(self):
        """Fecha consumer"""
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("✅ Consumer I-05 fechado")
            except Exception as e:
                logger.error(f"❌ Erro ao fechar consumer: {e}")
            self.consumer = None
