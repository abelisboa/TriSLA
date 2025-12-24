"""
BC-NSSMF - Blockchain-enabled Network Slice Subnet Management Function
Executa Smart Contracts e valida SLAs
"""

from fastapi import FastAPI, HTTPException, Response, APIRouter
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

import sys
import os
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


@app.get("/health/ready")
def health_ready():
    """Endpoint de readiness real - verifica RPC conectado e BC_PRIVATE_KEY válida"""
    try:
        # Verificar se módulos de wallet estão disponíveis
        try:
            from src.blockchain.tx_sender import rpc_connected
            from src.blockchain.wallet import get_sender_address
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
        except BCBusinessError as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "business")
            raise HTTPException(status_code=422, detail=str(e))
        except BCInfrastructureError as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "infrastructure")
            raise HTTPException(status_code=503, detail=str(e))
        except RuntimeError as e:
            # Manter compatibilidade com RuntimeError antigo (tratar como infraestrutura)
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "infrastructure")
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("sla.registered", False)
            span.set_attribute("sla.error_type", "unknown")
            raise HTTPException(status_code=500, detail=f"Erro ao registrar SLA: {str(e)}")


@app.post("/api/v1/update-sla-status")
async def update_sla_status(req: SLAStatusUpdateRequest):
    """Atualiza status de SLA no blockchain (Interface I-04) - Schema final"""
    with tracer.start_as_current_span("update_sla_status_i04") as span:
        if not enabled or not bc_service:
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error", "BC-NSSMF em modo degraded")
            raise HTTPException(
                status_code=503,
                detail="BC-NSSMF está em modo degraded. RPC Besu não disponível."
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
                raise HTTPException(
                    status_code=422,
                    detail=f"Status inválido: {req.status}. Valores permitidos: {list(status_map.keys())}"
                )
            
            new_status_int = status_map[req.status]
            
            # Atualizar status no blockchain
            receipt = bc_service.update_status(req.sla_id, new_status_int)
            
            span.set_attribute("sla.updated", True)
            span.set_attribute("sla.tx_hash", receipt.transactionHash.hex())
            span.set_attribute("sla.id", req.sla_id)
            span.set_attribute("sla.status", req.status)
            
            return {
                "status": "ok",
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "sla_id": req.sla_id,
                "new_status": req.status
            }
        except BCBusinessError as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "business")
            raise HTTPException(status_code=422, detail=str(e))
        except BCInfrastructureError as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "infrastructure")
            raise HTTPException(status_code=503, detail=str(e))
        except RuntimeError as e:
            # Manter compatibilidade com RuntimeError antigo (tratar como infraestrutura)
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "infrastructure")
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("sla.updated", False)
            span.set_attribute("sla.error_type", "unknown")
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
async def execute_contract(req: ContractExecuteRequest):
    """Executa smart contract REAL on-chain"""
    import logging
    from web3 import Web3
    from src.blockchain.tx_sender import w3 as get_w3
    from src.blockchain.wallet import load_account, get_sender_address
    from src.deploy_contracts import load_contract
    from solcx import compile_standard, set_solc_version
    import json
    import os
    
    logger_bc = logging.getLogger(__name__)
    
    with tracer.start_as_current_span("execute_contract") as span:
        if not enabled or not bc_service:
            span.set_attribute("contract.executed", False)
            raise HTTPException(status_code=503, detail="BC-NSSMF em modo degraded")
        
        try:
            if req.operation not in ["DEPLOY", "EXECUTE"]:
                raise HTTPException(status_code=422, detail=f"Operation inválida: {req.operation}")
            
            if req.operation == "EXECUTE" and (not req.function or req.args is None):
                raise HTTPException(status_code=422, detail="Campos obrigatórios faltando")
            
            w3 = get_w3()
            account = load_account()
            from_addr = get_sender_address()
            
            if req.operation == "DEPLOY":
                logger_bc.info("[BC-NSSMF] Iniciando deploy REAL")
                contract_source = load_contract()
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                
                try:
                    set_solc_version("0.8.20")
                except:
                    pass
                
                compiled = compile_standard({
                    "language": "Solidity",
                    "sources": {"SLAContract.sol": {"content": contract_source}},
                    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
                })
                
                abi = compiled["contracts"]["SLAContract.sol"]["SLAContract"]["abi"]
                bytecode = compiled["contracts"]["SLAContract.sol"]["SLAContract"]["evm"]["bytecode"]["object"]
                
                contract = w3.eth.contract(abi=abi, bytecode=bytecode)
                nonce = w3.eth.get_transaction_count(from_addr)
                chain_id = int(w3.eth.chain_id)
                
                tx = contract.constructor().build_transaction({
                    "from": from_addr,
                    "chainId": chain_id,
                    "nonce": nonce,
                    "gas": 6_000_000,
                    "gasPrice": w3.eth.gas_price,
                })
                
                signed = account.sign_transaction(tx)
                tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                logger_bc.info(f"[BC-NSSMF] txHash={tx_hash.hex()}")
                
            # PATCH CIRÚRGICO: Retornar imediatamente sem bloquear
                # PATCH CIRÚRGICO: Retornar imediatamente sem bloquear
                return {
                    "status": "submitted",
                    "operation": "DEPLOY",
                    "txHash": tx_hash.hex()
                }
            else:
                logger_bc.info(f"[BC-NSSMF] Executando função REAL: {req.function}")
                if not bc_service.contract:
                    raise HTTPException(status_code=503, detail="Contrato não deployado")
                
                contract_address = bc_service.contract_address
                
                if req.function in ["registerSLA", "register_sla"]:
                    if len(req.args) < 4:
                        raise HTTPException(status_code=422, detail="Argumentos insuficientes")
                    customer = str(req.args[0])
                    service_name = str(req.args[1])
                    sla_hash_str = str(req.args[2])
                    sla_hash = w3.keccak(text=sla_hash_str) if not sla_hash_str.startswith("0x") else bytes.fromhex(sla_hash_str[2:])
                    slos = req.args[3] if isinstance(req.args[3], list) else []
                    slos_formatted = [(slo.get("name", ""), int(slo.get("value", 0)), int(slo.get("threshold", 0))) if isinstance(slo, dict) else (str(slo[0]), int(slo[1]), int(slo[2])) for slo in slos]
                    receipt = bc_service.register_sla(customer, service_name, sla_hash, slos_formatted)
                elif req.function in ["updateSLAStatus", "update_status"]:
                    if len(req.args) < 2:
                        raise HTTPException(status_code=422, detail="Argumentos insuficientes")
                    receipt = bc_service.update_status(int(req.args[0]), int(req.args[1]))
                else:
                    raise HTTPException(status_code=422, detail=f"Função não suportada: {req.function}")
                
                tx_hash = receipt.transactionHash.hex()
                block_number = receipt.blockNumber
                logger_bc.info(f"[BC-NSSMF] txHash={tx_hash}")
                logger_bc.info(f"[BC-NSSMF] blockNumber={block_number}")
                
                return {
                    "status": "ok",
                    "operation": "EXECUTE",
                    "function": req.function,
                    "txHash": tx_hash,
                    "contractAddress": contract_address,
                    "blockNumber": block_number,
                    "receipt": {
                        "status": hex(receipt.status),
                    }
                }
        except HTTPException:
            raise
        except Exception as e:
            span.record_exception(e)
            logger_bc.error(f"Erro: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erro ao executar contrato: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)



@app.post("/api/v1/contract/deploy")
async def deploy_contract():
    """Deploy REAL de contrato no blockchain - Endpoint para Phase 08"""
    import logging
    from web3 import Web3
    from src.blockchain.tx_sender import w3 as get_w3
    from src.blockchain.wallet import load_account, get_sender_address
    from src.deploy_contracts import load_contract
    from solcx import compile_standard, set_solc_version
    import json
    import os
    
    logger_bc = logging.getLogger(__name__)
    
    with tracer.start_as_current_span("deploy_contract_phase08") as span:
        if not enabled or not bc_service:
            span.set_attribute("contract.deployed", False)
            span.set_attribute("contract.error", "BC-NSSMF em modo degraded")
            raise HTTPException(status_code=503, detail="BC-NSSMF está em modo degraded. RPC Besu não disponível.")
        
        try:
            w3 = get_w3()
            account = load_account()
            from_addr = get_sender_address()
            
            logger_bc.info("[BC-NSSMF] Iniciando deploy REAL via /api/v1/contract/deploy")
            contract_source = load_contract()
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            
            try:
                set_solc_version("0.8.20")
            except:
                pass
            
            compiled = compile_standard({
                "language": "Solidity",
                "sources": {"SLAContract.sol": {"content": contract_source}},
                "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
            })
            
            abi = compiled["contracts"]["SLAContract.sol"]["SLAContract"]["abi"]
            bytecode = compiled["contracts"]["SLAContract.sol"]["SLAContract"]["evm"]["bytecode"]["object"]
            
            contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            nonce = w3.eth.get_transaction_count(from_addr)
            chain_id = int(w3.eth.chain_id)
            
            tx = contract.constructor().build_transaction({
                "from": from_addr,
                "chainId": chain_id,
                "nonce": nonce,
                "gas": 6_000_000,
                "gasPrice": w3.eth.gas_price,
            })
            
            signed = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            logger_bc.info(f"[BC-NSSMF] txHash={tx_hash.hex()}")
            
            # PATCH CIRÚRGICO: Retornar imediatamente sem bloquear
            return {
                "status": "submitted",
                "operation": "DEPLOY",
                "txHash": tx_hash.hex()
            }
            # Retornar formato esperado pelo Phase 08
        except HTTPException:
            raise
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("contract.deployed", False)
            span.set_attribute("contract.error", str(e))
            logger_bc.error(f"Erro ao fazer deploy: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erro ao fazer deploy do contrato: {str(e)}")
