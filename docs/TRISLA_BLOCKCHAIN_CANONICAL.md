# TriSLA Blockchain — Documentação Canônica

**Versão:** v3.10.2  
**Data:** 2026-01-31  
**Consenso:** QBFT (single validator, ambiente experimental)  
**Referência:** PROMPT_S48.2, S55, S56.2, S48.1A, S57

---

## 1. Estado atual correto (QBFT + SSOT)

- **Besu:** Hyperledger Besu 23.x, QBFT single-node.
- **Genesis:** ConfigMap `trisla-besu-genesis` (chave `genesis.json`), montado em `/data` no pod Besu.
- **Validador SSOT:** Secret `trisla-besu-validator-key` (namespace `trisla`), chave `key` (hex da chave privada). Endereço do validador: **0x3d86b9df7ef6a2dbce2e617acf6df08de822a86b**.
- **initContainer:** O deployment Besu possui initContainer `copy-validator-key` que copia `/secrets/key` para `/opt/besu/data/key` antes do Besu iniciar. O Besu não gera chave dinamicamente; usa a chave SSOT.
- **BC-NSSMF:** Wallet BC (0x24f31b232A89bC9cdBc9CA36e6d161ec8f435044) pré-fundada no genesis (`alloc` 1 ETH). Contrato: ConfigMap `trisla-bc-contract-address`, endereço **0xFF5B566746CC44415ac48345d371a2A1A1754662** (SSOT pós-S57; reimplantado na chain atual).

---

## 2. Procedimento único de reset seguro do Besu

Quando for necessário trocar genesis ou redeploy do Besu:

1. `kubectl scale deploy/trisla-besu -n trisla --replicas=0`
2. `kubectl rollout status deploy/trisla-besu -n trisla --timeout=120s` (opcional)
3. `kubectl delete pvc trisla-besu-data -n trisla --wait=true`
4. `helm upgrade --install trisla helm/trisla -n trisla --reset-values` (a partir do repo em node006)
5. `kubectl scale deploy/trisla-besu -n trisla --replicas=1`
6. `kubectl rollout status deploy/trisla-besu -n trisla --timeout=180s`
7. Validar: `eth_blockNumber` aumenta (3 amostras); `POST /api/v1/register-sla` (BC-NSSMF) retorna HTTP 200 com `tx_hash` e `block_number`.

**Regra:** Não alterar o Secret `trisla-besu-validator-key` nem o extraData do genesis sem regenerar o genesis com o endereço do validador correspondente à chave no Secret.

---

## 3. Diagnóstico de falhas comuns

| Sintoma | Causa provável | Ação |
|--------|-----------------|------|
| eth_blockNumber = 0x0 e não aumenta | Validador no genesis (extraData) não coincide com a chave do nó | Verificar que o Secret e o extraData referem-se ao mesmo validador (S56.2). |
| BC-NSSMF "modo degraded" | BCService não conectou ao RPC no startup | Rollout restart do trisla-bc-nssmf (S48.1A). |
| register-sla 422 "Saldo insuficiente" | Wallet BC sem saldo no genesis | Garantir `alloc` para 0x24f31b... com 1 ETH no genesis (S48.1A). |
| register-sla 503 / receipt timeout | Besu não produz blocos | Validar produção de blocos (eth_blockNumber); corrigir validador/genesis (S56.2). |

---

## 4. Proibição explícita de procedimentos antigos

- **Não** usar genesis sem alloc da wallet BC (0x24f31b...).
- **Não** deixar o Besu gerar chave dinamicamente sem Secret SSOT (perde identidade após reset do PVC).
- **Não** usar `besu operator generate-blockchain-config` para gerar chave e genesis em produção sem alinhar extraData ao validador real (S56).
- **Não** executar PROMPT_S48 (Dataset Oficial) sem PASS prévio de S48.1 e S48.1A (e S56.2 quando aplicável).

---

## 5. Referência cruzada

- **S55:** BC-NSSMF nonce/replacement policy (v3.10.2).
- **S56.2:** QBFT Validator Identity SSOT (Secret + initContainer), genesis regenerado, block production PASS.
- **S48.1:** Blockchain Ready Gate Hard (validação Besu + BC-NSSMF + register-sla mínimo).
- **S48.1A:** BCService init fix, funding BC wallet via genesis alloc.
- **S48.2:** Congelamento canônico do blockchain + Dataset Oficial v3.10.2.

---

## 6. Resultado da execução S48.2 (evidência)

- **Host:** node006 (hostname node1).
- **Evidências:** `/home/porvir5g/evidencias_resultados_v3.10.2/00_gate/`.
- **FASE 0–3:** PASS (gate, Besu blockNumber crescente, Secret SSOT, genesis QBFT com alloc).
- **FASE 4:** ABORT — health/ready retornou `ready=false, reason=rpc_unreachable`; register-sla retornou HTTP 500. Part II (Dataset) não executada até correção do BC-NSSMF/health e register-sla.
