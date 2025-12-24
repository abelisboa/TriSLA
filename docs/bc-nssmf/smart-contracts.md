# Smart Contracts — BC-NSSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `BC_NSSMF_COMPLETE_GUIDE.md` (seção Smart Contracts)

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [SLAContract.sol](#slacontractsol)
3. [Estruturas](#estruturas)
4. [Funções](#funções)
5. [Eventos](#eventos)
6. [Deploy](#deploy)

---

## Visão Geral

O BC-NSSMF utiliza smart contracts Solidity para gerenciar SLAs on-chain. O contrato principal é `SLAContract.sol`, que define estruturas, funções e eventos para registro e atualização de SLAs.

### Características

- **Linguagem:** Solidity 0.8.20
- **Blockchain:** Hyperledger Besu (Ethereum permissionado)
- **Imutabilidade:** Todos os eventos registrados on-chain
- **Auditoria:** Eventos indexados para consulta eficiente

---

## SLAContract.sol

**Localização:** `apps/bc-nssmf/src/contracts/SLAContract.sol`

**Versão Solidity:** 0.8.20

### Estrutura Geral

```solidity
pragma solidity ^0.8.20;

contract SLAContract {
    // Estruturas
    // Variáveis de estado
    // Funções
    // Eventos
}
```

---

## Estruturas

### SLAStatus (Enum)

```solidity
enum SLAStatus {
    REQUESTED,
    APPROVED,
    REJECTED,
    ACTIVE,
    COMPLETED
}
```

**Estados:**
- **REQUESTED**: SLA solicitado (aguardando aprovação)
- **APPROVED**: SLA aprovado (pronto para ativação)
- **REJECTED**: SLA rejeitado
- **ACTIVE**: SLA ativo (em execução)
- **COMPLETED**: SLA completado (finalizado)

### SLO (Struct)

```solidity
struct SLO {
    string name;
    uint256 value;
    uint256 threshold;
}
```

**Campos:**
- **name**: Nome do SLO (ex: "latency", "throughput")
- **value**: Valor alvo
- **threshold**: Limite mínimo/máximo

### SLA (Struct)

```solidity
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

**Campos:**
- **id**: Identificador único do SLA
- **customer**: Identificador do tenant
- **serviceName**: Nome do serviço
- **slaHash**: Hash do SLA (bytes32)
- **status**: Status atual do SLA
- **slos**: Lista de SLOs
- **createdAt**: Timestamp de criação
- **updatedAt**: Timestamp de última atualização

---

## Funções

### registerSLA()

Registra um novo SLA on-chain.

**Assinatura:**
```solidity
function registerSLA(
    string memory customer,
    string memory serviceName,
    bytes32 slaHash,
    SLO[] memory slos
) public returns (uint256)
```

**Parâmetros:**
- `customer`: Identificador do tenant
- `serviceName`: Nome do serviço
- `slaHash`: Hash do SLA (bytes32)
- `slos`: Lista de SLOs

**Retorno:**
- `slaId`: Identificador único do SLA (uint256)

**Evento:**
- `SLARequested(uint256 indexed slaId, string customer, string serviceName)`

**Exemplo:**
```python
receipt = service.register_sla(
    customer="tenant-001",
    service_name="URLLC-Slice",
    sla_hash=bytes32_hash,
    slos=[("latency", 10, 10), ("throughput", 100, 100)]
)
```

### updateSLAStatus()

Atualiza status de um SLA.

**Assinatura:**
```solidity
function updateSLAStatus(
    uint256 slaId,
    SLAStatus newStatus
) public returns (bool)
```

**Parâmetros:**
- `slaId`: Identificador do SLA
- `newStatus`: Novo status (REQUESTED, APPROVED, REJECTED, ACTIVE, COMPLETED)

**Retorno:**
- `success`: Indica se atualização foi bem-sucedida (bool)

**Evento:**
- `SLAUpdated(uint256 indexed slaId, SLAStatus status)`

**Exemplo:**
```python
receipt = service.update_status(
    sla_id=1,
    status=2  # ACTIVE
)
```

### getSLA()

Consulta dados de um SLA.

**Assinatura:**
```solidity
function getSLA(uint256 slaId) public view returns (
    string memory customer,
    string memory serviceName,
    SLAStatus status,
    uint256 createdAt,
    uint256 updatedAt
)
```

**Parâmetros:**
- `slaId`: Identificador do SLA

**Retorno:**
- `customer`: Identificador do tenant
- `serviceName`: Nome do serviço
- `status`: Status atual
- `createdAt`: Timestamp de criação
- `updatedAt`: Timestamp de última atualização

**Exemplo:**
```python
sla_data = service.get_sla(sla_id=1)
# Retorna: (customer, serviceName, status, createdAt, updatedAt)
```

---

## Eventos

### SLARequested

Emitido quando um SLA é registrado on-chain.

```solidity
event SLARequested(
    uint256 indexed slaId,
    string customer,
    string serviceName
);
```

**Campos:**
- `slaId`: Identificador do SLA (indexado)
- `customer`: Identificador do tenant
- `serviceName`: Nome do serviço

### SLAUpdated

Emitido quando status de um SLA é atualizado.

```solidity
event SLAUpdated(
    uint256 indexed slaId,
    SLAStatus status
);
```

**Campos:**
- `slaId`: Identificador do SLA (indexado)
- `status`: Novo status

### SLACompleted

Emitido quando um SLA é completado.

```solidity
event SLACompleted(
    uint256 indexed slaId
);
```

**Campos:**
- `slaId`: Identificador do SLA (indexado)

---

## Deploy

### Script de Deploy

**Arquivo:** `apps/bc-nssmf/src/deploy_contracts.py`

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
- `TRISLA_RPC_URL`: URL do RPC Besu (padrão: `http://127.0.0.1:8545`)
- `TRISLA_PRIVATE_KEY`: Chave privada (produção)
- `TRISLA_DEV_PRIVATE_KEY`: Chave privada (desenvolvimento)
- `TRISLA_CHAIN_ID`: Chain ID (padrão: `1337`)

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `BC_NSSMF_COMPLETE_GUIDE.md` — Seção "Smart Contracts"

**Última atualização:** 2025-01-27  
**Versão:** S4.0

