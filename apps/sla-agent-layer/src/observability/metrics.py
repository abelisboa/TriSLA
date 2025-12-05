"""
Métricas Prometheus para SLA-Agent Layer
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/sla-agent-layer/src/observability/metrics.py

Uso:
  from observability.metrics import inc_sla_request, observe_compile_latency, inc_violation

  # Ao compilar um contrato
  inc_sla_request(contract_type="slice_sla", status="success")
  
  # Ao medir latência de compilação
  start_time = time.time()
  contract = compile_contract(...)
  observe_compile_latency(start_time, time.time())
  
  # Ao detectar violação
  inc_violation(severity="critical", contract_id="contract_123")
"""

from prometheus_client import Counter, Histogram, Gauge
import os

# ============================================================
# CONTADORES (Counters)
# ============================================================

# Total de requisições de compilação de contrato SLA
sla_requests_total = Counter(
    'trisla_sla_requests_total',
    'Total de requisições de compilação de contrato SLA',
    ['contract_type', 'status']  # contract_type: slice_sla, network_sla, etc. | status: success, error
)

# Total de violações de SLA detectadas
sla_violations_total = Counter(
    'trisla_sla_violations_total',
    'Total de violações de SLA detectadas',
    ['severity', 'contract_id']  # severity: critical, warning | contract_id: identificador do contrato
)

# ============================================================
# HISTOGRAMAS (Histograms)
# ============================================================

# Latência de compilação de contrato em milissegundos
sla_compile_latency_ms = Histogram(
    'trisla_sla_compile_latency_ms',
    'Latência de compilação de contrato SLA em milissegundos',
    buckets=[50.0, 100.0, 150.0, 200.0, 500.0, 1000.0, float('inf')]
)

# ============================================================
# GAUGES
# ============================================================

# Número de contratos SLA ativos
sla_active_contracts = Gauge(
    'trisla_sla_active_contracts',
    'Número de contratos SLA atualmente ativos'
)

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def inc_sla_request(contract_type='unknown', status='success'):
    """
    Incrementa o contador de requisições de compilação SLA.
    
    Args:
        contract_type: Tipo de contrato (slice_sla, network_sla, etc.)
        status: 'success' ou 'error'
    """
    sla_requests_total.labels(contract_type=contract_type, status=status).inc()


def inc_violation(severity='warning', contract_id='unknown'):
    """
    Incrementa o contador de violações de SLA.
    
    Args:
        severity: 'critical' ou 'warning'
        contract_id: Identificador do contrato
    """
    sla_violations_total.labels(severity=severity, contract_id=contract_id).inc()


def observe_compile_latency(start_time, end_time):
    """
    Observa a latência de compilação de contrato.
    
    Args:
        start_time: Timestamp inicial da compilação
        end_time: Timestamp final da compilação
    """
    elapsed_ms = (end_time - start_time) * 1000.0
    sla_compile_latency_ms.observe(elapsed_ms)


def set_active_contracts(count):
    """
    Define o número de contratos SLA ativos.
    
    Args:
        count: Número de contratos ativos
    """
    sla_active_contracts.set(count)


def inc_active_contracts():
    """Incrementa o número de contratos ativos."""
    sla_active_contracts.inc()


def dec_active_contracts():
    """Decrementa o número de contratos ativos."""
    sla_active_contracts.dec()

