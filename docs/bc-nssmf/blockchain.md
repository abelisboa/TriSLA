# Blockchain — BC-NSSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `BC_NSSMF_COMPLETE_GUIDE.md` (seções Deploy e Configuração, Integração Web3)

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Hyperledger Besu](#hyperledger-besu)
3. [Configuração](#configuração)
4. [Deploy](#deploy)
5. [Integração Web3](#integração-web3)

---

## Visão Geral

O BC-NSSMF utiliza **Hyperledger Besu** (Ethereum permissionado) como blockchain para registro on-chain de SLAs. A blockchain garante imutabilidade, rastreabilidade e execução determinística de regras contratuais.

### Características

- **Tipo:** Blockchain permissionada (Ethereum-compatível)
- **Consenso:** IBFT 2.0 (Istanbul BFT)
- **Tempo de bloco:** ~2 segundos
- **Tempo de confirmação:** < 5 segundos
- **Imutabilidade:** Todos os eventos registrados on-chain

---

## Hyperledger Besu

### O que é Besu

Hyperledger Besu é um cliente Ethereum de código aberto desenvolvido sob a Apache 2.0. Suporta redes públicas e permissionadas usando consenso Proof of Authority (PoA) ou Proof of Stake (PoS).

### Por que Besu

1. **Ethereum-compatível:** Suporta smart contracts Solidity
2. **Permissionado:** Controle de acesso a nós
3. **Performance:** Tempo de bloco rápido (~2 segundos)
4. **IBFT 2.0:** Consenso tolerante a falhas bizantinas

### Configuração Local

**Docker Compose:** `apps/bc-nssmf/blockchain/besu/docker-compose-besu.yaml`

**Iniciar:**
```bash
cd apps/bc-nssmf/blockchain/besu
docker-compose -f docker-compose-besu.yaml up -d
```

**Verificar:**
```bash
curl http://127.0.0.1:8545
```

---

## Configuração

### Variáveis de Ambiente

```bash
# Blockchain
TRISLA_RPC_URL=http://127.0.0.1:8545
TRISLA_CHAIN_ID=1337
TRISLA_PRIVATE_KEY=0x...  # Produção
TRISLA_DEV_PRIVATE_KEY=0x...  # Desenvolvimento
```

### Genesis Block

**Arquivo:** `apps/bc-nssmf/blockchain/besu/genesis.json`

Define configuração inicial da blockchain:
- Chain ID
- Contas pré-fundadas
- Configuração de consenso (IBFT 2.0)

---

## Deploy

### 1. Iniciar Blockchain Besu

```bash
cd apps/bc-nssmf/blockchain/besu
docker-compose -f docker-compose-besu.yaml up -d
```

### 2. Verificar Conectividade

```bash
curl http://127.0.0.1:8545
```

### 3. Deploy do Smart Contract

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

**Saída Esperada:**
```
[TriSLA] Compilando contrato Solidity...
[TriSLA] Usando conta: 0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1
[TriSLA] Saldo da conta: 100.0 ETH
[TriSLA] Enviando transação de deploy: 0x...
[TriSLA] Contrato implantado em: 0x42699A7612A82f1d9C36148af9C77354759b210b
[TriSLA] Endereço e ABI salvos em contract_address.json
```

---

## Integração Web3

### BCService

**Arquivo:** `apps/bc-nssmf/src/service.py`

**Classe:** `BCService`

**Inicialização:**
```python
from service import BCService

service = BCService()
```

**Processo:**
1. Conecta ao RPC Besu via `Web3.HTTPProvider`
2. Carrega ABI e endereço do contrato
3. Cria instância do contrato
4. Seleciona conta padrão

**Métodos Principais:**
```python
# Registrar SLA
receipt = service.register_sla(
    customer="tenant-001",
    service_name="URLLC-Slice",
    sla_hash=bytes32_hash,
    slos=[("latency", 10, 10), ("throughput", 100, 100)]
)

# Atualizar status
receipt = service.update_status(
    sla_id=1,
    status=2  # ACTIVE
)

# Consultar SLA
sla_data = service.get_sla(sla_id=1)
```

### Configuração

**Arquivo:** `apps/bc-nssmf/src/config.py`

```python
class BCConfig:
    rpc_url: str = "http://127.0.0.1:8545"
    contract_info_path: str = "apps/bc-nssmf/src/contracts/contract_address.json"
```

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `BC_NSSMF_COMPLETE_GUIDE.md` — Seções "Deploy e Configuração", "Integração Web3"

**Última atualização:** 2025-01-27  
**Versão:** S4.0

