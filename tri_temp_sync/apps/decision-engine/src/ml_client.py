"""
Cliente ML-NSMF - Decision Engine
Integração com ML-NSMF via HTTP REST (Interface I-05)
"""

import httpx
from typing import Optional, Dict, Any
from opentelemetry import trace

from config import config
from models import MLPrediction, RiskLevel, DecisionInput

tracer = trace.get_tracer(__name__)


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
                features = self._extract_features(decision_input)
                
                # Chamar endpoint de predição do ML-NSMF
                response = await self.http_client.post(
                    f"{config.ml_nsmf_http_url}/api/v1/predict",
                    json=features
                )
                response.raise_for_status()
                
                data = response.json()
                prediction_data = data.get("prediction", {})
                
                # Converter para MLPrediction
                prediction = MLPrediction(
                    risk_score=float(prediction_data.get("risk_score", 0.5)),
                    risk_level=RiskLevel(prediction_data.get("risk_level", "medium")),
                    confidence=float(prediction_data.get("confidence", 0.8)),
                    features_importance=data.get("explanation", {}).get("features_importance"),
                    explanation=data.get("explanation", {}).get("reasoning"),
                    timestamp=prediction_data.get("timestamp", "")
                )
                
                span.set_attribute("ml.risk_score", prediction.risk_score)
                span.set_attribute("ml.risk_level", prediction.risk_level.value)
                
                return prediction
                
            except httpx.HTTPError as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                # Em caso de erro, retornar predição padrão (risco médio)
                return MLPrediction(
                    risk_score=0.5,
                    risk_level=RiskLevel.MEDIUM,
                    confidence=0.5,
                    explanation=f"ML-NSMF não disponível: {str(e)}"
                )
            except Exception as e:
                span.record_exception(e)
                # Retornar predição padrão em caso de erro
                return MLPrediction(
                    risk_score=0.5,
                    risk_level=RiskLevel.MEDIUM,
                    confidence=0.5,
                    explanation=f"Erro ao obter predição: {str(e)}"
                )
    
    def _extract_features(self, decision_input: DecisionInput) -> Dict[str, Any]:
        """
        Extrai features do intent/nest para o ML
        Normaliza métricas (latency, throughput, reliability, etc.)
        """
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
        
        # Tipo de serviço (encoding numérico)
        service_type_map = {"eMBB": 1, "URLLC": 2, "mMTC": 3}
        features["service_type"] = service_type_map.get(
            decision_input.intent.service_type.value, 1
        )
        
        # Recursos do NEST (se disponível)
        if decision_input.nest:
            resources = decision_input.nest.resources
            features["cpu_cores"] = float(resources.get("cpu", 0))
            features["memory_gb"] = float(str(resources.get("memory", "0")).replace("Gi", "").replace("G", ""))
            features["bandwidth_mbps"] = float(str(resources.get("bandwidth", "0")).replace("Mbps", ""))
        
        return features
    
    async def close(self):
        """Fecha conexão HTTP"""
        await self.http_client.aclose()

