"""
Testes de Integração entre Módulos TriSLA
Testa comunicação e fluxo de dados entre diferentes módulos
"""

import pytest
import httpx
import asyncio
import os
import socket
from datetime import datetime


def is_docker_environment():
    """Detecta se está rodando dentro do Docker Compose"""
    if os.path.exists('/.dockerenv'):
        return True
    try:
        socket.gethostbyname('sem-csmf')
        return True
    except socket.gaierror:
        return False


# URLs baseadas no ambiente
if is_docker_environment():
    SEM_CSMF_URL = "http://sem-csmf:8080"
    ML_NSMF_URL = "http://ml-nsmf:8081"
    DECISION_ENGINE_URL = "http://decision-engine:8082"
    SLA_AGENT_URL = "http://sla-agent-layer:8084"
else:
    SEM_CSMF_URL = "http://localhost:8080"
    ML_NSMF_URL = "http://localhost:8081"
    DECISION_ENGINE_URL = "http://localhost:8082"
    SLA_AGENT_URL = "http://localhost:8084"


class TestModuleIntegration:
    """Testes de integração entre módulos"""
    
    @pytest.mark.asyncio
    async def test_sem_csmf_to_nest_flow(self):
        """Testa fluxo: SEM-CSMF cria intent e gera NEST"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Criar intent no SEM-CSMF
                intent_data = {
                    "intent_id": f"integration-intent-{datetime.now().timestamp()}",
                    "service_type": "eMBB",
                    "sla_requirements": {
                        "latency": "10ms",
                        "throughput": "100Mbps"
                    }
                }
                
                intent_response = await client.post(
                    f"{SEM_CSMF_URL}/api/v1/intents",
                    json=intent_data
                )
                assert intent_response.status_code == 200
                intent_result = intent_response.json()
                assert intent_result["status"] == "accepted"
                assert "nest_id" in intent_result
                
                # 2. Verificar NEST foi criado
                nest_id = intent_result["nest_id"]
                nest_response = await client.get(
                    f"{SEM_CSMF_URL}/api/v1/nests/{nest_id}"
                )
                assert nest_response.status_code == 200
                nest_data = nest_response.json()
                assert nest_data["nest_id"] == nest_id
                assert nest_data["intent_id"] == intent_data["intent_id"]
                assert len(nest_data["network_slices"]) > 0
                
                # 3. Verificar slice aparece na lista
                slices_response = await client.get(
                    f"{SEM_CSMF_URL}/api/v1/slices"
                )
                assert slices_response.status_code == 200
                slices_data = slices_response.json()
                assert slices_data["total"] > 0
                
                # Verificar que o slice do intent criado está na lista
                intent_slices = [
                    s for s in slices_data["slices"]
                    if s["intent_id"] == intent_data["intent_id"]
                ]
                assert len(intent_slices) > 0
                
            except httpx.ConnectError:
                pytest.skip("Serviços não estão rodando")
    
    @pytest.mark.asyncio
    async def test_sla_agent_metrics_collection(self):
        """Testa coleta de métricas do SLA-Agent Layer"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Verificar health de todos os agentes
                health_response = await client.get(f"{SLA_AGENT_URL}/health")
                assert health_response.status_code == 200
                health_data = health_response.json()
                assert health_data["status"] == "healthy"
                assert "agents" in health_data
                assert all([
                    health_data["agents"]["ran"],
                    health_data["agents"]["transport"],
                    health_data["agents"]["core"]
                ])
                
                # 2. Coletar métricas de cada agente
                ran_metrics = await client.post(f"{SLA_AGENT_URL}/api/v1/agents/ran/collect")
                assert ran_metrics.status_code == 200
                ran_data = ran_metrics.json()
                assert "domain" in ran_data
                assert ran_data["domain"] == "RAN"
                
                transport_metrics = await client.post(f"{SLA_AGENT_URL}/api/v1/agents/transport/collect")
                assert transport_metrics.status_code == 200
                
                core_metrics = await client.post(f"{SLA_AGENT_URL}/api/v1/agents/core/collect")
                assert core_metrics.status_code == 200
                
                # 3. Verificar métricas agregadas
                aggregated_response = await client.get(f"{SLA_AGENT_URL}/api/v1/metrics/realtime")
                assert aggregated_response.status_code == 200
                aggregated_data = aggregated_response.json()
                assert "domains" in aggregated_data
                assert len(aggregated_data["domains"]) == 3
                
            except httpx.ConnectError:
                pytest.skip("Serviços não estão rodando")
    
    @pytest.mark.asyncio
    async def test_sla_agent_slos_monitoring(self):
        """Testa monitoramento de SLOs no SLA-Agent Layer"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Obter SLOs
                slos_response = await client.get(f"{SLA_AGENT_URL}/api/v1/slos")
                assert slos_response.status_code == 200
                slos_data = slos_response.json()
                
                # 2. Validar estrutura
                assert "slos" in slos_data
                assert "compliance" in slos_data
                assert "overall_compliance" in slos_data
                
                # 3. Verificar cada domínio tem SLOs
                for domain in ["ran", "transport", "core"]:
                    assert domain in slos_data["slos"]
                    domain_slos = slos_data["slos"][domain]
                    assert "slos" in domain_slos
                    assert len(domain_slos["slos"]) > 0
                    assert "compliance_rate" in domain_slos
                
                # 4. Validar compliance rates
                assert 0.0 <= slos_data["overall_compliance"] <= 1.0
                for domain in ["ran", "transport", "core"]:
                    compliance = slos_data["compliance"][domain]
                    assert 0.0 <= compliance <= 1.0
                
            except httpx.ConnectError:
                pytest.skip("Serviços não estão rodando")
    
    @pytest.mark.asyncio
    async def test_cross_module_data_flow(self):
        """Testa fluxo de dados entre múltiplos módulos"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. SEM-CSMF: Criar intent
                intent_response = await client.post(
                    f"{SEM_CSMF_URL}/api/v1/intents",
                    json={
                        "intent_id": f"cross-module-{datetime.now().timestamp()}",
                        "service_type": "URLLC",
                        "sla_requirements": {
                            "latency": "1ms",
                            "reliability": 0.99999
                        }
                    }
                )
                assert intent_response.status_code == 200
                intent_data = intent_response.json()
                nest_id = intent_data["nest_id"]
                
                # 2. SEM-CSMF: Verificar NEST criado
                nest_response = await client.get(f"{SEM_CSMF_URL}/api/v1/nests/{nest_id}")
                assert nest_response.status_code == 200
                nest = nest_response.json()
                
                # 3. SEM-CSMF: Verificar slice criado
                slices_response = await client.get(f"{SEM_CSMF_URL}/api/v1/slices")
                assert slices_response.status_code == 200
                slices = slices_response.json()
                assert slices["total"] > 0
                
                # 4. SLA-Agent: Verificar métricas disponíveis
                metrics_response = await client.get(f"{SLA_AGENT_URL}/api/v1/metrics/realtime")
                assert metrics_response.status_code == 200
                metrics = metrics_response.json()
                assert metrics["summary"]["total_domains"] == 3
                
                # 5. SLA-Agent: Verificar SLOs
                slos_response = await client.get(f"{SLA_AGENT_URL}/api/v1/slos")
                assert slos_response.status_code == 200
                slos = slos_response.json()
                assert "overall_compliance" in slos
                
                # 6. Validar que os dados são consistentes
                # O slice criado deve ter recursos compatíveis com os SLOs
                created_slice = next(
                    (s for s in slices["slices"] if s["nest_id"] == nest_id),
                    None
                )
                assert created_slice is not None
                assert created_slice["slice_type"] == "URLLC"
                
            except httpx.ConnectError:
                pytest.skip("Serviços não estão rodando")
    
    @pytest.mark.asyncio
    async def test_all_modules_health(self):
        """Testa health de todos os módulos principais"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                modules = [
                    ("SEM-CSMF", SEM_CSMF_URL),
                    ("SLA-Agent", SLA_AGENT_URL),
                ]
                
                # Adicionar módulos opcionais se disponíveis
                try:
                    ml_response = await client.get(f"{ML_NSMF_URL}/health", timeout=5.0)
                    if ml_response.status_code == 200:
                        modules.append(("ML-NSMF", ML_NSMF_URL))
                except:
                    pass
                
                try:
                    de_response = await client.get(f"{DECISION_ENGINE_URL}/health", timeout=5.0)
                    if de_response.status_code == 200:
                        modules.append(("Decision-Engine", DECISION_ENGINE_URL))
                except:
                    pass
                
                # Verificar health de cada módulo
                for module_name, module_url in modules:
                    response = await client.get(f"{module_url}/health")
                    assert response.status_code == 200, f"{module_name} deve estar saudável"
                    health_data = response.json()
                    assert health_data["status"] == "healthy", f"{module_name} status deve ser healthy"
                
            except httpx.ConnectError:
                pytest.skip("Serviços não estão rodando")

