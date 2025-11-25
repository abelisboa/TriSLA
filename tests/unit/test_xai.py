"""
Testes unitários para XAI (Explainable AI)
"""

import pytest
import numpy as np
import sys
import os

# Adicionar caminho do módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/ml-nsmf/src"))

from predictor import RiskPredictor


@pytest.fixture
def risk_predictor():
    """Fixture para criar predictor"""
    return RiskPredictor()


@pytest.fixture
def sample_metrics():
    """Fixture para métricas de teste"""
    return {
        "latency": 15.0,
        "throughput": 500.0,
        "packet_loss": 0.001,
        "jitter": 2.0
    }


@pytest.fixture
def sample_prediction():
    """Fixture para predição de teste"""
    return {
        "risk_score": 0.75,
        "risk_level": "high",
        "confidence": 0.85,
        "timestamp": "2025-01-27T10:00:00Z"
    }


@pytest.mark.asyncio
async def test_explain_prediction_fallback(risk_predictor, sample_prediction, sample_metrics):
    """Testa explicação com fallback (sem modelo)"""
    metrics_array = np.array([15.0, 500.0, 0.001, 2.0])
    explanation = await risk_predictor.explain(sample_prediction, metrics_array)
    
    assert explanation is not None
    assert "method" in explanation
    assert "features_importance" in explanation
    assert "reasoning" in explanation
    assert len(explanation["features_importance"]) > 0


@pytest.mark.asyncio
async def test_explain_prediction_structure(risk_predictor, sample_prediction, sample_metrics):
    """Testa estrutura da explicação"""
    metrics_array = np.array([15.0, 500.0, 0.001, 2.0])
    explanation = await risk_predictor.explain(sample_prediction, metrics_array)
    
    # Verificar estrutura
    assert "method" in explanation
    assert "features_importance" in explanation
    assert "reasoning" in explanation
    assert "shap_available" in explanation
    assert "lime_available" in explanation
    
    # Verificar que features_importance tem valores válidos
    for feature, importance in explanation["features_importance"].items():
        assert isinstance(importance, (int, float))
        assert 0 <= importance <= 1  # Normalizado


@pytest.mark.asyncio
async def test_explain_prediction_reasoning(risk_predictor, sample_prediction, sample_metrics):
    """Testa que reasoning é gerado"""
    metrics_array = np.array([15.0, 500.0, 0.001, 2.0])
    explanation = await risk_predictor.explain(sample_prediction, metrics_array)
    
    assert explanation["reasoning"] is not None
    assert len(explanation["reasoning"]) > 0
    assert "Risk level" in explanation["reasoning"] or "risk" in explanation["reasoning"].lower()

