"""
Métricas Prometheus para BC-NSSMF (Blockchain NSSMF)
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/bc-nssmf/src/observability/metrics.py

Uso:
  from observability.metrics import inc_bc_transaction, observe_commit_latency

  # Ao processar uma transação
  inc_bc_transaction(contract_type="slice_contract", status="committed")
  
  # Ao medir latência de commit
  start_time = time.time()
  block_hash = blockchain.commit(...)
  observe_commit_latency(start_time, time.time())
"""

from prometheus_client import Counter, Histogram, Gauge
import os

# ============================================================
# CONTADORES (Counters)
# ============================================================

# Total de transações blockchain processadas
bc_transactions_total = Counter(
    'trisla_bc_transactions_total',
    'Total de transações blockchain processadas',
    ['contract_type', 'status']  # contract_type: slice_contract, sla_contract, etc. | status: committed, failed
)

# Total de falhas de transação blockchain
bc_failures_total = Counter(
    'trisla_bc_failures_total',
    'Total de falhas de transação blockchain',
    ['error_type']  # error_type: contract_error, network_error, validation_error, etc.
)

# ============================================================
# HISTOGRAMAS (Histograms)
# ============================================================

# Latência de commit de bloco em milissegundos
bc_commit_latency_ms = Histogram(
    'trisla_bc_commit_latency_ms',
    'Latência de commit de bloco em milissegundos',
    buckets=[100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0, 10000.0, float('inf')]
)

# ============================================================
# GAUGES
# ============================================================

# Altura atual do bloco blockchain
bc_block_height = Gauge(
    'trisla_bc_block_height',
    'Altura atual do bloco blockchain'
)

# Número de transações pendentes
bc_pending_transactions = Gauge(
    'trisla_bc_pending_transactions',
    'Número de transações pendentes na blockchain'
)

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def inc_bc_transaction(contract_type='unknown', status='committed'):
    """
    Incrementa o contador de transações blockchain.
    
    Args:
        contract_type: Tipo de contrato (slice_contract, sla_contract, etc.)
        status: 'committed' ou 'failed'
    """
    bc_transactions_total.labels(contract_type=contract_type, status=status).inc()


def inc_bc_failure(error_type='unknown'):
    """
    Incrementa o contador de falhas blockchain.
    
    Args:
        error_type: Tipo de erro (contract_error, network_error, validation_error, etc.)
    """
    bc_failures_total.labels(error_type=error_type).inc()


def observe_commit_latency(start_time, end_time):
    """
    Observa a latência de commit de bloco.
    
    Args:
        start_time: Timestamp inicial do commit
        end_time: Timestamp final do commit
    """
    elapsed_ms = (end_time - start_time) * 1000.0
    bc_commit_latency_ms.observe(elapsed_ms)


def set_block_height(height):
    """
    Define a altura atual do bloco.
    
    Args:
        height: Altura do bloco (número inteiro)
    """
    bc_block_height.set(height)


def set_pending_transactions(count):
    """
    Define o número de transações pendentes.
    
    Args:
        count: Número de transações pendentes
    """
    bc_pending_transactions.set(count)


def inc_pending_transactions():
    """Incrementa o número de transações pendentes."""
    bc_pending_transactions.inc()


def dec_pending_transactions():
    """Decrementa o número de transações pendentes."""
    bc_pending_transactions.dec()














