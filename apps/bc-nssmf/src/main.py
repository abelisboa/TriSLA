
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
BC-NSSMF - Blockchain-enabled Network Slice Subnet Management Function
Executa Smart Contracts e valida SLAs
"""

from fastapi import FastAPI, HTTPException, Response, APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

import sys
import os
import re
from typing import Any, Dict, List, Union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service import BCService, BCInfrastructureError, BCBusinessError
from oracle import MetricsOracle
from kafka_consumer import DecisionConsumer
from models import (
    SLARegisterRequest, 
    SLAStatusUpdateRequest, 
    ContractExecuteRequest,
    SLARequest,  # legado - para mapeamento interno
    SLAStatusUpdate  # legado - para mapeamento interno
)
import logging

logger = logging.getLogger(__name__)

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

app = FastAPI(title="TriSLA BC-NSSMF", version="3.10.0")
_trisla_attach_observability(app, os.getenv("TRISLA_SERVICE_NAME", "bc-nssmf"))
FastAPIInstrumentor.instrument_app(app)

# Inicializar com fallback para RPC offline (modo DEV)
bc_enabled = os.getenv("BC_ENABLED", "false").lower() == "true"
enabled = False
bc_service = None

if bc_enabled:
    try:
        bc_service = BCService()
        enabled = bool(getattr(bc_service, "enabled", False))
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
    rpc_ok = False
    if bc_service and getattr(bc_service, "w3", None):
        try:
            rpc_ok = bool(bc_service.w3.is_connected())
        except Exception:
            rpc_ok = False
    svc_ok = bool(bc_service and getattr(bc_service, "enabled", False))
    status = "healthy" if (svc_ok and rpc_ok) else "degraded"
    return {
        "status": status,
        "module": "bc-nssmf",
        "enabled": svc_ok,
        "rpc_connected": rpc_ok,
    }


@app.get("/health/ready")
def health_ready():
    """Endpoint de readiness real - verifica RPC conectado e BC_PRIVATE_KEY válida"""
    try:
        # Verificar se módulos de wallet estão disponíveis
        try:
            from blockchain.tx_sender import rpc_connected
            from blockchain.wallet import get_sender_address
        except ImportError:
            return JSONResponse(
                status_code=503,
                content={"ready": False, "reason": "wallet_module_unavailable"}
            )
        
        # Verificar RPC conectado
        if not rpc_connected():
            return JSONResponse(
                status_code=503,
                content={"ready": False, "reason": "rpc_unreachable"}
            )
        
        # Verificar BC_PRIVATE_KEY e derivar endereço
        addr = get_sender_address()
        return {
            "ready": True,
            "rpc_connected": True,
            "sender": addr
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"ready": False, "reason": "wallet_unavailable", "detail": str(e)}
        )


@app.get("/metrics")
async def metrics():
    """Expor métricas Prometheus"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

def _bc_error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"tx_hash": None, "status": "ERROR", "error": message},
    )


# Interface I-04 - REST API (schema v1.0 + compat legado; nunca acessar SLO.value sem fallback)


def _parse_latency_ms(v: Any) -> int:
    """Converte latency do portal (ex.: '3ms', '20ms') para inteiro em ms."""
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().lower()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*ms$", s)
    if m:
        return int(float(m.group(1)))
    m = re.match(r"^(\d+)$", s)
    if m:
        return int(m.group(1))
    try:
        return int(float(s))
    except ValueError:
        return 0


def _flatten_sla_requirements_dict(d: Dict[str, Any]) -> List[Dict[str, Union[int, str]]]:
    """
    O portal-backend envia `sla_requirements` como dict plano (latency, throughput, reliability, template_id).
    Iterar esse dict como lista de SLOs (via chaves) gera tuplas inválidas; convertemos para SLOs explícitos.
    """
    out: List[Dict[str, Union[int, str]]] = []
    if not isinstance(d, dict):
        return out
    if d.get("latency") is not None:
        ms = _parse_latency_ms(d.get("latency"))
        out.append({"name": "latency", "value": ms, "threshold": ms})
    if d.get("throughput") is not None:
        try:
            tv = int(float(d.get("throughput")))
        except (TypeError, ValueError):
            tv = 0
        out.append({"name": "throughput", "value": tv, "threshold": tv})
    if d.get("reliability") is not None:
        try:
            rv = int(float(d.get("reliability")) * 1000)
        except (TypeError, ValueError):
            rv = 990
        out.append({"name": "reliability", "value": rv, "threshold": rv})
    tid = d.get("template_id") or d.get("slice_type")
    if tid is not None:
        key = str(tid).strip().lower()
        slice_code = {"urllc": 1, "embb": 2, "mmtc": 3}.get(key)
        if slice_code is not None:
            out.append({"name": "slice", "value": slice_code, "threshold": slice_code})
    return out


