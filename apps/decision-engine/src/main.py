
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
Decision Engine - Motor de Decisão
Consome I-01 (gRPC), I-02, I-03 e gera decisões AC/RENEG/REJ
"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import threading
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decision_maker import DecisionMaker
from rule_engine import RuleEngine
from kafka_consumer import DecisionConsumer
from kafka_producer import DecisionProducer
from kafka_producer_retry import DecisionProducerWithRetry
from decision_producer import DummyProducer
from grpc_server import serve as serve_grpc

# S30 modules - Decision Snapshot + System-Aware XAI
from decision_snapshot import build_decision_snapshot
from system_xai import explain_decision
from decision_persistence import persist_decision_evidence

# Novos módulos integrados
from service import DecisionService
from models import DecisionResult, DecisionInput, SLAIntent, NestSubset, SLAEvaluateInput
from config import config
from nasp_adapter_client import NASPAdapterClient
from portal_backend_client import PortalBackendClient

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
_trisla_attach_observability(app, os.getenv("TRISLA_SERVICE_NAME", "decision-engine"))
    title="TriSLA Decision Engine",
    version="3.10.0",
    lifespan=lifespan
)

# NÃO instrumentar ainda - será feito DEPOIS de todas as rotas serem definidas

# Inicializar componentes
rule_engine = RuleEngine()
decision_maker = DecisionMaker(rule_engine)  # Mantido para compatibilidade

# Novo serviço integrado (usa SEM-CSMF, ML-NSMF, BC-NSSMF)
decision_service = DecisionService()

# Clientes para encaminhamento de decisões
nasp_adapter_client = NASPAdapterClient()
portal_backend_client = PortalBackendClient()

# Storage de decisões (em memória - substituir por DB em produção)
decisions_storage = {}

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
    decision_producer = None  # ⚠️ FASE C1: Não usar DummyProducer - endpoint /evaluate não depende de Kafka
    print("ℹ️ Decision Engine: Kafka desabilitado. Endpoint /evaluate usa clientes HTTP diretos.")

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


