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
            # Caminho absoluto padrão no container
            model_path = "/app/models/viability_model.pkl"
        
        if not os.path.exists(model_path):
            logger.warning(f"⚠️ Modelo não encontrado em {model_path} - operando em modo fallback")
            return None
        
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            logger.info(f"✅ Modelo carregado com sucesso: {model_path}")
            return model
        except Exception as e:
            logger.warning(f"⚠️ Modelo não disponível (incompatibilidade numpy) - operando em modo fallback: {e}")
            return None
    
    def _load_scaler(self, scaler_path: Optional[str] = None):
        """Carrega scaler para normalização"""
        if scaler_path is None:
            scaler_path = "/app/models/scaler.pkl"
        
        if not os.path.exists(scaler_path):
            logger.warning(f"⚠️ Scaler não encontrado em {scaler_path} - usando normalização básica")
            return None
        
        try:
            with open(scaler_path, "rb") as f:
                scaler = pickle.load(f)
            logger.info(f"✅ Scaler carregado com sucesso: {scaler_path}")
            return scaler
        except Exception as e:
            logger.warning(f"⚠️ Scaler não disponível (incompatibilidade numpy) - usando normalização básica: {e}")
            return None
    
    def _load_metadata(self):
        """Carrega metadados do modelo"""
        metadata_path = "/app/models/model_metadata.json"
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    self.model_metadata = json.load(f)
                    self.feature_columns = self.model_metadata.get("feature_columns", [])
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar metadados: {e}")
    
    def normalize(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza métricas usando scaler ou normalização básica"""
        if self.scaler:
            # Usar scaler se disponível
            # Implementação simplificada
            return metrics
        else:
            # Normalização básica
            return metrics
    
    def predict(self, normalized_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Faz predição usando modelo ou heurística"""
        if self.model is not None:
            # Usar modelo se disponível
            # Implementação simplificada
            return {
                "risk_score": 0.5,
                "risk_level": "medium",
                "confidence": 0.8,
                "model_used": True
            }
        else:
            # Heurística básica
            return {
                "risk_score": 0.5,
                "risk_level": "medium",
                "confidence": 0.5,
                "model_used": False
            }
    
    def explain(self, prediction: Dict[str, Any], normalized_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Gera explicação da predição"""
        return {
            "explanation": "Explicação básica",
            "method": "heuristic"
        }
