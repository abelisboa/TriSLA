"""
Kafka Consumer - SLA-Agent Layer
Consome decisões do Decision Engine via I-05 e executa ações nos agentes
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from opentelemetry import trace
import asyncio

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
        Inicializa consumer Kafka
        
        Args:
            agents: Lista de agentes (AgentRAN, AgentTransport, AgentCore)
            bootstrap_servers: Lista de servidores Kafka (padrão: kafka:9092)
        """
        self.agents = agents
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:29092,kafka:9092"
        ).split(",")
        
        self.consumer = None
        self.running = False
        self._create_consumer()
    
    def _create_consumer(self):
        """Cria consumer Kafka para tópico I-05"""
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
        except Exception as e:
            logger.error(f"❌ Erro ao criar consumer I-05: {e}")
            self.consumer = None
    
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
                
                # Obter agente apropriado
                agent = self._get_agent(domain)
                
                if not agent:
                    logger.warning(f"⚠️ Agente não encontrado para domínio: {domain}")
                    return {
                        "error": f"Agent not found for domain: {domain}",
                        "domain": domain,
                        "action": action
                    }
                
                # Executar ação no agente
                result = await agent.execute_action(decision)
                
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
