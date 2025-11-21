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

from smart_contracts import SmartContractExecutor
from oracle import MetricsOracle
from kafka_consumer import DecisionConsumer

# OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://otlp-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI(title="TriSLA BC-NSSMF", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

# Inicializar
contract_executor = SmartContractExecutor()
metrics_oracle = MetricsOracle()
decision_consumer = DecisionConsumer(contract_executor, metrics_oracle)


@app.get("/health")
async def health():
    return {"status": "healthy", "module": "bc-nssmf"}


@app.post("/api/v1/execute-contract")
async def execute_contract(contract_data: dict):
    """Executa smart contract"""
    with tracer.start_as_current_span("execute_contract") as span:
        # Obter métricas do oracle
        metrics = await metrics_oracle.get_metrics()
        
        # Executar contract
        result = await contract_executor.execute(contract_data, metrics)
        
        span.set_attribute("contract.executed", True)
        return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)

