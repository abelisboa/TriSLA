"""
BC-NSSMF - Blockchain-enabled Network Slice Subnet Management Function
Executa Smart Contracts Solidity em Ethereum Permissionado (GoQuorum/Besu)

Conforme dissertação TriSLA:
- Infraestrutura Ethereum permissionada (GoQuorum/Besu)
- Execução descentralizada dos contratos
- Rastreabilidade das cláusulas via eventos Solidity
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

from service import BCService
from oracle import MetricsOracle
from kafka_consumer import DecisionConsumer
from config import BCConfig

# OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://otlp-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI(
    title="TriSLA BC-NSSMF",
    description="Blockchain-enabled Network Slice Subnet Management Function - Ethereum Permissionado (GoQuorum/Besu)",
    version="1.0.0"
)
FastAPIInstrumentor.instrument_app(app)

# Inicializar componentes
try:
    bc_config = BCConfig()
    bc_service = BCService(bc_config)
    metrics_oracle = MetricsOracle()
    decision_consumer = DecisionConsumer(
        bc_service=bc_service,
        metrics_oracle=metrics_oracle
    )
    print(f"✅ BC-NSSMF inicializado com {bc_config.blockchain_type}")
except Exception as e:
    print(f"❌ Erro ao inicializar BC-NSSMF: {e}")
    bc_service = None
    metrics_oracle = None
    decision_consumer = None


@app.get("/health")
async def health():
    """Health check endpoint"""
    if bc_service is None:
        return {
            "status": "unhealthy",
            "module": "bc-nsmf",
            "error": "BCService não inicializado"
        }
    
    try:
        # Verificar conexão com blockchain
        is_connected = bc_service.w3.is_connected()
        return {
            "status": "healthy" if is_connected else "degraded",
            "module": "bc-nssmf",
            "blockchain": {
                "type": bc_service.config.blockchain_type,
                "connected": is_connected,
                "rpc_url": bc_service.config.rpc_url,
                "chain_id": bc_service.config.chain_id,
                "contract_address": bc_service.contract_address
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "module": "bc-nssmf",
            "error": str(e)
        }


@app.post("/api/v1/register-sla")
async def register_sla(sla_data: dict):
    """
    Registra SLA no contrato Solidity em Ethereum permissionado (GoQuorum/Besu)
    
    IMPORTANTE: Esta operação é executada na blockchain real, não em simulação.
    """
    with tracer.start_as_current_span("register_sla_api") as span:
        if bc_service is None:
            return {"error": "BCService não inicializado"}
        
        try:
            customer = sla_data.get("customer")
            service_name = sla_data.get("service_name")
            sla_hash = sla_data.get("sla_hash", "")
            slos = sla_data.get("slos", [])
            
            result = bc_service.register_sla(
                customer=customer,
                service_name=service_name,
                sla_hash=sla_hash,
                slos=slos
            )
            
            span.set_attribute("blockchain.tx_hash", result.get("transaction_hash"))
            span.set_attribute("blockchain.sla_id", result.get("sla_id"))
            
            return result
            
        except Exception as e:
            span.record_exception(e)
            return {"error": str(e)}


@app.get("/api/v1/sla/{sla_id}")
async def get_sla(sla_id: int):
    """
    Obtém informações do SLA do contrato Solidity
    """
    with tracer.start_as_current_span("get_sla_api") as span:
        if bc_service is None:
            return {"error": "BCService não inicializado"}
        
        try:
            sla_info = bc_service.get_sla(sla_id)
            span.set_attribute("sla.id", sla_id)
            return sla_info
        except Exception as e:
            span.record_exception(e)
            return {"error": str(e)}


@app.get("/api/v1/sla/{sla_id}/events")
async def get_sla_events(sla_id: int, from_block: int = 0):
    """
    Obtém eventos do SLA (SLARequested, SLAUpdated, SLACompleted)
    """
    with tracer.start_as_current_span("get_sla_events_api") as span:
        if bc_service is None:
            return {"error": "BCService não inicializado"}
        
        try:
            events = bc_service.get_sla_events(sla_id, from_block)
            span.set_attribute("sla.id", sla_id)
            span.set_attribute("events.count", len(events))
            return {"sla_id": sla_id, "events": events}
        except Exception as e:
            span.record_exception(e)
            return {"error": str(e)}


@app.get("/api/v1/oracle/metrics")
async def get_oracle_metrics():
    """
    Obtém métricas do Oracle (NASP Adapter)
    """
    with tracer.start_as_current_span("get_oracle_metrics_api") as span:
        if metrics_oracle is None:
            return {"error": "MetricsOracle não inicializado"}
        
        try:
            metrics = await metrics_oracle.get_metrics()
            span.set_attribute("metrics.source", metrics.get("source", "unknown"))
            return metrics
        except Exception as e:
            span.record_exception(e)
            return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
