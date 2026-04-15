
# === TRISLA_OBSERVABILITY_BEGIN ===
import os
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

# --- Prometheus primitives ---
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
    "CPU seconds (aprox) exposto via OTEL/Runtime; placeholder gauge para padronização",
    ["service"]
)

# --- OTEL setup (OTLP -> Collector) ---
def _trisla_setup_otel(service_name: str):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://trisla-otel-collector.trisla.svc.cluster.local:4317")
        insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=insecure)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        return FastAPIInstrumentor
    except Exception:
        return None

def _trisla_attach_observability(app: FastAPI, service_name: str):
    # Prometheus middleware + endpoint
    @app.middleware("http")
    async def _trisla_prom_mw(request: Request, call_next):
        method = request.method
        path = request.url.path
        with TRISLA_HTTP_REQUEST_DURATION_SECONDS.labels(service=service_name, method=method, path=path).time():
            response = await call_next(request)
        TRISLA_HTTP_REQUESTS_TOTAL.labels(service=service_name, method=method, path=path, status=str(response.status_code)).inc()
        return response

    @app.get("/metrics")
    async def _metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # OTEL instrument app (traces)
    instr = _trisla_setup_otel(service_name)
    if instr is not None:
        try:
            instr.instrument_app(app)
        except Exception:
            pass

# === TRISLA_OBSERVABILITY_END ===

"""
TriSLA Traffic Exporter — v3.10.8
Módulo de observabilidade passiva: exporta métricas Prometheus e opcionalmente eventos Kafka.
Sem interferência no plano de decisão.
Labels SLA/NSI/NSSI (PROMPT_SNASP_07): opcionais, default "unknown".
"""
import os
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI(title="TriSLA Traffic Exporter", version="3.10.8")
_trisla_attach_observability(app, os.getenv("TRISLA_SERVICE_NAME", "traffic-exporter"))

# Métricas baseline para reprodutibilidade científica
METRICS_PORT = int(os.environ.get("METRICS_PORT", "9105"))

# Labels canônicos SLA/NSI (SSOT PROMPT_SNASP_07); ausência → "unknown"
SLA_LABEL_NAMES = ["sla_id", "nsi_id", "nssi_id", "slice_type", "sst", "sd", "domain"]


def _sla_context(**overrides):
    """Retorna dicionário de labels SLA com default 'unknown'. Não lança exceção."""
    ctx = {k: "unknown" for k in SLA_LABEL_NAMES}
    for k, v in overrides.items():
        if k in ctx and v is not None:
            ctx[k] = str(v)
    return ctx


requests_total = Counter(
    "trisla_traffic_exporter_requests_total",
    "Total de requisições ao exporter",
    ["method", "path"] + SLA_LABEL_NAMES,
)
exporter_up = Gauge(
    "trisla_traffic_exporter_up",
    "Exporter está ativo (1 = up)",
    SLA_LABEL_NAMES,
)


@app.on_event("startup")
def startup():
    exporter_up.labels(**_sla_context()).set(1)


@app.get("/health")
def health():
    return {"status": "ok", "service": "trisla-traffic-exporter", "version": "3.10.8"}


@app.get("/metrics")
def metrics():
    requests_total.labels(method="GET", path="/metrics", **_sla_context()).inc()
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=METRICS_PORT)
