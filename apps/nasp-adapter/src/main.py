"""
NASP Adapter - Integração com NASP Real
Interface I-07 - Integração bidirecional
"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nasp_client import NASPClient
from metrics_collector import MetricsCollector
from action_executor import ActionExecutor

# OpenTelemetry (opcional em modo DEV)
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# OTLP endpoint via variável de ambiente (opcional)
otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"
if otlp_enabled:
    try:
        otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://otlp-collector:4317")
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        print("✅ OTLP habilitado para NASP Adapter")
    except Exception as e:
        print(f"⚠️ OTLP não disponível, continuando sem observabilidade: {e}")
else:
    print("ℹ️ NASP Adapter: Modo DEV - OTLP desabilitado (OTLP_ENABLED=false)")

app = FastAPI(title="TriSLA NASP Adapter", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

# Inicializar
nasp_client = NASPClient()
metrics_collector = MetricsCollector(nasp_client)
action_executor = ActionExecutor(nasp_client)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "module": "nasp-adapter",
        "nasp_connected": nasp_client.is_connected()
    }


@app.get("/api/v1/nasp/metrics")
async def get_nasp_metrics():
    """Coleta métricas reais do NASP (I-07)"""
    with tracer.start_as_current_span("collect_nasp_metrics") as span:
        metrics = await metrics_collector.collect_all()
        span.set_attribute("metrics.source", "nasp_real")
        return metrics


@app.post("/api/v1/nasp/actions")
async def execute_nasp_action(action: dict):
    """Executa ação real no NASP (I-07)"""
    with tracer.start_as_current_span("execute_nasp_action") as span:
        result = await action_executor.execute(action)
        span.set_attribute("action.executed", True)
        span.set_attribute("action.type", action.get("type"))
        return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)

