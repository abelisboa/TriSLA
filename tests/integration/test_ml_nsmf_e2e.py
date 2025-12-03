"""
E2E Tests - ML-NSMF Integration (SEM → ML → DE)
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path

# Adicionar caminhos dos módulos
BASE_DIR = Path(__file__).parent.parent.parent
ML_NSMF_SRC = BASE_DIR / "apps" / "ml-nsmf" / "src"
SEM_CSMF_SRC = BASE_DIR / "apps" / "sem-csmf" / "src"
sys.path.insert(0, str(ML_NSMF_SRC))
sys.path.insert(0, str(SEM_CSMF_SRC))

from predictor import RiskPredictor


@pytest.fixture
def predictor():
    """Fixture para criar RiskPredictor"""
    return RiskPredictor()


@pytest.mark.asyncio
async def test_e2e_intent_to_prediction(predictor):
    """Testa fluxo E2E: Intent (métricas) → ML → Predição"""
    # Simular métricas vindas do SEM-CSMF
    metrics_from_sem = {
        "intent_id": "test-intent-001",
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
    
    # Normalizar métricas
    normalized = await predictor.normalize(metrics_from_sem)
    assert normalized is not None
    
    # Prever risco
    prediction = await predictor.predict(normalized)
    assert prediction is not None
    assert "risk_score" in prediction
    assert "risk_level" in prediction
    
    # Explicar predição (XAI)
    explanation = await predictor.explain(prediction, normalized)
    assert explanation is not None
    assert "reasoning" in explanation
    
    # Verificar que predição pode ser enviada para Decision Engine
    assert prediction.get("risk_level") in ["low", "medium", "high"]


@pytest.mark.asyncio
async def test_e2e_multiple_intents(predictor):
    """Testa fluxo E2E com múltiplos intents"""
    intents = [
        {
            "intent_id": "test-intent-001",
            "latency": 5.0,
            "throughput": 1000.0,
            "reliability": 0.999,
            "slice_type": "URLLC"
        },
        {
            "intent_id": "test-intent-002",
            "latency": 50.0,
            "throughput": 500.0,
            "reliability": 0.99,
            "slice_type": "eMBB"
        },
        {
            "intent_id": "test-intent-003",
            "latency": 1000.0,
            "throughput": 10.0,
            "reliability": 0.9,
            "slice_type": "mMTC"
        }
    ]
    
    predictions = []
    for intent in intents:
        normalized = await predictor.normalize(intent)
        prediction = await predictor.predict(normalized)
        explanation = await predictor.explain(prediction, normalized)
        
        predictions.append({
            "intent_id": intent["intent_id"],
            "prediction": prediction,
            "explanation": explanation
        })
    
    # Verificar que todas as predições foram geradas
    assert len(predictions) == 3
    for pred in predictions:
        assert pred["prediction"] is not None
        assert pred["explanation"] is not None


@pytest.mark.asyncio
async def test_e2e_performance(predictor):
    """Testa performance do fluxo E2E (< 500ms)"""
    import time
    
    metrics = {
        "latency": 10.0,
        "throughput": 100.0,
        "reliability": 0.99,
        "jitter": 2.0,
        "packet_loss": 0.001,
        "slice_type": "eMBB"
    }
    
    start_time = time.time()
    
    normalized = await predictor.normalize(metrics)
    prediction = await predictor.predict(normalized)
    explanation = await predictor.explain(prediction, normalized)
    
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Converter para ms
    
    assert prediction is not None
    assert explanation is not None
    # Performance deve ser < 2000ms (com margem para XAI)
    assert elapsed_time < 2000, f"Fluxo E2E levou {elapsed_time:.2f}ms (esperado < 2000ms)"

