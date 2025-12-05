"""
Métricas Prometheus para Decision Engine
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/decision-engine/src/observability/metrics.py

Uso:
  from observability.metrics import inc_decision_intent, observe_pipeline_latency

  # Ao processar um intent
  inc_decision_intent(status="accepted", reason="sla_valid")
  
  # Ao medir latência do pipeline
  start_time = time.time()
  # ... pipeline completo ...
  observe_pipeline_latency(start_time, time.time())
"""

from prometheus_client import Counter, Histogram, Gauge
import os

# ============================================================
# CONTADORES (Counters)
# ============================================================

# Total de intents processadas pelo Decision Engine
decision_intents_total = Counter(
    'trisla_decision_intents_total',
    'Total de intents processadas pelo Decision Engine',
    ['status']  # status: accepted, rejected, error
)

# Total de intents aceitas
decision_accepted_total = Counter(
    'trisla_decision_accepted_total',
    'Total de intents aceitas pelo Decision Engine',
    ['reason']  # reason: sla_valid, capacity_available, etc.
)

# Total de intents rejeitadas
decision_rejected_total = Counter(
    'trisla_decision_rejected_total',
    'Total de intents rejeitadas pelo Decision Engine',
    ['reason']  # reason: sla_invalid, capacity_exceeded, timeout, etc.
)

# ============================================================
# HISTOGRAMAS (Histograms)
# ============================================================

# Latência total do pipeline de decisão em milissegundos
decision_pipeline_ms = Histogram(
    'trisla_decision_pipeline_ms',
    'Latência total do pipeline de decisão em milissegundos',
    buckets=[100.0, 200.0, 300.0, 500.0, 1000.0, 2000.0, 5000.0, float('inf')]
)

# Latência de validação de SLA em milissegundos
decision_sla_validation_latency_ms = Histogram(
    'trisla_decision_sla_validation_latency_ms',
    'Latência de validação de SLA em milissegundos',
    buckets=[50.0, 100.0, 200.0, 500.0, 1000.0, float('inf')]
)

# ============================================================
# GAUGES
# ============================================================

# Número de intents em processamento no pipeline
decision_pipeline_in_flight = Gauge(
    'trisla_decision_pipeline_in_flight',
    'Número de intents atualmente em processamento no pipeline'
)

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def inc_decision_intent(status='accepted'):
    """
    Incrementa o contador de intents processadas.
    
    Args:
        status: 'accepted', 'rejected', ou 'error'
    """
    decision_intents_total.labels(status=status).inc()


def inc_decision_accepted(reason='sla_valid'):
    """
    Incrementa o contador de intents aceitas.
    
    Args:
        reason: Razão da aceitação (sla_valid, capacity_available, etc.)
    """
    decision_accepted_total.labels(reason=reason).inc()
    inc_decision_intent(status='accepted')


def inc_decision_rejected(reason='unknown'):
    """
    Incrementa o contador de intents rejeitadas.
    
    Args:
        reason: Razão da rejeição (sla_invalid, capacity_exceeded, timeout, etc.)
    """
    decision_rejected_total.labels(reason=reason).inc()
    inc_decision_intent(status='rejected')


def observe_pipeline_latency(start_time, end_time):
    """
    Observa a latência total do pipeline de decisão.
    
    Args:
        start_time: Timestamp inicial do pipeline
        end_time: Timestamp final do pipeline
    """
    elapsed_ms = (end_time - start_time) * 1000.0
    decision_pipeline_ms.observe(elapsed_ms)


def observe_sla_validation_latency(start_time, end_time):
    """
    Observa a latência de validação de SLA.
    
    Args:
        start_time: Timestamp inicial da validação
        end_time: Timestamp final da validação
    """
    elapsed_ms = (end_time - start_time) * 1000.0
    decision_sla_validation_latency_ms.observe(elapsed_ms)


def set_pipeline_in_flight(value):
    """Define o número de intents em processamento no pipeline."""
    decision_pipeline_in_flight.set(value)


def inc_pipeline_in_flight():
    """Incrementa o número de intents em processamento."""
    decision_pipeline_in_flight.inc()


def dec_pipeline_in_flight():
    """Decrementa o número de intents em processamento."""
    decision_pipeline_in_flight.dec()

