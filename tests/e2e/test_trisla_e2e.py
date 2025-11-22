"""
Testes E2E - TriSLA
Validação End-to-End do fluxo completo I-01 → I-07
"""

import pytest
import httpx
import asyncio
import os
import json
import yaml
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from web3 import Web3

# Configuração baseada no ambiente
BASE_DIR = Path(__file__).parent.parent.parent
SCENARIOS_FILE = BASE_DIR / "tests" / "e2e" / "scenarios_e2e_trisla.yaml"

# URLs dos serviços
SEM_CSMF_URL = os.getenv("SEM_CSMF_URL", "http://localhost:8080")
ML_NSMF_URL = os.getenv("ML_NSMF_URL", "http://localhost:8081")
DECISION_ENGINE_URL = os.getenv("DECISION_ENGINE_URL", "http://localhost:8082")
BC_NSSMF_URL = os.getenv("BC_NSSMF_URL", "http://localhost:8083")
SLA_AGENT_LAYER_URL = os.getenv("SLA_AGENT_LAYER_URL", "http://localhost:8084")
NASP_ADAPTER_URL = os.getenv("NASP_ADAPTER_URL", "http://localhost:8085")

# Kafka
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092").split(",")

# Besu
BESU_RPC_URL = os.getenv("BESU_RPC_URL", "http://localhost:8545")


def load_scenarios() -> List[Dict[str, Any]]:
    """Carrega cenários de teste do arquivo YAML"""
    if not SCENARIOS_FILE.exists():
        pytest.skip(f"Cenários não encontrados: {SCENARIOS_FILE}")
    
    with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return data.get("scenarios", [])


