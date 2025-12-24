"""
Métricas Prometheus para SEM-CSMF (Semantic CSMF)
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/sem-csmf/src/observability/metrics.py
  ou
  src/observability/metrics.py (dependendo da estrutura do projeto)

Uso:
  from observability.metrics import inc_sem_intents, observe_translation_latency

  # Ao processar um intent
  inc_sem_intents(status="success")
  
  # Ao medir latência
  start_time = time.time()
  # ... código de tradução ...
  observe_translation_latency(start_time, time.time())
"""

from prometheus_client import Counter, Histogram, Gauge
import os

# ============================================================
# CONTADORES (Counters)
# ============================================================

# Total de intents processadas pelo SEM-CSMF
sem_intents_total = Counter(
    'trisla_sem_intents_total',
    'Total de intents processadas pelo SEM-CSMF',
    ['status']  # status: success, error, invalid
)

# Total de intents inválidas rejeitadas
sem_invalid_intents_total = Counter(
    'trisla_sem_invalid_intents_total',
    'Total de intents inválidas rejeitadas pelo SEM-CSMF',
    ['reason']  # reason: malformed, unsupported, ontology_error, etc.
)

# ============================================================
# HISTOGRAMAS (Histograms)
# ============================================================

# Latência da tradução semântica em milissegundos
sem_translation_latency_ms = Histogram(
    'trisla_sem_translation_latency_ms',
    'Latência da tradução semântica em milissegundos',
    buckets=[10.0, 30.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, float('inf')]
)

# Latência do raciocínio ontológico em milissegundos
sem_ontology_reasoning_latency_ms = Histogram(
    'trisla_sem_ontology_reasoning_latency_ms',
    'Latência do raciocínio ontológico em milissegundos',
    buckets=[10.0, 30.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, float('inf')]
)

# ============================================================
# GAUGES (Opcional)
# ============================================================

# Número de intents em processamento
sem_intents_in_flight = Gauge(
    'trisla_sem_intents_in_flight',
    'Número de intents atualmente em processamento'
)

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def inc_sem_intents(status='success'):
    """
    Incrementa o contador de intents processadas.
    
    Args:
        status: 'success', 'error', ou 'invalid'
    """
    sem_intents_total.labels(status=status).inc()


def inc_invalid_intent(reason='unknown'):
    """
    Incrementa o contador de intents inválidas.
    
    Args:
        reason: Razão da invalidação (malformed, unsupported, ontology_error, etc.)
    """
    sem_invalid_intents_total.labels(reason=reason).inc()


def observe_translation_latency(start_time, end_time):
    """
    Observa a latência da tradução semântica.
    
    Args:
        start_time: Timestamp inicial (time.time() ou time.perf_counter())
        end_time: Timestamp final (time.time() ou time.perf_counter())
    """
    elapsed_ms = (end_time - start_time) * 1000.0
    sem_translation_latency_ms.observe(elapsed_ms)


def observe_ontology_reasoning_latency(start_time, end_time):
    """
    Observa a latência do raciocínio ontológico.
    
    Args:
        start_time: Timestamp inicial
        end_time: Timestamp final
    """
    elapsed_ms = (end_time - start_time) * 1000.0
    sem_ontology_reasoning_latency_ms.observe(elapsed_ms)


def set_intents_in_flight(value):
    """
    Define o número de intents em processamento.
    
    Args:
        value: Número de intents em processamento
    """
    sem_intents_in_flight.set(value)


def inc_intents_in_flight():
    """Incrementa o número de intents em processamento."""
    sem_intents_in_flight.inc()


def dec_intents_in_flight():
    """Decrementa o número de intents em processamento."""
    sem_intents_in_flight.dec()














