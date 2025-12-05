# BC-NSSMF — Blockchain-enabled Network Slice Subnet Management Function

**Versão:** 3.7.5  
**Fase:** B (BC-NSSMF)  
**Status:** Estabilizado

---

## 📋 Visão Geral

O **BC-NSSMF** é o módulo blockchain do TriSLA, responsável por:

- **Registrar SLAs** no blockchain após decisões ACCEPT
- **Executar Smart Contracts** Solidity
- **Validar SLAs** usando métricas do NASP
- **Interface I-04** para comunicação com Decision Engine
- **Integração Besu/GoQuorum** para blockchain privada

---

## 🏗️ Arquitetura

### Componentes Principais

1. **BCService** (`src/service.py`)
   - Serviço principal de blockchain
   - Gerencia conexão Web3 e contratos

2. **MetricsOracle** (`src/oracle.py`)
   - Oracle que recebe métricas do NASP
   - Valida SLAs usando métricas reais

3. **DecisionConsumer** (`src/kafka_consumer.py`)
   - Consome decisões do Decision Engine via Kafka (I-04)
   - Executa smart contracts baseado em decisões

4. **SLAContract.sol** (`src/contracts/SLAContract.sol`)
   - Smart Contract Solidity para registro de SLAs
   - Suporta SLOs, eventos e atualização de status

---

## 🔄 Fluxo de Operação

```
1. Decision Engine → Decisão ACCEPT
2. BC-NSSMF → Recebe decisão (Interface I-04)
3. MetricsOracle → Obtém métricas do NASP
4. Smart Contract → Registra SLA no blockchain
5. Blockchain → Retorna transaction hash
```

---

## 🔌 Interface I-04

### REST API

- **POST `/api/v1/register-sla`**
  - Registra SLA no blockchain
  - Body: `SLARequest` (customer, serviceName, slaHash, slos)
  - Retorna: `{status: "ok", tx_hash: "...", block_number: ...}`

- **POST `/api/v1/update-sla-status`**
  - Atualiza status de SLA
  - Body: `SLAStatusUpdate` (slaId, newStatus)
  - Retorna: `{status: "ok", tx_hash: "...", block_number: ...}`

- **GET `/api/v1/get-sla/{sla_id}`**
  - Obtém SLA do blockchain
  - Retorna: `{sla_id, customer, service_name, status, created_at, updated_at}`

- **GET `/health`**
  - Health check do serviço
  - Retorna: `{status: "healthy"|"degraded", enabled: bool}`

### gRPC (Placeholder)

- **Servidor gRPC** (`src/api_grpc_server.py`)
  - Placeholder funcional
  - Estrutura mínima para futura implementação

---

## 📐 Smart Contract

### SLAContract.sol

**Estruturas:**
- `SLA`: id, customer, serviceName, slaHash, status, slos[], createdAt, updatedAt
- `SLO`: name, value, threshold

**Status:**
- `REQUESTED` (0)
- `APPROVED` (1)
- `REJECTED` (2)
- `ACTIVE` (3)
- `COMPLETED` (4)

**Funções:**
- `registerSLA(customer, serviceName, slaHash, slos[])` → uint256 (slaId)
- `updateSLAStatus(slaId, newStatus)`
- `getSLA(slaId)` → (customer, serviceName, status, createdAt, updatedAt)

**Eventos:**
- `SLARequested(slaId, customer, serviceName)`
- `SLAUpdated(slaId, status)`
- `SLACompleted(slaId)`

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Blockchain
BC_ENABLED=true  # false para modo DEV (stub)
TRISLA_RPC_URL=http://trisla-bc-nssmf:8545
TRISLA_CHAIN_ID=1337
TRISLA_PRIVATE_KEY=0x...  # Chave privada para assinar transações

# Kafka (opcional)
KAFKA_ENABLED=true
KAFKA_BROKERS=localhost:9092

