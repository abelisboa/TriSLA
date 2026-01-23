# TriSLA Deployment Guide – NASP Edition (Produção)

**Versão:** 3.5.0  
**Data:** 2025-01-27  
**Ambiente:** NASP (Network Automation & Slicing Platform)  
**Tipo:** Deploy Manual via Ansible  
**Status:** Documento Oficial de Produção

---

## 📋 Sumário Executivo

This document provides instruções completas, formais e acadêmicas para a implantação manual do **TriSLA (Trustworthy, Reasoned, Intelligent SLA)** no ambiente **NASP (Network Automation & Slicing Platform)**, utilizando **Ansible** para automação e **Helm** para gerenciamento de pacotes Kubernetes.

### Objective

O presente guia documenta o processo completo de deploy do TriSLA v3.5.0 em ambiente de produção real no NASP, cobrindo desde a preparação inicial até a validação end-to-end (E2E) do sistema.

### Escopo

- **Ambiente:** Cluster Kubernetes NASP (2 nodes: node1 e node2)
- **Method:** Deploy local no node1 (127.0.0.1), sem SSH
- **Ferramentas:** Ansible, Helm, kubectl
- **Namespace:** `trisla`
- **Release Helm:** `trisla`
- **Values File:** `helm/trisla/values-nasp.yaml`

### Pré-requisitos

- Acesso administrativo ao cluster NASP
- Execução local no node1 (sem SSH)
- `kubectl` configurado e conectado ao cluster
- `helm` instalado (versão ≥ 3.12)
- `ansible` instalado (versão ≥ 2.14)
- Acesso ao GHCR configurado (token e secret criado)

---

## 1. Informações do Ambiente NASP

### 1.1 Configuração de Rede

| Componente | Valor | Description |
|------------|-------|-----------|
| **Interface Main** | `my5g` | Interface de rede física do NASP |
| **Node1 IP** | `192.168.10.16` | IP do node1 (control plane + worker) |
| **Node2 IP** | `192.168.10.15` | IP do node2 (control plane + worker) |
| **Gateway** | `192.168.10.1` | Gateway padrão da rede |
| **Conexão Ansible** | `local` | Execução local (127.0.0.1), sem SSH |

### 1.2 Cluster Kubernetes

| Componente | Valor | Description |
|------------|-------|-----------|
| **Versão Kubernetes** | ≥ 1.26 | Versão mínima requerida |
| **CNI** | Calico | Container Network Interface |
| **Instalação** | Kubespray | Ferramenta de instalação |
| **Control Plane** | HA (2 nodes) | Alta disponibilidade |
| **StorageClass** | `local-path` ou `nfs` | Provisionamento de volumes |

### 1.3 Observabilidade NASP

| Componente | Namespace | Tipo | Description |
|------------|-----------|------|-----------|
| **Prometheus** | `monitoring` | ClusterIP/NodePort | Coleta de métricas |
| **Grafana** | `monitoring` | ClusterIP | Visualização de métricas |
| **Alertmanager** | `monitoring` | ClusterIP | Gerenciamento de alertas |
| **Loki** | `monitoring` | ClusterIP | Sistema de logs (se disponível) |

---

## 2. Arquitetura TriSLA Integrada ao NASP

### 2.1 Visão Geral da Arquitetura

O TriSLA é composto por **7 módulos principais** que se integram ao ambiente NASP:

1. **SEM-CSMF** — Interpretação Semântica
2. **ML-NSMF** — Predição ML com XAI
3. **BC-NSSMF** — Registro Blockchain
4. **Decision Engine** — Motor de Decisão
5. **SLA-Agent Layer** — Agentes Federados (RAN/Transport/Core)
6. **NASP Adapter** — Adaptador NASP
7. **UI Dashboard** — Interface Web

### 2.2 Módulo 1: SEM-CSMF (Semantic-enhanced Communication Service Management Function)

#### Objective Técnico

O SEM-CSMF é responsável por receber intents de alto nível, validá-los semanticamente usando uma ontologia OWL, processá-los com NLP e gerar NESTs (Network Slice Templates) para provisionamento de network slices.

#### Configuração de Deploy

| Parâmetro | Valor | Description |
|-----------|-------|-----------|
| **Namespace** | `trisla` | Namespace do TriSLA |
| **Tipo de Deploy** | `Deployment` | Deployment Kubernetes |
| **Replicas** | `3` | Alta disponibilidade |
| **Port HTTP** | `8080` | Porta REST API |
| **Port gRPC** | `50051` | Porta gRPC (I-01) |
| **Image** | `ghcr.io/abelisboa/trisla-sem-csmf:3.5.0` | Imagem Docker |
| **Node Affinity** | `node1, node2` | Pode rodar em ambos os nodes |

#### Recursos

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

#### Secrets Necessários

- `ghcr-secret` — Autenticação GHCR
- `postgres-secret` — Credenciais PostgreSQL (se aplicável)

#### ConfigMaps

- `trisla-config` — Configurações gerais
- `ontology-config` — Configurações da ontologia

#### PVCs

- `sem-csmf-data` — Dados persistentes (se aplicável)

#### Dependências

- **PostgreSQL** — Persistência de intents e NESTs
- **Kafka** — Comunicação com ML-NSMF (I-02)
- **Decision Engine** — Comunicação gRPC (I-01)
- **OpenTelemetry Collector** — Observabilidade

#### Interfaces Utilizadas

- **I-01 (gRPC):** SEM-CSMF → Decision Engine
- **I-02 (Kafka):** SEM-CSMF → ML-NSMF

#### Documentação

- **Guia Completo:** `docs/sem-csmf/SEM_CSMF_COMPLETE_GUIDE.md`
- **Ontologia:** `docs/sem-csmf/ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`

---

### 2.3 Módulo 2: ML-NSMF (Machine Learning Network Slice Management Function)

#### Objective Técnico

O ML-NSMF é responsável por prever a viabilidade de SLA de network slices usando modelos de machine learning (LSTM/GRU) e fornecer explicações usando XAI (SHAP/LIME).

#### Configuração de Deploy

| Parâmetro | Valor | Description |
|-----------|-------|-----------|
| **Namespace** | `trisla` | Namespace do TriSLA |
| **Tipo de Deploy** | `Deployment` | Deployment Kubernetes |
| **Replicas** | `3` | Alta disponibilidade |
| **Port HTTP** | `8081` | Porta REST API |
| **Image** | `ghcr.io/abelisboa/trisla-ml-nsmf:3.5.0` | Imagem Docker |
| **Node Affinity** | `node1, node2` | Pode rodar em ambos os nodes |

#### Recursos

```yaml
resources:
  requests:
    cpu: 2000m
    memory: 2Gi
  limits:
    cpu: 8000m
    memory: 8Gi
```

#### Secrets Necessários

- `ghcr-secret` — Autenticação GHCR

#### ConfigMaps

- `trisla-config` — Configurações gerais
- `ml-model-config` — Configurações do modelo ML

#### PVCs

- `ml-nsmf-models` — Modelos ML persistentes

#### Dependências

- **Kafka** — Comunicação com SEM-CSMF (I-02) e Decision Engine (I-03)
- **OpenTelemetry Collector** — Observabilidade

#### Interfaces Utilizadas

- **I-02 (Kafka):** SEM-CSMF → ML-NSMF
- **I-03 (Kafka):** ML-NSMF → Decision Engine

#### Documentação

- **Guia Completo:** `docs/ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md`

---

### 2.4 Módulo 3: BC-NSSMF (Blockchain Network Slice Service Management Function)

#### Objective Técnico

O BC-NSSMF é responsável por registrar SLAs em blockchain (Hyperledger Besu/GoQuorum) usando smart contracts Solidity, garantindo imutabilidade e auditabilidade.

#### Configuração de Deploy

| Parâmetro | Valor | Description |
|-----------|-------|-----------|
| **Namespace** | `trisla` | Namespace do TriSLA |
| **Tipo de Deploy** | `Deployment` | Deployment Kubernetes |
| **Replicas** | `2` | Alta disponibilidade |
| **Port HTTP** | `8083` | Porta REST API |
| **Image** | `ghcr.io/abelisboa/trisla-bc-nssmf:3.5.0` | Imagem Docker |
| **Node Affinity** | `node1, node2` | Pode rodar em ambos os nodes |

