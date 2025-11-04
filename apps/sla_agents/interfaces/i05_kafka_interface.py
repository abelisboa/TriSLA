#!/usr/bin/env python3
"""
Interface I-05: SLA-Agent Layer ↔ Decision Engine (Kafka)
Comunicação entre agentes SLA e Decision Engine via Kafka
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
import uuid

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class SLAEvent:
    """Evento SLA publicado via Kafka"""
    event_id: str
    agent_id: str
    domain: str
    event_type: str  # "metric", "violation", "status"
    timestamp: datetime
    data: Dict[str, Any]

@dataclass
class DecisionCommand:
    """Comando do Decision Engine para agentes SLA"""
    command_id: str
    agent_id: str
    command_type: str  # "adjust_policy", "change_interval", "emergency_stop"
    timestamp: datetime
    parameters: Dict[str, Any]

class I05_SLA_Agent_Interface:
    """Interface I-05: SLA-Agent Layer ↔ Decision Engine (Kafka)"""
    
    def __init__(self, kafka_bootstrap_servers: str = "kafka:9092"):
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.logger = logging.getLogger(__name__)
        
        # Configurações de tópicos Kafka
        self.metrics_topic = "sla-metrics"
        self.violations_topic = "sla-violations"
        self.commands_topic = "sla-commands"
        self.status_topic = "sla-status"
        
        # Produtores e consumidores (serão inicializados quando necessário)
        self.producer = None
        self.consumer = None
        self.running = False
        
        # Callbacks para processamento de comandos
        self.command_callbacks: Dict[str, Callable] = {}
    
    async def initialize(self):
        """Inicializar conexões Kafka"""
        try:
            # Em produção, usar aiokafka ou kafka-python
            # Por simplicidade, simular interface Kafka
            self.logger.info("Inicializando interface Kafka...")
            self.running = True
            self.logger.info("Interface Kafka inicializada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Kafka: {str(e)}")
            raise
    
    async def shutdown(self):
        """Encerrar conexões Kafka"""
        try:
            self.running = False
            if self.producer:
                await self.producer.stop()
            if self.consumer:
                await self.consumer.stop()
            self.logger.info("Interface Kafka encerrada")
        except Exception as e:
            self.logger.error(f"Erro ao encerrar Kafka: {str(e)}")
    
    async def publish_metrics(self, domain: str, metrics: List[Dict[str, Any]]):
        """
        Publicar métricas dos agentes SLA para o Decision Engine
        
        Args:
            domain: Domínio do agente (RAN, Transport Network, Core Network)
            metrics: Lista de métricas coletadas
        """
        try:
            if not self.running:
                self.logger.warning("Kafka não inicializado, simulando publicação de métricas")
                return
            
            # Criar evento de métricas
            event = SLAEvent(
                event_id=str(uuid.uuid4()),
                agent_id=metrics[0].get("agent_id", "unknown") if metrics else "unknown",
                domain=domain,
                event_type="metric",
                timestamp=datetime.now(),
                data={
                    "metrics": metrics,
                    "count": len(metrics)
                }
            )
            
            # Simular publicação (em produção, usar Kafka real)
            self.logger.debug(f"Publicando {len(metrics)} métricas do domínio {domain}")
            
            # Em produção:
            # await self.producer.send(self.metrics_topic, json.dumps(event.__dict__).encode())
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar métricas: {str(e)}")
    
    async def publish_violation(self, domain: str, violation: Dict[str, Any]):
        """
        Publicar violação de SLA para o Decision Engine
        
        Args:
            domain: Domínio do agente
            violation: Dados da violação
        """
        try:
            if not self.running:
                self.logger.warning("Kafka não inicializado, simulando publicação de violação")
                return
            
            # Criar evento de violação
            event = SLAEvent(
                event_id=str(uuid.uuid4()),
                agent_id=violation.get("agent_id", "unknown"),
                domain=domain,
                event_type="violation",
                timestamp=datetime.now(),
                data=violation
            )
            
            # Simular publicação (em produção, usar Kafka real)
            self.logger.warning(f"Publicando violação SLA do domínio {domain}: {violation.get('description', 'N/A')}")
            
            # Em produção:
            # await self.producer.send(self.violations_topic, json.dumps(event.__dict__).encode())
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar violação: {str(e)}")
    
    async def publish_status(self, domain: str, status: Dict[str, Any]):
        """
        Publicar status do agente SLA
        
        Args:
            domain: Domínio do agente
            status: Status atual do agente
        """
        try:
            if not self.running:
                self.logger.warning("Kafka não inicializado, simulando publicação de status")
                return
            
            # Criar evento de status
            event = SLAEvent(
                event_id=str(uuid.uuid4()),
                agent_id=status.get("agent_id", "unknown"),
                domain=domain,
                event_type="status",
                timestamp=datetime.now(),
                data=status
            )
            
            # Simular publicação (em produção, usar Kafka real)
            self.logger.debug(f"Publicando status do domínio {domain}: {status.get('sla_status', 'N/A')}")
            
            # Em produção:
            # await self.producer.send(self.status_topic, json.dumps(event.__dict__).encode())
            
        except Exception as e:
            self.logger.error(f"Erro ao publicar status: {str(e)}")
    
    async def start_consuming_commands(self, callback: Callable[[DecisionCommand], None]):
        """
        Iniciar consumo de comandos do Decision Engine
        
        Args:
            callback: Função para processar comandos recebidos
        """
        try:
            if not self.running:
                self.logger.warning("Kafka não inicializado, simulando consumo de comandos")
                return
            
            self.logger.info("Iniciando consumo de comandos do Decision Engine...")
            
            # Simular consumo de comandos (em produção, usar Kafka real)
            while self.running:
                # Em produção:
                # async for message in self.consumer:
                #     command_data = json.loads(message.value.decode())
                #     command = DecisionCommand(**command_data)
                #     await callback(command)
                
                await asyncio.sleep(1)  # Simular ciclo de consumo
                
        except Exception as e:
            self.logger.error(f"Erro ao consumir comandos: {str(e)}")
    
    def register_command_callback(self, command_type: str, callback: Callable[[DecisionCommand], None]):
        """
        Registrar callback para tipo específico de comando
        
        Args:
            command_type: Tipo do comando
            callback: Função para processar o comando
        """
        self.command_callbacks[command_type] = callback
        self.logger.info(f"Callback registrado para comando: {command_type}")
    
    async def send_command(self, agent_id: str, command_type: str, parameters: Dict[str, Any]):
        """
        Enviar comando para agente específico
        
        Args:
            agent_id: ID do agente destinatário
            command_type: Tipo do comando
            parameters: Parâmetros do comando
        """
        try:
            if not self.running:
                self.logger.warning("Kafka não inicializado, simulando envio de comando")
                return
            
            # Criar comando
            command = DecisionCommand(
                command_id=str(uuid.uuid4()),
                agent_id=agent_id,
                command_type=command_type,
                timestamp=datetime.now(),
                parameters=parameters
            )
            
            # Simular envio (em produção, usar Kafka real)
            self.logger.info(f"Enviando comando {command_type} para agente {agent_id}")
            
            # Em produção:
            # await self.producer.send(self.commands_topic, json.dumps(command.__dict__).encode())
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar comando: {str(e)}")
    
    async def get_metrics_summary(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Obter resumo de métricas (simulação)
        
        Args:
            domain: Domínio específico (opcional)
            
        Returns:
            Dict: Resumo das métricas
        """
        # Simular resumo de métricas
        summary = {
            "timestamp": datetime.now().isoformat(),
            "domains": ["RAN", "Transport Network", "Core Network"],
            "total_metrics": 150,
            "active_violations": 3,
            "agents_status": {
                "RAN": "HEALTHY",
                "Transport Network": "WARNING",
                "Core Network": "HEALTHY"
            }
        }
        
        if domain:
            summary["domain"] = domain
            summary["metrics_count"] = 50
            summary["violations_count"] = 1
        
        return summary
    
    async def get_violations_summary(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Obter resumo de violações (simulação)
        
        Args:
            domain: Domínio específico (opcional)
            
        Returns:
            Dict: Resumo das violações
        """
        # Simular resumo de violações
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_violations": 3,
            "critical_violations": 1,
            "warning_violations": 2,
            "domains": {
                "RAN": {"violations": 0, "status": "HEALTHY"},
                "Transport Network": {"violations": 2, "status": "WARNING"},
                "Core Network": {"violations": 1, "status": "HEALTHY"}
            }
        }
        
        if domain:
            summary["domain"] = domain
            summary["violations"] = summary["domains"].get(domain, {}).get("violations", 0)
        
        return summary

# Cliente Kafka para agentes SLA
class SLAKafkaClient:
    """Cliente Kafka simplificado para agentes SLA"""
    
    def __init__(self, interface: I05_SLA_Agent_Interface):
        self.interface = interface
        self.logger = logging.getLogger(__name__)
    
    async def publish_metrics(self, domain: str, metrics: List[Dict[str, Any]]):
        """Publicar métricas"""
        await self.interface.publish_metrics(domain, metrics)
    
    async def publish_violation(self, domain: str, violation: Dict[str, Any]):
        """Publicar violação"""
        await self.interface.publish_violation(domain, violation)
    
    async def publish_status(self, domain: str, status: Dict[str, Any]):
        """Publicar status"""
        await self.interface.publish_status(domain, status)
    
    async def start_listening(self, callback: Callable[[DecisionCommand], None]):
        """Iniciar escuta de comandos"""
        await self.interface.start_consuming_commands(callback)

# Função para criar interface Kafka
async def create_kafka_interface(bootstrap_servers: str = "kafka:9092") -> I05_SLA_Agent_Interface:
    """Criar e inicializar interface Kafka"""
    interface = I05_SLA_Agent_Interface(bootstrap_servers)
    await interface.initialize()
    return interface

if __name__ == "__main__":
    # Teste da interface Kafka
    async def test_kafka_interface():
        interface = await create_kafka_interface()
        
        # Testar publicação de métricas
        metrics = [
            {
                "agent_id": "ran-agent-001",
                "metric_type": "latency",
                "value": 8.5,
                "unit": "ms",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        await interface.publish_metrics("RAN", metrics)
        
        # Testar publicação de violação
        violation = {
            "agent_id": "tn-agent-001",
            "metric_type": "latency",
            "value": 6.0,
            "threshold": 5.0,
            "severity": "critical",
            "description": "Latência de transporte excedeu limite"
        }
        
        await interface.publish_violation("Transport Network", violation)
        
        # Testar resumo
        summary = await interface.get_metrics_summary()
        print(f"Resumo de métricas: {json.dumps(summary, indent=2)}")
        
        # Encerrar
        await interface.shutdown()
    
    asyncio.run(test_kafka_interface())

