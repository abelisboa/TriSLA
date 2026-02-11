"""
NASP Adapter - Integração com NASP Real
Interface I-07 - Integração bidirecional
"""

from fastapi import FastAPI, HTTPException
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
from gate_3gpp import run_gate

logger = logging.getLogger(__name__)

# PROMPT_SMDCE_V2_CAPACITY_ACCOUNTING — Capacity Accounting (ledger + rollback + reconciler)
CAPACITY_ACCOUNTING_ENABLED = os.getenv("CAPACITY_ACCOUNTING_ENABLED", "true").lower() == "true"
RESERVATION_TTL_SECONDS = int(os.getenv("RESERVATION_TTL_SECONDS", "300"))
RECONCILE_INTERVAL_SECONDS = int(os.getenv("RECONCILE_INTERVAL_SECONDS", "60"))
_reservation_store = None


def get_reservation_store():
    """Lazy init ReservationStore (requires K8s in-cluster)."""
    global _reservation_store
    if _reservation_store is None:
        from reservation_store import ReservationStore
        _reservation_store = ReservationStore()
    return _reservation_store

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

app = FastAPI(title="TriSLA NASP Adapter", version="3.10.0")
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

        # PROMPT_SMDCE_V2 — Reconciler (TTL + orphan)
        if CAPACITY_ACCOUNTING_ENABLED and RECONCILE_INTERVAL_SECONDS > 0:
            def _reconciler_loop():
                import time
                while True:
                    try:
                        store = get_reservation_store()
                        expired = store.expire_pending(RESERVATION_TTL_SECONDS)
                        if expired:
                            logger.info("[RECONCILER] expired %d PENDING reservation(s)", expired)
                        # Orphan check: ACTIVE reservations whose nsi_id no longer exists
                        for item in store.list_active():
                            spec = (item.get("spec") or {})
                            nsi_id = spec.get("nsiId") or ""
                            if not nsi_id:
                                continue
                            try:
                                from kubernetes import client
                                from controllers.k8s_auth import load_incluster_config_with_validation
                                api_client, _, namespace, _ = load_incluster_config_with_validation()
                                co = client.CustomObjectsApi(api_client=api_client)
                                co.get_namespaced_custom_object(
                                    group="trisla.io", version="v1", namespace=namespace,
                                    plural="networksliceinstances", name=nsi_id,
                                )
                            except Exception:
                                store.mark_orphaned(spec.get("reservationId") or item.get("metadata", {}).get("name"), "nsi_not_found")
                    except Exception as e:
                        logger.warning("[RECONCILER] loop error: %s", e)
                    time.sleep(RECONCILE_INTERVAL_SECONDS)
            rec_thread = threading.Thread(target=_reconciler_loop, daemon=True, name="Capacity-Reconciler")
            rec_thread.start()
            logger.info("[BOOTSTRAP] Capacity Reconciler started (interval=%ss)", RECONCILE_INTERVAL_SECONDS)
        
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


@app.get("/api/v1/metrics/multidomain")
async def get_metrics_multidomain():
    """
    Métricas multidomínio no schema SSOT MDCE (PROMPT_SMDCE_V1).
    Retorna docs/MDCE_SCHEMA.json: core.upf.*, ran.ue.active_count, transport.rtt_p95_ms.
    Campos indisponíveis = null e reasons incluem metric_unavailable.
    """
    with tracer.start_as_current_span("get_metrics_multidomain") as span:
        out = await metrics_collector.get_multidomain()
        span.set_attribute("mdce.reasons_count", len(out.get("reasons", [])))
        return out


@app.post("/api/v1/nasp/actions")
async def execute_nasp_action(action: dict):
    """Executa ação real no NASP (I-07)"""
    with tracer.start_as_current_span("execute_nasp_action") as span:
        result = await action_executor.execute(action)
        span.set_attribute("action.executed", True)
        span.set_attribute("action.type", action.get("type"))
        return result


# PROMPT_SNASP_01 — Registro de SLA no NASP pós-ACCEPT (SSOT)
SEM_CSMF_URL = os.getenv("SEM_CSMF_URL", "http://trisla-sem-csmf.trisla.svc.cluster.local:8080")


