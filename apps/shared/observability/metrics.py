"""
Métricas Customizadas - TriSLA
Métricas por interface (I-01 a I-07) e métricas gerais
"""

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
import os
import logging

logger = logging.getLogger(__name__)

# Criar resource com informações do serviço
resource = Resource.create({
    "service.name": "trisla",
    "service.version": os.getenv("SERVICE_VERSION", "v3.7.7"),
    "deployment.environment": os.getenv("DEPLOYMENT_ENVIRONMENT", "production")
})

# Configurar OTLP Metric Exporter
otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"
otlp_endpoint = os.getenv("OTLP_ENDPOINT_GRPC", "http://otlp-collector:4317")

if otlp_enabled:
    try:
        metric_exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            insecure=True
        )
        metric_reader = PeriodicExportingMetricReader(
            metric_exporter,
            export_interval_millis=5000  # Exportar a cada 5 segundos
        )
        meter_provider = MeterProvider(
            metric_readers=[metric_reader],
            resource=resource
        )
        metrics.set_meter_provider(meter_provider)
        logger.info(f"✅ OTLP Metrics habilitado: {otlp_endpoint}")
    except Exception as e:
        logger.warning(f"⚠️ OTLP Metrics não disponível: {e}")
        # Fallback para meter provider sem exportação
        meter_provider = MeterProvider(resource=resource)
        metrics.set_meter_provider(meter_provider)
else:
    meter_provider = MeterProvider(resource=resource)
    metrics.set_meter_provider(meter_provider)
    logger.info("ℹ️ OTLP Metrics desabilitado (OTLP_ENABLED=false)")

# Obter meter
meter = metrics.get_meter(__name__)

# ============================================
# Métricas por Interface (I-01 a I-07)
# ============================================

# I-01: SEM-CSMF → Decision Engine (gRPC)
i01_requests_total = meter.create_counter(
    name="trisla_i01_requests_total",
    description="Total de requisições I-01 (SEM-CSMF → Decision Engine)",
    unit="1"
)

i01_request_duration = meter.create_histogram(
    name="trisla_i01_request_duration_seconds",
    description="Duração de requisições I-01 em segundos",
    unit="s"
)

i01_errors_total = meter.create_counter(
    name="trisla_i01_errors_total",
    description="Total de erros I-01",
    unit="1"
)

# I-02: ML-NSMF → Decision Engine (Kafka)
i02_messages_total = meter.create_counter(
    name="trisla_i02_messages_total",
    description="Total de mensagens I-02 (ML-NSMF → Decision Engine)",
    unit="1"
)

i02_message_duration = meter.create_histogram(
    name="trisla_i02_message_duration_seconds",
    description="Duração de processamento de mensagens I-02 em segundos",
    unit="s"
)

i02_errors_total = meter.create_counter(
    name="trisla_i02_errors_total",
    description="Total de erros I-02",
    unit="1"
)

# I-03: Decision Engine → ML-NSMF (Kafka)
i03_messages_total = meter.create_counter(
    name="trisla_i03_messages_total",
    description="Total de mensagens I-03 (Decision Engine → ML-NSMF)",
    unit="1"
)

i03_message_duration = meter.create_histogram(
    name="trisla_i03_message_duration_seconds",
    description="Duração de processamento de mensagens I-03 em segundos",
    unit="s"
)

i03_errors_total = meter.create_counter(
    name="trisla_i03_errors_total",
    description="Total de erros I-03",
    unit="1"
)

# I-04: Decision Engine → BC-NSSMF (REST/gRPC)
i04_requests_total = meter.create_counter(
    name="trisla_i04_requests_total",
    description="Total de requisições I-04 (Decision Engine → BC-NSSMF)",
    unit="1"
)

i04_request_duration = meter.create_histogram(
    name="trisla_i04_request_duration_seconds",
    description="Duração de requisições I-04 em segundos",
    unit="s"
)

i04_errors_total = meter.create_counter(
    name="trisla_i04_errors_total",
    description="Total de erros I-04",
    unit="1"
)

