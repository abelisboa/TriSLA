# Helm Chart Architecture — TriSLA

**Versão:** v3.7.16 (Sprint S3.4 - Modular e Idempotente)  
**Data:** 2025-12-17  
**Chart:** `helm/trisla`

## 1. Princípios de Modularidade

### 1.1 Regra de Ouro

**Nenhum template Helm pode ser renderizado se o componente estiver desabilitado.**

Isso significa que TODO template deve respeitar:

```yaml
{{- if .Values.<component>.enabled }}
...
{{- end }}
```

**Sem exceções.**

### 1.2 Isolamento Funcional

Cada componente do TriSLA pode ser habilitado ou desabilitado de forma independente:

- **Besu** - Infraestrutura blockchain
- **BC-NSSMF** - Blockchain Network Slice Subnet Management Function
- **SEM-CSMF** - Semantic Communication Service Management Function
- **ML-NSMF** - Machine Learning Network Slice Management Function
- **Decision Engine** - Motor de decisão SLA-aware
- **SLA-Agent Layer** - Camada de agente SLA
- **NASP Adapter** - Adaptador NASP
- **UI Dashboard** - Dashboard de interface

### 1.3 Renderização Condicional

Todos os recursos Kubernetes (Deployment, Service, ConfigMap, PVC, Ingress) são protegidos por guard clauses:

```yaml
{{- if .Values.besu.enabled }}
apiVersion: apps/v1
kind: Deployment
...
{{- end }}
```

## 2. Tabela de Componentes vs Flags

| Componente | Flag | Templates Afetados |
|---|---|---|
| Besu | `besu.enabled` | `deployment-besu.yaml`, `service-besu.yaml`, `configmap-besu.yaml`, `pvc-besu.yaml` |
| BC-NSSMF | `bcNssmf.enabled` | `deployment-bc-nssmf.yaml`, `service-bc-nssmf.yaml` |
| SEM-CSMF | `semCsmf.enabled` | `deployment-sem-csmf.yaml`, `service-sem-csmf.yaml` |
| ML-NSMF | `mlNsmf.enabled` | `deployment-ml-nsmf.yaml`, `service-ml-nsmf.yaml` |
| Decision Engine | `decisionEngine.enabled` | `deployment-decision-engine.yaml`, `service-decision-engine.yaml` |
| SLA-Agent Layer | `slaAgentLayer.enabled` | `deployment-sla-agent-layer.yaml`, `service-sla-agent-layer.yaml` |
| NASP Adapter | `naspAdapter.enabled` | `deployment-nasp-adapter.yaml`, `service-nasp-adapter.yaml`, `nasp-adapter-rbac.yaml` |
| UI Dashboard | `uiDashboard.enabled` | `deployment-ui-dashboard.yaml`, `service-ui-dashboard.yaml` |

## 3. Estratégia de Idempotência

### 3.1 Valores Padrão Obrigatórios

Todos os componentes têm valores padrão em `values.yaml`:

```yaml
besu:
  enabled: false  # Base idempotente
  service:
    port: 8545

bcNssmf:
  enabled: false  # Base idempotente
  env:
    BC_ENABLED: "true"  # Valor padrão obrigatório

semCsmf:
  enabled: false  # Base idempotente
  env:
    DECISION_ENGINE_URL: ""  # Valor padrão obrigatório
```

**Nenhum campo obrigatório pode ficar sem valor default, mesmo vazio.**

### 3.2 Eliminação de Nil Pointer Errors

**❌ Errado:**
```yaml
value: {{ .Values.semCsmf.env.DECISION_ENGINE_URL }}
```

**✅ Correto:**
```yaml
{{- if and .Values.semCsmf.enabled .Values.semCsmf.env .Values.semCsmf.env.DECISION_ENGINE_URL }}
- name: DECISION_ENGINE_URL
  value: {{ .Values.semCsmf.env.DECISION_ENGINE_URL | quote }}
{{- end }}
```

### 3.3 Dependências Explícitas