@app.post("/api/v1/sla/register")
async def register_sla(payload: dict):
    """
    Registro idempotente de SLA no NASP (PROMPT_SNASP_01).
    Payload SSOT: sla_id, status, slice_type, template, created_at, source.
    Encaminha para SEM-CSMF POST /api/v1/intents/register.
    """
    import httpx
    with tracer.start_as_current_span("register_sla_nasp") as span:
        sla_id = payload.get("sla_id")
        if not sla_id:
            raise HTTPException(status_code=400, detail="sla_id é obrigatório")
        span.set_attribute("sla.id", sla_id)
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    f"{SEM_CSMF_URL}/api/v1/intents/register",
                    json=payload,
                )
                r.raise_for_status()
                out = r.json()
                logger.info(f"[REGISTER] SLA registrado no NASP: {sla_id}")
                return out
        except httpx.HTTPStatusError as e:
            logger.warning(f"[REGISTER] SEM-CSMF respondeu {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 400:
                raise HTTPException(status_code=400, detail=e.response.text)
            raise
        except Exception as e:
            logger.error(f"[REGISTER] Erro ao registrar SLA no NASP: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"NASP register failed: {str(e)}")


# GATE_3GPP_ENABLED: quando true, instantiate exige Gate PASS (PROMPT_S3GPP_GATE_v1.0)
GATE_3GPP_ENABLED = os.getenv("GATE_3GPP_ENABLED", "false").lower() == "true"


@app.get("/api/v1/3gpp/gate")
async def get_3gpp_gate():
    """Status geral do Gate 3GPP Real (GET). Sem payload."""
    with tracer.start_as_current_span("get_3gpp_gate") as span:
        result = run_gate(None)
        span.set_attribute("gate.result", result.get("gate", ""))
        return result


@app.post("/api/v1/3gpp/gate")
async def post_3gpp_gate(payload: dict = None):
    """Valida pré-condições 3GPP com payload do SLA (slice_type, thresholds, etc.)."""
    with tracer.start_as_current_span("post_3gpp_gate") as span:
        result = run_gate(payload or {})
        span.set_attribute("gate.result", result.get("gate", ""))
        return result


@app.post("/api/v1/nsi/instantiate")
async def instantiate_nsi(nsi_spec: dict):
    """
    Instancia um Network Slice Instance (NSI) no Kubernetes
    FASE C3-B2: Criação real de slice sem simulação
    FASE 5 (PROMPT_S3GPP_GATE): se GATE_3GPP_ENABLED=true e Gate FAIL → 409/422.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    with tracer.start_as_current_span("instantiate_nsi") as span:
        try:
            logger.info(f"🔷 [NSI] Recebida requisição de instanciação: {nsi_spec.get('nsiId', 'auto')}")
            
            # FASE 5 — Defesa em profundidade: Gate obrigatório antes de instantiate
            if GATE_3GPP_ENABLED:
                gate_result = run_gate(nsi_spec)
                if gate_result.get("gate") != "PASS":
                    reasons = gate_result.get("reasons", [])
                    msg = "; ".join(reasons)
                    logger.warning(f"[GATE] 3GPP Gate FAIL — bloqueando instantiate: {msg}")
                    raise HTTPException(
                        status_code=422,
                        detail={"gate": "FAIL", "reasons": reasons, "message": f"3GPP_GATE_FAIL:{msg}"}
                    )

            # PROMPT_SMDCE_V2 — Capacity Accounting: ledger check → reserve → instantiate → activate ou rollback (release)
            reservation_id = None
            if CAPACITY_ACCOUNTING_ENABLED:
                from capacity_accounting import ledger_check
                from cost_model import cost
                store = get_reservation_store()
                multidomain = await metrics_collector.get_multidomain()
                active = store.list_active()
                slice_type = nsi_spec.get("serviceProfile") or nsi_spec.get("service_type") or "eMBB"
                sla_req = nsi_spec.get("sla") or nsi_spec.get("sla_requirements") or {}
                result = ledger_check(multidomain, active, slice_type, sla_req)
                if not result.get("pass"):
                    reasons = result.get("reasons", ["capacity_insufficient"])
                    logger.warning("[CAPACITY] Ledger FAIL — bloqueando instantiate: %s", reasons)
                    raise HTTPException(
                        status_code=422,
                        detail={"capacity": "FAIL", "reasons": reasons, "message": "CAPACITY_ACCOUNTING:insufficient_headroom"}
                    )
                resources = cost(slice_type, sla_req)
                intent_id = nsi_spec.get("nsiId") or nsi_spec.get("intent_id") or "instantiate"
                res_obj = store.create_pending(intent_id=intent_id, slice_type=slice_type, resources_reserved=resources, ttl_seconds=RESERVATION_TTL_SECONDS)
                reservation_id = (res_obj.get("spec") or {}).get("reservationId") or res_obj.get("metadata", {}).get("name")
                logger.info("[CAPACITY] Reserva PENDING criada: %s", reservation_id)

                # PROMPT_SMDCE_V2_FINAL_CLOSE — teste TTL: reserve-only (não instancia; deixa PENDING para reconciler expirar)
                if nsi_spec.get("_reserveOnly") is True:
                    return {
                        "success": True,
                        "reservation_id": reservation_id,
                        "message": "Reservation PENDING created (reserve-only for TTL test)",
                    }

            # Criar NSI
            try:
                created_nsi = nsi_controller.create_nsi(nsi_spec)
            except Exception as e:
                if CAPACITY_ACCOUNTING_ENABLED and reservation_id:
                    get_reservation_store().release(reservation_id, reason="rollback:instantiate_failed")
                    logger.info("[CAPACITY] Rollback: reserva %s released após falha de instantiate", reservation_id)
                raise

            nsi_id = created_nsi.get("spec", {}).get("nsiId") or created_nsi.get("metadata", {}).get("name")
            if CAPACITY_ACCOUNTING_ENABLED and reservation_id:
                get_reservation_store().activate(reservation_id, nsi_id)

            span.set_attribute("nsi.id", nsi_id)
            span.set_attribute("nsi.phase", created_nsi.get("status", {}).get("phase"))
            logger.info(f"✅ [NSI] NSI instanciado: {nsi_id}")

            return {
                "success": True,
                "nsi": created_nsi,
                "message": "NSI instantiated successfully"
            }

        except HTTPException:
            raise
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

