"""
Rotas REAIS para SLA - SEM SIMULAÇÕES
Todas as respostas vêm do NASP real (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF)
"""
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from src.schemas.sla import (
    SLAInterpretRequest,
    SLASubmitRequest,
    SLAStatusResponse,
    SLAMetricsResponse,
    SLASubmitResponse,
    SLARevalidateTelemetryRequest,
    SLARevalidateTelemetryResponse,
)
from src.services.nasp import NASPService
from src.services.sla_status_telemetry import resolve_status_telemetry_snapshot
from src.services.sla_status_assurance import resolve_status_runtime_assurance
from src.services.sla_operational_summary import build_operational_summary
from src.services.admission_decision import (
    resolve_admission_context,
    resolve_admission_decision,
    resolve_runtime_lifecycle_enabled,
)
from src.services.sla_traceability import build_traceability_summary
from src.services.sla_lifecycle_success import is_sla_agent_ingest_success
from src.services.sla_revalidate_telemetry import enrich_revalidate_with_local_collect
from src.services.sla_metrics import compute_sla_metrics
from src.services.governance_metadata import (
    extract_governance_metadata,
    merge_governance_into_metadata,
)
from src.telemetry.collector import append_telemetry_csv, build_csv_row, collect_domain_metrics_async
from src.telemetry.contract_v2 import TELEMETRY_UNITS_V2
from src.observability.distributed_trace import (
    build_distributed_traceability,
    child_trace,
    inject_http_headers,
    merge_trace_into_metadata,
    new_root_trace,
    trace_from_metadata,
)
from src.utils.text_processing import corrigir_erros_ortograficos, inferir_tipo_slice, extrair_parametros_tecnicos

logger = logging.getLogger(__name__)

router = APIRouter()
nasp_service = NASPService()

_VALID_DECISIONS = {"ACCEPT", "REJECT", "RENEGOTIATE"}


async def _notify_sla_agent_pipeline(
    *,
    result: dict,
    metadata_out: dict,
    decision: str,
    lifecycle: dict,
    tenant_id: str,
) -> str:
    """Notifica SLA-Agent (HTTP) para fechar evidência E2E; opcional via env."""
    required = os.getenv("SLA_AGENT_REQUIRED_FOR_ACCEPT", "false").lower() == "true"
    url = os.getenv("SLA_AGENT_PIPELINE_INGEST_URL", "").strip()
    if decision == "ACCEPT" and required and not url:
        metadata_out["sla_agent_ingest"] = {
            "status": "ERROR",
            "reason": "SLA_AGENT_REQUIRED_FOR_ACCEPT but SLA_AGENT_PIPELINE_INGEST_URL unset",
        }
        return "ERROR"
    if not url:
        metadata_out["sla_agent_ingest"] = {
            "status": "SKIPPED",
            "reason": "SLA_AGENT_PIPELINE_INGEST_URL unset",
        }
        return "SKIPPED"
    intent_id = result.get("intent_id")
    run_slo = os.getenv("SLA_AGENT_INGEST_RUN_SLO", "false").lower() == "true"
    run_assurance = os.getenv("SLA_AGENT_INGEST_RUN_ASSURANCE", "true").lower() == "true"
    payload = {
        "intent_id": intent_id,
        "sla_id": result.get("sla_id") or intent_id,
        "nest_id": result.get("nest_id"),
        "tenant_id": result.get("tenant_id") or tenant_id,
        "decision": decision,
        "decision_source": metadata_out.get("decision_source"),
        "lifecycle_stage": "POST_SUBMIT",
        "lifecycle": dict(lifecycle),
        "module_latencies_ms": metadata_out.get("module_latencies_ms"),
        "run_slo_evaluation": run_slo,
        "run_runtime_assurance": run_assurance,
        "telemetry_snapshot": metadata_out.get("telemetry_snapshot"),
        "sla_requirements": result.get("sla_requirements"),
        "slice_type": result.get("service_type"),
        "service_type": result.get("service_type"),
        "metadata": {
            k: metadata_out.get(k)
            for k in ("trace_id", "span_id", "parent_span_id", "distributed_traceability")
            if metadata_out.get(k) is not None
        },
    }
    root_trace = trace_from_metadata(metadata_out) or trace_from_metadata(
        metadata_out.get("distributed_traceability")
    )
    if root_trace:
        sla_trace = child_trace(root_trace, "sla-agent")
        headers = inject_http_headers({}, sla_trace)
    else:
        sla_trace = None
        headers = {}
    timeout = 25.0 if run_slo or run_assurance else 4.0
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        ingest_http_ms = (time.perf_counter() - t0) * 1000.0
        metadata_out["sla_agent_ingest_latency_ms"] = ingest_http_ms
        lat = metadata_out.get("module_latencies_ms")
        if isinstance(lat, dict):
            lat["sla_agent_ingest_http_ms"] = ingest_http_ms
        ts = datetime.now(timezone.utc).isoformat()
        ing: dict = {
            "status": "OK",
            "http_status": r.status_code,
            "pipeline_ingested": body.get("pipeline_ingested"),
            "runtime_assurance": body.get("runtime_assurance"),
            "slo_evaluation_executed": body.get("slo_evaluation_executed"),
            "monitoring_note": body.get("monitoring_note"),
        }
        if body.get("runtime_assurance_payload") is not None:
            metadata_out["runtime_assurance"] = body.get("runtime_assurance_payload")
            ing["assurance_state"] = (body.get("runtime_assurance_payload") or {}).get("state")
            ing["last_evaluation"] = (body.get("runtime_assurance_payload") or {}).get(
                "last_evaluation"
            )
            ing["drift_detected"] = (body.get("runtime_assurance_payload") or {}).get(
                "drift_detected"
            )
        if body.get("runtime_governance_event") is not None:
            metadata_out["runtime_governance_event"] = body.get("runtime_governance_event")
        if sla_trace:
            hops = list(metadata_out.get("distributed_trace_hops") or [])
            hops.append(dict(sla_trace))
            metadata_out["distributed_trace_hops"] = hops
            root = trace_from_metadata(metadata_out) or sla_trace
            metadata_out["distributed_traceability"] = build_distributed_traceability(root, hops)
            metadata_out = merge_trace_into_metadata(metadata_out, root)
        if body.get("slo_evaluation") is not None:
            ing["slo_evaluation"] = body.get("slo_evaluation")
        if body.get("slo_evaluation_error"):
            ing["slo_evaluation_error"] = body.get("slo_evaluation_error")
        if body.get("runtime_assurance_error"):
            ing["runtime_assurance_error"] = body.get("runtime_assurance_error")
        metadata_out["sla_agent_ingest"] = ing
        lifecycle["PIPELINE_INGESTED"] = ts
        lifecycle["MONITORED"] = ts
        if body.get("runtime_assurance") is True:
            lifecycle["RUNTIME_ASSURANCE"] = ts
        if body.get("slo_evaluation_executed") is True:
            lifecycle["SLO_EVALUATED"] = ts
        if body.get("slo_evaluation_executed") is True:
            return "OK_WITH_SLO"
        if body.get("runtime_assurance") is True:
            return "OK_WITH_ASSURANCE"
        return "OK"
    except Exception as e:
        ingest_http_ms = (time.perf_counter() - t0) * 1000.0
        metadata_out["sla_agent_ingest_latency_ms"] = ingest_http_ms
        lat = metadata_out.get("module_latencies_ms")
        if isinstance(lat, dict):
            lat["sla_agent_ingest_http_ms"] = ingest_http_ms
        logger.warning("[SLA_AGENT_INGEST] %s", e)
        metadata_out["sla_agent_ingest"] = {"status": "ERROR", "error": str(e)[:240]}
        return "ERROR"


