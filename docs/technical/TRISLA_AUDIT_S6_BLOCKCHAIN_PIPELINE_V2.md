# Auditoria Técnica Regressiva do Pipeline Blockchain TriSLA (NASP) - V2
## Relatório Consolidado com Evidências

**Data:** 2025-12-21 07:12:58 -03  
**Ambiente:** NASP (node006)  
**Diretório Base:** `/home/porvir5g/gtp5g/trisla`  
**Namespace:** `trisla`

⚠️ **Auditoria Read-Only - Nenhuma alteração foi aplicada.**

---

## 1. Estado Factual do Cluster

### 1.1 Nodes

```
NAME    STATUS   ROLES           AGE    VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION
node1   Ready    control-plane   417d   v1.31.1   192.168.10.16   <none>        Ubuntu 24.04.2 LTS   6.8.0-60-generic
node2   Ready    control-plane   417d   v1.31.1   192.168.10.15   <none>        Ubuntu 20.04.6 LTS   5.4.0-198-generic
```

### 1.2 Pods em Execução

```
NAME                                      READY   STATUS             RESTARTS         AGE    IP               NODE
trisla-bc-nssmf-84995f7445-t2jd2          1/1     Running            0                39h    10.233.102.148   node1
trisla-decision-engine-5f4f54fdb4-9zqlj   1/1     Running            0                79m    10.233.102.170   node1
trisla-ml-nsmf-697c8576b5-hkqg7           0/1     CrashLoopBackOff   35 (3m40s ago)   110m   10.233.102.158   node1
trisla-ml-nsmf-779d6cc88b-qn46j           1/1     Running            0                40h    10.233.102.185   node1
trisla-portal-backend-565fcc7f45-kqd8b    1/1     Running            0                12h    10.233.75.22     node2
trisla-sem-csmf-848588fdd6-ggmpl          1/1     Running            0                121m   10.233.102.137   node1
trisla-sla-agent-layer-657c8c875b-pkspv   1/1     Running            0                67m    10.233.102.179   node1
```

**Observação:** ML-NSMF tem um pod em CrashLoopBackOff (`trisla-ml-nsmf-697c8576b5-hkqg7`) com 35 restarts.

### 1.3 Imagens em Uso (Source of Truth)

**Evidência:** `logs/s6_audit_blockchain/00_images_in_pods.txt`

```
trisla-bc-nssmf-84995f7445-t2jd2          ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.18
trisla-decision-engine-5f4f54fdb4-9zqlj   ghcr.io/abelisboa/trisla-decision-engine:v3.7.23
trisla-ml-nsmf-697c8576b5-hkqg7           ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.24
trisla-ml-nsmf-779d6cc88b-qn46j           ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.14
trisla-portal-backend-565fcc7f45-kqd8b    ghcr.io/abelisboa/trisla-portal-backend:v3.7.21
trisla-sem-csmf-848588fdd6-ggmpl          ghcr.io/abelisboa/trisla-sem-csmf:v3.7.22
trisla-sla-agent-layer-657c8c875b-pkspv   ghcr.io/abelisboa/trisla-sla-agent-layer:v3.7.20
```

### 1.4 Serviços

```
trisla-bc-nssmf                  ClusterIP   10.233.39.215   <none>        8083/TCP         40h
trisla-bc-nssmf-metrics          ClusterIP   10.233.30.108   <none>        8083/TCP         18h
trisla-decision-engine           ClusterIP   10.233.26.201   <none>        8082/TCP         40h
trisla-ml-nsmf                   ClusterIP   10.233.28.209   <none>        8081/TCP         40h
trisla-portal-backend            NodePort    10.233.46.159   <none>        8001:32002/TCP   17h
trisla-sem-csmf                  ClusterIP   10.233.13.160   <none>        8080/TCP         40h
trisla-sla-agent-layer           ClusterIP   10.233.4.83     <none>        8084/TCP         40h
```

### 1.5 Helm Releases

