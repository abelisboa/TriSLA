import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict

import httpx
import requests
from fastapi import HTTPException
from src.domain_actions.translator import translate_sla_to_domain_actions
from src.observability.distributed_trace import (
    build_distributed_traceability,
    child_trace,
    inject_http_headers,
    merge_trace_into_metadata,
    new_root_trace,
    trace_from_metadata,
)

logger = logging.getLogger(__name__)


class NASPService:
    def __init__(self):
        # PROMPT_127: stacks experimentais apontam cada portal a um SEM-CSMF distinto (DNS interno).
        self.sem_base = os.getenv(
            "SEM_CSMF_URL", "http://trisla-sem-csmf:8080"
        ).rstrip("/")
        self.sem_url = f"{self.sem_base}/health"
        self.bc_url = "http://trisla-bc-nssmf:8083/health"
        self.bc_nssmf_url = "http://trisla-bc-nssmf:8083"
        self.nasp_adapter_url = os.getenv(
            "NASP_ADAPTER_BASE_URL",
            "http://trisla-nasp-adapter.trisla.svc.cluster.local:8085",
        )

    def _probe(self, name, url):
        try:
            r = requests.get(url, timeout=3)
            return {
                "module": name,
                "reachable": r.ok,
                "status_code": r.status_code,
                "detail": "ok"
            }
        except Exception as e:
            return {
                "module": name,
                "reachable": False,
                "detail": str(e)
            }

    def check_sem_csmf(self):
        return self._probe("sem-csmf", self.sem_url)

    def check_bc_nssmf(self):
        return self._probe("bc-nssmf", self.bc_url)

    def check_all_nasp_modules(self):
        return {
            "sem_csmf": self._probe("sem-csmf", self.sem_url),
            "ml_nsmf": self._probe("ml-nsmf", "http://trisla-ml-nsmf:8081/health"),
            "decision": self._probe("decision-engine", "http://trisla-decision-engine:8082/health"),
            "bc_nssmf": self._probe("bc-nssmf", self.bc_url),
            "sla_agent": self._probe("sla-agent", "http://trisla-sla-agent-layer:8084/health"),
        }

    async def call_sem_csmf(self, intent_text: str, tenant_id: str, headers: dict | None = None):
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.sem_base}/api/v1/interpret",
                json={
                    "intent": intent_text,
                    "tenant_id": tenant_id
                },
                headers=headers or {},
            )
            response.raise_for_status()
            return response.json()

    async def submit_template_to_nasp(self, nest_template: dict, tenant_id: str):
        upstream_metadata = nest_template.get("metadata")
        metadata_for_sem = upstream_metadata if isinstance(upstream_metadata, dict) else {}
        root_trace = trace_from_metadata(metadata_for_sem) or new_root_trace("portal-backend")
        trace_hops: list[dict] = [dict(root_trace)]

        # PASSO 2 — extrair intent a partir do input recebido.
        # O SEM-CSMF /api/v1/interpret exige campo "intent" não vazio.
        sla_requirements = nest_template.get("sla_requirements") or {}
        intent = (
            nest_template.get("intent")
            or nest_template.get("service_name")
            or sla_requirements.get("intent")
            or sla_requirements.get("original_text")
            or sla_requirements.get("service_name")
            or f"SLA submission for template {nest_template.get('template_id', 'unknown')}"
        )

        t0 = time.perf_counter()
        sem_interpret_trace = child_trace(root_trace, "sem-csmf")
        interpret_headers = inject_http_headers({}, sem_interpret_trace)
        interpret_result = await self.call_sem_csmf(intent, tenant_id, headers=interpret_headers)
        trace_hops.append(dict(sem_interpret_trace))
        t1 = time.perf_counter()
        rtt_interpret_ms = (t1 - t0) * 1000
        internal = interpret_result.get("sem_csmf_internal_latency_ms")
        try:
            semantic_parsing_latency_ms = (
                float(internal) if internal is not None else rtt_interpret_ms
            )
        except (TypeError, ValueError):
            semantic_parsing_latency_ms = rtt_interpret_ms

        # PASSO 2/4 — extrair classificação semântica retornada pelo SEM-CSMF
        service_type = (
            interpret_result.get("service_type")
            or interpret_result.get("recommended_slice")
            or interpret_result.get("slice_type")
        )

        # Requisitos encaminhados ao SEM-CSMF (equivalente ao submit: form_values + metadados do template)
        sla_requirements_forward = dict(nest_template.get("sla_requirements") or {})
        # Normalização mínima de aliases para manter contrato legado do portal
        # sem alterar a lógica de decisão no Decision Engine.
        if (
            "throughput" not in sla_requirements_forward
            and "bandwidth" in sla_requirements_forward
        ):
            try:
                sla_requirements_forward["throughput"] = float(
                    sla_requirements_forward.get("bandwidth")
                )
            except Exception:
                pass
        if (
            "reliability" not in sla_requirements_forward
            and "availability" in sla_requirements_forward
        ):
            try:
                availability = float(sla_requirements_forward.get("availability"))
                # availability recebida como 0-100 no portal
                sla_requirements_forward["reliability"] = (
                    availability / 100.0 if availability > 1.0 else availability
                )
            except Exception:
                pass
        if nest_template.get("template_id") is not None:
            sla_requirements_forward.setdefault(
                "template_id", nest_template.get("template_id")
            )
        sla_type_forward = (
            nest_template.get("sla_type")
            or nest_template.get("type")
            or nest_template.get("slice_type")
        )
        if sla_type_forward is not None:
            sla_requirements_forward.setdefault("sla_type", sla_type_forward)
        if nest_template.get("form_values") is not None:
            sla_requirements_forward.setdefault(
                "form_values", nest_template.get("form_values")
            )

        upstream_metadata = nest_template.get("metadata")
        metadata_for_sem = upstream_metadata if isinstance(upstream_metadata, dict) else None
        if metadata_for_sem is None:
            metadata_for_sem = {}
        metadata_for_sem = merge_trace_into_metadata(metadata_for_sem, root_trace)

        t2 = time.perf_counter()
        sem_intent_trace = child_trace(root_trace, "sem-csmf")
        sem_headers = inject_http_headers({}, sem_intent_trace)
        async with httpx.AsyncClient(timeout=30.0) as client:
            intent_payload = {
                "service_type": service_type,
                "intent": intent,
                "tenant_id": tenant_id,
                "sla_requirements": sla_requirements_forward,
            }
            if metadata_for_sem:
                intent_payload["metadata"] = metadata_for_sem
            response = await client.post(
                f"{self.sem_base}/api/v1/intents",
                json=intent_payload,
                headers=sem_headers,
            )
            response.raise_for_status()
            sem_result = response.json()
            trace_hops.append(dict(sem_intent_trace))
            t3 = time.perf_counter()
            decision_duration_ms = (t3 - t2) * 1000
            admission_time_total_ms = (t3 - t0) * 1000

            # Caminho único: SEM-CSMF orquestra Decision Engine internamente; portal não chama /evaluate.
            merged = dict(sem_result)
            merged["sem_csmf_status"] = "OK"
            if merged.get("metadata") and (
                "ml_risk_score" in merged["metadata"]
                or "ml_confidence" in merged["metadata"]
            ):
                merged["ml_nsmf_status"] = "OK"
            else:
                merged["ml_nsmf_status"] = "SKIPPED"
            decision = (merged.get("decision") or "").upper()
            md_sem = merged.get("metadata") if isinstance(merged.get("metadata"), dict) else {}
            authority_ok = (
                md_sem.get("decision_engine_orchestration_authority") is True
                and isinstance(md_sem.get("orchestration_required"), bool)
            )
            if authority_ok:
                should_orchestrate = bool(md_sem.get("orchestration_required"))
            else:
                should_orchestrate = decision == "ACCEPT"

            orch_payload = self._build_orchestration_payload(
                merged=merged,
                service_type=service_type,
                sla_requirements=sla_requirements_forward,
                tenant_id=tenant_id,
            )
            if authority_ok and isinstance(md_sem.get("orchestration_intent"), dict) and md_sem.get(
                "orchestration_intent"
            ):
                orch_payload = {**orch_payload, **md_sem["orchestration_intent"]}
            orch_meta = {
                "nasp_orchestration_attempted": False,
                "nasp_orchestration_status": "SKIPPED",
                "nasp_latency_ms": None,
                "nasp_latency_available": False,
                "nasp_orchestration_response": {
                    "reason": f"decision={decision or 'UNKNOWN'}",
                    "endpoint": "/api/v1/nsi/instantiate",
                },
            }
            if decision == "ACCEPT" and should_orchestrate:
                orch_meta["nasp_orchestration_requested_at"] = datetime.now(
                    timezone.utc
                ).isoformat()
                logger.info(
                    "[NASP ORCH] calling adapter endpoint=%s nsiId=%s decision=%s",
                    "/api/v1/nsi/instantiate",
                    orch_payload.get("nsiId"),
                    decision,
                )
                orch_meta["nasp_orchestration_attempted"] = True
                nasp_t0 = time.perf_counter()
                try:
                    async with httpx.AsyncClient(timeout=20.0) as orch_client:
                        orch_response = await orch_client.post(
                            f"{self.nasp_adapter_url}/api/v1/nsi/instantiate",
                            json=orch_payload,
                        )
                        orch_response.raise_for_status()
                        try:
                            orch_body = orch_response.json()
                        except Exception:
                            orch_body = {}
                    body_ok = True
                    if isinstance(orch_body, dict) and "success" in orch_body:
                        body_ok = bool(orch_body.get("success"))
                    nsi_id = None
                    if isinstance(orch_body, dict):
                        nsi_id = (
                            (orch_body.get("nsi") or {}).get("spec", {}).get("nsiId")
                            or (orch_body.get("nsi") or {}).get("metadata", {}).get(
                                "name"
                            )
                            or orch_payload.get("nsiId")
                        )
                    if body_ok:
                        orch_meta["nasp_orchestration_status"] = "SUCCESS"
                        orch_meta["nasp_orchestration_response"] = {
                            "http_status": orch_response.status_code,
                            "success": True,
                            "nsi_id": nsi_id,
                        }
                        logger.info(
                            "[NASP ORCH] adapter response status=SUCCESS nsiId=%s",
                            nsi_id,
                        )
                    else:
                        orch_meta["nasp_orchestration_status"] = "ERROR"
                        orch_meta["nasp_orchestration_response"] = {
                            "http_status": orch_response.status_code,
                            "success": False,
                            "error": (
                                (orch_body or {}).get("error")
                                if isinstance(orch_body, dict)
                                else None
                            )
                            or (
                                (orch_body or {}).get("message")
                                if isinstance(orch_body, dict)
                                else None
                            ),
                            "nsi_id": nsi_id,
                        }
                        logger.error(
                            "[NASP ORCH] adapter body success=false http=%s",
                            orch_response.status_code,
                        )
                except httpx.HTTPStatusError as e:
                    orch_meta["nasp_orchestration_status"] = "ERROR"
                    orch_meta["nasp_orchestration_response"] = {
                        "http_status": e.response.status_code,
                        "error": e.response.text[:300],
                    }
                    logger.error(
                        "[NASP ORCH] failed status_code=%s body=%s",
                        e.response.status_code,
                        e.response.text[:300],
                    )
                except Exception as e:
                    orch_meta["nasp_orchestration_status"] = "ERROR"
                    orch_meta["nasp_orchestration_response"] = {
                        "error": str(e)[:300],
                    }
                    logger.error("[NASP ORCH] failed exception=%s", e, exc_info=True)
                finally:
                    nasp_t1 = time.perf_counter()
                    orch_meta["nasp_latency_ms"] = (nasp_t1 - nasp_t0) * 1000.0
                    orch_meta["nasp_latency_available"] = True
            elif decision == "ACCEPT" and not should_orchestrate:
                orch_meta["nasp_orchestration_response"] = {
                    "reason": "ACCEPT_but_orchestration_not_required_by_authority_fields",
                    "endpoint": "/api/v1/nsi/instantiate",
                }
            elif decision == "RENEGOTIATE":
                orch_meta["nasp_orchestration_response"] = {
                    "reason": "decision=RENEGOTIATE (intermediate decision)",
                    "endpoint": "/api/v1/nsi/instantiate",
                }
            elif decision == "REJECT":
                orch_meta["nasp_orchestration_response"] = {
                    "reason": "decision=REJECT",
                    "endpoint": "/api/v1/nsi/instantiate",
                }

            md = merged.get("metadata") if isinstance(merged.get("metadata"), dict) else {}
            telemetry_snapshot = (
                metadata_for_sem.get("telemetry_snapshot")
                if isinstance(metadata_for_sem, dict)
                else {}
            )
            if callable(translate_sla_to_domain_actions):
                try:
                    domain_actions = translate_sla_to_domain_actions(
                        sla=sla_requirements_forward,
                        decision={"decision": decision},
                        telemetry_snapshot=telemetry_snapshot if isinstance(telemetry_snapshot, dict) else {},
                    )
                    md["domain_actions"] = domain_actions
                except Exception as exc:
                    logger.warning("[NASP ORCH] domain_actions enrichment skipped: %s", exc)
            md.update(orch_meta)
            if authority_ok:
                md["decision_engine_orchestration_authority"] = True
                md.setdefault(
                    "orchestration_decision_source",
                    md_sem.get("orchestration_decision_source", "decision-engine"),
                )
            else:
                md["decision_engine_orchestration_authority"] = False
                md.setdefault(
                    "orchestration_authority_fallback_reason",
                    "orchestration_authority_fields_absent_using_legacy_accept_triggers_orchestration",
                )
            merged["metadata"] = md

            merged["orchestration_status"] = orch_meta.get("nasp_orchestration_status")
            orch_success = orch_meta.get("nasp_orchestration_status") == "SUCCESS"

            if decision == "ACCEPT" and orch_success:
                try:
                    # SEM /api/v1/intents não devolve sla_requirements no JSON; usar forward do submit.
                    bc_sla_req = merged.get("sla_requirements") or sla_requirements_forward
                    bc_payload = {
                        "intent_id": merged.get("intent_id"),
                        "nest_id": merged.get("nest_id"),
                        "sla_requirements": bc_sla_req,
                        "decision": decision,
                        "metadata": merged.get("metadata"),
                    }
                    bc_trace = child_trace(root_trace, "bc-nssmf")
                    bc_headers = inject_http_headers({}, bc_trace)
                    bc_t0 = time.perf_counter()
                    response = requests.post(
                        f"{self.bc_nssmf_url}/api/v1/register-sla",
                        json=bc_payload,
                        timeout=10,
                        headers=bc_headers,
                    )
                    bc_t1 = time.perf_counter()
                    trace_hops.append(dict(bc_trace))
                    merged["blockchain_transaction_latency_ms"] = (bc_t1 - bc_t0) * 1000
                    response.raise_for_status()
                    bc_result = response.json()
                    merged["bc_status"] = "COMMITTED"
                    merged["blockchain_status"] = "BLOCKCHAIN_REGISTERED"
                    merged["tx_hash"] = bc_result.get("tx_hash")
                    merged["block_number"] = bc_result.get("block_number")
                except Exception as e:
                    merged["bc_status"] = "BLOCKCHAIN_FAILED"
                    merged["blockchain_status"] = "BLOCKCHAIN_FAILED"
                    merged["bc_error"] = str(e)
            elif decision == "ACCEPT":
                merged["bc_status"] = "SKIPPED_ORCH_FAILED"
                merged["blockchain_status"] = "SKIPPED_ORCH_FAILED"
                merged["blockchain_transaction_latency_ms"] = None
                merged.pop("tx_hash", None)
                merged.pop("block_number", None)
            else:
                merged["bc_status"] = "SKIPPED"
                merged["blockchain_status"] = "SKIPPED"
            merged["semantic_parsing_latency_ms"] = semantic_parsing_latency_ms
            if interpret_result.get("sem_csmf_internal_latency_ms") is not None:
                try:
                    merged["sem_csmf_internal_latency_ms"] = float(
                        interpret_result["sem_csmf_internal_latency_ms"]
                    )
                except (TypeError, ValueError):
                    merged["sem_csmf_internal_latency_ms"] = None
            merged["decision_duration_ms"] = decision_duration_ms
            merged["admission_time_total_ms"] = admission_time_total_ms
            merged.setdefault("service_type", service_type)
            merged.setdefault("sla_requirements", sla_requirements_forward)
            md_final = merged.get("metadata") if isinstance(merged.get("metadata"), dict) else {}
            de_meta = trace_from_metadata(md_final)
            if de_meta and not any(h.get("service") == "decision-engine" for h in trace_hops):
                trace_hops.append({**de_meta, "service": "decision-engine"})
            md_final = merge_trace_into_metadata(md_final, root_trace)
            md_final["distributed_trace_hops"] = trace_hops
            md_final["distributed_traceability"] = build_distributed_traceability(
                root_trace, trace_hops
            )
            merged["metadata"] = md_final
            merged["trace_id"] = root_trace.get("trace_id")
            return merged

    def _build_orchestration_payload(
        self,
        merged: dict,
        service_type: str | None,
        sla_requirements: dict,
        tenant_id: str,
    ) -> dict:
        intent_id = (
            merged.get("nest_id")
            or merged.get("intent_id")
            or f"intent-{int(time.time() * 1000)}"
        )
        st = (
            service_type
            or merged.get("service_type")
            or sla_requirements.get("slice_type")
            or sla_requirements.get("type")
            or "eMBB"
        )
        return {
            "nsiId": str(intent_id),
            "serviceProfile": st,
            "service_type": st,
            "tenant_id": tenant_id,
            "sla_requirements": sla_requirements,
            "sla": sla_requirements,
            "source": "portal-backend-submit",
        }

    async def persist_intent_governance_metadata(
        self, intent_id: str, governance_fields: Dict[str, Any]
    ) -> bool:
        """
        Merge governance/on-chain fields into SEM intent extra_metadata (Sprint 10G.4).
        Non-fatal: submit may succeed even if SEM is temporarily unavailable.
        """
        if not intent_id or not governance_fields:
            return False
        url = f"{self.sem_base}/api/v1/intents/{intent_id}/governance-metadata"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.patch(url, json=governance_fields)
                response.raise_for_status()
                body = response.json()
                return bool(body.get("updated", True))
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "[GOV_PROPAGATION] SEM patch HTTP %s intent=%s: %s",
                    e.response.status_code,
                    intent_id,
                    e.response.text[:200],
                )
                return False
            except httpx.RequestError as e:
                logger.warning(
                    "[GOV_PROPAGATION] SEM patch connection intent=%s: %s",
                    intent_id,
                    e,
                )
                return False

    async def get_sla_status(self, sla_id: str) -> Dict[str, Any]:
        """Consulta status do intent/SLA no SEM-CSMF."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.sem_base}/api/v1/intents/{sla_id}",
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"SLA {sla_id} not found in NASP",
                    ) from e
                logger.error("SEM-CSMF status HTTP %s: %s", e.response.status_code, e.response.text)
                raise HTTPException(
                    status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                    detail=e.response.text,
                ) from e
            except httpx.RequestError as e:
                logger.error("SEM-CSMF status conexão: %s", e)
                raise HTTPException(status_code=503, detail=f"NASP offline: {e}") from e

    async def call_metrics(self, sla_id: str) -> Dict[str, Any]:
        """
        Métricas do SLA (contrato do router).
        Integração dedicada ao SLA-Agent não está neste serviço — retorno estruturado mínimo.
        """
        return {
            "sla_id": sla_id,
            "slice_status": None,
            "latency_ms": None,
            "jitter_ms": None,
            "throughput_ul": None,
            "throughput_dl": None,
            "packet_loss": None,
            "availability": None,
            "last_update": None,
            "tenant_id": None,
            "metrics": None,
        }


_service = NASPService()


def check_sem_csmf():
    return _service.check_sem_csmf()


def check_bc_nssmf():
    return _service.check_bc_nssmf()


def check_all_nasp_modules():
    return _service.check_all_nasp_modules()
