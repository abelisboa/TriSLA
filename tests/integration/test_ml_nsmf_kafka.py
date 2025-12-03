"""
Integration Tests - ML-NSMF Kafka Interfaces (I-02, I-03)
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
ML_NSMF_SRC = BASE_DIR / "apps" / "ml-nsmf" / "src"
sys.path.insert(0, str(ML_NSMF_SRC))

from kafka_consumer import MetricsConsumer
from kafka_producer import PredictionProducer


@pytest.fixture
def metrics_consumer():
    """Fixture para criar MetricsConsumer"""
    # Kafka desabilitado por padrão para testes
    os.environ["KAFKA_ENABLED"] = "false"
    return MetricsConsumer()


@pytest.fixture
def prediction_producer():
    """Fixture para criar PredictionProducer"""
    # Kafka desabilitado por padrão para testes
    os.environ["KAFKA_ENABLED"] = "false"
    return PredictionProducer()


@pytest.mark.asyncio
async def test_metrics_consumer_offline(metrics_consumer):
    """Testa MetricsConsumer em modo offline (sem Kafka)"""
    metrics = await metrics_consumer.consume_metrics()
    
    assert metrics is not None
    assert "latency" in metrics
    assert "throughput" in metrics
    assert "timestamp" in metrics
    assert metrics["source"] == "offline_simulation"


@pytest.mark.asyncio
async def test_prediction_producer_offline(prediction_producer):
    """Testa PredictionProducer em modo offline (sem Kafka)"""
    prediction = {
        "risk_score": 0.5,
        "risk_level": "medium",
        "confidence": 0.85,
        "timestamp": "2025-01-27T00:00:00Z"
    }
    
    explanation = {
        "method": "SHAP",
        "features_importance": {"latency": 0.4},
        "reasoning": "Test explanation"
    }
    
    # Não deve lançar exceção mesmo sem Kafka
    await prediction_producer.send_prediction(prediction, explanation)


@pytest.mark.asyncio
async def test_kafka_consumer_initialization():
    """Testa inicialização do MetricsConsumer com diferentes configurações"""
    # Teste 1: Kafka desabilitado
    os.environ["KAFKA_ENABLED"] = "false"
    consumer1 = MetricsConsumer()
    assert consumer1.consumer is None
    
    # Teste 2: Kafka habilitado mas não disponível (deve funcionar em modo offline)
    os.environ["KAFKA_ENABLED"] = "true"
    os.environ["KAFKA_BROKERS"] = "localhost:9092"
    os.environ["KAFKA_REQUIRED"] = "false"
    consumer2 = MetricsConsumer()
    # Deve inicializar mesmo sem Kafka disponível (modo offline)
    assert consumer2 is not None


@pytest.mark.asyncio
async def test_kafka_producer_initialization():
    """Testa inicialização do PredictionProducer com diferentes configurações"""
    # Teste 1: Kafka desabilitado
    os.environ["KAFKA_ENABLED"] = "false"
    producer1 = PredictionProducer()
    assert producer1.producer is None
    
    # Teste 2: Kafka habilitado mas não disponível (deve funcionar em modo offline)
    os.environ["KAFKA_ENABLED"] = "true"
    os.environ["KAFKA_BROKERS"] = "localhost:9092"
    os.environ["KAFKA_REQUIRED"] = "false"
    producer2 = PredictionProducer()
    # Deve inicializar mesmo sem Kafka disponível (modo offline)
    assert producer2 is not None

