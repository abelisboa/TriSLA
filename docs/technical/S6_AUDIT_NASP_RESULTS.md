# S6_AUDIT_NASP_RESULTS — Auditoria Técnica NASP

**Data:** 2025-12-21  
**Protocolo:** AUDITORIA TÉCNICA NASP — PRÉ-CONDIÇÃO OBRIGATÓRIA

---

## Respostas às Perguntas-Chave

### ❓ O NASP instancia slice real?

**Resposta:** **SIM (infraestrutura pronta, mas não executada)**

**Evidências:**
- ✅ CRDs NSI/NSSI definidos: `networksliceinstances.trisla.io`, `networkslicesubnetinstances.trisla.io`
- ✅ Controllers NSI/NSSI existem no código
- ✅ Serviços NASP externos existem no cluster (srsenb, open5gs-upf)
- ❌ Nenhuma instância NSI/NSSI criada após ACCEPT
- ❌ Fluxo falha antes de chegar à criação de CRDs

**Conclusão:** Infraestrutura completa para criar slices reais existe, mas o fluxo não executa porque falha na conexão com endpoint externo do NASP.

---

### ❓ O NASP fala NSI/NSSI?

**Resposta:** **SIM**

**Evidências:**
- ✅ CRDs definem NSI/NSSI conforme 3GPP TS 23.501
- ✅ Campos: `nsiId`, `nssiIds`, `sst` (Slice/Service Type), `sd` (Slice Differentiator)
- ✅ Controllers: `nsi_controller.py`, `nsi_watch_controller.py`
- ✅ RBAC configurado para gerenciar CRDs NSI/NSSI
- ❌ Controllers não são executados (fluxo falha antes)

**Conclusão:** O NASP Adapter foi projetado para trabalhar com NSI/NSSI, mas os controllers não são acionados porque o fluxo falha na etapa anterior.

---

### ❓ O NASP espera action/intent/policy?

**Resposta:** **ACTION**

**Evidências:**
- ✅ Endpoint: `POST /api/v1/nasp/actions`
- ✅ Payload esperado (segundo código):
  ```json
  {
    "type": "string",  // obrigatório
    "domain": "string"  // opcional, padrão: "ran"
  }
  ```
- ❌ Não espera "intent" nem "policy" diretamente

**Conclusão:** O NASP trabalha com **ações** (actions), não intents ou policies.

---

### ❓ Onde o NASP registra estado?

**Resposta:** **CRDs Kubernetes NSI/NSSI**

**Evidências:**
- ✅ CRDs definidos para persistir estado de NSI/NSSI
- ✅ Campos de estado: `phase` (lifecycle), `nsiId`, `nssiIds`, timestamps
- ✅ Controllers prontos para criar/atualizar CRDs
- ❌ Nenhuma instância criada (fluxo não chega até lá)

**Alternativas observadas:**
- Logs do NASP Adapter registram tentativas e erros
- Não há persistência de estado de sucesso (apenas falhas em logs)

**Conclusão:** O estado **deveria** ser registrado em CRDs NSI/NSSI, mas não está acontecendo porque o fluxo falha antes da criação.

---

### ❓ O NASP Adapter é executor real/simulador/proxy?

**Resposta:** **PROXY/EXECUTOR HÍBRIDO**

**Evidências:**

1. **Proxy para NASP externo:**
   - Chama endpoints externos: `POST {ran_endpoint}/api/v1/actions`
   - Endpoints configurados:
     - RAN: `http://srsenb.srsran.svc.cluster.local:36412`
     - Core: `http://open5gs-upf.open5gs.svc.cluster.local:8805`
     - AMF/SMF: namespace `ns-1274485`

2. **Executor no Kubernetes:**
   - Tem controllers para criar CRDs NSI/NSSI
   - RBAC configurado para criar recursos K8s
   - Infraestrutura completa para execução real

3. **Modo de operação:**
   - Modo "real" (padrão): tenta endpoints externos
   - Modo "mock" (se `NASP_MODE=mock`): usa endpoints mock

