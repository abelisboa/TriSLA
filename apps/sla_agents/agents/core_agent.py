#!/usr/bin/env python3
"""
TriSLA Core Network Agent
Agente SLA específico para domínio Core Network
Monitora métricas de processamento, memória, CPU, latência de processamento e disponibilidade de serviços
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import random
import math

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoreMetricType(Enum):
    """Tipos de métricas Core Network"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    PROCESSING_LATENCY = "processing_latency"
    SERVICE_AVAILABILITY = "service_availability"
    THROUGHPUT = "throughput"
    QUEUE_DEPTH = "queue_depth"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"

class SLAStatus(Enum):
    """Status de SLA"""
    COMPLIANT = "compliant"
    VIOLATED = "violated"
    AT_RISK = "at_risk"
    UNKNOWN = "unknown"

@dataclass
class CoreMetric:
    """Métrica Core Network individual"""
    metric_type: CoreMetricType
    value: float
    unit: str
    timestamp: datetime
    service_id: str
    slice_id: Optional[str] = None
    sla_threshold: Optional[float] = None
    status: SLAStatus = SLAStatus.UNKNOWN

@dataclass
class CoreSLAPolicy:
    """Política SLA para Core Network"""
    metric_type: CoreMetricType
    threshold: float
    operator: str  # "lt", "gt", "eq", "lte", "gte"
    severity: str  # "critical", "warning", "info"
    description: str