def _sync_prb_snapshot_from_metadata(metadata: dict, snapshot: object) -> None:
    """PROMPT_124.5: espelhar ran_prb_utilization_input no snapshot quando prb_utilization está ausente."""
    try:
        prb_input = metadata.get("ran_prb_utilization_input")
        if prb_input is None:
            return
        if not isinstance(snapshot, dict):
            return
        ran = snapshot.get("ran")
        if ran is None:
            snapshot["ran"] = {}
            ran = snapshot["ran"]
        elif not isinstance(ran, dict):
            return
        if ran.get("prb_utilization") is None:
            ran["prb_utilization"] = prb_input
    except Exception as exc:
        logger.warning("[TELEMETRY] PRB snapshot sync failed: %s", exc)


def _snapshot_missing_fields(snapshot: dict) -> list[str]:
    """Lista campos obrigatórios ausentes (valor None). Não inventa métricas.
    Reconhece aliases do contract v2 (mesmo objecto snapshot; p.ex. cpu_utilization vs cpu).
    """
    missing: list[str] = []
    if not isinstance(snapshot, dict):
        return ["snapshot"]
    ran = snapshot.get("ran") if isinstance(snapshot.get("ran"), dict) else {}
    tr = snapshot.get("transport") if isinstance(snapshot.get("transport"), dict) else {}
    co = snapshot.get("core") if isinstance(snapshot.get("core"), dict) else {}

    if ran.get("prb_utilization") is None:
        missing.append("ran.prb_utilization")
    if ran.get("latency") is None and ran.get("latency_ms") is None:
        missing.append("ran.latency")

    if tr.get("rtt") is None and tr.get("rtt_ms") is None:
        missing.append("transport.rtt")
    if tr.get("jitter") is None and tr.get("jitter_ms") is None:
        missing.append("transport.jitter")

    cpu = co.get("cpu")
    if cpu is None:
        cpu = co.get("cpu_utilization")
    mem = co.get("memory")
    if mem is None:
        mem = co.get("memory_utilization")
    if cpu is None:
        missing.append("core.cpu")
    if mem is None:
        missing.append("core.memory")
    return missing


def _ensure_telemetry_v2_flags(metadata: dict) -> None:
    """
    PR-05 / PROMPT_37: enriquecer metadata com versionamento e flags explícitas.
    PR-01 / PROMPT_39: unidades de referência (sem alterar valores numéricos).
    Não recalcula gaps — reutiliza telemetry_gaps existente ou [].
    telemetry_complete = (len(gaps) == 0), coerente com a lógica já aplicada no submit.
    """
    if not isinstance(metadata, dict):
        return
    gaps = metadata.get("telemetry_gaps")
    if gaps is None:
        gaps = []
    metadata["telemetry_gaps"] = gaps
    metadata["telemetry_version"] = "v2"
    metadata["telemetry_complete"] = len(gaps) == 0
    metadata["telemetry_units"] = dict(TELEMETRY_UNITS_V2)


def _build_temporal_intent_trace(
    *,
    intent_id: object,
    nest_id: object,
    execution_id: str,
    t_submit_iso: str,
    telemetry_pre_at: str | None,
    timestamp_decision: str,
    telemetry_snapshot: dict,
    lifecycle_state: str,
    sla_lifecycle: dict,
    trace_id: str | None = None,
    span_id: str | None = None,
    parent_span_id: str | None = None,
) -> dict:
    """
    P0: metadata temporal mínima por intent — sem drift automático, sem storage externo.
    """
    snap = telemetry_snapshot if isinstance(telemetry_snapshot, dict) else {}
    post_ts = snap.get("timestamp")
    trace = {
        "temporal_trace_version": "p0",
        "intent_id": intent_id,
        "nest_id": nest_id,
        "execution_id": execution_id,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "timestamps_utc": {
            "submitted": t_submit_iso,
            "telemetry_pre_decision": telemetry_pre_at,
            "decision_recorded": timestamp_decision,
            "telemetry_post_snapshot": post_ts,
        },
        "lifecycle_state": lifecycle_state,
        "sla_lifecycle": dict(sla_lifecycle) if isinstance(sla_lifecycle, dict) else {},
        "telemetry_contract_version": snap.get("telemetry_contract_version"),
    }
    return trace


def _minimal_telemetry_drift(reference: dict, current: dict) -> Dict[str, Any]:
    """P1: deltas numéricos null-safe entre snapshots (contract v2 / legacy keys)."""
    deltas: List[Dict[str, Any]] = []

    def pick_num(d: dict, *keys: str) -> Optional[float]:
        for k in keys:
            v = d.get(k)
            if v is not None:
                try:
                    return float(v)
                except (TypeError, ValueError):
                    continue
        return None

    def add_delta(path: str, ref_val: Optional[float], cur_val: Optional[float]) -> None:
        if ref_val is None and cur_val is None:
            return
        entry: Dict[str, Any] = {"path": path, "reference": ref_val, "current": cur_val}
        if ref_val is not None and cur_val is not None:
            entry["delta"] = cur_val - ref_val
        else:
            entry["delta"] = None
        deltas.append(entry)

    if not isinstance(reference, dict) or not isinstance(current, dict):
        return {"deltas": [], "fields_compared": 0, "error": "invalid_snapshot_shape"}

    ran_r = reference.get("ran") if isinstance(reference.get("ran"), dict) else {}
    ran_c = current.get("ran") if isinstance(current.get("ran"), dict) else {}
    tr_r = reference.get("transport") if isinstance(reference.get("transport"), dict) else {}
    tr_c = current.get("transport") if isinstance(current.get("transport"), dict) else {}
    co_r = reference.get("core") if isinstance(reference.get("core"), dict) else {}
    co_c = current.get("core") if isinstance(current.get("core"), dict) else {}

    add_delta("ran.prb_utilization", pick_num(ran_r, "prb_utilization"), pick_num(ran_c, "prb_utilization"))
    add_delta("ran.latency", pick_num(ran_r, "latency", "latency_ms"), pick_num(ran_c, "latency", "latency_ms"))
    add_delta("transport.rtt", pick_num(tr_r, "rtt", "rtt_ms"), pick_num(tr_c, "rtt", "rtt_ms"))
    add_delta("transport.jitter", pick_num(tr_r, "jitter", "jitter_ms"), pick_num(tr_c, "jitter", "jitter_ms"))
    add_delta("core.cpu", pick_num(co_r, "cpu", "cpu_utilization"), pick_num(co_c, "cpu", "cpu_utilization"))
    add_delta("core.memory", pick_num(co_r, "memory", "memory_bytes"), pick_num(co_c, "memory", "memory_bytes"))

    return {"deltas": deltas, "fields_compared": len(deltas)}


