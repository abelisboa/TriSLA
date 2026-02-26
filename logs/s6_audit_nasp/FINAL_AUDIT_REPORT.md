# AUDITORIA TÉCNICA NASP — Relatório Final

**Data:** 2025-12-21  
**Objetivo:** Descobrir como o NASP realmente cria (ou simula) um slice/SLA

## Descobertas Principais

### 1. Estrutura do NASP Adapter

**Código-fonte encontrado:**
- `apps/nasp-adapter/src/action_executor.py` - Executor de ações
- `apps/nasp-adapter/src/nasp_client.py` - Cliente HTTP para NASP externo
- `apps/nasp-adapter/src/main.py` - API FastAPI
- `apps/nasp-adapter/crds/` - Definições de CRDs NSI/NSSI

### 2. Endpoint e API

**Endpoint principal:**
- `POST /api/v1/nasp/actions` - Executa ação no NASP

**OpenAPI disponível:**
- `GET /openapi.json` - Esquema da API
- Descrição: "Executa ação real no NASP (I-07)"

### 3. CRDs Definidos

**CRDs encontrados no cluster:**
- `networksliceinstances.trisla.io` ✅ (definido)
- `networkslicesubnetinstances.trisla.io` ✅ (definido)

**Instâncias criadas:**
- Nenhuma instância NSI encontrada no cluster
- Nenhuma instância NSSI encontrada no cluster

### 4. Comportamento Observado

**Fluxo de execução:**
1. Recebe ação via `POST /api/v1/nasp/actions`
2. `action_executor.execute(action)` extrai:
   - `action.get("type")`
   - `action.get("domain", "ran")` (padrão: "ran")
3. `nasp_client.execute_ran_action(action)` chama:
   - `POST {ran_endpoint}/api/v1/actions`
4. Erro atual: "All connection attempts failed" - endpoint externo não acessível

### 5. Evidências de NSI/NSSI

**No código:**
- CRDs definem NSI/NSSI (3GPP compliant)
- Controllers NSI encontrados: `nsi_controller.py`, `nsi_watch_controller.py`
- RBAC configurado para CRDs NSI/NSSI

**No cluster:**
- CRDs existem mas nenhuma instância foi criada
- Nenhuma referência NSI/NSSI nos logs recentes

## Respostas às Perguntas-Chave

### ❓ O NASP instancia slice real?

**Resposta:** **PARCIALMENTE**

- ✅ CRDs NSI/NSSI estão definidos (infraestrutura pronta)
- ❌ Nenhuma instância NSI/NSSI foi criada após ACCEPT
- ❌ NASP Adapter tenta chamar endpoint externo do NASP mas falha (conectividade)

**Conclusão:** O código tem infraestrutura para criar slices reais via CRDs, mas não está sendo executado porque:
1. O endpoint externo do NASP não está acessível
2. O fluxo falha antes de chegar à criação de CRDs

### ❓ O NASP fala NSI/NSSI?

**Resposta:** **SIM (no código)**

- ✅ CRDs definem NSI/NSSI (3GPP TS 23.501)
- ✅ Controllers para NSI/NSSI existem
- ❌ Mas não estão sendo usados no fluxo atual

**Conclusão:** O NASP Adapter **foi projetado** para trabalhar com NSI/NSSI, mas o fluxo atual não chega a criar instâncias porque falha na conexão externa.

### ❓ O NASP espera action/intent/policy?

**Resposta:** **ACTION**

- ✅ Endpoint: `POST /api/v1/nasp/actions`
- ✅ Payload esperado: `action` (dict) com:
  - `type` (obrigatório)
  - `domain` (opcional, padrão: "ran")
- ❌ Não espera "intent" nem "policy" diretamente

**Conclusão:** O NASP trabalha com **ações** (actions), não intents ou policies diretamente.

### ❓ Onde o NASP registra estado?

**Resposta:** **CRDs Kubernetes (quando funcionar)**

- ✅ CRDs definidos para NSI/NSSI
- ✅ Controllers prontos para gerenciar CRDs
- ❌ Nenhuma instância criada (fluxo não chega até lá)

