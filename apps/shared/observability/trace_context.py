"""
Context Propagation - TriSLA
Propagação de contexto para traces distribuídos
"""

from opentelemetry import trace
from opentelemetry.propagate import extract, inject
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace import Span, Status, StatusCode
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Usar TraceContextTextMapPropagator para propagação de contexto
propagator = TraceContextTextMapPropagator()


def inject_trace_context(carrier: Dict[str, Any]) -> Dict[str, Any]:
    """
    Injeta contexto de trace no carrier (headers, metadata, etc.)
    
    Args:
        carrier: Dicionário para injetar contexto (ex: headers HTTP, metadata gRPC)
    
    Returns:
        Carrier com contexto injetado
    """
    inject(carrier, context=trace.context_api.get_current())
    return carrier


def extract_trace_context(carrier: Dict[str, Any]) -> trace.context_api.Context:
    """
    Extrai contexto de trace do carrier
    
    Args:
        carrier: Dicionário com contexto (ex: headers HTTP, metadata gRPC)
    
    Returns:
        Contexto de trace extraído
    """
    return extract(carrier)


def get_trace_id() -> Optional[str]:
    """
    Obtém o trace ID atual
    
    Returns:
        Trace ID como string ou None se não houver span ativo
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return None


def get_span_id() -> Optional[str]:
    """
    Obtém o span ID atual
    
    Returns:
        Span ID como string ou None se não houver span ativo
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, '016x')
    return None


def create_span_from_context(
    name: str,
    carrier: Dict[str, Any],
    kind: trace.SpanKind = trace.SpanKind.SERVER
) -> Span:
    """
    Cria span a partir de contexto extraído
    
    Args:
        name: Nome do span
        carrier: Dicionário com contexto
        kind: Tipo do span (SERVER, CLIENT, etc.)
    
    Returns:
        Span criado
    """
    tracer = trace.get_tracer(__name__)
    context = extract_trace_context(carrier)
    
    with trace.context_api.use_context(context):
        span = tracer.start_span(name, kind=kind)
        return span


def add_interface_attributes(span: Span, interface: str, **kwargs):
    """
    Adiciona atributos relacionados a interface ao span
    
    Args:
        span: Span para adicionar atributos
        interface: Nome da interface (I-01, I-02, etc.)
        **kwargs: Atributos adicionais
    """
    span.set_attribute("interface", interface)
    span.set_attribute("service.name", "trisla")
    
    for key, value in kwargs.items():
        span.set_attribute(key, value)


def set_span_status(span: Span, success: bool, error: Optional[Exception] = None):
    """
    Define status do span
    
    Args:
        span: Span para definir status
        success: Se a operação foi bem-sucedida
        error: Exceção (se houver)
    """
    if success:
        span.set_status(Status(StatusCode.OK))
    else:
        if error:
            span.record_exception(error)
        span.set_status(Status(StatusCode.ERROR, str(error) if error else "Operation failed"))


def create_distributed_trace(
    name: str,
    interface: str,
    carrier: Optional[Dict[str, Any]] = None,
    **attributes
) -> Span:
    """
    Cria trace distribuído com propagação de contexto
    
    Args:
        name: Nome do span
        interface: Nome da interface (I-01, I-02, etc.)
        carrier: Carrier com contexto (opcional)
        **attributes: Atributos adicionais
    
    Returns:
        Span criado
    """
    tracer = trace.get_tracer(__name__)
    
    if carrier:
        # Extrair contexto do carrier
        context = extract_trace_context(carrier)
        with trace.context_api.use_context(context):
            span = tracer.start_span(name, kind=trace.SpanKind.SERVER)
    else:
        # Criar novo span
        span = tracer.start_span(name, kind=trace.SpanKind.SERVER)
    
    # Adicionar atributos
    add_interface_attributes(span, interface, **attributes)
    
    return span






