# guide de Preenchimento de values-nasp.yaml — TriSLA

**Versão:** 1.0  
**Objective:** Explicar como preencher corretamente o arquivo `helm/trisla/values-nasp.yaml` for deploy no NASP

---

## 1. Explicação Conceitual

### 1.1 Papel of values.yaml (Default/Dev)

O arquivo `helm/trisla/values.yaml` contém **valores padrão** for development local e testes. Ele is usado quando:

- Executando `docker-compose.yml` localmente
- Testes E2E in environment controlado
- development de novos módulos

**Características:**
- Valores genéricos e seguros for development
- Endpoints mockados ou locais
- Minimum configurations de recursos

### 1.2 Papel of values-nasp.yaml (production NASP)

O arquivo `helm/trisla/values-nasp.yaml` contém **valores específicos** for production no environment NASP. Ele **sobrescreve** valores of `values.yaml` durante o deploy.

**Características:**
- Valores específicos of environment NASP
- Endpoints reais descobertos no cluster
- Resource configurations otimizadas for production
- Secrets e credenciais (via Kubernetes Secrets, nunca hardcoded)

### 1.3 Perigos de Subir Valores Genéricos

⚠️ **NUNCA faça commit de `values-nasp.yaml` com:**

- IPs reais de nodes ou serviços
- Tokens ou credenciais hardcoded
- Endpoints específicos of seu environment (use placeholders in documentação)

✅ **SEMPRE:**

- Use placeholders in documentação Markdown
- Armazene valores reais apenas no arquivo YAML local (não versionado)
- Use Kubernetes Secrets for credenciais
- Valide com `helm template` antes of deploy

---

## 2. table de Parâmetros Críticos

| Chave YAML | description | Fonte de Informação | Obrigatório | Exemplo (genérico) |
|------------|-----------|---------------------|-------------|-------------------|
| `global.namespace` | Namespace in que o TriSLA será instalado | Padrão of environment NASP | Sim | `trisla` |
| `global.imageRegistry` | Registry de imagens Docker | GHCR configured | Sim | `ghcr.io/<GHCR_USER>` |
| `semCsmf.service.port` | Porta HTTP of SEM-CSMF | Padrão of Helm / app | Sim | `8080` |
| `mlNsmf.modelPath` | Caminho of modelo de viabilidade ML | Artefatos ML treinados | Sim | `/models/viability_model.pkl` |
| `bcNssmf.besu.rpcUrl` | URL RPC of GoQuorum/Besu | Configuration local of Besu | Sim | `http://<BESU_SERVICE>.<BESU_NS>.svc.cluster.local:8545` |
| `bcNssmf.besu.chainId` | Chain ID of blockchain | Besu Configuration | Sim | `1337` |
| `naspAdapter.naspEndpoints.ran` | Endpoint base of RAN | Descoberta NASP | Sim | `http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_PORT>` |
| `naspAdapter.naspEndpoints.ran_metrics` | Endpoint de metrics RAN | Descoberta NASP | Sim | `http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_METRICS_PORT>` |
| `naspAdapter.naspEndpoints.core_upf` | Endpoint UPF (Core) | Descoberta NASP | Sim | `http://<UPF_SERVICE>.<CORE_NS>.svc.cluster.local:<UPF_PORT>` |
| `naspAdapter.naspEndpoints.core_upf_metrics` | Endpoint de metrics UPF | Descoberta NASP | Sim | `http://<UPF_SERVICE>.<CORE_NS>.svc.cluster.local:<UPF_METRICS_PORT>` |
| `naspAdapter.naspEndpoints.core_amf` | Endpoint AMF (Core) | Descoberta NASP | Sim | `http://<AMF_SERVICE>.<CORE_NS>.svc.cluster.local:<AMF_PORT>` |
| `naspAdapter.naspEndpoints.core_smf` | Endpoint SMF (Core) | Descoberta NASP | Sim | `http://<SMF_SERVICE>.<CORE_NS>.svc.cluster.local:<SMF_PORT>` |
| `naspAdapter.naspEndpoints.transport` | Endpoint Transport | Descoberta NASP | Sim | `http://<TRANSPORT_SERVICE>.<TRANSPORT_NS>.svc.cluster.local:<TRANSPORT_PORT>` |
| `observability.otlp.endpoint` | Endpoint OTLP Collector | Stack de observabilidade NASP | Sim | `http://<OTLP_SERVICE>.<MONITORING_NS>.svc.cluster.local:4317` |
| `observability.prometheus.endpoint` | Endpoint Prometheus | Stack de observabilidade NASP | Sim | `http://<PROMETHEUS_SERVICE>.<MONITORING_NS>.svc.cluster.local:9090` |
| `network.interface` | Interface de rede NASP | Cluster Configuration | Sim | `my5g` |
| `nodes.node1.ip` | IP of Node1 | Cluster Configuration | Sim | `<NODE1_IP>` |
| `nodes.node2.ip` | IP of Node2 | Cluster Configuration | Sim | `<NODE2_IP>` |
| `network.gateway` | Gateway IP | Cluster Configuration | Sim | `<GATEWAY_IP>` |

---

## 3. Erros Comuns e Como Evitar

### 3.1 Valores Vazios in Campos Obrigatórios

**problem:**
```yaml
naspAdapter:
  naspEndpoints:
    ran: ""  # ❌ Vazio
```

