# Guia de Preenchimento de values-production.yaml — TriSLA

**Versão:** 1.0  
**Objetivo:** Explicar como preencher corretamente o arquivo `helm/trisla/values-production.yaml` para deploy no NASP

---

## 1. Explicação Conceitual

### 1.1 Papel do values.yaml (Default/Dev)

O arquivo `helm/trisla/values.yaml` contém **valores padrão** para desenvolvimento local e testes. Ele é usado quando:

- Executando `docker-compose.yml` localmente
- Testes E2E em ambiente controlado
- Desenvolvimento de novos módulos

**Características:**
- Valores genéricos e seguros para desenvolvimento
- Endpoints mockados ou locais
- Configurações mínimas de recursos

### 1.2 Papel do values-production.yaml (Produção NASP)

O arquivo `helm/trisla/values-production.yaml` contém **valores específicos** para produção no ambiente NASP. Ele **sobrescreve** valores do `values.yaml` durante o deploy.

**Características:**
- Valores específicos do ambiente NASP
- Endpoints reais descobertos no cluster
- Configurações de recursos otimizadas para produção
- Secrets e credenciais (via Kubernetes Secrets, nunca hardcoded)

### 1.3 Perigos de Subir Valores Genéricos

⚠️ **NUNCA faça commit de `values-production.yaml` com:**

- IPs reais de nodes ou serviços
- Tokens ou credenciais hardcoded
- Endpoints específicos do seu ambiente (use placeholders em documentação)

✅ **SEMPRE:**

- Use placeholders em documentação Markdown
- Armazene valores reais apenas no arquivo YAML local (não versionado)
- Use Kubernetes Secrets para credenciais
- Valide com `helm template` antes do deploy

---

## 2. Tabela de Parâmetros Críticos

| Chave YAML | Descrição | Fonte de Informação | Obrigatório | Exemplo (genérico) |
|------------|-----------|---------------------|-------------|-------------------|
| `global.namespace` | Namespace em que o TriSLA será instalado | Padrão do ambiente NASP | Sim | `trisla` |
| `global.imageRegistry` | Registry de imagens Docker | GHCR configurado | Sim | `ghcr.io/<GHCR_USER>` |
| `semCsmf.service.port` | Porta HTTP do SEM-CSMF | Padrão do Helm / app | Sim | `8080` |
| `mlNsmf.modelPath` | Caminho do modelo de viabilidade ML | Artefatos ML treinados | Sim | `/models/viability_model.pkl` |
| `bcNssmf.besu.rpcUrl` | URL RPC do GoQuorum/Besu | Configuração local do Besu | Sim | `http://<BESU_SERVICE>.<BESU_NS>.svc.cluster.local:8545` |
| `bcNssmf.besu.chainId` | Chain ID da blockchain | Configuração do Besu | Sim | `1337` |
| `naspAdapter.naspEndpoints.ran` | Endpoint base do RAN | Descoberta NASP | Sim | `http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_PORT>` |
| `naspAdapter.naspEndpoints.ran_metrics` | Endpoint de métricas RAN | Descoberta NASP | Sim | `http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_METRICS_PORT>` |
| `naspAdapter.naspEndpoints.core_upf` | Endpoint UPF (Core) | Descoberta NASP | Sim | `http://<UPF_SERVICE>.<CORE_NS>.svc.cluster.local:<UPF_PORT>` |
| `naspAdapter.naspEndpoints.core_upf_metrics` | Endpoint de métricas UPF | Descoberta NASP | Sim | `http://<UPF_SERVICE>.<CORE_NS>.svc.cluster.local:<UPF_METRICS_PORT>` |
| `naspAdapter.naspEndpoints.core_amf` | Endpoint AMF (Core) | Descoberta NASP | Sim | `http://<AMF_SERVICE>.<CORE_NS>.svc.cluster.local:<AMF_PORT>` |
| `naspAdapter.naspEndpoints.core_smf` | Endpoint SMF (Core) | Descoberta NASP | Sim | `http://<SMF_SERVICE>.<CORE_NS>.svc.cluster.local:<SMF_PORT>` |
| `naspAdapter.naspEndpoints.transport` | Endpoint Transport | Descoberta NASP | Sim | `http://<TRANSPORT_SERVICE>.<TRANSPORT_NS>.svc.cluster.local:<TRANSPORT_PORT>` |
| `observability.otlp.endpoint` | Endpoint OTLP Collector | Stack de observabilidade NASP | Sim | `http://<OTLP_SERVICE>.<MONITORING_NS>.svc.cluster.local:4317` |
| `observability.prometheus.endpoint` | Endpoint Prometheus | Stack de observabilidade NASP | Sim | `http://<PROMETHEUS_SERVICE>.<MONITORING_NS>.svc.cluster.local:9090` |
| `network.interface` | Interface de rede NASP | Configuração do cluster | Sim | `my5g` |
| `nodes.node1.ip` | IP do Node1 | Configuração do cluster | Sim | `<NODE1_IP>` |
| `nodes.node2.ip` | IP do Node2 | Configuração do cluster | Sim | `<NODE2_IP>` |
| `network.gateway` | Gateway IP | Configuração do cluster | Sim | `<GATEWAY_IP>` |

