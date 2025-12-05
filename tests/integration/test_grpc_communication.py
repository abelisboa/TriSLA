"""
Testes de Integração - Comunicação gRPC
Testa a comunicação I-01 entre SEM-CSMF e Decision Engine
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Adicionar paths dos módulos
BASE_DIR = Path(__file__).parent.parent.parent
SEM_CSMF_SRC = BASE_DIR / "apps" / "sem-csmf" / "src"
sys.path.insert(0, str(SEM_CSMF_SRC))

from grpc_client import DecisionEngineClient


@pytest.mark.asyncio
async def test_grpc_send_nest_metadata():
    """Testa envio de metadata do NEST via gRPC"""
    client = DecisionEngineClient()
    
    result = await client.send_nest_metadata(
        intent_id="test-grpc-integration",
        nest_id="nest-test-grpc-integration",
        tenant_id="tenant-1",
        service_type="eMBB",
        sla_requirements={"latency": "10ms", "throughput": "100Mbps"},
        nest_status="generated",
        metadata={"test": "integration", "source": "test_grpc_communication"}
    )
    
    assert result.get("success") is True, f"gRPC call failed: {result}"
    assert result.get("decision_id") is not None, "Decision ID should not be None"
    # Status code pode ser 0 (gRPC) ou 200 (HTTP fallback)
    assert result.get("status_code") in [0, 200], f"Status code should be 0 or 200, got {result.get('status_code')}"


@pytest.mark.asyncio
async def test_grpc_multiple_requests():
    """Testa múltiplas requisições gRPC sequenciais"""
    client = DecisionEngineClient()
    
    results = []
    for i in range(3):
        result = await client.send_nest_metadata(
            intent_id=f"test-grpc-multi-{i}",
            nest_id=f"nest-test-grpc-multi-{i}",
            tenant_id="tenant-1",
            service_type="eMBB",
            sla_requirements={"latency": f"{10+i}ms"},
            nest_status="generated",
            metadata={"iteration": i}
        )
        results.append(result)
    
    # Todas as requisições devem ter sucesso
    assert all(r.get("success") for r in results), "All gRPC calls should succeed"
    assert len(set(r.get("decision_id") for r in results if r.get("decision_id"))) == 3, "Each request should have unique decision ID"


@pytest.mark.asyncio
async def test_grpc_error_handling():
    """Testa tratamento de erros na comunicação gRPC"""
    client = DecisionEngineClient()
    
    # Testar com dados inválidos
    result = await client.send_nest_metadata(
        intent_id="",
        nest_id="",
        tenant_id="",
        service_type="",
        sla_requirements={},
        nest_status="invalid",
        metadata={}
    )
    
    # Deve retornar resultado (sucesso ou falha, mas não exceção)
    assert "success" in result, "Result should contain 'success' field"
    assert "status_code" in result, "Result should contain 'status_code' field"


@pytest.mark.asyncio
async def test_grpc_connection_recovery():
    """Testa recuperação de conexão gRPC após falha"""
    client = DecisionEngineClient()
    
    # Primeira chamada
    result1 = await client.send_nest_metadata(
        intent_id="test-grpc-recovery-1",
        nest_id="nest-test-grpc-recovery-1",
        tenant_id="tenant-1",
        service_type="eMBB",
        sla_requirements={"latency": "10ms"},
        nest_status="generated",
        metadata={"test": "recovery"}
    )
    
    # Segunda chamada (deve funcionar mesmo se primeira falhou)
    result2 = await client.send_nest_metadata(
        intent_id="test-grpc-recovery-2",
        nest_id="nest-test-grpc-recovery-2",
        tenant_id="tenant-1",
        service_type="eMBB",
        sla_requirements={"latency": "10ms"},
        nest_status="generated",
        metadata={"test": "recovery"}
    )
    
    # Pelo menos uma deve ter sucesso
    assert result1.get("success") or result2.get("success"), "At least one gRPC call should succeed"

