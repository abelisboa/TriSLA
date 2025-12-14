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
import threading
import logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nasp_client import NASPClient
from metrics_collector import MetricsCollector
from action_executor import ActionExecutor
from controllers.nsi_controller import NSIController
from controllers.nsi_watch_controller import start_nsi_watch

logger = logging.getLogger(__name__)

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
nsi_controller = NSIController()  # FASE C3-B2: Controller real de NSI

# FASE C3-C1.1-FIX: Bootstrap robusto e verificável do NSI Watch Controller
@app.on_event("startup")
async def startup_event():
    """
    Inicia watch controller no startup
    FASE C3-C1.1-FIX: Bootstrap robusto com tratamento de erro explícito
    """
    try:
        logger.info("[BOOTSTRAP] Starting NSI Watch Controller")
        logger.info("[BOOTSTRAP] Importing start_nsi_watch from controllers.nsi_watch_controller")
        
        # Import explícito (já feito no topo, mas log para evidência)
        from controllers.nsi_watch_controller import start_nsi_watch
        
        logger.info("[BOOTSTRAP] Starting NSI Watch Controller in daemon thread")
        watch_thread = threading.Thread(target=start_nsi_watch, daemon=True, name="NSI-Watch-Thread")
        watch_thread.start()
        
        # Aguardar um momento para verificar se a thread iniciou sem erro imediato
        import asyncio
        await asyncio.sleep(0.5)
        
        if not watch_thread.is_alive():
            raise RuntimeError("NSI Watch Controller thread died immediately after start")
        
        logger.info("[BOOTSTRAP] NSI Watch Controller STARTED")
        logger.info(f"[BOOTSTRAP] Watch thread is alive: {watch_thread.is_alive()}")
        logger.info(f"[BOOTSTRAP] Watch thread name: {watch_thread.name}")
        
    except Exception as e:
        logger.exception("[BOOTSTRAP] FAILED to start NSI Watch Controller")
        logger.error(f"[BOOTSTRAP] Error details: {type(e).__name__}: {str(e)}")
        raise RuntimeError("NSI Controller bootstrap failed") from e


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


@app.post("/api/v1/nsi/instantiate")
async def instantiate_nsi(nsi_spec: dict):
    """
    Instancia um Network Slice Instance (NSI) no Kubernetes
    FASE C3-B2: Criação real de slice sem simulação
    
    Args:
        nsi_spec: Especificação do NSI contendo:
            - nsiId: ID do NSI (opcional, será gerado se não fornecido)
            - tenantId: ID do tenant
            - serviceProfile: URLLC | eMBB | mMTC
            - nssai: {sst, sd?}
            - sla: {latency, reliability, availability, throughput}
    
    Returns:
        NSI criado com status
    """
    import logging
    logger = logging.getLogger(__name__)
    
    with tracer.start_as_current_span("instantiate_nsi") as span:
        try:
            logger.info(f"🔷 [NSI] Recebida requisição de instanciação: {nsi_spec.get('nsiId', 'auto')}")
            
            # Criar NSI
            created_nsi = nsi_controller.create_nsi(nsi_spec)
            
            span.set_attribute("nsi.id", created_nsi.get("spec", {}).get("nsiId"))
            span.set_attribute("nsi.phase", created_nsi.get("status", {}).get("phase"))
            
            logger.info(f"✅ [NSI] NSI instanciado: {created_nsi.get('spec', {}).get('nsiId')}")
            
            return {
                "success": True,
                "nsi": created_nsi,
                "message": "NSI instantiated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ [NSI] Erro ao instanciar NSI: {e}", exc_info=True)
            span.record_exception(e)
            from opentelemetry import trace as otel_trace
            span.set_status(otel_trace.Status(otel_trace.StatusCode.ERROR, str(e)))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to instantiate NSI: {str(e)}"
            }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)