#### Recursos

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

#### Secrets Necessários

- `ghcr-secret` — Autenticação GHCR
- `besu-secret` — Credenciais Besu (se aplicável)

#### ConfigMaps

- `trisla-config` — Configurações gerais
- `besu-config` — Configurações do Besu

#### PVCs

- `bc-nssmf-contracts` — Smart contracts persistentes

#### Dependências

- **Kafka** — Comunicação com Decision Engine (I-04)
- **Hyperledger Besu/GoQuorum** — Blockchain (RPC endpoint)
- **OpenTelemetry Collector** — Observabilidade

#### Interfaces Utilizadas

- **I-04 (Kafka):** Decision Engine → BC-NSSMF

#### Documentação

- **Guia Completo:** `docs/bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md`

---

### 2.5 Módulo 4: Decision Engine

#### Objective Técnico

O Decision Engine é responsável por tomar decisões baseadas em regras sobre a admissão, reconfiguração ou rejeição de network slices, integrando informações do ML-NSMF e do SEM-CSMF.

#### Configuração de Deploy

| Parâmetro | Valor | Description |
|-----------|-------|-----------|
| **Namespace** | `trisla` | Namespace do TriSLA |
| **Tipo de Deploy** | `Deployment` | Deployment Kubernetes |
| **Replicas** | `2` | Alta disponibilidade |
| **Port HTTP** | `8082` | Porta REST API |
| **Port gRPC** | `50051` | Porta gRPC (I-01) |
| **Image** | `ghcr.io/abelisboa/trisla-decision-engine:3.5.0` | Imagem Docker |
| **Node Affinity** | `node1, node2` | Pode rodar em ambos os nodes |

#### Recursos

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

#### Secrets Necessários

- `ghcr-secret` — Autenticação GHCR

#### ConfigMaps

- `trisla-config` — Configurações gerais
- `decision-rules` — Regras de decisão (YAML)

#### Dependências

- **Kafka** — Comunicação com ML-NSMF (I-03), BC-NSSMF (I-04), SLA-Agent Layer (I-05)
- **SEM-CSMF** — Comunicação gRPC (I-01)
- **NASP Adapter** — Comunicação REST (I-07)
- **OpenTelemetry Collector** — Observabilidade

#### Interfaces Utilizadas

- **I-01 (gRPC):** SEM-CSMF → Decision Engine
- **I-03 (Kafka):** ML-NSMF → Decision Engine
- **I-04 (Kafka):** Decision Engine → BC-NSSMF
- **I-05 (Kafka):** Decision Engine → SLA-Agent Layer
- **I-07 (REST):** Decision Engine → NASP Adapter

---

### 2.6 Módulo 5: SLA-Agent Layer

#### Objective Técnico

O SLA-Agent Layer é responsável por monitorar e garantir SLAs em cada domínio (RAN, Transport, Core) usando agentes federados que coletam métricas reais do NASP.

#### Configuração de Deploy

| Parâmetro | Valor | Description |
|-----------|-------|-----------|
| **Namespace** | `trisla` | Namespace do TriSLA |
| **Tipo de Deploy** | `DaemonSet` | Um pod por node |
| **Replicas** | `2` (um por node) | Distribuído em node1 e node2 |
| **Port HTTP** | `8084` | Porta REST API |
| **Image** | `ghcr.io/abelisboa/trisla-sla-agent-layer:3.5.0` | Imagem Docker |
| **Node Affinity** | `node1, node2` | Deve rodar em ambos os nodes |

#### Recursos

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

#### Secrets Necessários

- `ghcr-secret` — Autenticação GHCR
- `nasp-credentials` — Credenciais NASP (se aplicável)

#### ConfigMaps

- `trisla-config` — Configurações gerais
- `slo-config-ran` — SLOs para RAN
- `slo-config-transport` — SLOs para Transport
- `slo-config-core` — SLOs para Core

#### Dependências

- **Kafka** — Comunicação com Decision Engine (I-05) e NASP Adapter (I-06)
- **NASP Adapter** — Coleta de métricas reais (I-06)
- **OpenTelemetry Collector** — Observabilidade

#### Interfaces Utilizadas

- **I-05 (Kafka):** Decision Engine → SLA-Agent Layer
- **I-06 (Kafka):** SLA-Agent Layer → NASP Adapter

---

### 2.7 Módulo 6: NASP Adapter

#### Objective Técnico

O NASP Adapter é responsável por conectar o TriSLA aos serviços reais do NASP (RAN, Transport, Core), provisionando slices e coletando métricas reais.

#### Configuração de Deploy

| Parâmetro | Valor | Description |
|-----------|-------|-----------|
| **Namespace** | `trisla` | Namespace do TriSLA |
| **Tipo de Deploy** | `Deployment` | Deployment Kubernetes |
| **Replicas** | `2` | Alta disponibilidade |
| **Port HTTP** | `8085` | Porta REST API |
| **Image** | `ghcr.io/abelisboa/trisla-nasp-adapter:3.5.0` | Imagem Docker |
| **Node Affinity** | `node1, node2` | Pode rodar em ambos os nodes |

#### Recursos

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

#### Secrets Necessários

- `ghcr-secret` — Autenticação GHCR
- `nasp-oauth2-secret` — Credenciais OAuth2 NASP

#### ConfigMaps

- `trisla-config` — Configurações gerais
- `nasp-endpoints` — Endpoints reais do NASP

#### Dependências

- **NASP Services** — Services reais do NASP (RAN, Transport, Core)
- **Kafka** — Comunicação com SLA-Agent Layer (I-06)
- **Decision Engine** — Comunicação REST (I-07)
- **OpenTelemetry Collector** — Observabilidade

#### Interfaces Utilizadas

- **I-06 (Kafka):** SLA-Agent Layer → NASP Adapter
- **I-07 (REST):** Decision Engine → NASP Adapter

---

### 2.8 Módulo 7: UI Dashboard

#### Objective Técnico

O UI Dashboard fornece uma interface web para visualização e gerenciamento do TriSLA, incluindo dashboards de métricas, status de slices e configurações.

#### Configuração de Deploy

| Parâmetro | Valor | Description |
|-----------|-------|-----------|
| **Namespace** | `trisla` | Namespace do TriSLA |
| **Tipo de Deploy** | `Deployment` | Deployment Kubernetes |
| **Replicas** | `2` | Alta disponibilidade |
| **Port HTTP** | `3000` | Porta Web UI |
| **Image** | `ghcr.io/abelisboa/trisla-ui-dashboard:3.5.0` | Imagem Docker |
| **Node Affinity** | `node1, node2` | Pode rodar em ambos os nodes |

#### Recursos

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

#### Secrets Necessários

- `ghcr-secret` — Autenticação GHCR

#### ConfigMaps

- `trisla-config` — Configurações gerais
- `ui-config` — Configurações da UI

#### Dependências

- **Backend API** — APIs REST do TriSLA
- **Grafana** — Dashboards de métricas (opcional)

---

### 2.9 Tabela Consolidada: TriSLA → NASP (node1/node2)

| Módulo | Namespace | Tipo | Replicas | Port HTTP | Port gRPC | Node1 | Node2 | Image Registry |
|--------|-----------|------|----------|-----------|-----------|-------|-------|----------------|
| **SEM-CSMF** | `trisla` | Deployment | 3 | 8080 | 50051 | ✅ | ✅ | `ghcr.io/abelisboa/trisla-sem-csmf:3.5.0` |
| **ML-NSMF** | `trisla` | Deployment | 3 | 8081 | - | ✅ | ✅ | `ghcr.io/abelisboa/trisla-ml-nsmf:3.5.0` |
| **BC-NSSMF** | `trisla` | Deployment | 2 | 8083 | - | ✅ | ✅ | `ghcr.io/abelisboa/trisla-bc-nssmf:3.5.0` |
| **Decision Engine** | `trisla` | Deployment | 2 | 8082 | 50051 | ✅ | ✅ | `ghcr.io/abelisboa/trisla-decision-engine:3.5.0` |
| **SLA-Agent Layer** | `trisla` | DaemonSet | 2 | 8084 | - | ✅ | ✅ | `ghcr.io/abelisboa/trisla-sla-agent-layer:3.5.0` |
| **NASP Adapter** | `trisla` | Deployment | 2 | 8085 | - | ✅ | ✅ | `ghcr.io/abelisboa/trisla-nasp-adapter:3.5.0` |
| **UI Dashboard** | `trisla` | Deployment | 2 | 3000 | - | ✅ | ✅ | `ghcr.io/abelisboa/trisla-ui-dashboard:3.5.0` |

