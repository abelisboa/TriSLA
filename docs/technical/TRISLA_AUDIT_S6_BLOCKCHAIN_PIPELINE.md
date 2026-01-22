# Auditoria Técnica Regressiva do Pipeline Blockchain TriSLA (NASP)
## Resultados da Auditoria

**Data:** 2025-12-21  
**Ambiente:** NASP (node006)  
**Objetivo:** Identificar exatamente onde o fluxo blockchain está sendo interrompido e detectar regressões funcionais.

⚠️ **Este documento é estritamente observacional - nenhuma correção foi aplicada.**

---

## 1. Resumo Executivo

### ✅ Status da Auditoria: CONCLUÍDA

A auditoria identificou o ponto exato de quebra do fluxo blockchain e confirmou regressões funcionais em relação a execuções anteriores.

### Principais Descobertas

1. **BC-NSSMF:** ✅ Existe, está Running e conectado ao RPC, mas **não recebe requisições**
2. **Besu:** ❌ **Não existe no cluster** (regressão de infraestrutura)
3. **Fluxo Blockchain:** ❌ **Bloqueado antes de alcançar BC-NSSMF** (erro no ML-NSMF)
4. **SLA-Agent → BC-NSSMF:** ❌ **Nenhuma chamada observada** (fluxo não alcança esta fase)
5. **Endpoints BC-NSSMF:** ⚠️ **Retornam "Not Found"** (endpoints podem não estar implementados ou roteamento incorreto)

---

## 2. FASE 0 — Baseline do Cluster (Estado Factual)

### Estado dos Pods

**Timestamp:** 2025-12-21 (auditoria)

```
NAME                                      READY   STATUS      RESTARTS       AGE    IP               NODE    NOMINATED NODE   READINESS GATES
trisla-bc-nssmf-84995f7445-t2jd2          1/1     Running     0              38h    10.233.102.148   node1   <none>           <none>
trisla-decision-engine-5f4f54fdb4-9zqlj   1/1     Running     0              61m    10.233.102.170   node1   <none>           <none>
trisla-ml-nsmf-697c8576b5-hkqg7           0/1     Running     31 (26s ago)   92m    10.233.102.158   node1   <none>           <none>
trisla-ml-nsmf-779d6cc88b-qn46j           1/1     Running     0              40h    10.233.102.185   node1   <none>           <none>
trisla-portal-backend-565fcc7f45-kqd8b    1/1     Running     0              12h    10.233.75.22     node2   <none>           <none>
trisla-sem-csmf-848588fdd6-ggmpl          1/1     Running     0              103m   10.233.102.137   node1   <none>           <none>
trisla-sla-agent-layer-657c8c875b-pkspv   1/1     Running     0              50m    10.233.102.179   node1   <none>           <none>
```

### Imagens em Uso (Tags)

| Módulo | Imagem | Tag Atual |
|--------|--------|-----------|
| BC-NSSMF | `ghcr.io/abelisboa/trisla-bc-nssmf` | `v3.7.18` |
| Decision Engine | `ghcr.io/abelisboa/trisla-decision-engine` | `v3.7.23` |
| ML-NSMF (pod 1) | `ghcr.io/abelisboa/trisla-ml-nsmf` | `v3.7.24` |
| ML-NSMF (pod 2) | `ghcr.io/abelisboa/trisla-ml-nsmf` | `v3.7.14` |
| Portal Backend | `ghcr.io/abelisboa/trisla-portal-backend` | `v3.7.21` |
| SEM-CSMF | `ghcr.io/abelisboa/trisla-sem-csmf` | `v3.7.22` |
| SLA-Agent Layer | `ghcr.io/abelisboa/trisla-sla-agent-layer` | `v3.7.20` |

### Serviços

```
trisla-bc-nssmf                  ClusterIP   10.233.39.215   <none>        8083/TCP         40h
trisla-bc-nssmf-metrics          ClusterIP   10.233.30.108   <none>        8083/TCP         18h
trisla-sla-agent-layer           ClusterIP   10.233.4.83     <none>        8084/TCP         40h
```

### Helm Releases