def _normalize_slos_to_contract(slos_list) -> list:
    """Converte SLOs para formato do contrato (name, value_int, threshold_int). Compat: value opcional."""
    out = []
    for s in slos_list:
        name = getattr(s, "name", "") or (s.get("name") if isinstance(s, dict) else "")
        th = getattr(s, "threshold", None)
        if th is None and isinstance(s, dict):
            th = s.get("threshold")
        if isinstance(th, dict):
            th = th.get("value") or th.get("threshold")
        th = int(th) if th is not None else 0
        val = getattr(s, "value", None)
        if val is None and isinstance(s, dict):
            val = s.get("value")
        val = int(val) if val is not None else th
        out.append((str(name), val, th))
    return out


@app.post("/api/v1/register-sla")
async def register_sla(request: Request):
    """Registra SLA no blockchain (Interface I-04). Aceita schema v1.0 (slo_set/sla_requirements) e legado (slos)."""
    with tracer.start_as_current_span("register_sla_i04") as span:
        if not enabled or not bc_service:
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error", "BC-NSSMF em modo degraded")
            return _bc_error_response(
                503,
                "BC-NSSMF está em modo degraded. RPC Besu não disponível.",
            )
        
        try:
            body = await request.json()
            correlation_id = body.get("correlation_id") or body.get("intent_id") or ""
            span.set_attribute("sla.correlation_id", str(correlation_id)[:64])
            print(
                f"[BC_REGISTER_SLA] intent_id={body.get('intent_id')} "
                f"nest_id={body.get('nest_id')} decision={body.get('decision')}",
                flush=True,
            )
            logger.info(
                "[BC_REGISTER_SLA] intent_id=%s nest_id=%s decision=%s",
                body.get("intent_id"),
                body.get("nest_id"),
                body.get("decision"),
            )
            
            # Schema v1.0: slo_set ou sla_requirements
            slos_raw = body.get("slo_set") or body.get("sla_requirements")
            if slos_raw is not None:
                if isinstance(slos_raw, dict):
                    slos_raw = _flatten_sla_requirements_dict(slos_raw)
                slos = _normalize_slos_to_contract(slos_raw)
                customer = body.get("customer") or body.get("intent_id") or correlation_id or "default"
                service_name = (
                    body.get("service_name")
                    or body.get("action")
                    or body.get("decision")
                    or "ACCEPT"
                )
                sla_hash = body.get("slaHash") or body.get("sla_hash") or correlation_id or ""
            else:
                # Legado: SLARequest com slos[]
                try:
                    req = SLARequest(**body)
                except ValidationError as e:
                    return _bc_error_response(422, f"Payload inválido (schema legado): {e.errors()}")
                slos = _normalize_slos_to_contract(req.slos)
                customer = req.customer
                service_name = req.serviceName
                sla_hash = req.slaHash or ""
            
            if not slos:
                return _bc_error_response(
                    422,
                    "Lista de SLOs vazia ou inválida. Use slo_set, sla_requirements ou slos (legado).",
                )
            
            # Converter slaHash para bytes32
            from web3 import Web3
            sla_hash_bytes = Web3.keccak(text=str(sla_hash)) if sla_hash else Web3.keccak(text="")
            
            # Registrar SLA no blockchain
            receipt = bc_service.register_sla(
                customer,
                service_name,
                sla_hash_bytes,
                slos
            )
            
            span.set_attribute("sla.registered", True)
            span.set_attribute("sla.tx_hash", receipt.transactionHash.hex())
            
            return {
                "status": "COMMITTED",
                "bc_status": "COMMITTED",
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "sla_id": customer,
                "correlation_id": correlation_id,
            }
        except BCBusinessError as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "business")
            return _bc_error_response(422, str(e))
        except BCInfrastructureError as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "infrastructure")
            return _bc_error_response(503, str(e))
        except RuntimeError as e:
            # Manter compatibilidade com RuntimeError antigo (tratar como infraestrutura)
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "infrastructure")
            return _bc_error_response(503, str(e))
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "unknown")
            return _bc_error_response(500, f"Erro ao registrar SLA: {str(e)}")