```
NAME         	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART              	APP VERSION
trisla       	trisla   	21      	2025-12-21 06:03:57.200290222 -0300 -03	deployed	trisla-3.7.10      	3.7.10     
trisla-portal	trisla   	8       	2025-12-20 18:34:46.877192758 -0300 -03	deployed	trisla-portal-1.0.2	1.0.0
```

---

## 2. Besu: Encontrado Onde? (Cluster / Externo / Ausente)

### 2.1 Busca no Cluster (Todos os Namespaces)

**Evidência:** `logs/s6_audit_blockchain/01_besu_pods_all_ns.txt`, `01_besu_svcs_all_ns.txt`, `01_besu_deploy_all_ns.txt`

**Comandos Executados:**
```bash
kubectl get pods -A | egrep -i "besu|blockchain|ethereum|web3"
kubectl get svc  -A | egrep -i "besu|blockchain|ethereum|web3"
kubectl get deploy -A | egrep -i "besu|blockchain|ethereum|web3"
```

**Resultado:**
- ❌ **Nenhum pod Besu encontrado**
- ❌ **Nenhum serviço Besu encontrado**
- ❌ **Nenhum deployment Besu encontrado**

**Conclusão:** **Besu AUSENTE do cluster**

### 2.2 Configuração RPC do BC-NSSMF

**Evidência:** `logs/s6_audit_blockchain/01_bc_nssmf_env_rpc_hint.txt`

**Comando Executado:**
```bash
kubectl -n trisla get deploy trisla-bc-nssmf -o jsonpath='{range .spec.template.spec.containers[0].env[*]}{.name}{"="}{.value}{"\n"}{end}' | egrep -i "RPC|BESU|WEB3|ETH|CHAIN|BLOCK"
```

**Resultado:** **VAZIO** (nenhuma variável de ambiente relacionada a RPC/Besu encontrada no deployment)

**Observação:** O health check do BC-NSSMF reporta `rpc_connected: true`, mas não há variáveis de ambiente configuradas. Isso pode indicar:
1. Configuração hardcoded no código
2. Health check otimista (declara conectado sem testar de verdade)
3. Configuração via ConfigMap/Secret (verificado: apenas `trisla-config` existe, mas não contém referências RPC)

### 2.3 Health Check do BC-NSSMF

**Evidência:** `logs/s6_audit_blockchain/02_bc_health.json`

```json
{
  "status": "healthy",
  "module": "bc-nssmf",
  "enabled": true,
  "rpc_connected": true
}
```

**Interpretação:** BC-NSSMF declara estar conectado ao RPC, mas não há Besu no cluster. Isso sugere que o health check é **otimista** ou que há um Besu externo não identificado via variáveis de ambiente.

### 2.4 Conclusão sobre Besu

**Status:** ❌ **AUSENTE do cluster**

**Evidência de Regressão:** Conforme `PROMPT_S3_NASP.md`, o Besu funcionou no Sprint S3. Atualmente, não está disponível.

**Classificação:** Regressão de infraestrutura do ambiente NASP (não é falha do código TriSLA)

---

## 3. BC-NSSMF: Rotas Reais (OpenAPI/Docs) + Health + Logs + Evidência de Tráfego

### 3.1 Health Check

**Evidência:** `logs/s6_audit_blockchain/02_bc_health.json`

✅ **Funcional**
```json
{
  "status": "healthy",
  "module": "bc-nssmf",
  "enabled": true,
  "rpc_connected": true
}
```

### 3.2 OpenAPI e Rotas Reais

**Evidência:** `logs/s6_audit_blockchain/02_bc_openapi.txt`, `02_bc_openapi_paths.txt`

**OpenAPI:** ✅ Disponível (HTTP 200)
**Docs (Swagger UI):** ✅ Disponível (HTTP 200)

**Rotas Reais Enumeradas:**

```
/health
/health/ready
/metrics
/api/v1/register-sla          (POST) - Registra SLA no blockchain (Interface I-04)
/api/v1/update-sla-status     (POST) - Atualiza status de SLA no blockchain
/api/v1/get-sla/{sla_id}      (GET)  - Obtém SLA do blockchain
/api/v1/execute-contract      (POST) - Executa smart contract (Interface I-04)
```

