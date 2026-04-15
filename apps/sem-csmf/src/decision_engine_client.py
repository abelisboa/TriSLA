"""
HTTP Client - SEM-CSMF
Cliente para comunicação HTTP com Decision Engine (Interface I-01)
Substitui comunicação gRPC por HTTP REST
"""

import math
import os
import requests
from typing import Dict, Any, Optional
from opentelemetry import trace
import logging

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Decision Engine HTTP endpoint
DECISION_ENGINE_URL = os.getenv(
    "DECISION_ENGINE_URL",
    "http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate"
)
PORTAL_PROM_QUERY_URL = os.getenv(
    "PORTAL_PROM_QUERY_URL",
    "http://trisla-portal-backend.trisla.svc.cluster.local:8001/api/v1/prometheus/query",
)

# Timeout curto para não bloquear o fluxo de intents (segundos)
SEM_PRB_PROM_TIMEOUT = float(os.getenv("SEM_PRB_PROM_TIMEOUT", "3.0"))

# PROMPT_116: preferir proxy UE/UPF antes do simulador; override via SEM_PRB_JOB_PRIORITY.
_SEM_PRB_JOB_PRIORITY = tuple(
    j.strip()
    for j in (os.getenv("SEM_PRB_JOB_PRIORITY") or "").split(",")
    if j.strip()
) or ("trisla-ran-ue-upf-proxy", "trisla-prb-simulator")

# Core CPU: % 0–100 via uso agregado TriSLA / cores da máquina; sem machine_cpu_cores → escala “cores-equivalent %”.
_CORE_CPU_QUERY_PCT = (
    '100 * sum(rate(process_cpu_seconds_total{job=~"trisla-.*"}[1m])) '
    "/ sum(machine_cpu_cores)"
)
_CORE_CPU_QUERY_PCT_SUM_ONLY = (
    '100 * sum(rate(process_cpu_seconds_total{job=~"trisla-.*"}[1m]))'
)

# Transporte: média móvel curta para RTT estável; fallback por série única.
_TRANSPORT_LATENCY_QUERY = (
    'avg_over_time(probe_duration_seconds{job=~"probe/.*"}[30s])'
)
_TRANSPORT_LATENCY_FALLBACK = "avg_over_time(probe_duration_seconds[30s])"

# Configuração de timeout
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10.0"))  # segundos


