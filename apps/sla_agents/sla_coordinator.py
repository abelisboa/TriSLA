#!/usr/bin/env python3
"""
TriSLA SLA Coordinator
Coordenador da Camada Federada de Agentes SLA
Gerencia todos os agentes SLA e orquestra comunicação com Decision Engine
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import signal
import sys

# Importar agentes
from .agents.ran_agent import RANAgent, create_ran_agent
from .agents.tn_agent import TNAgent, create_tn_agent
from .agents.core_agent import CoreAgent, create_core_agent
from .interfaces.i05_kafka_interface import I05_SLA_Agent_Interface, create_kafka_interface

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SLAStatus:
    """Status geral da SLA-Agent Layer"""
    timestamp: datetime
    total_agents: int
    active_agents: int
    total_violations: int
    critical_violations: int
    warning_violations: int
    overall_status: str  # "HEALTHY", "WARNING", "CRITICAL"

class SLACoordinator:
    """Coordenador da Camada Federada de Agentes SLA"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.kafka_interface: Optional[I05_SLA_Agent_Interface] = None
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.tasks: List[asyncio.Task] = []
        
        # Configurações
        self.kafka_bootstrap_servers = "kafka:9092"
        self.monitoring_interval = 5.0  # segundos
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        self.logger.info(f"Recebido sinal {signum}, iniciando shutdown...")
        asyncio.create_task(self.shutdown())
    
    async def initialize(self):
        """Inicializar coordenador e agentes"""
        try:
            self.logger.info("Inicializando SLA Coordinator...")
            
            # Inicializar interface Kafka
            self.kafka_interface = await create_kafka_interface(self.kafka_bootstrap_servers)
            
            # Criar e inicializar agentes
            await self._create_agents()
            
            # Configurar callbacks de comando
            await self._setup_command_callbacks()
            
            self.logger.info("SLA Coordinator inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar SLA Coordinator: {str(e)}")
            raise
    
    async def _create_agents(self):
        """Criar e configurar agentes SLA"""
        try:
            # Criar RAN Agent
            ran_agent = await create_ran_agent("ran-agent-001", self.kafka_interface)
            self.agents["RAN"] = ran_agent
            self.logger.info("RAN Agent criado")
            
            # Criar TN Agent
            tn_agent = await create_tn_agent("tn-agent-001", self.kafka_interface)
            self.agents["Transport Network"] = tn_agent
            self.logger.info("TN Agent criado")
            
            # Criar Core Agent
            core_agent = await create_core_agent("core-agent-001", self.kafka_interface)
            self.agents["Core Network"] = core_agent
            self.logger.info("Core Agent criado")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar agentes: {str(e)}")
            raise
    
    async def _setup_command_callbacks(self):
        """Configurar callbacks para comandos do Decision Engine"""
        if not self.kafka_interface:
            return
        
        # Callback para comandos de ajuste de política
        async def handle_policy_adjustment(command):
            await self._handle_policy_adjustment(command)
        
        # Callback para comandos de mudança de intervalo
        async def handle_interval_change(command):
            await self._handle_interval_change(command)
        
        # Callback para comandos de parada de emergência
        async def handle_emergency_stop(command):
            await self._handle_emergency_stop(command)
        
        # Registrar callbacks
        self.kafka_interface.register_command_callback("adjust_policy", handle_policy_adjustment)
        self.kafka_interface.register_command_callback("change_interval", handle_interval_change)
        self.kafka_interface.register_command_callback("emergency_stop", handle_emergency_stop)
    
    async def start(self):
        """Iniciar coordenador e todos os agentes"""
        try:
            self.running = True
            self.logger.info("Iniciando SLA Coordinator...")
            
            # Iniciar monitoramento de todos os agentes
            for domain, agent in self.agents.items():
                task = asyncio.create_task(agent.start_monitoring())
                self.tasks.append(task)
                self.logger.info(f"Agente {domain} iniciado")
            
            # Iniciar consumo de comandos
            if self.kafka_interface:
                command_task = asyncio.create_task(
                    self.kafka_interface.start_consuming_commands(self._handle_command)
                )
                self.tasks.append(command_task)
                self.logger.info("Consumo de comandos iniciado")
            
            # Iniciar monitoramento geral
            monitoring_task = asyncio.create_task(self._monitor_overall_status())
            self.tasks.append(monitoring_task)
            self.logger.info("Monitoramento geral iniciado")
            
            self.logger.info("SLA Coordinator em execução")
            
            # Aguardar todas as tarefas
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Erro durante execução: {str(e)}")
            await self.shutdown()
    
    async def stop(self):
        """Parar coordenador e todos os agentes"""
        try:
            self.logger.info("Parando SLA Coordinator...")
            self.running = False
            
            # Parar todos os agentes
            for domain, agent in self.agents.items():
                await agent.stop_monitoring()
                self.logger.info(f"Agente {domain} parado")
            
            # Cancelar todas as tarefas
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Aguardar cancelamento
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
            self.logger.info("SLA Coordinator parado")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar coordenador: {str(e)}")
    
    async def shutdown(self):
        """Shutdown completo do coordenador"""
        try:
            await self.stop()
            
            if self.kafka_interface:
                await self.kafka_interface.shutdown()
            
            self.logger.info("SLA Coordinator encerrado")
            
        except Exception as e:
            self.logger.error(f"Erro durante shutdown: {str(e)}")
    
    async def _monitor_overall_status(self):
        """Monitorar status geral da SLA-Agent Layer"""
        while self.running:
            try:
                # Coletar status de todos os agentes
                status_data = await self._collect_overall_status()
                
                # Publicar status via Kafka
                if self.kafka_interface:
                    await self.kafka_interface.publish_status("SLA-Agent Layer", status_data)
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento geral: {str(e)}")
                await asyncio.sleep(5)
    
    async def _collect_overall_status(self) -> Dict[str, Any]:
        """Coletar status geral de todos os agentes"""
        total_violations = 0
        critical_violations = 0
        warning_violations = 0
        active_agents = 0
        
        agent_statuses = {}
        
        for domain, agent in self.agents.items():
            try:
                # Obter status do agente
                sla_status = await agent.get_sla_status()
                agent_statuses[domain] = sla_status
                
                # Contar violações
                total_violations += sla_status.get("total_violations", 0)
                critical_violations += sla_status.get("critical_violations", 0)
                warning_violations += sla_status.get("warning_violations", 0)
                
                # Verificar se agente está ativo
                if sla_status.get("sla_status") != "UNKNOWN":
                    active_agents += 1
                
            except Exception as e:
                self.logger.error(f"Erro ao obter status do agente {domain}: {str(e)}")
                agent_statuses[domain] = {"sla_status": "ERROR", "error": str(e)}
        
        # Determinar status geral
        if critical_violations > 0:
            overall_status = "CRITICAL"
        elif warning_violations > 0:
            overall_status = "WARNING"
        else:
            overall_status = "HEALTHY"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "total_violations": total_violations,
            "critical_violations": critical_violations,
            "warning_violations": warning_violations,
            "overall_status": overall_status,
            "agent_statuses": agent_statuses
        }
    
    async def _handle_command(self, command):
        """Processar comando recebido do Decision Engine"""
        try:
            self.logger.info(f"Processando comando: {command.command_type} para {command.agent_id}")
            
            # Encontrar agente destinatário
            target_agent = None
            for domain, agent in self.agents.items():
                if hasattr(agent, 'agent_id') and agent.agent_id == command.agent_id:
                    target_agent = agent
                    break
            
            if not target_agent:
                self.logger.warning(f"Agente {command.agent_id} não encontrado")
                return
            
            # Processar comando baseado no tipo
            if command.command_type == "adjust_policy":
                await self._handle_policy_adjustment(command)
            elif command.command_type == "change_interval":
                await self._handle_interval_change(command)
            elif command.command_type == "emergency_stop":
                await self._handle_emergency_stop(command)
            else:
                self.logger.warning(f"Tipo de comando desconhecido: {command.command_type}")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar comando: {str(e)}")
    
    async def _handle_policy_adjustment(self, command):
        """Processar comando de ajuste de política"""
        try:
            parameters = command.parameters
            metric_type = parameters.get("metric_type")
            new_threshold = parameters.get("threshold")
            severity = parameters.get("severity", "warning")
            
            # Aplicar ajuste de política (implementação simplificada)
            self.logger.info(f"Ajustando política: {metric_type} = {new_threshold}")
            
            # Em produção, implementar lógica específica para cada agente
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar política: {str(e)}")
    
    async def _handle_interval_change(self, command):
        """Processar comando de mudança de intervalo"""
        try:
            parameters = command.parameters
            new_interval = parameters.get("interval", 5.0)
            
            # Aplicar novo intervalo de monitoramento
            self.monitoring_interval = new_interval
            self.logger.info(f"Intervalo de monitoramento alterado para {new_interval}s")
            
        except Exception as e:
            self.logger.error(f"Erro ao alterar intervalo: {str(e)}")
    
    async def _handle_emergency_stop(self, command):
        """Processar comando de parada de emergência"""
        try:
            self.logger.critical("PARADA DE EMERGÊNCIA SOLICITADA")
            
            # Parar todos os agentes imediatamente
            for domain, agent in self.agents.items():
                await agent.stop_monitoring()
                self.logger.info(f"Agente {domain} parado por emergência")
            
        except Exception as e:
            self.logger.error(f"Erro na parada de emergência: {str(e)}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Obter status atual do coordenador"""
        return await self._collect_overall_status()
    
    async def get_agent_status(self, domain: str) -> Optional[Dict[str, Any]]:
        """Obter status de agente específico"""
        if domain not in self.agents:
            return None
        
        try:
            return await self.agents[domain].get_sla_status()
        except Exception as e:
            self.logger.error(f"Erro ao obter status do agente {domain}: {str(e)}")
            return None

# Função principal para executar coordenador
async def main():
    """Função principal para executar SLA Coordinator"""
    coordinator = SLACoordinator()
    
    try:
        # Inicializar
        await coordinator.initialize()
        
        # Iniciar execução
        await coordinator.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupção recebida, encerrando...")
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
    finally:
        # Shutdown
        await coordinator.shutdown()

if __name__ == "__main__":
    # Executar coordenador
    asyncio.run(main())