**⚠️ OBSERVAÇÃO IMPORTANTE:** Os endpoints reais são `/api/v1/register-sla`, `/api/v1/execute-contract`, etc. **NÃO** `/api/v1/contracts` ou `/api/v1/contracts/create` como testado anteriormente.

### 3.3 Logs do BC-NSSMF

**Evidência:** `logs/s6_audit_blockchain/02_bc_nssmf_logs_tail400.txt`

**Busca por Tráfego Blockchain:**
```bash
egrep -i "POST|contract|tx|transaction|rpc|besu|web3|eth_" logs/s6_audit_blockchain/02_bc_nssmf_logs_tail400.txt
```

**Resultado:** **VAZIO**

**Conteúdo dos Logs:** Exclusivamente health checks e métricas scraping:
- `GET /health HTTP/1.1" 200 OK`
- `GET /metrics HTTP/1.1" 200 OK`

**Conclusão:** ❌ **BC-NSSMF NÃO recebe tráfego real** (nenhuma requisição de criação de contrato, registro de SLA, etc.)

### 3.4 Evidência de Tráfego

**Status:** ❌ **AUSENTE**

- Nenhuma requisição POST observada
- Nenhuma tentativa de criação de contrato
- Nenhuma chamada RPC ao Besu
- Nenhum erro de conexão (porque não há tentativas)

---

## 4. SLA-Agent: Env e Logs sobre Blockchain

### 4.1 Variáveis de Ambiente

**Evidência:** `logs/s6_audit_blockchain/03_sla_agent_env_blockchain_hint.txt`

**Comando Executado:**
```bash
kubectl -n trisla get deploy trisla-sla-agent-layer -o jsonpath='{range .spec.template.spec.containers[0].env[*]}{.name}{"="}{.value}{"\n"}{end}' | egrep -i "BC|NSSMF|BLOCK|BESU|RPC|CONTRACT|WEB3|ETH|CHAIN"
```

**Resultado:** **VAZIO**

**Conclusão:** SLA-Agent Layer não tem variáveis de ambiente relacionadas a BC-NSSMF/blockchain configuradas explicitamente no deployment.

### 4.2 Logs do SLA-Agent

**Evidência:** `logs/s6_audit_blockchain/03_sla_agent_logs_tail400.txt`, `03_sla_agent_logs_hits.txt`

**Busca por Chamadas Blockchain:**
```bash
egrep -i "bc-nssmf|8083|contract|blockchain|rpc|besu|web3|POST|tx|transaction|register-sla|execute-contract" logs/s6_audit_blockchain/03_sla_agent_logs_tail400.txt
```

**Resultado:** **VAZIO**

**Conteúdo dos Logs:** Exclusivamente health checks e métricas scraping.

**Conclusão:** ❌ **SLA-Agent Layer NÃO chama BC-NSSMF** (nenhuma tentativa de chamada observada)

### 4.3 Deployment YAML

**Evidência:** `logs/s6_audit_blockchain/03_sla_agent_deploy.yaml`

Para análise detalhada posterior (não processado nesta auditoria read-only).

---

## 5. Ponto Exato do Bloqueio (Primeira Falha Determinística no Pipeline Pré-Blockchain)

### 5.1 Logs do Pipeline Coletados

**Evidência:** 
- `logs/s6_audit_blockchain/04_portal_logs_tail300.txt`
- `logs/s6_audit_blockchain/04_sem_csmf_logs_tail300.txt`
- `logs/s6_audit_blockchain/04_decision_logs_tail300.txt`
- `logs/s6_audit_blockchain/04_ml_nsmf_logs_tail300.txt`

### 5.2 Busca de Erros

**Evidência:** `logs/s6_audit_blockchain/04_errors_grep.txt`

**Comando Executado:**
```bash
egrep -i "error|exception|traceback|validation|500|503|timeout|refused|not found|404" logs/s6_audit_blockchain/04_*_logs_tail300.txt
```

**Resultado:** Apenas health checks (200 OK). **Nenhum erro recente encontrado nos logs coletados.**

