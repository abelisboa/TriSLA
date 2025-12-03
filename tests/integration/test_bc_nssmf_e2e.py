"""
E2E Tests - BC-NSSMF (Decision Engine → BC-NSSMF → Blockchain)
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
def sample_decision_result_accept():
    """Fixture para criar DecisionResult ACCEPT"""
    return DecisionResult(
        decision_id="dec-e2e-001",
        intent_id="test-intent-e2e-001",
        nest_id="test-nest-e2e-001",
        action=DecisionAction.ACCEPT,
        reasoning="SLA aceito - risco baixo",
        confidence=0.9,
        ml_risk_score=0.2,
        ml_risk_level=None,
        slos=[
            SLARequirement(name="latency", value=10.0, threshold=10.0, unit="ms"),
            SLARequirement(name="reliability", value=0.99, threshold=0.99, unit="ratio")
        ],
        domains=["RAN", "Transporte"]
    )


@pytest.fixture
def sample_decision_result_reject():
    """Fixture para criar DecisionResult REJECT"""
    return DecisionResult(
        decision_id="dec-e2e-002",
        intent_id="test-intent-e2e-002",
        nest_id="test-nest-e2e-002",
        action=DecisionAction.REJECT,
        reasoning="SLA rejeitado - risco alto",
        confidence=0.85,
        ml_risk_score=0.8,
        ml_risk_level=None,
        slos=[],
        domains=[]
    )


@pytest.mark.asyncio
async def test_e2e_decision_accept_to_blockchain(bc_service, sample_decision_result_accept):
    """Testa E2E: Decision ACCEPT → Blockchain"""
    # Em modo degraded, deve retornar None
    result = bc_service.register_sla_on_chain(sample_decision_result_accept)
    assert result is None  # Modo degraded


@pytest.mark.asyncio
async def test_e2e_decision_reject_skipped(bc_service, sample_decision_result_reject):
    """Testa E2E: Decision REJECT não deve ser registrado no blockchain"""
    # REJECT não deve ser registrado
    result = bc_service.register_sla_on_chain(sample_decision_result_reject)
    assert result is None  # REJECT não é registrado


@pytest.mark.asyncio
async def test_e2e_sla_lifecycle(bc_service, sample_decision_result_accept):
    """Testa E2E: Ciclo de vida completo do SLA"""
    # 1. Registrar SLA (em modo degraded, retorna None)
    tx_hash = bc_service.register_sla_on_chain(sample_decision_result_accept)
    assert tx_hash is None  # Modo degraded
    
    # 2. Obter SLA (em modo degraded, retorna None)
    sla_data = bc_service.get_sla(1)
    assert sla_data is None  # Modo degraded
    
    # 3. Atualizar status (em modo degraded, lança RuntimeError)
    with pytest.raises(RuntimeError):
        bc_service.update_status(1, 3)  # ACTIVE


@pytest.mark.asyncio
async def test_e2e_performance(bc_service, sample_decision_result_accept):
    """Testa performance do fluxo E2E"""
    import time
    
    start_time = time.time()
    result = bc_service.register_sla_on_chain(sample_decision_result_accept)
    end_time = time.time()
    
    elapsed_time = (end_time - start_time) * 1000  # Converter para ms
    
    # Em modo degraded, deve ser rápido (< 100ms)
    assert elapsed_time < 100, f"Fluxo E2E levou {elapsed_time:.2f}ms (esperado < 100ms em modo degraded)"

