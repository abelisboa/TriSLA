# Implementação — BC-NSSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `BC_NSSMF_COMPLETE_GUIDE.md` (seções Arquitetura, API REST, Oracle, Integração, Troubleshooting)

---

## 📋 Sumário

1. [Arquitetura do Módulo](#arquitetura-do-módulo)
2. [Componentes Principais](#componentes-principais)
3. [Interfaces de Comunicação](#interfaces-de-comunicação)
4. [Configuração](#configuração)
5. [Exemplos de Implementação](#exemplos-de-implementação)
6. [Troubleshooting](#troubleshooting)

---

## Arquitetura do Módulo

### Estrutura de Diretórios

```
apps/bc-nssmf/
├── src/
│   ├── main.py                 # Aplicação FastAPI
│   ├── service.py               # BCService (integração Web3)
│   ├── api_rest.py              # Endpoints REST
│   ├── api_grpc_server.py       # Servidor gRPC (placeholder)
│   ├── models.py                # Modelos Pydantic
│   ├── config.py                # Configuração
│   ├── oracle.py                # MetricsOracle
│   ├── kafka_consumer.py        # Consumer Kafka (I-04)
│   ├── deploy_contracts.py      # Script de deploy
│   └── contracts/
│       ├── SLAContract.sol      # Smart Contract Solidity
│       └── contract_address.json # Endereço e ABI do contrato
├── blockchain/
│   └── besu/
│       ├── docker-compose-besu.yaml
│       ├── genesis.json
│       └── data/
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

### Tecnologias Utilizadas

- **Framework**: FastAPI (Python 3.10+)
- **Blockchain**: Hyperledger Besu (Ethereum permissionado)
- **Smart Contracts**: Solidity 0.8.20
- **Web3**: web3.py
- **Comunicação**: Kafka (kafka-python)
- **Observabilidade**: OpenTelemetry

---

## Componentes Principais

### 1. BCService

**Arquivo:** `src/service.py`

**Responsabilidades:**
- Integração Web3 com Besu
- Execução de transações on-chain
- Processamento de eventos

**Métodos principais:**
```python
class BCService:
    def register_sla(self, customer, service_name, sla_hash, slos) -> Dict:
        """Registra SLA on-chain"""
        
    def update_status(self, sla_id, status) -> Dict:
        """Atualiza status de SLA"""
        
    def get_sla(self, sla_id) -> Dict:
        """Consulta SLA"""
```

### 2. DecisionConsumer

**Arquivo:** `src/kafka_consumer.py`

**Responsabilidades:**
- Consumir decisões do Decision Engine (I-04)
- Processar mensagens assíncronas
- Disparar registro on-chain

### 3. MetricsOracle

**Arquivo:** `src/oracle.py`

**Responsabilidades:**
- Obter métricas do NASP Adapter
- Validar violações de SLA
- Atualizar status on-chain

### 4. API REST

**Arquivo:** `src/api_rest.py`

**Endpoints:**
- `POST /bc/register`: Registra SLA on-chain
- `POST /bc/update`: Atualiza status de SLA
- `GET /bc/{sla_id}`: Consulta SLA por ID
- `GET /bc/events/{sla_id}`: Consulta eventos de um SLA

---

## Interfaces de Comunicação

### Interface I-04 (Kafka)

**Protocolo:** Kafka  
**Direção:** Decision Engine → BC-NSSMF  
**Tópico:** `trisla-i04-decisions`

**Implementação:**
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'trisla-i04-decisions',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    decision = message.value
    # Processar decisão e registrar SLA on-chain
```

### API REST

**Base URL:** `http://bc-nssmf:8083`

**Exemplo:**
```bash
curl -X POST http://localhost:8083/bc/register \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "tenant-001",
    "serviceName": "URLLC-Slice",
    "slaHash": "0x...",
    "slos": [
      {"name": "latency", "value": 10, "threshold": 10}
    ]
  }'
```

---

## Configuração

### Variáveis de Ambiente

```bash
# Blockchain
TRISLA_RPC_URL=http://127.0.0.1:8545
TRISLA_CHAIN_ID=1337
TRISLA_PRIVATE_KEY=0x...
TRISLA_DEV_PRIVATE_KEY=0x...

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_DECISIONS=trisla-i04-decisions

# OpenTelemetry
OTLP_ENDPOINT=http://otlp-collector:4317
```

### Dependências

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
web3==6.11.0
kafka-python==2.0.2
httpx==0.25.0
opentelemetry-api==1.21.0
pydantic==2.5.0
```

---

## Exemplos de Implementação

### Exemplo 1: Registrar SLA On-Chain

```python
from service import BCService

service = BCService()

receipt = service.register_sla(
    customer="tenant-001",
    service_name="URLLC-Slice",
    sla_hash=bytes32_hash,
    slos=[("latency", 10, 10), ("throughput", 100, 100)]
)

print(f"SLA registrado: {receipt['slaId']}")
print(f"Transação: {receipt['transactionHash']}")
```

### Exemplo 2: Atualizar Status

```python
receipt = service.update_status(
    sla_id=1,
    status=2  # ACTIVE
)

print(f"Status atualizado: {receipt['status']}")
```

---

## Troubleshooting

### Problema 1: Besu não conecta

**Sintoma:** `ConnectionError` ao conectar ao RPC

**Solução:**
- Verificar se Besu está rodando: `docker ps`
- Verificar `TRISLA_RPC_URL`
- Verificar firewall

### Problema 2: Transação falha

**Sintoma:** `TransactionFailed` ou `InsufficientFunds`

**Solução:**
- Verificar saldo da conta
- Verificar gas price
- Verificar nonce

### Problema 3: Kafka não recebe mensagens

**Sintoma:** Consumer não recebe decisões

**Solução:**
- Verificar se Kafka está rodando
- Verificar `KAFKA_BOOTSTRAP_SERVERS`
- Verificar tópico existe

---

## Observabilidade

### Métricas Prometheus

- `trisla_slas_registered_total`: Total de SLAs registrados
- `trisla_blockchain_transactions_total`: Total de transações
- `trisla_blockchain_transaction_duration_seconds`: Duração de transação

### Traces OpenTelemetry

- Span: `bc_nssmf.receive_decision` (I-04)
- Span: `bc_nssmf.register_sla`
- Span: `bc_nssmf.blockchain_transaction`

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `BC_NSSMF_COMPLETE_GUIDE.md` — Seções "Arquitetura", "API REST", "Oracle", "Integração", "Troubleshooting"

**Última atualização:** 2025-01-27  
**Versão:** S4.0

