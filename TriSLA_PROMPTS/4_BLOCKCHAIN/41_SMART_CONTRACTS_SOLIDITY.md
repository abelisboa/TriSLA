# 41 – Smart Contracts, Hardhat e Deploy Ethereum Permissionado  
**BC-NSSMF – Infraestrutura Blockchain Completa para o TriSLA**

---

## 🎯 Objetivo
Implementar toda a infraestrutura blockchain usada pelo BC-NSSMF, incluindo:

- Smart Contracts Solidity  
- Projeto Hardhat  
- Scripts de deploy  
- Geração automática de ABI  
- Testes on-chain  
- Integração com Hyperledger Besu / GoQuorum  

---

# 1. Estrutura Completa do Projeto Hardhat

Criar:

```
blockchain/bc_nssmf/hardhat/
  contracts/
    SLAContract.sol
  scripts/
    deploy.js
    seed_demo.js
  test/
    SLAContract.test.js
  hardhat.config.js
  package.json
  README.md
```

---

# 2. Smart Contract: `SLAContract.sol`

Implementar o contrato completo:

- enum `SLAStatus { ACTIVE, VIOLATED, TERMINATED }`
- estrutura `SLA { ... }`
- mapping interno
- id autoincremental
- funções:
  - `createSLA(...)`
  - `setStatus(id, status, reason)`
  - `getSLA(id)`
- eventos:
  - `SLACreated`
  - `SLAStatusChanged`

---

# 3. hardhat.config.js

Configurar:

- Solidity ^0.8.20
- Rede local
- Rede Besu:

```
networks: {
  besu: {
    url: process.env.BESU_RPC_URL,
    chainId: parseInt(process.env.BESU_CHAIN_ID),
    accounts: [process.env.BC_NSSMF_DEPLOYER_PK]
  }
}
```

---

# 4. Scripts de Deploy

`deploy.js` deve:

- compilar  
- deployar `SLAContract`  
- imprimir endereço  
- salvar arquivo:

```
apps/bc_nssmf/abi/SLAContract.json
apps/bc_nssmf/address.json
```

---

# 5. Testes Hardhat

Criar `SLAContract.test.js` validando:

- criação de SLA  
- leitura  
- alteração de status  
- emissão de eventos  

---

# 6. README.md explicando:

- Como rodar Hardhat local  
- Como conectar ao Besu  
- Como deployar  
- Como gerar ABI  
- Como consumir no BC-NSSMF  

---

# 7. Resultado esperado

Após executar este prompt, o TriSLA terá:

- **Smart Contract real**, compilado e deployado  
- **Projeto Hardhat completo**  
- **Estrutura ABI integrada ao backend**  
- **Capacidade de auditoria on-chain real**  
- **Compatibilidade com Besu/GoQuorum**  

---

# ✔ PRONTO PARA IMPLEMENTAÇÃO NO CURSOR
