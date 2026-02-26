
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


# ==============================
# TRI-SLA HARDENING HELPERS
# ==============================
import re as _re

_RFC1123_RE = _re.compile(r'[^a-z0-9\-\.]+')

def _to_rfc1123_name(name: str) -> str:
    """
    Normaliza nomes para RFC1123 (K8s metadata.name):
    - lowercase
    - permite [a-z0-9-\.]
    - remove caracteres inválidos
    - garante começar/terminar com alfanumérico
    """
    if not name:
        return "nsi"
    s = str(name).strip().lower()
    s = _RFC1123_RE.sub("-", s)
    s = _re.sub(r'[-\.]+', '-', s)
    s = s.strip('-.')
    if not s:
        s = "nsi"
    return s

def _normalize_latency(val):
    """
    CRD espera spec.sla.latency como string.
    Aceita:
      - int/float (assume ms) -> "10ms"
      - "10" -> "10ms"
      - "10ms" -> "10ms"
      - "0.5s" mantém
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        # assume ms
        if float(val).is_integer():
            return f"{int(val)}ms"
        return f"{val}ms"
    s = str(val).strip()
    if not s:
        return None
    # se for só número, assume ms
    if _re.fullmatch(r'[0-9]+(\.[0-9]+)?', s):
        if s.endswith(".0"):
            s = s[:-2]
        return f"{s}ms"
    return s

def _normalize_sla(sla: dict) -> dict:
    """
    CRD schema (observado):
      sla:
        availability: number
        reliability: number
        latency: string
    Remove campos desconhecidos e normaliza aliases como latency_max_ms.
    """
    if not isinstance(sla, dict):
        return {}
    out = {}

    # aliases comuns
    if "latency" in sla:
        out["latency"] = _normalize_latency(sla.get("latency"))
    elif "latency_max_ms" in sla:
        out["latency"] = _normalize_latency(sla.get("latency_max_ms"))

    if "availability" in sla:
        try:
            out["availability"] = float(sla.get("availability"))
        except Exception:
            pass
    if "reliability" in sla:
        try:
            out["reliability"] = float(sla.get("reliability"))
        except Exception:
            pass

    # remove None
    return {k: v for k, v in out.items() if v is not None}

def _sanitize_nsi_payload(nsi_spec: dict) -> dict:
    """
    Remove campos não suportados, aplica aliases e garante conformidade CRD.
    """
    if not isinstance(nsi_spec, dict):
        return {}
    # aliases (snake_case -> camelCase)
    nsi_id = nsi_spec.get("nsiId") or nsi_spec.get("nsi_id") or nsi_spec.get("intent_id")
    service_profile = nsi_spec.get("serviceProfile") or nsi_spec.get("service_profile") or nsi_spec.get("service_type")
    tenant_id = nsi_spec.get("tenantId") or nsi_spec.get("tenant_id") or "default"

    # nssai: manter apenas sst/sd se existir
    nssai = nsi_spec.get("nssai") or {}
    if not isinstance(nssai, dict):
        nssai = {}
    clean_nssai = {}
    if "sst" in nssai:
        clean_nssai["sst"] = nssai.get("sst")
    else:
        clean_nssai["sst"] = 1
    if "sd" in nssai and nssai.get("sd"):
        clean_nssai["sd"] = str(nssai.get("sd"))

    sla = nsi_spec.get("sla") or nsi_spec.get("sla_requirements") or {}
    clean_sla = _normalize_sla(sla)

    # gera id se faltar
    if not nsi_id:
        import uuid
        nsi_id = f"nsi-{uuid.uuid4().hex[:8]}"

    # RFC1123
    nsi_id = _to_rfc1123_name(nsi_id)

    out = {
        "nsiId": nsi_id,
        "serviceProfile": service_profile or "eMBB",
        "tenantId": tenant_id,
        "nssai": clean_nssai,
        "sla": clean_sla,
    }

    # suporte a reserveOnly (cap accounting TTL tests)
    if nsi_spec.get("_reserveOnly") is True:
        out["_reserveOnly"] = True

    return out

def _span_set(span, k, v):
    """
    Evita erro do OpenTelemetry com NoneType.
    """
    try:
        if v is None:
            return
        span.set_attribute(k, v)
    except Exception:
        # nunca quebrar o fluxo por observabilidade
        return
# ==============================
# END HARDENING HELPERS
# ==============================


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
_trisla_attach_observability(app, os.getenv("TRISLA_SERVICE_NAME", "nasp-adapter"))
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
        _span_set(span, "metrics.source", "nasp_real")
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
        _span_set(span, "mdce.reasons_count", len(out.get("reasons", [])))
        return out


@app.post("/api/v1/nasp/actions")
async def execute_nasp_action(action: dict):
    """Executa ação real no NASP (I-07)"""
    with tracer.start_as_current_span("execute_nasp_action") as span:
        result = await action_executor.execute(action)
        _span_set(span, "action.executed", True)
        _span_set(span, "action.type", action.get("type"))
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
        _span_set(span, "sla.id", sla_id)
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
        _span_set(span, "gate.result", result.get("gate", ""))
        return result


@app.post("/api/v1/3gpp/gate")
async def post_3gpp_gate(payload: dict = None):
    """Valida pré-condições 3GPP com payload do SLA (slice_type, thresholds, etc.)."""
    with tracer.start_as_current_span("post_3gpp_gate") as span:
        result = run_gate(payload or {})
        _span_set(span, "gate.result", result.get("gate", ""))
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
            nsi_spec = _sanitize_nsi_payload(nsi_spec)
            nsi_spec.pop("status", None)
            logger.info(f"🔷 [NSI] Recebida requisição de instanciação: {nsi_spec.get('nsiId','auto')}")
            
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

            _span_set(span, "nsi.id", nsi_id)
            _span_set(span, "nsi.phase", created_nsi.get("status", {}).get("phase"))
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
