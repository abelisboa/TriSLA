#!/usr/bin/env python3
"""
TriSLA RAN Agent
Agente SLA específico para domínio RAN (Radio Access Network)
Monitora métricas de latência, throughput, cobertura e qualidade do sinal
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

class MetricType(Enum):
    """Tipos de métricas RAN"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    COVERAGE = "coverage"
    SIGNAL_QUALITY = "signal_quality"
    CONNECTION_DENSITY = "connection_density"
    HANDOVER_SUCCESS = "handover_success"
    BLOCKING_RATE = "blocking_rate"

class SLAStatus(Enum):
    """Status de SLA"""
    COMPLIANT = "compliant"
    VIOLATED = "violated"
    AT_RISK = "at_risk"
    UNKNOWN = "unknown"

@dataclass
class RANMetric:
    """Métrica RAN individual"""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    cell_id: str
    slice_id: Optional[str] = None
    sla_threshold: Optional[float] = None
    status: SLAStatus = SLAStatus.UNKNOWN

@dataclass
class RANSLAPolicy:
    """Política SLA para RAN"""
    metric_type: MetricType
    threshold: float
    operator: str  # "lt", "gt", "eq", "lte", "gte"
    severity: str  # "critical", "warning", "info"
    description: str

class RANAgent:
    """Agente SLA para domínio RAN"""
    
    def __init__(self, agent_id: str = "ran-agent-001"):
        self.agent_id = agent_id
        self.domain = "RAN"
        self.metrics: Dict[str, RANMetric] = {}
        self.sla_policies: List[RANSLAPolicy] = []
        self.violations: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False
        self.kafka_producer = None  # Será inicializado via interface
        
        # Configurações de monitoramento
        self.monitoring_interval = 1.0  # segundos
        self.cells = ["cell-001", "cell-002", "cell-003", "cell-004", "cell-005"]
        self.slices = ["urllc-slice", "embb-slice", "mmtc-slice"]
        
        # Inicializar políticas SLA padrão
        self._load_default_sla_policies()
    
    def _load_default_sla_policies(self):
        """Carregar políticas SLA padrão para RAN"""
        self.sla_policies = [
            RANSLAPolicy(
                metric_type=MetricType.LATENCY,
                threshold=10.0,
                operator="lte",
                severity="critical",
                description="Latência RAN deve ser ≤ 10ms para URLLC"
            ),
            RANSLAPolicy(
                metric_type=MetricType.THROUGHPUT,
                threshold=1000.0,
                operator="gte",
                severity="warning",
                description="Throughput RAN deve ser ≥ 1 Gbps para eMBB"
            ),
            RANSLAPolicy(
                metric_type=MetricType.COVERAGE,
                threshold=95.0,
                operator="gte",
                severity="critical",
                description="Cobertura RAN deve ser ≥ 95%"
            ),
            RANSLAPolicy(
                metric_type=MetricType.SIGNAL_QUALITY,
                threshold=-80.0,
                operator="gte",
                severity="warning",
                description="Qualidade do sinal deve ser ≥ -80 dBm"
            ),
            RANSLAPolicy(
                metric_type=MetricType.CONNECTION_DENSITY,
                threshold=10000.0,
                operator="gte",
                severity="info",
                description="Densidade de conexões deve suportar ≥ 10k dispositivos"
            ),
            RANSLAPolicy(
                metric_type=MetricType.HANDOVER_SUCCESS,
                threshold=99.0,
                operator="gte",
                severity="critical",
                description="Taxa de sucesso de handover deve ser ≥ 99%"
            ),
            RANSLAPolicy(
                metric_type=MetricType.BLOCKING_RATE,
                threshold=1.0,
                operator="lte",
                severity="warning",
                description="Taxa de bloqueio deve ser ≤ 1%"
            )
        ]
    
    async def start_monitoring(self):
        """Iniciar monitoramento contínuo de métricas RAN"""
        self.monitoring_active = True
        self.logger.info(f"RAN Agent {self.agent_id} iniciando monitoramento...")
        
        while self.monitoring_active:
            try:
                # Coletar métricas de todas as células
                await self._collect_ran_metrics()
                
                # Avaliar violações de SLA
                await self._evaluate_sla_violations()
                
                # Publicar métricas via Kafka
                await self._publish_metrics()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento RAN: {str(e)}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
    
    async def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring_active = False
        self.logger.info(f"RAN Agent {self.agent_id} parando monitoramento...")
    
    async def _collect_ran_metrics(self):
        """Coletar métricas específicas do domínio RAN"""
        current_time = datetime.now()
        
        for cell_id in self.cells:
            # Simular coleta de métricas reais (em produção, conectar com O-RAN)
            metrics_data = await self._simulate_ran_metrics(cell_id)
            
            for metric_type, value, unit in metrics_data:
                metric = RANMetric(
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    timestamp=current_time,
                    cell_id=cell_id,
                    slice_id=random.choice(self.slices) if random.random() > 0.3 else None
                )
                
                # Avaliar contra políticas SLA
                await self._evaluate_metric_against_policies(metric)
                
                # Armazenar métrica
                metric_key = f"{cell_id}_{metric_type.value}_{current_time.timestamp()}"
                self.metrics[metric_key] = metric
    
    async def _simulate_ran_metrics(self, cell_id: str) -> List[tuple]:
        """Simular métricas RAN (em produção, conectar com O-RAN)"""
        # Simular variações realistas baseadas no tipo de célula
        cell_factor = hash(cell_id) % 100 / 100.0
        
        metrics = []
        
        # Latência (ms) - varia entre 5-15ms
        latency = 5 + (cell_factor * 10) + random.gauss(0, 1)
        metrics.append((MetricType.LATENCY, max(1, latency), "ms"))
        
        # Throughput (Mbps) - varia entre 800-1200 Mbps
        throughput = 800 + (cell_factor * 400) + random.gauss(0, 50)
        metrics.append((MetricType.THROUGHPUT, max(100, throughput), "Mbps"))
        
        # Cobertura (%) - varia entre 90-99%
        coverage = 90 + (cell_factor * 9) + random.gauss(0, 2)
        metrics.append((MetricType.COVERAGE, min(100, max(80, coverage)), "%"))
        
        # Qualidade do sinal (dBm) - varia entre -90 a -70 dBm
        signal_quality = -90 + (cell_factor * 20) + random.gauss(0, 3)
        metrics.append((MetricType.SIGNAL_QUALITY, signal_quality, "dBm"))
        
        # Densidade de conexões - varia entre 5000-15000
        connection_density = 5000 + (cell_factor * 10000) + random.gauss(0, 1000)
        metrics.append((MetricType.CONNECTION_DENSITY, max(1000, connection_density), "devices"))
        
        # Taxa de sucesso de handover (%) - varia entre 95-99.5%
        handover_success = 95 + (cell_factor * 4.5) + random.gauss(0, 1)
        metrics.append((MetricType.HANDOVER_SUCCESS, min(100, max(90, handover_success)), "%"))
        
        # Taxa de bloqueio (%) - varia entre 0.1-2%
        blocking_rate = 0.1 + (cell_factor * 1.9) + random.gauss(0, 0.2)
        metrics.append((MetricType.BLOCKING_RATE, max(0, min(5, blocking_rate)), "%"))
        
        return metrics
    
    async def _evaluate_metric_against_policies(self, metric: RANMetric):
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
                        "cell_id": metric.cell_id,
                        "slice_id": metric.slice_id,
                        "metric_type": metric.metric_type.value,
                        "value": metric.value,
                        "threshold": policy.threshold,
                        "severity": policy.severity,
                        "description": policy.description
                    }
                    
                    self.violations.append(violation)
                    self.logger.warning(f"Violation SLA RAN: {violation}")
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
                self.logger.critical(f"CRITICAL SLA violations in RAN: {len(critical_violations)}")
            
            if warning_violations:
                self.logger.warning(f"WARNING SLA violations in RAN: {len(warning_violations)}")
    
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
                        "cell_id": metric.cell_id,
                        "slice_id": metric.slice_id,
                        "status": metric.status.value
                    })
            
            if metrics_to_publish:
                # Publicar via Kafka
                await self.kafka_producer.publish_metrics(
                    domain=self.domain,
                    metrics=metrics_to_publish
                )
                
                self.logger.debug(f"Published {len(metrics_to_publish)} RAN metrics")
        
        except Exception as e:
            self.logger.error(f"Erro ao publicar métricas RAN: {str(e)}")
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Obter resumo das métricas RAN"""
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
            "cells_monitored": len(self.cells)
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
    
    def add_sla_policy(self, policy: RANSLAPolicy):
        """Adicionar nova política SLA"""
        self.sla_policies.append(policy)
        self.logger.info(f"Nova política SLA adicionada: {policy.description}")
    
    def remove_sla_policy(self, metric_type: MetricType, description: str):
        """Remover política SLA"""
        self.sla_policies = [
            p for p in self.sla_policies
            if not (p.metric_type == metric_type and p.description == description)
        ]
        self.logger.info(f"Política SLA removida: {description}")

# Função para criar e configurar RAN Agent
async def create_ran_agent(agent_id: str = "ran-agent-001", kafka_producer=None) -> RANAgent:
    """Criar e configurar RAN Agent"""
    agent = RANAgent(agent_id)
    agent.kafka_producer = kafka_producer
    return agent

if __name__ == "__main__":
    # Teste do RAN Agent
    async def test_ran_agent():
        agent = await create_ran_agent()
        
        # Iniciar monitoramento por 10 segundos
        monitoring_task = asyncio.create_task(agent.start_monitoring())
        await asyncio.sleep(10)
        
        # Parar monitoramento
        await agent.stop_monitoring()
        monitoring_task.cancel()
        
        # Obter resumo
        summary = await agent.get_metrics_summary()
        print(f"Resumo RAN: {json.dumps(summary, indent=2)}")
        
        # Obter status SLA
        sla_status = await agent.get_sla_status()
        print(f"Status SLA: {json.dumps(sla_status, indent=2)}")
    
    asyncio.run(test_ran_agent())
