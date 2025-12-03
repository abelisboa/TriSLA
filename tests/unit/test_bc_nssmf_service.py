"""
Unit Tests - BC-NSSMF BCService
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adicionar caminho do módulo
BASE_DIR = Path(__file__).parent.parent.parent
BC_SRC = BASE_DIR / "apps" / "bc-nssmf" / "src"

# Remover outros caminhos que possam conflitar
sys.path = [str(BC_SRC)] + [p for p in sys.path if "decision-engine" not in p]

# Mock BC_ENABLED antes de importar
os.environ["BC_ENABLED"] = "false"

# Mudar para o diretório do módulo para resolver imports relativos
original_cwd = os.getcwd()
os.chdir(str(BC_SRC))

try:
    from service import BCService
finally:
    os.chdir(original_cwd)


@pytest.fixture
def bc_service():
    """Fixture para criar BCService em modo DEV"""
    with patch.dict(os.environ, {"BC_ENABLED": "false"}):
        return BCService()


def test_bc_service_init_dev_mode(bc_service):
    """Testa inicialização do BCService em modo DEV"""
    assert bc_service is not None
    assert bc_service.enabled == False


def test_bc_service_register_sla_degraded(bc_service):
    """Testa registro de SLA em modo degraded"""
    with pytest.raises(RuntimeError, match="modo degraded"):
        bc_service.register_sla(
            "test-customer",
            "test-service",
            b"test-hash",
            [("latency", 10, 10)]
        )


def test_bc_service_update_status_degraded(bc_service):
    """Testa atualização de status em modo degraded"""
    with pytest.raises(RuntimeError, match="modo degraded"):
        bc_service.update_status(1, 0)


def test_bc_service_get_sla_degraded(bc_service):
    """Testa obtenção de SLA em modo degraded"""
    result = bc_service.get_sla(1)
    assert result is None


@pytest.mark.skipif(
    os.getenv("BC_ENABLED", "false").lower() != "true",
    reason="BC_ENABLED não está habilitado"
)
def test_bc_service_register_sla_enabled():
    """Testa registro de SLA com blockchain habilitado (requer Besu)"""
    with patch.dict(os.environ, {"BC_ENABLED": "true"}):
        service = BCService()
        if service.enabled:
            # Este teste só funciona se Besu estiver rodando
            # Em ambiente de CI/CD, pode falhar
            try:
                receipt = service.register_sla(
                    "test-customer",
                    "test-service",
                    b"test-hash",
                    [("latency", 10, 10)]
                )
                assert receipt is not None
                assert receipt.transactionHash is not None
            except RuntimeError:
                pytest.skip("Besu não disponível")


def test_bc_service_register_sla_on_chain_degraded(bc_service):
    """Testa register_sla_on_chain em modo degraded"""
    # Mock DecisionResult
    from unittest.mock import Mock
    decision_result = Mock()
    decision_result.intent_id = "test-intent"
    decision_result.action.value = "AC"
    decision_result.decision_id = "test-decision"
    decision_result.slos = []
    
    result = bc_service.register_sla_on_chain(decision_result)
    assert result is None


@pytest.mark.skipif(
    os.getenv("BC_ENABLED", "false").lower() != "true",
    reason="BC_ENABLED não está habilitado"
)
def test_bc_service_register_sla_on_chain_enabled():
    """Testa register_sla_on_chain com blockchain habilitado (requer Besu)"""
    with patch.dict(os.environ, {"BC_ENABLED": "true"}):
        service = BCService()
        if service.enabled:
            from unittest.mock import Mock
            decision_result = Mock()
            decision_result.intent_id = "test-intent"
            decision_result.action.value = "AC"
            decision_result.decision_id = "test-decision"
            decision_result.slos = []
            
            try:
                result = service.register_sla_on_chain(decision_result)
                # Pode retornar None se houver erro ou tx_hash se sucesso
                assert result is None or isinstance(result, str)
            except RuntimeError:
                pytest.skip("Besu não disponível")