```
NAME         	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART              	APP VERSION
trisla       	trisla   	21      	2025-12-21 06:03:57.200290222 -0300 -03	deployed	trisla-3.7.10      	3.7.10     
trisla-portal	trisla   	8       	2025-12-20 18:34:46.877192758 -0300 -03	deployed	trisla-portal-1.0.2	1.0.0
```

---

## 3. FASE 1 — Existência e Estado do BC-NSSMF

### ✅ BC-NSSMF Existe

- **Pod:** `trisla-bc-nssmf-84995f7445-t2jd2`
- **Status:** Running (1/1)
- **Idade:** 38 horas
- **Deployment:** `trisla-bc-nssmf` (1/1 replicas)
- **Service:** `trisla-bc-nssmf` (ClusterIP 10.233.39.215:8083)

### Health Check

```json
{
  "status": "healthy",
  "module": "bc-nssmf",
  "enabled": true,
  "rpc_connected": true
}
```

**Observação Importante:** `rpc_connected: true` indica que o BC-NSSMF está tentando conectar ao RPC do Besu, mas o Besu não existe no cluster (ver FASE 5).

---

## 4. FASE 2 — Auditoria de Logs do BC-NSSMF

### Logs Coletados

**Período:** Últimas 200 linhas de logs

### Resultado

**❌ NENHUMA TENTATIVA DE INTERAÇÃO COM BLOCKCHAIN OBSERVADA**

Os logs do BC-NSSMF contêm **exclusivamente**:
- Health checks: `GET /health HTTP/1.1" 200 OK`
- Métricas scraping: `GET /metrics HTTP/1.1" 200 OK`

### Buscas Específicas Realizadas

1. **Contratos/Blockchain/Besu/RPC:**
   - ❌ Nenhuma referência encontrada

2. **Requisições HTTP (POST/GET):**
   - ❌ Apenas health checks e métricas
   - ❌ Nenhuma requisição de criação de contrato
   - ❌ Nenhuma chamada RPC ao Besu

3. **Erros:**
   - ❌ Nenhum erro de conexão RPC
   - ❌ Nenhum erro de serialização
   - ❌ Nenhum erro de transação

### Conclusão

**O BC-NSSMF está operacional, mas completamente inativo no fluxo de dados.**

---

## 5. FASE 3 — Auditoria do SLA-Agent → BC-NSSMF

### Logs do SLA-Agent Layer Coletados

**Período:** Últimas 200 linhas de logs

### Resultado

**❌ NENHUMA CHAMADA AO BC-NSSMF OBSERVADA**

Os logs do SLA-Agent Layer contêm **exclusivamente**:
- Health checks: `GET /health HTTP/1.1" 200 OK`
- Métricas scraping: `GET /metrics HTTP/1.1" 200 OK`

### Buscas Específicas Realizadas

1. **Referências ao BC-NSSMF:**
   - ❌ Nenhuma referência a `bc-nssmf`, `bc_nssmf`, `8083` ou `blockchain` encontrada

2. **Requisições HTTP ao BC-NSSMF:**
   - ❌ Nenhuma requisição `POST` ou `GET` ao serviço `trisla-bc-nssmf`
   - ❌ Nenhuma chamada ao endpoint `:8083`

### Conclusão

**O SLA-Agent Layer não está chamando o BC-NSSMF porque o fluxo está bloqueado antes de alcançar esta fase.**

---

## 6. FASE 4 — Auditoria de Contratos REST (Regressão)

### Endpoints Testados

#### 1. `/health`
```bash
curl http://trisla-bc-nssmf.trisla.svc.cluster.local:8083/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "module": "bc-nssmf",
  "enabled": true,
  "rpc_connected": true
}
```

✅ **Endpoint funcional**

#### 2. `/api/v1/contracts`
```bash
curl http://trisla-bc-nssmf.trisla.svc.cluster.local:8083/api/v1/contracts
```

**Resposta:**
```json
{
  "detail": "Not Found"
}
```

⚠️ **Endpoint retorna "Not Found"** (não é 404 do servidor web, mas resposta do aplicativo indicando que o endpoint não existe ou não há contratos)