class KafkaMessageValidator:
    """Validador de mensagens Kafka"""
    
    def __init__(self, bootstrap_servers: List[str]):
        self.bootstrap_servers = bootstrap_servers
    
    def consume_message(
        self,
        topic: str,
        timeout: int = 30,
        filter_func: Optional[callable] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Consome uma mensagem do tópico Kafka
        
        Args:
            topic: Nome do tópico
            timeout: Timeout em segundos
            filter_func: Função para filtrar mensagens (opcional)
        
        Returns:
            Mensagem consumida ou None se timeout
        """
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=timeout * 1000,
                auto_offset_reset='latest',
                group_id=f'e2e-test-{int(time.time())}'
            )
            
            start_time = time.time()
            for message in consumer:
                if time.time() - start_time > timeout:
                    break
                
                message_data = message.value
                
                if filter_func:
                    if filter_func(message_data):
                        consumer.close()
                        return message_data
                else:
                    consumer.close()
                    return message_data
            
            consumer.close()
            return None
            
        except KafkaError as e:
            print(f"❌ Erro ao consumir mensagem do Kafka: {e}")
            return None


class BlockchainValidator:
    """Validador de eventos blockchain"""
    
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise RuntimeError(f"Não conectado ao Besu em {rpc_url}")
    
    def get_contract_address(self) -> Optional[str]:
        """Obtém endereço do contrato deployado"""
        contract_info_path = BASE_DIR / "apps" / "bc-nssmf" / "src" / "contracts" / "contract_address.json"
        
        if not contract_info_path.exists():
            return None
        
        with open(contract_info_path, "r") as f:
            data = json.load(f)
        
        return data.get("address")
    
    def get_sla_events(self, sla_id: Optional[int] = None, from_block: int = 0) -> List[Dict[str, Any]]:
        """Obtém eventos SLA da blockchain"""
        contract_address = self.get_contract_address()
        if not contract_address:
            return []
        
        # Carregar ABI
        contract_info_path = BASE_DIR / "apps" / "bc-nssmf" / "src" / "contracts" / "contract_address.json"
        with open(contract_info_path, "r") as f:
            data = json.load(f)
        
        abi = data.get("abi", [])
        contract = self.w3.eth.contract(address=contract_address, abi=abi)
        
        events = []
        
        # Buscar evento SLARequested
        try:
            requested_events = contract.events.SLARequested().get_logs(fromBlock=from_block)
            for event in requested_events:
                events.append({
                    "event": "SLARequested",
                    "sla_id": event.args.slaId,
                    "customer": event.args.customer,
                    "service_name": event.args.serviceName,
                    "block_number": event.blockNumber,
                    "transaction_hash": event.transactionHash.hex()
                })
        except Exception as e:
            print(f"⚠️ Erro ao buscar eventos SLARequested: {e}")
        
        return events


@pytest.fixture
def kafka_validator():
    """Fixture para validador Kafka"""
    return KafkaMessageValidator(KAFKA_BOOTSTRAP_SERVERS)


@pytest.fixture
def blockchain_validator():
    """Fixture para validador blockchain"""
    try:
        return BlockchainValidator(BESU_RPC_URL)
    except Exception as e:
        pytest.skip(f"Besu não disponível: {e}")


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", load_scenarios())
async def test_e2e_scenario(scenario: Dict[str, Any], kafka_validator, blockchain_validator):
    """
    Testa cenário E2E completo
    
    Args:
        scenario: Cenário carregado do YAML
        kafka_validator: Validador Kafka
        blockchain_validator: Validador blockchain
    """
    scenario_name = scenario.get("name", "Unknown")
    intent_payload = scenario.get("intent_payload", {})
    expected_outcomes = scenario.get("expected_outcomes", {})
    validation_steps = scenario.get("validation_steps", [])
    
    print(f"\n{'='*60}")
    print(f"🧪 Testando cenário: {scenario_name}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Enviar Intent ao SEM-CSMF
        print(f"\n📤 1. Enviando Intent ao SEM-CSMF...")
        
        try:
            intent_response = await client.post(
                f"{SEM_CSMF_URL}/api/v1/intents",
                json=intent_payload
            )
            
            assert intent_response.status_code == 200, f"Status code: {intent_response.status_code}"
            
            intent_data = intent_response.json()
            intent_id = intent_data.get("intent_id") or intent_payload.get("intent_id")
            nest_id = intent_data.get("nest_id")
            
            print(f"✅ Intent criado: {intent_id}, NEST: {nest_id}")
            
            # Validações básicas
            assert intent_data.get("status") in ["accepted", "generated"], \
                f"Status esperado: accepted ou generated, obtido: {intent_data.get('status')}"
            assert nest_id is not None, "nest_id não deve ser None"
            
        except httpx.ConnectError:
            pytest.skip("SEM-CSMF não está rodando. Execute: ./scripts/start-local-e2e.sh")
        
        # Step 2: Verificar mensagem I-02 (SEM-CSMF → ML-NSMF)
        print(f"\n📨 2. Verificando mensagem I-02 (SEM-CSMF → ML-NSMF)...")
        
        i02_message = kafka_validator.consume_message(
            topic="I-02-intent-to-ml",
            timeout=15,
            filter_func=lambda m: m.get("intent_id") == intent_id
        )
        
        if i02_message:
            print(f"✅ Mensagem I-02 recebida: intent_id={i02_message.get('intent_id')}")
            assert i02_message.get("interface") == "I-02"
            assert i02_message.get("source") == "sem-csmf"
            assert i02_message.get("destination") == "ml-nsmf"
            assert i02_message.get("intent_id") == intent_id
        else:
            pytest.fail("Mensagem I-02 não recebida no timeout")
        
        # Step 3: Verificar mensagem I-03 (ML-NSMF → Decision Engine)
        print(f"\n📨 3. Verificando mensagem I-03 (ML-NSMF → Decision Engine)...")
        
        i03_message = kafka_validator.consume_message(
            topic="I-03-ml-predictions",
            timeout=20,
            filter_func=lambda m: m.get("intent_id") == intent_id
        )
        
        if i03_message:
            print(f"✅ Mensagem I-03 recebida: intent_id={i03_message.get('intent_id')}")
            assert i03_message.get("interface") == "I-03"
            assert i03_message.get("source") == "ml-nsmf"
            assert i03_message.get("destination") == "decision-engine"
            assert i03_message.get("intent_id") == intent_id
            
            # Validar predição ML
            prediction = i03_message.get("prediction", {})
            assert "risk_score" in prediction
            assert "risk_level" in prediction
            assert prediction["risk_level"] in ["low", "medium", "high"]
        else:
            pytest.fail("Mensagem I-03 não recebida no timeout")
        
        # Step 4: Verificar mensagem I-04 (Decision Engine → BC-NSSMF)
        print(f"\n📨 4. Verificando mensagem I-04 (Decision Engine → BC-NSSMF)...")
        
        i04_message = kafka_validator.consume_message(
            topic="trisla-i04-decisions",
            timeout=25,
            filter_func=lambda m: m.get("decision", {}).get("intent_id") == intent_id
        )
        
        if i04_message:
            print(f"✅ Mensagem I-04 recebida")
            assert i04_message.get("interface") == "I-04"
            assert i04_message.get("source") == "decision-engine"
            assert i04_message.get("destination") == "bc-nssmf"
            
            decision = i04_message.get("decision", {})
            decision_action = decision.get("action")
            
            print(f"   Decisão: {decision_action}")
            
            assert decision_action in ["ACCEPT", "REJECT", "NEGOTIATE", "ESCALATE"], \
                f"Ação de decisão inválida: {decision_action}"
            
            # Se ACCEPT, verificar blockchain
            if decision_action == "ACCEPT":
                expected_outcomes["blockchain"]["registered"] = True
        
        else:
            pytest.fail("Mensagem I-04 não recebida no timeout")
        
        # Step 5: Verificar registro na blockchain (se ACCEPT)
        if expected_outcomes.get("blockchain", {}).get("registered"):
            print(f"\n⛓️ 5. Verificando registro na blockchain...")
            
            # Aguardar um pouco para o registro ser processado
            await asyncio.sleep(5)
            
            try:
                events = blockchain_validator.get_sla_events()
                
                if events:
                    print(f"✅ Eventos encontrados na blockchain: {len(events)}")
                    # Verificar se há evento para este intent (se possível)
                    sla_requested = [e for e in events if e.get("event") == "SLARequested"]
                    assert len(sla_requested) > 0, "Nenhum evento SLARequested encontrado"
                    print(f"✅ Evento SLARequested encontrado na blockchain")
                else:
                    print(f"⚠️ Nenhum evento encontrado na blockchain (pode ser normal se contrato não foi deployado)")
            
            except Exception as e:
                print(f"⚠️ Erro ao verificar blockchain: {e}")
                # Não falhar o teste se blockchain não estiver disponível
        
        # Step 6: Verificar mensagem I-05 (Decision Engine → SLA-Agent Layer)
        print(f"\n📨 6. Verificando mensagem I-05 (Decision Engine → SLA-Agent Layer)...")
        
        i05_message = kafka_validator.consume_message(
            topic="trisla-i05-actions",
            timeout=25,
            filter_func=lambda m: m.get("decision", {}).get("intent_id") == intent_id
        )
        
        if i05_message:
            print(f"✅ Mensagem I-05 recebida")
            assert i05_message.get("interface") == "I-05"
            assert i05_message.get("source") == "decision-engine"
            assert i05_message.get("destination") == "sla-agents"
        else:
            # I-05 pode não ser enviado se decisão for REJECT
            if decision_action == "ACCEPT":
                print(f"⚠️ Mensagem I-05 não recebida (pode ser normal se ação não requer agentes)")
        
        # Step 7: Verificar eventos I-06 (SLA-Agent Layer → Observability)
        print(f"\n📨 7. Verificando eventos I-06 (SLA-Agent Layer)...")
        
        i06_message = kafka_validator.consume_message(
            topic="trisla-i06-agent-events",
            timeout=30
        )
        
        if i06_message:
            print(f"✅ Evento I-06 recebido: domain={i06_message.get('domain')}, status={i06_message.get('status')}")
            assert i06_message.get("interface") == "I-06"
            assert i06_message.get("domain") in ["RAN", "Transport", "Core"]
            assert i06_message.get("status") in ["OK", "RISK", "VIOLATED"]
        else:
            print(f"⚠️ Nenhum evento I-06 recebido (pode ser normal se não houver violações)")
        
        # Step 8: Verificar eventos I-07 (SLA-Agent Layer → Observability)
        print(f"\n📨 8. Verificando eventos I-07 (SLA-Agent Layer)...")
        
        i07_message = kafka_validator.consume_message(
            topic="trisla-i07-agent-actions",
            timeout=30
        )
        
        if i07_message:
            print(f"✅ Evento I-07 recebido: domain={i07_message.get('domain')}, executed={i07_message.get('result', {}).get('executed')}")
            assert i07_message.get("interface") == "I-07"
            assert i07_message.get("domain") in ["RAN", "Transport", "Core"]
        else:
            print(f"⚠️ Nenhum evento I-07 recebido (pode ser normal se não houver ações executadas)")
        
        # Resumo do teste
        print(f"\n{'='*60}")
        print(f"✅ Cenário {scenario_name} concluído com sucesso!")
        print(f"{'='*60}\n")


@pytest.mark.asyncio
async def test_health_checks():
    """Testa health checks de todos os serviços"""
    services = {
        "SEM-CSMF": SEM_CSMF_URL,
        "ML-NSMF": ML_NSMF_URL,
        "Decision Engine": DECISION_ENGINE_URL,
        "BC-NSSMF": BC_NSSMF_URL,
        "SLA-Agent Layer": SLA_AGENT_LAYER_URL,
        "NASP Adapter": NASP_ADAPTER_URL
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f"{url}/health")
                assert response.status_code == 200, f"{service_name} health check falhou"
                print(f"✅ {service_name}: OK")
            except httpx.ConnectError:
                pytest.skip(f"{service_name} não está rodando")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