**solution:**
- Execute `scripts/discover-nasp-endpoints.sh` for descobrir endpoints
- Use `scripts/fill_values_production.sh` for preenchimento guiado
- Valide com `helm template` antes of deploy

### 3.2 Usar IP Real in Documentação

**problem:**
```markdown
# ❌ NUNCA faça isso in .md:
Endpoint: http://192.168.10.16:8080
```

**solution:**
```markdown
# ✅ SEMPRE use placeholders:
Endpoint: http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_PORT>
```

### 3.3 Não Alinhar Portas com docker-compose ou values.yaml

**problem:**
- `docker-compose.yml` usa porta `8080`
- `values-nasp.yaml` usa porta `8081`
- Resultado: Incompatibilidade

**solution:**
- Mantenha portas consistentes entre dev e production
- Documente mudanças de porta quando necessário
- Use variables de environment quando possível

### 3.4 Endpoints com IPs Hardcoded

**problem:**
```yaml
naspAdapter:
  naspEndpoints:
    ran: "http://192.168.10.16:8080"  # ❌ IP hardcoded
```

**solution:**
```yaml
naspAdapter:
  naspEndpoints:
    ran: "http://ran-controller.ran-namespace.svc.cluster.local:8080"  # ✅ FQDN Kubernetes
```

**Vantagens of FQDN:**
- Resolution automática via DNS of cluster
- Funciona mesmo se IPs mudarem
- Mais resiliente a mudanças de infraestrutura

### 3.5 Secrets Hardcoded

**problem:**
```yaml
# ❌ NUNCA faça isso:
secrets:
  ghcr_token: "ghp_xxxxxxxxxxxx"
```

**solution:**
```yaml
# ✅ Use Kubernetes Secrets:
secrets:
  ghcr_token:
    secretName: ghcr-secret
    secretKey: password
```

E crie o secret separadamente:
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GHCR_USER> \
  --docker-password=<GHCR_TOKEN> \
  --namespace=trisla
```

---

## 4. Fluxo Recomendado de Preenchimento

### Passo 1: Descobrir Endpoints

```bash
# No node1 of NASP
./scripts/discover-nasp-endpoints.sh
```

### Passo 2: Revisar Relatório

```bash
# Revisar relatório gerado
cat docs/NASP_CONTEXT_REPORT.md
cat tmp/nasp_context_raw.txt
```

### Passo 3: Preencher values-nasp.yaml

```bash
# Preenchimento guiado
./scripts/fill_values_production.sh
```

Ou manualmente, editando `helm/trisla/values-nasp.yaml`.

### Passo 4: Validar

```bash
# Validar sintaxe e valores
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

### Passo 5: Revisar Antes of Deploy

- ✅ Todos os placeholders substituídos?
- ✅ Nenhum IP real in documentação?
- ✅ Secrets configurados via Kubernetes?
- ✅ Endpoints usando FQDNs?

---

## 5. Exemplo de values-nasp.yaml Completo

```yaml
# ============================================
# Values for production REAL - NASP Node1
# ============================================

global:
  namespace: trisla
  imageRegistry: ghcr.io/<GHCR_USER>

# Network Configuration
network:
  interface: my5g
  gateway: <GATEWAY_IP>

nodes:
  node1:
    ip: <NODE1_IP>
    interface: my5g
  node2:
    ip: <NODE2_IP>
    interface: my5g

# NASP Adapter Endpoints
naspAdapter:
  naspEndpoints:
    ran: "http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_PORT>"
    ran_metrics: "http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_METRICS_PORT>"
    core_upf: "http://<UPF_SERVICE>.<CORE_NS>.svc.cluster.local:<UPF_PORT>"
    core_upf_metrics: "http://<UPF_SERVICE>.<CORE_NS>.svc.cluster.local:<UPF_METRICS_PORT>"
    core_amf: "http://<AMF_SERVICE>.<CORE_NS>.svc.cluster.local:<AMF_PORT>"
    core_smf: "http://<SMF_SERVICE>.<CORE_NS>.svc.cluster.local:<SMF_PORT>"
    transport: "http://<TRANSPORT_SERVICE>.<TRANSPORT_NS>.svc.cluster.local:<TRANSPORT_PORT>"

# Blockchain Configuration
bcNssmf:
  besu:
    rpcUrl: "http://<BESU_SERVICE>.<BESU_NS>.svc.cluster.local:8545"
    chainId: 1337

# Observability
observability:
  otlp:
    endpoint: "http://<OTLP_SERVICE>.<MONITORING_NS>.svc.cluster.local:4317"
  prometheus:
    endpoint: "http://<PROMETHEUS_SERVICE>.<MONITORING_NS>.svc.cluster.local:9090"

# Production Settings
production:
  enabled: true
  simulationMode: false
  useRealServices: true
  executeRealActions: true
```

---

## 6. Referências

- **Descoberta de Endpoints:** `scripts/discover-nasp-endpoints.sh`
- **Preenchimento Guiado:** `scripts/fill_values_production.sh`
- **Checklist de Pré-Deploy:** `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`
- **Runbook de Deploy:** `docs/NASP_DEPLOY_RUNBOOK.md`

---

**Versão:** 1.0  
**ENGINE MASTER:** Sistema de Configuration TriSLA


