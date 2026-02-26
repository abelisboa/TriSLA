"""
E2E Tests - Fluxo Completo TriSLA
Detecta automaticamente se está rodando em Docker ou localmente
"""

import pytest
import httpx
import asyncio
import os
import socket
from datetime import datetime


def is_docker_environment():
    """Detecta se está rodando dentro do Docker Compose"""
    # Verifica se está dentro de um container Docker
    if os.path.exists('/.dockerenv'):
        return True
    # Verifica se pode resolver nomes de serviços Docker
    try:
        socket.gethostbyname('sem-csmf')
        return True
    except socket.gaierror:
        return False


# Configuração baseada no ambiente
if is_docker_environment():
    SEM_CSMF_URL = "http://sem-csmf:8080"
    API_GATEWAY_URL = "http://api-gateway:8080"
else:
    SEM_CSMF_URL = "http://localhost:8080"
    API_GATEWAY_URL = "http://localhost:8080"


class TestFullWorkflow:
    """Testes end-to-end do fluxo completo"""
    
    @pytest.mark.asyncio
    async def test_intent_to_slice_creation(self):
        """Testa fluxo completo: Intent → NEST → Slice"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Criar intent
                intent_response = await client.post(
                    f"{SEM_CSMF_URL}/api/v1/intents",
                    json={
                        "intent_id": f"e2e-intent-{datetime.now().timestamp()}",
                        "service_type": "eMBB",
                        "sla_requirements": {
                            "latency": "10ms",
                            "throughput": "100Mbps"
                        }
                    }
                )
                assert intent_response.status_code == 200
                intent_data = intent_response.json()
                assert intent_data["status"] == "accepted"
                
                # 2. Aguardar processamento
                await asyncio.sleep(5)
                
                # 3. Verificar NEST gerado
                nest_response = await client.get(
                    f"{SEM_CSMF_URL}/api/v1/nests/{intent_data.get('nest_id')}"
                )
                assert nest_response.status_code == 200
                
                # 4. Verificar slice ativo
                slices_response = await client.get(
                    f"{SEM_CSMF_URL}/api/v1/slices"
                )
                assert slices_response.status_code == 200
                slices_data = slices_response.json()
                assert "slices" in slices_data
                assert "total" in slices_data
                assert slices_data["total"] > 0
                
                # Validar estrutura dos slices
                assert len(slices_data["slices"]) > 0
                first_slice = slices_data["slices"][0]
                assert "slice_id" in first_slice
                assert "nest_id" in first_slice
                assert "intent_id" in first_slice
                assert "slice_type" in first_slice
                assert "status" in first_slice
                assert "resources" in first_slice
                
                # Verificar que o slice criado está na lista
                created_slice = next(
                    (s for s in slices_data["slices"] if s["intent_id"] == intent_data["intent_id"]),
                    None
                )
                assert created_slice is not None, "Slice criado deve estar na lista"
                assert created_slice["status"] in ["generated", "active"]
            except httpx.ConnectError:
                pytest.skip("Serviços não estão rodando. Execute: docker compose up -d")
    
    @pytest.mark.asyncio
    async def test_sla_monitoring(self):
        """Testa monitoramento de SLA em tempo real"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Obter métricas do SLA-Agent Layer (porta 8084)
                SLA_AGENT_URL = "http://localhost:8084" if not is_docker_environment() else "http://sla-agent-layer:8084"
                
                metrics_response = await client.get(
                    f"{SLA_AGENT_URL}/api/v1/metrics/realtime"
                )
                assert metrics_response.status_code == 200
                metrics_data = metrics_response.json()
                
                # Validações das métricas
                assert "timestamp" in metrics_data
                assert "domains" in metrics_data
                assert "summary" in metrics_data
                assert metrics_data["summary"]["total_domains"] == 3
                assert metrics_data["summary"]["healthy_domains"] == 3
                
                # Validar estrutura de cada domínio
                for domain_name in ["ran", "transport", "core"]:
                    assert domain_name in metrics_data["domains"]
                    domain_metrics = metrics_data["domains"][domain_name]
                    assert "domain" in domain_metrics
                    assert "timestamp" in domain_metrics
                    assert domain_metrics["status"] == "healthy"
                
                # 2. Verificar SLOs
                slos_response = await client.get(
                    f"{SLA_AGENT_URL}/api/v1/slos"
                )
                assert slos_response.status_code == 200
                slos_data = slos_response.json()
                
                # Validações dos SLOs
                assert "timestamp" in slos_data
                assert "slos" in slos_data
                assert "compliance" in slos_data
                assert "overall_compliance" in slos_data
                
                # Validar que há SLOs para cada domínio
                for domain_name in ["ran", "transport", "core"]:
                    assert domain_name in slos_data["slos"]
                    domain_slos = slos_data["slos"][domain_name]
                    assert "domain" in domain_slos
                    assert "slos" in domain_slos
                    assert isinstance(domain_slos["slos"], list)
                    assert len(domain_slos["slos"]) > 0
                    assert "compliance_rate" in domain_slos
                    assert 0.0 <= domain_slos["compliance_rate"] <= 1.0
                
                # Validar estrutura de cada SLO
                for domain_name in ["ran", "transport", "core"]:
                    for slo in slos_data["slos"][domain_name]["slos"]:
                        assert "name" in slo
                        assert "target" in slo
                        assert "current" in slo
                        assert "compliance" in slo
                        assert isinstance(slo["compliance"], bool)
                
                # Validar overall_compliance
                assert 0.0 <= slos_data["overall_compliance"] <= 1.0
                
            except httpx.ConnectError:
                pytest.skip("Serviços não estão rodando. Execute: docker compose up -d")