@app.post("/api/v1/update-sla-status")
async def update_sla_status(req: SLAStatusUpdateRequest):
    """Atualiza status de SLA no blockchain (Interface I-04) - Schema final"""
    with tracer.start_as_current_span("update_sla_status_i04") as span:
        if not enabled or not bc_service:
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error", "BC-NSSMF em modo degraded")
            return _bc_error_response(
                503,
                "BC-NSSMF está em modo degraded. RPC Besu não disponível.",
            )
        
        try:
            # Mapear status string para int (schema final usa string)
            status_map = {
                "CREATED": 0,
                "ACTIVE": 1,
                "VIOLATED": 2,
                "RENEGOTIATED": 3,
                "CLOSED": 4
            }
            
            if req.status not in status_map:
                return _bc_error_response(
                    422,
                    f"Status inválido: {req.status}. Valores permitidos: {list(status_map.keys())}",
                )
            
            new_status_int = status_map[req.status]
            
            # Atualizar status no blockchain
            receipt = bc_service.update_status(req.sla_id, new_status_int)
            
            span.set_attribute("sla.updated", True)
            span.set_attribute("sla.tx_hash", receipt.transactionHash.hex())
            span.set_attribute("sla.id", req.sla_id)
            span.set_attribute("sla.status", req.status)
            
            return {
                "status": "COMMITTED",
                "bc_status": "COMMITTED",
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "sla_id": req.sla_id,
                "new_status": req.status,
            }
        except BCBusinessError as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "business")
            return _bc_error_response(422, str(e))
        except BCInfrastructureError as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "infrastructure")
            return _bc_error_response(503, str(e))
        except RuntimeError as e:
            # Manter compatibilidade com RuntimeError antigo (tratar como infraestrutura)
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "infrastructure")
            return _bc_error_response(503, str(e))
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "unknown")
            return _bc_error_response(500, f"Erro ao atualizar status: {str(e)}")


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
async def execute_contract(req: ContractExecuteRequest):
    """Executa smart contract (Interface I-04) - Schema final explícito"""
    with tracer.start_as_current_span("execute_contract") as span:
        if not enabled or not bc_service:
            span.set_attribute("contract.executed", False)
            span.set_attribute("contract.error", "BC-NSSMF em modo degraded")
            raise HTTPException(
                status_code=503,
                detail="BC-NSSMF está em modo degraded. RPC Besu não disponível."
            )
        
        try:
            # Validar schema final
            if req.operation not in ["DEPLOY", "EXECUTE"]:
                raise HTTPException(
                    status_code=422,
                    detail=f"Operation inválida: {req.operation}. Valores permitidos: DEPLOY, EXECUTE"
                )
            
            if req.operation == "EXECUTE":
                if not req.function:
                    raise HTTPException(
                        status_code=422,
                        detail="Campo 'function' é obrigatório quando operation='EXECUTE'"
                    )
                if req.args is None:
                    raise HTTPException(
                        status_code=422,
                        detail="Campo 'args' é obrigatório quando operation='EXECUTE'"
                    )
            
            # Obter métricas do oracle
            metrics = await metrics_oracle.get_metrics()
            
            # Executar operação
            if req.operation == "DEPLOY":
                # Deploy de contrato (implementação futura)
                result = {
                    "status": "ok",
                    "operation": "DEPLOY",
                    "message": "Contract deployment initiated",
                    "metrics": metrics
                }
            else:  # EXECUTE
                # Executar função do contrato (implementação futura)
                result = {
                    "status": "ok",
                    "operation": "EXECUTE",
                    "function": req.function,
                    "args": req.args,
                    "message": f"Function {req.function} executed",
                    "metrics": metrics
                }
            
            span.set_attribute("contract.executed", True)
            span.set_attribute("contract.operation", req.operation)
            return result
        except HTTPException:
            raise
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("contract.executed", False)
            raise HTTPException(status_code=500, detail=f"Erro ao executar contrato: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
