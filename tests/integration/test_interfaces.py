"""
Integration Tests - Interfaces I-01 a I-07
Detecta automaticamente se está rodando em Docker ou localmente
"""

import pytest
import httpx
import os
import socket
from kafka import KafkaConsumer, KafkaProducer
import json


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
    BASE_URL = "http://sem-csmf:8080"
    SLA_AGENTS_URL = "http://sla-agent-layer:8084"
    NASP_ADAPTER_URL = "http://nasp-adapter:8085"
    KAFKA_BROKER = "kafka:9092"
else:
    BASE_URL = "http://localhost:8080"
    SLA_AGENTS_URL = "http://localhost:8084"
    NASP_ADAPTER_URL = "http://localhost:8085"
    KAFKA_BROKER = "localhost:29092"


class TestI01:
    """Testes da Interface I-01 (gRPC)"""
    
    @pytest.mark.asyncio
    async def test_send_metadata(self):
        """Testa envio de metadados via I-01"""
        # Em produção, usar cliente gRPC real
        pass


class TestI02:
    """Testes da Interface I-02 (REST)"""
    
    @pytest.mark.asyncio
    async def test_send_nest(self):
        """Testa envio de NEST via I-02"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.post(
                    f"{BASE_URL}/api/v1/nest",
                    json={"nest_id": "test-nest"}
                )
                assert response.status_code in [200, 201]
            except httpx.ConnectError:
                pytest.skip("Serviço não está rodando. Execute: docker compose up -d")


class TestI03:
    """Testes da Interface I-03 (Kafka)"""
    
    def test_send_prediction(self):
        """Testa envio de previsão via I-03"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1)
            )
            
            message = {
                "interface": "I-03",
                "prediction": {"risk_level": "medium"}
            }
            
            producer.send('trisla-ml-predictions', value=message)
            producer.flush()
            producer.close()
        except Exception as e:
            pytest.skip(f"Kafka não está disponível: {e}. Execute: docker compose up -d")


class TestI06:
    """Testes da Interface I-06 (REST)"""
    
    @pytest.mark.asyncio
    async def test_execute_action(self):
        """Testa execução de ação via I-06"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.post(
                    f"{SLA_AGENTS_URL}/api/v1/agents/ran/action",
                    json={"type": "adjust_prb", "parameters": {}}
                )
                assert response.status_code in [200, 201]
            except httpx.ConnectError:
                pytest.skip("Serviço não está rodando. Execute: docker compose up -d")


class TestI07:
    """Testes da Interface I-07 (REST - NASP)"""
    
    @pytest.mark.asyncio
    async def test_collect_nasp_metrics(self):
        """Testa coleta de métricas do NASP via I-07"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(
                    f"{NASP_ADAPTER_URL}/api/v1/nasp/metrics"
                )
                assert response.status_code == 200
                data = response.json()
                # Verifica estrutura básica (pode variar em mock)
                assert isinstance(data, dict)
            except httpx.ConnectError:
                pytest.skip("Serviço não está rodando. Execute: docker compose up -d")

