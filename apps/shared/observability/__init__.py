"""
Observability Shared Module - TriSLA
Módulo compartilhado para observabilidade
"""

from .metrics import (
    # Métricas por interface
    i01_requests_total, i01_request_duration, i01_errors_total,
    i02_messages_total, i02_message_duration, i02_errors_total,
    i03_messages_total, i03_message_duration, i03_errors_total,
    i04_requests_total, i04_request_duration, i04_errors_total,
    i05_messages_total, i05_message_duration, i05_errors_total,
    i06_events_total, i06_event_duration, i06_errors_total,
    i07_requests_total, i07_request_duration, i07_errors_total,
    # Métricas gerais
    intents_total, intent_processing_duration,
    nests_generated_total,
    predictions_total, prediction_duration,
    decisions_total, decision_latency,
    blockchain_transactions_total, transaction_duration,
    actions_executed_total, action_duration,
    slo_compliance_rate, slo_violations_total,
    slo_compliance_by_interface
)

from .trace_context import (
    inject_trace_context,
    extract_trace_context,
    get_trace_id,
    get_span_id,
    create_span_from_context,
    add_interface_attributes,
    set_span_status,
    create_distributed_trace
)

from .slo_calculator import SLOCalculator

__all__ = [
    # Métricas
    "i01_requests_total", "i01_request_duration", "i01_errors_total",
    "i02_messages_total", "i02_message_duration", "i02_errors_total",
    "i03_messages_total", "i03_message_duration", "i03_errors_total",
    "i04_requests_total", "i04_request_duration", "i04_errors_total",
    "i05_messages_total", "i05_message_duration", "i05_errors_total",
    "i06_events_total", "i06_event_duration", "i06_errors_total",
    "i07_requests_total", "i07_request_duration", "i07_errors_total",
    "intents_total", "intent_processing_duration",
    "nests_generated_total",
    "predictions_total", "prediction_duration",
    "decisions_total", "decision_latency",
    "blockchain_transactions_total", "transaction_duration",
    "actions_executed_total", "action_duration",
    "slo_compliance_rate", "slo_violations_total",
    "slo_compliance_by_interface",
    # Trace Context
    "inject_trace_context",
    "extract_trace_context",
    "get_trace_id",
    "get_span_id",
    "create_span_from_context",
    "add_interface_attributes",
    "set_span_status",
    "create_distributed_trace",
    # SLO Calculator
    "SLOCalculator"
]