---

## 3. Inventário Ansible Completo

### 3.1 Estrutura do Inventário

O inventário Ansible está localizado em `ansible/inventory.yaml` e utiliza conexão local (sem SSH):

```yaml
# ============================================
# Inventory Ansible YAML - TriSLA NASP
# ============================================
# Inventário para deploy local 127.0.0.1
# ============================================

[nasp]
127.0.0.1 ansible_connection=local ansible_python_interpreter=/usr/bin/python3
```

### 3.2 Variáveis de Grupo

#### 3.2.1 `ansible/group_vars/all.yml`

```yaml
# ============================================
# Variáveis Globais Ansible - TriSLA
# ============================================

# Configurações de rede NASP
trisla_network:
  interface: "my5g"
  node_ip: "192.168.10.16"
  gateway: "192.168.10.1"

# Configurações do Kubernetes
kubernetes:
  namespace: "trisla"
  kubeconfig_path: "/etc/kubernetes/admin.conf"

# Configurações do TriSLA
trisla:
  namespace: "trisla"
  image_registry: "ghcr.io/abelisboa"
  image_pull_secret: "ghcr-secret"
  
  # Módulos
  modules:
    sem_csmf:
      enabled: true
      image: "{{ trisla.image_registry }}/trisla-sem-csmf"
      tag: "3.5.0"
    
    ml_nsmf:
      enabled: true
      image: "{{ trisla.image_registry }}/trisla-ml-nsmf"
      tag: "3.5.0"
    
    decision_engine:
      enabled: true
      image: "{{ trisla.image_registry }}/trisla-decision-engine"
      tag: "3.5.0"
    
    bc_nssmf:
      enabled: true
      image: "{{ trisla.image_registry }}/trisla-bc-nssmf"
      tag: "3.5.0"
    
    sla_agent_layer:
      enabled: true
      image: "{{ trisla.image_registry }}/trisla-sla-agent-layer"
      tag: "3.5.0"
    
    nasp_adapter:
      enabled: true
      image: "{{ trisla.image_registry }}/trisla-nasp-adapter"
      tag: "3.5.0"
    
    ui_dashboard:
      enabled: true
      image: "{{ trisla.image_registry }}/trisla-ui-dashboard"
      tag: "3.5.0"

# Configurações de produção
production:
  enabled: true
  simulation_mode: false
  use_real_services: true
  execute_real_actions: true

# Configurações de observabilidade
observability:
  enabled: true
  otlp_collector:
    enabled: true
    image: "otel/opentelemetry-collector:latest"
  
  prometheus:
    enabled: true
  
  grafana:
    enabled: true
    admin_password: "admin"  # ⚠️ ALTERAR EM PRODUÇÃO

# Configurações de recursos
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "2000m"
    memory: "2Gi"
```

#### 3.2.2 `ansible/group_vars/nasp.yml` (se necessário)

```yaml
# Configurações específicas do NASP
nasp:
  cluster_name: "nasp-cluster"
  kubeconfig: "/etc/kubernetes/admin.conf"
  storage_class: "local-path"
```

#### 3.2.3 `ansible/group_vars/trisla.yml` (se necessário)

```yaml
# Configurações específicas do TriSLA
trisla:
  helm_chart_path: "{{ playbook_dir }}/../helm/trisla"
  values_file: "{{ helm_chart_path }}/values-nasp.yaml"
  release_name: "trisla"
```

### 3.3 Variáveis de Host

#### 3.3.1 `ansible/host_vars/node1.yml` (se necessário)

```yaml
# Configurações específicas do node1
node1:
  ip: "192.168.10.16"
  interface: "my5g"
  role: "control-plane,worker"
```

#### 3.3.2 `ansible/host_vars/node2.yml` (se necessário)

```yaml
# Configurações específicas do node2
node2:
  ip: "192.168.10.15"
  interface: "my5g"
  role: "control-plane,worker"
```

---

## 4. Estrutura Completa dos Playbooks e Roles

### 4.1 Playbooks Principais

#### 4.1.1 `ansible/playbooks/pre-flight.yml`

**Propósito:** Validações pré-deploy do cluster NASP

**Fases Internas:**
1. Verifiesr versão do Kubernetes
2. Verifiesr certificados do cluster
3. Verifiesr DNS interno
4. Verifiesr autenticação GHCR
5. Verifiesr suporte a NetworkPolicy
6. Verifiesr saúde do Calico
7. Verifiesr Helm
8. Verifiesr StorageClass

**Roles Chamadas:** Nenhuma (tasks diretos)

**Templates Utilizados:** Nenhum

**Variáveis Essenciais:**
- `namespace`
- `kubeconfig_path`

**Ordem Recomendada:** Primeiro playbook a ser executado

---

#### 4.1.2 `ansible/playbooks/setup-namespace.yml`

**Propósito:** Criar namespace e secrets necessários

**Fases Internas:**
1. Criar namespace `trisla`
2. Criar secret GHCR
3. Criar secrets adicionais (se necessário)

**Roles Chamadas:** Nenhuma (tasks diretos)

**Templates Utilizados:** Nenhum

**Variáveis Essenciais:**
- `namespace`
- `ghcr_user`
- `ghcr_token`

**Ordem Recomendada:** Segundo playbook a ser executado

---

#### 4.1.3 `ansible/playbooks/deploy-trisla-nasp.yml`

**Propósito:** Deploy completo do TriSLA no NASP

**Fases Internas:**
1. Validar pré-requisitos
2. Criar namespace
3. Configurar secrets
4. Validar Helm chart
5. Dry-run do deploy
6. Deploy real do TriSLA
7. Verifiesr status do deploy
8. Waitsr pods estarem prontos
9. Verifiesr serviços
10. Validar deploy

**Roles Chamadas:** Nenhuma (tasks diretos)

**Templates Utilizados:** Nenhum

**Variáveis Essenciais:**
- `namespace`
- `helm_chart_path`
- `values_file`

**Ordem Recomendada:** Terceiro playbook a ser executado (após pre-flight e setup-namespace)

---

#### 4.1.4 `ansible/playbooks/validate-cluster.yml`

**Propósito:** Validação pós-deploy do cluster TriSLA

**Fases Internas:**
1. Verifiesr pods em Running
2. Verifiesr readiness probes
3. Verifiesr liveness probes
4. Verifiesr serviços
5. Verifiesr health checks
6. Verifiesr conectividade entre módulos

**Roles Chamadas:** Nenhuma (tasks diretos)

**Templates Utilizados:** Nenhum

**Variáveis Essenciais:**
- `namespace`

**Ordem Recomendada:** Quarto playbook a ser executado (após deploy)

---

### 4.2 Roles (Estrutura Conceitual)

Embora o repositório atual não possua roles separadas, a estrutura recomendada seria:

#### 4.2.1 `ansible/roles/sem_csmf/`

**Propósito:** Deploy do módulo SEM-CSMF

**Tasks:**
- Deploy Helm chart para SEM-CSMF
- Verifiesr pods
- Verifiesr serviços
- Validar health checks

---

#### 4.2.2 `ansible/roles/ml_nsmf/`

**Propósito:** Deploy do módulo ML-NSMF

**Tasks:**
- Deploy Helm chart para ML-NSMF
- Verifiesr pods
- Verifiesr serviços
- Validar health checks

---

#### 4.2.3 `ansible/roles/bc_nssmf/`

**Propósito:** Deploy do módulo BC-NSSMF

**Tasks:**
- Deploy Helm chart para BC-NSSMF
- Verifiesr pods
- Verifiesr serviços
- Validar health checks

