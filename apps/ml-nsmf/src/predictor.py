"""
Risk Predictor - ML-NSMF
Previsão de viabilidade usando modelo ML real (Random Forest/Gradient Boosting)
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import os
import sys
import joblib
from opentelemetry import trace

# Adicionar path para modelos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Caminho absoluto para models/ (relativo a src/)
_model_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dir = os.path.join(_model_base, "models")

tracer = trace.get_tracer(__name__)


class RiskPredictor:
    """Previsor de viabilidade usando ML real"""
    
    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Inicializa predictor com modelo real
        
        Args:
            model_path: Caminho para modelo treinado (padrão: models/viability_model.pkl)
            scaler_path: Caminho para scaler treinado (padrão: models/scaler.pkl)
        """
        self.model_path = model_path or os.path.join(model_dir, "viability_model.pkl")
        self.scaler_path = scaler_path or os.path.join(model_dir, "scaler.pkl")
        self.model = self._load_model()
        self.scaler = self._load_scaler()
        self.feature_columns = [
            "latency", "throughput", "reliability", "jitter", "packet_loss",
            "latency_throughput_ratio", "reliability_packet_loss_ratio",
            "jitter_latency_ratio", "slice_type_encoded"
        ]
    
    def _load_model(self):
        """Carrega modelo ML treinado"""
        try:
            if os.path.exists(self.model_path):
                model = joblib.load(self.model_path)
                print(f"✅ Modelo carregado: {self.model_path}")
                return model
            else:
                print(f"⚠️ Modelo não encontrado em {self.model_path}")
                print("   Execute training/train_model.py para treinar o modelo")
                return None
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return None
    
    def _load_scaler(self):
        """Carrega scaler treinado"""
        try:
            if os.path.exists(self.scaler_path):
                scaler = joblib.load(self.scaler_path)
                print(f"✅ Scaler carregado: {self.scaler_path}")
                return scaler
            else:
                print(f"⚠️ Scaler não encontrado em {self.scaler_path}")
                print("   Usando StandardScaler padrão (não treinado)")
                from sklearn.preprocessing import StandardScaler
                return StandardScaler()
        except Exception as e:
            print(f"❌ Erro ao carregar scaler: {e}")
            from sklearn.preprocessing import StandardScaler
            return StandardScaler()
    
    async def normalize(self, metrics: Dict[str, Any], slice_type: str = "eMBB") -> np.ndarray:
        """
        Normaliza métricas para entrada do modelo usando scaler real
        
        Args:
            metrics: Dicionário com métricas
            slice_type: Tipo de slice (URLLC, eMBB, mMTC)
        
        Returns:
            Array normalizado pronto para predição
        """
        with tracer.start_as_current_span("normalize_metrics") as span:
            # Extrair métricas básicas
            latency = float(metrics.get("latency", 0))
            throughput = float(metrics.get("throughput", 0))
            reliability = float(metrics.get("reliability", 0.99))
            jitter = float(metrics.get("jitter", 0))
            packet_loss = float(metrics.get("packet_loss", 0))
            
            # Calcular features derivadas
            latency_throughput_ratio = latency / (throughput + 1e-6)
            reliability_packet_loss_ratio = reliability / (packet_loss + 1e-9)
            jitter_latency_ratio = jitter / (latency + 1e-6)
            
            # Codificar slice_type
            slice_type_map = {"URLLC": 0, "eMBB": 1, "mMTC": 2}
            slice_type_encoded = slice_type_map.get(slice_type, 1)
            
            # Criar array de features na ordem correta
            features = np.array([[
                latency,
                throughput,
                reliability,
                jitter,
                packet_loss,
                latency_throughput_ratio,
                reliability_packet_loss_ratio,
                jitter_latency_ratio,
                slice_type_encoded
            ]])
            
            # Normalizar usando scaler real
            if self.scaler is not None:
                try:
                    normalized = self.scaler.transform(features)
                except Exception as e:
                    print(f"⚠️ Erro ao normalizar com scaler: {e}, usando normalização básica")
                    # Fallback para normalização básica
                    normalized = np.array([[
                        latency / 100,
                        throughput / 1000,
                        reliability,
                        jitter / 10,
                        packet_loss,
                        latency_throughput_ratio,
                        reliability_packet_loss_ratio,
                        jitter_latency_ratio,
                        slice_type_encoded
                    ]])
            else:
                # Fallback se scaler não disponível
                normalized = features
            
            span.set_attribute("metrics.normalized", True)
            span.set_attribute("metrics.slice_type", slice_type)
            return normalized
    
    async def predict(self, normalized_metrics: np.ndarray) -> Dict[str, Any]:
        """
        Previsão de viabilidade usando modelo ML real
        
        Args:
            normalized_metrics: Array normalizado de features
        
        Returns:
            Dicionário com predição de viabilidade
        """
        with tracer.start_as_current_span("predict_viability") as span:
            if self.model is None:
                # Fallback se modelo não disponível
                print("⚠️ Modelo não disponível, usando predição de fallback")
                viability_score = 0.5  # Score neutro
                confidence = 0.0
            else:
                try:
                    # Predição real usando modelo treinado
                    viability_score = float(self.model.predict(normalized_metrics)[0])
                    viability_score = np.clip(viability_score, 0.0, 1.0)
                    
                    # Calcular confiança baseada na proximidade dos limites
                    # (Quanto mais próximo de 0 ou 1, maior a confiança)
                    confidence = 1.0 - 2.0 * abs(viability_score - 0.5)
                    confidence = max(0.0, min(1.0, confidence))
                except Exception as e:
                    print(f"❌ Erro ao fazer predição: {e}")
                    viability_score = 0.5
                    confidence = 0.0
            
            # Converter viabilidade em nível de risco (inverso)
            # Alta viabilidade = baixo risco
            risk_score = 1.0 - viability_score
            risk_level = "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
            
            # Determinar recomendação
            if viability_score >= 0.7:
                recommendation = "ACCEPT"
            elif viability_score >= 0.4:
                recommendation = "RENEGOTIATE"
            else:
                recommendation = "REJECT"
            
            prediction = {
                "viability_score": float(viability_score),
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "recommendation": recommendation,
                "confidence": float(confidence),
                "timestamp": self._get_timestamp()
            }
            
            span.set_attribute("prediction.viability_score", viability_score)
            span.set_attribute("prediction.risk_level", risk_level)
            span.set_attribute("prediction.recommendation", recommendation)
            span.set_attribute("prediction.confidence", confidence)
            
            return prediction
    
    async def explain(self, prediction: Dict[str, Any], normalized_metrics: np.ndarray) -> Dict[str, Any]:
        """
        Explicabilidade (XAI) da previsão usando SHAP
        
        Args:
            prediction: Resultado da predição
            normalized_metrics: Features normalizadas usadas na predição
        
        Returns:
            Dicionário com explicação XAI
        """
        with tracer.start_as_current_span("explain_prediction") as span:
            if self.model is None:
                # Fallback se modelo não disponível
                explanation = {
                    "method": "fallback",
                    "features_importance": {
                        "latency": 0.4,
                        "throughput": 0.3,
                        "reliability": 0.2,
                        "jitter": 0.05,
                        "packet_loss": 0.05
                    },
                    "reasoning": f"Viabilidade {prediction.get('viability_score', 0.5):.2f} - modelo não disponível"
                }
                span.set_attribute("explanation.method", "fallback")
                return explanation
            
            try:
                # Tentar usar SHAP se disponível
                try:
                    import shap
                    
                    # Criar explainer (TreeExplainer para Random Forest/Gradient Boosting)
                    explainer = shap.TreeExplainer(self.model)
                    shap_values = explainer.shap_values(normalized_metrics)
                    
                    # Extrair valores de importância
                    if isinstance(shap_values, list):
                        shap_values = shap_values[0]  # Para regressão
                    
                    # Calcular importância média absoluta
                    feature_importance = {
                        col: float(abs(shap_values[0][i]))
                        for i, col in enumerate(self.feature_columns)
                    }
                    
                    # Normalizar importâncias
                    total_importance = sum(feature_importance.values())
                    if total_importance > 0:
                        feature_importance = {
                            k: v / total_importance
                            for k, v in feature_importance.items()
                        }
                    
                    # Identificar features mais importantes
                    top_features = sorted(
                        feature_importance.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                    
                    explanation = {
                        "method": "SHAP",
                        "features_importance": feature_importance,
                        "top_features": [
                            {"feature": feat, "importance": float(imp)}
                            for feat, imp in top_features
                        ],
                        "shap_values": shap_values[0].tolist() if len(shap_values.shape) > 1 else shap_values.tolist(),
                        "reasoning": self._generate_reasoning(prediction, top_features)
                    }
                    
                    span.set_attribute("explanation.method", "SHAP")
                    span.set_attribute("explanation.top_feature", top_features[0][0] if top_features else "unknown")
                    
                except ImportError:
                    # SHAP não disponível, usar feature importance do modelo
                    if hasattr(self.model, 'feature_importances_'):
                        feature_importance = {
                            col: float(imp)
                            for col, imp in zip(self.feature_columns, self.model.feature_importances_)
                        }
                        
                        top_features = sorted(
                            feature_importance.items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:5]
                        
                        explanation = {
                            "method": "feature_importance",
                            "features_importance": feature_importance,
                            "top_features": [
                                {"feature": feat, "importance": float(imp)}
                                for feat, imp in top_features
                            ],
                            "reasoning": self._generate_reasoning(prediction, top_features)
                        }
                        
                        span.set_attribute("explanation.method", "feature_importance")
                    else:
                        raise
                        
            except Exception as e:
                print(f"⚠️ Erro ao gerar explicação XAI: {e}")
                # Fallback
                explanation = {
                    "method": "fallback",
                    "features_importance": {
                        "latency": 0.4,
                        "throughput": 0.3,
                        "reliability": 0.2,
                        "jitter": 0.05,
                        "packet_loss": 0.05
                    },
                    "reasoning": f"Viabilidade {prediction.get('viability_score', 0.5):.2f} - erro na explicação"
                }
                span.set_attribute("explanation.method", "fallback")
            
            return explanation
    
    def _generate_reasoning(self, prediction: Dict[str, Any], top_features: list) -> str:
        """Gera explicação textual baseada na predição e features importantes"""
        viability = prediction.get("viability_score", 0.5)
        recommendation = prediction.get("recommendation", "UNKNOWN")
        
        if top_features:
            main_feature = top_features[0][0]
            reasoning = (
                f"Viabilidade {viability:.2%} ({recommendation}). "
                f"Feature mais importante: {main_feature}. "
            )
            
            if viability >= 0.7:
                reasoning += "SLA viável com alta confiança."
            elif viability >= 0.4:
                reasoning += "SLA requer negociação de requisitos."
            else:
                reasoning += "SLA não viável com recursos atuais."
        else:
            reasoning = f"Viabilidade {viability:.2%} ({recommendation})."
        
        return reasoning
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

