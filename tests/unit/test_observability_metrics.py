"""
Unit Tests - Observability Metrics
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
OBS_SRC = BASE_DIR / "apps" / "shared" / "observability"
sys.path.insert(0, str(OBS_SRC))

try:
    from metrics import (
        i01_requests_total, i01_request_duration,
        intents_total, predictions_total, decisions_total,
        slo_compliance_rate
    )
except ImportError:
    # Se não conseguir importar, pular testes
    pytest.skip("Observability module not available", allow_module_level=True)


def test_metrics_initialized():
    """Testa se métricas foram inicializadas"""
    assert i01_requests_total is not None
    assert intents_total is not None
    assert predictions_total is not None
    assert decisions_total is not None


def test_metrics_increment():
    """Testa incremento de métricas"""
    # Incrementar contador
    i01_requests_total.add(1, {"interface": "I-01", "status": "success"})
    intents_total.add(1, {"module": "sem-csmf"})


def test_metrics_record():
    """Testa gravação de histogramas"""
    # Gravar duração
    i01_request_duration.record(0.1, {"interface": "I-01"})


def test_slo_compliance_gauge():
    """Testa gauge de SLO compliance"""
    # Definir valor
    slo_compliance_rate.set(0.95, {"interface": "I-01"})

