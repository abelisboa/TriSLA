"""
Unit Tests - SLO Calculator
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
OBS_SRC = BASE_DIR / "apps" / "shared" / "observability"
sys.path.insert(0, str(OBS_SRC))

try:
    from slo_calculator import SLOCalculator
except ImportError:
    pytest.skip("SLO Calculator module not available", allow_module_level=True)


def test_slo_calculator_initialization():
    """Testa inicialização do SLO Calculator"""
    calculator = SLOCalculator()
    assert calculator is not None
    assert calculator.SLO_TARGETS is not None


def test_slo_calculation_i01():
    """Testa cálculo de SLO para I-01"""
    calculator = SLOCalculator()
    
    # Métricas dentro do target
    result = calculator.calculate_slo_compliance(
        interface="I-01",
        latency_p99_ms=95.0,
        throughput_rps=105.0,
        error_rate=0.005,
        availability=0.995
    )
    
    assert result is not None
    assert result["interface"] == "I-01"
    assert result["status"] == "OK"
    assert result["compliance"] > 0.8
    assert len(result["violations"]) == 0


def test_slo_calculation_violation():
    """Testa cálculo de SLO com violação"""
    calculator = SLOCalculator()
    
    # Métricas violando target
    result = calculator.calculate_slo_compliance(
        interface="I-01",
        latency_p99_ms=150.0,  # Violando 100ms
        throughput_rps=50.0,  # Violando 100 req/s
        error_rate=0.02,  # Violando 1%
        availability=0.98
    )
    
    assert result is not None
    assert result["status"] == "VIOLATED"
    assert len(result["violations"]) > 0


def test_slo_calculation_all_interfaces():
    """Testa cálculo de SLO para todas as interfaces"""
    calculator = SLOCalculator()
    
    metrics_by_interface = {
        "I-01": {
            "latency_p99_ms": 95.0,
            "throughput_rps": 105.0,
            "error_rate": 0.005,
            "availability": 0.995
        },
        "I-02": {
            "latency_p99_ms": 180.0,
            "throughput_rps": 55.0,
            "error_rate": 0.008,
            "availability": 0.992
        }
    }
    
    result = calculator.calculate_all_slos(metrics_by_interface)
    
    assert result is not None
    assert "overall_compliance" in result
    assert "interfaces" in result
    assert len(result["interfaces"]) == 2


def test_slo_targets():
    """Testa obtenção de SLO targets"""
    calculator = SLOCalculator()
    targets = calculator.get_slo_targets()
    
    assert targets is not None
    assert "I-01" in targets
    assert "I-07" in targets

