# BC-NSSMF — Blockchain-enabled Network Slice Subnet Management Function

**Versão:** 3.7.10  
**Fase:** B (BC-NSSMF)  
**Status:** Estabilizado

---

## 1. Visão Geral do Módulo

### Objetivo no TriSLA (Papel Arquitetural)

O **BC-NSSMF** é responsável por registrar SLAs on-chain em uma blockchain permissionada, garantindo imutabilidade, rastreabilidade e execução determinística de regras contratuais. O módulo utiliza Hyperledger Besu (Ethereum permissionado) e smart contracts Solidity para registrar e gerenciar o ciclo de vida de SLAs.

**Papel no fluxo TriSLA:**
- **Entrada**: Decisão de aceitação do Decision Engine (via I-04 Kafka)
- **Processamento**: Registro on-chain de SLA + atualização de status
- **Saída**: Eventos on-chain (SLARequested, SLAUpdated) + API REST para consulta

### Entradas e Saídas (Alto Nível)

**Entradas:**
- Decisão de aceitação do Decision Engine (I-04)
- Dados de SLA (tenant_id, slice_type, requisitos)
- Atualizações de status (ACTIVE, VIOLATED, TERMINATED)

**Saídas:**
- Transações on-chain registradas
- Eventos on-chain (SLARequested, SLAUpdated, SLACompleted)
- API REST para consulta de SLAs

---

## 2. Componentes Internos

### 2.1 BCService
Serviço principal de integração Web3. Conecta ao Besu RPC, carrega smart contract e executa transações on-chain.

### 2.2 SmartContractExecutor
Executor de smart contracts. Gerencia transações, aguarda confirmações e processa eventos on-chain.

### 2.3 MetricsOracle
Oracle que obtém métricas do NASP Adapter. Usado para validação de violações de SLA.

### 2.4 DecisionConsumer
Consumer Kafka que recebe decisões do Decision Engine via interface I-04. Processa mensagens assíncronas e dispara registro on-chain.

### 2.5 SLAContract
Smart Contract Solidity que gerencia SLAs on-chain. Define estruturas, funções e eventos para registro e atualização de SLAs.

---

## 3. Fluxo Operacional

### Passo a Passo

1. **Recepção de Decisão**
   - Consumer Kafka recebe decisão do Decision Engine (I-04)
   - Tópico: `trisla-i04-decisions`
   - Validação de formato

2. **Preparação de Dados**
   - Extrai dados de SLA da decisão
   - Calcula hash do SLA
   - Prepara SLOs (Service Level Objectives)

3. **Registro On-Chain**
   - Chama função `registerSLA()` do smart contract
   - Envia transação para blockchain
   - Aguarda confirmação (< 5 segundos)

4. **Emissão de Evento**
   - Smart contract emite evento `SLARequested`
   - Evento indexado por `slaId`
   - Logs on-chain imutáveis

5. **Atualização de Status**
   - Quando SLA é ativado: `updateSLAStatus(ACTIVE)`
   - Quando SLA é violado: `updateSLAStatus(VIOLATED)`
   - Quando SLA é terminado: `updateSLAStatus(TERMINATED)`

6. **Emissão de Eventos**
   - Smart contract emite evento `SLAUpdated`
   - Evento indexado por `slaId` e `status`
   - Logs on-chain imutáveis

---

## 4. Interfaces

### 4.1 Interface I-04 (Kafka) — Entrada

**Protocolo:** Kafka  
**Direção:** Decision Engine → BC-NSSMF  
**Tópico:** `trisla-i04-decisions`  
**Partições:** 3  
**Replicação:** 1

**Descrição Conceitual:**
Recebe decisões de aceitação do Decision Engine. A decisão contém dados do SLA aprovado que será registrado on-chain.

**Payload (conceitual):**
- `decision`: Decisão (ACCEPT/REJECT)
- `nest_id`: Identificador do NEST
- `sla_data`: Dados do SLA (tenant_id, slice_type, requisitos)
- `timestamp`: Timestamp da decisão

### 4.2 API REST — Consulta

**Protocolo:** HTTP REST  
**Direção:** Cliente → BC-NSSMF  
**Base URL:** `http://bc-nssmf:8083`

**Endpoints:**
- `POST /bc/register`: Registra SLA on-chain
- `POST /bc/update`: Atualiza status de SLA
- `GET /bc/{sla_id}`: Consulta SLA por ID
- `GET /bc/events/{sla_id}`: Consulta eventos de um SLA

**Descrição Conceitual:**
API REST para registro, atualização e consulta de SLAs. Permite integração com sistemas externos e SLO Reporter.

---

## 5. Dados e Modelos

### 5.1 Smart Contract (SLAContract.sol)

**Localização:** `apps/bc-nssmf/src/contracts/SLAContract.sol`