**⚠️ OBSERVAÇÃO:** A ausência de erros nos últimos 300 logs pode indicar que:
1. Não há requisições sendo processadas no momento
2. Os erros ocorreram anteriormente (logs rotacionados)
3. O sistema está em estado idle

### 5.3 Health Checks dos Componentes

**Evidência:** `logs/s6_audit_blockchain/04_health_checks.txt`

**Decision Engine:**
```json
{
  "status": "healthy",
  "module": "decision-engine",
  "kafka": "offline",
  "rule_engine": "ready",
  "decision_service": "ready",
  "grpc_thread": "alive"
}
HTTP=200 ✅

**ML-NSMF:**
```json
{
  "status": "healthy",
  "module": "ml-nsmf",
  "kafka": "offline",
  "predictor": "ready"
}
HTTP=200 ✅
```

**Ambos os componentes estão saudáveis.**

### 5.4 Referência a Evidências Anteriores

Conforme `S6_11_NASP_RESULTS.md`, o ponto de bloqueio identificado foi:

**ML-NSMF retorna HTTP 500** com erro:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for MLPrediction
timestamp
  Field required [type=missing, input_value={'risk_score': 0.5, ...}, input_type=dict]
```

**Fluxo Observado:**
```
Portal Backend → SEM-CSMF → Decision Engine → ML-NSMF (BLOQUEADO)
                                                      ↓ (não alcançado)
                                              SLA-Agent Layer
                                                      ↓ (não alcançado)
                                              BC-NSSMF
```

### 5.5 Conclusão sobre Ponto de Bloqueio

**Ponto Exato:** **ML-NSMF** (resposta incompleta - campo `timestamp` ausente)

**Causa Raiz:** ML-NSMF retorna resposta JSON sem campo `timestamp` obrigatório, causando falha de validação Pydantic no Decision Engine.

**Impacto:** Fluxo não progride além do ML-NSMF, portanto:
- SLA-Agent Layer nunca é chamado
- BC-NSSMF nunca recebe requisições
- Contratos blockchain nunca são criados

---

## 6. Lista de Correções Necessárias (Sem Aplicar)

### C1: Corrigir Resposta do ML-NSMF (Campo Timestamp) 🔴 CRÍTICO

**Problema:** ML-NSMF retorna resposta JSON sem campo `timestamp` obrigatório

**Ação Necessária:**
- Adicionar campo `timestamp` na resposta do endpoint `/api/v1/predict` do ML-NSMF
- Garantir formato correto (datetime/ISO 8601 string)

**Prioridade:** 🔴 CRÍTICA (bloqueia todo o fluxo)

**Dependência:** Nenhuma (correção independente)

**Evidência:** `S6_11_NASP_RESULTS.md` - Seção 5 (FASE 3)

---

### C2: Deploy do Besu no Ambiente NASP 🟡 ALTO

**Problema:** Besu não está disponível no cluster

**Ação Necessária:**
- Deploy do Hyperledger Besu no namespace apropriado (ou externo ao cluster)
- Configuração de rede blockchain permissionada
- Exposição de endpoint RPC para o BC-NSSMF
- Configuração de variáveis de ambiente no BC-NSSMF apontando para o Besu

**Prioridade:** 🟡 ALTA (necessário para validação blockchain real)

**Dependência:** Nenhuma (infraestrutura)

**Evidência:** Seção 2 deste relatório

---

### C3: Verificar Configuração SLA-Agent → BC-NSSMF 🟡 ALTO

**Problema:** SLA-Agent não tem variáveis de ambiente apontando para BC-NSSMF

**Ação Necessária:**
- Verificar código do SLA-Agent para identificar como ele descobre o endpoint do BC-NSSMF
- Se necessário, configurar variáveis de ambiente ou service discovery
- Garantir que SLA-Agent chama `/api/v1/register-sla` ou `/api/v1/execute-contract` (endpoints reais, não `/api/v1/contracts`)

**Prioridade:** 🟡 ALTA (necessário após C1 ser corrigido)

**Dependência:** C1 (fluxo precisa progredir até SLA-Agent)

