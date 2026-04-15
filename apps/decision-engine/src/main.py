# === TRISLA_OBSERVABILITY_BEGIN ===
import os
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

TRISLA_HTTP_REQUESTS_TOTAL = Counter(
    "trisla_http_requests_total",
    "Total de requisições HTTP por serviço e rota",
    ["service", "method", "path", "status"]
)

TRISLA_HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "trisla_http_request_duration_seconds",
    "Duração de requisições HTTP em segundos por serviço e rota",
    ["service", "method", "path"]
)

TRISLA_PROCESS_CPU_SECONDS_TOTAL = Gauge(
    "trisla_process_cpu_seconds_total",
    "CPU seconds placeholder",
    ["service"]
)


def _trisla_setup_otel(service_name: str):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://trisla-otel-collector.trisla.svc.cluster.local:4317"
        )

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)

        return FastAPIInstrumentor

    except Exception:
        return None


def _trisla_attach_observability(app: FastAPI, service_name: str):

    @app.middleware("http")
    async def _trisla_prom_mw(request: Request, call_next):
        method = request.method
        path = request.url.path

        with TRISLA_HTTP_REQUEST_DURATION_SECONDS.labels(
            service=service_name,
            method=method,
            path=path
        ).time():
            response = await call_next(request)

        TRISLA_HTTP_REQUESTS_TOTAL.labels(
            service=service_name,
            method=method,
            path=path,
            status=str(response.status_code)
        ).inc()

        return response


    @app.get("/metrics")
    async def _metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    instr = _trisla_setup_otel(service_name)
    if instr:
        try:
            instr.instrument_app(app)
        except Exception:
            pass

# === TRISLA_OBSERVABILITY_END ===


"""
Decision Engine - Motor de Decisão
"""

from contextlib import asynccontextmanager
from typing import Optional
import logging
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import threading
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decision_maker import DecisionMaker
from rule_engine import RuleEngine
from kafka_consumer import DecisionConsumer
from kafka_producer import DecisionProducer
from kafka_producer_retry import DecisionProducerWithRetry
from grpc_server import serve as serve_grpc

from decision_snapshot import build_decision_snapshot
from system_xai import explain_decision
from decision_persistence import persist_decision_evidence

from service import DecisionService
from models import DecisionResult, DecisionInput, SLAIntent, NestSubset, SLAEvaluateInput
from config import config
from nasp_adapter_client import NASPAdapterClient
from portal_backend_client import PortalBackendClient


trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
_evaluate_logger = logging.getLogger(__name__)


otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"

if otlp_enabled:
    try:
        otlp_endpoint = os.getenv("OTLP_ENDPOINT_GRPC", config.otlp_endpoint_grpc)

        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

            span_processor = BatchSpanProcessor(otlp_exporter)

            trace.get_tracer_provider().add_span_processor(span_processor)

    except Exception as e:
        print(f"⚠️ OTLP não disponível: {e}")


grpc_thread = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global grpc_thread

    import logging
    import time

    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    logger.info("Starting gRPC server thread")

    grpc_thread = threading.Thread(
        target=serve_grpc,
        daemon=True,
        name="gRPC-Server"
    )

    grpc_thread.start()

    time.sleep(2)

    yield

    logger.info("Stopping Decision Engine")


app = FastAPI(
    title="TriSLA Decision Engine",
    version="3.10.0",
    lifespan=lifespan
)


# 🔵 AQUI ESTÁ A CORREÇÃO CRÍTICA
_trisla_attach_observability(
    app,
    os.getenv("TRISLA_SERVICE_NAME", "decision-engine")
)


rule_engine = RuleEngine()
decision_maker = DecisionMaker(rule_engine)

decision_service = DecisionService()

nasp_adapter_client = NASPAdapterClient()
portal_backend_client = PortalBackendClient()

decisions_storage = {}


kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

if kafka_enabled:

    decision_consumer = DecisionConsumer(decision_maker)

    USE_KAFKA_RETRY = os.getenv("USE_KAFKA_RETRY", "true").lower() == "true"

    if USE_KAFKA_RETRY:

        kafka_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "kafka:9092"
        ).split(",")

        decision_producer = DecisionProducerWithRetry(kafka_servers)

    else:

        decision_producer = DecisionProducer()

else:

    decision_consumer = None
    decision_producer = None


@app.get("/health")
async def health():

    kafka_status = "enabled" if kafka_enabled else "offline"

    return {
        "status": "healthy",
        "module": "decision-engine",
        "kafka": kafka_status,
        "grpc_thread": "alive" if grpc_thread and grpc_thread.is_alive() else "not_running"
    }


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/evaluate", response_model=DecisionResult)
async def evaluate_sla(sla_input: SLAEvaluateInput):

    with tracer.start_as_current_span("evaluate_sla"):

        telemetry_snapshot = sla_input.telemetry_snapshot or {}
        ran = telemetry_snapshot.get("ran") or {}
        transport = telemetry_snapshot.get("transport") or {}
        core = telemetry_snapshot.get("core") or {}
        ran_prb = ran.get("prb_utilization")
        print(f"[PRB RECEIVED] ran_prb={ran_prb}")
        _evaluate_logger.info("[PRB RECEIVED] ran_prb=%s", ran_prb)
        rtt = transport.get("latency_ms")
        if rtt is None:
            rtt = transport.get("rtt")
        print(
            f"[MULTI-DOMAIN] PRB={ran_prb} RTT={rtt} "
            f"CPU={core.get('cpu_utilization')} MEM={core.get('memory_utilization')}"
        )
        _evaluate_logger.info(
            "[MULTI-DOMAIN] PRB=%s RTT=%s CPU=%s MEM=%s",
            ran_prb,
            rtt,
            core.get("cpu_utilization"),
            core.get("memory_utilization"),
        )

        merged_context: dict = dict(sla_input.context or {})
        if sla_input.telemetry_snapshot is not None:
            merged_context["telemetry_snapshot"] = sla_input.telemetry_snapshot

        decision_input = DecisionInput(
            intent=sla_input.intent,
            nest=sla_input.nest,
            context=merged_context if merged_context else None,
        )

        decision_result = await decision_service.process_decision_from_input(
            decision_input
        )

        decisions_storage[decision_result.decision_id] = decision_result.dict()

        return decision_result


FastAPIInstrumentor.instrument_app(app)


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082
    )
