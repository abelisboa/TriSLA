"""
Kafka Consumer - Decision Engine
Consome I-03 (previsões ML-NSMF) e processa decisões automaticamente
"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
from typing import Dict, Any, Optional, Callable
from opentelemetry import trace
import asyncio
import logging
import os

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class DecisionConsumer:
    """
    Consome mensagens de I-03 (ML-NSMF predictions) e processa decisões
    """
    
    def __init__(
        self,
        decision_callback: Optional[Callable] = None,
        bootstrap_servers: list = None
    ):
        """
        Inicializa consumer Kafka
        
        Args:
            decision_callback: Função async para processar decisão (opcional)
            bootstrap_servers: Lista de servidores Kafka (padrão: kafka:9092)
        """
        self.decision_callback = decision_callback
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:29092,kafka:9092"
        ).split(",")
        
        # Consumer para I-03 (ML-NSMF predictions)
        self.consumer_i03 = None
        self._create_consumer_i03()
        
        # Flag para controle de loop
        self.running = False
    
    def _create_consumer_i03(self):
        """Cria consumer para tópico I-03"""
        try:
            self.consumer_i03 = KafkaConsumer(
                'ml-nsmf-predictions',  # Tópico I-03
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='decision-engine-i03',
                auto_offset_reset='latest',  # Começar do último offset
                enable_auto_commit=True,
                consumer_timeout_ms=1000  # Timeout para não bloquear indefinidamente
            )
            logger.info(f"✅ Consumer I-03 criado para tópico: ml-nsmf-predictions")
        except Exception as e:
            logger.error(f"❌ Erro ao criar consumer I-03: {e}")
            self.consumer_i03 = None
    
    async def consume_i03_predictions(self) -> Optional[Dict[str, Any]]:
        """
        Consome uma mensagem de I-03 (ML-NSMF predictions)
        
        Returns:
            Dicionário com predição do ML-NSMF ou None se não houver mensagem
        """
        with tracer.start_as_current_span("consume_i03") as span:
            if self.consumer_i03 is None:
                logger.warning("⚠️ Consumer I-03 não disponível")
                return None
            
            try:
                # Consumir mensagem (timeout de 1s)
                message = next(self.consumer_i03, None)
                
                if message is None:
                    return None
                
                prediction_data = message.value
                
                span.set_attribute("kafka.topic", message.topic)
                span.set_attribute("kafka.partition", message.partition)
                span.set_attribute("kafka.offset", message.offset)
                span.set_attribute("prediction.intent_id", prediction_data.get("intent_id", "unknown"))
                
                logger.info(f"✅ Mensagem I-03 recebida: intent_id={prediction_data.get('intent_id')}")
                
                return prediction_data
                
            except StopIteration:
                # Timeout - nenhuma mensagem disponível
                return None
            except KafkaError as e:
                span.record_exception(e)
                logger.error(f"❌ Erro ao consumir I-03: {e}")
                return None
            except Exception as e:
                span.record_exception(e)
                logger.error(f"❌ Erro inesperado ao consumir I-03: {e}")
                return None
    
    async def start_consuming_loop(self):
        """
        Inicia loop contínuo de consumo de mensagens I-03
        Processa predições do ML-NSMF e gera decisões automaticamente
        """
        self.running = True
        logger.info("🔄 Iniciando loop de consumo I-03...")
        
        while self.running:
            try:
                # Consumir mensagem
                prediction_data = await self.consume_i03_predictions()
                
                if prediction_data and self.decision_callback:
                    # Processar decisão usando callback
                    await self.decision_callback(prediction_data)
                
                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de consumo: {e}")
                await asyncio.sleep(1)  # Delay maior em caso de erro
    
    def stop_consuming(self):
        """Para o loop de consumo"""
        self.running = False
        logger.info("🛑 Parando loop de consumo I-03...")
    
    def close(self):
        """Fecha consumer"""
        if self.consumer_i03:
            try:
                self.consumer_i03.close()
                logger.info("✅ Consumer I-03 fechado")
            except Exception as e:
                logger.error(f"❌ Erro ao fechar consumer: {e}")
            self.consumer_i03 = None
