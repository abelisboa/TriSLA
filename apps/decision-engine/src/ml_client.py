"""
Cliente ML-NSMF - Decision Engine
Integração com ML-NSMF via HTTP REST (Interface I-05)
"""

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
                
                # Chamar endpoint de predição do ML-NSMF
                logger.info(f"Chamando ML-NSMF em {config.ml_nsmf_http_url}/api/v1/predict")
                response = await self.http_client.post(
                    f"{config.ml_nsmf_http_url}/api/v1/predict",
                    json=features
                )
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
                
                # Converter para MLPrediction
                prediction = MLPrediction(
                    risk_score=float(prediction_data.get("risk_score", 0.5)),
                    risk_level=RiskLevel(prediction_data.get("risk_level", "medium")),
                    confidence=float(prediction_data.get("confidence", 0.8)),
                    features_importance=data.get("explanation", {}).get("features_importance"),
                    explanation=data.get("explanation", {}).get("reasoning"),
                    timestamp=prediction_data.get("timestamp", "")
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
                    explanation=f"[FALLBACK] ML-NSMF não disponível: {str(e)}"
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
                    explanation=f"[FALLBACK] Erro ao obter predição: {str(e)}"
                )
    
    def _extract_features(self, decision_input: DecisionInput) -> Dict[str, Any]:
        """
        Extrai features do intent/nest para o ML
        Normaliza métricas (latency, throughput, reliability, etc.)
        Alinhado com modelo ML-NSMF v3.7.0
        """
        logger.debug(f"Extraindo features para slice_type={decision_input.intent.service_type.value}")
        features = {}
        sla_reqs = decision_input.intent.sla_requirements
        
        # Latência (ms)
        if "latency" in sla_reqs:
            latency_str = str(sla_reqs["latency"]).replace("ms", "").strip()
            try:
                features["latency"] = float(latency_str)
            except (ValueError, TypeError):
                features["latency"] = 0.0
        
        # Throughput (Mbps)
        if "throughput" in sla_reqs:
            throughput_str = str(sla_reqs["throughput"]).replace("Mbps", "").replace("Gbps", "000").strip()
            try:
                features["throughput"] = float(throughput_str)
            except (ValueError, TypeError):
                features["throughput"] = 0.0
        
        # Reliability
        if "reliability" in sla_reqs:
            features["reliability"] = float(sla_reqs.get("reliability", 0.99))
        else:
            features["reliability"] = 0.99
        
        # Jitter (ms)
        if "jitter" in sla_reqs:
            jitter_str = str(sla_reqs["jitter"]).replace("ms", "").strip()
            try:
                features["jitter"] = float(jitter_str)
            except (ValueError, TypeError):
                features["jitter"] = 0.0
        
        # Packet loss (inferido do reliability se não especificado)
        if "packet_loss" not in features:
            features["packet_loss"] = 1.0 - features.get("reliability", 0.99)
        
        # Tipo de slice (encoding numérico alinhado com modelo v3.7.0)
        # Modelo treinado com: {URLLC: 1, eMBB: 2, mMTC: 3}
        slice_type_map = {"URLLC": 1, "eMBB": 2, "mMTC": 3}
        features["slice_type"] = decision_input.intent.service_type.value  # Enviar string também
        features["slice_type_encoded"] = slice_type_map.get(
            decision_input.intent.service_type.value, 2  # Default: eMBB
        )
        
        # Recursos do NEST (se disponível)
        # Converter para formato esperado pelo predictor
        if decision_input.nest:
            resources = decision_input.nest.resources
            
            # CPU: converter cores para utilization (0-1)
            # Assumindo que 1 core = 100% utilization, normalizar para 0-1
            cpu_cores = float(resources.get("cpu", 0))
            # Se não especificado, usar default 0.5 (50% utilization)
            features["cpu_utilization"] = min(1.0, cpu_cores / 10.0) if cpu_cores > 0 else 0.5
            
            # Memory: converter GB para utilization (0-1)
            # Assumindo que 100GB = 100% utilization, normalizar
            memory_str = str(resources.get("memory", "0")).replace("Gi", "").replace("G", "").strip()
            try:
                memory_gb = float(memory_str) if memory_str else 0.0
                features["memory_utilization"] = min(1.0, memory_gb / 100.0) if memory_gb > 0 else 0.5
            except (ValueError, TypeError):
                features["memory_utilization"] = 0.5
            
            # Bandwidth: usar diretamente em Mbps
            bandwidth_str = str(resources.get("bandwidth", "0")).replace("Mbps", "").strip()
            try:
                features["network_bandwidth_available"] = float(bandwidth_str) if bandwidth_str else 500.0
            except (ValueError, TypeError):
                features["network_bandwidth_available"] = 500.0
        else:
            # Defaults se NEST não disponível
            features["cpu_utilization"] = 0.5
            features["memory_utilization"] = 0.5
            features["network_bandwidth_available"] = 500.0
        
        # Active slices count (se disponível no contexto ou NEST)
        if decision_input.context and "active_slices_count" in decision_input.context:
            features["active_slices_count"] = float(decision_input.context["active_slices_count"])
        elif decision_input.nest and decision_input.nest.metadata:
            features["active_slices_count"] = float(decision_input.nest.metadata.get("active_slices_count", 1))
        else:
            features["active_slices_count"] = 1.0  # Default
        
        return features
    
    async def close(self):
        """Fecha conexão HTTP"""
        await self.http_client.aclose()