- **BC-NSSMF → Besu:** `TRISLA_RPC_URL` injetada quando `besu.enabled=true`
- **SEM-CSMF → Decision Engine:** `DECISION_ENGINE_URL` configurável via `semCsmf.env.DECISION_ENGINE_URL`
- **Nenhuma dependência implícita:** Todos os valores são explícitos

## 4. Exemplo de Deploy Isolado

### 4.1 Deploy apenas Besu

```bash
helm install trisla helm/trisla \
  --set besu.enabled=true \
  --set bcNssmf.enabled=false \
  --set semCsmf.enabled=false \
  --set mlNsmf.enabled=false \
  --set decisionEngine.enabled=false
```

**Resultado:** Apenas recursos do Besu são criados (Deployment, Service, ConfigMap, PVC).

### 4.2 Deploy apenas BC-NSSMF

```bash
helm install trisla helm/trisla \
  --set besu.enabled=false \
  --set bcNssmf.enabled=true \
  --set semCsmf.enabled=false \
  --set mlNsmf.enabled=false \
  --set decisionEngine.enabled=false
```

**Resultado:** Apenas recursos do BC-NSSMF são criados (Deployment, Service, RBAC).

### 4.3 Deploy stack completo

```bash
helm install trisla helm/trisla \
  --set besu.enabled=true \
  --set bcNssmf.enabled=true \
  --set semCsmf.enabled=true \
  --set mlNsmf.enabled=true \
  --set decisionEngine.enabled=true
```

**Resultado:** Todos os componentes habilitados são criados.

## 5. Garantia de Compatibilidade Multi-Cluster

### 5.1 Idempotência Total

- **Helm install/uninstall/reinstall:** Sem efeitos colaterais
- **Templates idempotentes:** Mesmos valores geram mesmos manifests
- **Sem dependências de ordem:** Componentes podem ser habilitados em qualquer ordem

### 5.2 Validação Local

```bash
# Validar sintaxe
helm lint helm/trisla

# Validar renderização isolada
helm template trisla helm/trisla --set besu.enabled=true --set bcNssmf.enabled=false

# Validar stack completo
helm template trisla helm/trisla --set besu.enabled=true --set bcNssmf.enabled=true
```

### 5.3 Nenhum Ajuste Manual Necessário

- ✅ Chart renderiza corretamente qualquer combinação
- ✅ Nenhum nil pointer error
- ✅ Nenhuma dependência implícita
- ✅ Repositório pronto para NASP e outros clusters

## 6. Estrutura do Chart

```
helm/trisla/
├── Chart.yaml          # Metadados do chart
├── values.yaml          # Valores padrão (base idempotente)
└── templates/
    ├── deployment-*.yaml    # Deployments (todos com guard clauses)
    ├── service-*.yaml       # Services (todos com guard clauses)
    ├── configmap-*.yaml     # ConfigMaps (todos com guard clauses)
    ├── pvc-*.yaml           # PersistentVolumeClaims (todos com guard clauses)
    ├── ingress.yaml         # Ingress (com guard clause)
    ├── namespace.yaml       # Namespace
    ├── secret-ghcr.yaml    # Secret para GHCR
    └── nasp-adapter-rbac.yaml  # RBAC para NASP Adapter (com guard clause)
```

## 7. Consolidação Sprint S3.4

### 7.1 Correções Aplicadas

**Guard Clauses:**
- ✅ Todos os templates Deployment têm `{{- if .Values.<component>.enabled }}`
- ✅ Todos os templates Service têm `{{- if .Values.<component>.enabled }}`
- ✅ Todos os templates ConfigMap têm `{{- if .Values.<component>.enabled }}`
- ✅ Todos os templates PVC têm `{{- if .Values.<component>.enabled }}`

**Valores Padrão:**
- ✅ Todos os componentes têm `enabled: false` por padrão (base idempotente)
- ✅ Campos obrigatórios têm valores padrão (mesmo vazios)
- ✅ `semCsmf.env.DECISION_ENGINE_URL: ""` (valor padrão obrigatório)
- ✅ `bcNssmf.env.BC_ENABLED: "true"` (valor padrão obrigatório)