---

#### 4.2.4 `ansible/roles/decision_engine/`

**Propósito:** Deploy do Decision Engine

**Tasks:**
- Deploy Helm chart para Decision Engine
- Verifiesr pods
- Verifiesr serviços
- Validar health checks

---

#### 4.2.5 `ansible/roles/sla_agents/`

**Propósito:** Deploy do SLA-Agent Layer

**Tasks:**
- Deploy Helm chart para SLA-Agent Layer
- Verifiesr DaemonSet
- Verifiesr pods em cada node
- Validar health checks

---

#### 4.2.6 `ansible/roles/api_backend/`

**Propósito:** Deploy do Backend/API (se separado)

**Tasks:**
- Deploy Helm chart para Backend
- Verifiesr pods
- Verifiesr serviços
- Validar health checks

---

#### 4.2.7 `ansible/roles/portal/`

**Propósito:** Deploy do UI Dashboard

**Tasks:**
- Deploy Helm chart para UI Dashboard
- Verifiesr pods
- Verifiesr serviços
- Validar health checks

---

#### 4.2.8 `ansible/roles/monitoring/`

**Propósito:** Configuração de observabilidade

**Tasks:**
- Configurar OpenTelemetry Collector
- Configurar ServiceMonitors
- Configurar dashboards Grafana (se aplicável)

---

## 5. Preparação Manual (Somente no node1)

### 5.1 Verifiesção da Saúde do Cluster

**Executar localmente no node1:**

```bash
# Verifiesr nodes
kubectl get nodes

# Saída esperada:
# NAME     STATUS   ROLES           AGE   VERSION
# node1    Ready    control-plane   30d   v1.26.0
# node2    Ready    control-plane   30d   v1.26.0

# Verifiesr pods do sistema
kubectl get pods -A

# Verifiesr pods do Calico
kubectl get pods -n kube-system -l k8s-app=calico-node

# Saída esperada:
# NAME                READY   STATUS    RESTARTS   AGE
# calico-node-xxxxx   1/1     Running   0          30d
# calico-node-yyyyy   1/1     Running   0          30d
```

---

### 5.2 Validação CNI (Calico)

```bash
# Verifiesr status do Calico
kubectl get nodes -o wide

# Verifiesr Network Policies
kubectl get networkpolicies --all-namespaces

# Verifiesr conectividade entre pods
kubectl run test-pod --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default
```

---

### 5.3 Validação kubelet / kube-proxy

```bash
# Verifiesr kubelet
systemctl status kubelet

# Verifiesr kube-proxy
kubectl get pods -n kube-system -l k8s-app=kube-proxy

# Verifiesr logs do kubelet (se necessário)
journalctl -u kubelet -f
```

---

### 5.4 Verifiesção de StorageClass

```bash
# Listar StorageClasses
kubectl get storageclass

# Saída esperada:
# NAME          PROVISIONER       RECLAIMPOLICY   VOLUMEBINDINGMODE   AGE
# local-path    rancher.io/local-path   Delete         WaitForFirstConsumer   30d

# Verifiesr StorageClass padrão
kubectl get storageclass -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}'

# Verifiesr volumes persistentes
kubectl get pv
kubectl get pvc --all-namespaces
```

---

### 5.5 Checagem de Portas Reais

**Executar no node1:**

```bash
# Verifiesr portas em uso
ss -tulnp | grep -E "8080|8081|8082|8083|8084|8085|50051|9090|3000|4317|9092"

# Verifiesr portas dos serviços Kubernetes
kubectl get svc --all-namespaces | grep -E "8080|8081|8082|8083|8084|8085|50051"

# Verifiesr NodePorts (se aplicável)
kubectl get svc --all-namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.type}{"\t"}{.spec.ports[*].port}{"\n"}{end}' | grep NodePort
```

---

### 5.6 Validação DNS Interno do Cluster

```bash
# Testar DNS interno
kubectl run test-dns --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default

# Testar DNS de serviços
kubectl run test-dns-service --image=busybox --rm -it --restart=Never -- nslookup kube-dns.kube-system.svc.cluster.local

# Verifiesr CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

---

### 5.7 Validação de Recursos node1 e node2

```bash
# Verifiesr recursos do node1
kubectl describe node node1 | grep -A 10 "Allocated resources"

# Verifiesr recursos do node2
kubectl describe node node2 | grep -A 10 "Allocated resources"

# Verifiesr capacidade total
kubectl top nodes
```

---

### 5.8 Checklist Final de Prontidão

**Antes de prosseguir com o deploy, verificar:**

- [ ] Cluster Kubernetes operacional (2 nodes Ready)
- [ ] CNI Calico funcionando
- [ ] StorageClass disponível
- [ ] DNS interno funcionando
- [ ] Portas livres (8080-8085, 50051, etc.)
- [ ] Recursos suficientes (CPU, memória)
- [ ] `kubectl` configurado e conectado
- [ ] `helm` instalado (versão ≥ 3.12)
- [ ] `ansible` instalado (versão ≥ 2.14)
- [ ] Acesso ao GHCR configurado
- [ ] `values-nasp.yaml` preenchido com valores reais
- [ ] Imagens GHCR disponíveis

---

## 6. Deploy Completo via Ansible

### 6.1 Pré-Checagem Esperada

**Executar no node1:**

```bash
cd ~/gtp5g/trisla

# Pré-checagem do playbook de deploy
ansible-playbook -i ansible/inventory.yaml ansible/playbooks/deploy-trisla-nasp.yml --check

# Pré-checagem do playbook de pre-flight
ansible-playbook -i ansible/inventory.yaml ansible/playbooks/pre-flight.yml --check
```

**Validação Esperada:**
- Nenhum erro crítico
- Todas as tasks marcadas como `ok` ou `changed` (sem `failed`)
- Warnings são aceitáveis (verificar se não são críticos)

---

### 6.2 Execução Real (Description, Não Execução)

**IMPORTANTE:** Este documento descreve o processo, mas **NÃO executa** comandos reais.

#### 6.2.1 Passo 1: Pre-Flight Checks

```bash
# Executar validações pré-deploy
ansible-playbook -i ansible/inventory.yaml ansible/playbooks/pre-flight.yml
```

**Resultado Esperado:**
- Kubernetes versão ≥ 1.26
- Helm instalado e funcional
- Calico operacional
- StorageClass disponível
- DNS interno funcionando
- GHCR autenticado

---

#### 6.2.2 Passo 2: Setup Namespace

```bash
# Criar namespace e secrets
ansible-playbook -i ansible/inventory.yaml ansible/playbooks/setup-namespace.yml
```

**Resultado Esperado:**
- Namespace `trisla` criado
- Secret `ghcr-secret` criado
- Secrets adicionais criados (se necessário)

---

#### 6.2.3 Passo 3: Deploy TriSLA

```bash
# Deploy completo do TriSLA
ansible-playbook -i ansible/inventory.yaml ansible/playbooks/deploy-trisla-nasp.yml
```

**Resultado Esperado:**
- Helm chart validado
- Deploy executado com sucesso
- Pods em status `Running`
- Services criados
- Readiness probes passando

---

#### 6.2.4 Passo 4: Validação Pós-Deploy

```bash
# Validar deploy
ansible-playbook -i ansible/inventory.yaml ansible/playbooks/validate-cluster.yml
```

**Resultado Esperado:**
- Todos os pods em `Running`
- Readiness probes passando
- Liveness probes passando
- Services acessíveis
- Health checks respondendo

---

### 6.3 Ordem Oficial de Instalação

A ordem de instalação dos módulos é gerenciada pelo Helm chart, mas a sequência lógica é:

1. **SEM-CSMF** — Base semântica
2. **ML-NSMF** — Predição ML
3. **BC-NSSMF** — Registro blockchain
4. **Decision Engine** — Motor de decisão
5. **SLA-Agent Layer** — Agentes federados
6. **NASP Adapter** — Adaptador NASP
7. **UI Dashboard** — Interface web
8. **Observabilidade** — OpenTelemetry, Prometheus, Grafana

---

### 6.4 Recursos Criados por Módulo

#### 6.4.1 SEM-CSMF

**Recursos Esperados:**
- Deployment: `trisla-sem-csmf`
- Service: `trisla-sem-csmf` (ClusterIP, port 8080)
- Service: `trisla-sem-csmf-grpc` (ClusterIP, port 50051)
- ConfigMap: `trisla-config`
- Secret: `ghcr-secret` (referenciado)

**Comando de Verifiesção:**
```bash
kubectl get pods,svc,configmap -n trisla -l app.kubernetes.io/component=sem-csmf
```

**Readiness Esperada:**
```bash
kubectl get pods -n trisla -l app.kubernetes.io/component=sem-csmf
# Saída esperada:
# NAME                              READY   STATUS    RESTARTS   AGE
# trisla-sem-csmf-xxxxx-xxxxx       1/1     Running   0          5m
# trisla-sem-csmf-yyyyy-yyyyy       1/1     Running   0          5m
# trisla-sem-csmf-zzzzz-zzzzz       1/1     Running   0          5m
```

**Endpoints Expostos:**
- HTTP: `http://trisla-sem-csmf.trisla.svc.cluster.local:8080`
- gRPC: `trisla-sem-csmf-grpc.trisla.svc.cluster.local:50051`