**Alternativamente:**
- Logs do NASP Adapter registram tentativas
- Erros são registrados mas não há persistência de estado de sucesso

**Conclusão:** O estado **deveria** ser registrado em CRDs NSI/NSSI, mas não está acontecendo porque o fluxo falha antes.

### ❓ O NASP Adapter é executor real/simulador/proxy?

**Resposta:** **PROXY/EXECUTOR HÍBRIDO**

- ✅ Chama endpoint externo do NASP (`{ran_endpoint}/api/v1/actions`)
- ✅ Tem controllers para criar CRDs NSI/NSSI (execução real no K8s)
- ⚠️ Não é puro simulador (tenta conexão externa real)
- ⚠️ Não é puro executor (depende de endpoint externo)

**Conclusão:** O NASP Adapter é um **proxy/executor híbrido** que:
1. Recebe ações do TriSLA
2. Tenta executar no NASP externo (proxy)
3. Se bem-sucedido, deveria criar CRDs NSI/NSSI (executor)
4. Atualmente falha no passo 2 (endpoint externo inacessível)

## Limitações Identificadas

1. **Conectividade Externa:**
   - NASP Adapter tenta conectar a endpoint externo (`{ran_endpoint}/api/v1/actions`)
   - Endpoint não está acessível (Connection refused)
   - Variável de ambiente `RAN_ENDPOINT` não encontrada (provavelmente não configurada)

2. **Fluxo Incompleto:**
   - Ação falha antes de chegar à criação de CRDs
   - Controllers NSI/NSSI nunca são acionados
   - Nenhuma instância NSI/NSSI criada

3. **Falta de Estado Persistente:**
   - Sem conexão externa bem-sucedida, não há criação de recursos
   - Logs registram apenas falhas

## Recomendações para S6.17

1. **Decisão Arquitetural:**
   - Definir se NASP Adapter deve funcionar em modo degradado (sem endpoint externo)
   - Ou se endpoint externo é obrigatório

2. **Fluxo Alternativo:**
   - Se endpoint externo não disponível, criar CRDs NSI/NSSI diretamente?
   - Ou retornar erro informativo e não criar nada?

3. **Configuração:**
   - Verificar se variáveis de ambiente do NASP externo estão configuradas
   - Documentar endpoint esperado do NASP externo

## Evidências Coletadas

- ✅ Código-fonte analisado
- ✅ CRDs verificados no cluster
- ✅ Logs analisados
- ✅ OpenAPI documentado
- ✅ Deployment YAML coletado

---

**Status:** ✅ Auditoria completa  
**Próximo passo:** S6.17 - Implementar correção baseada nas descobertas

---

## Descoberta Crítica: Endpoints do NASP Externo

### Endpoints Configurados no Código (modo real):

**RAN:**
- Endpoint: `http://srsenb.srsran.svc.cluster.local:36412`
- Métricas: `http://srsenb.srsran.svc.cluster.local:9092`

**Core (Open5GS):**
- UPF: `http://open5gs-upf.open5gs.svc.cluster.local:8805`
- UPF Métricas: `http://open5gs-upf.open5gs.svc.cluster.local:9090`
- AMF: `http://amf-namf.ns-1274485.svc.cluster.local:80`
- SMF: `http://smf-nsmf.ns-1274485.svc.cluster.local:80`

**Transport:**
- Usa UPF como transport: `http://open5gs-upf.open5gs.svc.cluster.local:8805`

### Modo de Operação:

O código tem dois modos:
1. **Mock** (`NASP_MODE=mock`): Usa endpoints mock para desenvolvimento
2. **Real** (`NASP_MODE=real` ou padrão): Tenta conectar aos endpoints reais do NASP

**Modo atual:** Real (padrão, sem variável NASP_MODE configurada)

### Problema Identificado:

O NASP Adapter está configurado para conectar a serviços do NASP em namespaces específicos:
- `srsran` (para RAN - srsenb)
- `open5gs` (para Core - UPF)
- `ns-1274485` (para Core - AMF/SMF)

Se esses namespaces/serviços não existem ou não são acessíveis, o erro "All connection attempts failed" é esperado.

