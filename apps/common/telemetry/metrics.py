#!/usr/bin/env python3
"""
TriSLA Custom Metrics
Métricas personalizadas para monitoramento da arquitetura TriSLA
"""

import time
from typing import Dict, Any, Optional, List
from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram, Gauge, UpDownCounter

# Configurar logging
import logging
logger = logging.getLogger(__name__)

class TriSLAMetrics:
    """Classe para métricas personalizadas da TriSLA"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.meter = metrics.get_meter(f"trisla.{service_name}")
        
        # Métricas de SLA
        self._setup_sla_metrics()
        
        # Métricas de performance
        self._setup_performance_metrics()
        
        # Métricas de sistema
        self._setup_system_metrics()
        
        # Métricas de negócio
        self._setup_business_metrics()
    
    def _setup_sla_metrics(self):
        """Configurar métricas de SLA"""
        # Contador de violações SLA
        self.sla_violations = self.meter.create_counter(
            name="trisla_sla_violations_total",
            description="Total de violações de SLA",
            unit="1"
        )
        
        # Contador de slices ativados
        self.slices_activated = self.meter.create_counter(
            name="trisla_slices_activated_total",
            description="Total de slices ativados",
            unit="1"
        )
        
        # Contador de slices desativados
        self.slices_deactivated = self.meter.create_counter(
            name="trisla_slices_deactivated_total",
            description="Total de slices desativados",
            unit="1"
        )
        
        # Histograma de latência SLA
        self.sla_latency = self.meter.create_histogram(
            name="trisla_sla_latency_seconds",
            description="Latência de processamento SLA",
            unit="s"
        )
        
        # Gauge de disponibilidade SLA
        self.sla_availability = self.meter.create_gauge(
            name="trisla_sla_availability_percent",
            description="Disponibilidade SLA atual",
            unit="%"
        )
    
    def _setup_performance_metrics(self):
        """Configurar métricas de performance"""
        # Histograma de tempo de resposta
        self.response_time = self.meter.create_histogram(
            name="trisla_response_time_seconds",
            description="Tempo de resposta das operações",
            unit="s"
        )
        
        # Contador de requisições
        self.requests_total = self.meter.create_counter(
            name="trisla_requests_total",
            description="Total de requisições processadas",
            unit="1"
        )
        
        # Contador de erros
        self.errors_total = self.meter.create_counter(
            name="trisla_errors_total",
            description="Total de erros processados",
            unit="1"
        )
        
        # Gauge de throughput
        self.throughput = self.meter.create_gauge(
            name="trisla_throughput_per_second",
            description="Throughput atual (requisições por segundo)",
            unit="req/s"
        )
    
    def _setup_system_metrics(self):
        """Configurar métricas de sistema"""
        # Gauge de uso de CPU
        self.cpu_usage = self.meter.create_gauge(
            name="trisla_cpu_usage_percent",
            description="Uso de CPU atual",
            unit="%"
        )
        
        # Gauge de uso de memória
        self.memory_usage = self.meter.create_gauge(
            name="trisla_memory_usage_bytes",
            description="Uso de memória atual",
            unit="bytes"
        )
        
        # Gauge de conexões ativas
        self.active_connections = self.meter.create_gauge(
            name="trisla_active_connections",
            description="Número de conexões ativas",
            unit="1"
        )
        
        # Contador de reinicializações
        self.restarts_total = self.meter.create_counter(
            name="trisla_restarts_total",
            description="Total de reinicializações do serviço",
            unit="1"
        )
    
    def _setup_business_metrics(self):
        """Configurar métricas de negócio"""
        # Contador de decisões tomadas
        self.decisions_total = self.meter.create_counter(
            name="trisla_decisions_total",
            description="Total de decisões tomadas pelo Decision Engine",
            unit="1"
        )
        
        # Contador de predições ML
        self.ml_predictions_total = self.meter.create_counter(
            name="trisla_ml_predictions_total",
            description="Total de predições ML realizadas",
            unit="1"
        )
        
        # Contador de análises semânticas
        self.semantic_analyses_total = self.meter.create_counter(
            name="trisla_semantic_analyses_total",
            description="Total de análises semânticas realizadas",
            unit="1"
        )
        
        # Contador de validações blockchain
        self.blockchain_validations_total = self.meter.create_counter(
            name="trisla_blockchain_validations_total",
            description="Total de validações blockchain realizadas",
            unit="1"
        )
    
    # Métodos para SLA
    def record_sla_violation(self, domain: str, violation_type: str, severity: str):
        """Registrar violação de SLA"""
        self.sla_violations.add(1, {
            "domain": domain,
            "violation_type": violation_type,
            "severity": severity,
            "service": self.service_name
        })
    
    def record_slice_activated(self, slice_type: str, slice_id: str):
        """Registrar slice ativado"""
        self.slices_activated.add(1, {
            "slice_type": slice_type,
            "slice_id": slice_id,
            "service": self.service_name
        })
    
    def record_slice_deactivated(self, slice_type: str, slice_id: str):
        """Registrar slice desativado"""
        self.slices_deactivated.add(1, {
            "slice_type": slice_type,
            "slice_id": slice_id,
            "service": self.service_name
        })
    
    def record_sla_latency(self, latency: float, domain: str):
        """Registrar latência SLA"""
        self.sla_latency.record(latency, {
            "domain": domain,
            "service": self.service_name
        })
    
    def set_sla_availability(self, availability: float, domain: str):
        """Definir disponibilidade SLA"""
        self.sla_availability.set(availability, {
            "domain": domain,
            "service": self.service_name
        })
    
    # Métodos para performance
    def record_response_time(self, response_time: float, operation: str, status: str):
        """Registrar tempo de resposta"""
        self.response_time.record(response_time, {
            "operation": operation,
            "status": status,
            "service": self.service_name
        })
    
    def record_request(self, operation: str, status: str):
        """Registrar requisição"""
        self.requests_total.add(1, {
            "operation": operation,
            "status": status,
            "service": self.service_name
        })
    
    def record_error(self, error_type: str, operation: str):
        """Registrar erro"""
        self.errors_total.add(1, {
            "error_type": error_type,
            "operation": operation,
            "service": self.service_name
        })
    
    def set_throughput(self, throughput: float):
        """Definir throughput atual"""
        self.throughput.set(throughput, {
            "service": self.service_name
        })
    
    # Métodos para sistema
    def set_cpu_usage(self, cpu_usage: float):
        """Definir uso de CPU"""
        self.cpu_usage.set(cpu_usage, {
            "service": self.service_name
        })
    
    def set_memory_usage(self, memory_usage: int):
        """Definir uso de memória"""
        self.memory_usage.set(memory_usage, {
            "service": self.service_name
        })
    
    def set_active_connections(self, connections: int):
        """Definir conexões ativas"""
        self.active_connections.set(connections, {
            "service": self.service_name
        })
    
    def record_restart(self):
        """Registrar reinicialização"""
        self.restarts_total.add(1, {
            "service": self.service_name
        })
    
    # Métodos para negócio
    def record_decision(self, decision_type: str, result: str):
        """Registrar decisão tomada"""
        self.decisions_total.add(1, {
            "decision_type": decision_type,
            "result": result,
            "service": self.service_name
        })
    
    def record_ml_prediction(self, prediction_type: str, confidence: float):
        """Registrar predição ML"""
        self.ml_predictions_total.add(1, {
            "prediction_type": prediction_type,
            "confidence": confidence,
            "service": self.service_name
        })
    
    def record_semantic_analysis(self, analysis_type: str, confidence: float):
        """Registrar análise semântica"""
        self.semantic_analyses_total.add(1, {
            "analysis_type": analysis_type,
            "confidence": confidence,
            "service": self.service_name
        })
    
    def record_blockchain_validation(self, validation_type: str, result: str):
        """Registrar validação blockchain"""
        self.blockchain_validations_total.add(1, {
            "validation_type": validation_type,
            "result": result,
            "service": self.service_name
        })

# Classes de métricas específicas
class Counter:
    """Wrapper para contador de métricas"""
    
    def __init__(self, name: str, description: str, unit: str = "1"):
        self.meter = metrics.get_meter(__name__)
        self.counter = self.meter.create_counter(
            name=name,
            description=description,
            unit=unit
        )
    
    def add(self, value: int, labels: Optional[Dict[str, str]] = None):
        """Adicionar valor ao contador"""
        self.counter.add(value, labels or {})

class Histogram:
    """Wrapper para histograma de métricas"""
    
    def __init__(self, name: str, description: str, unit: str = "1"):
        self.meter = metrics.get_meter(__name__)
        self.histogram = self.meter.create_histogram(
            name=name,
            description=description,
            unit=unit
        )
    
    def record(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Registrar valor no histograma"""
        self.histogram.record(value, labels or {})

class Gauge:
    """Wrapper para gauge de métricas"""
    
    def __init__(self, name: str, description: str, unit: str = "1"):
        self.meter = metrics.get_meter(__name__)
        self.gauge = self.meter.create_gauge(
            name=name,
            description=description,
            unit=unit
        )
    
    def set(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Definir valor do gauge"""
        self.gauge.set(value, labels or {})

# Função para criar métricas TriSLA
def create_trisla_metrics(service_name: str) -> TriSLAMetrics:
    """Criar instância de métricas TriSLA"""
    return TriSLAMetrics(service_name)