---

#### 6.4.2 ML-NSMF

**Recursos Esperados:**
- Deployment: `trisla-ml-nsmf`
- Service: `trisla-ml-nsmf` (ClusterIP, port 8081)
- ConfigMap: `trisla-config`
- PVC: `ml-nsmf-models` (se aplicável)

**Comando de Verifiesção:**
```bash
kubectl get pods,svc,pvc -n trisla -l app.kubernetes.io/component=ml-nsmf
```

**Readiness Esperada:**
```bash
kubectl get pods -n trisla -l app.kubernetes.io/component=ml-nsmf
# Saída esperada:
# NAME                            READY   STATUS    RESTARTS   AGE
# trisla-ml-nsmf-xxxxx-xxxxx     1/1     Running   0          5m
# trisla-ml-nsmf-yyyyy-yyyyy     1/1     Running   0          5m
# trisla-ml-nsmf-zzzzz-zzzzz     1/1     Running   0          5m
```

**Endpoints Expostos:**
- HTTP: `http://trisla-ml-nsmf.trisla.svc.cluster.local:8081`

---

#### 6.4.3 BC-NSSMF

**Recursos Esperados:**
- Deployment: `trisla-bc-nssmf`
- Service: `trisla-bc-nssmf` (ClusterIP, port 8083)
- ConfigMap: `trisla-config`, `besu-config`
- PVC: `bc-nssmf-contracts` (se aplicável)

**Comando de Verifiesção:**
```bash
kubectl get pods,svc,pvc -n trisla -l app.kubernetes.io/component=bc-nssmf
```

**Readiness Esperada:**
```bash
kubectl get pods -n trisla -l app.kubernetes.io/component=bc-nssmf
# Saída esperada:
# NAME                              READY   STATUS    RESTARTS   AGE
# trisla-bc-nssmf-xxxxx-xxxxx       1/1     Running   0          5m
# trisla-bc-nssmf-yyyyy-yyyyy       1/1     Running   0          5m
```

**Endpoints Expostos:**
- HTTP: `http://trisla-bc-nssmf.trisla.svc.cluster.local:8083`

---

#### 6.4.4 Decision Engine

**Recursos Esperados:**
- Deployment: `trisla-decision-engine`
- Service: `trisla-decision-engine` (ClusterIP, port 8082)
- Service: `trisla-decision-engine-grpc` (ClusterIP, port 50051)
- ConfigMap: `trisla-config`, `decision-rules`

**Comando de Verifiesção:**
```bash
kubectl get pods,svc,configmap -n trisla -l app.kubernetes.io/component=decision-engine
```

**Readiness Esperada:**
```bash
kubectl get pods -n trisla -l app.kubernetes.io/component=decision-engine
# Saída esperada:
# NAME                                    READY   STATUS    RESTARTS   AGE
# trisla-decision-engine-xxxxx-xxxxx      1/1     Running   0          5m
# trisla-decision-engine-yyyyy-yyyyy      1/1     Running   0          5m
```

**Endpoints Expostos:**
- HTTP: `http://trisla-decision-engine.trisla.svc.cluster.local:8082`
- gRPC: `trisla-decision-engine-grpc.trisla.svc.cluster.local:50051`

---

#### 6.4.5 SLA-Agent Layer

**Recursos Esperados:**
- DaemonSet: `trisla-sla-agent-layer`
- Service: `trisla-sla-agent-layer` (ClusterIP, port 8084)
- ConfigMap: `trisla-config`, `slo-config-ran`, `slo-config-transport`, `slo-config-core`

**Comando de Verifiesção:**
```bash
kubectl get daemonset,pods,svc -n trisla -l app.kubernetes.io/component=sla-agent-layer
```

**Readiness Esperada:**
```bash
kubectl get pods -n trisla -l app.kubernetes.io/component=sla-agent-layer
# Saída esperada:
# NAME                                    READY   STATUS    RESTARTS   AGE
# trisla-sla-agent-layer-xxxxx            1/1     Running   0          5m  # node1
# trisla-sla-agent-layer-yyyyy            1/1     Running   0          5m  # node2
```

**Endpoints Expostos:**
- HTTP: `http://trisla-sla-agent-layer.trisla.svc.cluster.local:8084`

---

#### 6.4.6 NASP Adapter

**Recursos Esperados:**
- Deployment: `trisla-nasp-adapter`
- Service: `trisla-nasp-adapter` (ClusterIP, port 8085)
- ConfigMap: `trisla-config`, `nasp-endpoints`
- Secret: `nasp-oauth2-secret` (se aplicável)

**Comando de Verifiesção:**
```bash
kubectl get pods,svc,configmap -n trisla -l app.kubernetes.io/component=nasp-adapter
```

**Readiness Esperada:**
```bash
kubectl get pods -n trisla -l app.kubernetes.io/component=nasp-adapter
# Saída esperada:
# NAME                                READY   STATUS    RESTARTS   AGE
# trisla-nasp-adapter-xxxxx-xxxxx     1/1     Running   0          5m
# trisla-nasp-adapter-yyyyy-yyyyy     1/1     Running   0          5m
```

**Endpoints Expostos:**
- HTTP: `http://trisla-nasp-adapter.trisla.svc.cluster.local:8085`

---

#### 6.4.7 UI Dashboard

**Recursos Esperados:**
- Deployment: `trisla-ui-dashboard`
- Service: `trisla-ui-dashboard` (ClusterIP, port 3000)
- Ingress: `trisla-ingress` (se configurado)
- ConfigMap: `trisla-config`, `ui-config`

**Comando de Verifiesção:**
```bash
kubectl get pods,svc,ingress -n trisla -l app.kubernetes.io/component=ui-dashboard
```

**Readiness Esperada:**
```bash
kubectl get pods -n trisla -l app.kubernetes.io/component=ui-dashboard
# Saída esperada:
# NAME                              READY   STATUS    RESTARTS   AGE
# trisla-ui-dashboard-xxxxx-xxxxx   1/1     Running   0          5m
# trisla-ui-dashboard-yyyyy-yyyyy   1/1     Running   0          5m
```

**Endpoints Expostos:**
- HTTP: `http://trisla-ui-dashboard.trisla.svc.cluster.local:3000`
- Ingress: `http://trisla.local` (se configurado)

---

## 7. Pós-Deploy (Validação E2E)

### 7.1 Testes de Endpoints

#### 7.1.1 SEM-CSMF — `/semantic/intents`

**Teste de Health Check:**
```bash
# Port-forward
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080 &

# Health check
curl http://localhost:8080/health

# Resposta esperada:
# {"status":"healthy","version":"3.5.0"}
```

**Teste de Intent:**
```bash
# Criar intent
curl -X POST http://localhost:8080/api/v1/intents \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id": "test-urllc-001",
    "tenant_id": "test-tenant",
    "service_type": "URLLC",
    "sla_requirements": {
      "latency": "10ms",
      "throughput": "100Mbps",
      "reliability": 0.99999
    }
  }'

# Resposta esperada:
# {"intent_id":"test-urllc-001","status":"validated","nest_id":"nest-urllc-001"}
```

