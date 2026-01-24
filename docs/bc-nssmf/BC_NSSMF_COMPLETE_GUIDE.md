# BC-NSSMF Module Complete Guide

**Version:** 3.5.0  
**Date:** 2025-01-27  
**Module:** Blockchain-enabled Network Slice Subnet Management Function

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Module Architecture](#module-architecture)
3. [Smart Contracts](#smart-contracts)
4. [Web3 Integration](#web3-integration)
5. [REST and gRPC API](#rest-and-grpc-api)
6. [Metrics Oracle](#metrics-oracle)
7. [Integration with Other Modules](#integration-with-other-modules)
8. [Interface I-04 (Kafka)](#interface-i-04-kafka)
9. [Deployment and Configuration](#deployment-and-configuration)
10. [Usage Examples](#usage-examples)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **BC-NSSMF (Blockchain-enabled Network Slice Subnet Management Function)** is responsible for registering SLAs on-chain on a permissioned blockchain, ensuring immutability, traceability, and deterministic execution of contractual rules.

### Objectives

1. **On-Chain Registration:** Register approved SLAs by the Decision Engine on the blockchain
2. **Status Update:** Update SLA status (ACTIVE, VIOLATED, TERMINATED)
3. **Violation Registration:** Register SLA violations in an immutable way
4. **audit:** Provide complete audit via on-chain events
5. **Enforcement:** Automatically execute contractual rules

### Main Features

- **Blockchain:** Hyperledger Besu (permissioned Ethereum)
- **Smart Contracts:** Solidity 0.8.20
- **Web3 Client:** web3.py
- **Confirmation Time:** < 5 seconds (local blockchain)
- **Immutability:** All events registered on-chain

---

## 🏗️ Module Architecture

### Directory Structure

```
apps/bc-nssmf/
├── src/
│   ├── main.py                 # FastAPI Application
│   ├── service.py               # BCService (Web3 Integration)
│   ├── api_rest.py              # Endpoints REST
│   ├── api_grpc_server.py       # gRPC Server (placeholder)
│   ├── models.py                # Pydantic Models
│   ├── config.py                # Configuration
│   ├── oracle.py                # MetricsOracle
│   ├── kafka_consumer.py        # Kafka Consumer (I-04)
│   ├── deploy_contracts.py      # Deployment Script
│   └── contracts/
│       ├── SLAContract.sol      # Smart Contract Solidity
│       └── contract_address.json # Contract Address and ABI
├── blockchain/
│   └── besu/
│       ├── docker-compose-besu.yaml  # Docker Compose Besu
│       ├── genesis.json              # Genesis block
│       └── data/                      # Blockchain Data
├── tests/
│   └── unit/                   # Unit Tests
├── Dockerfile
├── requirements.txt
└── README.md
```

### Main Components

1. **BCService** — Main Web3 integration service
2. **SmartContractExecutor** — Smart contract executor
3. **MetricsOracle** — Oracle that obtains metrics from NASP
4. **DecisionConsumer** — Kafka consumer for decisions (I-04)
5. **SLAContract** — Smart Contract Solidity

### Data Flow

```
┌─────────────────┐
│ Decision Engine │  (via Kafka I-04)
│  (ACCEPT decision)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Kafka Consumer  │  (consumes decision)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BCService       │  (registers SLA on-chain)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Smart Contract  │  (SLAContract.sol)
│  (Besu)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ On-Chain Events│  (SLARequested, SLAUpdated)
└─────────────────┘
```

---

## 📜 Smart Contracts

### SLAContract.sol

**Location:** `apps/bc-nssmf/src/contracts/SLAContract.sol`

**Solidity Version:** 0.8.20

#### Structures

```solidity
enum SLAStatus {
    REQUESTED,
    APPROVED,
    REJECTED,
    ACTIVE,
    COMPLETED
}

struct SLO {
    string name;
    uint256 value;
    uint256 threshold;
}

struct SLA {
    uint256 id;
    string customer;
    string serviceName;
    bytes32 slaHash;
    SLAStatus status;
    SLO[] slos;
    uint256 createdAt;
    uint256 updatedAt;
}
```

#### Main Functions

1. **`registerSLA()`**
   - Registers a new SLA on-chain
   - Parameters: `customer`, `serviceName`, `slaHash`, `slos[]`
   - Returns: `slaId` (uint256)
   - Event: `SLARequested`

2. **`updateSLAStatus()`**
   - Updates the status of an SLA
   - Parameters: `slaId`, `newStatus`
   - Event: `SLAUpdated`

3. **`getSLA()`**
   - Queries SLA data
   - Parameters: `slaId`
   - Returns: `customer`, `serviceName`, `status`, `createdAt`, `updatedAt`

#### Events

```solidity
event SLARequested(uint256 indexed slaId, string customer, string serviceName);
event SLAUpdated(uint256 indexed slaId, SLAStatus status);
event SLACompleted(uint256 indexed slaId);
```

### Contract Deployment

**Script:** `apps/bc-nssmf/src/deploy_contracts.py`

**Command:**
```bash
cd apps/bc-nssmf
python src/deploy_contracts.py
```

**Process:**
1. Compiles Solidity contract
2. Connects to Besu RPC
3. Verifies account balance
4. Sends deployment transaction
5. Waits for confirmation
6. Saves address and ABI to `contract_address.json`

**Environment Variables:**
- `TRISLA_RPC_URL` — URL of RPC Besu (default: `http://127.0.0.1:8545`)
- `TRISLA_PRIVATE_KEY` — Private key (production)
- `TRISLA_DEV_PRIVATE_KEY` — Private key (development)
- `TRISLA_CHAIN_ID` — Chain ID (default: `1337`)

---

## 🔗 Web3 Integration

### BCService

**File:** `apps/bc-nssmf/src/service.py`

**Class:** `BCService`

#### Initialization

```python
from service import BCService

service = BCService()
```

**Process:**
1. Connects to Besu RPC via `Web3.HTTPProvider`
2. Loads contract ABI and address
3. Creates contract instance
4. Selects default account

#### Main Methods

1. **`register_sla()`**
   ```python
   receipt = service.register_sla(
       customer="tenant-001",
       service_name="URLLC-Slice",
       sla_hash=bytes32_hash,
       slos=[("latency", 10, 10), ("throughput", 100, 100)]
   )
   ```

2. **`update_status()`**
   ```python
   receipt = service.update_status(
       sla_id=1,
       status=2  # ACTIVE
   )
   ```

3. **`get_sla()`**
   ```python
   sla_data = service.get_sla(sla_id=1)
   # Returns: (customer, serviceName, status, createdAt, updatedAt)
   ```

### Configuration

**File:** `apps/bc-nssmf/src/config.py`

```python
class BCConfig:
    rpc_url: str = "http://127.0.0.1:8545"
    contract_info_path: str = "apps/bc-nssmf/src/contracts/contract_address.json"
```

---

## 🌐 REST and gRPC API

### API REST

**File:** `apps/bc-nssmf/src/api_rest.py`

**Endpoints:**

1. **`POST /bc/register`**
   - Registers SLA on-chain
   - Body: `SLARequest`
   - Returns: `{"status": "ok", "tx": "0x..."}`

2. **`POST /bc/update`**
   - Updates SLA status
   - Body: `SLAStatusUpdate`
   - Returns: `{"status": "ok", "tx": "0x..."}`

3. **`GET /bc/{sla_id}`**
   - Queries SLA
   - Returns: SLA data

**Modelos Pydantic:**

```python
class SLO(BaseModel):
    name: str
    value: int
    threshold: int

class SLARequest(BaseModel):
    customer: str
    serviceName: str
    slaHash: str
    slos: List[SLO]

class SLAStatusUpdate(BaseModel):
    slaId: int
    newStatus: int
```

### gRPC (Placeholder)

**File:** `apps/bc-nssmf/src/api_grpc_server.py`

**Status:** Placeholder funcional (estrutura mínima)

**Note:** The complete implementation de gRPC está nas interfaces I-01 a I-07.

---

## 🔮 Metrics Oracle

### MetricsOracle

**File:** `apps/bc-nssmf/src/oracle.py`

**Class:** `MetricsOracle`

**Function:** obtains real metrics from NASP for smart contract validation.

#### Main Method

```python
metrics = await metrics_oracle.get_metrics()
```

**return:**
```python
{
    "latency": 12.5,
    "throughput": 850.0,
    "packet_loss": 0.001,
    "jitter": 2.3,
    "source": "nasp_real",
    "timestamp": "2025-01-27T10:00:00Z"
}
```

**In Production:**
- Connects to NASP Adapter via HTTP REST
- obtains metrics in real time
- Validates against SLA thresholds

---

## 🔌 Integration with Other Modules

### 1. Decision Engine (Interface I-04)

**Tipo:** Kafka Consumer  
**Topic:** `trisla-i04-decisions`  
**Payload:** Decisão de aceitação/rejeição

**Código:**
```python
from kafka_consumer import DecisionConsumer

consumer = DecisionConsumer(contract_executor, metrics_oracle)

# Consume decisions
result = await consumer.consume_and_execute()
```

**Fluxo:**
1. Decision Engine sends decision `ACCEPT` via Kafka
2. BC-NSSMF consome message
3. BC-NSSMF Registers SLA on-chain
4. BC-NSSMF retorna `tx_hash` e `block_number`

### 2. SLO Reporter

**Tipo:** HTTP REST  
**Endpoint:** `POST /bc/update`  
**Payload:** violation de SLA

**Fluxo:**
1. SLO Reporter detects violation
2. SLO Reporter calls BC-NSSMF
3. BC-NSSMF Updates status for `VIOLATED`
4. BC-NSSMF emits event `SLAUpdated`

### 3. NASP Adapter

**Tipo:** HTTP REST  
**Endpoint:** `http://nasp-adapter:8080/api/v1/metrics`  
**Function:** provide metrics ao Oracle

---

## 📡 Interface I-04 (Kafka)

### topic Kafka

**Nome:** `trisla-i04-decisions`

### schema of Message

```json
{
  "decision": "ACCEPT",
  "nest_id": "nest-urllc-001",
  "sla_data": {
    "tenant_id": "tenant-001",
    "slice_type": "URLLC",
    "requirements": {
      "latency": "10ms",
      "throughput": "100Mbps",
      "reliability": 0.99999
    }
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### Consumer Kafka

**File:** `apps/bc-nssmf/src/kafka_consumer.py`

**Class:** `DecisionConsumer`

**Configuration:**
```python
consumer = KafkaConsumer(
    'trisla-i04-decisions',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='bc-nssmf-consumer'
)
```

---

## 🚀 Deployment and Configuration

### 1. start Blockchain Besu

**Docker Compose:** `apps/bc-nssmf/blockchain/besu/docker-compose-besu.yaml`

**Command:**
```bash
cd apps/bc-nssmf/blockchain/besu
docker-compose -f docker-compose-besu.yaml up -d
```

**Verify:**
```bash
curl http://127.0.0.1:8545
```

### 2. Deploy of Smart Contract

**Command:**
```bash
cd apps/bc-nssmf
python src/deploy_contracts.py
```

**output expected:**
```
[TriSLA] Compiling Solidity contract...
[TriSLA] Usando conta: 0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1
[TriSLA] Saldo of account: 100.0 ETH
[TriSLA] Enviando transação de deploy: 0x...
[TriSLA] Contrato implantado em: 0x42699A7612A82f1d9C36148af9C77354759b210b
[TriSLA] address e ABI salvos to contract_address.json
```

### 3. Configurar Environment Variables

**File:** `.env` ou environment variables

```bash
# Blockchain
TRISLA_RPC_URL=http://127.0.0.1:8545
TRISLA_CHAIN_ID=1337
TRISLA_PRIVATE_KEY=0x...  # production
TRISLA_DEV_PRIVATE_KEY=0x...  # development

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### 4. start Aplicação

**Command:**
```bash
cd apps/bc-nssmf
uvicorn src.main:app --host 0.0.0.0 --port 8083
```

**Verify:**
```bash
curl http://localhost:8083/health
```

---

## 💡 Usage Examples

### Exemplo 1: Registrar SLA On-Chain

**Via API REST:**
```bash
curl -X POST http://localhost:8083/bc/register \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "tenant-001",
    "serviceName": "URLLC-Slice",
    "slaHash": "0x1234...abcd",
    "slos": [
      {"name": "latency", "value": 10, "threshold": 10},
      {"name": "throughput", "value": 100, "threshold": 100}
    ]
  }'
```

**Resposta:**
```json
{
  "status": "ok",
  "tx": "0x5678...efgh"
}
```

**Via Python:**
```python
from service import BCService

service = BCService()

receipt = service.register_sla(
    customer="tenant-001",
    service_name="URLLC-Slice",
    sla_hash=bytes32_hash,
    slos=[("latency", 10, 10), ("throughput", 100, 100)]
)

print(f"Transaction Hash: {receipt.transactionHash.hex()}")
print(f"Block Number: {receipt.blockNumber}")
```

### Exemplo 2: Atualizar Status

**Via API REST:**
```bash
curl -X POST http://localhost:8083/bc/update \
  -H "Content-Type: application/json" \
  -d '{
    "slaId": 1,
    "newStatus": 3
  }'
```

**Via Python:**
```python
receipt = service.update_status(sla_id=1, status=3)  # ACTIVE
print(f"Status atualizado: {receipt.transactionHash.hex()}")
```

### Exemplo 3: Consultar SLA

**Via API REST:**
```bash
curl http://localhost:8083/bc/1
```

**Resposta:**
```json
{
  "customer": "tenant-001",
  "serviceName": "URLLC-Slice",
  "status": 3,
  "createdAt": 1706356800,
  "updatedAt": 1706356800
}
```

**Via Python:**
```python
sla_data = service.get_sla(sla_id=1)
customer, service_name, status, created_at, updated_at = sla_data
print(f"Customer: {customer}, Status: {status}")
```

### Exemplo 4: consume decisions from Decision Engine

**Código:**
```python
from kafka_consumer import DecisionConsumer
from smart_contracts import SmartContractExecutor
from oracle import MetricsOracle

executor = SmartContractExecutor()
oracle = MetricsOracle()
consumer = DecisionConsumer(executor, oracle)

# consume continuamente
while True:
    result = await consumer.consume_and_execute()
    print(f"Contrato executado: {result}")
```

### Exemplo 5: Consultar On-Chain Events

**Código:**
```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
contract_address = "0x42699A7612A82f1d9C36148af9C77354759b210b"

# Carregar ABI
with open("apps/bc-nssmf/src/contracts/contract_address.json") as f:
    contract_data = json.load(f)
    abi = contract_data["abi"]

contract = w3.eth.contract(address=contract_address, abi=abi)

# Consultar eventos
event_filter = contract.events.SLARequested.create_filter(fromBlock=0)
events = event_filter.get_all_entries()

for event in events:
    print(f"SLA ID: {event.args.slaId}")
    print(f"Customer: {event.args.customer}")
    print(f"Service: {event.args.serviceName}")
```

---

## 🔧 Troubleshooting

### Problema 1: Não conecta ao Besu RPC

**Sintoma:** `RuntimeError: Erro: RPC Besu não conectado`

**solution:**
```bash
# Verificar se Besu está rodando
docker ps | grep besu

# Verificar RPC
curl http://127.0.0.1:8545

# Se não estiver rodando, start
cd apps/bc-nssmf/blockchain/besu
docker-compose -f docker-compose-besu.yaml up -d
```

### Problema 2: Saldo insuficiente

**Sintoma:** `RuntimeError: Saldo insuficiente`

**solution:**
```bash
# Em modo DEV, usar conta padrão of Besu
# Chave privada: 0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63
# address: 0xfe3b557e8fb62b89f4916b721be55ceb828dbd73

# Verificar saldo
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
balance = w3.eth.get_balance("0xfe3b557e8fb62b89f4916b721be55ceb828dbd73")
print(f"Saldo: {w3.from_wei(balance, 'ether')} ETH")
```

### Problema 3: Contrato não encontrado

**Sintoma:** `ValueError: Contrato não encontrado`

**solution:**
```bash
# Verificar se contrato foi deployado
cat apps/bc-nssmf/src/contracts/contract_address.json

# Se não existir, fazer deploy
cd apps/bc-nssmf
python src/deploy_contracts.py
```

### Problema 4: Erro ao compilar contrato

**Sintoma:** `solcx.exceptions.SolcError`

**solution:**
```bash
# Instalar solc
pip install py-solc-x

# Instalar versão específica of Solidity
python -c "from solcx import install_solc; install_solc('0.8.20')"
```

### Problema 5: Kafka não conecta

**Sintoma:** `kafka.errors.KafkaError`

**solution:**
```bash
# Verificar se Kafka está rodando
docker ps | grep kafka

# Verificar conectividade
telnet kafka 9092

# Se não estiver rodando, start
docker-compose -f docker-compose-kafka.yaml up -d
```

---

## 📊 Observabilidade

### metrics Prometheus

| Métrica | Tipo | Description |
|---------|------|-----------|
| `bc_nssmf_transactions_total` | Counter | Total de transações enviadas |
| `bc_nssmf_transaction_duration_seconds` | Histogram | Tempo de confirmação |
| `bc_nssmf_contract_calls_total` | Counter | Total de chamadas ao contrato |
| `bc_nssmf_events_total` | Counter | Total de eventos on-chain |
| `bc_nssmf_gas_used` | Histogram | Gas usado por transação |

### Traces OTLP

**Spans:**
- `register_sla` — Registro de SLA
- `update_status` — Atualização de status
- `get_sla` — Queries de SLA
- `consume_i04` — Consumo de decisions
- `execute_contract` — Execução de contrato

---

## 📚 Referências

- **Hyperledger Besu:** https://besu.hyperledger.org/
- **web3.py:** https://web3py.readthedocs.io/
- **Solidity:** https://docs.soliditylang.org/
- **Ethereum:** https://ethereum.org/
- **Kafka Python:** https://kafka-python.readthedocs.io/

---

## 🎯 Conclusão

O BC-NSSMF fornece registro on-chain de SLAs com imutabilidade e audit completa. O módulo:

- ✅ **Registers SLAs** on-chain após aprovação from Decision Engine
- ✅ **Updates status** de SLAs (ACTIVE, VIOLATED, TERMINATED)
- ✅ **Registers violações** in an immutable way
- ✅ **Fornece audit** via on-chain events
- ✅ **Integra-se** com Decision Engine e SLO Reporter
- ✅ **Observável** via Prometheus e OpenTelemetry

Para mais informações, consulte:
- `apps/bc-nssmf/src/service.py` — service main
- `apps/bc-nssmf/src/contracts/SLAContract.sol` — Smart Contract
- `apps/bc-nssmf/src/deploy_contracts.py` — Script de deploy

---

**end of Guia**