**Chart.yaml:**
- ✅ Dependências fantasmas removidas (trisla-besu comentado)

### 7.2 Validação

**Helm Lint:**
```bash
helm lint helm/trisla
# Resultado: 1 chart(s) linted, 0 chart(s) failed
```

**Helm Template (isolado):**
```bash
# Besu isolado
helm template trisla helm/trisla --set besu.enabled=true --set bcNssmf.enabled=false
# ✅ Gera apenas recursos do Besu

# BC-NSSMF isolado
helm template trisla helm/trisla --set besu.enabled=false --set bcNssmf.enabled=true
# ✅ Gera apenas recursos do BC-NSSMF
```

**Helm Template (stack completo):**
```bash
helm template trisla helm/trisla \
  --set besu.enabled=true \
  --set bcNssmf.enabled=true \
  --set semCsmf.enabled=true \
  --set mlNsmf.enabled=true \
  --set decisionEngine.enabled=true
# ✅ Gera todos os recursos habilitados (20+ recursos)
```

## 8. Estado Final (Sprint S3.4)

### 8.1 Garantias

- ✅ **Modularidade total:** Cada componente pode ser habilitado/desabilitado independentemente
- ✅ **Renderização condicional correta:** Todos os templates têm guard clauses
- ✅ **Eliminação definitiva de nil pointer errors:** Valores padrão obrigatórios
- ✅ **Idempotência total do Helm:** Install/uninstall/reinstall sem efeitos colaterais
- ✅ **Isolamento funcional:** Nenhum componente interfere em outro
- ✅ **Base sólida para qualquer rede/cluster futuro:** Compatibilidade multi-cluster garantida

### 8.2 Evidências

- ✅ `helm lint` sem erros
- ✅ `helm template` funcional para qualquer combinação
- ✅ Nenhum nil pointer
- ✅ Nenhuma dependência implícita
- ✅ Repositório pronto para NASP e outros clusters

## 9. Infraestrutura Besu (Sprint S3.5.1)

### 9.1 Configuração do Besu

**Versão:** `23.10.1` (compatível com Besu ≥ 23.x)

**Flags Válidas (mínimo funcional - Sprint S3.5.4):**
```yaml
args:
  - --data-path=/opt/besu/data
  - --network=dev
  - --rpc-http-enabled=true
  - --rpc-http-host=0.0.0.0
  - --rpc-http-port=8545
  - --rpc-http-api=ETH,NET,WEB3
  - --rpc-http-cors-origins=*
  - --host-allowlist=*
```

**❌ Removido (Sprint S3.5.4):**
- `--genesis-file` (usando --network=dev sem genesis customizado)

**❌ Flags Obsoletas Removidas:**
- `--miner-enabled` (não necessário em dev network)
- `--miner-coinbase` (não necessário)
- `--miner-extra-data` (não necessário)

**Opinião técnica:** Este modo é suficiente para RPC funcional, deploy de contrato e testes on-chain no NASP.

### 9.2 Estratégia de Probes (Sprint S3.5.5 - Correção Definitiva)

**Probes httpGet Nativo Kubernetes:**

As probes usam `httpGet` nativo do Kubernetes, sem dependências no container:

```yaml
readinessProbe:
  httpGet:
    path: /
    port: 8545
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 6

livenessProbe:
  httpGet:
    path: /
    port: 8545
  initialDelaySeconds: 60
  periodSeconds: 20
  timeoutSeconds: 5
  failureThreshold: 6
```

**❌ Removido (Sprint S3.5.5):**
- Probes baseadas em `exec` com `curl` (imagem oficial Besu não contém curl)
- Dependências externas no container

**✅ Benefícios:**
- Portabilidade total (sem dependências no container)
- Elimina CrashLoopBackOff causado por "curl: not found"
- Usa recursos nativos do Kubernetes
- Besu responde HTTP 200 quando RPC está pronto

### 9.3 Labels e Selectors Consistentes

Todos os recursos do Besu compartilham o mesmo conjunto de labels:

```yaml
labels:
  app: besu
  component: blockchain
  app.kubernetes.io/component: besu
```

