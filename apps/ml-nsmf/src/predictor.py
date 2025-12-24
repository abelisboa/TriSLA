"""
Risk Predictor - ML-NSMF
Previsão de risco usando modelo Random Forest (ou LSTM/GRU)
"""

from typing import Dict, Any, Optional
import numpy as np
import pickle
import os
import json
import logging
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class RiskPredictor:
    """Previsor de risco usando ML"""
    
    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        """
        Inicializa o predictor com modelo treinado
        
        Args:
            model_path: Caminho para o modelo treinado (padrão: models/viability_model.pkl)
            scaler_path: Caminho para o scaler (padrão: models/scaler.pkl)
        """
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.model_metadata = None
        
        # Carregar modelo e scaler
        self.model = self._load_model(model_path)
        self.scaler = self._load_scaler(scaler_path)
        self._load_metadata()
    
    def _load_model(self, model_path: Optional[str] = None):
        """Carrega modelo treinado (Random Forest ou LSTM/GRU)"""
        if model_path is None:
            # Caminho padrão relativo ao diretório do módulo
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "viability_model.pkl")
        
        if not os.path.exists(model_path):
            logger.warning(f"Modelo não encontrado em {model_path}. Usando modo fallback.")
            return None
        
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            logger.info(f"Modelo carregado com sucesso: {model_path}")
            return model
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return None
    
    def _load_scaler(self, scaler_path: Optional[str] = None):
        """Carrega scaler usado no treinamento"""
        if scaler_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            scaler_path = os.path.join(base_dir, "models", "scaler.pkl")
        
        if not os.path.exists(scaler_path):
            logger.warning(f"Scaler não encontrado em {scaler_path}. Usando normalização básica.")
            return None
        
        try:
            with open(scaler_path, "rb") as f:
                scaler = pickle.load(f)
            logger.info(f"Scaler carregado com sucesso: {scaler_path}")
            return scaler
        except Exception as e:
            logger.error(f"Erro ao carregar scaler: {e}")
            return None
    
    def _load_metadata(self):
        """Carrega metadados do modelo"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        metadata_path = os.path.join(base_dir, "models", "model_metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    self.model_metadata = json.load(f)
                self.feature_columns = self.model_metadata.get("feature_columns", [])
                logger.info(f"Metadados carregados: {len(self.feature_columns)} features")
            except Exception as e:
                logger.warning(f"Erro ao carregar metadados: {e}")
    
    async def normalize(self, metrics: Dict[str, Any]) -> np.ndarray:
        """
        Normaliza métricas para entrada do modelo
        
        Args:
            metrics: Dicionário com métricas (latency, throughput, reliability, jitter, packet_loss, etc.)
        
        Returns:
            Array numpy normalizado com as features na ordem esperada pelo modelo
        """
        with tracer.start_as_current_span("normalize_metrics") as span:
            # Se temos feature_columns definidas, usar ordem correta
            if self.feature_columns:
                # Criar features derivadas se necessário
                epsilon = 0.001
                latency = metrics.get("latency", 0)
                throughput = metrics.get("throughput", 0)
                reliability = metrics.get("reliability", 0.99)
                jitter = metrics.get("jitter", 0)
                packet_loss = metrics.get("packet_loss", 0.001)
                
                # Features derivadas
                latency_throughput_ratio = latency / (throughput + epsilon)
                reliability_packet_loss_ratio = reliability / (packet_loss + epsilon)
                jitter_latency_ratio = jitter / (latency + epsilon) if latency > 0 else 0
                
                # Mapear slice_type para encoded
                slice_type = metrics.get("slice_type", "eMBB")
                slice_type_encoded = {"URLLC": 1, "eMBB": 2, "mMTC": 3}.get(slice_type, 2)
                
                # Construir array na ordem das features
                feature_dict = {
                    "latency": latency,
                    "throughput": throughput,
                    "reliability": reliability,
                    "jitter": jitter,
                    "packet_loss": packet_loss,
                    "cpu_utilization": metrics.get("cpu_utilization", 0.5),
                    "memory_utilization": metrics.get("memory_utilization", 0.5),
                    "network_bandwidth_available": metrics.get("network_bandwidth_available", 500),
                    "active_slices_count": metrics.get("active_slices_count", 1),
                    "slice_type_encoded": slice_type_encoded,
                    "latency_throughput_ratio": latency_throughput_ratio,
                    "reliability_packet_loss_ratio": reliability_packet_loss_ratio,
                    "jitter_latency_ratio": jitter_latency_ratio
                }
                
                # Extrair features na ordem correta
                feature_array = np.array([feature_dict.get(col, 0) for col in self.feature_columns])
            else:
                # Fallback: normalização básica
                feature_array = np.array([
                    metrics.get("latency", 0) / 100,
                    metrics.get("throughput", 0) / 1000,
                    metrics.get("packet_loss", 0),
                    metrics.get("jitter", 0) / 10
                ])
            
            # Aplicar scaler se disponível
            if self.scaler is not None:
                # Reshape para formato esperado pelo scaler (1, n_features)
                feature_array = feature_array.reshape(1, -1)
                normalized = self.scaler.transform(feature_array)[0]
            else:
                # Normalização básica manual
                normalized = feature_array
            
            span.set_attribute("metrics.normalized", True)
            span.set_attribute("metrics.features_count", len(normalized))
            return normalized
    
    async def predict(self, normalized_metrics: np.ndarray) -> Dict[str, Any]:
        """
        Previsão de risco usando modelo treinado
        
        Args:
            normalized_metrics: Array numpy com métricas normalizadas
        
        Returns:
            Dicionário com predição (risk_score, risk_level, confidence, viability_score)
        """
        with tracer.start_as_current_span("predict_risk") as span:
            if self.model is None:
                # Fallback: simulação se modelo não estiver disponível
                logger.warning("Modelo não disponível - usando predição simulada")
                risk_score = float(np.random.random())
                viability_score = 1.0 - risk_score
            else:
                try:
                    # Reshape para formato esperado pelo modelo (1, n_features)
                    X = normalized_metrics.reshape(1, -1)
                    
                    # Predição do modelo (viability_score: 0-1, onde 1 = totalmente viável)
                    viability_score = float(self.model.predict(X)[0])
                    
                    # Converter viability_score para risk_score (inverso)
                    # viability_score alto = risk_score baixo
                    risk_score = max(0.0, min(1.0, 1.0 - viability_score))
                    
                    # Calcular confiança baseada na distância do score para os extremos
                    # Scores próximos de 0.5 têm menor confiança
                    confidence = 1.0 - abs(viability_score - 0.5) * 2
                    confidence = max(0.5, min(1.0, confidence))
                    
                    span.set_attribute("prediction.viability_score", viability_score)
                    span.set_attribute("prediction.model_used", True)
                except Exception as e:
                    logger.error(f"Erro na predição: {e}")
                    # Fallback em caso de erro
                    risk_score = 0.5
                    viability_score = 0.5
                    confidence = 0.5
                    span.record_exception(e)
            
            # Determinar nível de risco
            if risk_score > 0.7:
                risk_level = "high"
            elif risk_score > 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            prediction = {
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "viability_score": float(viability_score) if self.model is not None else None,
                "confidence": float(confidence) if self.model is not None else 0.85,
                "timestamp": self._get_timestamp(),
                "model_used": self.model is not None
            }
            
            span.set_attribute("prediction.risk_level", risk_level)
            span.set_attribute("prediction.risk_score", risk_score)
            span.set_attribute("prediction.confidence", prediction["confidence"])
            
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
                    # Usar feature names do metadata se disponível
                    feature_names = self.feature_columns if self.feature_columns else [
                        "latency", "throughput", "reliability", "jitter", "packet_loss"
                    ]
                    
                    # Criar explainer SHAP baseado no tipo de modelo
                    if hasattr(model, 'feature_importances_'):
                        # Random Forest ou modelos tree-based
                        explainer = shap.TreeExplainer(model)
                    else:
                        # Outros modelos (LSTM, etc.) - usar KernelExplainer
                        # Criar dados de background (amostra pequena para performance)
                        background_data = np.random.rand(50, len(feature_names))
                        explainer = shap.KernelExplainer(model.predict, background_data)
                    
                    # Calcular SHAP values
                    X = metrics.reshape(1, -1)
                    shap_values = explainer.shap_values(X)
                    
                    # Tratar diferentes formatos de saída do SHAP
                    if isinstance(shap_values, list):
                        shap_values = shap_values[0] if len(shap_values) > 0 else shap_values
                    
                    # Extrair importância das features
                    if len(shap_values.shape) > 1:
                        shap_values = shap_values[0]  # Pegar primeira amostra
                    
                    if len(shap_values) == len(feature_names):
                        explanation["features_importance"] = {
                            name: float(abs(value))
                            for name, value in zip(feature_names, shap_values)
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
                        logger.debug("Explicação SHAP gerada com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao gerar explicação SHAP: {e}")
                    span.set_attribute("explanation.shap_error", str(e))
            
            # Usar LIME se disponível e SHAP não funcionou
            if lime_available and not explanation.get("shap_available") and model is not None:
                try:
                    # Usar feature names do metadata se disponível
                    feature_names = self.feature_columns if self.feature_columns else [
                        "latency", "throughput", "reliability", "jitter", "packet_loss"
                    ]
                    
                    # Criar dados de treinamento para LIME (usar distribuição similar aos dados reais)
                    # Em produção, usar dados históricos reais
                    n_samples = 100
                    training_data = np.random.rand(n_samples, len(feature_names))
                    
                    # Determinar modo (regression para viability_score)
                    mode = 'regression'
                    
                    explainer = lime_tabular.LimeTabularExplainer(
                        training_data,
                        feature_names=feature_names,
                        mode=mode,
                        discretize_continuous=True
                    )
                    
                    # Função de predição para LIME
                    def predict_fn(X):
                        return model.predict(X)
                    
                    # Gerar explicação
                    explanation_lime = explainer.explain_instance(
                        metrics,
                        predict_fn,
                        num_features=min(len(feature_names), 10)  # Limitar número de features
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
                    logger.debug("Explicação LIME gerada com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao gerar explicação LIME: {e}")
                    span.set_attribute("explanation.lime_error", str(e))
            
            # Gerar reasoning baseado em importância
            if explanation["features_importance"]:
                # Ordenar features por importância
                sorted_features = sorted(
                    explanation["features_importance"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                top_feature = sorted_features[0]
                top_3_features = sorted_features[:3]
                
                # Construir reasoning detalhado
                reasoning_parts = [
                    f"Risk level {prediction['risk_level']} (score: {prediction['risk_score']:.2f})"
                ]
                
                if prediction.get("viability_score") is not None:
                    reasoning_parts.append(f"viability: {prediction['viability_score']:.2f}")
                
                reasoning_parts.append(f"Principal fator: {top_feature[0]} ({top_feature[1]:.1%})")
                
                if len(top_3_features) > 1:
                    other_factors = ", ".join([f"{f[0]} ({f[1]:.1%})" for f in top_3_features[1:]])
                    reasoning_parts.append(f"Outros fatores: {other_factors}")
                
                explanation["reasoning"] = ". ".join(reasoning_parts) + "."
            else:
                # Fallback: usar feature importance do metadata se disponível
                if self.model_metadata and "feature_importance" in self.model_metadata.get("training_history", {}):
                    feature_importance = self.model_metadata["training_history"]["feature_importance"]
                    if feature_importance:
                        top_feature = max(feature_importance.items(), key=lambda x: x[1])
                        explanation["reasoning"] = (
                            f"Risk level {prediction['risk_level']} "
                            f"baseado em importância histórica de {top_feature[0]} "
                            f"({top_feature[1]:.1%})"
                        )
                    else:
                        explanation["reasoning"] = f"Risk level {prediction['risk_level']}"
                else:
                    explanation["reasoning"] = f"Risk level {prediction['risk_level']}"
            
            span.set_attribute("explanation.method", explanation["method"])
            return explanation
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

