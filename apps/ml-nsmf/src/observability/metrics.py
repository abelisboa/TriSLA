"""
Métricas Prometheus para ML-NSMF (Machine Learning NSMF)
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/ml-nsmf/src/observability/metrics.py

Uso:
  from observability.metrics import inc_ml_request, observe_decision_latency, set_confidence_score

  # Ao processar uma predição
  inc_ml_request(slice_type="eMBB", status="success")
  
  # Ao medir latência
  start_time = time.time()
  prediction = model.predict(...)
  observe_decision_latency(slice_type="eMBB", start_time, time.time())
  set_confidence_score("eMBB", prediction.confidence)
"""

from prometheus_client import Counter, Histogram, Gauge
import os

# ============================================================
# CONTADORES (Counters)
# ============================================================

# Total de requisições de predição ML
ml_requests_total = Counter(
    'trisla_ml_requests_total',
    'Total de requisições de predição ML processadas',
    ['slice_type', 'status']  # slice_type: eMBB, URLLC, mIoT, etc. | status: success, error
)

# Total de erros de predição ML
ml_errors_total = Counter(
    'trisla_ml_errors_total',
    'Total de erros de predição ML',
    ['slice_type', 'error_type']  # error_type: model_error, timeout, invalid_input, etc.
)

# ============================================================
# HISTOGRAMAS (Histograms)
# ============================================================

# Latência de decisão ML em milissegundos
ml_decision_latency_ms = Histogram(
    'trisla_ml_decision_latency_ms',
    'Latência de decisão ML em milissegundos',
    ['slice_type'],
    buckets=[50.0, 100.0, 200.0, 400.0, 800.0, 1600.0, 3000.0, float('inf')]
)

# ============================================================
# GAUGES
# ============================================================

# Confidence score médio das predições
ml_confidence_score = Gauge(
    'trisla_ml_confidence_score',
    'Confidence score médio das predições ML',
    ['slice_type']
)

# Versão do modelo ML em uso
ml_model_version = Gauge(
    'trisla_ml_model_version',
    'Versão do modelo ML em uso',
    ['version']
)

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def inc_ml_request(slice_type='unknown', status='success'):
    """
    Incrementa o contador de requisições ML.
    
    Args:
        slice_type: Tipo de slice (eMBB, URLLC, mIoT, etc.)
        status: 'success' ou 'error'
    """
    ml_requests_total.labels(slice_type=slice_type, status=status).inc()


def inc_ml_error(slice_type='unknown', error_type='unknown'):
    """
    Incrementa o contador de erros ML.
    
    Args:
        slice_type: Tipo de slice
        error_type: Tipo de erro (model_error, timeout, invalid_input, etc.)
    """
    ml_errors_total.labels(slice_type=slice_type, error_type=error_type).inc()


def observe_decision_latency(slice_type, start_time, end_time):
    """
    Observa a latência de decisão ML.
    
    Args:
        slice_type: Tipo de slice
        start_time: Timestamp inicial
        end_time: Timestamp final
    """
    elapsed_ms = (end_time - start_time) * 1000.0
    ml_decision_latency_ms.labels(slice_type=slice_type).observe(elapsed_ms)


def set_confidence_score(slice_type, score):
    """
    Define o confidence score para um tipo de slice.
    
    Args:
        slice_type: Tipo de slice
        score: Confidence score (0.0 a 1.0)
    """
    ml_confidence_score.labels(slice_type=slice_type).set(score)


def set_model_version(version):
    """
    Define a versão do modelo ML.
    
    Args:
        version: Versão do modelo (ex: "1.0.0", "v2.1")
    """
    # Limpa versões anteriores (opcional, pode manter histórico)
    ml_model_version.labels(version=version).set(1)














