"""
Rotas REAIS para SLA - SEM SIMULAÇÕES
Todas as respostas vêm do NASP real (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF)
"""
import logging
import os
import time
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException
from src.schemas.sla import (
    SLAInterpretRequest,
    SLASubmitRequest,
    SLAStatusResponse,
    SLAMetricsResponse,
    SLASubmitResponse,
)
from src.services.nasp import NASPService
from src.services.sla_metrics import compute_sla_metrics
from src.telemetry.collector import append_telemetry_csv, build_csv_row, collect_domain_metrics_async
from src.telemetry.contract_v2 import TELEMETRY_UNITS_V2
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
    }
    timeout = 20.0 if run_slo else 4.0
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=payload)
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
            "slo_evaluation_executed": body.get("slo_evaluation_executed"),
            "monitoring_note": body.get("monitoring_note"),
        }
        if body.get("slo_evaluation") is not None:
            ing["slo_evaluation"] = body.get("slo_evaluation")
        if body.get("slo_evaluation_error"):
            ing["slo_evaluation_error"] = body.get("slo_evaluation_error")
        metadata_out["sla_agent_ingest"] = ing
        lifecycle["PIPELINE_INGESTED"] = ts
        lifecycle["MONITORED"] = ts
        if body.get("slo_evaluation_executed") is True:
            lifecycle["SLO_EVALUATED"] = ts
        if body.get("slo_evaluation_executed") is True:
            return "OK_WITH_SLO"
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
        nest_template["metadata"] = {
            "telemetry_snapshot": telemetry_before_decision,
            "ran_prb_utilization_input": prb_value_pre,
            "telemetry_collected_at": timestamp_pre_decision,
            "execution_id": execution_id,
        }
        
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
        if base_done and (not req_sa or sla_agent_status in ("OK", "OK_WITH_SLO")):
            lifecycle["COMPLETED"] = datetime.now(timezone.utc).isoformat()
        elif decision == "ACCEPT" and metadata_out.get("nasp_orchestration_attempted") and not orch_ok:
            metadata_out["failure_reason"] = "orchestration_failed"
            metadata_out["failure_code"] = "ORCHESTRATION_FAILED"
            lifecycle["FAILED"] = now_iso
        elif decision == "ACCEPT" and orch_ok and not bc_ok:
            metadata_out["failure_reason"] = metadata_out.get("failure_reason") or "blockchain_failed"
            metadata_out["failure_code"] = metadata_out.get("failure_code") or "BLOCKCHAIN_FAILED"
            lifecycle["FAILED"] = now_iso
        elif decision == "ACCEPT" and base_done and req_sa and sla_agent_status not in (
            "OK",
            "OK_WITH_SLO",
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

        _ensure_telemetry_v2_flags(metadata_out)

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


@router.get("/status/{sla_id}", response_model=SLAStatusResponse)
async def get_sla_status(sla_id: str):
    """
    Status do SLA
    
    Consulta em tempo real ao NASP - SEM cache local
    """
    try:
        result = await nasp_service.get_sla_status(sla_id)
        
        return SLAStatusResponse(
            sla_id=sla_id,
            status=result.get("status", "unknown"),
            tenant_id=result.get("tenant_id", ""),
            intent_id=result.get("intent_id"),
            nest_id=result.get("nest_id"),
            created_at=result.get("created_at"),
            updated_at=result.get("updated_at")
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