---

#### 7.1.2 ML-NSMF — `/predict`

**Teste de Health Check:**
```bash
# Port-forward
kubectl port-forward -n trisla svc/trisla-ml-nsmf 8081:8081 &

# Health check
curl http://localhost:8081/health

# Resposta esperada:
# {"status":"healthy","version":"3.5.0"}
```

**Teste de Predição:**
```bash
# Predição de viabilidade
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{
    "nest_id": "nest-urllc-001",
    "metrics": {
      "latency": 5.0,
      "throughput": 100.0,
      "packet_loss": 0.001,
      "jitter": 1.0
    }
  }'

# Resposta esperada:
# {"risk_score":0.2,"risk_level":"low","confidence":0.95,"explanation":{...}}
```

---

#### 7.1.3 BC-NSSMF — `/contract/validate`

**Teste de Health Check:**
```bash
# Port-forward
kubectl port-forward -n trisla svc/trisla-bc-nssmf 8083:8083 &

# Health check
curl http://localhost:8083/health

# Resposta esperada:
# {"status":"healthy","version":"3.5.0"}
```

**Teste de Validação de Contrato:**
```bash
# Validar contrato
curl -X POST http://localhost:8083/contract/validate \
  -H "Content-Type: application/json" \
  -d '{
    "contract_address": "0x...",
    "sla_id": "sla-001"
  }'

# Resposta esperada:
# {"valid":true,"contract_address":"0x...","sla_id":"sla-001"}
```

---

#### 7.1.4 Decision Engine — `/decision/evaluate`

**Teste de Health Check:**
```bash
# Port-forward
kubectl port-forward -n trisla svc/trisla-decision-engine 8082:8082 &

# Health check
curl http://localhost:8082/health

# Resposta esperada:
# {"status":"healthy","version":"3.5.0"}
```

**Teste de Decisão:**
```bash
# Avaliar decisão
curl -X POST http://localhost:8082/decision/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "nest_id": "nest-urllc-001",
    "risk_assessment": {
      "risk_score": 0.2,
      "risk_level": "low"
    }
  }'

# Resposta esperada:
# {"decision":"ADMIT","nest_id":"nest-urllc-001","confidence":0.95}
```

---

#### 7.1.5 SLA-Agent Layer — `/agents/slo`

**Teste de Health Check:**
```bash
# Port-forward
kubectl port-forward -n trisla svc/trisla-sla-agent-layer 8084:8084 &

# Health check
curl http://localhost:8084/health

# Resposta esperada:
# {"status":"healthy","version":"3.5.0"}
```

**Teste de SLO:**
```bash
# Verifiesr SLO
curl http://localhost:8084/agents/slo?domain=RAN

# Resposta esperada:
# {"domain":"RAN","slo_status":"compliant","metrics":{...}}
```

---

#### 7.1.6 Backend/API — `/api/v1/*`

**Teste de Health Check:**
```bash
# Port-forward (se backend separado)
kubectl port-forward -n trisla svc/trisla-api 8086:8086 &

# Health check
curl http://localhost:8086/health

# Resposta esperada:
# {"status":"healthy","version":"3.5.0"}
```

---

### 7.2 Validação do Ciclo Fechado TriSLA

**Fluxo Completo:**

```
Intent → SEM-CSMF → NEST → Decision Engine → SLA-Agent Layer → Observabilidade → BC-NSSMF → Portal
```

**Teste E2E:**

```bash
# 1. Criar intent via SEM-CSMF
INTENT_RESPONSE=$(curl -X POST http://localhost:8080/api/v1/intents \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id": "e2e-test-001",
    "tenant_id": "test-tenant",
    "service_type": "URLLC",
    "sla_requirements": {
      "latency": "10ms",
      "throughput": "100Mbps",
      "reliability": 0.99999
    }
  }')

# 2. Verifiesr NEST gerado
NEST_ID=$(echo $INTENT_RESPONSE | jq -r '.nest_id')

# 3. Verifiesr predição ML-NSMF (via Kafka)
# (Waitsr processamento assíncrono)

# 4. Verifiesr decisão Decision Engine
DECISION_RESPONSE=$(curl -X POST http://localhost:8082/decision/evaluate \
  -H "Content-Type: application/json" \
  -d "{
    \"nest_id\": \"$NEST_ID\",
    \"risk_assessment\": {
      \"risk_score\": 0.2,
      \"risk_level\": \"low\"
    }
  }")

# 5. Verifiesr registro BC-NSSMF (via Kafka)
# (Waitsr processamento assíncrono)

# 6. Verifiesr SLA-Agent Layer
SLA_RESPONSE=$(curl http://localhost:8084/agents/slo?domain=RAN)

# 7. Verifiesr observabilidade (Prometheus)
# (Waitsr coleta de métricas)
```

**Validação Esperada:**
- Intent processado com sucesso
- NEST gerado
- Predição ML realizada
- Decisão tomada (ADMIT/REJECT/RECONFIGURE)
- SLA registrado em blockchain
- Métricas coletadas
- Observabilidade funcionando

---

### 7.3 Validação de Dashboards TriSLA no Grafana

**Acessar Grafana:**
```bash
# Port-forward
kubectl port-forward -n monitoring svc/grafana 3000:3000 &

# Acessar: http://localhost:3000
# Credenciais: admin/admin (alterar em produção)
```

**Dashboards Esperados:**
- **TriSLA Overview** — Visão geral do sistema
- **SEM-CSMF Metrics** — Métricas de intents e NESTs
- **ML-NSMF Metrics** — Métricas de predições e XAI
- **Decision Engine Metrics** — Métricas de decisões
- **BC-NSSMF Metrics** — Métricas de blockchain
- **SLA-Agent Layer Metrics** — Métricas de SLOs por domínio
- **NASP Adapter Metrics** — Métricas de integration NASP

**Validação:**
- [ ] Dashboards carregados
- [ ] Métricas sendo coletadas
- [ ] Gráficos atualizando
- [ ] Alertas configurados (se aplicável)

---

### 7.4 Validação de Ingestão OTLP

**Verifiesr OpenTelemetry Collector:**
```bash
# Verifiesr pods do OTLP Collector
kubectl get pods -n trisla -l app.kubernetes.io/component=otel-collector

# Verifiesr logs
kubectl logs -n trisla -l app.kubernetes.io/component=otel-collector --tail=100

# Verifiesr métricas no Prometheus
# (Waitsr coleta)
```

**Validação Esperada:**
- OTLP Collector em `Running`
- Traces sendo coletados
- Métricas sendo exportadas para Prometheus
- Logs sendo coletados (se configurado)

---

### 7.5 Validação Final dos Pods e Services

**Comando Completo:**
```bash
# Verifiesr todos os pods
kubectl get pods -n trisla

# Saída esperada:
# NAME                                    READY   STATUS    RESTARTS   AGE
# trisla-sem-csmf-xxxxx-xxxxx             1/1     Running   0          10m
# trisla-sem-csmf-yyyyy-yyyyy             1/1     Running   0          10m
# trisla-sem-csmf-zzzzz-zzzzz             1/1     Running   0          10m
# trisla-ml-nsmf-xxxxx-xxxxx              1/1     Running   0          10m
# trisla-ml-nsmf-yyyyy-yyyyy              1/1     Running   0          10m
# trisla-ml-nsmf-zzzzz-zzzzz              1/1     Running   0          10m
# trisla-bc-nssmf-xxxxx-xxxxx             1/1     Running   0          10m
# trisla-bc-nssmf-yyyyy-yyyyy             1/1     Running   0          10m
# trisla-decision-engine-xxxxx-xxxxx     1/1     Running   0          10m
# trisla-decision-engine-yyyyy-yyyyy      1/1     Running   0          10m
# trisla-sla-agent-layer-xxxxx            1/1     Running   0          10m  # node1
# trisla-sla-agent-layer-yyyyy            1/1     Running   0          10m  # node2
# trisla-nasp-adapter-xxxxx-xxxxx         1/1     Running   0          10m
# trisla-nasp-adapter-yyyyy-yyyyy         1/1     Running   0          10m
# trisla-ui-dashboard-xxxxx-xxxxx         1/1     Running   0          10m
# trisla-ui-dashboard-yyyyy-yyyyy         1/1     Running   0          10m

# Verifiesr todos os serviços
kubectl get svc -n trisla

# Verifiesr deployments
kubectl get deployments -n trisla

# Verifiesr daemonset
kubectl get daemonset -n trisla
```