---

## 3. Erros Comuns e Como Evitar

### 3.1 Valores Vazios em Campos Obrigatórios

**Problema:**
```yaml
naspAdapter:
  naspEndpoints:
    ran: ""  # ❌ Vazio
```

**Solução:**
- Execute `scripts/discover_nasp_endpoints.sh` para descobrir endpoints
- Use `scripts/fill_values_production.sh` para preenchimento guiado
- Valide com `helm template` antes do deploy

### 3.2 Usar IP Real em Documentação

**Problema:**
```markdown
# ❌ NUNCA faça isso em .md:
Endpoint: http://192.168.10.16:8080
```

**Solução:**
```markdown
# ✅ SEMPRE use placeholders:
Endpoint: http://<RAN_SERVICE>.<RAN_NS>.svc.cluster.local:<RAN_PORT>
```

### 3.3 Não Alinhar Portas com docker-compose ou values.yaml

**Problema:**
- `docker-compose.yml` usa porta `8080`
- `values-production.yaml` usa porta `8081`
- Resultado: Incompatibilidade

**Solução:**
- Mantenha portas consistentes entre dev e produção
- Documente mudanças de porta quando necessário
- Use variáveis de ambiente quando possível

### 3.4 Endpoints com IPs Hardcoded

**Problema:**
```yaml
naspAdapter:
  naspEndpoints:
    ran: "http://192.168.10.16:8080"  # ❌ IP hardcoded
```

**Solução:**
```yaml
naspAdapter:
  naspEndpoints:
    ran: "http://ran-controller.ran-namespace.svc.cluster.local:8080"  # ✅ FQDN Kubernetes
```

**Vantagens do FQDN:**
- Resolução automática via DNS do cluster
- Funciona mesmo se IPs mudarem
- Mais resiliente a mudanças de infraestrutura

### 3.5 Secrets Hardcoded

**Problema:**
```yaml
# ❌ NUNCA faça isso:
secrets:
  ghcr_token: "ghp_xxxxxxxxxxxx"
```

**Solução:**
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
# No node1 do NASP
./scripts/discover_nasp_endpoints.sh
```

### Passo 2: Revisar Relatório

```bash
# Revisar relatório gerado
cat docs/NASP_CONTEXT_REPORT.md
cat tmp/nasp_context_raw.txt
```

### Passo 3: Preencher values-production.yaml

```bash
# Preenchimento guiado
./scripts/fill_values_production.sh
```

Ou manualmente, editando `helm/trisla/values-production.yaml`.

### Passo 4: Validar

```bash
# Validar sintaxe e valores
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-production.yaml \
  --debug
```

### Passo 5: Revisar Antes do Deploy

- ✅ Todos os placeholders substituídos?
- ✅ Nenhum IP real em documentação?
- ✅ Secrets configurados via Kubernetes?
- ✅ Endpoints usando FQDNs?

---

## 5. Exemplo de values-production.yaml Completo

```yaml
# ============================================
# Values para PRODUÇÃO REAL - NASP Node1
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

- **Descoberta de Endpoints:** `scripts/discover_nasp_endpoints.sh`
- **Preenchimento Guiado:** `scripts/fill_values_production.sh`
- **Checklist de Pré-Deploy:** `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`
- **Runbook de Deploy:** `docs/NASP_DEPLOY_RUNBOOK.md`

---

**Versão:** 1.0  
**ENGINE MASTER:** Sistema de Configuração TriSLA


