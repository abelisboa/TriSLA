"""
Cliente ML-NSMF - Decision Engine
Integração com ML-NSMF via HTTP REST (Interface I-05)
"""

import time

import httpx
from typing import Optional, Dict, Any
from opentelemetry import trace
import logging

from config import config
from models import MLPrediction, RiskLevel, DecisionInput

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class MLClient:
    """
    Cliente para comunicação com ML-NSMF (Interface I-05)
    Obtém previsão de viabilidade/risco para SLA
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=15.0)

    @staticmethod
    def _safe_float(value: Any, default: float) -> float:
        """Converte para float com fallback seguro para None/valores inválidos."""
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default
    
    async def predict_viability(self, decision_input: DecisionInput) -> Optional[MLPrediction]:
        """
        Prever viabilidade do SLA usando ML-NSMF
        
        Args:
            decision_input: Entrada agregada com intent e nest
        
        Returns:
            MLPrediction com risco estimado
        """
        with tracer.start_as_current_span("predict_viability_ml") as span:
            span.set_attribute("intent.id", decision_input.intent.intent_id)
            
            try:
                # Preparar features para o ML
                logger.debug(f"Extraindo features para intent_id={decision_input.intent.intent_id}")
                features = self._extract_features(decision_input)
                logger.debug(f"Features extraídas: {list(features.keys())}")
                logger.info("[ML PAYLOAD FINAL] %s", features)
                
                # Chamar endpoint de predição do ML-NSMF
                logger.info(f"Chamando ML-NSMF em {config.ml_nsmf_http_url}/api/v1/predict")
                t_req0 = time.perf_counter()
                response = await self.http_client.post(
                    f"{config.ml_nsmf_http_url}/api/v1/predict",
                    json=features
                )
                http_predict_ms = (time.perf_counter() - t_req0) * 1000.0
                response.raise_for_status()
                logger.debug(f"Resposta recebida do ML-NSMF: status={response.status_code}")
                
                data = response.json()
                prediction_data = data.get("prediction", {})
                
                # Verificar se modelo foi usado (não fallback)
                model_used = prediction_data.get("model_used", True)
                if not model_used:
                    logger.warning("⚠️ ML-NSMF usando modo fallback - modelo não disponível")
                    span.set_attribute("ml.fallback_mode", True)
                    span.set_attribute("ml.warning", "ML-NSMF usando modo fallback")
                else:
                    logger.debug("✅ ML-NSMF usando modelo real (não fallback)")
                
                # Extrair viability_score se disponível
                viability_score = prediction_data.get("viability_score")
                if viability_score is not None:
                    span.set_attribute("ml.viability_score", float(viability_score))

                raw_rs = prediction_data.get("raw_risk_score", None)
                adj_rs = prediction_data.get("slice_adjusted_risk_score", None)
                risk_main = self._safe_float(prediction_data.get("risk_score"), 0.5)
                raw_final = self._safe_float(raw_rs, risk_main) if raw_rs is not None else risk_main
                adj_final = self._safe_float(adj_rs, raw_final) if adj_rs is not None else raw_final
                dom_xai = prediction_data.get("slice_domain_xai") or {}
                dom = dom_xai.get("dominant_domain") or data.get("explanation", {}).get("dominant_domain")
                tops = dom_xai.get("top_factors") or data.get("explanation", {}).get("top_factors")

                # Converter para MLPrediction
                pdc = prediction_data.get("predicted_decision_class")
                cconf = prediction_data.get("classifier_confidence")
                if cconf is None:
                    cconf = prediction_data.get("confidence_score")

                _lat = prediction_data.get("latency_ms")
                if _lat is None:
                    _lat = prediction_data.get("prediction_latency_ms")
                if _lat is None and isinstance(data, dict):
                    _lat = data.get("latency_ms")
                if _lat is None:
                    _lat = http_predict_ms
                prediction = MLPrediction(
                    risk_score=risk_main,
                    risk_level=RiskLevel(prediction_data.get("risk_level", "medium")),
                    confidence=self._safe_float(prediction_data.get("confidence"), 0.8),
                    prediction_latency_ms=_lat,
                    features_importance=data.get("explanation", {}).get("features_importance"),
                    explanation=data.get("explanation", {}).get("reasoning"),
                    timestamp=prediction_data.get("timestamp"),
                    raw_risk_score=raw_final,
                    slice_adjusted_risk_score=adj_final,
                    dominant_domain=dom,
                    top_factors=tops if isinstance(tops, list) else None,
                    predicted_decision_class=pdc if isinstance(pdc, str) else None,
                    classifier_confidence=self._safe_float(cconf, 0.0) if cconf is not None else None,
                )
                
                # Adicionar viability_score ao explanation se disponível
                if viability_score is not None and prediction.explanation:
                    prediction.explanation = f"[viability_score={viability_score:.4f}] {prediction.explanation}"
                
                span.set_attribute("ml.risk_score", prediction.risk_score)
                span.set_attribute("ml.risk_level", prediction.risk_level.value)
                
                return prediction
                
            except httpx.HTTPError as e:
                logger.error(f"❌ Erro HTTP ao chamar ML-NSMF: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("ml.fallback_mode", True)
                span.set_attribute("ml.error", str(e))
                # Em caso de erro, retornar predição padrão (risco médio) com flag de fallback
                return MLPrediction(
                    risk_score=0.5,
                    risk_level=RiskLevel.MEDIUM,
                    confidence=0.5,
                    explanation=f"[FALLBACK] ML-NSMF não disponível: {str(e)}",
                    raw_risk_score=0.5,
                    slice_adjusted_risk_score=0.5,
                    predicted_decision_class=None,
                    classifier_confidence=0.0,
                )
            except Exception as e:
                logger.error(f"❌ Erro inesperado ao chamar ML-NSMF: {e}", exc_info=True)
                span.record_exception(e)
                span.set_attribute("ml.fallback_mode", True)
                span.set_attribute("ml.error", str(e))
                # Retornar predição padrão em caso de erro com flag de fallback
                return MLPrediction(
                    risk_score=0.5,
                    risk_level=RiskLevel.MEDIUM,
                    confidence=0.5,
                    explanation=f"[FALLBACK] Erro ao obter predição: {str(e)}",
                    raw_risk_score=0.5,
                    slice_adjusted_risk_score=0.5,
                    predicted_decision_class=None,
                    classifier_confidence=0.0,
                )
    
    def _extract_features(self, decision_input: DecisionInput) -> Dict[str, Any]:
        """
        Extrai features do intent/nest para o ML
        Normaliza métricas (latency, throughput, reliability, etc.)
        Alinhado com modelo ML-NSMF v3.7.0
        """
        logger.debug(f"Extraindo features para slice_type={decision_input.intent.service_type.value}")
        features = {"intent_id": decision_input.intent.intent_id}
        sla_reqs = decision_input.intent.sla_requirements
        
        # Latência (ms)
        if "latency" in sla_reqs:
            latency_str = str(sla_reqs["latency"]).replace("ms", "").strip()
            try:
                features["latency"] = float(latency_str)
            except (ValueError, TypeError):
                features["latency"] = 1.0
        else:
            features["latency"] = 1.0
        
        # Throughput (Mbps)
        if "throughput" in sla_reqs:
            throughput_str = str(sla_reqs["throughput"]).replace("Mbps", "").replace("Gbps", "000").strip()
            try:
                features["throughput"] = float(throughput_str)
            except (ValueError, TypeError):
                features["throughput"] = 2000.0
        else:
            features["throughput"] = 2000.0
        
        # Reliability
        if "reliability" in sla_reqs:
            features["reliability"] = self._safe_float(sla_reqs.get("reliability"), 0.99)
        else:
            features["reliability"] = 0.99
        
        # Jitter (ms) - default otimista controlado para cenário de baixo risco
        if "jitter" in sla_reqs:
            jitter_str = str(sla_reqs["jitter"]).replace("ms", "").strip()
            try:
                features["jitter"] = float(jitter_str)
            except (ValueError, TypeError):
                features["jitter"] = 0.1
        else:
            features["jitter"] = 0.1
        
        # Packet loss (inferido do reliability se não especificado)
        if "packet_loss" in sla_reqs:
            features["packet_loss"] = self._safe_float(sla_reqs.get("packet_loss"), 0.0001)
        else:
            features["packet_loss"] = max(0.0001, 1.0 - features.get("reliability", 0.99))
        
        # Tipo de slice (encoding numérico alinhado com modelo v3.7.0)
        # Modelo treinado com: {URLLC: 1, eMBB: 2, mMTC: 3}
        slice_type_map = {"URLLC": 1, "eMBB": 2, "mMTC": 3}
        features["slice_type"] = decision_input.intent.service_type.value  # Enviar string também
        features["slice_type_encoded"] = slice_type_map.get(
            decision_input.intent.service_type.value, 2  # Default: eMBB
        )
        
        # Campos que não vêm do submit devem usar defaults otimistas controlados.
        # Só usar valor explícito se vier em sla_requirements.
        features["cpu_utilization"] = self._safe_float(sla_reqs.get("cpu_utilization"), 0.1)
        features["memory_utilization"] = self._safe_float(sla_reqs.get("memory_utilization"), 0.1)
        features["network_bandwidth_available"] = self._safe_float(
            sla_reqs.get("network_bandwidth_available"), 10000.0
        )
        
        # Active slices count (se disponível no contexto ou NEST)
        if decision_input.context and "active_slices_count" in decision_input.context:
            features["active_slices_count"] = float(decision_input.context["active_slices_count"])
        elif decision_input.nest and decision_input.nest.metadata:
            features["active_slices_count"] = float(decision_input.nest.metadata.get("active_slices_count", 1))
        else:
            features["active_slices_count"] = 1.0  # Default

        # Fase 2: observabilidade — PRB + transporte + core no payload para o ML (enriquecimento).
        ts = (decision_input.context or {}).get("telemetry_snapshot") or {}
        ran_raw = (ts.get("ran") or {}).get("prb_utilization")
        try:
            features["ran_prb_utilization"] = (
                float(ran_raw) if ran_raw is not None else 0.0
            )
        except (TypeError, ValueError):
            features["ran_prb_utilization"] = 0.0

        transport = ts.get("transport") or {}
        core = ts.get("core") or {}
        lat_ms = transport.get("latency_ms")
        if lat_ms is None:
            lat_ms = transport.get("rtt")
        features["transport_latency_ms"] = self._safe_float(lat_ms, 0.0)
        # Snapshot: cpu_utilization já em % 0–100 (SEM-CSMF); ML recebe 0–1.
        features["core_cpu_utilization"] = (
            self._safe_float(core.get("cpu_utilization"), 0.0) / 100.0
        )
        features["core_memory_utilization"] = self._safe_float(
            core.get("memory_utilization"), 0.0
        )

        return features
    
    async def close(self):
        """Fecha conexão HTTP"""
        await self.http_client.aclose()

