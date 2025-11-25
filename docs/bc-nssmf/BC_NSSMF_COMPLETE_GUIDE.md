# Guia Completo do Módulo BC-NSSMF

**Versão:** 3.5.0  
**Data:** 2025-01-27  
**Módulo:** Blockchain-enabled Network Slice Subnet Management Function

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Módulo](#arquitetura-do-módulo)
3. [Smart Contracts](#smart-contracts)
4. [Integração Web3](#integração-web3)
5. [API REST e gRPC](#api-rest-e-grpc)
6. [Oracle de Métricas](#oracle-de-métricas)
7. [Integração com Outros Módulos](#integração-com-outros-módulos)
8. [Interface I-04 (Kafka)](#interface-i-04-kafka)
9. [Deploy e Configuração](#deploy-e-configuração)
10. [Exemplos de Uso](#exemplos-de-uso)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **BC-NSSMF (Blockchain-enabled Network Slice Subnet Management Function)** é responsável por registrar SLAs on-chain em uma blockchain permissionada, garantindo imutabilidade, rastreabilidade e execução determinística de regras contratuais.

### Objetivos

1. **Registro On-Chain:** Registrar SLAs aprovados pelo Decision Engine na blockchain
2. **Atualização de Status:** Atualizar status de SLAs (ACTIVE, VIOLATED, TERMINATED)
3. **Registro de Violações:** Registrar violações de SLA de forma imutável
4. **Auditoria:** Fornecer auditoria completa via eventos on-chain
5. **Enforcement:** Executar regras contratuais automaticamente

### Características Principais

- **Blockchain:** Hyperledger Besu (Ethereum permissionado)
- **Smart Contracts:** Solidity 0.8.20
- **Cliente Web3:** web3.py
- **Tempo de Confirmação:** < 5 segundos (blockchain local)
- **Imutabilidade:** Todos os eventos registrados on-chain

---

## 🏗️ Arquitetura do Módulo

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
│       ├── docker-compose-besu.yaml  # Docker Compose Besu
│       ├── genesis.json              # Genesis block
│       └── data/                      # Dados da blockchain
├── tests/
│   └── unit/                   # Testes unitários
├── Dockerfile
├── requirements.txt
└── README.md
```

### Componentes Principais

1. **BCService** — Serviço principal de integração Web3
2. **SmartContractExecutor** — Executor de smart contracts
3. **MetricsOracle** — Oracle que obtém métricas do NASP
4. **DecisionConsumer** — Consumer Kafka para decisões (I-04)
5. **SLAContract** — Smart Contract Solidity

### Fluxo de Dados

```
┌─────────────────┐
│ Decision Engine │  (via Kafka I-04)
│  (decisão AC)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Kafka Consumer  │  (consome decisão)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BCService       │  (registra SLA on-chain)
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
│ Eventos On-Chain│  (SLARequested, SLAUpdated)
└─────────────────┘
```

---

## 📜 Smart Contracts

### SLAContract.sol

**Localização:** `apps/bc-nssmf/src/contracts/SLAContract.sol`

**Versão Solidity:** 0.8.20

#### Estruturas

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

#### Funções Principais

1. **`registerSLA()`**
   - Registra um novo SLA on-chain
   - Parâmetros: `customer`, `serviceName`, `slaHash`, `slos[]`
   - Retorna: `slaId` (uint256)
   - Evento: `SLARequested`

2. **`updateSLAStatus()`**
   - Atualiza status de um SLA
   - Parâmetros: `slaId`, `newStatus`
   - Evento: `SLAUpdated`

3. **`getSLA()`**
   - Consulta dados de um SLA
   - Parâmetros: `slaId`
   - Retorna: `customer`, `serviceName`, `status`, `createdAt`, `updatedAt`

#### Eventos

```solidity
event SLARequested(uint256 indexed slaId, string customer, string serviceName);
event SLAUpdated(uint256 indexed slaId, SLAStatus status);
event SLACompleted(uint256 indexed slaId);
```

### Deploy do Contrato

**Script:** `apps/bc-nssmf/src/deploy_contracts.py`

**Comando:**
```bash
cd apps/bc-nssmf
python src/deploy_contracts.py
```

**Processo:**
1. Compila contrato Solidity
2. Conecta ao Besu RPC
3. Verifica saldo da conta
4. Envia transação de deploy
5. Aguarda confirmação
6. Salva endereço e ABI em `contract_address.json`

**Variáveis de Ambiente:**
- `TRISLA_RPC_URL` — URL do RPC Besu (padrão: `http://127.0.0.1:8545`)
- `TRISLA_PRIVATE_KEY` — Chave privada (produção)
- `TRISLA_DEV_PRIVATE_KEY` — Chave privada (desenvolvimento)
- `TRISLA_CHAIN_ID` — Chain ID (padrão: `1337`)

---

## 🔗 Integração Web3

### BCService

**Arquivo:** `apps/bc-nssmf/src/service.py`

**Classe:** `BCService`

#### Inicialização

```python
from service import BCService

service = BCService()
```

**Processo:**
1. Conecta ao RPC Besu via `Web3.HTTPProvider`
2. Carrega ABI e endereço do contrato
3. Cria instância do contrato
4. Seleciona conta padrão

#### Métodos Principais

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
   # Retorna: (customer, serviceName, status, createdAt, updatedAt)
   ```

### Configuração

**Arquivo:** `apps/bc-nssmf/src/config.py`

```python
class BCConfig:
    rpc_url: str = "http://127.0.0.1:8545"
    contract_info_path: str = "apps/bc-nssmf/src/contracts/contract_address.json"
```

---

## 🌐 API REST e gRPC

### API REST

**Arquivo:** `apps/bc-nssmf/src/api_rest.py`

**Endpoints:**

1. **`POST /bc/register`**
   - Registra SLA on-chain
   - Body: `SLARequest`
   - Retorna: `{"status": "ok", "tx": "0x..."}`

2. **`POST /bc/update`**
   - Atualiza status de SLA
   - Body: `SLAStatusUpdate`
   - Retorna: `{"status": "ok", "tx": "0x..."}`

3. **`GET /bc/{sla_id}`**
   - Consulta SLA
   - Retorna: Dados do SLA

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

**Arquivo:** `apps/bc-nssmf/src/api_grpc_server.py`

**Status:** Placeholder funcional (estrutura mínima)

**Nota:** A implementação completa de gRPC está nas interfaces I-01 a I-07.

---

## 🔮 Oracle de Métricas

### MetricsOracle

**Arquivo:** `apps/bc-nssmf/src/oracle.py`

**Classe:** `MetricsOracle`

**Função:** Obtém métricas reais do NASP para validação de smart contracts.

#### Método Principal

```python
metrics = await metrics_oracle.get_metrics()
```

**Retorno:**
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

**Em Produção:**
- Conecta ao NASP Adapter via HTTP REST
- Obtém métricas em tempo real
- Valida contra thresholds do SLA

---

## 🔌 Integração com Outros Módulos

### 1. Decision Engine (Interface I-04)

**Tipo:** Kafka Consumer  
**Tópico:** `trisla-i04-decisions`  
**Payload:** Decisão de aceitação/rejeição

**Código:**
```python
from kafka_consumer import DecisionConsumer

consumer = DecisionConsumer(contract_executor, metrics_oracle)

# Consumir decisões
result = await consumer.consume_and_execute()
```

**Fluxo:**
1. Decision Engine envia decisão `ACCEPT` via Kafka
2. BC-NSSMF consome mensagem
3. BC-NSSMF registra SLA on-chain
4. BC-NSSMF retorna `tx_hash` e `block_number`

### 2. SLO Reporter

**Tipo:** HTTP REST  
**Endpoint:** `POST /bc/update`  
**Payload:** Violação de SLA

**Fluxo:**
1. SLO Reporter detecta violação
2. SLO Reporter chama BC-NSSMF
3. BC-NSSMF atualiza status para `VIOLATED`
4. BC-NSSMF emite evento `SLAUpdated`

### 3. NASP Adapter

**Tipo:** HTTP REST  
**Endpoint:** `http://nasp-adapter:8080/api/v1/metrics`  
**Função:** Fornecer métricas ao Oracle

---

## 📡 Interface I-04 (Kafka)

### Tópico Kafka

**Nome:** `trisla-i04-decisions`

### Schema da Mensagem

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

**Arquivo:** `apps/bc-nssmf/src/kafka_consumer.py`

**Classe:** `DecisionConsumer`

**Configuração:**
```python
consumer = KafkaConsumer(
    'trisla-i04-decisions',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='bc-nssmf-consumer'
)
```

---

## 🚀 Deploy e Configuração

### 1. Iniciar Blockchain Besu

**Docker Compose:** `apps/bc-nssmf/blockchain/besu/docker-compose-besu.yaml`

**Comando:**
```bash
cd apps/bc-nssmf/blockchain/besu
docker-compose -f docker-compose-besu.yaml up -d
```

**Verificar:**
```bash
curl http://127.0.0.1:8545
```

### 2. Deploy do Smart Contract

**Comando:**
```bash
cd apps/bc-nssmf
python src/deploy_contracts.py
```

**Saída Esperada:**
```
[TriSLA] Compilando contrato Solidity...
[TriSLA] Usando conta: 0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1
[TriSLA] Saldo da conta: 100.0 ETH
[TriSLA] Enviando transação de deploy: 0x...
[TriSLA] Contrato implantado em: 0x42699A7612A82f1d9C36148af9C77354759b210b
[TriSLA] Endereço e ABI salvos em contract_address.json
```

### 3. Configurar Variáveis de Ambiente

**Arquivo:** `.env` ou variáveis de ambiente

```bash
# Blockchain
TRISLA_RPC_URL=http://127.0.0.1:8545
TRISLA_CHAIN_ID=1337
TRISLA_PRIVATE_KEY=0x...  # Produção
TRISLA_DEV_PRIVATE_KEY=0x...  # Desenvolvimento

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### 4. Iniciar Aplicação

**Comando:**
```bash
cd apps/bc-nssmf
uvicorn src.main:app --host 0.0.0.0 --port 8083
```

**Verificar:**
```bash
curl http://localhost:8083/health
```

---

## 💡 Exemplos de Uso

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

### Exemplo 4: Consumir Decisões do Decision Engine

**Código:**
```python
from kafka_consumer import DecisionConsumer
from smart_contracts import SmartContractExecutor
from oracle import MetricsOracle

executor = SmartContractExecutor()
oracle = MetricsOracle()
consumer = DecisionConsumer(executor, oracle)

# Consumir continuamente
while True:
    result = await consumer.consume_and_execute()
    print(f"Contrato executado: {result}")
```

### Exemplo 5: Consultar Eventos On-Chain

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

**Solução:**
```bash
# Verificar se Besu está rodando
docker ps | grep besu

# Verificar RPC
curl http://127.0.0.1:8545

# Se não estiver rodando, iniciar
cd apps/bc-nssmf/blockchain/besu
docker-compose -f docker-compose-besu.yaml up -d
```

### Problema 2: Saldo insuficiente

**Sintoma:** `RuntimeError: Saldo insuficiente`

**Solução:**
```bash
# Em modo DEV, usar conta padrão do Besu
# Chave privada: 0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63
# Endereço: 0xfe3b557e8fb62b89f4916b721be55ceb828dbd73

# Verificar saldo
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
balance = w3.eth.get_balance("0xfe3b557e8fb62b89f4916b721be55ceb828dbd73")
print(f"Saldo: {w3.from_wei(balance, 'ether')} ETH")
```

### Problema 3: Contrato não encontrado

**Sintoma:** `ValueError: Contrato não encontrado`

**Solução:**
```bash
# Verificar se contrato foi deployado
cat apps/bc-nssmf/src/contracts/contract_address.json

# Se não existir, fazer deploy
cd apps/bc-nssmf
python src/deploy_contracts.py
```

### Problema 4: Erro ao compilar contrato

**Sintoma:** `solcx.exceptions.SolcError`

**Solução:**
```bash
# Instalar solc
pip install py-solc-x

# Instalar versão específica do Solidity
python -c "from solcx import install_solc; install_solc('0.8.20')"
```

### Problema 5: Kafka não conecta

**Sintoma:** `kafka.errors.KafkaError`

**Solução:**
```bash
# Verificar se Kafka está rodando
docker ps | grep kafka

# Verificar conectividade
telnet kafka 9092

# Se não estiver rodando, iniciar
docker-compose -f docker-compose-kafka.yaml up -d
```

---

## 📊 Observabilidade

### Métricas Prometheus

| Métrica | Tipo | Descrição |
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
- `get_sla` — Consulta de SLA
- `consume_i04` — Consumo de decisões
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

O BC-NSSMF fornece registro on-chain de SLAs com imutabilidade e auditoria completa. O módulo:

- ✅ **Registra SLAs** on-chain após aprovação do Decision Engine
- ✅ **Atualiza status** de SLAs (ACTIVE, VIOLATED, TERMINATED)
- ✅ **Registra violações** de forma imutável
- ✅ **Fornece auditoria** via eventos on-chain
- ✅ **Integra-se** com Decision Engine e SLO Reporter
- ✅ **Observável** via Prometheus e OpenTelemetry

Para mais informações, consulte:
- `apps/bc-nssmf/src/service.py` — Serviço principal
- `apps/bc-nssmf/src/contracts/SLAContract.sol` — Smart Contract
- `apps/bc-nssmf/src/deploy_contracts.py` — Script de deploy

---

**Fim do Guia**