**Validação Esperada:**
- Todos os pods em `Running`
- Todos os pods com `READY 1/1`
- Nenhum pod em `CrashLoopBackOff` ou `Error`
- Todos os serviços criados
- Deployments com réplicas corretas
- DaemonSet com pods em ambos os nodes

---

## 8. Diagramas ASCII

### 8.1 Arquitetura TriSLA dentro do NASP

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         NASP Cluster (Kubernetes)                        │
│                    Node1 (192.168.10.16) + Node2 (192.168.10.15)        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         Namespace: trisla                                │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   SEM-CSMF   │──────│   ML-NSMF    │──────│ Decision     │
│  (3 replicas)│      │  (3 replicas)│      │ Engine       │
│  Port: 8080  │      │  Port: 8081  │      │ (2 replicas) │
│  gRPC: 50051 │      │              │      │ Port: 8082   │
└──────┬───────┘      └──────┬───────┘      │ gRPC: 50051  │
       │ I-01 (gRPC)         │ I-02 (Kafka) └──────┬───────┘
       │                     │                      │
       │                     │                      │ I-03 (Kafka)
       │                     │                      │
       │                     │                      ▼
       │                     │              ┌──────────────┐
       │                     │              │   BC-NSSMF  │
       │                     │              │ (2 replicas)│
       │                     │              │ Port: 8083  │
       │                     │              └──────┬───────┘
       │                     │                     │ I-04 (Kafka)
       │                     │                     │
       │                     │                     ▼
       │                     │              ┌──────────────┐
       │                     │              │ SLA-Agent   │
       │                     │              │   Layer      │
       │                     │              │ (DaemonSet)  │
       │                     │              │ Port: 8084  │
       │                     │              │ node1+node2  │
       │                     │              └──────┬───────┘
       │                     │                     │ I-05 (Kafka)
       │                     │                     │
       │                     │                     ▼
       │                     │              ┌──────────────┐
       │                     │              │ NASP Adapter │
       │                     │              │ (2 replicas) │
       │                     │              │ Port: 8085   │
       │                     │              └──────┬───────┘
       │                     │                     │ I-06 (Kafka)
       │                     │                     │ I-07 (REST)
       │                     │                     │
       │                     │                     ▼
       │                     │              ┌──────────────┐
       │                     │              │  NASP Real   │
       │                     │              │  (RAN/Trans/ │
       │                     │              │    Core)     │
       │                     │              └──────────────┘
       │                     │
       │                     │
       │                     ▼
       │              ┌──────────────┐
       │              │ UI Dashboard │
       │              │ (2 replicas) │
       │              │ Port: 3000   │
       │              └──────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    Observabilidade (OpenTelemetry)                       │
│  OTLP Collector → Prometheus (monitoring) → Grafana (monitoring)       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    Message Bus (Kafka)                                   │
│  Topics: sem-csmf-nests, ml-nsmf-predictions, decisions, sla-events    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 8.2 Fluxo Interno Intent→Slice→SLA

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FLUXO COMPLETO                                │
└─────────────────────────────────────────────────────────────────────────┘

1. INTENT (Tenant)
   │
   ▼
┌─────────────────┐
│   SEM-CSMF      │  • Recebe intent (linguagem natural ou estruturado)
│                 │  • Processa com NLP
│                 │  • Valida com ontologia OWL
│                 │  • Gera NEST (Network Slice Template)
└────────┬────────┘
         │ I-01 (gRPC)
         │ I-02 (Kafka)
         ▼
┌─────────────────┐
│   ML-NSMF       │  • Recebe NEST via Kafka
│                 │  • Prediz viabilidade de SLA
│                 │  • Gera explicação XAI (SHAP/LIME)
└────────┬────────┘
         │ I-03 (Kafka)
         ▼
┌─────────────────┐
│ Decision Engine │  • Recebe predição ML
│                 │  • Avalia regras de decisão
│                 │  • Toma decisão: ADMIT/REJECT/RECONFIGURE
└────────┬────────┘
         │ I-04 (Kafka)
         │ I-05 (Kafka)
         │ I-07 (REST)
         ▼
┌─────────────────┐
│   BC-NSSMF      │  • Registra SLA em blockchain
│                 │  • Smart contract Solidity
│                 │  • Imutabilidade e auditabilidade
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SLA-Agent Layer │  • Monitora SLOs em RAN/Transport/Core
│  (DaemonSet)    │  • Coleta métricas reais do NASP
│                 │  • Garante conformidade de SLA
└────────┬────────┘
         │ I-06 (Kafka)
         ▼
┌─────────────────┐
│ NASP Adapter    │  • Connects a serviços reais do NASP
│                 │  • Provisiona slices
│                 │  • Coleta métricas
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   NASP Real     │  • RAN Controller
│                 │  • Transport Controller
│                 │  • Core Controller (UPF, AMF, SMF)
└─────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    Observabilidade (Tempo Real)                         │
│  • Métricas: Prometheus                                                 │
│  • Traces: OpenTelemetry                                                │
│  • Logs: Loki (se disponível)                                           │
│  • Dashboards: Grafana                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 8.3 Fluxo de Deploy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FLUXO DE DEPLOY                                 │
└─────────────────────────────────────────────────────────────────────────┘

1. PREPARAÇÃO (node1)
   │
   ├─► Verifiesr cluster Kubernetes
   ├─► Verifiesr CNI Calico
   ├─► Verifiesr StorageClass
   ├─► Verifiesr DNS interno
   ├─► Verifiesr recursos (CPU, memória)
   └─► Verifiesr portas livres
   │
   ▼
2. PRE-FLIGHT CHECKS (Ansible)
   │
   ├─► ansible-playbook pre-flight.yml
   ├─► Validar Kubernetes versão
   ├─► Validar Helm
   ├─► Validar Calico
   ├─► Validar StorageClass
   └─► Validar GHCR autenticação
   │
   ▼
3. SETUP NAMESPACE (Ansible)
   │
   ├─► ansible-playbook setup-namespace.yml
   ├─► Criar namespace trisla
   ├─► Criar secret GHCR
   └─► Criar secrets adicionais
   │
   ▼
4. DEPLOY TRISLA (Ansible + Helm)
   │
   ├─► ansible-playbook deploy-trisla-nasp.yml
   ├─► Validar Helm chart
   ├─► Dry-run do deploy
   ├─► Deploy real (helm upgrade --install)
   ├─► Waitsr pods prontos
   └─► Verifiesr serviços
   │
   ▼
5. VALIDAÇÃO PÓS-DEPLOY (Ansible)
   │
   ├─► ansible-playbook validate-cluster.yml
   ├─► Verifiesr pods em Running
   ├─► Verifiesr readiness probes
   ├─► Verifiesr liveness probes
   └─► Verifiesr health checks
   │
   ▼
6. TESTES E2E (Manual)
   │
   ├─► Testar endpoints REST
   ├─► Testar ciclo fechado TriSLA
   ├─► Validar dashboards Grafana
   ├─► Validar ingestão OTLP
   └─► Validar integration NASP
   │
   ▼
