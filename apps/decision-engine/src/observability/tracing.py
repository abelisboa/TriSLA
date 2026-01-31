"""
Tracing OpenTelemetry para Decision Engine
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/decision-engine/src/observability/tracing.py
"""

from opentelemetry import trace
from observability.tracing_base import setup_tracer

_tracer = None

def init_tracer(service_name: str = "trisla-decision-engine", **kwargs):
    """Inicializa o tracer para Decision Engine."""
    global _tracer
    _tracer = setup_tracer(service_name, **kwargs)
    return _tracer


def get_decision_tracer():
    """Obtém o tracer do Decision Engine."""
    global _tracer
    if _tracer is None:
        _tracer = init_tracer()
    return _tracer


def create_decision_span(operation: str, intent=None, parent_context=None):
    """
    Cria um span para uma operação do Decision Engine.
    
    Args:
        operation: Nome da operação ("pipeline", "sla_validation")
        intent: Objeto intent
        parent_context: Contexto pai
    """
    tracer = get_decision_tracer()
    span_name = f"decision.{operation}"
    
    kwargs = {}
    if parent_context:
        kwargs['context'] = parent_context
    
    span = tracer.start_as_current_span(span_name, **kwargs)
    
    if intent:
        if hasattr(intent, 'id'):
            span.set_attribute("trisla.intent.id", str(intent.id))
    
    return span


def set_decision_span_attributes(span, intent=None, status=None, reason=None, **kwargs):
    """Define atributos comuns em spans do Decision Engine."""
    if intent:
        if hasattr(intent, 'id'):
            span.set_attribute("trisla.intent.id", str(intent.id))
        if hasattr(intent, 'type'):
            span.set_attribute("trisla.intent.type", str(intent.type))
    
    if status:
        span.set_attribute("trisla.decision.status", str(status))
    if reason:
        span.set_attribute("trisla.decision.reason", str(reason))
    
    for key, value in kwargs.items():
        span.set_attribute(f"trisla.{key}", str(value))


def trace_pipeline(intent, pipeline_func, parent_context=None):
    """
    Helper para rastrear pipeline completo de decisão.
    
    Uso:
        result = trace_pipeline(intent, lambda: execute_pipeline(intent))
    """
    with create_decision_span("pipeline", intent, parent_context) as span:
        set_decision_span_attributes(span, intent, operation="pipeline")
        try:
            result = pipeline_func()
            
            # Adicionar status do resultado
            if hasattr(result, 'status'):
                set_decision_span_attributes(span, status=result.status, reason=result.reason)
            
            span.set_attribute("trisla.pipeline.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.pipeline.status", "error")
            raise


def trace_sla_validation(intent, validation_func, parent_context=None):
    """
    Helper para rastrear validação de SLA.
    
    Uso:
        result = trace_sla_validation(intent, lambda: validate_sla(intent))
    """
    with create_decision_span("sla_validation", intent, parent_context) as span:
        set_decision_span_attributes(span, intent, operation="sla_validation")
        try:
            result = validation_func()
            
            span.set_attribute("trisla.sla.validation.result", str(result))
            span.set_attribute("trisla.sla.validation.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.sla.validation.status", "error")
            raise














