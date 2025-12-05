"""
Tracing OpenTelemetry para SEM-CSMF
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/sem-csmf/src/observability/tracing.py

Uso:
  from observability.tracing import setup_tracer, create_sem_span
  
  # No startup
  tracer = setup_tracer("trisla-sem-csmf")
  
  # Ao processar intent
  with create_sem_span("semantic_translation", intent) as span:
      # ... lógica de tradução ...
"""

from opentelemetry import trace
from observability.tracing_base import setup_tracer, get_tracer
import contextvars

# Tracer global para o módulo
_tracer = None

def init_tracer(service_name: str = "trisla-sem-csmf", **kwargs):
    """
    Inicializa o tracer para SEM-CSMF.
    Deve ser chamado no startup da aplicação.
    """
    global _tracer
    _tracer = setup_tracer(service_name, **kwargs)
    return _tracer


def get_sem_tracer():
    """Obtém o tracer do SEM-CSMF."""
    global _tracer
    if _tracer is None:
        _tracer = init_tracer()
    return _tracer


def create_sem_span(operation: str, intent=None, parent_context=None):
    """
    Cria um span para uma operação do SEM-CSMF.
    
    Args:
        operation: Nome da operação ("semantic_translation", "ontology_reasoning")
        intent: Objeto intent (opcional, para adicionar atributos)
        parent_context: Contexto pai (para propagação)
    
    Returns:
        Context manager para o span
    """
    tracer = get_sem_tracer()
    span_name = f"sem.{operation}"
    
    if parent_context:
        return tracer.start_as_current_span(span_name, context=parent_context)
    else:
        return tracer.start_as_current_span(span_name)


def set_sem_span_attributes(span, intent=None, **kwargs):
    """
    Define atributos comuns em spans do SEM-CSMF.
    
    Args:
        span: Span OpenTelemetry
        intent: Objeto intent
        **kwargs: Atributos adicionais
    """
    if intent:
        if hasattr(intent, 'id'):
            span.set_attribute("trisla.intent.id", str(intent.id))
        if hasattr(intent, 'type'):
            span.set_attribute("trisla.intent.type", str(intent.type))
        if hasattr(intent, 'status'):
            span.set_attribute("trisla.intent.status", str(intent.status))
    
    # Atributos adicionais
    for key, value in kwargs.items():
        span.set_attribute(f"trisla.{key}", str(value))


# ============================================================
# Helpers para Operações Específicas
# ============================================================

def trace_semantic_translation(intent, translation_func):
    """
    Helper para rastrear tradução semântica.
    
    Uso:
        result = trace_semantic_translation(intent, lambda: translate(intent))
    """
    with create_sem_span("semantic_translation", intent) as span:
        set_sem_span_attributes(span, intent, operation="translation")
        try:
            result = translation_func()
            span.set_attribute("trisla.translation.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.translation.status", "error")
            raise


def trace_ontology_reasoning(intent, reasoning_func):
    """
    Helper para rastrear raciocínio ontológico.
    
    Uso:
        result = trace_ontology_reasoning(intent, lambda: reason(intent))
    """
    with create_sem_span("ontology_reasoning", intent) as span:
        set_sem_span_attributes(span, intent, operation="reasoning")
        try:
            result = reasoning_func()
            span.set_attribute("trisla.reasoning.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.reasoning.status", "error")
            raise