def _p2_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _domain_from_drift_path(path: str) -> str:
    if path.startswith("ran."):
        return "ran"
    if path.startswith("transport."):
        return "transport"
    if path.startswith("core."):
        return "core"
    return "unknown"


def _build_remediation_evidence_p2(
    *,
    drift_summary: Dict[str, Any],
    reference: Optional[Dict[str, Any]],
    current: Dict[str, Any],
    revalidation_status: str,
) -> Dict[str, Any]:
    """
    P2: evidência declarativa apenas — sem execução automática, orchestration ou callbacks.
    Usa drift_summary, limiares mínimos (env) e snapshots ref/atual.
    """
    th_prb = _p2_env_float("TRISLA_P2_PRB_DELTA_THRESHOLD", 5.0)
    th_lat = _p2_env_float("TRISLA_P2_LATENCY_MS_DELTA_THRESHOLD", 2.0)
    th_rtt = _p2_env_float("TRISLA_P2_RTT_MS_DELTA_THRESHOLD", 1.0)
    th_jit = _p2_env_float("TRISLA_P2_JITTER_MS_DELTA_THRESHOLD", 1.0)
    th_cpu = _p2_env_float("TRISLA_P2_CPU_DELTA_THRESHOLD", 5.0)
    th_mem_rel = _p2_env_float("TRISLA_P2_MEMORY_RELATIVE_THRESHOLD", 0.05)

    path_abs_thresholds = {
        "ran.prb_utilization": th_prb,
        "ran.latency": th_lat,
        "transport.rtt": th_rtt,
        "transport.jitter": th_jit,
        "core.cpu": th_cpu,
    }

    affected: set[str] = set()
    breach_paths: list[str] = []

    compared = bool(drift_summary.get("compared"))
    if not compared:
        if revalidation_status == "INCOMPLETE":
            for g in _snapshot_missing_fields(current):
                dom = g.split(".", 1)[0]
                if dom in ("ran", "transport", "core"):
                    affected.add(dom)
            return {
                "recommendation": (
                    "Telemetria atual incompleta e sem snapshot de referência; "
                    "não há correlação de drift numérica."
                ),
                "severity": "MEDIUM",
                "affected_domains": sorted(affected),
                "suggested_action": (
                    "Completar exportação Prometheus para o snapshot atual e "
                    "reenviar revalidate-telemetry com reference_telemetry_snapshot."
                ),
                "revalidation_required": True,
            }
        return {
            "recommendation": (
                "Nenhuma comparação de drift: reference_telemetry_snapshot não foi enviado."
            ),
            "severity": "INFO",
            "affected_domains": [],
            "suggested_action": (
                "Opcional: incluir reference_telemetry_snapshot (ex.: metadata.telemetry_snapshot "
                "do submit) para gerar deltas e avaliação de remediação declarativa."
            ),
            "revalidation_required": False,
        }

    for d in drift_summary.get("deltas") or []:
        if not isinstance(d, dict):
            continue
        path = str(d.get("path") or "")
        delta = d.get("delta")
        ref_v = d.get("reference")
        cur_v = d.get("current")

        if path == "core.memory":
            if (
                ref_v is not None
                and cur_v is not None
                and isinstance(ref_v, (int, float))
                and isinstance(cur_v, (int, float))
            ):
                rv = float(ref_v)
                cv = float(cur_v)
                base = max(abs(rv), 1e-9)
                if abs(cv - rv) / base > th_mem_rel:
                    affected.add("core")
                    breach_paths.append(path)
            continue

        if isinstance(delta, (int, float)):
            lim = path_abs_thresholds.get(path)
            if lim is not None and abs(float(delta)) > lim:
                dom = _domain_from_drift_path(path)
                if dom != "unknown":
                    affected.add(dom)
                breach_paths.append(path)

    if revalidation_status == "INCOMPLETE":
        for g in _snapshot_missing_fields(current):
            dom = g.split(".", 1)[0]
            if dom in ("ran", "transport", "core"):
                affected.add(dom)

    affected_sorted = sorted(affected)

    if not affected_sorted:
        return {
            "recommendation": (
                "Nenhum desvio acima dos limiares mínimos configurados; "
                "telemetria atual dentro da banda em relação à referência."
            ),
            "severity": "INFO",
            "affected_domains": [],
            "suggested_action": (
                "Nenhuma ação declarativa obrigatória; manter observabilidade conforme política de SLA."
            ),
            "revalidation_required": False,
        }

    if len(affected_sorted) > 1 or len(breach_paths) > 2:
        severity = "HIGH"
    else:
        severity = "MEDIUM"

    breach_txt = ", ".join(breach_paths) if breach_paths else ", ".join(affected_sorted)
    return {
        "recommendation": (
            f"Desvio temporal acima dos limiares mínimos nos caminhos: {breach_txt}."
        ),
        "severity": severity,
        "affected_domains": affected_sorted,
        "suggested_action": (
            "Revisar domínios listados e a política de slice no plano de controle; "
            "após correções operacionais, chamar novamente revalidate-telemetry "
            "(sem execução automática neste endpoint)."
        ),
        "revalidation_required": True,
    }