# OpenTelemetry
OTLP_ENABLED=true
OTLP_ENDPOINT_GRPC=http://trisla-otel-collector:4317
```

### Modo DEV

Quando `BC_ENABLED=false`:
- BCService funciona em modo stub
- Não conecta ao blockchain
- Retorna None para operações
- Permite desenvolvimento sem Besu

---

## 🔗 Integração Besu/GoQuorum

### Besu

**Configuração:**
- RPC endpoint: `http://localhost:8545` (padrão)
- Chain ID: `1337` (dev) ou configurável
- Conta padrão: pré-financiada em modo dev

**Deploy:**
```bash
cd apps/bc-nssmf/src
python deploy_contracts.py
```

### GoQuorum

Suportado via Web3.py (mesma interface que Besu).

---

## 🧪 Testes

### Testes Unitários

```bash
pytest tests/unit/test_bc_nssmf_service.py -v
```

**Cobertura:**
- Inicialização em modo DEV
- Registro de SLA em modo degraded
- Atualização de status
- Obtenção de SLA

### Testes de Integração

```bash
pytest tests/integration/test_bc_nssmf_integration.py -v
```

**Cobertura:**
- Integração Decision Engine → BC-NSSMF
- Interface I-04 (REST)
- Conversão DecisionResult → Blockchain

### Testes E2E

```bash
pytest tests/integration/test_bc_nssmf_e2e.py -v
```

**Cobertura:**
- Fluxo completo: Decision → Blockchain
- Ciclo de vida do SLA
- Performance E2E

---

## 📊 Performance

### Latência de Transação

- **Registro de SLA:** < 5s (depende do blockchain)
- **Atualização de status:** < 3s
- **Leitura de SLA:** < 1s

### Otimizações

- Modo degraded para desenvolvimento
- Cache de contratos (futuro)
- Batch de transações (futuro)

---

## 📦 Estrutura de Diretórios

```
apps/bc-nssmf/
├── src/
│   ├── main.py              # FastAPI application
│   ├── service.py           # BCService (serviço principal)
│   ├── oracle.py            # MetricsOracle
│   ├── kafka_consumer.py    # DecisionConsumer
│   ├── api_rest.py          # API REST (I-04)
│   ├── api_grpc_server.py   # gRPC Server (I-04 - placeholder)
│   ├── deploy_contracts.py  # Script de deploy
│   ├── models.py            # Modelos Pydantic
│   ├── config.py            # Configurações
│   └── contracts/
│       ├── SLAContract.sol  # Smart Contract
│       └── contract_address.json  # Endereço e ABI
├── blockchain/
│   └── besu/
│       ├── docker-compose-besu.yaml
│       └── genesis.json
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Uso

### Exemplo de Requisição REST

```bash
curl -X POST http://localhost:8083/api/v1/register-sla \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "tenant-001",
    "serviceName": "SLA-URLLC-001",
    "slaHash": "0x...",
    "slos": [
      {"name": "latency", "value": 10, "threshold": 10},
      {"name": "reliability", "value": 999, "threshold": 999}
    ]
  }'
```

### Resposta

```json
{
  "status": "ok",
  "tx_hash": "0x1234...",
  "block_number": 42
}
```

---

## 📝 Changelog

### v3.7.5 (FASE B)

- ✅ Smart Contract unificado e validado
- ✅ Interface I-04 finalizada (REST)
- ✅ Integração Besu/GoQuorum validada
- ✅ Execução real de ações implementada
- ✅ Testes unitários completos
- ✅ Testes de integração completos
- ✅ Testes E2E completos
- ✅ Documentação completa
- ✅ Correções de datetime (timezone-aware)
- ✅ Correções de imports

---

## 🔗 Referências

- **Roadmap:** `TRISLA_PROMPTS_v3.5/roadmap/TRISLA_GUIDE_PHASED_IMPLEMENTATION.md`
- **Tabela NASP:** `TRISLA_PROMPTS_v3.5/roadmap/05_TABELA_CONSOLIDADA_NASP.md`
- **Besu:** https://besu.hyperledger.org/
- **Web3.py:** https://web3py.readthedocs.io/

---

**Status:** ✅ Estabilizado — Pronto para produção