**Validado em:**
- Deployment (Pod template)
- Service (selector)
- ConfigMap
- PVC

**❗ Service selector deve bater exatamente com o Pod.**

### 9.4 Service Besu

O Service expõe corretamente o RPC na porta 8545:

```yaml
ports:
  - name: rpc
    port: 8545
    targetPort: 8545
    protocol: TCP
```

**Selector corresponde exatamente ao Deployment:**
```yaml
selector:
  app: besu
  component: blockchain
```

### 9.5 Garantia de Compatibilidade com Besu ≥ 23.x

- ✅ Flags atualizadas para versões atuais do Besu
- ✅ Nenhuma flag obsoleta presente
- ✅ Probes httpGet nativo Kubernetes (sem dependências no container)
- ✅ Service e selectors consistentes
- ✅ Container Besu inicializa corretamente

### 9.6 Correções Aplicadas (Sprint S3.5.1 - S3.5.5)

**Sprint S3.5.1:**
- ✅ Remoção definitiva de flags obsoletas (`--miner-enabled`, `--miner-coinbase`, `--miner-extra-data`)
- ✅ Labels e selectors consolidados em todos os recursos
- ✅ Service expõe corretamente porta 8545
- ✅ Values.yaml com defaults idempotentes (`enabled: false`)

**Sprint S3.5.4:**
- ✅ Remoção de `--genesis-file` e ConfigMap de genesis
- ✅ Besu em modo DEV (`--network=dev`) sem genesis customizado
- ✅ Elimina CrashLoopBackOff por genesis.json

**Sprint S3.5.5:**
- ✅ Probes `exec` com `curl` removidas (imagem Besu não contém curl)
- ✅ Probes substituídas por `httpGet` nativo Kubernetes
- ✅ Elimina CrashLoopBackOff por "curl: not found"
- ✅ Portabilidade total (sem dependências no container)

**Validação:**
- ✅ Helm lint passa sem erros
- ✅ Helm template isolado do Besu funciona
- ✅ Nenhum curl nos templates renderizados
- ✅ Nenhum exec nos probes do Besu

## 10. Sprint S3.5.5 — Correção Definitiva dos Probes do Besu

### 10.1 Problema Identificado

**Erro no NASP:**
```
Readiness probe failed: /bin/sh: curl: not found
```

**Causa raiz:**
- Imagem oficial `hyperledger/besu:*` não contém `curl`
- Probes baseadas em `exec` + `curl` são inválidas
- Causa CrashLoopBackOff mesmo com Besu funcional

### 10.2 Solução Aplicada

**Probes httpGet Nativo Kubernetes:**
- ✅ Removidos todos os probes baseados em `exec` com `curl`
- ✅ Substituídos por `httpGet` nativo do Kubernetes
- ✅ Path: `/` (raiz do RPC HTTP)
- ✅ Port: `8545` (porta RPC)
- ✅ Sem dependências no container

**Benefícios:**
- ✅ Elimina CrashLoopBackOff por "curl: not found"
- ✅ Portabilidade total (sem dependências externas)
- ✅ Usa recursos nativos do Kubernetes
- ✅ Helm Chart 100% idempotente

### 10.3 Validação

**Helm Lint:**
```bash
helm lint helm/trisla
# Resultado: 1 chart(s) linted, 0 chart(s) failed
```

**Helm Template:**
```bash
helm template trisla helm/trisla --set besu.enabled=true
# ✅ Nenhum curl nos templates renderizados
# ✅ Nenhum exec nos probes do Besu
# ✅ Apenas httpGet presente
```

## 11. Próximos Passos

O Helm Chart está consolidado e pronto para:
- ✅ Deploy idempotente em qualquer cluster Kubernetes
- ✅ Eliminação de hotfixes manuais
- ✅ Reprodutibilidade completa da arquitetura
- ✅ Novos ambientes (clusters) sem correções ad-hoc
- ✅ Besu funcional e estável (Sprint S3.5.5)
- ✅ Probes portáveis (sem dependências no container)