@router.post("/interpret")
async def interpret_sla(request: SLAInterpretRequest):
    """
    Interpretação PLN → Ontologia (REAL)
    
    Chama módulo SEM-CSMF REAL do NASP:
    - Retorna tipo de slice
    - Retorna parâmetros técnicos interpretados
    - Retorna mensagens de erro semânticas quando houver
    - Nunca aceita entrada inválida
    """
    try:
        # Validação básica de entrada
        if not request.intent_text or not request.intent_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Intent text não pode ser vazio"
            )
        
        if not request.tenant_id or not request.tenant_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Tenant ID não pode ser vazio"
            )
        
        # ETAPA 1: Corrigir erros ortográficos (Cap. 5 - PNL)
        intent_text_corrigido = corrigir_erros_ortograficos(request.intent_text.strip())
        
        # ETAPA 2: Inferir tipo de slice se necessário
        tipo_slice_inferido = inferir_tipo_slice(intent_text_corrigido)
        
        # ETAPA 3: Extrair parâmetros técnicos do texto
        parametros_extraidos = extrair_parametros_tecnicos(intent_text_corrigido)
        
        # Chamada REAL ao SEM-CSMF do NASP
        result = await nasp_service.call_sem_csmf(
            intent_text=intent_text_corrigido,
            tenant_id=request.tenant_id.strip()
        )
        
        # Enriquecer resposta com informações processadas localmente
        if not result.get("service_type") and tipo_slice_inferido != "AUTO":
            result["service_type"] = tipo_slice_inferido
        
        # Mesclar parâmetros extraídos com resposta do SEM-CSMF
        if parametros_extraidos:
            sla_req = result.get("sla_requirements", {})
            sla_req.update(parametros_extraidos)
            result["sla_requirements"] = sla_req
        
        # Verificar se há erros semânticos na resposta
        if result.get("error") or result.get("semantic_error"):
            raise HTTPException(
                status_code=422,
                detail=result.get("error") or result.get("semantic_error")
            )
        
        # Retornar resposta REAL do SEM-CSMF com parâmetros técnicos sugeridos
        # Conforme Capítulo 5 - SEM-CSMF deve retornar parâmetros técnicos editáveis
        service_type_final = result.get("service_type") or result.get("slice_type") or tipo_slice_inferido
        
        # Construir parâmetros técnicos sugeridos (ETAPA 2)
        technical_parameters = result.get("technical_parameters", {})
        if parametros_extraidos:
            technical_parameters.update(parametros_extraidos)
        
        # Se SEM-CSMF não retornou parâmetros, usar valores padrão baseados no tipo de slice
        if not technical_parameters and service_type_final:
            if service_type_final.upper() == "URLLC":
                technical_parameters = {
                    "latency_maxima_ms": 10,
                    "disponibilidade_percent": 99.99,
                    "confiabilidade_percent": 99.99,
                    "numero_dispositivos": 10
                }
            elif service_type_final.upper() == "EMBB":
                technical_parameters = {
                    "latency_maxima_ms": 50,
                    "disponibilidade_percent": 99.9,
                    "confiabilidade_percent": 99.9,
                    "throughput_min_dl_mbps": 100,
                    "throughput_min_ul_mbps": 50
                }
            elif service_type_final.upper() == "MMTC":
                technical_parameters = {
                    "latency_maxima_ms": 100,
                    "disponibilidade_percent": 95,
                    "confiabilidade_percent": 95,
                    "numero_dispositivos": 1000
                }
        
        return {
            "intent_id": result.get("intent_id") or result.get("id"),
            "service_type": service_type_final,
            "sla_requirements": result.get("sla_requirements", {}),
            "sla_id": result.get("intent_id") or result.get("id"),
            "status": "processing",
            "tenant_id": request.tenant_id,
            "nest_id": result.get("nest_id"),
            "slice_type": service_type_final,
            "technical_parameters": technical_parameters,  # Parâmetros técnicos sugeridos (ETAPA 2)
            "created_at": result.get("created_at") or result.get("timestamp") or None,
            "message": "SLA interpretado pelo SEM-CSMF com sucesso. Ajuste os parâmetros técnicos na próxima etapa."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao interpretar SLA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=SLASubmitResponse)
