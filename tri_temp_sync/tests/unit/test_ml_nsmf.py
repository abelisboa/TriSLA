"""
Unit Tests - ML-NSMF
"""

import pytest
import sys
from pathlib import Path

# Adiciona os diretórios src ao path (diretórios com hífen não podem ser importados diretamente)
BASE_DIR = Path(__file__).parent.parent.parent
ML_NSMF_SRC = BASE_DIR / "apps" / "ml-nsmf" / "src"
sys.path.insert(0, str(ML_NSMF_SRC))

from predictor import RiskPredictor


class TestRiskPredictor:
    """Testes do RiskPredictor"""
    
    @pytest.mark.asyncio
    async def test_normalize(self):
        """Testa normalização de métricas"""
        predictor = RiskPredictor()
        metrics = {
            "latency": 50,
            "throughput": 500,
            "packet_loss": 0.01,
            "jitter": 5
        }
        
        normalized = await predictor.normalize(metrics)
        assert normalized is not None
        assert len(normalized) == 4
    
    @pytest.mark.asyncio
    async def test_predict(self):
        """Testa previsão de risco"""
        predictor = RiskPredictor()
        normalized = [0.5, 0.5, 0.01, 0.5]
        
        prediction = await predictor.predict(normalized)
        assert prediction["risk_level"] in ["low", "medium", "high"]
        assert 0 <= prediction["risk_score"] <= 1

