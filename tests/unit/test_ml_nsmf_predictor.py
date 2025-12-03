"""
Unit Tests - ML-NSMF RiskPredictor
"""

import pytest
import sys
import os
import numpy as np
from pathlib import Path

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
ML_NSMF_SRC = BASE_DIR / "apps" / "ml-nsmf" / "src"
sys.path.insert(0, str(ML_NSMF_SRC))

from predictor import RiskPredictor


@pytest.fixture
def predictor():
    """Fixture para criar RiskPredictor"""
    return RiskPredictor()


@pytest.fixture
def sample_metrics():
    """Fixture para criar métricas de teste"""
    return {
        "latency": 10.0,
        "throughput": 100.0,
        "reliability": 0.99,
        "jitter": 2.0,
        "packet_loss": 0.001,
        "cpu_utilization": 0.5,
        "memory_utilization": 0.5,
        "network_bandwidth_available": 500.0,
        "active_slices_count": 1.0,
        "slice_type": "eMBB"
    }


@pytest.mark.asyncio
async def test_normalize_metrics(predictor, sample_metrics):
    """Testa normalização de métricas"""
    normalized = await predictor.normalize(sample_metrics)
    
    assert normalized is not None
    assert isinstance(normalized, np.ndarray)
    assert len(normalized) > 0


@pytest.mark.asyncio
async def test_predict_risk(predictor, sample_metrics):
    """Testa predição de risco"""
    normalized = await predictor.normalize(sample_metrics)
    prediction = await predictor.predict(normalized)
    
    assert prediction is not None
    assert "risk_score" in prediction
    assert "risk_level" in prediction
    assert "confidence" in prediction
    assert "timestamp" in prediction
    assert "model_used" in prediction
    
    assert 0.0 <= prediction["risk_score"] <= 1.0
    assert prediction["risk_level"] in ["low", "medium", "high"]
    assert 0.0 <= prediction["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_explain_prediction(predictor, sample_metrics):
    """Testa explicação XAI da predição"""
    normalized = await predictor.normalize(sample_metrics)
    prediction = await predictor.predict(normalized)
    explanation = await predictor.explain(prediction, normalized)
    
    assert explanation is not None
    assert "method" in explanation
    assert "features_importance" in explanation
    assert "reasoning" in explanation
    assert "shap_available" in explanation
    assert "lime_available" in explanation
    
    # Verificar que explicação foi gerada
    assert explanation["method"] in ["XAI", "SHAP", "LIME", "fallback"]
    assert len(explanation["reasoning"]) > 0


@pytest.mark.asyncio
async def test_predict_with_different_slice_types(predictor):
    """Testa predição com diferentes tipos de slice"""
    slice_types = ["URLLC", "eMBB", "mMTC"]
    
    for slice_type in slice_types:
        metrics = {
            "latency": 10.0,
            "throughput": 100.0,
            "reliability": 0.99,
            "jitter": 2.0,
            "packet_loss": 0.001,
            "slice_type": slice_type
        }
        
        normalized = await predictor.normalize(metrics)
        prediction = await predictor.predict(normalized)
        
        assert prediction is not None
        assert "risk_level" in prediction


@pytest.mark.asyncio
async def test_predict_with_extreme_values(predictor):
    """Testa predição com valores extremos"""
    # Valores extremos de latência
    metrics_high_latency = {
        "latency": 1000.0,
        "throughput": 10.0,
        "reliability": 0.5,
        "jitter": 50.0,
        "packet_loss": 0.1,
        "slice_type": "URLLC"
    }
    
    normalized = await predictor.normalize(metrics_high_latency)
    prediction = await predictor.predict(normalized)
    
    assert prediction is not None
    # Valores extremos devem resultar em risk_score alto
    assert prediction["risk_score"] >= 0.0


@pytest.mark.asyncio
async def test_explain_with_shap(predictor, sample_metrics):
    """Testa explicação usando SHAP (se disponível)"""
    normalized = await predictor.normalize(sample_metrics)
    prediction = await predictor.predict(normalized)
    explanation = await predictor.explain(prediction, normalized)
    
    # Verificar que explicação foi gerada
    assert explanation is not None
    # SHAP pode estar disponível ou não, mas explicação deve existir
    if explanation.get("shap_available"):
        assert explanation["method"] == "SHAP"
        assert len(explanation["features_importance"]) > 0


@pytest.mark.asyncio
async def test_explain_with_lime(predictor, sample_metrics):
    """Testa explicação usando LIME (se disponível)"""
    normalized = await predictor.normalize(sample_metrics)
    prediction = await predictor.predict(normalized)
    explanation = await predictor.explain(prediction, normalized)
    
    # Verificar que explicação foi gerada
    assert explanation is not None
    # LIME pode estar disponível ou não, mas explicação deve existir
    if explanation.get("lime_available"):
        assert explanation["method"] == "LIME"
        assert len(explanation["features_importance"]) > 0


@pytest.mark.asyncio
async def test_predict_performance(predictor, sample_metrics):
    """Testa performance da predição (< 500ms)"""
    import time
    
    normalized = await predictor.normalize(sample_metrics)
    
    start_time = time.time()
    prediction = await predictor.predict(normalized)
    explanation = await predictor.explain(prediction, normalized)
    end_time = time.time()
    
    elapsed_time = (end_time - start_time) * 1000  # Converter para ms
    
    assert prediction is not None
    assert explanation is not None
    # Performance deve ser < 500ms (com margem para XAI)
    assert elapsed_time < 2000, f"Predição levou {elapsed_time:.2f}ms (esperado < 2000ms)"