7. PRODUÇÃO APROVADA ✅
```

---

### 8.4 Mapa de Comunicação (Incluindo SLA-Agent Layer)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MAPA DE COMUNICAÇÃO TRISLA                           │
└─────────────────────────────────────────────────────────────────────────┘

INTERFACES:

I-01 (gRPC):     SEM-CSMF ────────────────► Decision Engine
                 Port: 50051

I-02 (Kafka):    SEM-CSMF ────────────────► ML-NSMF
                 Topic: sem-csmf-nests

I-03 (Kafka):    ML-NSMF ─────────────────► Decision Engine
                 Topic: ml-nsmf-predictions

I-04 (Kafka):    Decision Engine ─────────► BC-NSSMF
                 Topic: decisions

I-05 (Kafka):    Decision Engine ─────────► SLA-Agent Layer
                 Topic: sla-commands

I-06 (Kafka):    SLA-Agent Layer ────────► NASP Adapter
                 Topic: sla-metrics

I-07 (REST):     Decision Engine ─────────► NASP Adapter
                 HTTP: POST /nasp-adapter/provision

OBSERVABILIDADE:

OTLP:            Todos os módulos ────────► OTLP Collector
                 Endpoint: otlp-collector:4317

PROMETHEUS:      OTLP Collector ──────────► Prometheus
                 Namespace: monitoring

GRAFANA:         Prometheus ──────────────► Grafana
                 Namespace: monitoring

MESSAGE BUS:

KAFKA:           Todos os módulos ────────► Kafka Broker
                 Bootstrap: kafka:9092
                 Topics: sem-csmf-nests, ml-nsmf-predictions, decisions,
                         sla-commands, sla-metrics

SLA-AGENT LAYER (Distribuído):

node1:           SLA-Agent Layer Pod ─────► NASP Adapter
                 Coleta métricas RAN/Transport/Core

node2:           SLA-Agent Layer Pod ─────► NASP Adapter
                 Coleta métricas RAN/Transport/Core

NASP INTEGRATION:

NASP Adapter ───► NASP Real Services
                 • RAN Controller
                 • Transport Controller
                 • Core Controller (UPF, AMF, SMF)
```

---

## 9. Checklist de Produção (Oficial)

### 9.1 Pré-requisitos Verifiesdos

- [ ] Cluster Kubernetes operacional (2 nodes Ready)
- [ ] CNI Calico funcionando
- [ ] StorageClass disponível (`local-path` ou `nfs`)
- [ ] DNS interno funcionando (CoreDNS)
- [ ] Portas livres (8080-8085, 50051, 9090, 3000, 4317, 9092)
- [ ] Recursos suficientes (CPU ≥ 16 cores, RAM ≥ 32 GiB)
- [ ] `kubectl` configurado e conectado
- [ ] `helm` instalado (versão ≥ 3.12)
- [ ] `ansible` instalado (versão ≥ 2.14)
- [ ] Acesso ao GHCR configurado (token e secret criado)

---

### 9.2 Inventário Final Aprovado

- [ ] `ansible/inventory.yaml` configurado (127.0.0.1, local)
- [ ] `ansible/group_vars/all.yml` preenchido
- [ ] Variáveis de rede configuradas (interface, IPs, gateway)
- [ ] Variáveis do TriSLA configuradas (namespace, registry, tags)
- [ ] Variáveis de produção configuradas (simulation_mode: false)

---

### 9.3 Variáveis Corretas

- [ ] `helm/trisla/values-nasp.yaml` preenchido com valores reais
- [ ] Todos os placeholders substituídos
- [ ] Endpoints NASP configurados (FQDNs Kubernetes)
- [ ] Autenticação OAuth2 configurada (se necessário)
- [ ] Recursos ajustados para produção
- [ ] Replicas configuradas corretamente

---

### 9.4 Playbooks Revisados

- [ ] `ansible/playbooks/pre-flight.yml` revisado
- [ ] `ansible/playbooks/setup-namespace.yml` revisado
- [ ] `ansible/playbooks/deploy-trisla-nasp.yml` revisado
- [ ] `ansible/playbooks/validate-cluster.yml` revisado
- [ ] Pré-checagem executada (`--check`) sem erros críticos

---

### 9.5 Portas Livres

- [ ] Porta 8080 (SEM-CSMF) livre
- [ ] Porta 8081 (ML-NSMF) livre
- [ ] Porta 8082 (Decision Engine) livre
- [ ] Porta 8083 (BC-NSSMF) livre
- [ ] Porta 8084 (SLA-Agent Layer) livre
- [ ] Porta 8085 (NASP Adapter) livre
- [ ] Porta 50051 (gRPC) livre
- [ ] Porta 3000 (UI Dashboard) livre

---

### 9.6 Storage OK

- [ ] StorageClass disponível
- [ ] PVCs criados (se necessário)
- [ ] Volumes persistentes funcionando
- [ ] Capacidade suficiente

---

### 9.7 Deploy Aplicado

- [ ] Pre-flight checks executados com sucesso
- [ ] Namespace criado
- [ ] Secrets criados
- [ ] Helm chart validado
- [ ] Deploy executado (`helm upgrade --install`)
- [ ] Todos os pods em `Running`
- [ ] Todos os serviços criados
- [ ] Readiness probes passando
- [ ] Liveness probes passando

---

### 9.8 Services Respondendo

- [ ] SEM-CSMF health check OK (`/health`)
- [ ] ML-NSMF health check OK (`/health`)
- [ ] BC-NSSMF health check OK (`/health`)
- [ ] Decision Engine health check OK (`/health`)
- [ ] SLA-Agent Layer health check OK (`/health`)
- [ ] NASP Adapter health check OK (`/health`)
- [ ] UI Dashboard acessível

---

### 9.9 Dashboards Ativos

- [ ] Prometheus acessível (port-forward ou NodePort)
- [ ] Grafana acessível (port-forward ou NodePort)
- [ ] Dashboards TriSLA carregados
- [ ] Métricas sendo coletadas
- [ ] Gráficos atualizando
- [ ] Alertas configurados (se aplicável)

---

### 9.10 Produção Aprovada

- [ ] Testes E2E executados com sucesso
- [ ] Ciclo fechado TriSLA validado
- [ ] Integração NASP funcionando
- [ ] Observabilidade funcionando
- [ ] Documentação atualizada
- [ ] Rollback testado (se necessário)

---

## 10. Conclusão

This document provides a complete guide, formal e acadêmico para a implantação manual do TriSLA v3.5.0 in the NASP environment utilizando Ansible e Helm. O processo é dividido em fases claras, desde a preparação inicial até a validação end-to-end, garantindo um deploy controlado e auditável.

### Principais Características

- **Deploy Local:** Execução no node1 (127.0.0.1), sem SSH
- **Automação:** Ansible para orquestração, Helm para gerenciamento
- **Produção Real:** Configurações para ambiente de produção, sem simulação
- **Observabilidade:** Integração completa com Prometheus, Grafana e OpenTelemetry
- **Alta Disponibilidade:** Réplicas configuradas para todos os módulos
- **Distribuição:** SLA-Agent Layer distribuído em node1 e node2

### Próximos Passos

Após a conclusão bem-sucedida do deploy:

1. **Monitoramento Contínuo:** Acompanhar métricas e logs
2. **Otimização:** Ajustar recursos conforme necessário
3. **Manutenção:** Atualizar imagens e configurações
4. **Expansão:** Adicionar novos módulos ou funcionalidades

---

## 11. Referências

### Documentação TriSLA

- **README Main:** `README.md`
- **Guia SEM-CSMF:** `docs/sem-csmf/SEM_CSMF_COMPLETE_GUIDE.md`
- **Guia Ontologia:** `docs/sem-csmf/ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`
- **Guia ML-NSMF:** `docs/ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md`
- **Guia BC-NSSMF:** `docs/bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md`
- **Relatório Validação Produção:** `docs/reports/PRODUCTION_VALIDATION_REPORT_v3.5.0.md`

### Documentação NASP

- **Guia Deploy NASP:** `docs/nasp/NASP_DEPLOY_GUIDE.md`
- **Runbook Deploy:** `docs/nasp/NASP_DEPLOY_RUNBOOK.md`
- **Checklist Pré-Deploy:** `docs/nasp/NASP_PREDEPLOY_CHECKLIST_v2.md`
- **Relatório Contexto:** `docs/nasp/NASP_CONTEXT_REPORT.md`

### Arquivos de Configuração

- **Values NASP:** `helm/trisla/values-nasp.yaml`
- **Inventory Ansible:** `ansible/inventory.yaml`
- **Playbooks:** `ansible/playbooks/`

---

**Fim do Documento**

**Versão:** 3.5.0  
**Data:** 2025-01-27  
**Status:** Documento Oficial de Produção  
**Autor:** TriSLA Team