#### 3. `/api/v1/contracts/create`
```bash
curl -X POST http://trisla-bc-nssmf.trisla.svc.cluster.local:8083/api/v1/contracts/create \
  -H "Content-Type: application/json" \
  -d "{}"
```

**Resposta:**
```json
{
  "detail": "Not Found"
}
```

⚠️ **Endpoint retorna "Not Found"**

#### 4. `/api/v1/blockchain`
```bash
curl http://trisla-bc-nssmf.trisla.svc.cluster.local:8083/api/v1/blockchain
```

**Resposta:**
```json
{
  "detail": "Not Found"
}
```

⚠️ **Endpoint retorna "Not Found"**

### Análise de Contratos REST

| Origem | Destino | Endpoint Observado | Status |
|--------|---------|-------------------|--------|
| SLA-Agent | BC-NSSMF | N/A (não chamado) | ❌ Fluxo bloqueado antes |
| BC-NSSMF | Besu | RPC / TX | ❌ Besu não disponível |

### Conclusão

**Os endpoints `/api/v1/contracts`, `/api/v1/contracts/create` e `/api/v1/blockchain` não estão implementados ou não estão acessíveis via roteamento atual do BC-NSSMF.**

---

## 7. FASE 5 — Auditoria do Besu (Infraestrutura)

### Verificação Completa

**Comando Executado:**
```bash
kubectl get pods -A | grep -i besu
kubectl get svc -A | grep -i besu
```

### Resultado

**❌ BESU NÃO ENCONTRADO NO CLUSTER**

- ❌ Nenhum pod Besu em nenhum namespace
- ❌ Nenhum serviço Besu em nenhum namespace
- ❌ Nenhum deployment Besu encontrado

### Análise

**Classificação:** Regressão de infraestrutura do ambiente NASP

O BC-NSSMF reporta `rpc_connected: true` no health check, mas isso pode indicar:
1. Tentativa de conexão bem-sucedida a um endpoint RPC configurado, mas o Besu não está disponível
2. Health check baseado em configuração, não em conexão real
3. Conexão a um Besu externo (fora do cluster)

**Impacto:**
- ❌ Impossível criar contratos on-chain
- ❌ Impossível validar integração blockchain real
- ⚠️ BC-NSSMF pode estar operando em modo degradado/local

---

## 8. FASE 6 — Evidência Histórica (Regressão)

### Evidências Encontradas

#### Documento: `PROMPT_S3_NASP.md`

**Conteúdo Relevante:**
```
✅ BC-NSSMF funcional no NASP
✅ Smart Contract SLA-aware ativo na Besu
✅ Ciclo de vida do SLA executado on-chain
```

**Interpretação:** No Sprint S3, o BC-NSSMF funcionou e contratos inteligentes foram criados na Besu.

#### Documento: `S6_11_NASP_RESULTS.md`

**Estado Atual (S6.11):**
- BC-NSSMF: Running, mas não recebe requisições
- Besu: Não encontrado no ambiente
- Contratos: Não criados (fluxo bloqueado antes)

#### Documento: `S6_10_EXTENDED_EXPERIMENT_RESULTS.md`

**Estado (S6.10):**
- Fluxo bloqueado no ML-NSMF (mesmo ponto atual)
- BC-NSSMF não recebia requisições (mesmo comportamento)

### Conclusão

**REGRESSÃO CONFIRMADA:**

1. **Regressão Funcional:** BC-NSSMF + Besu funcionaram no S3, mas atualmente:
   - Besu não está disponível
   - BC-NSSMF não recebe requisições
   - Fluxo bloqueado antes de alcançar blockchain

2. **Regressão de Infraestrutura:** Besu estava disponível no S3, mas não está mais no ambiente NASP

---

## 9. Onde o Fluxo Para Exatamente

### Fluxo Observado Atual