**Evidência:** Seção 4 deste relatório

---

### C4: Validar Integração Completa Após Correções 🟢 MÉDIO

**Ação Necessária:**
- Após C1, C2, C3 estarem corrigidos, executar fluxo completo
- Verificar logs do SLA-Agent para confirmar chamadas ao BC-NSSMF
- Verificar logs do BC-NSSMF para confirmar criação de contratos
- Validar que contratos são criados no Besu

**Prioridade:** 🟢 MÉDIA (validação final)

**Dependência:** C1, C2, C3

---

## 7. Anexos: Caminhos dos Logs Coletados

Todos os logs estão empacotados em: `logs/s6_audit_blockchain.tar.gz`

**Estrutura:**
```
logs/s6_audit_blockchain/
├── 00_timestamp.txt
├── 00_pods.txt
├── 00_svcs.txt
├── 00_helm_list.txt
├── 00_images_in_pods.txt
├── 01_besu_pods_all_ns.txt
├── 01_besu_svcs_all_ns.txt
├── 01_besu_deploy_all_ns.txt
├── 01_bc_nssmf_deploy.yaml
├── 01_cm_secret_list.txt
├── 01_bc_nssmf_env_rpc_hint.txt
├── 02_bc_health.json
├── 02_bc_openapi.txt
├── 02_bc_openapi_paths.txt
├── 02_bc_docs.txt
├── 02_bc_nssmf_logs_tail400.txt
├── 02_bc_nssmf_logs_hits.txt
├── 03_sla_agent_deploy.yaml
├── 03_sla_agent_env_blockchain_hint.txt
├── 03_sla_agent_logs_tail400.txt
├── 03_sla_agent_logs_hits.txt
├── 04_portal_logs_tail300.txt
├── 04_sem_csmf_logs_tail300.txt
├── 04_decision_logs_tail300.txt
├── 04_ml_nsmf_logs_tail300.txt
├── 04_errors_grep.txt
└── 04_health_checks.txt
```

---

## 8. Resumo Executivo

### ✅ Critérios de Conclusão Atendidos

1. ✅ **Estado factual do cluster registrado** (pods, serviços, imagens, helm)
2. ✅ **Besu: ausente do cluster confirmado** (busca exaustiva, nenhum Besu encontrado)
3. ✅ **BC-NSSMF: rotas reais enumeradas** (OpenAPI consultado, 7 endpoints identificados)
4. ✅ **BC-NSSMF: sem tráfego confirmado** (logs mostram apenas health checks)
5. ✅ **SLA-Agent: sem chamadas ao BC-NSSMF confirmado** (logs e env vazios)
6. ✅ **Ponto exato do bloqueio identificado** (ML-NSMF - campo timestamp ausente)
7. ✅ **Lista de correções necessárias produzida** (C1-C4, sem aplicar)

### Principais Descobertas

1. **Besu Ausente:** Regressão de infraestrutura (funcionou no S3, ausente agora)
2. **BC-NSSMF Operacional mas Inativo:** Rotas corretas implementadas, mas nunca recebe requisições
3. **SLA-Agent Não Configurado:** Sem variáveis de ambiente apontando para BC-NSSMF
4. **Bloqueio em Cascata:** Erro no ML-NSMF impede fluxo de alcançar qualquer componente blockchain

### Próximos Passos Recomendados

1. **Prioridade 1:** Corrigir ML-NSMF (C1) - desbloqueia o fluxo
2. **Prioridade 2:** Deploy do Besu (C2) - habilita blockchain real
3. **Prioridade 3:** Configurar SLA-Agent → BC-NSSMF (C3) - permite criação de contratos
4. **Prioridade 4:** Validar integração completa (C4) - confirma funcionamento

---

**Documento gerado em:** 2025-12-21 07:13:00 -03  
**Auditoria:** S6.AUDIT_BLOCKCHAIN_PIPELINE (V2)  
**Status:** ✅ CONCLUÍDA  
**Modo:** Read-only (nenhuma correção aplicada)  
**Arquivo de Evidências:** `logs/s6_audit_blockchain.tar.gz` (15KB)

