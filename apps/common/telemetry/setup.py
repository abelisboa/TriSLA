#!/usr/bin/env python3
"""
TriSLA Common Telemetry Setup
Configuração centralizada do OpenTelemetry para todos os módulos
"""

import logging
import os
from typing import Optional
from opentelemetry import trace, metrics, logs
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.kafka import KafkaInstrumentor

# Configurar logging
logger = logging.getLogger(__name__)

# Variáveis globais para providers
_tracer_provider: Optional[TracerProvider] = None
_meter_provider: Optional[MeterProvider] = None
_logger_provider: Optional[LoggerProvider] = None

def setup_telemetry(
    service_name: str,
    service_version: str = "1.0.0",
    otel_endpoint: str = "http://otel-collector:4317",
    environment: str = "production",
    enable_auto_instrumentation: bool = True
) -> None:
    """
    Configurar OpenTelemetry para o serviço
    
    Args:
        service_name: Nome do serviço
        service_version: Versão do serviço
        otel_endpoint: Endpoint do OpenTelemetry Collector
        environment: Ambiente (development, staging, production)
        enable_auto_instrumentation: Habilitar instrumentação automática
    """
    try:
        logger.info(f"Configurando OpenTelemetry para {service_name}")
        
        # Configurar resource
        resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            "service.namespace": "trisla",
            "deployment.environment": environment,
            "cluster.name": "trisla-cluster"
        })
        
        # Configurar traces
        _setup_traces(resource, otel_endpoint)
        
        # Configurar métricas
        _setup_metrics(resource, otel_endpoint)
        
        # Configurar logs
        _setup_logs(resource, otel_endpoint)
        
        # Configurar instrumentação automática
        if enable_auto_instrumentation:
            _setup_auto_instrumentation()
        
        logger.info(f"OpenTelemetry configurado com sucesso para {service_name}")
        
    except Exception as e:
        logger.error(f"Erro ao configurar OpenTelemetry: {str(e)}")
        raise

def _setup_traces(resource: Resource, otel_endpoint: str) -> None:
    """Configurar traces"""
    global _tracer_provider
    
    try:
        # Criar tracer provider
        _tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(_tracer_provider)
        
        # Configurar exportador OTLP
        otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint)
        span_processor = BatchSpanProcessor(otlp_exporter)
        _tracer_provider.add_span_processor(span_processor)
        
        logger.info("Traces configurados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao configurar traces: {str(e)}")
        raise

def _setup_metrics(resource: Resource, otel_endpoint: str) -> None:
    """Configurar métricas"""
    global _meter_provider
    
    try:
        # Configurar exportador OTLP para métricas
        otlp_metric_exporter = OTLPMetricExporter(endpoint=otel_endpoint)
        metric_reader = PeriodicExportingMetricReader(
            exporter=otlp_metric_exporter,
            export_interval_millis=30000  # 30 segundos
        )
        
        # Criar meter provider
        _meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(_meter_provider)
        
        logger.info("Métricas configuradas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao configurar métricas: {str(e)}")
        raise

def _setup_logs(resource: Resource, otel_endpoint: str) -> None:
    """Configurar logs"""
    global _logger_provider
    
    try:
        # Configurar exportador OTLP para logs
        otlp_log_exporter = OTLPLogExporter(endpoint=otel_endpoint)
        log_processor = BatchLogRecordProcessor(otlp_log_exporter)
        
        # Criar logger provider
        _logger_provider = LoggerProvider(
            resource=resource,
            processors=[log_processor]
        )
        logs.set_logger_provider(_logger_provider)
        
        # Configurar handler para logs
        handler = LoggingHandler(logger_provider=_logger_provider)
        logging.getLogger().addHandler(handler)
        
        logger.info("Logs configurados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao configurar logs: {str(e)}")
        raise

def _setup_auto_instrumentation() -> None:
    """Configurar instrumentação automática"""
    try:
        # Instrumentar FastAPI
        FastAPIInstrumentor.instrument()
        
        # Instrumentar HTTPX
        HTTPXClientInstrumentor().instrument()
        
        # Instrumentar Redis
        RedisInstrumentor().instrument()
        
        # Instrumentar Kafka
        KafkaInstrumentor().instrument()
        
        logger.info("Instrumentação automática configurada")
        
    except Exception as e:
        logger.error(f"Erro ao configurar instrumentação automática: {str(e)}")
        raise

def get_tracer(name: str) -> trace.Tracer:
    """Obter tracer para o módulo"""
    if _tracer_provider is None:
        raise RuntimeError("OpenTelemetry não foi configurado. Chame setup_telemetry() primeiro.")
    
    return trace.get_tracer(name)

def get_meter(name: str) -> metrics.Meter:
    """Obter meter para o módulo"""
    if _meter_provider is None:
        raise RuntimeError("OpenTelemetry não foi configurado. Chame setup_telemetry() primeiro.")
    
    return metrics.get_meter(name)

def get_logger(name: str) -> logging.Logger:
    """Obter logger para o módulo"""
    if _logger_provider is None:
        raise RuntimeError("OpenTelemetry não foi configurado. Chame setup_telemetry() primeiro.")
    
    return logs.get_logger(name)

def shutdown_telemetry() -> None:
    """Encerrar telemetria"""
    global _tracer_provider, _meter_provider, _logger_provider
    
    try:
        if _tracer_provider:
            _tracer_provider.shutdown()
            _tracer_provider = None
        
        if _meter_provider:
            _meter_provider.shutdown()
            _meter_provider = None
        
        if _logger_provider:
            _logger_provider.shutdown()
            _logger_provider = None
        
        logger.info("Telemetria encerrada")
        
    except Exception as e:
        logger.error(f"Erro ao encerrar telemetria: {str(e)}")

# Configuração automática baseada em variáveis de ambiente
def auto_setup_telemetry() -> None:
    """Configuração automática baseada em variáveis de ambiente"""
    service_name = os.getenv("SERVICE_NAME", "trisla-service")
    service_version = os.getenv("SERVICE_VERSION", "1.0.0")
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    environment = os.getenv("ENVIRONMENT", "production")
    
    setup_telemetry(
        service_name=service_name,
        service_version=service_version,
        otel_endpoint=otel_endpoint,
        environment=environment
    )