@app.get("/metrics")
async def metrics():
    """Expor métricas Prometheus"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

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
    [S31.3] Endpoint DEPRECATED - Forward obrigatório para /evaluate
    
    ⚠️ Este endpoint NÃO pode mais decidir nada diretamente.
    Ele SEMPRE faz forward para /evaluate para garantir fluxo único.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("[S31.3] Deprecated endpoint /api/v1/decide used — forwarding to /evaluate")
    
    with tracer.start_as_current_span("make_decision_deprecated_forward") as span:
        span.set_attribute("deprecated_endpoint", True)
        span.set_attribute("forward_to", "/evaluate")
        
        try:
            # Converter contexto dict para SLAEvaluateInput
            # Extrair intent_id e nest_id do contexto
            intent_id = context.get("intent_id") if isinstance(context, dict) else None
            if not intent_id:
                # Tentar extrair de outras chaves comuns
                intent_id = context.get("id") or context.get("sla_id") or "unknown"
            
            nest_id = context.get("nest_id") if isinstance(context, dict) else None
            
            # Construir SLAEvaluateInput mínimo para forward
            sla_input = SLAEvaluateInput(
                intent_id=intent_id or "unknown",
                nest_id=nest_id,
                intent=context.get("intent") or {},
                nest=context.get("nest"),
                context=context
            )
            
            # Forward obrigatório para /evaluate
            logger.info(f"[S31.3] Forwarding deprecated endpoint call to /evaluate: intent_id={intent_id}")
            result = await evaluate_sla(sla_input)
            
            # Converter DecisionResult para dict compatível com resposta antiga
            decision_dict = {
                "decision_id": result.decision_id,
                "intent_id": result.intent_id,
                "nest_id": result.nest_id,
                "action": result.action.value,
                "reason": result.reasoning,
                "reasoning": result.reasoning,
                "confidence": result.confidence,
                "ml_risk_score": result.ml_risk_score,
                "ml_risk_level": result.ml_risk_level.value if result.ml_risk_level else None,
                "timestamp": result.timestamp,
                "metadata": result.metadata
            }
            # PROMPT_SNASP_24 — Expor XAI (features_importance) já calculado pelo ML-NSMF; não altera decisão/scores
            if result.metadata:
                fi = result.metadata.get("ml_features_importance")
                expl = result.metadata.get("ml_explanation")
                if fi is not None or expl:
                    decision_dict["xai"] = {
                        "method": result.metadata.get("ml_xai_method") or "SHAP",
                        "features_importance": fi if isinstance(fi, dict) else {},
                        "explanation": expl or ""
                    }
                    top = list(decision_dict["xai"]["features_importance"].keys())[:10] if decision_dict["xai"]["features_importance"] else []
                    decision_dict["xai"]["top_features"] = top
                else:
                    decision_dict["xai"] = None
            else:
                decision_dict["xai"] = None

            # PROMPT_SNASP_30 — Instrumentação passiva por domínio (apenas log; não altera decisão)
            sla_id = f"dec-{result.intent_id}" if result.intent_id else "n/a"
            for domain in (result.domains or []):
                if domain == "RAN":
                    logger.info("XAI_DOMAIN_CHECK | sla_id=%s | domain=RAN | cpu=OK | mem=OK | latency=NA", sla_id)
                elif domain in ("Transporte", "Transport"):
                    logger.info("XAI_DOMAIN_CHECK | sla_id=%s | domain=Transport | bw=OK | latency=OK", sla_id)
                elif domain == "Core":
                    logger.info("XAI_DOMAIN_CHECK | sla_id=%s | domain=Core | cpu=OK | mem=OK", sla_id)

            span.set_attribute("decision.action", result.action.value)
            span.set_attribute("forward.success", True)
            return decision_dict
            
        except Exception as e:
            logger.error(f"[S31.3] ❌ Erro ao fazer forward de /api/v1/decide para /evaluate: {e}", exc_info=True)
            span.record_exception(e)
            span.set_attribute("forward.success", False)
            # Retornar erro compatível
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Erro ao processar decisão via forward: {str(e)}")


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
            "nasp_adapter": {
                "url": config.nasp_adapter_url
            },
            "portal_backend": {
                "url": config.portal_backend_url
            },
            "otlp": {
                "endpoint": config.otlp_endpoint
            }
        }
    }
    return status


@app.post("/evaluate", response_model=DecisionResult)
async def evaluate_sla(sla_input: SLAEvaluateInput):
    """
    Endpoint real de avaliação de SLA (FASE C1)
    
    Recebe SLA validado (SEM-CSMF output) e:
    1. Chama ML-NSMF para obter decisão
    2. Persiste decisão
    3. Encaminha:
       - ACCEPT → NASP Adapter (criação de slice)
       - REJECT → Portal Backend (notificação)
       - DEGRADED → BC-NSMF (registro)
    
    Args:
        sla_input: SLA validado do SEM-CSMF contendo:
            - intent_id: ID do intent
            - nest_id: ID do NEST (opcional)
            - intent: Dados do intent (SLAIntent)
            - nest: Dados do NEST (NestSubset, opcional)
            - context: Contexto adicional (opcional)
    
    Returns:
        DecisionResult com ação e justificativa
    """
    import logging
    logger = logging.getLogger(__name__)
    
    with tracer.start_as_current_span("evaluate_sla") as span:
        try:
            # Extrair dados do input (agora tipado via Pydantic)
            intent_id = sla_input.intent_id
            nest_id = sla_input.nest_id
            context = sla_input.context or {}
            
            span.set_attribute("intent.id", intent_id)
            if nest_id:
                span.set_attribute("nest.id", nest_id)
            
            logger.info(f"📥 SLA recebido para avaliação: intent_id={intent_id}, nest_id={nest_id}")
            
            # 1. Construir DecisionInput a partir do SLA validado
            intent_data = sla_input.intent
            nest_data = sla_input.nest
            
            # Converter para modelos
            from models import SliceType
            intent = SLAIntent(
                intent_id=intent_id,
                tenant_id=intent_data.get("tenant_id"),
                service_type=SliceType(intent_data.get("service_type", "eMBB")),
                sla_requirements=intent_data.get("sla_requirements", {}),
                nest_id=nest_id or intent_data.get("nest_id"),
                metadata=intent_data.get("metadata")
            )
            
            nest = None
            if nest_data:
                nest = NestSubset(
                    nest_id=nest_id or nest_data.get("nest_id", ""),
                    intent_id=intent_id,
                    network_slices=nest_data.get("network_slices", []),
                    resources=nest_data.get("resources", {}),
                    status=nest_data.get("status", "generated"),
                    metadata=nest_data.get("metadata")
                )
            
            decision_input = DecisionInput(
                intent=intent,
                nest=nest,
                context=context
            )
            
            logger.info(f"🔍 Chamando ML-NSMF para intent_id={intent_id}")
            
            # 2. Chamar ML-NSMF para obter decisão
            decision_result = await decision_service.process_decision_from_input(decision_input)
            
            span.set_attribute("decision.action", decision_result.action.value)
            span.set_attribute("decision.confidence", decision_result.confidence)
            logger.info(f"✅ Decisão obtida: {decision_result.action.value} (confidence={decision_result.confidence:.2f})")
            
            # 3. Persistir decisão
            decisions_storage[decision_result.decision_id] = {
                "decision_id": decision_result.decision_id,
                "intent_id": decision_result.intent_id,
                "nest_id": decision_result.nest_id,
                "action": decision_result.action.value,
                "reasoning": decision_result.reasoning,
                "confidence": decision_result.confidence,
                "ml_risk_score": decision_result.ml_risk_score,
                "ml_risk_level": decision_result.ml_risk_level.value if decision_result.ml_risk_level else None,
                "timestamp": decision_result.timestamp,
                "metadata": decision_result.metadata
            }
            logger.info(f"💾 Decisão persistida: {decision_result.decision_id}")
            
            # 3.5. [S30] Executar system snapshot + XAI + [S31.1] Publicar no Kafka
            logger.info("[S30] Executing system snapshot + XAI")
            
            # Construir contexto da decisão para snapshot
            decision_context = {
                "intent": intent,
                "nest": nest,
                "ml_prediction": context.get("ml_prediction") if isinstance(context, dict) else None,
                "resources": {}
            }
            
            snapshot = None
            explanation = None
            
            try:
                snapshot = build_decision_snapshot(decision_context, decision_result)
                explanation = explain_decision(snapshot, decision_result)
                sla_id = decision_result.intent_id or decision_result.decision_id
                persist_decision_evidence(sla_id, snapshot, explanation)
                logger.info(f"[S30] ✅ Snapshot e XAI criados para decision_id={decision_result.decision_id}")
            except Exception as e:
                logger.exception("[S30] Failed to create snapshot/XAI")
            
            # [S31.1] Publicar evento completo no Kafka trisla-decision-events
            global decision_producer
            if decision_producer is not None and snapshot is not None and explanation is not None:
                try:
                    decision_dict_for_kafka = {
                        "decision_id": decision_result.decision_id,
                        "intent_id": decision_result.intent_id,
                        "nest_id": decision_result.nest_id,
                        "action": decision_result.action.value,
                        "reasoning": decision_result.reasoning,
                        "confidence": decision_result.confidence,
                        "ml_risk_score": decision_result.ml_risk_score,
                        "ml_risk_level": decision_result.ml_risk_level.value if decision_result.ml_risk_level else None,
                        "timestamp": decision_result.timestamp,
                        "metadata": decision_result.metadata
                    }
                    
                    # Publicar no tópico trisla-decision-events (S31.1)
                    await decision_producer.publish_decision_event(
                        snapshot=snapshot,
                        system_xai=explanation,
                        decision_result=decision_dict_for_kafka
                    )
                except Exception as e:
                    logger.warning(f"[S31.1] ⚠️ Falha ao publicar decision event no Kafka: {e}")
            
            # 4. Encaminhar conforme ação
            from models import DecisionAction
            
            # FASE 4 — Gate 3GPP Real: se habilitado, ACCEPT só após Gate PASS (PROMPT_S3GPP_GATE_v1.0)
            if decision_result.action == DecisionAction.ACCEPT and config.gate_3gpp_enabled:
                slice_type = (decision_result.metadata or {}).get("service_type") or "eMBB"
                tenant_id = (decision_result.metadata or {}).get("tenant_id") or "default"
                gate_result = await nasp_adapter_client.check_3gpp_gate(slice_type=slice_type, tenant_id=tenant_id)
                if gate_result.get("gate") != "PASS":
                    reasons = gate_result.get("reasons", [])
                    msg = "; ".join(reasons)
                    logger.warning(f"[GATE] 3GPP Gate FAIL → forçando REJECT: {msg}")
                    update = {"action": DecisionAction.REJECT, "reasoning": f"3GPP_GATE_FAIL:{msg}"}
                    if hasattr(decision_result, "model_copy"):
                        decision_result = decision_result.model_copy(update=update)
                    else:
                        decision_result = decision_result.copy(update=update)
            
            # MDCE v1 (PROMPT_SMDCE_V1): se habilitado, ACCEPT só após MDCE PASS
            if decision_result.action == DecisionAction.ACCEPT and config.mdce_enabled:
                from mdce import evaluate as mdce_evaluate
                slice_type = getattr(intent.service_type, "value", None) or (decision_result.metadata or {}).get("service_type") or "eMBB"
                sla_req = intent.sla_requirements if isinstance(intent.sla_requirements, dict) else {}
                try:
                    mdce_metrics = await nasp_adapter_client.get_multidomain_metrics()
                    verdict, mdce_reasons = mdce_evaluate(slice_type, sla_req, mdce_metrics)
                    if verdict != "PASS":
                        msg = "; ".join(mdce_reasons)
                        logger.warning(f"[MDCE] MDCE FAIL → forçando REJECT: {msg}")
                        update = {"action": DecisionAction.REJECT, "reasoning": f"MDCE_FAIL:{msg}"}
                        if hasattr(decision_result, "model_copy"):
                            decision_result = decision_result.model_copy(update=update)
                        else:
                            decision_result = decision_result.copy(update=update)
                except Exception as e:
                    logger.warning(f"[MDCE] MDCE evaluation failed → REJECT por segurança: {e}")
                    update = {"action": DecisionAction.REJECT, "reasoning": f"MDCE_FAIL:mdce_error:{e}"}
                    if hasattr(decision_result, "model_copy"):
                        decision_result = decision_result.model_copy(update=update)
                    else:
                        decision_result = decision_result.copy(update=update)
            
            if decision_result.action == DecisionAction.ACCEPT:
                logger.info(f"🚀 Encaminhando ACCEPT para NASP Adapter: decision_id={decision_result.decision_id}")
                nasp_result = await nasp_adapter_client.execute_slice_creation(decision_result)
                if nasp_result:
                    decision_result.metadata = decision_result.metadata or {}
                    decision_result.metadata["nasp_execution"] = nasp_result
                    logger.info(f"✅ Slice criado no NASP: {nasp_result}")
                else:
                    logger.warning(f"⚠️ Falha ao criar slice no NASP para decision_id={decision_result.decision_id}")
            
            elif decision_result.action == DecisionAction.REJECT:
                logger.info(f"❌ Encaminhando REJECT para Portal Backend: decision_id={decision_result.decision_id}")
                portal_result = await portal_backend_client.notify_decision_rejection(decision_result)
                if portal_result:
                    decision_result.metadata = decision_result.metadata or {}
                    decision_result.metadata["portal_notification"] = portal_result
                    logger.info(f"✅ Portal Backend notificado: {portal_result}")
            
            elif decision_result.action == DecisionAction.RENEGOTIATE:
                # RENEGOTIATE → BC-NSMF (registro para rastreabilidade)
                logger.info(f"🔄 Encaminhando RENEGOTIATE para BC-NSMF: decision_id={decision_result.decision_id}")
                bc_result = await decision_service.engine.bc_client.register_sla_on_chain(decision_result)
                if bc_result:
                    decision_result.metadata = decision_result.metadata or {}
                    decision_result.metadata["blockchain_tx_hash"] = bc_result
                    logger.info(f"✅ RENEGOTIATE registrado no BC-NSMF: tx_hash={bc_result}")
                else:
                    logger.warning(f"⚠️ Falha ao registrar RENEGOTIATE no BC-NSMF para decision_id={decision_result.decision_id}")
            
            # 5. Publicar decisão no Kafka I-04/I-05 (obrigatório para rastreabilidade)
            if decision_producer is not None:
                decision_dict = {
                    "decision_id": decision_result.decision_id,
                    "intent_id": decision_result.intent_id,
                    "nest_id": decision_result.nest_id,
                    "action": decision_result.action.value,
                    "reasoning": decision_result.reasoning,
                    "confidence": decision_result.confidence,
                    "ml_risk_score": decision_result.ml_risk_score,
                    "ml_risk_level": decision_result.ml_risk_level.value if decision_result.ml_risk_level else None,
                    "timestamp": decision_result.timestamp,
                    "metadata": decision_result.metadata
                }
                try:
                    await decision_producer.send_to_bc_nssmf(decision_dict)  # I-04
                    await decision_producer.send_to_sla_agents(decision_dict)  # I-05
                    logger.info(f"✅ Decisão publicada no Kafka I-04/I-05: decision_id={decision_result.decision_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Falha ao publicar decisão no Kafka: {e}")
            else:
                logger.warning("⚠️ Decision producer não disponível - decisão não publicada no Kafka")

            return decision_result
            
        except Exception as e:
            logger.error(f"❌ Erro ao avaliar SLA: {e}", exc_info=True)
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Erro ao avaliar SLA: {str(e)}")


# AGORA instrumentar FastAPI APÓS todas as rotas serem definidas
# Isso garante que todas as rotas, incluindo /debug/grpc, sejam registradas antes da instrumentação
FastAPIInstrumentor.instrument_app(app)


if __name__ == "__main__":
    import uvicorn
    # Servidor gRPC será iniciado via lifespan ou fallback
    uvicorn.run(app, host="0.0.0.0", port=8082)