**Estruturas:**
- **SLAStatus**: Enum (REQUESTED, APPROVED, REJECTED, ACTIVE, COMPLETED)
- **SLO**: Struct (name, value, threshold)
- **SLA**: Struct (id, customer, serviceName, slaHash, status, slos[], createdAt, updatedAt)

**Funções Principais:**
- `registerSLA()`: Registra novo SLA on-chain
- `updateSLAStatus()`: Atualiza status de SLA
- `getSLA()`: Consulta dados de SLA

**Eventos:**
- `SLARequested`: Emitido quando SLA é registrado
- `SLAUpdated`: Emitido quando status é atualizado
- `SLACompleted`: Emitido quando SLA é completado

**Documentação Completa:** [`smart-contracts.md`](smart-contracts.md)

### 5.2 Blockchain (Hyperledger Besu)

**Tipo:** Ethereum permissionado

**Características:**
- **Consenso:** IBFT 2.0 (Istanbul BFT)
- **Tempo de bloco:** ~2 segundos
- **Tempo de confirmação:** < 5 segundos
- **Imutabilidade:** Todos os eventos registrados on-chain

**Documentação Completa:** [`blockchain.md`](blockchain.md)

### 5.3 Modelos de Dados

**SLARequest (Pydantic):**
- `customer`: Identificador do tenant
- `serviceName`: Nome do serviço
- `slaHash`: Hash do SLA (bytes32)
- `slos`: Lista de SLOs

**SLAStatusUpdate (Pydantic):**
- `sla_id`: Identificador do SLA
- `status`: Novo status (REQUESTED, APPROVED, REJECTED, ACTIVE, COMPLETED)

---

## 6. Observabilidade e Métricas

### 6.1 Métricas Expostas

O módulo expõe métricas via endpoint `/metrics` (Prometheus):

- `trisla_slas_registered_total`: Total de SLAs registrados on-chain
- `trisla_sla_status_updates_total`: Total de atualizações de status
- `trisla_blockchain_transactions_total`: Total de transações on-chain
- `trisla_blockchain_transaction_duration_seconds`: Duração de transação
- `trisla_blockchain_events_total`: Total de eventos on-chain

### 6.2 Traces OpenTelemetry

Traces distribuídos são gerados para rastreabilidade:
- Span: `bc_nssmf.receive_decision` (I-04)
- Span: `bc_nssmf.register_sla`
- Span: `bc_nssmf.blockchain_transaction`
- Span: `bc_nssmf.update_status`

### 6.3 Logs Estruturados

Logs estruturados incluem:
- `sla_id`: Identificador do SLA
- `transaction_hash`: Hash da transação on-chain
- `block_number`: Número do bloco
- `status`: Status do SLA
- `processing_time`: Tempo de processamento

---

## 7. Limitações Conhecidas

### 7.1 Tempo de Confirmação

- **Limitação**: Tempo de confirmação depende do consenso da blockchain
- **Impacto**: Latência de registro pode variar (2-5 segundos)
- **Mitigação**: Usar blockchain local/permissionada com consenso rápido

### 7.2 Custo de Transação

- **Limitação**: Cada transação consome gas (custo computacional)
- **Impacto**: Alto volume de transações pode ser custoso
- **Mitigação**: Otimizar smart contracts, usar batch transactions

### 7.3 Escalabilidade

- **Limitação**: Blockchain pode ter limitações de throughput
- **Impacto**: Alto volume de SLAs pode causar congestionamento
- **Mitigação**: Usar sidechains, otimizar consenso, batch processing

### 7.4 Privacidade

- **Limitação**: Dados on-chain são públicos (mesmo em blockchain permissionada)
- **Impacto**: Informações sensíveis podem ser expostas
- **Mitigação**: Usar hashes em vez de dados completos, criptografia

---

## 8. Como Ler a Documentação deste Módulo

### 8.1 Ordem Recomendada de Leitura

1. **Este README.md** — Visão geral e guia de leitura
2. **[blockchain.md](blockchain.md)** — Blockchain e configuração Besu
3. **[smart-contracts.md](smart-contracts.md)** — Smart contracts Solidity
4. **[implementation.md](implementation.md)** — Detalhes de implementação

### 8.2 Documentação Adicional

- **[BC_NSSMF_COMPLETE_GUIDE.md](BC_NSSMF_COMPLETE_GUIDE.md)** — Guia completo (referência)
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** — Arquitetura geral do TriSLA

### 8.3 Links para Outros Módulos

- **[Decision Engine](../../apps/decision-engine/README.md)** — Motor de decisão (envia decisão via I-04)
- **[SEM-NSMF](../sem-csmf/README.md)** — Módulo de interpretação semântica
- **[ML-NSMF](../ml-nsmf/README.md)** — Módulo de predição ML

---

**Última atualização:** 2025-01-27  
**Versão:** S4.0
