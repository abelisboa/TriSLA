"""
Tracing OpenTelemetry para BC-NSSMF
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/bc-nssmf/src/observability/tracing.py
"""

from opentelemetry import trace
from observability.tracing_base import setup_tracer

_tracer = None

def init_tracer(service_name: str = "trisla-bc-nssmf", **kwargs):
    """Inicializa o tracer para BC-NSSMF."""
    global _tracer
    _tracer = setup_tracer(service_name, **kwargs)
    return _tracer


def get_bc_tracer():
    """Obtém o tracer do BC-NSSMF."""
    global _tracer
    if _tracer is None:
        _tracer = init_tracer()
    return _tracer


def create_bc_span(operation: str, contract_type=None, parent_context=None):
    """
    Cria um span para uma operação do BC-NSSMF.
    
    Args:
        operation: Nome da operação ("smart_contract_execution", "block_commit")
        contract_type: Tipo de contrato
        parent_context: Contexto pai
    """
    tracer = get_bc_tracer()
    span_name = f"bc.{operation}"
    
    kwargs = {}
    if parent_context:
        kwargs['context'] = parent_context
    
    span = tracer.start_as_current_span(span_name, **kwargs)
    
    if contract_type:
        span.set_attribute("trisla.contract.type", str(contract_type))
    
    return span


def set_bc_span_attributes(span, contract_type=None, transaction_hash=None, block_number=None, **kwargs):
    """Define atributos comuns em spans do BC-NSSMF."""
    if contract_type:
        span.set_attribute("trisla.contract.type", str(contract_type))
    if transaction_hash:
        span.set_attribute("trisla.transaction.hash", str(transaction_hash))
    if block_number:
        span.set_attribute("trisla.bc.block_number", int(block_number))
    
    for key, value in kwargs.items():
        span.set_attribute(f"trisla.{key}", str(value))


def trace_smart_contract_execution(contract_type, execution_func, parent_context=None):
    """
    Helper para rastrear execução de smart contract.
    
    Uso:
        result = trace_smart_contract_execution("slice_contract", lambda: execute_contract(...))
    """
    with create_bc_span("smart_contract_execution", contract_type, parent_context) as span:
        set_bc_span_attributes(span, contract_type=contract_type, operation="contract_execution")
        try:
            result = execution_func()
            
            if hasattr(result, 'transaction_hash'):
                set_bc_span_attributes(span, transaction_hash=result.transaction_hash)
            
            span.set_attribute("trisla.contract.execution.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.contract.execution.status", "error")
            raise


def trace_block_commit(commit_func, parent_context=None):
    """
    Helper para rastrear commit de bloco.
    
    Uso:
        result = trace_block_commit(lambda: blockchain.commit(...))
    """
    with create_bc_span("block_commit", parent_context=parent_context) as span:
        set_bc_span_attributes(span, operation="block_commit")
        try:
            result = commit_func()
            
            if hasattr(result, 'block_number'):
                set_bc_span_attributes(span, block_number=result.block_number)
            if hasattr(result, 'block_hash'):
                span.set_attribute("trisla.bc.block_hash", str(result.block_hash))
            
            span.set_attribute("trisla.block.commit.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.block.commit.status", "error")
            raise