**Conclusão:** O NASP Adapter é um **proxy/executor híbrido**:
1. Recebe ações do TriSLA (via SLA-Agent)
2. Tenta executar no NASP externo (proxy)
3. Se bem-sucedido, deveria criar CRDs NSI/NSSI (executor no K8s)
4. Atualmente falha no passo 2 (endpoint externo não acessível)

---

## Descobertas Técnicas

### Endpoints NASP Externos

**Namespaces e serviços existem no cluster:**
- ✅ `srsran` namespace: Serviço `srsenb` (36412/TCP, 9092/TCP)
- ✅ `open5gs` namespace: Serviço `open5gs-upf` (8805/TCP, 9090/TCP)
- ✅ `ns-1274485` namespace: Existe

**Problema identificado:**
- Serviços existem mas conexão falha
- Endpoint específico `/api/v1/actions` pode não estar implementado
- Ou pods dos serviços não estão rodando/healthy

### Fluxo de Execução

1. **Recebimento:** `POST /api/v1/nasp/actions` (do SLA-Agent)
2. **Processamento:** `action_executor.execute(action)`
   - Extrai `type` e `domain` (padrão: "ran")
3. **Proxy externo:** `nasp_client.execute_ran_action(action)`
   - Chama `POST {ran_endpoint}/api/v1/actions`
   - **FALHA AQUI** → "All connection attempts failed"
4. **Executor K8s:** Se passo 3 sucesso, criar CRDs NSI/NSSI
   - **NUNCA EXECUTADO** (passo 3 falha)

### Estrutura de Código

**Arquivos principais:**
- `apps/nasp-adapter/src/main.py` - API FastAPI
- `apps/nasp-adapter/src/action_executor.py` - Executor de ações
- `apps/nasp-adapter/src/nasp_client.py` - Cliente HTTP para NASP externo
- `apps/nasp-adapter/src/controllers/nsi_controller.py` - Controller NSI
- `apps/nasp-adapter/crds/` - Definições CRDs

---

## Limitações Identificadas

1. **Conectividade Externa:**
   - Endpoints NASP externos existem mas não são acessíveis
   - Possíveis causas: pods down, NetworkPolicy, endpoint não implementado

2. **Fluxo Incompleto:**
   - Ação falha antes de chegar à criação de CRDs
   - Controllers NSI/NSSI nunca são acionados
   - Nenhuma instância NSI/NSSI criada

3. **Falta de Modo Degradado:**
   - Não há fallback se endpoint externo não disponível
   - Fluxo para completamente se conexão falha

---

## Recomendações para S6.17

1. **Investigar endpoint correto:**
   - Verificar se `/api/v1/actions` existe no srsenb
   - Verificar se pods dos serviços estão rodando
   - Verificar NetworkPolicies

2. **Decisão arquitetural:**
   - Implementar modo degradado (criar CRDs mesmo sem conexão externa)?
   - Ou documentar que endpoint externo é obrigatório?

3. **Validação:**
   - Quando endpoint funcionar, validar criação completa de CRDs NSI/NSSI
   - Validar ciclo de vida completo de NSI/NSSI

---

## Evidências Coletadas

- ✅ Código-fonte analisado
- ✅ CRDs verificados no cluster
- ✅ Logs analisados
- ✅ OpenAPI documentado
- ✅ Deployment YAML coletado
- ✅ Serviços NASP externos verificados

**Arquivos gerados:**
- `logs/s6_audit_nasp/FINAL_AUDIT_REPORT.md`
- `logs/s6_audit_nasp/AUDIT_REPORT.md`
- `logs/s6_audit_nasp/CONCLUSOES_FINAIS.md`
- `logs/s6_audit_nasp/nasp_adapter_deployment.yaml`

---

**Status:** ✅ Auditoria completa  
**Próximo passo:** S6.17 - Implementar correção baseada nas descobertas
