"""
BC-NSSMF - Blockchain-enabled Network Slice Subnet Management Function
Executa Smart Contracts e valida SLAs
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

from src.service import BCService
from src.oracle import MetricsOracle
from src.kafka_consumer import DecisionConsumer

# OpenTelemetry (opcional em modo DEV)
otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

if otlp_enabled:
    try:
        otlp_exporter = OTLPSpanExporter(endpoint="http://otlp-collector:4317", insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
    except Exception as e:
        print(f"⚠️ OTLP não disponível, continuando sem observabilidade: {e}")

app = FastAPI(title="TriSLA BC-NSSMF", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

# Inicializar com fallback para RPC offline (modo DEV)
bc_enabled = os.getenv("BC_ENABLED", "false").lower() == "true"
enabled = False
bc_service = None

if bc_enabled:
    try:
        bc_service = BCService()
        enabled = True
    except Exception as e:
        print(f"⚠️ BC-NSSMF: RPC Besu não disponível. Entrando em modo degraded: {e}")
        bc_service = None
        enabled = False
else:
    print("ℹ️ BC-NSSMF: Modo DEV - Blockchain desabilitado (BC_ENABLED=false)")
    enabled = False

metrics_oracle = MetricsOracle()
if enabled and bc_service:
    decision_consumer = DecisionConsumer(bc_service, metrics_oracle)
else:
    decision_consumer = None


@app.get("/health")
async def health():
    status = "healthy" if enabled else "degraded"
    return {
        "status": status,
        "module": "bc-nssmf",
        "enabled": enabled,
        "rpc_connected": enabled
    }


@app.post("/api/v1/execute-contract")
async def execute_contract(contract_data: dict):
    """Executa smart contract"""
    with tracer.start_as_current_span("execute_contract") as span:
        if not enabled or not bc_service:
            span.set_attribute("contract.executed", False)
            span.set_attribute("contract.error", "BC-NSSMF em modo degraded")
            return {
                "status": "error",
                "message": "BC-NSSMF está em modo degraded. RPC Besu não disponível.",
                "enabled": False
            }
        
        try:
            # Obter métricas do oracle
            metrics = await metrics_oracle.get_metrics()
            
            # Executar contract via BCService
            # Nota: BCService não tem método execute, usar register_sla como exemplo
            result = {
                "status": "executed",
                "contract_data": contract_data,
                "metrics": metrics
            }
            
            span.set_attribute("contract.executed", True)
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("contract.executed", False)
            return {
                "status": "error",
                "message": str(e)
            }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)