async def submit_sla_template(request: SLASubmitRequest):
    """
    Submissão com TODOS os módulos TriSLA
    
    Fluxo REAL completo:
    1. SEM-CSMF: Interpreta template e gera NEST
    2. ML-NSMF: Avalia capacidades e recursos
    3. Decision Engine: Decisão final (ACCEPT/REJECT)
    4. BC-NSSMF: Registro no blockchain
    
    Resposta padronizada conforme especificação
    """
    try:
        # Validação básica
        if not request.template_id or not request.template_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Template ID não pode ser vazio"
            )
        
        if not request.form_values:
            raise HTTPException(
                status_code=400,
                detail="Form values não podem ser vazios"
            )
        
        # Construir template NEST a partir do template_id e form_values
        # Extrair service_type dos form_values (pode vir em type, slice_type, ou service_type)
        service_type_from_form = (
            request.form_values.get("type") or
            request.form_values.get("slice_type") or
            request.form_values.get("service_type") or
            None
        )
        
        nest_template = {
            "sla_requirements": request.form_values,
            "tenant_id": request.tenant_id,
            "template_id": request.template_id
        }
        logger.info(
            "[SLA SUBMIT] received template_id=%s tenant_id=%s fields=%s",
            request.template_id,
            request.tenant_id,
            ",".join(sorted(list(request.form_values.keys()))),
        )
        t_submit_iso = datetime.now(timezone.utc).isoformat()
        execution_id = str(uuid.uuid4())
        root_trace = new_root_trace("portal-backend")
        timestamp_pre_decision = datetime.now(timezone.utc).isoformat()

        # Coleta telemetria antes da decisão para preservar causalidade PRB -> Decision Engine.
        telemetry_before_decision, _tel_ms_pre = await collect_domain_metrics_async(
            execution_id, timestamp_pre_decision
        )
        pre_ran = telemetry_before_decision.get("ran") if isinstance(telemetry_before_decision, dict) else {}
        if not isinstance(pre_ran, dict):
            pre_ran = {}
        prb_value_pre = pre_ran.get("prb_utilization")
        print("DEBUG_PRB_BEFORE_DECISION:", prb_value_pre)
        logger.info("[DEBUG_PRB_BEFORE_DECISION] prb=%s", prb_value_pre)

        # Incluir type/slice_type se existir nos form_values
        if service_type_from_form:
            nest_template["type"] = service_type_from_form
            nest_template["slice_type"] = service_type_from_form
        nest_template["metadata"] = merge_trace_into_metadata(
            {
                "telemetry_snapshot": telemetry_before_decision,
                "ran_prb_utilization_input": prb_value_pre,
                "telemetry_collected_at": timestamp_pre_decision,
                "execution_id": execution_id,
            },
            root_trace,
        )
        
        # Enviar ao NASP com TODOS os módulos (sequência completa)
        result = await nasp_service.submit_template_to_nasp(
            nest_template=nest_template,
            tenant_id=request.tenant_id
        )
        
        decision_raw = result.get("decision")
        decision = str(decision_raw).upper() if decision_raw is not None else None
        if decision not in _VALID_DECISIONS:
            raise RuntimeError(f"Invalid decision returned: {decision_raw}")
        logger.info("[SLA SUBMIT] final_decision=%s", decision)

        timestamp_decision = datetime.now(timezone.utc).isoformat()
        metadata_out = dict(result.get("metadata") or {})
        result_meta = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
        for key in (
            "trace_id",
            "span_id",
            "parent_span_id",
            "distributed_trace_hops",
            "distributed_traceability",
        ):
            if result_meta.get(key) is not None:
                metadata_out[key] = result_meta[key]
        try:
            telemetry_snapshot, _tel_ms = await collect_domain_metrics_async(
                execution_id, timestamp_decision
            )
            _sync_prb_snapshot_from_metadata(metadata_out, telemetry_snapshot)
            gaps = _snapshot_missing_fields(telemetry_snapshot)
            strict = os.getenv("TELEMETRY_SNAPSHOT_STRICT", "").lower() in (
                "1",
                "true",
                "yes",
            )
            if gaps:
                if strict:
                    raise RuntimeError(
                        "Telemetry fields missing: " + ", ".join(gaps)
                    )
                logger.warning(
                    "[TELEMETRY] snapshot incompleto (sem dados inventados) missing=%s",
                    gaps,
                )
            metadata_out["telemetry_snapshot"] = telemetry_snapshot
            metadata_out["execution_id"] = execution_id
            metadata_out["telemetry_gaps"] = gaps
            metadata_out["telemetry_complete"] = len(gaps) == 0
        except Exception as tel_exc:
            logger.error("[TELEMETRY HARD FAIL] %s", tel_exc, exc_info=True)
            raise

        md_src = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
        ml_risk = md_src.get("ml_risk_score")
        if ml_risk is None and isinstance(metadata_out.get("ml_risk_score"), (int, float)):
            ml_risk = metadata_out.get("ml_risk_score")

        slice_type = (
            request.form_values.get("type")
            or request.form_values.get("slice_type")
            or request.form_values.get("service_type")
            or ""
        )
        scenario = str(request.form_values.get("scenario") or "")
        csv_path = os.getenv("TELEMETRY_SNAPSHOT_CSV")
        append_telemetry_csv(
            csv_path,
            build_csv_row(
                execution_id,
                timestamp_decision,
                decision,
                float(ml_risk) if isinstance(ml_risk, (int, float)) else None,
                metadata_out.get("telemetry_snapshot") or {},
                scenario,
                str(slice_type),
                nasp_latency_ms=(
                    float(metadata_out["nasp_latency_ms"])
                    if isinstance(metadata_out.get("nasp_latency_ms"), (int, float))
                    else None
                ),
                nasp_latency_available=metadata_out.get("nasp_latency_available"),
            ),
        )

        # SLA-aware metrics (metadata only; IEEE-level instrumentation)
        snap = metadata_out.get("telemetry_snapshot") or {}
        domains_for_metrics = {
            "ran": snap.get("ran") or {},
            "transport": snap.get("transport") or {},
            "core": snap.get("core") or {},
        }
        ml_for_metrics = dict(result.get("ml_prediction") or {})
        if ml_for_metrics.get("risk_score") is None and isinstance(ml_risk, (int, float)):
            ml_for_metrics["risk_score"] = float(ml_risk)
        if ml_for_metrics.get("confidence") is None and result.get("confidence") is not None:
            try:
                ml_for_metrics["confidence"] = float(result.get("confidence"))
            except (TypeError, ValueError):
                pass
        sla_m = compute_sla_metrics(
            decision=decision,
            ml_prediction=ml_for_metrics,
            domains=domains_for_metrics,
            telemetry_snapshot=snap,
        )
        metadata_out["sla_metrics"] = sla_m
        metadata_out["sla_policy_version"] = sla_m.get("sla_policy_version", "v1")

        now_iso = datetime.now(timezone.utc).isoformat()
        lifecycle = {
            "SUBMITTED": t_submit_iso,
            "DECIDED": timestamp_decision,
        }
        if decision == "ACCEPT":
            lifecycle["DECIDED_ACCEPT"] = timestamp_decision
        elif decision == "RENEGOTIATE":
            lifecycle["DECIDED_RENEGOTIATE"] = timestamp_decision
        else:
            lifecycle["DECIDED_REJECT"] = timestamp_decision

        orch_ok = metadata_out.get("nasp_orchestration_status") == "SUCCESS"
        bc_ok = result.get("bc_status") == "COMMITTED"

        if decision == "ACCEPT" and metadata_out.get("nasp_orchestration_attempted"):
            rq = metadata_out.get("nasp_orchestration_requested_at")
            lifecycle["ORCHESTRATION_REQUESTED"] = rq or timestamp_decision
        if metadata_out.get("nasp_orchestration_attempted") and orch_ok:
            lifecycle["ORCHESTRATED"] = now_iso
        elif decision == "ACCEPT" and metadata_out.get("nasp_orchestration_attempted"):
            lifecycle["ORCHESTRATION_FAILED"] = now_iso

        if result.get("bc_status") == "COMMITTED":
            lifecycle["BLOCKCHAIN_COMMITTED"] = now_iso
            lifecycle["BLOCKCHAIN_REGISTERED"] = now_iso
        elif decision == "ACCEPT" and result.get("bc_status") == "BLOCKCHAIN_FAILED":
            lifecycle["BLOCKCHAIN_FAILED"] = now_iso

        md_lat = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
        ml_predict_ms = md_lat.get("ml_prediction_latency_ms")
        if ml_predict_ms is None and isinstance(metadata_out, dict):
            ml_predict_ms = metadata_out.get("ml_prediction_latency_ms")
        metadata_out["module_latencies_ms"] = {
            "semantic_parsing_ms": result.get("semantic_parsing_latency_ms"),
            "sem_csmf_internal_ms": result.get("sem_csmf_internal_latency_ms"),
            "sem_pipeline_to_decision_ms": result.get("decision_duration_ms"),
            "admission_total_ms": result.get("admission_time_total_ms"),
            "ml_nsmf_predict_ms": ml_predict_ms,
            "nasp_orchestration_ms": metadata_out.get("nasp_latency_ms"),
            "blockchain_register_ms": result.get("blockchain_transaction_latency_ms"),
        }

        req_sa = os.getenv("SLA_AGENT_REQUIRED_FOR_ACCEPT", "false").lower() == "true"
        if decision == "ACCEPT" and orch_ok and bc_ok:
            lifecycle["SLA_AGENT_REQUESTED"] = now_iso
            sla_agent_status = await _notify_sla_agent_pipeline(
                result=result,
                metadata_out=metadata_out,
                decision=decision,
                lifecycle=lifecycle,
                tenant_id=request.tenant_id,
            )
            if sla_agent_status == "ERROR" and req_sa:
                lifecycle["SLA_AGENT_FAILED"] = datetime.now(timezone.utc).isoformat()
        else:
            if decision == "ACCEPT":
                metadata_out["sla_agent_ingest"] = {
                    "status": "SKIPPED",
                    "reason": "orchestration_or_blockchain_incomplete",
                }
                sla_agent_status = (
                    "SKIPPED_PIPELINE_INCOMPLETE"
                    if req_sa
                    else "SKIPPED"
                )
            else:
                metadata_out["sla_agent_ingest"] = {
                    "status": "SKIPPED",
                    "reason": f"decision={decision}",
                }
                sla_agent_status = "SKIPPED"

        base_done = decision == "ACCEPT" and orch_ok and bc_ok
        if base_done and (not req_sa or is_sla_agent_ingest_success(sla_agent_status)):
            lifecycle["COMPLETED"] = datetime.now(timezone.utc).isoformat()
        elif decision == "ACCEPT" and metadata_out.get("nasp_orchestration_attempted") and not orch_ok:
            metadata_out["failure_reason"] = "orchestration_failed"
            metadata_out["failure_code"] = "ORCHESTRATION_FAILED"
            lifecycle["FAILED"] = now_iso
        elif decision == "ACCEPT" and orch_ok and not bc_ok:
            metadata_out["failure_reason"] = metadata_out.get("failure_reason") or "blockchain_failed"
            metadata_out["failure_code"] = metadata_out.get("failure_code") or "BLOCKCHAIN_FAILED"
            lifecycle["FAILED"] = now_iso
        elif decision == "ACCEPT" and base_done and req_sa and not is_sla_agent_ingest_success(
            sla_agent_status
        ):
            metadata_out["failure_reason"] = "sla_agent_ingest_failed"
            metadata_out["failure_code"] = "SLA_AGENT_FAILED"
            lifecycle["FAILED"] = now_iso

        if lifecycle.get("COMPLETED"):
            lifecycle_state = "COMPLETED"
        elif lifecycle.get("FAILED"):
            lifecycle_state = "FAILED"
        elif lifecycle.get("ORCHESTRATION_FAILED"):
            lifecycle_state = "ORCHESTRATION_FAILED"
        elif lifecycle.get("BLOCKCHAIN_FAILED"):
            lifecycle_state = "BLOCKCHAIN_FAILED"
        elif lifecycle.get("SLA_AGENT_FAILED"):
            lifecycle_state = "SLA_AGENT_FAILED"
        else:
            lifecycle_state = "IN_PROGRESS"

        orch_ref = None
        if isinstance(metadata_out.get("nasp_orchestration_response"), dict):
            orch_ref = metadata_out["nasp_orchestration_response"].get("nsi_id")

        metadata_out["sla_lifecycle"] = lifecycle
        metadata_out["lifecycle_state"] = lifecycle_state

        de_orch_ls = metadata_out.get("orchestration_lifecycle_state")
        if isinstance(de_orch_ls, str) and de_orch_ls.strip():
            metadata_out["de_initial_lifecycle_state"] = de_orch_ls.strip()
        if metadata_out.get("decision_engine_orchestration_authority") is True:
            metadata_out["lifecycle_state_source"] = (
                "decision_engine_authority_plus_portal_composite"
            )
        else:
            metadata_out.setdefault(
                "lifecycle_state_source",
                "portal_legacy_composite",
            )

        # === FASE 4 — Portal Backend deixa de ser autoridade semântica de
        # lifecycle/governance: apenas repassa o que o Decision Engine declarou
        # (lifecycle_event/governance_event) e marca a fonte de autoridade.
        # O bloco operacional (sla_lifecycle/lifecycle_state) é mantido por
        # compatibilidade, mas explicitamente etiquetado como "pipeline".
        try:
            de_lifecycle_event = metadata_out.get("lifecycle_event")
            de_governance_event = metadata_out.get("governance_event")
            de_lifecycle_authority = metadata_out.get("lifecycle_authority")
            de_governance_authority = metadata_out.get("governance_authority")
            de_lc_auth_flag = bool(
                metadata_out.get("decision_engine_lifecycle_authority")
            )
            de_gv_auth_flag = bool(
                metadata_out.get("decision_engine_governance_authority")
            )

            metadata_out["lifecycle_pipeline_state"] = lifecycle_state
            metadata_out["lifecycle_pipeline_state_source"] = (
                "portal_backend_pipeline_composite"
            )

            if isinstance(de_lifecycle_event, dict) and de_lc_auth_flag:
                metadata_out["lifecycle_authority_source"] = "decision-engine"
                metadata_out["lifecycle_initial_state"] = de_lifecycle_event.get(
                    "lifecycle_state"
                )
                metadata_out["lifecycle_event_type"] = de_lifecycle_event.get(
                    "lifecycle_event_type"
                )
                metadata_out["lifecycle_transition_reason"] = de_lifecycle_event.get(
                    "lifecycle_transition_reason"
                )
                metadata_out["lifecycle_authority"] = (
                    de_lifecycle_authority or "decision-engine"
                )
                metadata_out["portal_lifecycle_role"] = "relay"
            else:
                metadata_out.setdefault("lifecycle_authority_source", "portal-legacy")
                metadata_out.setdefault("portal_lifecycle_role", "legacy-composer")

            governance_attempted = decision == "ACCEPT"
            governance_registered = bool(result.get("bc_status") == "COMMITTED")
            tx_hash_present = bool(result.get("tx_hash"))

            if isinstance(de_governance_event, dict) and de_gv_auth_flag:
                metadata_out["governance_authority_source"] = "decision-engine"
                metadata_out["governance_event_id"] = de_governance_event.get(
                    "governance_event_id"
                )
                metadata_out["governance_event_state"] = de_governance_event.get(
                    "event_state"
                )
                metadata_out["governance_event_type"] = de_governance_event.get(
                    "event_type"
                )
                metadata_out["governance_authority"] = (
                    de_governance_authority or "decision-engine"
                )
                metadata_out["portal_governance_role"] = "relay"
                if governance_registered and tx_hash_present:
                    metadata_out["governance_registration_status"] = "REGISTERED"
                    metadata_out["governance_registration_fallback"] = False
                    metadata_out["governance_registration_authority"] = "bc-nssmf"
                    metadata_out["governance_registration_tx_hash"] = result.get(
                        "tx_hash"
                    )
                    metadata_out["governance_registration_block_number"] = result.get(
                        "block_number"
                    )
                elif governance_attempted:
                    metadata_out["governance_registration_status"] = "DEGRADED_FALLBACK"
                    metadata_out["governance_registration_fallback"] = True
                    metadata_out.setdefault(
                        "governance_registration_fallback_reason",
                        "bc_not_committed_or_tx_hash_absent",
                    )
                else:
                    metadata_out["governance_registration_status"] = "SKIPPED_NO_ACCEPT"
                    metadata_out["governance_registration_fallback"] = False
            else:
                metadata_out.setdefault("governance_authority_source", "portal-legacy")
                metadata_out.setdefault("portal_governance_role", "legacy-relayer")
                if governance_registered and tx_hash_present:
                    metadata_out.setdefault(
                        "governance_registration_status", "REGISTERED_LEGACY"
                    )
                    metadata_out.setdefault("governance_registration_fallback", False)
                elif governance_attempted:
                    metadata_out.setdefault(
                        "governance_registration_status", "DEGRADED_FALLBACK"
                    )
                    metadata_out.setdefault("governance_registration_fallback", True)
                else:
                    metadata_out.setdefault(
                        "governance_registration_status", "SKIPPED_NO_ACCEPT"
                    )
                    metadata_out.setdefault("governance_registration_fallback", False)
        except Exception as _fase4_err:
            metadata_out["governance_registration_fallback"] = True
            metadata_out["lifecycle_authority_source"] = "portal-legacy-on-error"
            metadata_out["governance_authority_source"] = "portal-legacy-on-error"
            metadata_out["fase4_relay_error"] = str(_fase4_err)[:200]

        md_pre = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
        telemetry_pre_at = md_pre.get("telemetry_collected_at")
        metadata_out["temporal_intent_trace"] = _build_temporal_intent_trace(
            intent_id=result.get("intent_id"),
            nest_id=result.get("nest_id"),
            execution_id=execution_id,
            t_submit_iso=t_submit_iso,
            telemetry_pre_at=telemetry_pre_at if isinstance(telemetry_pre_at, str) else None,
            timestamp_decision=timestamp_decision,
            telemetry_snapshot=metadata_out.get("telemetry_snapshot") or {},
            lifecycle_state=lifecycle_state,
            sla_lifecycle=lifecycle,
            trace_id=metadata_out.get("trace_id"),
            span_id=metadata_out.get("span_id"),
            parent_span_id=metadata_out.get("parent_span_id"),
        )
        logger.info(
            "[TEMPORAL_P0] intent_id=%s execution_id=%s lifecycle_state=%s",
            result.get("intent_id"),
            execution_id,
            lifecycle_state,
        )

        _ensure_telemetry_v2_flags(metadata_out)

        merge_governance_into_metadata(metadata_out, result)
        intent_id_for_gov = result.get("intent_id")
        if intent_id_for_gov:
            gov_patch = extract_governance_metadata(result, metadata_out)
            if gov_patch:
                persisted = await nasp_service.persist_intent_governance_metadata(
                    str(intent_id_for_gov), gov_patch
                )
                metadata_out["governance_metadata_persisted"] = persisted
                if not persisted:
                    logger.warning(
                        "[GOV_PROPAGATION] SEM persistence failed intent=%s",
                        intent_id_for_gov,
                    )

        telemetry_complete = bool(metadata_out.get("telemetry_complete"))
        telemetry_status = "COMPLETE" if telemetry_complete else "INCOMPLETE"

        return SLASubmitResponse(
            decision=decision,
            reason=result.get("reason") or result.get("justification", ""),
            justification=result.get("justification") or result.get("reason", ""),
            sla_id=result.get("sla_id"),
            timestamp=result.get("timestamp") or None,
            intent_id=result.get("intent_id"),
            service_type=result.get("service_type"),
            sla_requirements=result.get("sla_requirements"),
            ml_prediction=result.get("ml_prediction"),
            blockchain_tx_hash=result.get("blockchain_tx_hash") or result.get("tx_hash"),
            tx_hash=result.get("tx_hash") or result.get("blockchain_tx_hash"),
            sla_hash=result.get("sla_hash"),  # Hash SHA-256 do SLA-aware
            status=result.get("status", "ok"),
            sem_csmf_status=result.get("sem_csmf_status", "ERROR"),
            ml_nsmf_status=result.get("ml_nsmf_status", "ERROR"),
            bc_status=result.get("bc_status", "ERROR"),
            sla_agent_status=sla_agent_status,
            block_number=result.get("block_number"),
            nest_id=result.get("nest_id"),
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            domains=result.get("domains"),
            metadata=metadata_out,
            semantic_parsing_latency_ms=result.get("semantic_parsing_latency_ms"),
            sem_csmf_internal_latency_ms=result.get("sem_csmf_internal_latency_ms"),
            decision_duration_ms=result.get("decision_duration_ms"),
            admission_time_total_ms=result.get("admission_time_total_ms"),
            blockchain_transaction_latency_ms=result.get("blockchain_transaction_latency_ms"),
            lifecycle_state=lifecycle_state,
            orchestration_status=result.get("orchestration_status")
            or metadata_out.get("nasp_orchestration_status"),
            blockchain_status=result.get("blockchain_status"),
            failure_reason=metadata_out.get("failure_reason"),
            failure_code=metadata_out.get("failure_code"),
            orchestration_reference=orch_ref,
            telemetry_status=telemetry_status,
            telemetry_complete=telemetry_complete,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao submeter SLA: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar submissão do SLA: {str(e)}"
        )


