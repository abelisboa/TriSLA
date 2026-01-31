"""
Tracing OpenTelemetry para SLA-Agent Layer
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/sla-agent-layer/src/observability/tracing.py
"""

from opentelemetry import trace
from observability.tracing_base import setup_tracer

_tracer = None

def init_tracer(service_name: str = "trisla-sla-agent", **kwargs):
    """Inicializa o tracer para SLA-Agent."""
    global _tracer
    _tracer = setup_tracer(service_name, **kwargs)
    return _tracer


def get_sla_tracer():
    """Obtém o tracer do SLA-Agent."""
    global _tracer
    if _tracer is None:
        _tracer = init_tracer()
    return _tracer


def create_sla_span(operation: str, contract_id=None, parent_context=None):
    """
    Cria um span para uma operação do SLA-Agent.
    
    Args:
        operation: Nome da operação ("compile_contract", "check_violation")
        contract_id: ID do contrato
        parent_context: Contexto pai
    """
    tracer = get_sla_tracer()
    span_name = f"sla.{operation}"
    
    kwargs = {}
    if parent_context:
        kwargs['context'] = parent_context
    
    span = tracer.start_as_current_span(span_name, **kwargs)
    
    if contract_id:
        span.set_attribute("trisla.contract.id", str(contract_id))
    
    return span


def set_sla_span_attributes(span, contract_id=None, contract_type=None, contract_version=None, **kwargs):
    """Define atributos comuns em spans do SLA-Agent."""
    if contract_id:
        span.set_attribute("trisla.contract.id", str(contract_id))
    if contract_type:
        span.set_attribute("trisla.contract.type", str(contract_type))
    if contract_version:
        span.set_attribute("trisla.contract.version", str(contract_version))
    
    for key, value in kwargs.items():
        span.set_attribute(f"trisla.{key}", str(value))


def trace_compile_contract(contract_id, compile_func, parent_context=None):
    """
    Helper para rastrear compilação de contrato SLA.
    
    Uso:
        result = trace_compile_contract("contract_123", lambda: compile(contract))
    """
    with create_sla_span("compile_contract", contract_id, parent_context) as span:
        set_sla_span_attributes(span, contract_id=contract_id, operation="compile")
        try:
            result = compile_func()
            
            if hasattr(result, 'version'):
                set_sla_span_attributes(span, contract_version=result.version)
            
            span.set_attribute("trisla.contract.compile.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.contract.compile.status", "error")
            raise


def trace_check_violation(contract_id, check_func, parent_context=None):
    """
    Helper para rastrear verificação de violação de SLA.
    
    Uso:
        result = trace_check_violation("contract_123", lambda: check_violations(contract))
    """
    with create_sla_span("check_violation", contract_id, parent_context) as span:
        set_sla_span_attributes(span, contract_id=contract_id, operation="violation_check")
        try:
            result = check_func()
            
            if isinstance(result, (list, tuple)) and len(result) > 0:
                span.set_attribute("trisla.violations.count", len(result))
                span.set_attribute("trisla.violations.detected", "true")
            else:
                span.set_attribute("trisla.violations.detected", "false")
            
            span.set_attribute("trisla.violation.check.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.violation.check.status", "error")
            raise














