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
            raise FileNotFoundError(f"Modelo não encontrado em {model_path}")
        
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            logger.info(f"Modelo carregado com sucesso: {model_path}")
            return model
        except Exception as e:
            logger.exception(f"Erro ao carregar modelo de {model_path}: {e}")
            raise RuntimeError(f"Falha crítica no carregamento do modelo: {e}") from e
    
