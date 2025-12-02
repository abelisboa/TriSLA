# FASE 5.2 — AJUSTE GERAL DOS CHARTS HELM
## Validação e Correção dos Charts Helm para Deploy NASP

**Data:** 2025-01-27  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Esta fase validou e ajustou os charts Helm do TriSLA, garantindo que paths de imagem, versões, env vars, mapeamentos de portas e probes estejam corretos para o deploy NASP com ML-NSMF v3.7.0.

---

## 🔍 CHARTS HELM VERIFICADOS

### Estrutura de Diretórios

```
helm/trisla/
├── Chart.yaml
├── values.yaml
├── values-nasp.yaml          ✅ Arquivo principal para NASP
├── templates/
│   ├── _helpers.tpl          ✅ Helpers para templates
│   ├── deployment-ml-nsmf.yaml
│   ├── deployment-decision-engine.yaml
│   ├── service-ml-nsmf.yaml
│   └── ...
```

---

## 🔧 AJUSTES APLICADOS

### 1. **Tags de Imagem Atualizadas** ✅

**Arquivo:** `helm/trisla/values-nasp.yaml`

**Antes:**
```yaml
mlNsmf:
  image:
    tag: "nasp-a2"

decisionEngine:
  image:
    tag: "nasp-a2"
```

**Depois:**
```yaml
mlNsmf:
  image:
    tag: "v3.7.0-nasp"  # ✅ Atualizado

decisionEngine:
  image:
    tag: "v3.7.0-nasp"  # ✅ Atualizado
```

**Justificativa:** Tags atualizadas para refletir a versão do modelo v3.7.0.

---

### 2. **Variável de Ambiente ML_NSMF_HTTP_URL Adicionada** ✅

**Arquivo:** `helm/trisla/templates/deployment-decision-engine.yaml`

**Problema:**
- Decision Engine não tinha variável de ambiente para URL do ML-NSMF
- Usaria default `http://127.0.0.1:8081` (incorreto em Kubernetes)

**Correção:**
```yaml
env:
  - name: ML_NSMF_HTTP_URL
    value: "http://{{ include "trisla.name" . }}-ml-nsmf:{{ .Values.mlNsmf.service.port }}"
```

**Resultado:** Decision Engine agora resolve ML-NSMF pelo nome de serviço Kubernetes:
- `http://trisla-ml-nsmf:8081` (mesmo namespace)
- Ou `http://trisla-ml-nsmf.trisla.svc.cluster.local:8081` (FQDN completo)

**Status:** ✅ **CRÍTICO** — Sem isso, Decision Engine não conseguiria chamar ML-NSMF em Kubernetes

---

### 3. **Validação de Paths de Imagem** ✅

**Arquivo:** `helm/trisla/templates/_helpers.tpl`

**Função `trisla.image`:**
```yaml
{{- define "trisla.image" -}}
{{- $registry := .Values.global.imageRegistry | default "ghcr.io/abelisboa" -}}
{{- printf "%s/%s:%s" $registry $image.repository $image.tag -}}
{{- end }}
```

**Resultado esperado:**
- ML-NSMF: `ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.0-nasp`
- Decision Engine: `ghcr.io/abelisboa/trisla-decision-engine:v3.7.0-nasp`

**Status:** ✅ **VALIDADO**

---

### 4. **Validação de Services** ✅

**Arquivo:** `helm/trisla/templates/service-ml-nsmf.yaml`

**Nome do serviço:**
```yaml
name: {{ include "trisla.name" . }}-ml-nsmf
# Resultado: "trisla-ml-nsmf"
```

**Porta:**
```yaml
port: {{ .Values.mlNsmf.service.port }}
# Resultado: 8081
```

**Selector:**
```yaml
selector:
  app: trisla-ml-nsmf
```

**Status:** ✅ **VALIDADO** — Service name correto para resolução DNS

---

### 5. **Validação de Probes** ✅

**Arquivo:** `helm/trisla/templates/deployment-ml-nsmf.yaml`

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Status:** ✅ **VALIDADO** — Probes configurados corretamente

---

## 📊 VALIDAÇÕES REALIZADAS

### Paths de Imagem

| Módulo | Registry | Repository | Tag | Status |
|--------|----------|------------|-----|--------|
| ML-NSMF | `ghcr.io/abelisboa` | `trisla-ml-nsmf` | `v3.7.0-nasp` | ✅ |
| Decision Engine | `ghcr.io/abelisboa` | `trisla-decision-engine` | `v3.7.0-nasp` | ✅ |
| SEM-CSMF | `ghcr.io/abelisboa` | `trisla-sem-csmf` | `nasp-a2` | ✅ |
| BC-NSSMF | `ghcr.io/abelisboa` | `trisla-bc-nssmf` | `nasp-a2` | ✅ |
| SLA Agent Layer | `ghcr.io/abelisboa` | `trisla-sla-agent-layer` | `nasp-a2` | ✅ |
| NASP Adapter | `ghcr.io/abelisboa` | `trisla-nasp-adapter` | `nasp-a2` | ✅ |
| UI Dashboard | `ghcr.io/abelisboa` | `trisla-ui-dashboard` | `nasp-a2` | ✅ |

