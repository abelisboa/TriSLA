"""
Base de Tracing OpenTelemetry para Módulos Python
TriSLA v3.7.9

Este módulo fornece funções utilitárias para configuração de tracing OTEL.
Deve ser adaptado para cada módulo específico.

Uso:
  from observability.tracing import setup_tracer, get_tracer
  
  # Inicializar no startup da aplicação
  tracer = setup_tracer("trisla-sem-csmf")
  
  # Usar no código
  with tracer.start_as_current_span("sem.semantic_translation") as span:
      span.set_attribute("trisla.intent.id", intent.id)
      # ... lógica ...
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositeHTTPPropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.propagation.b3 import B3MultiFormat
import os
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Configuração de Tracing
# ============================================================

def setup_tracer(
    service_name: str,
    service_version: str = "3.7.9",
    environment: str = None,
    endpoint: str = None,
    insecure: bool = True
):
    """
    Configura e retorna um Tracer OpenTelemetry.
    
    Args:
        service_name: Nome do serviço (ex: "trisla-sem-csmf")
        service_version: Versão do serviço (padrão: "3.7.9")
        environment: Ambiente de deployment (padrão: TRISLA_ENV ou "nasp-lab")
        endpoint: Endpoint do OTEL Collector (padrão: variável de ambiente)
        insecure: Se True, usa conexão insegura (sem TLS)
    
    Returns:
        Tracer configurado
    """
    # Obter configurações de variáveis de ambiente
    endpoint = endpoint or os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://otel-collector.monitoring.svc.cluster.local:4317"
    )
    environment = environment or os.getenv("TRISLA_ENV", "nasp-lab")
    
    # Configurar sampling (10% em produção, 100% em desenvolvimento)
    sampling_rate = float(os.getenv("OTEL_TRACES_SAMPLER_ARG", "0.1"))
    
    # Criar Resource com atributos do serviço
    resource = Resource.create({
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": environment,
        "trisla.version": service_version,
        "trisla.module": service_name.replace("trisla-", "")
    })
    
    # Criar TracerProvider
    provider = TracerProvider(resource=resource)
    
    # Configurar exportador OTLP
    span_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=insecure
    )
    
    # Processador em batch para melhor performance
    span_processor = BatchSpanProcessor(span_exporter)
    provider.add_span_processor(span_processor)
    
    # Configurar provider global
    trace.set_tracer_provider(provider)
    
    # Configurar propagação de contexto (W3C TraceContext)
    propagator = CompositeHTTPPropagator([
        TraceContextTextMapPropagator(),
        B3MultiFormat()
    ])
    set_global_textmap(propagator)
    
    # Obter e retornar tracer
    tracer = trace.get_tracer(service_name, service_version)
    
    logger.info(f"Tracing OTEL configurado para {service_name} (endpoint: {endpoint})")
    
    return tracer


def get_tracer(service_name: str):
    """
    Obtém o tracer atual para um serviço.
    
    Args:
        service_name: Nome do serviço
    
    Returns:
        Tracer
    """
    return trace.get_tracer(service_name)


def create_span_context(carrier: dict):
    """
    Extrai contexto de tracing de um carrier (ex: headers HTTP/gRPC).
    
    Args:
        carrier: Dicionário com headers/metadata
    
    Returns:
        Contexto de tracing
    """
    from opentelemetry import propagate
    return propagate.extract(carrier)


def inject_span_context(carrier: dict, context: trace.SpanContext = None):
    """
    Injeta contexto de tracing em um carrier.
    
    Args:
        carrier: Dicionário para injetar headers
        context: Contexto de span (opcional, usa o atual se não fornecido)
    """
    from opentelemetry import propagate
    if context:
        propagate.inject(carrier, context=context)
    else:
        propagate.inject(carrier)


# ============================================================
# Decoradores Úteis
# ============================================================

def trace_function(span_name: str, tracer_name: str = None):
    """
    Decorador para rastrear automaticamente uma função.
    
    Uso:
        @trace_function("sem.translate_intent", "trisla-sem-csmf")
        def translate_intent(intent):
            # ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer(tracer_name or func.__module__)
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("function.name", func.__name__)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator














