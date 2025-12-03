"""
Integration Tests - BC-NSSMF Integration (Decision Engine → BC-NSSMF)
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Adicionar caminhos dos módulos
BASE_DIR = Path(__file__).parent.parent.parent
BC_SRC = BASE_DIR / "apps" / "bc-nssmf" / "src"
DE_SRC = BASE_DIR / "apps" / "decision-engine" / "src"

# Remover outros caminhos que possam conflitar e adicionar na ordem correta
sys.path = [str(BC_SRC), str(DE_SRC)] + [p for p in sys.path if "decision-engine" not in p or p == str(DE_SRC)]

# Mock BC_ENABLED antes de importar
os.environ["BC_ENABLED"] = "false"

# Mudar para o diretório do módulo para resolver imports relativos
original_cwd = os.getcwd()
os.chdir(str(BC_SRC))

try:
    from service import BCService
finally:
    os.chdir(original_cwd)

# Importar models do decision-engine (precisa estar no sys.path correto)
# Remover bc-nssmf do path temporariamente
sys.path = [str(DE_SRC)] + [p for p in sys.path if "bc-nssmf" not in p]
os.chdir(str(DE_SRC))
try:
    from models import DecisionResult, DecisionAction, SLARequirement
finally:
    os.chdir(original_cwd)
    # Restaurar path
    sys.path = [str(BC_SRC), str(DE_SRC)] + [p for p in sys.path if "bc-nssmf" not in p and "decision-engine" not in p]


@pytest.fixture
def bc_service():
    """Fixture para criar BCService em modo DEV"""
    with patch.dict(os.environ, {"BC_ENABLED": "false"}):
        return BCService()


@pytest.fixture
def sample_decision_result():
    """Fixture para criar DecisionResult de teste"""
    return DecisionResult(
        decision_id="dec-test-001",
        intent_id="test-intent-001",
        nest_id="test-nest-001",
        action=DecisionAction.ACCEPT,
        reasoning="SLA aceito",
        confidence=0.9,
        ml_risk_score=0.2,
        ml_risk_level=None,
        slos=[
            SLARequirement(name="latency", value=10.0, threshold=10.0, unit="ms"),
            SLARequirement(name="reliability", value=0.99, threshold=0.99, unit="ratio")
        ],
        domains=["RAN", "Transporte"]
    )


@pytest.mark.asyncio
async def test_integration_bc_service_register_sla_on_chain(bc_service, sample_decision_result):
    """Testa integração: BCService.register_sla_on_chain com DecisionResult"""
    # Em modo degraded, deve retornar None
    result = bc_service.register_sla_on_chain(sample_decision_result)
    assert result is None


def test_integration_bc_service_interface_i04_register(bc_service):
    """Testa Interface I-04: registro de SLA via API"""
    # Em modo degraded, deve lançar RuntimeError
    with pytest.raises(RuntimeError):
        bc_service.register_sla(
            "test-customer",
            "test-service",
            b"test-hash",
            [("latency", 10, 10)]
        )


def test_integration_bc_service_interface_i04_update(bc_service):
    """Testa Interface I-04: atualização de status via API"""
    # Em modo degraded, deve lançar RuntimeError
    with pytest.raises(RuntimeError):
        bc_service.update_status(1, 0)


def test_integration_bc_service_interface_i04_get(bc_service):
    """Testa Interface I-04: obtenção de SLA via API"""
    # Em modo degraded, deve retornar None
    result = bc_service.get_sla(1)
    assert result is None


@pytest.mark.asyncio
async def test_integration_decision_result_to_blockchain(bc_service, sample_decision_result):
    """Testa conversão de DecisionResult para formato blockchain"""
    # Verificar que DecisionResult tem campos necessários
    assert sample_decision_result.intent_id is not None
    assert sample_decision_result.action == DecisionAction.ACCEPT
    assert sample_decision_result.slos is not None
    assert len(sample_decision_result.slos) > 0
    
    # Em modo degraded, register_sla_on_chain retorna None
    result = bc_service.register_sla_on_chain(sample_decision_result)
    assert result is None

