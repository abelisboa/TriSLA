# TriSLA Common Telemetry
# Biblioteca comum para instrumentação OpenTelemetry

from .setup import setup_telemetry, get_tracer, get_meter, get_logger
from .decorators import trace_function, measure_time, log_execution
from .metrics import Counter, Histogram, Gauge
from .traces import SpanContext, TraceContext

__all__ = [
    'setup_telemetry',
    'get_tracer',
    'get_meter', 
    'get_logger',
    'trace_function',
    'measure_time',
    'log_execution',
    'Counter',
    'Histogram',
    'Gauge',
    'SpanContext',
    'TraceContext'
]