# I-05: Decision Engine → SLA-Agent Layer (Kafka)
i05_messages_total = meter.create_counter(
    name="trisla_i05_messages_total",
    description="Total de mensagens I-05 (Decision Engine → SLA-Agent Layer)",
    unit="1"
)

i05_message_duration = meter.create_histogram(
    name="trisla_i05_message_duration_seconds",
    description="Duração de processamento de mensagens I-05 em segundos",
    unit="s"
)

i05_errors_total = meter.create_counter(
    name="trisla_i05_errors_total",
    description="Total de erros I-05",
    unit="1"
)

# I-06: SLA-Agent Layer → Decision Engine (Kafka/REST)
i06_events_total = meter.create_counter(
    name="trisla_i06_events_total",
    description="Total de eventos I-06 (SLA-Agent Layer → Decision Engine)",
    unit="1"
)

i06_event_duration = meter.create_histogram(
    name="trisla_i06_event_duration_seconds",
    description="Duração de processamento de eventos I-06 em segundos",
    unit="s"
)

i06_errors_total = meter.create_counter(
    name="trisla_i06_errors_total",
    description="Total de erros I-06",
    unit="1"
)

# I-07: NASP Adapter (REST)
i07_requests_total = meter.create_counter(
    name="trisla_i07_requests_total",
    description="Total de requisições I-07 (NASP Adapter)",
    unit="1"
)

i07_request_duration = meter.create_histogram(
    name="trisla_i07_request_duration_seconds",
    description="Duração de requisições I-07 em segundos",
    unit="s"
)

i07_errors_total = meter.create_counter(
    name="trisla_i07_errors_total",
    description="Total de erros I-07",
    unit="1"
)

# ============================================
# Métricas Gerais
# ============================================

# Intents
intents_total = meter.create_counter(
    name="trisla_intents_total",
    description="Total de intents processados",
    unit="1"
)

intent_processing_duration = meter.create_histogram(
    name="trisla_intent_processing_duration_seconds",
    description="Duração de processamento de intents em segundos",
    unit="s"
)

# NESTs
nests_generated_total = meter.create_counter(
    name="trisla_nests_generated_total",
    description="Total de NESTs gerados",
    unit="1"
)

# Predictions
predictions_total = meter.create_counter(
    name="trisla_predictions_total",
    description="Total de predições ML realizadas",
    unit="1"
)

prediction_duration = meter.create_histogram(
    name="trisla_prediction_duration_seconds",
    description="Duração de predições ML em segundos",
    unit="s"
)

# Decisions
decisions_total = meter.create_counter(
    name="trisla_decisions_total",
    description="Total de decisões tomadas",
    unit="1"
)

decision_latency = meter.create_histogram(
    name="trisla_decision_latency_seconds",
    description="Latência de decisões em segundos",
    unit="s"
)

# Blockchain Transactions
blockchain_transactions_total = meter.create_counter(
    name="trisla_blockchain_transactions_total",
    description="Total de transações blockchain",
    unit="1"
)

transaction_duration = meter.create_histogram(
    name="trisla_transaction_duration_seconds",
    description="Duração de transações blockchain em segundos",
    unit="s"
)

# Actions
actions_executed_total = meter.create_counter(
    name="trisla_actions_executed_total",
    description="Total de ações executadas",
    unit="1"
)

action_duration = meter.create_histogram(
    name="trisla_action_duration_seconds",
    description="Duração de execução de ações em segundos",
    unit="s"
)

# SLO Compliance (usando UpDownCounter como alternativa a Gauge)
slo_compliance_rate = meter.create_up_down_counter(
    name="trisla_slo_compliance_rate",
    description="Taxa de compliance com SLO (0.0 a 1.0)",
    unit="1"
)

slo_violations_total = meter.create_counter(
    name="trisla_slo_violations_total",
    description="Total de violações de SLO",
    unit="1"
)

# SLO por Interface (usando UpDownCounter como alternativa a Gauge)
slo_compliance_by_interface = meter.create_up_down_counter(
    name="trisla_slo_compliance_by_interface",
    description="Taxa de compliance com SLO por interface",
    unit="1"
)