async def _revalidate_telemetry_local_fallback(
    request: SLARevalidateTelemetryRequest,
) -> SLARevalidateTelemetryResponse:
    """
    FALLBACK IN-PROCESS — comportamento histórico de /api/v1/sla/revalidate-telemetry.

    Mantido intacto durante a FASE 2 da refatoração (REFACTOR_TRISLA_RESPONSIBILITY_GUIDE.md).
    A autoridade canônica passa a ser o SLA-Agent (`POST /api/v1/agent/revalidate-telemetry`);
    este caminho permanece como fallback quando o SLA-Agent estiver indisponível ou quando
    `SLA_AGENT_REVALIDATE_URL` não estiver configurado.

    Não remover até a FASE 7 (consolidação).
    """
    intent_id = request.intent_id
    trace = request.temporal_intent_trace if isinstance(request.temporal_intent_trace, dict) else None
    temporal_correlation: Dict[str, Any] = {
        "intent_id_requested": intent_id,
        "temporal_intent_trace_present": trace is not None,
    }
    if trace:
        tid = trace.get("intent_id")
        temporal_correlation["intent_id_match"] = tid is not None and str(tid) == intent_id
        temporal_correlation["trace_execution_id"] = trace.get("execution_id")
        temporal_correlation["trace_temporal_version"] = trace.get("temporal_trace_version")
        ts_tr = trace.get("timestamps_utc")
        if isinstance(ts_tr, dict):
            temporal_correlation["prior_telemetry_post_at"] = ts_tr.get("telemetry_post_snapshot")
    if request.correlation_execution_id:
        cex = str(request.correlation_execution_id).strip()
        temporal_correlation["correlation_execution_id"] = cex
        tex = trace.get("execution_id") if trace else None
        if tex is not None:
            temporal_correlation["execution_id_match"] = str(tex) == cex
        else:
            temporal_correlation["execution_id_match"] = None

    execution_id_rev = str(uuid.uuid4())
    collected_at = datetime.now(timezone.utc).isoformat()
    telemetry_snapshot_atual, _tel_ms = await collect_domain_metrics_async(
        execution_id_rev,
        collected_at,
    )

    ref = request.reference_telemetry_snapshot
    if isinstance(ref, dict) and ref:
        drift_summary: Dict[str, Any] = {"compared": True, **_minimal_telemetry_drift(ref, telemetry_snapshot_atual)}
    else:
        drift_summary = {
            "compared": False,
            "reason": "no_reference_telemetry_snapshot",
            "note": "Opcional: enviar metadata.telemetry_snapshot do submit anterior para deltas numéricos.",
        }

    gaps = _snapshot_missing_fields(telemetry_snapshot_atual)
    revalidation_status = "OK" if len(gaps) == 0 else "INCOMPLETE"

    timestamps_utc = {
        "revalidation_collected": telemetry_snapshot_atual.get("timestamp") or collected_at,
        "revalidation_requested_wall": collected_at,
        "prior_telemetry_post_from_trace": temporal_correlation.get("prior_telemetry_post_at"),
    }

    remediation = _build_remediation_evidence_p2(
        drift_summary=drift_summary,
        reference=ref if isinstance(ref, dict) else None,
        current=telemetry_snapshot_atual,
        revalidation_status=revalidation_status,
    )
    metadata_out: Dict[str, Any] = {"remediation_evidence": remediation}

    logger.info(
        "[TEMPORAL_P1] revalidate intent_id=%s execution_id_rev=%s status=%s",
        intent_id,
        execution_id_rev,
        revalidation_status,
    )

    return SLARevalidateTelemetryResponse(
        intent_id=intent_id,
        execution_id_revalidation=execution_id_rev,
        telemetry_snapshot_atual=telemetry_snapshot_atual,
        timestamps_utc=timestamps_utc,
        drift_summary=drift_summary,
        revalidation_status=revalidation_status,
        temporal_correlation=temporal_correlation,
        metadata=metadata_out,
    )