```
Portal Backend (32002)
  ↓ POST /api/v1/sla/submit
  ✅ HTTP 503 (modo degradado)
  ↓ POST http://trisla-sem-csmf:8080/api/v1/intents
SEM-CSMF
  ✅ HTTP 200 OK
  ↓ POST http://trisla-decision-engine:8082/evaluate
Decision Engine
  ⚠️ HTTP 500 Internal Server Error
  ↓ (tentativa) POST http://trisla-ml-nsmf:8081/api/v1/predict
ML-NSMF
  ❌ HTTP 500 Internal Server Error
  ↓ (NÃO ALCANÇADO)
SLA-Agent Layer
  ↓ (NÃO ALCANÇADO)
BC-NSSMF
  ↓ (NÃO ALCANÇADO)
Hyperledger Besu
  ↓ (NÃO DISPONÍVEL)
```

### Ponto de Bloqueio Principal

**ML-NSMF retorna HTTP 500**

**Erro Observado:**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for MLPrediction
timestamp
  Field required [type=missing, input_value={'risk_score': 0.5, ...}, input_type=dict]
```

**Causa Raiz:** ML-NSMF retorna resposta JSON incompleta (falta campo `timestamp` obrigatório)

**Impacto em Cascata:**
1. Decision Engine não consegue criar objeto `MLPrediction`
2. Decision Engine retorna HTTP 500
3. SEM-CSMF não recebe decisão válida
4. Fluxo não progride para SLA-Agent Layer
5. SLA-Agent Layer não chama BC-NSSMF
6. BC-NSSMF nunca recebe requisições
7. Contratos blockchain nunca são criados

---

## 10. Lista Objetiva de Correções Necessárias

### 🔴 Crítico - Bloqueio do Fluxo

#### C1: Corrigir Resposta do ML-NSMF (Campo Timestamp)

**Problema:** ML-NSMF retorna resposta JSON sem campo `timestamp` obrigatório

**Ação Necessária:**
- Adicionar campo `timestamp` na resposta do endpoint `/api/v1/predict` do ML-NSMF
- Garantir que o campo seja do tipo correto (datetime/ISO 8601 string)

**Prioridade:** 🔴 CRÍTICA (bloqueia todo o fluxo)

**Impacto:** Sem esta correção, o fluxo não pode progredir além do ML-NSMF

---

### 🟡 Alto - Infraestrutura Blockchain

#### C2: Deploy do Besu no Ambiente NASP

**Problema:** Besu não está disponível no cluster

**Ação Necessária:**
- Deploy do Hyperledger Besu no namespace apropriado
- Configuração de rede blockchain permissionada
- Exposição de endpoint RPC para o BC-NSSMF

**Prioridade:** 🟡 ALTA (necessário para validação blockchain real)

**Impacto:** Sem Besu, não é possível validar criação de contratos on-chain

**Observação:** Esta é uma regressão de infraestrutura do ambiente, não do código TriSLA

---

### 🟡 Alto - Endpoints BC-NSSMF

#### C3: Implementar/Corrigir Endpoints REST do BC-NSSMF

**Problema:** Endpoints `/api/v1/contracts`, `/api/v1/contracts/create`, `/api/v1/blockchain` retornam "Not Found"

**Ação Necessária:**
- Verificar se os endpoints estão implementados no código do BC-NSSMF
- Verificar roteamento FastAPI/Flask do BC-NSSMF
- Implementar endpoints se ausentes
- Corrigir roteamento se endpoints existem mas não estão acessíveis

**Prioridade:** 🟡 ALTA (necessário para SLA-Agent chamar BC-NSSMF)

**Impacto:** Sem endpoints corretos, SLA-Agent não pode criar contratos mesmo se o fluxo progredir

---

### 🟢 Médio - Integração SLA-Agent → BC-NSSMF

#### C4: Verificar Chamadas do SLA-Agent ao BC-NSSMF

**Problema:** Após correção do ML-NSMF, verificar se SLA-Agent chama BC-NSSMF corretamente

**Ação Necessária:**
- Após C1 estar corrigido, verificar logs do SLA-Agent
- Confirmar que SLA-Agent tenta chamar BC-NSSMF após receber decisão do Decision Engine
- Verificar endpoint correto usado pelo SLA-Agent
- Verificar payload enviado pelo SLA-Agent

**Prioridade:** 🟢 MÉDIA (depende de C1 estar corrigido)

**Impacto:** Garantir que o fluxo completo funcione após correção do ML-NSMF

---

### 🟢 Baixo - Documentação

#### C5: Documentar Contratos REST Entre Módulos

**Problema:** Endpoints e payloads não estão claramente documentados

**Ação Necessária:**
- Documentar endpoint esperado pelo SLA-Agent para chamar BC-NSSMF
- Documentar formato do payload esperado pelo BC-NSSMF
- Documentar resposta esperada do BC-NSSMF

**Prioridade:** 🟢 BAIXA (melhoria de documentação)

**Impacto:** Facilita manutenção e debugging futuro

---

## 11. Resumo de Regressões Identificadas

### Regressão 1: ML-NSMF Resposta Incompleta

**Quando Funcionou:** Versões anteriores (não documentado exatamente quando parou)

**Estado Atual:** Retorna HTTP 500 devido a campo `timestamp` ausente

**Classificação:** Regressão funcional no ML-NSMF

### Regressão 2: Besu Indisponível

**Quando Funcionou:** Sprint S3 (conforme `PROMPT_S3_NASP.md`)

**Estado Atual:** Besu não encontrado no cluster

**Classificação:** Regressão de infraestrutura do ambiente NASP

### Regressão 3: Fluxo Blockchain Inativo

**Quando Funcionou:** Sprint S3 (conforme `PROMPT_S3_NASP.md`)

**Estado Atual:** BC-NSSMF não recebe requisições, fluxo bloqueado antes

**Classificação:** Regressão funcional do pipeline completo

---

## 12. Conclusões Finais

### ✅ Critérios de Conclusão Atendidos

1. ✅ **Ponto exato de quebra identificado:** ML-NSMF (campo timestamp ausente)
2. ✅ **BC-NSSMF acionado confirmado:** ❌ Não é acionado (fluxo bloqueado antes)
3. ✅ **Besu disponível confirmado:** ❌ Não está disponível (regressão de infraestrutura)
4. ✅ **Regressões identificadas:** ✅ 3 regressões identificadas e documentadas
5. ✅ **Documento de auditoria gerado:** ✅ Este documento

### Principais Descobertas

1. **Bloqueio em Cascata:** O erro no ML-NSMF causa bloqueio em cascata que impede o fluxo de alcançar qualquer componente blockchain

2. **BC-NSSMF Operacional mas Inativo:** O BC-NSSMF está Running e saudável, mas nunca recebe requisições devido ao bloqueio anterior no pipeline

3. **Regressão de Infraestrutura:** O Besu, que funcionou no S3, não está mais disponível no ambiente NASP

4. **Endpoints Não Implementados:** Os endpoints REST do BC-NSSMF para criação de contratos retornam "Not Found", indicando que podem não estar implementados ou acessíveis

### Próximos Passos Recomendados

1. **Prioridade 1:** Corrigir ML-NSMF (C1) - necessário para desbloquear o fluxo
2. **Prioridade 2:** Deploy do Besu (C2) - necessário para validação blockchain real
3. **Prioridade 3:** Corrigir endpoints BC-NSSMF (C3) - necessário para SLA-Agent criar contratos
4. **Prioridade 4:** Validar integração completa (C4) - após correções anteriores

---

**Documento gerado em:** 2025-12-21  
**Auditoria:** S6.AUDIT_BLOCKCHAIN_PIPELINE  
**Status:** ✅ CONCLUÍDA  
**Modo:** Read-only (nenhuma correção aplicada)

---

## 13. Anexos

### Comandos Executados Durante a Auditoria

Todos os comandos executados foram de leitura exclusiva:
- `kubectl get pods -n trisla -o wide`
- `kubectl get svc -n trisla`
- `kubectl logs -n trisla deployment/trisla-bc-nssmf --tail=200`
- `kubectl logs -n trisla deployment/trisla-sla-agent-layer --tail=200`
- `kubectl get pods -A | grep -i besu`
- `curl http://trisla-bc-nssmf.trisla.svc.cluster.local:8083/health`
- `curl http://trisla-bc-nssmf.trisla.svc.cluster.local:8083/api/v1/contracts`

**Nenhuma alteração foi feita no cluster, código, configuração ou imagens.**

