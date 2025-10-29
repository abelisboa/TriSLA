#!/usr/bin/env python3
"""
TriSLA Transport Network Agent
Agente SLA específico para domínio Transport Network
Monitora métricas de largura de banda, latência, jitter, perda de pacotes e disponibilidade
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

class TNMetricType(Enum):
    """Tipos de métricas Transport Network"""
    BANDWIDTH = "bandwidth"
    LATENCY = "latency"
    JITTER = "jitter"
    PACKET_LOSS = "packet_loss"
    AVAILABILITY = "availability"
    THROUGHPUT = "throughput"
    CONGESTION = "congestion"
    LINK_UTILIZATION = "link_utilization"

class SLAStatus(Enum):
    """Status de SLA"""
    COMPLIANT = "compliant"
    VIOLATED = "violated"
    AT_RISK = "at_risk"
    UNKNOWN = "unknown"

@dataclass
class TNMetric:
    """Métrica Transport Network individual"""
    metric_type: TNMetricType
    value: float
    unit: str
    timestamp: datetime
    link_id: str
    slice_id: Optional[str] = None
    sla_threshold: Optional[float] = None
    status: SLAStatus = SLAStatus.UNKNOWN

@dataclass
class TNSLAPolicy:
    """Política SLA para Transport Network"""
    metric_type: TNMetricType
    threshold: float
    operator: str  # "lt", "gt", "eq", "lte", "gte"
    severity: str  # "critical", "warning", "info"
    description: str

class TNAgent:
    """Agente SLA para domínio Transport Network"""
    
    def __init__(self, agent_id: str = "tn-agent-001"):
        self.agent_id = agent_id
        self.domain = "Transport Network"
        self.metrics: Dict[str, TNMetric] = {}
        self.sla_policies: List[TNSLAPolicy] = []
        self.violations: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False
        self.kafka_producer = None  # Será inicializado via interface
        
        # Configurações de monitoramento
        self.monitoring_interval = 2.0  # segundos
        self.links = ["link-001", "link-002", "link-003", "link-004", "link-005"]
        self.slices = ["urllc-slice", "embb-slice", "mmtc-slice"]
        
        # Inicializar políticas SLA padrão
        self._load_default_sla_policies()
    
    def _load_default_sla_policies(self):
        """Carregar políticas SLA padrão para Transport Network"""
        self.sla_policies = [
            TNSLAPolicy(
                metric_type=TNMetricType.LATENCY,
                threshold=5.0,
                operator="lte",
                severity="critical",
                description="Latência de transporte deve ser ≤ 5ms"
            ),
            TNSLAPolicy(
                metric_type=TNMetricType.JITTER,
                threshold=1.0,
                operator="lte",
                severity="critical",
                description="Jitter deve ser ≤ 1ms"
            ),
            TNSLAPolicy(
                metric_type=TNMetricType.PACKET_LOSS,
                threshold=0.001,
                operator="lte",
                severity="critical",
                description="Perda de pacotes deve ser ≤ 0.1%"
            ),
            TNSLAPolicy(
                metric_type=TNMetricType.AVAILABILITY,
                threshold=99.9,
                operator="gte",
                severity="critical",
                description="Disponibilidade deve ser ≥ 99.9%"
            ),
            TNSLAPolicy(
                metric_type=TNMetricType.BANDWIDTH,
                threshold=1000.0,
                operator="gte",
                severity="warning",
                description="Largura de banda deve ser ≥ 1 Gbps"
            ),
            TNSLAPolicy(
                metric_type=TNMetricType.THROUGHPUT,
                threshold=800.0,
                operator="gte",
                severity="warning",
                description="Throughput deve ser ≥ 800 Mbps"
            ),
            TNSLAPolicy(
                metric_type=TNMetricType.CONGESTION,
                threshold=80.0,
                operator="lte",
                severity="warning",
                description="Congestionamento deve ser ≤ 80%"
            ),
            TNSLAPolicy(
                metric_type=TNMetricType.LINK_UTILIZATION,
                threshold=90.0,
                operator="lte",
                severity="info",
                description="Utilização de link deve ser ≤ 90%"
            )
        ]
    
    async def start_monitoring(self):
        """Iniciar monitoramento contínuo de métricas Transport Network"""
        self.monitoring_active = True
        self.logger.info(f"TN Agent {self.agent_id} iniciando monitoramento...")
        
        while self.monitoring_active:
            try:
                # Coletar métricas de todos os links
                await self._collect_tn_metrics()
                
                # Avaliar violações de SLA
                await self._evaluate_sla_violations()
                
                # Publicar métricas via Kafka
                await self._publish_metrics()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento TN: {str(e)}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
    
    async def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring_active = False
        self.logger.info(f"TN Agent {self.agent_id} parando monitoramento...")
    
    async def _collect_tn_metrics(self):
        """Coletar métricas específicas do domínio Transport Network"""
        current_time = datetime.now()
        
        for link_id in self.links:
            # Simular coleta de métricas reais (em produção, conectar com SDN/NFV)
            metrics_data = await self._simulate_tn_metrics(link_id)
            
            for metric_type, value, unit in metrics_data:
                metric = TNMetric(
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    timestamp=current_time,
                    link_id=link_id,
                    slice_id=random.choice(self.slices) if random.random() > 0.3 else None
                )
                
                # Avaliar contra políticas SLA
                await self._evaluate_metric_against_policies(metric)
                
                # Armazenar métrica
                metric_key = f"{link_id}_{metric_type.value}_{current_time.timestamp()}"
                self.metrics[metric_key] = metric
    
    async def _simulate_tn_metrics(self, link_id: str) -> List[tuple]:
        """Simular métricas Transport Network (em produção, conectar com SDN/NFV)"""
        # Simular variações realistas baseadas no tipo de link
        link_factor = hash(link_id) % 100 / 100.0
        
        metrics = []
        
        # Latência (ms) - varia entre 1-8ms
        latency = 1 + (link_factor * 7) + random.gauss(0, 0.5)
        metrics.append((TNMetricType.LATENCY, max(0.1, latency), "ms"))
        
        # Jitter (ms) - varia entre 0.1-2ms
        jitter = 0.1 + (link_factor * 1.9) + random.gauss(0, 0.1)
        metrics.append((TNMetricType.JITTER, max(0.01, jitter), "ms"))
        
        # Perda de pacotes (%) - varia entre 0.0001-0.01%
        packet_loss = 0.0001 + (link_factor * 0.0099) + random.gauss(0, 0.001)
        metrics.append((TNMetricType.PACKET_LOSS, max(0, packet_loss), "%"))
        
        # Disponibilidade (%) - varia entre 99.5-99.99%
        availability = 99.5 + (link_factor * 0.49) + random.gauss(0, 0.01)
        metrics.append((TNMetricType.AVAILABILITY, min(100, max(95, availability)), "%"))
        
        # Largura de banda (Mbps) - varia entre 800-1200 Mbps
        bandwidth = 800 + (link_factor * 400) + random.gauss(0, 50)
        metrics.append((TNMetricType.BANDWIDTH, max(100, bandwidth), "Mbps"))
        
        # Throughput (Mbps) - varia entre 700-1100 Mbps
        throughput = 700 + (link_factor * 400) + random.gauss(0, 50)
        metrics.append((TNMetricType.THROUGHPUT, max(100, throughput), "Mbps"))
        
        # Congestionamento (%) - varia entre 20-90%
        congestion = 20 + (link_factor * 70) + random.gauss(0, 5)
        metrics.append((TNMetricType.CONGESTION, max(0, min(100, congestion)), "%"))
        
        # Utilização de link (%) - varia entre 30-95%
        link_utilization = 30 + (link_factor * 65) + random.gauss(0, 5)
        metrics.append((TNMetricType.LINK_UTILIZATION, max(0, min(100, link_utilization)), "%"))
        
        return metrics
    
    async def _evaluate_metric_against_policies(self, metric: TNMetric):
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
                        "link_id": metric.link_id,
                        "slice_id": metric.slice_id,
                        "metric_type": metric.metric_type.value,
                        "value": metric.value,
                        "threshold": policy.threshold,
                        "severity": policy.severity,
                        "description": policy.description
                    }
                    
                    self.violations.append(violation)
                    self.logger.warning(f"Violation SLA TN: {violation}")
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
                self.logger.critical(f"CRITICAL SLA violations in TN: {len(critical_violations)}")
            
            if warning_violations:
                self.logger.warning(f"WARNING SLA violations in TN: {len(warning_violations)}")
    
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
                        "link_id": metric.link_id,
                        "slice_id": metric.slice_id,
                        "status": metric.status.value
                    })
            
            if metrics_to_publish:
                # Publicar via Kafka
                await self.kafka_producer.publish_metrics(
                    domain=self.domain,
                    metrics=metrics_to_publish
                )
                
                self.logger.debug(f"Published {len(metrics_to_publish)} TN metrics")
        
        except Exception as e:
            self.logger.error(f"Erro ao publicar métricas TN: {str(e)}")
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Obter resumo das métricas Transport Network"""
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
            "links_monitored": len(self.links)
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
    
    def add_sla_policy(self, policy: TNSLAPolicy):
        """Adicionar nova política SLA"""
        self.sla_policies.append(policy)
        self.logger.info(f"Nova política SLA adicionada: {policy.description}")
    
    def remove_sla_policy(self, metric_type: TNMetricType, description: str):
        """Remover política SLA"""
        self.sla_policies = [
            p for p in self.sla_policies
            if not (p.metric_type == metric_type and p.description == description)
        ]
        self.logger.info(f"Política SLA removida: {description}")

# Função para criar e configurar TN Agent
async def create_tn_agent(agent_id: str = "tn-agent-001", kafka_producer=None) -> TNAgent:
    """Criar e configurar TN Agent"""
    agent = TNAgent(agent_id)
    agent.kafka_producer = kafka_producer
    return agent

if __name__ == "__main__":
    # Teste do TN Agent
    async def test_tn_agent():
        agent = await create_tn_agent()
        
        # Iniciar monitoramento por 10 segundos
        monitoring_task = asyncio.create_task(agent.start_monitoring())
        await asyncio.sleep(10)
        
        # Parar monitoramento
        await agent.stop_monitoring()
        monitoring_task.cancel()
        
        # Obter resumo
        summary = await agent.get_metrics_summary()
        print(f"Resumo TN: {json.dumps(summary, indent=2)}")
        
        # Obter status SLA
        sla_status = await agent.get_sla_status()
        print(f"Status SLA: {json.dumps(sla_status, indent=2)}")
    
    asyncio.run(test_tn_agent())