async def _delegate_revalidate_to_sla_agent(
    request: SLARevalidateTelemetryRequest,
    url: str,
    timeout_s: float,
) -> SLARevalidateTelemetryResponse:
    """Chama o SLA-Agent (HTTP) e devolve a resposta como modelo do contrato público."""
    payload = request.model_dump(exclude_none=False)
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, timeout=httpx.Timeout(timeout_s))
        r.raise_for_status()
        body = r.json()
        if not isinstance(body, dict):
            raise ValueError(
                f"sla-agent response not a JSON object (got {type(body).__name__})"
            )
        return SLARevalidateTelemetryResponse(**body)


@router.post("/revalidate-telemetry", response_model=SLARevalidateTelemetryResponse)
async def revalidate_telemetry(request: SLARevalidateTelemetryRequest):
    """
    P1: revalidação temporal — nova leitura Prometheus.
    P2: metadata.remediation_evidence (declarativo; sem execução automática).

    Runtime gating: only ACCEPT SLAs may revalidate (HTTP 409 otherwise).
    """
    try:
        sem_result = await nasp_service.get_sla_status(request.intent_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("[REVALIDATE_GATE] status lookup failed intent=%s err=%s", request.intent_id, exc)
        sem_result = {}

    admission_decision = resolve_admission_decision(sem_result if isinstance(sem_result, dict) else {})
    if admission_decision != "ACCEPT":
        raise HTTPException(
            status_code=409,
            detail="Runtime lifecycle unavailable for non-accepted SLA.",
        )

    sla_agent_url = (os.getenv("SLA_AGENT_REVALIDATE_URL") or "").strip()
    timeout_s = float(os.getenv("SLA_AGENT_REVALIDATE_TIMEOUT_S", "8.0") or 8.0)
    delegate_enabled = os.getenv("SLA_AGENT_REVALIDATE_ENABLED", "true").lower() == "true"

    delegated = False
    delegation_target: Optional[str] = sla_agent_url or None
    delegation_fallback_reason: Optional[str] = None

    response: Optional[SLARevalidateTelemetryResponse] = None
    if delegate_enabled and sla_agent_url:
        try:
            response = await _delegate_revalidate_to_sla_agent(
                request, sla_agent_url, timeout_s
            )
            delegated = True
        except Exception as exc:
            delegation_fallback_reason = (
                f"sla_agent_call_failed: {type(exc).__name__}: {str(exc)[:200]}"
            )
            logger.warning(
                "[REVALIDATE_DELEGATION] falha ao chamar SLA-Agent url=%s err=%s — usando fallback in-process",
                sla_agent_url,
                exc,
            )
    elif not delegate_enabled:
        delegation_fallback_reason = "SLA_AGENT_REVALIDATE_ENABLED=false"
    else:
        delegation_fallback_reason = "SLA_AGENT_REVALIDATE_URL_unset"

    if response is None:
        response = await _revalidate_telemetry_local_fallback(request)

    response = await enrich_revalidate_with_local_collect(
        request,
        response,
        collect_fn=collect_domain_metrics_async,
        drift_fn=_minimal_telemetry_drift,
        remediation_fn=_build_remediation_evidence_p2,
    )

    meta = dict(response.metadata) if isinstance(response.metadata, dict) else {}
    meta["delegated_to_sla_agent"] = delegated
    if delegation_target:
        meta["delegation_target"] = delegation_target
    if delegation_fallback_reason:
        meta["delegation_fallback_reason"] = delegation_fallback_reason
    response = response.model_copy(update={"metadata": meta})
    return response


@router.get("/status/{sla_id}", response_model=SLAStatusResponse)
async def get_sla_status(sla_id: str):
    """
    Status do SLA
    
    Consulta em tempo real ao NASP - SEM cache local
    """
    try:
        result = await nasp_service.get_sla_status(sla_id)

        admission_decision, runtime_enabled, admission_snap = resolve_admission_context(result)

        collected_snapshot: Optional[Dict[str, Any]] = None
        if runtime_enabled:
            try:
                collected_at = datetime.now(timezone.utc).isoformat()
                execution_id = f"status-{sla_id}"
                collected_snapshot, _tel_ms = await collect_domain_metrics_async(
                    execution_id,
                    collected_at,
                )
            except Exception as exc:
                logger.warning(
                    "[SLA STATUS] telemetry_snapshot collect skipped intent=%s err=%s",
                    sla_id,
                    exc,
                )

        telemetry_snapshot = resolve_status_telemetry_snapshot(
            result,
            collected_snapshot,
            runtime_lifecycle_enabled=runtime_enabled,
        )

        runtime_assurance = resolve_status_runtime_assurance(
            result,
            telemetry_snapshot=telemetry_snapshot,
            runtime_lifecycle_enabled=runtime_enabled,
        )

        operational_summary = build_operational_summary(result)
        traceability = build_traceability_summary(result)
        md = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
        decision_evidence = md.get("decision_evidence")
        if not isinstance(decision_evidence, list):
            decision_evidence = None
        admission_reasoning = (
            md.get("decision_explanation_plain")
            or md.get("decision_explanation")
            or md.get("reasoning")
        )

        return SLAStatusResponse(
            sla_id=sla_id,
            status=result.get("status", "unknown"),
            tenant_id=result.get("tenant_id", ""),
            intent_id=result.get("intent_id"),
            nest_id=result.get("nest_id"),
            created_at=result.get("created_at"),
            updated_at=result.get("updated_at"),
            admission_decision=admission_decision,
            runtime_lifecycle_enabled=runtime_enabled,
            admission_telemetry_snapshot=admission_snap,
            admission_decision_evidence=decision_evidence,
            admission_reasoning=str(admission_reasoning) if admission_reasoning else None,
            telemetry_snapshot=telemetry_snapshot,
            runtime_assurance=runtime_assurance,
            operational_summary=operational_summary,
            traceability=traceability,
        )
    except HTTPException:
        raise
    except Exception as e:
        if "não encontrado" in str(e).lower() or "not found" in str(e).lower() or "404" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        logger.error(f"Erro ao obter status do SLA {sla_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{sla_id}", response_model=SLAMetricsResponse)
async def get_sla_metrics(sla_id: str):
    """
    Métricas Reais do NASP (SLOs)
    
    Retorna métricas REAIS padronizadas:
    - latency_ms
    - jitter_ms
    - throughput_ul
    - throughput_dl
    - packet_loss
    - availability
    - slice_status (ACTIVE | FAILED | PENDING | TERMINATED)
    - last_update (ISO8601)
    
    Consulta REAL a cada chamada - SEM cache local
    Se NASP offline → erro 503
    """
    try:
        result = await nasp_service.call_metrics(sla_id)
        
        # Retornar resposta padronizada
        return SLAMetricsResponse(
            sla_id=sla_id,
            slice_status=result.get("slice_status"),
            latency_ms=result.get("latency_ms"),
            jitter_ms=result.get("jitter_ms"),
            throughput_ul=result.get("throughput_ul"),
            throughput_dl=result.get("throughput_dl"),
            packet_loss=result.get("packet_loss"),
            availability=result.get("availability"),
            last_update=result.get("last_update"),
            tenant_id=result.get("tenant_id"),
            metrics=result.get("metrics")
        )
    except HTTPException:
        raise
    except Exception as e:
        if "não encontrado" in str(e).lower() or "not found" in str(e).lower() or "404" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        logger.error(f"Erro ao obter métricas do SLA {sla_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
