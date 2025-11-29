"""
Decision Engine - Motor de Decisão
Consome I-01 (gRPC), I-02, I-03 e gera decisões AC/RENEG/REJ
"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import threading
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decision_maker import DecisionMaker
from rule_engine import RuleEngine
from kafka_consumer import DecisionConsumer
from kafka_producer import DecisionProducer
from kafka_producer_retry import DecisionProducerWithRetry
from grpc_server import serve as serve_grpc

# Novos módulos integrados
from service import DecisionService
from models import DecisionResult
from config import config

# OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Usar endpoint configurável do OTLP Collector (opcional em modo DEV)
otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"
if otlp_enabled:
    try:
        otlp_endpoint = os.getenv("OTLP_ENDPOINT_GRPC", config.otlp_endpoint_grpc)
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
    except Exception as e:
        print(f"⚠️ OTLP não disponível, continuando sem observabilidade: {e}")

# Variável global para thread do gRPC
grpc_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager para inicializar e finalizar recursos"""
    # Startup
    global grpc_thread
    import sys
    import logging
    import time
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)
    
    # Logs explícitos
    logger.info("=" * 60)
    logger.info("🚀 LIFESPAN STARTUP - Starting gRPC server thread...")
    logger.info("=" * 60)
    print("=" * 60, file=sys.stderr, flush=True)
    print("🚀 LIFESPAN STARTUP - Starting gRPC server thread...", file=sys.stderr, flush=True)
    print("=" * 60, file=sys.stderr, flush=True)
    
    try:
        grpc_thread = threading.Thread(target=serve_grpc, daemon=True, name="gRPC-Server")
        grpc_thread.start()
        
        # Aguardar um pouco para verificar se iniciou
        time.sleep(2)
        
        logger.info("✅ gRPC server thread started successfully")
        logger.info(f"   Thread name: {grpc_thread.name}")
        logger.info(f"   Thread alive: {grpc_thread.is_alive()}")
        print("✅ gRPC server thread started successfully", file=sys.stderr, flush=True)
        print(f"   Thread name: {grpc_thread.name}", file=sys.stderr, flush=True)
        print(f"   Thread alive: {grpc_thread.is_alive()}", file=sys.stderr, flush=True)
    except Exception as e:
        logger.error(f"❌ ERROR starting gRPC server: {e}", exc_info=True)
        print(f"❌ ERROR starting gRPC server: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 LIFESPAN SHUTDOWN - Shutting down gRPC server...")
    logger.info("=" * 60)
    print("=" * 60, file=sys.stderr, flush=True)
    print("🛑 LIFESPAN SHUTDOWN - Shutting down gRPC server...", file=sys.stderr, flush=True)
    print("=" * 60, file=sys.stderr, flush=True)

app = FastAPI(
    title="TriSLA Decision Engine",
    version="1.0.0",
    lifespan=lifespan
)

# NÃO instrumentar ainda - será feito DEPOIS de todas as rotas serem definidas

# Inicializar componentes
rule_engine = RuleEngine()
decision_maker = DecisionMaker(rule_engine)  # Mantido para compatibilidade

# Novo serviço integrado (usa SEM-CSMF, ML-NSMF, BC-NSSMF)
decision_service = DecisionService()

# DecisionConsumer e Producer podem ser None se Kafka estiver desabilitado
kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
if kafka_enabled:
    decision_consumer = DecisionConsumer(decision_maker)
    # Usar producer com retry se habilitado
    USE_KAFKA_RETRY = os.getenv("USE_KAFKA_RETRY", "true").lower() == "true"
    if USE_KAFKA_RETRY:
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")
        decision_producer = DecisionProducerWithRetry(kafka_servers)
    else:
        decision_producer = DecisionProducer()
else:
    decision_consumer = None
    decision_producer = None
    print("ℹ️ Decision Engine: Modo DEV - Kafka desabilitado (KAFKA_ENABLED=false)")

