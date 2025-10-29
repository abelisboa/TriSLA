#!/usr/bin/env python3
"""
TriSLA Closed Loop Controller
Implementa o ciclo contínuo: Requisição → Análise → Decisão → Execução → Observação → Ajuste
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

# Importar módulos TriSLA
from apps.common.telemetry import create_trisla_metrics, trace_function, measure_time
from apps.decision_engine.main import DecisionEngine, DecisionRequest, DecisionResponse
from apps.sla_agents.sla_coordinator import SLACoordinator
from apps.sla_agents.interfaces.i05_kafka_interface import I05_SLA_Agent_Interface

# Configurar logging
logger = logging.getLogger(__name__)

class ClosedLoopState(Enum):
    """Estados do Closed Loop"""
    IDLE = "idle"
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    DECIDING = "deciding"
    EXECUTING = "executing"
    ADJUSTING = "adjusting"
    ERROR = "error"

class ActionType(Enum):
    """Tipos de ações do Closed Loop"""
    SLICE_ACTIVATION = "slice_activation"
    SLICE_DEACTIVATION = "slice_deactivation"
    SLICE_MODIFICATION = "slice_modification"
    POLICY_ADJUSTMENT = "policy_adjustment"
    RESOURCE_SCALING = "resource_scaling"
    ALERT_NOTIFICATION = "alert_notification"

@dataclass
class ClosedLoopAction:
    """Ação do Closed Loop"""
    action_id: str
    action_type: ActionType
    target_module: str
    parameters: Dict[str, Any]
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    timestamp: datetime = None
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ClosedLoopCycle:
    """Ciclo completo do Closed Loop"""
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    state: ClosedLoopState = ClosedLoopState.IDLE
    actions: List[ClosedLoopAction] = None
    metrics: Dict[str, Any] = None
    violations: List[Dict[str, Any]] = None
    adjustments: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.metrics is None:
            self.metrics = {}
        if self.violations is None:
            self.violations = []
        if self.adjustments is None:
            self.adjustments = []

class ClosedLoopController:
    """Controlador do Closed Loop TriSLA"""
    
    def __init__(self):
        self.controller_id = f"closed-loop-{uuid.uuid4().hex[:8]}"
        self.logger = logging.getLogger(__name__)
        self.metrics = create_trisla_metrics("closed-loop")
        
        # Componentes do sistema
        self.decision_engine: Optional[DecisionEngine] = None
        self.sla_coordinator: Optional[SLACoordinator] = None
        self.kafka_interface: Optional[I05_SLA_Agent_Interface] = None
        
        # Estado do controlador
        self.running = False
        self.current_cycle: Optional[ClosedLoopCycle] = None
        self.cycle_interval = 5.0  # segundos
        self.max_cycle_duration = 300.0  # 5 minutos
        
        # Histórico de ciclos
        self.cycle_history: List[ClosedLoopCycle] = []
        self.max_history_size = 100
        
        # Callbacks para eventos
        self.event_callbacks: Dict[str, List[Callable]] = {
            "cycle_started": [],
            "cycle_completed": [],
            "violation_detected": [],
            "action_executed": [],
            "adjustment_made": []
        }
    
    async def initialize(self):
        """Inicializar controlador do Closed Loop"""
        try:
            self.logger.info(f"Inicializando Closed Loop Controller {self.controller_id}")
            
            # Inicializar componentes
            await self._initialize_components()
            
            # Configurar callbacks
            await self._setup_callbacks()
            
            self.logger.info("Closed Loop Controller inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Closed Loop Controller: {str(e)}")
            raise
    
    async def _initialize_components(self):
        """Inicializar componentes do sistema"""
        try:
            # Inicializar Decision Engine
            self.decision_engine = DecisionEngine()
            
            # Inicializar SLA Coordinator
            self.sla_coordinator = SLACoordinator()
            await self.sla_coordinator.initialize()
            
            # Inicializar Interface Kafka
            from apps.sla_agents.interfaces.i05_kafka_interface import create_kafka_interface
            self.kafka_interface = await create_kafka_interface()
            
            self.logger.info("Componentes inicializados")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar componentes: {str(e)}")
            raise
    
    async def _setup_callbacks(self):
        """Configurar callbacks para eventos"""
        try:
            # Callback para violações de SLA
            async def handle_sla_violation(violation_data):
                await self._handle_sla_violation(violation_data)
            
            if self.kafka_interface:
                self.kafka_interface.register_command_callback("sla_violation", handle_sla_violation)
            
            self.logger.info("Callbacks configurados")
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar callbacks: {str(e)}")
    
    async def start(self):
        """Iniciar Closed Loop Controller"""
        try:
            self.running = True
            self.logger.info("Iniciando Closed Loop Controller")
            
            # Iniciar SLA Coordinator
            if self.sla_coordinator:
                await self.sla_coordinator.start()
            
            # Iniciar ciclo principal
            await self._run_main_loop()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar Closed Loop Controller: {str(e)}")
            await self.stop()
    
    async def stop(self):
        """Parar Closed Loop Controller"""
        try:
            self.running = False
            self.logger.info("Parando Closed Loop Controller")
            
            # Parar SLA Coordinator
            if self.sla_coordinator:
                await self.sla_coordinator.stop()
            
            # Finalizar ciclo atual
            if self.current_cycle:
                await self._complete_current_cycle()
            
            self.logger.info("Closed Loop Controller parado")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar Closed Loop Controller: {str(e)}")
    
    async def _run_main_loop(self):
        """Executar loop principal do Closed Loop"""
        while self.running:
            try:
                # Iniciar novo ciclo
                await self._start_new_cycle()
                
                # Executar ciclo
                await self._execute_cycle()
                
                # Finalizar ciclo
                await self._complete_current_cycle()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.cycle_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no loop principal: {str(e)}")
                await asyncio.sleep(10)  # Aguardar antes de tentar novamente
    
    @trace_function(operation_name="start_new_cycle")
    async def _start_new_cycle(self):
        """Iniciar novo ciclo do Closed Loop"""
        try:
            cycle_id = f"cycle-{uuid.uuid4().hex[:8]}"
            
            self.current_cycle = ClosedLoopCycle(
                cycle_id=cycle_id,
                start_time=datetime.now(),
                state=ClosedLoopState.OBSERVING
            )
            
            # Notificar callbacks
            await self._notify_callbacks("cycle_started", self.current_cycle)
            
            self.logger.info(f"Novo ciclo iniciado: {cycle_id}")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar novo ciclo: {str(e)}")
            raise
    
    @trace_function(operation_name="execute_cycle")
    async def _execute_cycle(self):
        """Executar ciclo completo do Closed Loop"""
        try:
            if not self.current_cycle:
                return
            
            # 1. OBSERVAR - Coletar métricas e status
            await self._observe_system()
            
            # 2. ANALISAR - Detectar violações e problemas
            await self._analyze_system()
            
            # 3. DECIDIR - Tomar decisões baseadas na análise
            await self._decide_actions()
            
            # 4. EXECUTAR - Executar ações decididas
            await self._execute_actions()
            
            # 5. AJUSTAR - Ajustar sistema baseado nos resultados
            await self._adjust_system()
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ciclo: {str(e)}")
            self.current_cycle.state = ClosedLoopState.ERROR
    
    @trace_function(operation_name="observe_system")
    async def _observe_system(self):
        """Observar sistema - coletar métricas e status"""
        try:
            self.current_cycle.state = ClosedLoopState.OBSERVING
            
            # Coletar métricas dos agentes SLA
            if self.sla_coordinator:
                status = await self.sla_coordinator.get_status()
                self.current_cycle.metrics.update(status)
            
            # Coletar métricas do Decision Engine
            if self.decision_engine:
                # Simular coleta de métricas
                self.current_cycle.metrics.update({
                    "decision_engine_status": "healthy",
                    "active_policies": len(self.decision_engine.policies),
                    "decision_history_size": len(self.decision_engine.decision_history)
                })
            
            self.logger.debug(f"Métricas coletadas: {len(self.current_cycle.metrics)} itens")
            
        except Exception as e:
            self.logger.error(f"Erro ao observar sistema: {str(e)}")
            raise
    
    @trace_function(operation_name="analyze_system")
    async def _analyze_system(self):
        """Analisar sistema - detectar violações e problemas"""
        try:
            self.current_cycle.state = ClosedLoopState.ANALYZING
            
            # Analisar violações de SLA
            violations = await self._detect_sla_violations()
            self.current_cycle.violations = violations
            
            # Analisar performance
            performance_issues = await self._detect_performance_issues()
            
            # Analisar recursos
            resource_issues = await self._detect_resource_issues()
            
            self.logger.info(f"Análise concluída: {len(violations)} violações, {len(performance_issues)} problemas de performance, {len(resource_issues)} problemas de recursos")
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar sistema: {str(e)}")
            raise
    
    @trace_function(operation_name="decide_actions")
    async def _decide_actions(self):
        """Decidir ações baseadas na análise"""
        try:
            self.current_cycle.state = ClosedLoopState.DECIDING
            
            actions = []
            
            # Decidir ações para violações de SLA
            for violation in self.current_cycle.violations:
                action = await self._decide_action_for_violation(violation)
                if action:
                    actions.append(action)
            
            # Decidir ações para problemas de performance
            performance_actions = await self._decide_performance_actions()
            actions.extend(performance_actions)
            
            # Decidir ações para problemas de recursos
            resource_actions = await self._decide_resource_actions()
            actions.extend(resource_actions)
            
            # Adicionar ações ao ciclo
            self.current_cycle.actions = actions
            
            self.logger.info(f"Decisões tomadas: {len(actions)} ações")
            
        except Exception as e:
            self.logger.error(f"Erro ao decidir ações: {str(e)}")
            raise
    
    @trace_function(operation_name="execute_actions")
    async def _execute_actions(self):
        """Executar ações decididas"""
        try:
            self.current_cycle.state = ClosedLoopState.EXECUTING
            
            for action in self.current_cycle.actions:
                try:
                    # Executar ação
                    result = await self._execute_action(action)
                    action.result = result
                    action.status = "completed"
                    
                    # Notificar callbacks
                    await self._notify_callbacks("action_executed", action)
                    
                    self.logger.info(f"Ação executada: {action.action_type.value}")
                    
                except Exception as e:
                    action.status = "failed"
                    action.error_message = str(e)
                    self.logger.error(f"Erro ao executar ação {action.action_id}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ações: {str(e)}")
            raise
    
    @trace_function(operation_name="adjust_system")
    async def _adjust_system(self):
        """Ajustar sistema baseado nos resultados"""
        try:
            self.current_cycle.state = ClosedLoopState.ADJUSTING
            
            adjustments = []
            
            # Ajustar políticas baseado nos resultados
            policy_adjustments = await self._adjust_policies()
            adjustments.extend(policy_adjustments)
            
            # Ajustar configurações baseado nos resultados
            config_adjustments = await self._adjust_configurations()
            adjustments.extend(config_adjustments)
            
            # Ajustar recursos baseado nos resultados
            resource_adjustments = await self._adjust_resources()
            adjustments.extend(resource_adjustments)
            
            self.current_cycle.adjustments = adjustments
            
            # Notificar callbacks
            for adjustment in adjustments:
                await self._notify_callbacks("adjustment_made", adjustment)
            
            self.logger.info(f"Ajustes realizados: {len(adjustments)} itens")
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar sistema: {str(e)}")
            raise
    
    async def _detect_sla_violations(self) -> List[Dict[str, Any]]:
        """Detectar violações de SLA"""
        try:
            violations = []
            
            # Simular detecção de violações
            if self.current_cycle.metrics.get("total_violations", 0) > 0:
                violations.append({
                    "type": "sla_violation",
                    "domain": "RAN",
                    "metric": "latency",
                    "threshold": 10.0,
                    "actual_value": 15.0,
                    "severity": "critical",
                    "timestamp": datetime.now().isoformat()
                })
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar violações de SLA: {str(e)}")
            return []
    
    async def _detect_performance_issues(self) -> List[Dict[str, Any]]:
        """Detectar problemas de performance"""
        try:
            issues = []
            
            # Simular detecção de problemas de performance
            if self.current_cycle.metrics.get("cpu_usage", 0) > 80:
                issues.append({
                    "type": "performance_issue",
                    "metric": "cpu_usage",
                    "value": self.current_cycle.metrics.get("cpu_usage", 0),
                    "threshold": 80.0,
                    "severity": "warning"
                })
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar problemas de performance: {str(e)}")
            return []
    
    async def _detect_resource_issues(self) -> List[Dict[str, Any]]:
        """Detectar problemas de recursos"""
        try:
            issues = []
            
            # Simular detecção de problemas de recursos
            if self.current_cycle.metrics.get("memory_usage", 0) > 85:
                issues.append({
                    "type": "resource_issue",
                    "metric": "memory_usage",
                    "value": self.current_cycle.metrics.get("memory_usage", 0),
                    "threshold": 85.0,
                    "severity": "warning"
                })
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar problemas de recursos: {str(e)}")
            return []
    
    async def _decide_action_for_violation(self, violation: Dict[str, Any]) -> Optional[ClosedLoopAction]:
        """Decidir ação para violação específica"""
        try:
            violation_type = violation.get("type")
            severity = violation.get("severity", "low")
            
            if violation_type == "sla_violation":
                if severity == "critical":
                    return ClosedLoopAction(
                        action_id=str(uuid.uuid4()),
                        action_type=ActionType.SLICE_MODIFICATION,
                        target_module="nasp-api",
                        parameters={
                            "slice_id": "auto-generated",
                            "adjustments": {"latency_threshold": 5.0}
                        },
                        priority=4
                    )
                elif severity == "warning":
                    return ClosedLoopAction(
                        action_id=str(uuid.uuid4()),
                        action_type=ActionType.POLICY_ADJUSTMENT,
                        target_module="decision-engine",
                        parameters={
                            "policy_name": "latency_policy",
                            "adjustments": {"threshold": 8.0}
                        },
                        priority=2
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao decidir ação para violação: {str(e)}")
            return None
    
    async def _decide_performance_actions(self) -> List[ClosedLoopAction]:
        """Decidir ações para problemas de performance"""
        try:
            actions = []
            
            # Simular decisões de performance
            if self.current_cycle.metrics.get("cpu_usage", 0) > 80:
                actions.append(ClosedLoopAction(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.RESOURCE_SCALING,
                    target_module="kubernetes",
                    parameters={
                        "resource_type": "cpu",
                        "scale_factor": 1.5
                    },
                    priority=3
                ))
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Erro ao decidir ações de performance: {str(e)}")
            return []
    
    async def _decide_resource_actions(self) -> List[ClosedLoopAction]:
        """Decidir ações para problemas de recursos"""
        try:
            actions = []
            
            # Simular decisões de recursos
            if self.current_cycle.metrics.get("memory_usage", 0) > 85:
                actions.append(ClosedLoopAction(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.RESOURCE_SCALING,
                    target_module="kubernetes",
                    parameters={
                        "resource_type": "memory",
                        "scale_factor": 1.2
                    },
                    priority=3
                ))
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Erro ao decidir ações de recursos: {str(e)}")
            return []
    
    async def _execute_action(self, action: ClosedLoopAction) -> Dict[str, Any]:
        """Executar ação específica"""
        try:
            action.status = "executing"
            
            # Simular execução baseada no tipo de ação
            if action.action_type == ActionType.SLICE_MODIFICATION:
                result = await self._execute_slice_modification(action)
            elif action.action_type == ActionType.POLICY_ADJUSTMENT:
                result = await self._execute_policy_adjustment(action)
            elif action.action_type == ActionType.RESOURCE_SCALING:
                result = await self._execute_resource_scaling(action)
            else:
                result = {"status": "not_implemented", "message": "Ação não implementada"}
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação {action.action_id}: {str(e)}")
            raise
    
    async def _execute_slice_modification(self, action: ClosedLoopAction) -> Dict[str, Any]:
        """Executar modificação de slice"""
        try:
            # Simular modificação de slice
            self.logger.info(f"Modificando slice: {action.parameters}")
            
            return {
                "status": "success",
                "message": "Slice modificado com sucesso",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao modificar slice: {str(e)}")
            raise
    
    async def _execute_policy_adjustment(self, action: ClosedLoopAction) -> Dict[str, Any]:
        """Executar ajuste de política"""
        try:
            # Simular ajuste de política
            self.logger.info(f"Ajustando política: {action.parameters}")
            
            return {
                "status": "success",
                "message": "Política ajustada com sucesso",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar política: {str(e)}")
            raise
    
    async def _execute_resource_scaling(self, action: ClosedLoopAction) -> Dict[str, Any]:
        """Executar escalonamento de recursos"""
        try:
            # Simular escalonamento de recursos
            self.logger.info(f"Escalonando recursos: {action.parameters}")
            
            return {
                "status": "success",
                "message": "Recursos escalonados com sucesso",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao escalonar recursos: {str(e)}")
            raise
    
    async def _adjust_policies(self) -> List[Dict[str, Any]]:
        """Ajustar políticas baseado nos resultados"""
        try:
            adjustments = []
            
            # Simular ajustes de política
            adjustments.append({
                "type": "policy_adjustment",
                "policy_name": "latency_policy",
                "old_threshold": 10.0,
                "new_threshold": 8.0,
                "reason": "violations_detected"
            })
            
            return adjustments
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar políticas: {str(e)}")
            return []
    
    async def _adjust_configurations(self) -> List[Dict[str, Any]]:
        """Ajustar configurações baseado nos resultados"""
        try:
            adjustments = []
            
            # Simular ajustes de configuração
            adjustments.append({
                "type": "configuration_adjustment",
                "parameter": "cycle_interval",
                "old_value": 5.0,
                "new_value": 3.0,
                "reason": "performance_optimization"
            })
            
            return adjustments
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar configurações: {str(e)}")
            return []
    
    async def _adjust_resources(self) -> List[Dict[str, Any]]:
        """Ajustar recursos baseado nos resultados"""
        try:
            adjustments = []
            
            # Simular ajustes de recursos
            adjustments.append({
                "type": "resource_adjustment",
                "resource_type": "cpu",
                "old_limit": "1000m",
                "new_limit": "1500m",
                "reason": "high_usage_detected"
            })
            
            return adjustments
            
        except Exception as e:
            self.logger.error(f"Erro ao ajustar recursos: {str(e)}")
            return []
    
    async def _complete_current_cycle(self):
        """Finalizar ciclo atual"""
        try:
            if self.current_cycle:
                self.current_cycle.end_time = datetime.now()
                self.current_cycle.state = ClosedLoopState.IDLE
                
                # Adicionar ao histórico
                self.cycle_history.append(self.current_cycle)
                
                # Limitar tamanho do histórico
                if len(self.cycle_history) > self.max_history_size:
                    self.cycle_history = self.cycle_history[-self.max_history_size:]
                
                # Notificar callbacks
                await self._notify_callbacks("cycle_completed", self.current_cycle)
                
                self.logger.info(f"Ciclo {self.current_cycle.cycle_id} finalizado")
                
                # Limpar ciclo atual
                self.current_cycle = None
            
        except Exception as e:
            self.logger.error(f"Erro ao finalizar ciclo: {str(e)}")
    
    async def _handle_sla_violation(self, violation_data: Dict[str, Any]):
        """Manipular violação de SLA detectada"""
        try:
            self.logger.warning(f"Violation de SLA detectada: {violation_data}")
            
            # Notificar callbacks
            await self._notify_callbacks("violation_detected", violation_data)
            
            # Registrar métrica
            self.metrics.record_sla_violation(
                domain=violation_data.get("domain", "unknown"),
                violation_type=violation_data.get("type", "unknown"),
                severity=violation_data.get("severity", "unknown")
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao manipular violação de SLA: {str(e)}")
    
    async def _notify_callbacks(self, event_type: str, data: Any):
        """Notificar callbacks registrados"""
        try:
            callbacks = self.event_callbacks.get(event_type, [])
            for callback in callbacks:
                try:
                    await callback(data)
                except Exception as e:
                    self.logger.error(f"Erro no callback {event_type}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Erro ao notificar callbacks: {str(e)}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """Registrar callback para evento"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        
        self.event_callbacks[event_type].append(callback)
        self.logger.info(f"Callback registrado para evento: {event_type}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status do controlador"""
        return {
            "controller_id": self.controller_id,
            "running": self.running,
            "current_cycle": self.current_cycle.to_dict() if self.current_cycle else None,
            "cycle_history_size": len(self.cycle_history),
            "cycle_interval": self.cycle_interval,
            "max_cycle_duration": self.max_cycle_duration
        }
    
    def get_cycle_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obter histórico de ciclos"""
        recent_cycles = self.cycle_history[-limit:]
        return [cycle.to_dict() for cycle in recent_cycles]

# Função para criar controlador
async def create_closed_loop_controller() -> ClosedLoopController:
    """Criar e inicializar controlador do Closed Loop"""
    controller = ClosedLoopController()
    await controller.initialize()
    return controller