class CoreAgent:
    """Agente SLA para domínio Core Network"""
    
    def __init__(self, agent_id: str = "core-agent-001"):
        self.agent_id = agent_id
        self.domain = "Core Network"
        self.metrics: Dict[str, CoreMetric] = {}
        self.sla_policies: List[CoreSLAPolicy] = []
        self.violations: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False
        self.kafka_producer = None  # Será inicializado via interface
        
        # Configurações de monitoramento
        self.monitoring_interval = 3.0  # segundos
        self.services = ["amf", "smf", "upf", "pcf", "udm", "ausf", "nrf", "nssf"]
        self.slices = ["urllc-slice", "embb-slice", "mmtc-slice"]
        
        # Inicializar políticas SLA padrão
        self._load_default_sla_policies()
    
    def _load_default_sla_policies(self):
        """Carregar políticas SLA padrão para Core Network"""
        self.sla_policies = [
            CoreSLAPolicy(
                metric_type=CoreMetricType.CPU_USAGE,
                threshold=80.0,
                operator="lte",
                severity="critical",
                description="Uso de CPU deve ser ≤ 80%"
            ),
            CoreSLAPolicy(
                metric_type=CoreMetricType.MEMORY_USAGE,
                threshold=85.0,
                operator="lte",
                severity="critical",
                description="Uso de memória deve ser ≤ 85%"
            ),
            CoreSLAPolicy(
                metric_type=CoreMetricType.PROCESSING_LATENCY,
                threshold=50.0,
                operator="lte",
                severity="critical",
                description="Latência de processamento deve ser ≤ 50ms"
            ),
            CoreSLAPolicy(
                metric_type=CoreMetricType.SERVICE_AVAILABILITY,
                threshold=99.9,
                operator="gte",
                severity="critical",
                description="Disponibilidade de serviço deve ser ≥ 99.9%"
            ),
            CoreSLAPolicy(
                metric_type=CoreMetricType.THROUGHPUT,
                threshold=1000.0,
                operator="gte",
                severity="warning",
                description="Throughput deve ser ≥ 1000 req/s"
            ),
            CoreSLAPolicy(
                metric_type=CoreMetricType.QUEUE_DEPTH,
                threshold=100.0,
                operator="lte",
                severity="warning",
                description="Profundidade da fila deve ser ≤ 100"
            ),
            CoreSLAPolicy(
                metric_type=CoreMetricType.ERROR_RATE,
                threshold=0.1,
                operator="lte",
                severity="critical",
                description="Taxa de erro deve ser ≤ 0.1%"
            ),
            CoreSLAPolicy(
                metric_type=CoreMetricType.RESPONSE_TIME,
                threshold=100.0,
                operator="lte",
                severity="warning",
                description="Tempo de resposta deve ser ≤ 100ms"
            )
        ]
    
    async def start_monitoring(self):
        """Iniciar monitoramento contínuo de métricas Core Network"""
        self.monitoring_active = True
        self.logger.info(f"Core Agent {self.agent_id} iniciando monitoramento...")
        
        while self.monitoring_active:
            try:
                # Coletar métricas de todos os serviços
                await self._collect_core_metrics()
                
                # Avaliar violações de SLA
                await self._evaluate_sla_violations()
                
                # Publicar métricas via Kafka
                await self._publish_metrics()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento Core: {str(e)}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
    
    async def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring_active = False
        self.logger.info(f"Core Agent {self.agent_id} parando monitoramento...")
    
    async def _collect_core_metrics(self):
        """Coletar métricas específicas do domínio Core Network"""
        current_time = datetime.now()
        
        for service_id in self.services:
            # Simular coleta de métricas reais (em produção, conectar com 5GC)
            metrics_data = await self._simulate_core_metrics(service_id)
            
            for metric_type, value, unit in metrics_data:
                metric = CoreMetric(
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    timestamp=current_time,
                    service_id=service_id,
                    slice_id=random.choice(self.slices) if random.random() > 0.3 else None
                )
                
                # Avaliar contra políticas SLA
                await self._evaluate_metric_against_policies(metric)
                
                # Armazenar métrica
                metric_key = f"{service_id}_{metric_type.value}_{current_time.timestamp()}"
                self.metrics[metric_key] = metric
    
    async def _simulate_core_metrics(self, service_id: str) -> List[tuple]:
        """Simular métricas Core Network (em produção, conectar com 5GC)"""
        # Simular variações realistas baseadas no tipo de serviço
        service_factor = hash(service_id) % 100 / 100.0
        
        metrics = []
        
        # Uso de CPU (%) - varia entre 20-90%
        cpu_usage = 20 + (service_factor * 70) + random.gauss(0, 5)
        metrics.append((CoreMetricType.CPU_USAGE, max(0, min(100, cpu_usage)), "%"))
        
        # Uso de memória (%) - varia entre 30-95%
        memory_usage = 30 + (service_factor * 65) + random.gauss(0, 5)
        metrics.append((CoreMetricType.MEMORY_USAGE, max(0, min(100, memory_usage)), "%"))
        
        # Latência de processamento (ms) - varia entre 10-80ms
        processing_latency = 10 + (service_factor * 70) + random.gauss(0, 5)
        metrics.append((CoreMetricType.PROCESSING_LATENCY, max(1, processing_latency), "ms"))
        
        # Disponibilidade de serviço (%) - varia entre 99.5-99.99%
        service_availability = 99.5 + (service_factor * 0.49) + random.gauss(0, 0.01)
        metrics.append((CoreMetricType.SERVICE_AVAILABILITY, min(100, max(95, service_availability)), "%"))
        
        # Throughput (req/s) - varia entre 500-2000 req/s
        throughput = 500 + (service_factor * 1500) + random.gauss(0, 100)
        metrics.append((CoreMetricType.THROUGHPUT, max(100, throughput), "req/s"))
        
        # Profundidade da fila - varia entre 10-150
        queue_depth = 10 + (service_factor * 140) + random.gauss(0, 10)
        metrics.append((CoreMetricType.QUEUE_DEPTH, max(0, queue_depth), "requests"))
        
        # Taxa de erro (%) - varia entre 0.001-0.5%
        error_rate = 0.001 + (service_factor * 0.499) + random.gauss(0, 0.05)
        metrics.append((CoreMetricType.ERROR_RATE, max(0, error_rate), "%"))
        
        # Tempo de resposta (ms) - varia entre 20-150ms
        response_time = 20 + (service_factor * 130) + random.gauss(0, 10)
        metrics.append((CoreMetricType.RESPONSE_TIME, max(1, response_time), "ms"))
        
        return metrics
    
    async def _evaluate_metric_against_policies(self, metric: CoreMetric):
        """Avaliar métrica contra políticas SLA"""
        for policy in self.sla_policies:
            if policy.metric_type == metric.metric_type:
                # Aplicar operador de comparação
                is_violated = self._apply_operator(
                    metric.value, policy.operator, policy.threshold
                )
                
                if is_violated:
                    metric.status = SLAStatus.VIOLATED
                    metric.sla_threshold = policy.threshold
                    
                    # Registrar violação
                    violation = {
                        "timestamp": metric.timestamp.isoformat(),
                        "agent_id": self.agent_id,
                        "domain": self.domain,
                        "service_id": metric.service_id,
                        "slice_id": metric.slice_id,
                        "metric_type": metric.metric_type.value,
                        "value": metric.value,
                        "threshold": policy.threshold,
                        "severity": policy.severity,
                        "description": policy.description
                    }
                    
                    self.violations.append(violation)
                    self.logger.warning(f"Violation SLA Core: {violation}")
                else:
                    metric.status = SLAStatus.COMPLIANT
    
    def _apply_operator(self, value: float, operator: str, threshold: float) -> bool:
        """Aplicar operador de comparação"""
        if operator == "lt":
            return value < threshold
        elif operator == "gt":
            return value > threshold
        elif operator == "eq":
            return abs(value - threshold) < 0.001
        elif operator == "lte":
            return value <= threshold
        elif operator == "gte":
            return value >= threshold
        else:
            return False
    
    async def _evaluate_sla_violations(self):
        """Avaliar violações de SLA e gerar alertas"""
        if not self.violations:
            return
        
        # Processar violações recentes (últimos 5 minutos)
        recent_violations = [
            v for v in self.violations
            if (datetime.now() - datetime.fromisoformat(v["timestamp"])).seconds < 300
        ]
        
        if recent_violations:
            # Agrupar por severidade
            critical_violations = [v for v in recent_violations if v["severity"] == "critical"]
            warning_violations = [v for v in recent_violations if v["severity"] == "warning"]
            
            if critical_violations:
                self.logger.critical(f"CRITICAL SLA violations in Core: {len(critical_violations)}")
            
            if warning_violations:
                self.logger.warning(f"WARNING SLA violations in Core: {len(warning_violations)}")
    
    async def _publish_metrics(self):
        """Publicar métricas via Kafka (Interface I-05)"""
        if not self.kafka_producer:
            return
        
        try:
            # Preparar métricas para publicação
            metrics_to_publish = []
            
            # Pegar métricas dos últimos 30 segundos
            cutoff_time = datetime.now().timestamp() - 30
            
            for metric_key, metric in self.metrics.items():
                if metric.timestamp.timestamp() > cutoff_time:
                    metrics_to_publish.append({
                        "agent_id": self.agent_id,
                        "domain": self.domain,
                        "metric_type": metric.metric_type.value,
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat(),
                        "service_id": metric.service_id,
                        "slice_id": metric.slice_id,
                        "status": metric.status.value
                    })
            
            if metrics_to_publish:
                # Publicar via Kafka
                await self.kafka_producer.publish_metrics(
                    domain=self.domain,
                    metrics=metrics_to_publish
                )
                
                self.logger.debug(f"Published {len(metrics_to_publish)} Core metrics")
        
        except Exception as e:
            self.logger.error(f"Erro ao publicar métricas Core: {str(e)}")
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Obter resumo das métricas Core Network"""
        current_time = datetime.now()
        recent_metrics = [
            m for m in self.metrics.values()
            if (current_time - m.timestamp).seconds < 300  # últimos 5 minutos
        ]
        
        if not recent_metrics:
            return {"error": "No recent metrics available"}
        
        # Agrupar por tipo de métrica
        metrics_by_type = {}
        for metric in recent_metrics:
            metric_type = metric.metric_type.value
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(metric.value)
        
        # Calcular estatísticas
        summary = {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "timestamp": current_time.isoformat(),
            "total_metrics": len(recent_metrics),
            "metrics_by_type": {},
            "sla_violations": len(self.violations),
            "services_monitored": len(self.services)
        }
        
        for metric_type, values in metrics_by_type.items():
            summary["metrics_by_type"][metric_type] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "unit": recent_metrics[0].unit if recent_metrics else "unknown"
            }
        
        return summary
    
    async def get_sla_status(self) -> Dict[str, Any]:
        """Obter status atual de SLA"""
        current_time = datetime.now()
        recent_violations = [
            v for v in self.violations
            if (current_time - datetime.fromisoformat(v["timestamp"])).seconds < 300
        ]
        
        critical_count = len([v for v in recent_violations if v["severity"] == "critical"])
        warning_count = len([v for v in recent_violations if v["severity"] == "warning"])
        
        if critical_count > 0:
            sla_status = "CRITICAL"
        elif warning_count > 0:
            sla_status = "WARNING"
        else:
            sla_status = "HEALTHY"
        
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "sla_status": sla_status,
            "critical_violations": critical_count,
            "warning_violations": warning_count,
            "total_violations": len(recent_violations),
            "timestamp": current_time.isoformat()
        }
    
    def add_sla_policy(self, policy: CoreSLAPolicy):
        """Adicionar nova política SLA"""
        self.sla_policies.append(policy)
        self.logger.info(f"Nova política SLA adicionada: {policy.description}")
    
    def remove_sla_policy(self, metric_type: CoreMetricType, description: str):
        """Remover política SLA"""
        self.sla_policies = [
            p for p in self.sla_policies
            if not (p.metric_type == metric_type and p.description == description)
        ]
        self.logger.info(f"Política SLA removida: {description}")

# Função para criar e configurar Core Agent
async def create_core_agent(agent_id: str = "core-agent-001", kafka_producer=None) -> CoreAgent:
    """Criar e configurar Core Agent"""
    agent = CoreAgent(agent_id)
    agent.kafka_producer = kafka_producer
    return agent

if __name__ == "__main__":
    # Teste do Core Agent
    async def test_core_agent():
        agent = await create_core_agent()
        
        # Iniciar monitoramento por 10 segundos
        monitoring_task = asyncio.create_task(agent.start_monitoring())
        await asyncio.sleep(10)
        
        # Parar monitoramento
        await agent.stop_monitoring()
        monitoring_task.cancel()
        
        # Obter resumo
        summary = await agent.get_metrics_summary()
        print(f"Resumo Core: {json.dumps(summary, indent=2)}")
        
        # Obter status SLA
        sla_status = await agent.get_sla_status()
        print(f"Status SLA: {json.dumps(sla_status, indent=2)}")
    
    asyncio.run(test_core_agent())

