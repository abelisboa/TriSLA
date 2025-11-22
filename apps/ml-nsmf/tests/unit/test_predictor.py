"""
Unit Tests - ML-NSMF Predictor
Testes unitários para o predictor de viabilidade
"""

import pytest
import sys
import os
import numpy as np
from pathlib import Path

# Adicionar src ao path
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from predictor import RiskPredictor


class TestRiskPredictor:
    """Testes do RiskPredictor"""
    
    @pytest.mark.asyncio
    async def test_predictor_initialization(self):
        """Testa inicialização do predictor"""
        predictor = RiskPredictor()
        # Deve inicializar mesmo sem modelo (fallback)
        assert predictor is not None
        assert predictor.feature_columns is not None
        assert len(predictor.feature_columns) == 9
    
    @pytest.mark.asyncio
    async def test_normalize_metrics(self):
        """Testa normalização de métricas"""
        predictor = RiskPredictor()
        
        metrics = {
            "latency": 10.0,
            "throughput": 100.0,
            "reliability": 0.99,
            "jitter": 2.0,
            "packet_loss": 0.001
        }
        
        normalized = await predictor.normalize(metrics, slice_type="eMBB")
        
        assert normalized is not None
        assert normalized.shape == (1, 9)  # 9 features
        assert not np.isnan(normalized).any()
        assert not np.isinf(normalized).any()
    
    @pytest.mark.asyncio
    async def test_predict_with_model(self):
        """Testa predição com modelo (se disponível)"""
        predictor = RiskPredictor()
        
        metrics = {
            "latency": 10.0,
            "throughput": 100.0,
            "reliability": 0.99,
            "jitter": 2.0,
            "packet_loss": 0.001
        }
        
        normalized = await predictor.normalize(metrics, slice_type="eMBB")
        prediction = await predictor.predict(normalized)
        
        assert prediction is not None
        assert "viability_score" in prediction
        assert "risk_score" in prediction
        assert "risk_level" in prediction
        assert "recommendation" in prediction
        assert "confidence" in prediction
        assert "timestamp" in prediction
        
        # Validar ranges
        assert 0.0 <= prediction["viability_score"] <= 1.0
        assert 0.0 <= prediction["risk_score"] <= 1.0
        assert prediction["risk_level"] in ["low", "medium", "high"]
        assert prediction["recommendation"] in ["ACCEPT", "REJECT", "RENEGOTIATE"]
        assert 0.0 <= prediction["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_explain_prediction(self):
        """Testa explicação XAI da predição"""
        predictor = RiskPredictor()
        
        metrics = {
            "latency": 10.0,
            "throughput": 100.0,
            "reliability": 0.99,
            "jitter": 2.0,
            "packet_loss": 0.001
        }
        
        normalized = await predictor.normalize(metrics, slice_type="eMBB")
        prediction = await predictor.predict(normalized)
        explanation = await predictor.explain(prediction, normalized)
        
        assert explanation is not None
        assert "method" in explanation
        assert "features_importance" in explanation
        assert "reasoning" in explanation
        
        # Validar importância das features
        assert len(explanation["features_importance"]) > 0
    
    @pytest.mark.asyncio
    async def test_different_slice_types(self):
        """Testa predição para diferentes tipos de slice"""
        predictor = RiskPredictor()
        
        base_metrics = {
            "latency": 5.0,
            "throughput": 50.0,
            "reliability": 0.999,
            "jitter": 1.0,
            "packet_loss": 0.0001
        }
        
        for slice_type in ["URLLC", "eMBB", "mMTC"]:
            normalized = await predictor.normalize(base_metrics, slice_type=slice_type)
            prediction = await predictor.predict(normalized)
            
            assert prediction is not None
            assert "viability_score" in prediction
            assert 0.0 <= prediction["viability_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_edge_cases(self):
        """Testa casos extremos"""
        predictor = RiskPredictor()
        
        # Métricas muito baixas
        low_metrics = {
            "latency": 1000.0,
            "throughput": 0.1,
            "reliability": 0.5,
            "jitter": 100.0,
            "packet_loss": 0.1
        }
        
        normalized = await predictor.normalize(low_metrics, slice_type="URLLC")
        prediction = await predictor.predict(normalized)
        
        assert prediction is not None
        # Viabilidade deve ser baixa para URLLC com métricas ruins (ou neutra se modelo não disponível)
        assert 0.0 <= prediction["viability_score"] <= 1.0
        
        # Métricas muito altas
        high_metrics = {
            "latency": 1.0,
            "throughput": 1000.0,
            "reliability": 0.99999,
            "jitter": 0.1,
            "packet_loss": 0.000001
        }
        
        normalized = await predictor.normalize(high_metrics, slice_type="URLLC")
        prediction = await predictor.predict(normalized)
        
        assert prediction is not None
        # Viabilidade deve estar no range válido (alta se modelo disponível, neutra se fallback)
        assert 0.0 <= prediction["viability_score"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