# Fallback: Iniciar gRPC quando o módulo é importado
# Isso garante que o servidor gRPC inicie mesmo se o lifespan não funcionar
def start_grpc_fallback():
    """Inicia gRPC quando o módulo é importado (fallback)"""
    global grpc_thread
    if grpc_thread is None or not grpc_thread.is_alive():
        try:
            import sys
            import logging
            import os
            import time
            import traceback
            
            # Configurar logging primeiro
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout), logging.StreamHandler(sys.stderr)],
                force=True
            )
            logger = logging.getLogger(__name__)
            
            # Criar arquivo de log para debug
            log_file = os.getenv("GRPC_LOG_FILE", "/tmp/grpc_fallback.log")
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                with open(log_file, "a") as f:
                    f.write(f"[{time.time()}] Starting gRPC server (fallback method)...\n")
                    f.flush()
            except Exception as e:
                logger.warning(f"Could not write to log file {log_file}: {e}")
            
            # Logs em múltiplos lugares
            logger.info("=" * 60)
            logger.info("🔄 Starting gRPC server (fallback method)...")
            logger.info("=" * 60)
            print("🔄 Starting gRPC server (fallback method)...", file=sys.stderr, flush=True)
            print("🔄 Starting gRPC server (fallback method)...", file=sys.stdout, flush=True)
            
            # Verificar se serve_grpc está disponível
            try:
                from grpc_server import serve as serve_grpc_func
            except Exception as e:
                logger.error(f"Could not import serve_grpc: {e}")
                raise
            
            # Criar thread com tratamento de erro
            def serve_with_error_handling():
                try:
                    serve_grpc_func()
                except Exception as e:
                    logger.error(f"Error in gRPC server thread: {e}", exc_info=True)
                    try:
                        with open(log_file, "a") as f:
                            f.write(f"[{time.time()}] ERROR in gRPC thread: {e}\n")
                            traceback.print_exc(file=f)
                    except Exception:
                        pass
            
            grpc_thread = threading.Thread(
                target=serve_with_error_handling,
                daemon=True,
                name="gRPC-Server-Fallback"
            )
            grpc_thread.start()
            
            time.sleep(3)  # Aguardar mais tempo para iniciar
            
            # Verificar se iniciou
            thread_alive = grpc_thread.is_alive()
            logger.info(f"Thread started: alive={thread_alive}")
            try:
                with open(log_file, "a") as f:
                    f.write(f"[{time.time()}] Thread started: alive={thread_alive}\n")
                    f.flush()
            except Exception:
                pass
            
            if thread_alive:
                logger.info("✅ gRPC server started (fallback)")
                print("✅ gRPC server started (fallback)", file=sys.stderr, flush=True)
                print("✅ gRPC server started (fallback)", file=sys.stdout, flush=True)
            else:
                logger.warning("⚠️ gRPC thread started but is not alive")
                print("⚠️ gRPC thread started but is not alive", file=sys.stderr, flush=True)
        except Exception as e:
            import sys
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"⚠️ Could not start gRPC (fallback): {e}", exc_info=True)
            print(f"⚠️ Could not start gRPC (fallback): {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            # Escrever erro em arquivo
            try:
                log_file = os.getenv("GRPC_LOG_FILE", "/tmp/grpc_fallback.log")
                with open(log_file, "a") as f:
                    f.write(f"[{time.time()}] ERROR: {e}\n")
                    traceback.print_exc(file=f)
            except Exception:
                pass

# Tentar iniciar gRPC imediatamente (fallback)
try:
    start_grpc_fallback()
except Exception as e:
    import sys
    print(f"Failed to start gRPC fallback during import: {e}", file=sys.stderr, flush=True)


@app.get("/health")
async def health():
    """Health check endpoint"""
    kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
    kafka_status = "enabled" if kafka_enabled else "offline"
    
    return {
        "status": "healthy",
        "module": "decision-engine",
        "kafka": kafka_status,
        "rule_engine": "ready" if rule_engine else "not_ready",
        "decision_service": "ready" if decision_service else "not_ready",
        "grpc_thread": "alive" if grpc_thread and grpc_thread.is_alive() else "not_running"
    }


@app.get("/debug/grpc", include_in_schema=True)
async def debug_grpc():
    """Endpoint de debug para verificar status do servidor gRPC"""
    global grpc_thread
    import socket
    
    # Verificar thread
    thread_status = {
        "exists": grpc_thread is not None,
        "alive": grpc_thread.is_alive() if grpc_thread else False,
        "name": grpc_thread.name if grpc_thread else None
    }
    
    # Verificar porta
    port = int(os.getenv("GRPC_PORT", "50051"))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('localhost', port))
        s.close()
        port_status = "OPEN" if result == 0 else "CLOSED"
    except Exception as e:
        port_status = f"ERROR: {e}"
    
    return {
        "grpc_thread": thread_status,
        "port": {
            "number": port,
            "status": port_status
        },
        "fallback_executed": grpc_thread is not None
    }


@app.post("/api/v1/decide")
async def make_decision(context: dict):
    """
    Faz decisão baseada em contexto (endpoint compatível)
    Mantido para compatibilidade com código existente
    """
    with tracer.start_as_current_span("make_decision") as span:
        decision = await decision_maker.decide(context)
        
        # Enviar para BC-NSSMF (I-04) e SLA-Agents (I-05)
        await decision_producer.send_to_bc_nssmf(decision)  # I-04
        await decision_producer.send_to_sla_agents(decision)  # I-05
        
        span.set_attribute("decision.action", decision.get("action"))
        return decision


@app.post("/api/v1/decide/intent/{intent_id}", response_model=DecisionResult)
async def decide_intent(intent_id: str, nest_id: Optional[str] = None, context: Optional[dict] = None):
    """
    Novo endpoint integrado para decisão de intent/NEST
    Orquestra SEM-CSMF → ML-NSMF → BC-NSSMF
    """
    with tracer.start_as_current_span("decide_intent_integrated") as span:
        span.set_attribute("intent.id", intent_id)
        if nest_id:
            span.set_attribute("nest.id", nest_id)
        
        # Processar decisão usando o serviço integrado
        decision_result = await decision_service.process_decision(
            intent_id=intent_id,
            nest_id=nest_id,
            context=context
        )
        
        span.set_attribute("decision.action", decision_result.action.value)
        span.set_attribute("decision.confidence", decision_result.confidence)
        
        return decision_result


@app.get("/api/v1/status")
async def get_status():
    """Status do Decision Engine e componentes integrados"""
    status = {
        "status": "healthy",
        "module": "decision-engine",
        "integrations": {
            "sem_csmf": {
                "url": config.sem_csmf_http_url,
                "grpc_endpoint": config.sem_csmf_grpc_endpoint
            },
            "ml_nsmf": {
                "url": config.ml_nsmf_http_url
            },
            "bc_nssmf": {
                "rpc_url": config.bc_nssmf_rpc_url,
                "contract_path": config.bc_nssmf_contract_path
            },
            "otlp": {
                "endpoint": config.otlp_endpoint
            }
        }
    }
    return status


# AGORA instrumentar FastAPI APÓS todas as rotas serem definidas
# Isso garante que todas as rotas, incluindo /debug/grpc, sejam registradas antes da instrumentação
FastAPIInstrumentor.instrument_app(app)


if __name__ == "__main__":
    import uvicorn
    # Servidor gRPC será iniciado via lifespan ou fallback
    uvicorn.run(app, host="0.0.0.0", port=8082)