class DecisionEngineHTTPClient:
    """Cliente HTTP para Decision Engine (Interface I-01)"""
    
    def __init__(self):
        self.base_url = DECISION_ENGINE_URL
        logger.info(f"Decision Engine HTTP Client inicializado: {self.base_url}")

    @staticmethod
    def _extract_ran_prb_from_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[float]:
        """Prioridade A: PRB já presente em metadata (vários formatos legados)."""
        if not isinstance(metadata, dict):
            return None
        candidates = [
            (((metadata.get("telemetry_snapshot") or {}).get("ran") or {}).get("prb_utilization")),
            ((metadata.get("ran") or {}).get("prb_utilization")),
            metadata.get("prb_utilization"),
            metadata.get("ran_prb"),
        ]
        for value in candidates:
            try:
                if value is None:
                    continue
                return float(value)
            except (TypeError, ValueError):
                continue
        return None

    @staticmethod
    def _parse_prom_sample_value(series: Dict[str, Any]) -> Optional[float]:
        value = (series or {}).get("value")
        if not isinstance(value, list) or len(value) < 2:
            return None
        try:
            return float(value[1])
        except (TypeError, ValueError):
            return None

    def _prometheus_instant_for_job(
        self,
        query: str,
        *,
        prefer_job: Optional[str] = "trisla-prb-simulator",
    ) -> Optional[float]:
        """
        Prioridade B: instant query via portal-backend (proxy Prometheus).
        Se prefer_job estiver definido e houver várias séries, escolhe esse job.
        """
        try:
            resp = requests.get(
                PORTAL_PROM_QUERY_URL,
                params={"query": query},
                timeout=SEM_PRB_PROM_TIMEOUT,
            )
            resp.raise_for_status()
            payload = resp.json() if resp.content else {}
            if payload.get("status") != "success":
                logger.warning(
                    "[PRB RESOLUTION] prometheus api status=%s error_type=%s",
                    payload.get("status"),
                    (payload.get("errorType") or payload.get("error")),
                )
                return None
            results = (payload.get("data") or {}).get("result") or []
            if not isinstance(results, list) or not results:
                return None
            if prefer_job:
                for series in results:
                    job = ((series or {}).get("metric") or {}).get("job")
                    if job == prefer_job:
                        v = self._parse_prom_sample_value(series)
                        if v is not None:
                            return v
            for series in results:
                v = self._parse_prom_sample_value(series)
                if v is not None:
                    return v
            return None
        except requests.exceptions.Timeout:
            logger.warning("[PRB RESOLUTION] prometheus timeout url=%s", PORTAL_PROM_QUERY_URL)
            return None
        except Exception as exc:
            logger.warning("[PRB RESOLUTION] prometheus request failed: %s", exc)
            return None

    def _fetch_ran_prb_from_prometheus(self) -> Optional[float]:
        """trisla_ran_prb_utilization: proxy UE/UPF (PROMPT_116) antes do simulador de laboratório."""
        for job in _SEM_PRB_JOB_PRIORITY:
            v = self._prometheus_instant_for_job(
                f'trisla_ran_prb_utilization{{job="{job}"}}',
                prefer_job=job,
            )
            if v is not None:
                return v
        return self._prometheus_instant_for_job(
            "trisla_ran_prb_utilization",
            prefer_job=None,
        )

    def fetch_prometheus_metric(
        self,
        query: str,
        *,
        prefer_job: Optional[str] = None,
    ) -> Optional[float]:
        """Instant query via portal-backend (proxy Prometheus)."""
        return self._prometheus_instant_for_job(query, prefer_job=prefer_job)

    @staticmethod
    def _clamp_cpu_percent(value: Any) -> Optional[float]:
        """Garante cpu_utilization semântica em % real 0–100."""
        if value is None:
            return None
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return None

    def _fetch_core_cpu_percent(self) -> Optional[float]:
        """CPU % cluster-aware; fallback sem machine_cpu_cores = cores-equivalent scaled to %."""
        v = self.fetch_prometheus_metric(_CORE_CPU_QUERY_PCT, prefer_job=None)
        if v is not None and math.isfinite(float(v)):
            return float(v)
        v2 = self.fetch_prometheus_metric(_CORE_CPU_QUERY_PCT_SUM_ONLY, prefer_job=None)
        if v2 is not None and math.isfinite(float(v2)):
            return float(v2)
        return None

    def _extract_or_fetch_telemetry(
        self, metadata: Optional[Dict[str, Any]]
    ) -> tuple[Dict[str, Any], str]:
        """
        Monta telemetry_snapshot {ran, transport, core} com PRB (metadata/Prometheus)
        e, em falta, transporte/core via Prometheus — sem alterar fluxo de decisão downstream.
        Retorna (telemetry_dict, prb_source) com prb_source ∈ {metadata, prometheus, none}.
        """
        telemetry: Dict[str, Any] = {"ran": {}, "transport": {}, "core": {}}
        prb_source = "none"

        md = metadata if isinstance(metadata, dict) else {}
        ts_in = md.get("telemetry_snapshot")
        if isinstance(ts_in, dict):
            r, t, c = ts_in.get("ran") or {}, ts_in.get("transport") or {}, ts_in.get("core") or {}
            if isinstance(r, dict):
                telemetry["ran"].update(r)
            if isinstance(t, dict):
                telemetry["transport"].update(t)
            if isinstance(c, dict):
                telemetry["core"].update(c)

        prb_val = None
        if telemetry["ran"].get("prb_utilization") is not None:
            try:
                prb_val = float(telemetry["ran"]["prb_utilization"])
                prb_source = "metadata_snapshot"
            except (TypeError, ValueError):
                prb_val = None
        if prb_val is None:
            from_md = self._extract_ran_prb_from_metadata(metadata)
            if from_md is not None:
                prb_val = float(from_md)
                prb_source = "metadata"
        if prb_val is None:
            from_prom = self._fetch_ran_prb_from_prometheus()
            if from_prom is not None:
                prb_val = float(from_prom)
                prb_source = "prometheus"
        if prb_val is not None:
            telemetry["ran"]["prb_utilization"] = prb_val

        need_transport = (
            telemetry["transport"].get("latency_ms") is None
            and telemetry["transport"].get("rtt") is None
        )
        if need_transport:
            lat_s = self.fetch_prometheus_metric(
                _TRANSPORT_LATENCY_QUERY, prefer_job=None
            )
            if lat_s is None:
                lat_s = self.fetch_prometheus_metric(
                    _TRANSPORT_LATENCY_FALLBACK, prefer_job=None
                )
            if lat_s is not None:
                telemetry["transport"]["latency_ms"] = float(lat_s) * 1000.0
            else:
                telemetry["transport"]["latency_ms"] = None
            _lat_ms = telemetry["transport"].get("latency_ms")
            if _lat_ms is not None:
                print(f"[TRANSPORT TELEMETRY] latency_ms={float(_lat_ms):.2f}")
                logger.info("[TRANSPORT TELEMETRY] latency_ms=%.2f", float(_lat_ms))
            else:
                print("[TRANSPORT TELEMETRY] latency_ms=None")
                logger.info("[TRANSPORT TELEMETRY] latency_ms=None")

        if telemetry["core"].get("cpu_utilization") is None:
            cpu_pct = self._fetch_core_cpu_percent()
            if cpu_pct is not None:
                telemetry["core"]["cpu_utilization"] = cpu_pct

        if telemetry["core"].get("memory_utilization") is None:
            mem_raw = self.fetch_prometheus_metric(
                "process_resident_memory_bytes", prefer_job=None
            )
            if mem_raw is not None:
                telemetry["core"]["memory_utilization"] = float(mem_raw)

        _cpu_clamped = self._clamp_cpu_percent(telemetry["core"].get("cpu_utilization"))
        if _cpu_clamped is not None:
            telemetry["core"]["cpu_utilization"] = _cpu_clamped
        elif telemetry["core"].get("cpu_utilization") is not None:
            telemetry["core"].pop("cpu_utilization", None)

        _mem_log = telemetry["core"].get("memory_utilization")
        if _cpu_clamped is not None:
            print(f"[CORE TELEMETRY] cpu_percent={_cpu_clamped:.2f} mem={_mem_log}")
            logger.info(
                "[CORE TELEMETRY] cpu_percent=%.2f mem=%s", _cpu_clamped, _mem_log
            )
        else:
            print(f"[CORE TELEMETRY] cpu_percent=None mem={_mem_log}")
            logger.info("[CORE TELEMETRY] cpu_percent=None mem=%s", _mem_log)

        return telemetry, prb_source

    @staticmethod
    def _build_telemetry_features(
        telemetry: Dict[str, Any], metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """PROMPT_132 — features compostas opcionais para o Decision Engine (context.telemetry_features)."""
        ran = telemetry.get("ran") or {}
        prb = ran.get("prb_utilization")
        try:
            prb_current = float(prb) if prb is not None else None
        except (TypeError, ValueError):
            prb_current = None

        def _band_prb(p: Optional[float]) -> str:
            if p is None:
                return "unknown"
            if p < 40:
                return "low"
            if p < 75:
                return "medium"
            return "high"

        md = metadata if isinstance(metadata, dict) else {}
        rp = md.get("resource_pressure")
        try:
            rp_f = float(rp) if rp is not None else None
        except (TypeError, ValueError):
            rp_f = None

        def _band_press(p: Optional[float]) -> str:
            if p is None:
                return "unknown"
            if p < 0.35:
                return "low"
            if p < 0.65:
                return "medium"
            return "high"

        completeness = 0
        n = 0
        if prb_current is not None:
            n += 1
            completeness += 1
        tr = telemetry.get("transport") or {}
        if tr.get("latency_ms") is not None or tr.get("rtt") is not None:
            n += 1
            completeness += 1
        cr = telemetry.get("core") or {}
        if cr.get("cpu_utilization") is not None:
            n += 1
            completeness += 1
        tel_frac = float(completeness) / float(n) if n else 0.0

        feas_band = "unknown"
        if isinstance(md.get("feasibility_score"), (int, float)):
            feas_band = "high" if float(md["feasibility_score"]) >= 0.7 else "medium"

        return {
            "prb_current": prb_current,
            "prb_band": _band_prb(prb_current),
            "resource_pressure_band": _band_press(rp_f),
            "feasibility_band": feas_band,
            "telemetry_completeness": round(tel_frac, 4),
        }
    
    async def send_nest_metadata(
        self,
        intent_id: str,
        nest_id: str,
        tenant_id: Optional[str],
        service_type: str,
        sla_requirements: Dict[str, Any],
        nest_status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envia metadados de NEST para Decision Engine via HTTP POST
        
        Payload esperado pelo Decision Engine:
        {
            "intent_id": str,
            "nest_id": str,
            "tenant_id": str,
            "service_type": str,
            "sla_requirements": dict,
            "nest_status": str,
            "metadata": dict (opcional)
        }
        """
        with tracer.start_as_current_span("send_nest_metadata_http") as span:
            span.set_attribute("intent.id", intent_id)
            span.set_attribute("nest.id", nest_id)
            span.set_attribute("decision_engine.url", self.base_url)
            
            try:
                # Montar payload conforme contrato do Decision Engine
                safe_metadata = metadata or {}
                payload = {
                    "intent": {
                        "intent_id": intent_id,
                        "intent": safe_metadata.get("original_text") or safe_metadata.get("intent") or "",
                        "service_type": service_type,
                        "sla_requirements": sla_requirements,
                        "tenant_id": tenant_id or "default",
                    },
                    "intent_id": intent_id,
                    "nest_id": nest_id,
                    "tenant_id": tenant_id or "default",
                    "service_type": service_type,
                    "sla_requirements": sla_requirements,
                    "nest_status": nest_status,
                }
                
                # Adicionar metadata se fornecido
                if metadata:
                    payload["metadata"] = metadata

                # FASE 1R: snapshot multi-domínio (PRB + transporte + core) no payload.
                telemetry, prb_source = self._extract_or_fetch_telemetry(metadata)
                prb_float = telemetry["ran"].get("prb_utilization")
                if prb_float is not None:
                    logger.info("[PRB RESOLUTION] source=%s prb=%s", prb_source, prb_float)
                    print(f"[PRB RESOLUTION] source={prb_source} prb={prb_float}")
                else:
                    logger.warning("[PRB RESOLUTION] source=none prb_missing_in_telemetry")
                    print("[PRB RESOLUTION] source=none prb_missing_in_telemetry")
                payload["telemetry_snapshot"] = telemetry
                features = self._build_telemetry_features(telemetry, safe_metadata)
                payload["context"] = {"telemetry_features": features}
                strict_tf = (
                    os.getenv("SEM_TELEMETRY_FEATURES_STRICT", "false").lower() == "true"
                )
                if strict_tf and float(features.get("telemetry_completeness") or 0) < 1.0:
                    logger.warning(
                        "[TELEMETRY_FEATURES] strict incomplete completeness=%s",
                        features.get("telemetry_completeness"),
                    )
                
                logger.info(
                    f"Enviando NEST metadata para Decision Engine: "
                    f"intent_id={intent_id}, nest_id={nest_id}"
                )
                
                # Fazer requisição HTTP POST
                # FIX: nunca enviar 'decision' como input ao Decision Engine

                if isinstance(payload, dict):

                    payload.pop('decision', None)

                print("DECISION_ENGINE_PAYLOAD=", payload)
                response = requests.post(
                    self.base_url,
                    json=payload,
                    timeout=HTTP_TIMEOUT,
                    headers={"Content-Type": "application/json"}
                )
                print("DECISION_ENGINE_STATUS=", response.status_code)
                print("DECISION_ENGINE_BODY=", response.text)
                
                # Verificar status HTTP
                response.raise_for_status()
                
                # Parsear resposta JSON
                result = response.json()
                print("DECISION_ENGINE_RAW=", result)
                
                # Normalizar resposta para compatibilidade com código existente
                decision_action = (result.get("action") or "").upper()

                if decision_action in ["AC", "ACCEPT"]:
                    mapped_decision = "ACCEPT"
                elif decision_action in ["REJ", "REJECT"]:
                    mapped_decision = "REJECT"
                elif decision_action in ["RENEG", "RENEGOTIATE"]:
                    mapped_decision = "RENEGOTIATE"
                else:
                    mapped_decision = "REJECT"

                # O /evaluate retorna latência ML dentro de metadata, não no topo do JSON.
                _md = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
                _ml_lat = result.get("ml_prediction_latency_ms")
                if _ml_lat is None:
                    _ml_lat = _md.get("ml_prediction_latency_ms")
                _ml_conf = result.get("ml_confidence")
                if _ml_conf is None:
                    _ml_conf = _md.get("ml_confidence")

                decision_response = {
                    "success": result.get("success", True),
                    "decision_id": result.get("decision_id"),
                    "decision": mapped_decision,
                    "action": decision_action,
                    "message": result.get("message", "Decision processed successfully"),
                    "status_code": result.get("status_code", 200),
                    "reasoning": result.get("reasoning"),
                    "confidence": result.get("confidence"),
                    "domains": result.get("domains"),
                    "ml_risk_score": result.get("ml_risk_score"),
                    "ml_prediction_latency_ms": _ml_lat,
                    "ml_confidence": _ml_conf,
                    "metadata": result.get("metadata"),
                }
                
                if decision_response.get("decision_id"):
                    span.set_attribute("decision.id", decision_response.get("decision_id"))
                span.set_attribute("decision.success", decision_response.get("success", False))
                span.set_attribute("http.status_code", response.status_code)
                
                logger.info(
                    f"Resposta do Decision Engine: success={decision_response.get('success')}, "
                    f"decision_id={decision_response.get('decision_id')}"
                )
                
                return decision_response
                
            except requests.exceptions.Timeout as e:
                error_msg = f"Timeout ao comunicar com Decision Engine: {str(e)}"
                logger.error(error_msg)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                span.set_attribute("http.error", "timeout")
                
                return {
                    "success": False,
                    "decision_id": None,
                    "decision": "REJECT",
                    "message": error_msg,
                    "status_code": 504,
                    "reasoning": None,
                    "confidence": None,
                    "domains": None,
                    "metadata": None,
                }
                
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Erro de conexão com Decision Engine: {str(e)}"
                logger.error(error_msg)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                span.set_attribute("http.error", "connection_error")
                
                return {
                    "success": False,
                    "decision_id": None,
                    "decision": "REJECT",
                    "message": error_msg,
                    "status_code": 503,
                    "reasoning": None,
                    "confidence": None,
                    "domains": None,
                    "metadata": None,
                }
                
            except requests.exceptions.HTTPError as e:
                error_msg = f"Erro HTTP ao comunicar com Decision Engine: {str(e)}"
                logger.error(error_msg)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                span.set_attribute("http.status_code", e.response.status_code if hasattr(e, 'response') else 500)
                
                return {
                    "success": False,
                    "decision_id": None,
                    "decision": "REJECT",
                    "message": error_msg,
                    "status_code": e.response.status_code if hasattr(e, 'response') else 500,
                    "reasoning": None,
                    "confidence": None,
                    "domains": None,
                    "metadata": None,
                }
                
            except Exception as e:
                error_msg = f"Erro inesperado ao comunicar com Decision Engine: {str(e)}"
                logger.error(error_msg, exc_info=True)
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
                
                return {
                    "success": False,
                    "decision_id": None,
                    "decision": "REJECT",
                    "message": error_msg,
                    "status_code": 500,
                    "reasoning": None,
                    "confidence": None,
                    "domains": None,
                    "metadata": None,
                }
    
    async def get_decision_status(self, decision_id: str, intent_id: str) -> Optional[Dict[str, Any]]:
        """
        Consulta status de decisão (se o Decision Engine expor endpoint para isso)
        Por enquanto, retorna None pois o endpoint pode não estar disponível
        """
        logger.debug("get_decision_status não é necessário para HTTP client (status via /evaluate)")
        return None
    
    def close(self):
        """Método de compatibilidade (não necessário para HTTP, mas mantido para compatibilidade)"""
        logger.debug("HTTP client close() chamado (no-op para HTTP)")


# Alias para compatibilidade com código existente
DecisionEngineClient = DecisionEngineHTTPClient
DecisionEngineClientWithRetry = DecisionEngineHTTPClient

