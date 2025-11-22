# README - Módulo Blockchain (BC-NSSMF)

**TriSLA – Blockchain-enabled Network Slice Subnet Management Function**

---

## 🎯 Função do Módulo

O **BC-NSSMF** é responsável por:

1. **Receber decisões** do Decision Engine via interface I-04
2. **Registrar SLAs** on-chain em blockchain permissionada
3. **Atualizar status** de SLAs (ACTIVE, VIOLATED, TERMINATED)
4. **Registrar violações** recebidas do SLO Reporter
5. **Fornecer auditoria imutável** de todos os eventos

---

## 📥 Entradas

### 1. Decisão do Decision Engine (I-04)

```json
{
  "decision": "ACCEPT",
  "nest_id": "nest-urllc-001",
  "sla_data": {
    "tenant_id": "tenant-001",
    "slice_type": "URLLC",
    "requirements": {...}
  }
}
```

### 2. Violação do SLO Reporter

```json
{
  "sla_id": "sla-001",
  "violation_type": "LATENCY",
  "violation_value": 15.5,
  "threshold": 10.0,
  "timestamp": "2025-01-19T10:30:00Z"
}
```

---

## 📤 Saídas

### 1. Transação Blockchain

```json
{
  "tx_hash": "0x1234...abcd",
  "block_number": 12345,
  "status": "confirmed",
  "gas_used": 50000,
  "timestamp": "2025-01-19T10:30:00Z"
}
```

### 2. Eventos On-Chain

- `SLACreated` - SLA registrado
- `SLAStatusChanged` - Status atualizado
- `SLAViolated` - Violação registrada
- `SLATerminated` - SLA encerrado

---

## 🔗 Integrações

### Interface I-04 (REST/gRPC)

**Endpoint:** `POST /bc-nssmf/sla/register`

**Fluxo:**
1. Decision Engine envia decisão AC
2. BC-NSSMF registra SLA on-chain
3. BC-NSSMF retorna tx_hash e block_number

### Integração com SLO Reporter

**Fluxo:**
1. SLO Reporter detecta violação
2. SLO Reporter chama BC-NSSMF
3. BC-NSSMF registra violação on-chain

---

## 🎯 Responsabilidades

1. **Registro on-chain** de SLAs aprovados
2. **Atualização de status** de SLAs
3. **Registro de violações** imutável
4. **Auditoria completa** de eventos
5. **Execução de smart contracts** (Solidity)
6. **Observabilidade** (métricas, traces, logs)

---

## 🔄 Relação com Decision Engine

O BC-NSSMF é **executor de ações** do Decision Engine:

- **Recebe:** Decisão AC via I-04
- **Executa:** Registro on-chain
- **Retorna:** tx_hash e block_number
- **Relação:** Bidirecional (Decision Engine ↔ BC-NSSMF)

---

## 📋 Requisitos Técnicos

### Tecnologias

- **Python 3.12+**
- **FastAPI** - Framework web
- **Web3.py** - Cliente blockchain
- **Solidity** - Smart contracts
- **Hyperledger Besu / GoQuorum** - Blockchain permissionada
- **Hardhat** - Framework de desenvolvimento
- **OTLP** - Observabilidade

### Dependências

- **Decision Engine** - Recebe decisões via I-04
- **7_SLO** - Recebe violações do SLO Reporter
- **Blockchain Infrastructure** - Hyperledger Besu/GoQuorum

---

## 📚 Referências à Dissertação

- **Capítulo 4** - Arquitetura e Design
- **Capítulo 5** - Implementação e Validação
- **Blockchain** - Registro imutável e auditoria
- **Smart Contracts** - Execução determinística

---

## ✔ Módulo Completo e Documentado