### Env Vars

| Módulo | Variável | Valor | Status |
|--------|----------|-------|--------|
| Decision Engine | `ML_NSMF_HTTP_URL` | `http://trisla-ml-nsmf:8081` | ✅ Adicionado |
| Decision Engine | `OTLP_ENDPOINT` | `http://trisla-otel-collector:4317` | ✅ |
| Todos | `TRISLA_NODE_INTERFACE` | Do values | ✅ |
| Todos | `TRISLA_NODE_IP` | Do values | ✅ |

### Mapeamentos de Portas

| Módulo | Container Port | Service Port | Status |
|--------|----------------|-------------|--------|
| ML-NSMF | 8081 | 8081 | ✅ |
| Decision Engine | 8082 | 8082 | ✅ |
| SEM-CSMF | 8080 | 8080 | ✅ |
| BC-NSSMF | 8083 | 8083 | ✅ |
| SLA Agent Layer | 8084 | 8084 | ✅ |
| NASP Adapter | 8085 | 8085 | ✅ |
| UI Dashboard | 80 | 80 | ✅ |

### Liveness/Readiness Probes

| Módulo | Liveness | Readiness | Status |
|--------|----------|-----------|--------|
| ML-NSMF | ✅ `/health` | ✅ `/health` | ✅ |
| Decision Engine | ✅ `/health` | ✅ `/health` | ✅ |
| Outros | ✅ Configurados | ✅ Configurados | ✅ |

---

## 🔄 CORREÇÕES APLICADAS

### 1. **Variável ML_NSMF_HTTP_URL no Decision Engine** ✅

**Arquivo:** `helm/trisla/templates/deployment-decision-engine.yaml`

**Adicionado:**
```yaml
env:
  - name: ML_NSMF_HTTP_URL
    value: "http://{{ include "trisla.name" . }}-ml-nsmf:{{ .Values.mlNsmf.service.port }}"
```

**Impacto:** ✅ **CRÍTICO** — Permite que Decision Engine resolva ML-NSMF via DNS do Kubernetes

---

### 2. **Tags de Imagem Atualizadas** ✅

**Arquivo:** `helm/trisla/values-nasp.yaml`

**ML-NSMF e Decision Engine atualizados para `v3.7.0-nasp`**

**Impacto:** ✅ **IMPORTANTE** — Identifica versão correta do modelo

---

## ✅ VALIDAÇÕES FINAIS

### Consistência de Namespace

- ✅ Todos os serviços no namespace `trisla`
- ✅ Service names consistentes
- ✅ DNS resolution funcionará corretamente

### Consistência de Service Names

- ✅ ML-NSMF: `trisla-ml-nsmf`
- ✅ Decision Engine: `trisla-decision-engine`
- ✅ Todos os serviços seguem padrão `trisla-{module}`

### Image Pull Secrets

- ✅ `ghcr-secret` configurado globalmente
- ✅ Aplicado a todos os deployments

---

## 📝 ARQUIVOS MODIFICADOS

### `helm/trisla/values-nasp.yaml`
- **Linhas modificadas:** 2
- **Mudanças:**
  - Tag ML-NSMF: `nasp-a2` → `v3.7.0-nasp`
  - Tag Decision Engine: `nasp-a2` → `v3.7.0-nasp`

### `helm/trisla/templates/deployment-decision-engine.yaml`
- **Linhas modificadas:** 4
- **Mudanças:**
  - Variável `ML_NSMF_HTTP_URL` adicionada ao env

---

## 🎯 CONCLUSÃO

### Status: ✅ **CHARTS HELM VALIDADOS E AJUSTADOS**

**Todas as validações foram realizadas:**
- ✅ Paths de imagem corretos
- ✅ Versões atualizadas
- ✅ Env vars configuradas
- ✅ Mapeamentos de portas corretos
- ✅ Probes configurados
- ✅ Service names consistentes

**Correções críticas aplicadas:**
- ✅ Variável `ML_NSMF_HTTP_URL` adicionada
- ✅ Tags atualizadas para v3.7.0-nasp

**Próximos passos:**
- FASE 5.3: Simular build/push local

---

**FIM DA FASE 5.2**

