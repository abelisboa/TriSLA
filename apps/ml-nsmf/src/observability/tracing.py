"""
Tracing OpenTelemetry para ML-NSMF
TriSLA v3.7.9

Este módulo deve ser integrado em:
  apps/ml-nsmf/src/observability/tracing.py
"""

from opentelemetry import trace
from observability.tracing_base import setup_tracer
import contextvars

_tracer = None

def init_tracer(service_name: str = "trisla-ml-nsmf", **kwargs):
    """Inicializa o tracer para ML-NSMF."""
    global _tracer
    _tracer = setup_tracer(service_name, **kwargs)
    return _tracer


def get_ml_tracer():
    """Obtém o tracer do ML-NSMF."""
    global _tracer
    if _tracer is None:
        _tracer = init_tracer()
    return _tracer


def create_ml_span(operation: str, slice_type=None, parent_context=None):
    """
    Cria um span para uma operação do ML-NSMF.
    
    Args:
        operation: Nome da operação ("predict_slice", "evaluation_loop")
        slice_type: Tipo de slice (eMBB, URLLC, etc.)
        parent_context: Contexto pai
    """
    tracer = get_ml_tracer()
    span_name = f"ml.{operation}"
    
    kwargs = {}
    if parent_context:
        kwargs['context'] = parent_context
    
    span = tracer.start_as_current_span(span_name, **kwargs)
    
    if slice_type:
        span.set_attribute("trisla.slice.type", slice_type)
    
    return span


def set_ml_span_attributes(span, slice_type=None, confidence=None, model_version=None, **kwargs):
    """Define atributos comuns em spans do ML-NSMF."""
    if slice_type:
        span.set_attribute("trisla.slice.type", str(slice_type))
    if confidence is not None:
        span.set_attribute("trisla.ml.confidence_score", float(confidence))
    if model_version:
        span.set_attribute("trisla.ml.model_version", str(model_version))
    
    for key, value in kwargs.items():
        span.set_attribute(f"trisla.{key}", str(value))


def trace_predict_slice(slice_type, predict_func, parent_context=None):
    """
    Helper para rastrear predição de slice.
    
    Uso:
        result = trace_predict_slice("eMBB", lambda: model.predict(data))
    """
    with create_ml_span("predict_slice", slice_type, parent_context) as span:
        set_ml_span_attributes(span, slice_type=slice_type, operation="prediction")
        try:
            result = predict_func()
            
            # Adicionar confidence score se disponível
            if hasattr(result, 'confidence'):
                set_ml_span_attributes(span, confidence=result.confidence)
            
            span.set_attribute("trisla.prediction.status", "success")
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("trisla.prediction.status", "error")
            raise














