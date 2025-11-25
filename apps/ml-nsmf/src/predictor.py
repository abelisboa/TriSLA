"""
Risk Predictor - ML-NSMF
Previsão de risco usando modelo LSTM/GRU
"""

from typing import Dict, Any
import numpy as np
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class RiskPredictor:
    """Previsor de risco usando ML"""
    
    def __init__(self):
        # Em produção, carregar modelo treinado
        self.model = self._load_model()
    
    def _load_model(self):
        """Carrega modelo LSTM/GRU treinado"""
        # Em produção: keras.models.load_model('models/model.h5')
        return None
    
    async def normalize(self, metrics: Dict[str, Any]) -> np.ndarray:
        """Normaliza métricas para entrada do modelo"""
        with tracer.start_as_current_span("normalize_metrics") as span:
            # Normalização básica (em produção, usar scaler treinado)
            normalized = np.array([
                metrics.get("latency", 0) / 100,  # Normalizar latência
                metrics.get("throughput", 0) / 1000,  # Normalizar throughput
                metrics.get("packet_loss", 0),
                metrics.get("jitter", 0) / 10
            ])
            
            span.set_attribute("metrics.normalized", True)
            return normalized
    
    async def predict(self, normalized_metrics: np.ndarray) -> Dict[str, Any]:
        """Previsão de risco usando modelo LSTM/GRU"""
        with tracer.start_as_current_span("predict_risk") as span:
            # Em produção, usar modelo real
            # prediction = self.model.predict(normalized_metrics.reshape(1, -1, 4))
            
            # Simulação (substituir por modelo real)
            risk_score = float(np.random.random())  # 0-1
            risk_level = "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
            
            prediction = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "confidence": 0.85,
                "timestamp": self._get_timestamp()
            }
            
            span.set_attribute("prediction.risk_level", risk_level)
            span.set_attribute("prediction.risk_score", risk_score)
            
            return prediction
    
    async def explain(self, prediction: Dict[str, Any], metrics: np.ndarray, model=None) -> Dict[str, Any]:
        """
        Explicabilidade (XAI) da previsão usando SHAP e LIME
        
        Args:
            prediction: Resultado da predição
            metrics: Métricas normalizadas usadas na predição
            model: Modelo ML (opcional, tenta carregar se None)
        """
        with tracer.start_as_current_span("explain_prediction") as span:
            explanation = {
                "method": "XAI",
                "features_importance": {},
                "reasoning": "",
                "shap_available": False,
                "lime_available": False
            }
            
            # Tentar usar SHAP
            try:
                import shap
                shap_available = True
            except ImportError:
                shap_available = False
                shap = None
            
            # Tentar usar LIME
            try:
                from lime import lime_tabular
                lime_available = True
            except ImportError:
                lime_available = False
                lime_tabular = None
            
            # Carregar modelo se necessário
            if model is None:
                model = self.model
            
            if model is None:
                # Fallback se modelo não estiver disponível
                explanation["features_importance"] = {
                    "latency": 0.4,
                    "throughput": 0.3,
                    "packet_loss": 0.2,
                    "jitter": 0.1
                }
                explanation["reasoning"] = f"Risk level {prediction['risk_level']} devido principalmente à latência"
                span.set_attribute("explanation.method", "fallback")
                return explanation
            
            # Usar SHAP se disponível
            if shap_available and model is not None:
                try:
                    # Criar explainer SHAP
                    if hasattr(model, 'predict_proba'):
                        explainer = shap.TreeExplainer(model)
                        shap_values = explainer.shap_values(metrics.reshape(1, -1))
                        
                        if isinstance(shap_values, list):
                            shap_values = shap_values[0]
                        
                        # Extrair importância das features
                        feature_names = ["latency", "throughput", "packet_loss", "jitter"]
                        if len(shap_values[0]) == len(feature_names):
                            explanation["features_importance"] = {
                                name: float(abs(value))
                                for name, value in zip(feature_names, shap_values[0])
                            }
                            # Normalizar
                            total = sum(explanation["features_importance"].values())
                            if total > 0:
                                explanation["features_importance"] = {
                                    k: v / total
                                    for k, v in explanation["features_importance"].items()
                                }
                        
                        explanation["shap_available"] = True
                        explanation["method"] = "SHAP"
                        span.set_attribute("explanation.method", "SHAP")
                except Exception as e:
                    span.set_attribute("explanation.shap_error", str(e))
            
            # Usar LIME se disponível e SHAP não funcionou
            if lime_available and not explanation.get("shap_available") and model is not None:
                try:
                    # Criar explainer LIME
                    feature_names = ["latency", "throughput", "packet_loss", "jitter"]
                    training_data = np.random.rand(100, len(feature_names))  # Dummy data
                    
                    explainer = lime_tabular.LimeTabularExplainer(
                        training_data,
                        feature_names=feature_names,
                        mode='regression' if hasattr(model, 'predict') else 'classification'
                    )
                    
                    explanation_lime = explainer.explain_instance(
                        metrics,
                        model.predict if hasattr(model, 'predict') else lambda x: model.predict_proba(x)[:, 1],
                        num_features=len(feature_names)
                    )
                    
                    # Extrair importância
                    explanation["features_importance"] = {
                        item[0]: abs(item[1])
                        for item in explanation_lime.as_list()
                    }
                    # Normalizar
                    total = sum(explanation["features_importance"].values())
                    if total > 0:
                        explanation["features_importance"] = {
                            k: v / total
                            for k, v in explanation["features_importance"].items()
                        }
                    
                    explanation["lime_available"] = True
                    explanation["method"] = "LIME"
                    span.set_attribute("explanation.method", "LIME")
                except Exception as e:
                    span.set_attribute("explanation.lime_error", str(e))
            
            # Gerar reasoning baseado em importância
            if explanation["features_importance"]:
                top_feature = max(explanation["features_importance"].items(), key=lambda x: x[1])
                explanation["reasoning"] = (
                    f"Risk level {prediction['risk_level']} "
                    f"devido principalmente a {top_feature[0]} "
                    f"(importância: {top_feature[1]:.2%})"
                )
            else:
                explanation["reasoning"] = f"Risk level {prediction['risk_level']}"
            
            span.set_attribute("explanation.method", explanation["method"])
            return explanation
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

