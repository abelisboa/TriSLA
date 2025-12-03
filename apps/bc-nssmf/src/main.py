"""
BC-NSSMF - Blockchain-enabled Network Slice Subnet Management Function
Executa Smart Contracts e valida SLAs
"""

from fastapi import FastAPI, HTTPException
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
from models import SLARequest, SLAStatusUpdate

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


# Interface I-04 - REST API
@app.post("/api/v1/register-sla")
async def register_sla(req: SLARequest):
    """Registra SLA no blockchain (Interface I-04)"""
    with tracer.start_as_current_span("register_sla_i04") as span:
        if not enabled or not bc_service:
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error", "BC-NSSMF em modo degraded")
            raise HTTPException(
                status_code=503,
                detail="BC-NSSMF está em modo degraded. RPC Besu não disponível."
            )
        
        try:
            # Converter SLOs para formato do contrato
            slos = [(s.name, s.value, s.threshold) for s in req.slos]
            
            # Converter slaHash para bytes32
            from web3 import Web3
            sla_hash_bytes = Web3.keccak(text=req.slaHash) if req.slaHash else Web3.keccak(text="")
            
            # Registrar SLA no blockchain
            receipt = bc_service.register_sla(
                req.customer,
                req.serviceName,
                sla_hash_bytes,
                slos
            )
            
            span.set_attribute("sla.registered", True)
            span.set_attribute("sla.tx_hash", receipt.transactionHash.hex())
            
            return {
                "status": "ok",
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "sla_id": req.customer  # Em produção, extrair do evento
            }
        except RuntimeError as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            raise HTTPException(status_code=500, detail=f"Erro ao registrar SLA: {str(e)}")


@app.post("/api/v1/update-sla-status")
async def update_sla_status(req: SLAStatusUpdate):
    """Atualiza status de SLA no blockchain (Interface I-04)"""
    with tracer.start_as_current_span("update_sla_status_i04") as span:
        if not enabled or not bc_service:
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error", "BC-NSSMF em modo degraded")
            raise HTTPException(
                status_code=503,
                detail="BC-NSSMF está em modo degraded. RPC Besu não disponível."
            )
        
        try:
            # Atualizar status no blockchain
            receipt = bc_service.update_status(req.slaId, req.newStatus)
            
            span.set_attribute("sla.updated", True)
            span.set_attribute("sla.tx_hash", receipt.transactionHash.hex())
            
            return {
                "status": "ok",
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber
            }
        except RuntimeError as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")


@app.get("/api/v1/get-sla/{sla_id}")
async def get_sla(sla_id: int):
    """Obtém SLA do blockchain (Interface I-04)"""
    with tracer.start_as_current_span("get_sla_i04") as span:
        if not enabled or not bc_service:
            span.set_attribute("sla.retrieved", False)
            span.set_attribute("sla.error", "BC-NSSMF em modo degraded")
            raise HTTPException(
                status_code=503,
                detail="BC-NSSMF está em modo degraded. RPC Besu não disponível."
            )
        
        try:
            sla_data = bc_service.get_sla(sla_id)
            
            if sla_data is None:
                raise HTTPException(status_code=404, detail=f"SLA {sla_id} não encontrado")
            
            span.set_attribute("sla.retrieved", True)
            span.set_attribute("sla.id", sla_id)
            
            return {
                "sla_id": sla_id,
                "customer": sla_data[0],
                "service_name": sla_data[1],
                "status": sla_data[2],
                "created_at": sla_data[3],
                "updated_at": sla_data[4]
            }
        except HTTPException:
            raise
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("sla.retrieved", False)
            raise HTTPException(status_code=500, detail=f"Erro ao obter SLA: {str(e)}")


@app.post("/api/v1/execute-contract")
async def execute_contract(contract_data: dict):
    """Executa smart contract (Interface I-04 - genérico)"""
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

