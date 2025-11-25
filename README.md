# TriSLA — Trustworthy, Reasoned and Intelligent SLA Architecture

[![Version](https://img.shields.io/badge/version-3.5.0-blue.svg)](https://github.com/abelisboa/TriSLA)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Kubernetes](https://img.shields.io/badge/kubernetes-1.29%2B-blue.svg)](https://kubernetes.io/)
[![Helm](https://img.shields.io/badge/helm-3.14%2B-blue.svg)](https://helm.sh/)

**TriSLA** é uma arquitetura **SLA-Aware, explicável e automatizada** para garantia de Service Level Agreements (SLAs) em redes 5G e O-RAN. A arquitetura integra Inteligência Artificial, Ontologias Semânticas e Blockchain para fornecer um sistema de gerenciamento de network slicing com closed-loop assurance, transparência e auditabilidade.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura Geral](#-arquitetura-geral)
- [Requisitos](#-requisitos)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Deploy Local no NASP](#-deploy-local-no-nasp)
- [Deploy via Ansible (Modo Local)](#-deploy-via-ansible-modo-local)
- [Arquivo Canônico values-nasp.yaml](#-arquivo-canônico-values-naspyaml)
- [Testes E2E](#-testes-e2e)
- [Como Contribuir](#-como-contribuir)
- [Licença](#-licença)
- [Links Úteis](#-links-úteis)

---

## 🎯 Visão Geral

### Objetivo da Arquitetura

O **TriSLA** foi projetado para resolver os desafios críticos de gerenciamento de SLAs em ambientes 5G/O-RAN, oferecendo:

- **Interpretação Semântica Inteligente**: Processamento de intenções de alto nível usando ontologias OWL
- **Predição Baseada em ML**: Antecipação de violações de SLA usando modelos LSTM com explicações (XAI)
- **Decisão Automatizada**: Motor de decisão baseado em regras para ações corretivas
- **Registro Imutável**: Blockchain para auditoria e compliance de SLAs
- **Agentes Federados**: Coleta e execução distribuída em domínios RAN, Transport e Core
- **Observabilidade Completa**: Métricas, logs e traces via OpenTelemetry, Prometheus e Grafana

### Integração com O-RAN / 5G

O TriSLA integra-se nativamente com ambientes **O-RAN** e **5G** através de:

- **NASP Adapter**: Interface com controladores NASP (RAN, Transport, Core)
- **Interfaces Padronizadas**: Suporte a interfaces I-01 a I-07 conforme especificações O-RAN
- **Network Slicing**: Gerenciamento automático de network slices com garantia de SLA
- **Closed-Loop Assurance**: Ciclo completo de monitoramento, análise, decisão e execução

### Módulos Principais

| Módulo | Descrição | Tecnologia |
|--------|-----------|------------|
| **SEM-CSMF** | Interpretação Semântica e geração de NEST | Python, OWL, PostgreSQL, gRPC |
| **ML-NSMF** | Predição de viabilidade de SLA | Python, LSTM, XAI, Kafka |
| **Decision Engine** | Motor de decisão baseado em regras | Python, YAML Rules, Kafka |
| **BC-NSSMF** | Smart Contracts para registro de SLA | Python, Solidity, Besu/GoQuorum |
| **SLA-Agent Layer** | Agentes federados por domínio | Python, Kafka, YAML Config |
| **NASP Adapter** | Integração com ambiente NASP | Python, REST, gRPC |
| **UI Dashboard** | Interface visual para operadores | TypeScript, React, Vite |

---

## 🏗️ Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                    TriSLA Architecture                          │
│              (Trustworthy, Reasoned, Intelligent SLA)           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Tenant     │  ──I-01──>  ┌──────────────┐
│   Portal     │             │  SEM-CSMF    │  (Semantic Interpretation)
└──────────────┘             │  (Intent →   │
                             │   NEST)      │
                             └──────┬───────┘
                                    │ I-02
                                    ▼
                             ┌──────────────┐
                             │   ML-NSMF    │  (ML Prediction + XAI)
                             │  (Viability  │
                             │  Prediction) │
                             └──────┬───────┘
                                    │ I-03
                                    ▼
                             ┌──────────────┐
                             │   Decision   │  (Rule-Based Decision)
                             │   Engine     │
                             │  (Actions)   │
                             └──────┬───────┘
                                    │ I-04
                                    ▼
                             ┌──────────────┐
                             │   BC-NSSMF   │  (Blockchain Registration)
                             │  (Smart      │
                             │  Contracts)  │
                             └──────┬───────┘
                                    │ I-05
                                    ▼
                             ┌──────────────┐
                             │ SLA-Agent    │  (Federated Agents)
                             │   Layer      │
                             │  (RAN/Trans/ │
                             │   Core)      │
                             └──────┬───────┘
                                    │ I-06, I-07
                                    ▼
                             ┌──────────────┐
                             │  NASP        │  (NASP Integration)
                             │  Adapter     │
                             └──────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Observability Stack                          │
│  OpenTelemetry Collector → Prometheus → Grafana                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Message Bus (Kafka)                         │
│  Topics: I-02, I-03, I-04, I-05, I-06, I-07                    │
└─────────────────────────────────────────────────────────────────┘
```

### Diagramas e Documentação de Arquitetura

Para diagramas detalhados e documentação completa da arquitetura, consulte:

- **Documentação de Arquitetura**: [`docs/architecture/`](docs/architecture/)
- **Figuras e Diagramas**: Diagramas Draw.io e ilustrações técnicas
- **Especificações de Interfaces**: Documentação das interfaces I-01 a I-07
- **Guia da Ontologia TriSLA**: [`docs/ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md`](docs/ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md) — Guia completo da ontologia OWL, classes, propriedades, diagramas Protégé
- **Guia do ML-NSMF**: [`docs/ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md`](docs/ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md) — Guia completo do módulo ML, treinamento de modelos e XAI
- **Guia do BC-NSSMF**: [`docs/bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md`](docs/bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md) — Guia completo do módulo Blockchain, smart contracts, integração Web3 e deploy
- **Relatório de Validação Produção**: [`docs/reports/PRODUCTION_VALIDATION_REPORT_v3.5.0.md`](docs/reports/PRODUCTION_VALIDATION_REPORT_v3.5.0.md) — Análise completa de todos os módulos para produção real no NASP

---

## 📦 Requisitos

### Requisitos de Sistema

| Componente | Versão Mínima | Versão Recomendada | Notas |
|------------|---------------|-------------------|-------|
| **Kubernetes** | 1.26+ | 1.29+ | Cluster com CNI (Calico recomendado) |
| **Helm** | 3.12+ | 3.14+ | Gerenciador de pacotes Kubernetes |
| **Docker/Containerd** | 20.10+ | Latest | Runtime de containers |
| **kubectl** | 1.26+ | 1.29+ | Cliente Kubernetes |
| **Python** | 3.10+ | 3.11+ | Para scripts auxiliares |
| **Git** | 2.30+ | Latest | Controle de versão |

### Requisitos de Ambiente NASP

- **NASP instalado no Node1**: Cluster Kubernetes operacional
- **Acesso local ao node**: Você já está dentro do node1 do NASP
- **Projeto localizado**: `/home/porvir5g/gtp5g/trisla`
- **kubectl configurado**: Acesso ao cluster Kubernetes
- **Helm instalado**: Versão 3.14 ou superior

### Requisitos de Recursos

**Por Pod (mínimo):**
- CPU: 500m (request) / 2000m (limit)
- Memória: 512Mi (request) / 2Gi (limit)

**Cluster Total (recomendado):**
- CPU: 16 cores
- Memória: 32 GiB
- Storage: 200 GiB (para volumes persistentes)

### Requisitos de Rede

- **Conectividade entre pods**: CNI funcional (Calico)
- **DNS interno**: CoreDNS operacional
- **Acesso a NASP**: Endpoints RAN, Transport e Core acessíveis
- **Portas**: Portas padrão do Kubernetes (6443, 10250, etc.)

---

## 📁 Estrutura do Repositório

```
TriSLA/
├── apps/                          # Aplicações principais
│   ├── sem-csmf/                 # Interpretação Semântica
│   │   ├── src/                  # Código-fonte Python
│   │   ├── ontology/             # Ontologias OWL
│   │   ├── Dockerfile            # Imagem Docker
│   │   └── requirements.txt       # Dependências Python
│   ├── ml-nsmf/                  # Predição ML
│   │   ├── src/                  # Código-fonte
│   │   ├── models/               # Modelos LSTM treinados
│   │   └── training/             # Scripts de treinamento
│   ├── decision-engine/          # Motor de Decisão
│   │   ├── src/                  # Código-fonte
│   │   └── config/               # Regras de decisão (YAML)
│   ├── bc-nssmf/                 # Blockchain NSSMF
│   │   ├── src/                  # Código-fonte
│   │   ├── contracts/            # Smart Contracts Solidity
│   │   └── blockchain/           # Configuração Besu
│   ├── sla-agent-layer/          # Agentes Federados
│   │   ├── src/                  # Código-fonte
│   │   └── src/config/           # Configurações SLO por domínio
│   ├── nasp-adapter/             # Adaptador NASP
│   │   └── src/                  # Integração com NASP
│   └── ui-dashboard/             # Dashboard Web
│       └── src/                  # Interface React/TypeScript
│
├── helm/                          # Helm Charts
│   └── trisla/                   # Chart principal
│       ├── Chart.yaml            # Metadados do chart
│       ├── values.yaml           # Valores padrão
│       ├── values-nasp.yaml      # ⭐ Valores canônicos para NASP
│       └── templates/            # Templates Kubernetes
│           ├── deployment-*.yaml
│           ├── service-*.yaml
│           ├── configmap.yaml
│           └── secret-ghcr.yaml
│
├── ansible/                       # Automação Ansible
│   ├── inventory.yaml            # Inventário (127.0.0.1 local)
│   ├── ansible.cfg               # Configuração Ansible
│   ├── playbooks/                # Playbooks de deploy
│   │   ├── deploy-trisla-nasp.yml
│   │   ├── validate-cluster.yml
│   │   ├── pre-flight.yml
│   │   └── setup-namespace.yml
│   └── group_vars/               # Variáveis por grupo
│       ├── all.yml
│       ├── control_plane.yml
│       └── workers.yml
│
├── scripts/                       # Scripts de automação
│   ├── deploy-trisla-nasp-auto.sh    # ⭐ Deploy automático
│   ├── fill_values_production.sh     # Preparar values-nasp.yaml
│   ├── discover-nasp-endpoints.sh    # Descobrir endpoints NASP
│   ├── prepare-nasp-deploy.sh        # Preparar ambiente
│   ├── pre-check-nasp.sh             # Pré-verificações
│   ├── complete-e2e-test.sh          # Testes E2E
│   └── ...                         # Outros scripts utilitários
│
├── docs/                          # Documentação completa
│   ├── nasp/                     # Documentação NASP
│   ├── ontology/                 # Documentação da Ontologia OWL
│   │   └── ONTOLOGY_IMPLEMENTATION_GUIDE.md
│   ├── ml-nsmf/                  # Documentação do ML-NSMF
│   │   └── ML_NSMF_COMPLETE_GUIDE.md
│   ├── bc-nssmf/                 # Documentação do BC-NSSMF
│   │   └── BC_NSSMF_COMPLETE_GUIDE.md
│   │   ├── NASP_DEPLOY_GUIDE.md
│   │   ├── NASP_DEPLOY_RUNBOOK.md
│   │   └── NASP_PREDEPLOY_CHECKLIST_v2.md
│   ├── deployment/               # Guias de deploy
│   │   ├── VALUES_PRODUCTION_GUIDE.md
│   │   ├── DEVELOPER_GUIDE.md
│   │   └── INSTALL_FULL_PROD.md
│   ├── architecture/             # Arquitetura e diagramas
│   ├── reports/                  # Relatórios técnicos
│   └── security/                 # Segurança e hardening
│
├── monitoring/                    # Observabilidade
│   ├── prometheus/               # Configuração Prometheus
│   ├── grafana/                  # Dashboards Grafana
│   ├── otel-collector/           # OpenTelemetry Collector
│   └── alertmanager/             # Alertas
│
├── tests/                         # Testes automatizados
│   ├── unit/                     # Testes unitários
│   ├── integration/              # Testes de integração
│   └── e2e/                      # Testes end-to-end
│
└── README.md                      # Este arquivo
```

---

## 🚀 Deploy Local no NASP

O deploy do TriSLA no ambiente NASP é realizado no Node onde o cluster Kubernetes está rodando.

### Pré-requisitos

Antes de iniciar o deploy, certifique-se de que:

- ✅ Você já está dentro do node1 do NASP
- ✅ O projeto está localizado em `~/gtp5g/trisla`
- ✅ `kubectl` está configurado e conectado ao cluster
- ✅ `helm` versão 3.14+ está instalado
- ✅ Cluster Kubernetes está operacional

### Fluxo Oficial de Deploy

#### 1. Início

```bash
cd ~/gtp5g/trisla
```

**Verificar ambiente:**
```bash
# Verificar acesso ao cluster
kubectl cluster-info

# Verificar nós
kubectl get nodes

# Verificar Helm
helm version
```

#### 2. Preparar Valores

O arquivo canônico `helm/trisla/values-nasp.yaml` já está configurado com valores padrão do NASP.

**Se necessário, descobrir endpoints NASP:**
```bash
./scripts/discover-nasp-endpoints.sh
```

**Editar valores manualmente (se necessário):**
```bash
vim helm/trisla/values-nasp.yaml
```

**Se necessário, descobrir endpoints NASP:**
```bash
./scripts/discover-nasp-endpoints.sh
```

#### 3. Validar

```bash
helm lint ./helm/trisla
```

**Validação com values:**
```bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
```

**Validação esperada:**
- ✅ Chart válido
- ✅ Sem erros de sintaxe
- ✅ Valores corretos

#### 4. Deploy Automático

```bash
./scripts/deploy-trisla-nasp-auto.sh
```

Este script executa automaticamente:
1. Preparação do ambiente (namespace, secrets)
2. Validação do Helm chart
3. Deploy do TriSLA via Helm
4. Verificação do status dos pods

#### 5. Verificar Saúde

```bash
kubectl get pods -n trisla
```

**Comandos adicionais úteis:**
```bash
# Verificar serviços
kubectl get svc -n trisla

# Verificar eventos
kubectl get events -n trisla --sort-by='.lastTimestamp'

# Verificar logs de um pod específico
kubectl logs -n trisla <pod-name> -f

# Verificar status completo
kubectl get all -n trisla

# Verificar Helm release
helm status trisla -n trisla
```

### Deploy Manual (Alternativo)

Se preferir executar o deploy manualmente:

```bash
cd ~/gtp5g/trisla

# Criar namespace (se não existir)
kubectl create namespace trisla --dry-run=client -o yaml | kubectl apply -f -

# Criar secret do GHCR (se necessário)
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USER> \
  --docker-password=<GITHUB_TOKEN> \
  --docker-email=<EMAIL> \
  -n trisla \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy via Helm
helm upgrade --install trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --create-namespace \
  --wait \
  --timeout 15m
```

### Documentação Completa de Deploy

Para instruções detalhadas, consulte:

- **Guia Completo**: [`docs/nasp/NASP_DEPLOY_GUIDE.md`](docs/nasp/NASP_DEPLOY_GUIDE.md)
- **Runbook Operacional**: [`docs/nasp/NASP_DEPLOY_RUNBOOK.md`](docs/nasp/NASP_DEPLOY_RUNBOOK.md)
- **Checklist Pré-Deploy**: [`docs/nasp/NASP_PREDEPLOY_CHECKLIST_v2.md`](docs/nasp/NASP_PREDEPLOY_CHECKLIST_v2.md)

---

## 🔧 Deploy via Ansible (Modo Local)

O TriSLA inclui playbooks Ansible para automação completa do deploy. Todos os playbooks são executados **localmente no node1** (127.0.0.1), sem necessidade de SSH ou acesso remoto.

### Configuração do Ansible

O Ansible está configurado para operação **100% local**:

**Inventário (`ansible/inventory.yaml`):**
```yaml
[nasp]
127.0.0.1 ansible_connection=local ansible_python_interpreter=/usr/bin/python3
```

**Configuração (`ansible/ansible.cfg`):**
- `inventory = inventory.yaml`
- Sem seção `[ssh_connection]` (deploy local)
- `become = True` (elevação de privilégios local)

### Estrutura dos Playbooks

```
ansible/
├── inventory.yaml              # ⭐ Inventário local (127.0.0.1)
├── ansible.cfg                 # Configuração Ansible
├── playbooks/                  # Playbooks de deploy
│   ├── pre-flight.yml          # Validações pré-deploy
│   ├── validate-cluster.yml     # Validação do cluster
│   ├── setup-namespace.yml      # Criação de namespace
│   └── deploy-trisla-nasp.yml  # Deploy completo
└── group_vars/                 # Variáveis por grupo
    ├── all.yml                 # Variáveis globais
    ├── control_plane.yml       # Variáveis do control plane
    └── workers.yml             # Variáveis dos workers
```

### Características dos Playbooks

Todos os playbooks seguem o padrão local:

```yaml
- name: <Nome do Playbook>
  hosts: nasp                    # Grupo local (127.0.0.1)
  connection: local              # Execução local
  become: yes                    # Elevação de privilégios
  gather_facts: no               # Sem coleta de facts (otimização)
```

### Playbooks Disponíveis

#### 1. Pre-Flight Checks

**Objetivo:** Validar que o cluster está pronto para receber o TriSLA.

```bash
cd ~/gtp5g/trisla
cd ansible
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml
```

**Validações realizadas:**
- ✅ Versão do Kubernetes (≥ 1.26)
- ✅ Helm instalado e funcional
- ✅ Calico operacional
- ✅ StorageClass disponível
- ✅ Namespace pode ser criado
- ✅ Autenticação GHCR configurada

#### 2. Validação do Cluster

**Objetivo:** Verificar saúde e configuração do cluster Kubernetes.

```bash
cd ~/gtp5g/trisla
cd ansible
ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml
```

**Verificações:**
- ✅ Conectividade com o cluster
- ✅ Nós do cluster acessíveis
- ✅ CoreDNS operacional
- ✅ CNI (Calico) funcional
- ✅ StorageClass disponível

#### 3. Setup do Namespace

**Objetivo:** Criar namespace e configurar recursos básicos.

```bash
cd ~/gtp5g/trisla
cd ansible
ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml
```

**Ações realizadas:**
- Criação do namespace `trisla`
- Verificação de criação bem-sucedida

#### 4. Deploy Completo do TriSLA

**Objetivo:** Deploy completo do TriSLA via Helm.

```bash
cd ~/gtp5g/trisla
cd ansible
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml
```

**Processo executado:**
1. Validação de pré-requisitos
2. Criação de namespace (se necessário)
3. Configuração de secrets (GHCR)
4. Validação do Helm chart
5. Dry-run do deploy
6. Deploy real do TriSLA
7. Verificação de status dos pods
8. Validação do deploy

### Fluxo Completo via Ansible

**Deploy completo automatizado:**

```bash
cd ~/gtp5g/trisla

# 1. Pre-flight checks
cd ansible
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml

# 2. Validar cluster
ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml

# 3. Setup namespace
ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml

# 4. Deploy TriSLA
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml
```

### Variáveis Ansible

As variáveis são definidas em `ansible/group_vars/all.yml`:

```yaml
# Configurações do TriSLA
trisla:
  namespace: "trisla"
  image_registry: "ghcr.io/abelisboa"
  image_pull_secret: "ghcr-secret"

# Configurações de produção
production:
  enabled: true
  simulationMode: false
  useRealServices: true
  executeRealActions: true
```

### Vantagens do Deploy via Ansible

- ✅ **Idempotência**: Execução segura múltiplas vezes
- ✅ **Automação completa**: Deploy em um único comando
- ✅ **Validações integradas**: Verificações automáticas antes do deploy
- ✅ **Operação local**: Sem dependências de SSH ou acesso remoto
- ✅ **Auditabilidade**: Logs detalhados de todas as operações

### Troubleshooting Ansible

**Verificar inventário:**
```bash
ansible-inventory -i inventory.yaml --list
```

**Testar conectividade:**
```bash
ansible nasp -i inventory.yaml -m ping
```

**Executar com verbose:**
```bash
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml -v
```

**Executar com debug:**
```bash
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml -vvv
```

### Documentação Ansible

Para mais informações sobre Ansible, consulte:

- **README Ansible**: [`ansible/README.md`](ansible/README.md)

---

## 🔄 Fluxo de Automação DevOps

O TriSLA implementa um fluxo DevOps completo e automatizado que integra scripts, Ansible e Helm para garantir deploy consistente e reproduzível.

### Visão Geral do Fluxo

```
┌─────────────────────────────────────────────────────────┐
│           Fluxo DevOps TriSLA - Deploy NASP             │
└─────────────────────────────────────────────────────────┘

FASE 0: Pré-Checks
├── Verificar cluster Kubernetes
├── Verificar kubectl e helm
└── Verificar conectividade NASP

FASE 1: Preparação
├── Criar namespace trisla
├── Configurar secrets (GHCR)
└── Validar ambiente

FASE 2: Configuração
├── Descobrir endpoints NASP (opcional)
├── Preparar values-nasp.yaml
└── Validar configuração

FASE 3: Validação
├── helm lint
├── helm template (dry-run)
└── Verificar recursos

FASE 4: Deploy
├── helm upgrade --install trisla
├── Aguardar pods prontos
└── Verificar status

FASE 5: Validação Pós-Deploy
├── Health checks
├── Testes E2E básicos
└── Verificar interfaces I-01 a I-07
```

### Métodos de Deploy Disponíveis

#### 1. Script Automatizado (Recomendado)

**Comando único:**
```bash
cd ~/gtp5g/trisla
./scripts/deploy-trisla-nasp-auto.sh
```

**O que executa:**
- ✅ FASE 1: Preparação (namespace, secrets)
- ✅ FASE 2: Validação Helm (lint + template)
- ✅ FASE 3: Deploy (helm upgrade --install)
- ✅ FASE 4: Validação pós-deploy (pods, serviços)

#### 2. Scripts Individuais

**Fluxo passo a passo:**
```bash
cd ~/gtp5g/trisla

# FASE 0: Pré-checks
./scripts/pre-check-nasp.sh

# FASE 1: Preparação
./scripts/prepare-nasp-deploy.sh

# FASE 2: Configuração (se necessário)
./scripts/discover-nasp-endpoints.sh
vim helm/trisla/values-nasp.yaml

# FASE 3: Validação
./scripts/validate-helm.sh

# FASE 4: Deploy
./scripts/deploy-trisla-nasp.sh --helm-install

# FASE 5: Validação
./scripts/validate-production-real.sh
```

#### 3. Ansible Playbooks

**Deploy completo via Ansible:**
```bash
cd ~/gtp5g/trisla

# FASE 0: Pre-flight
cd ansible
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml

# FASE 1: Setup namespace
ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml

# FASE 2-4: Deploy completo
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml
```

#### 4. Helm Manual

**Deploy direto via Helm:**
```bash
cd ~/gtp5g/trisla

# FASE 3: Validação
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug

# FASE 4: Deploy
helm upgrade --install trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --create-namespace \
  --wait \
  --timeout 15m
```

### Scripts Principais do Fluxo DevOps

| Script | Fase | Descrição |
|--------|------|-----------|
| `pre-check-nasp.sh` | 0 | Pré-verificações do cluster NASP |
| `prepare-nasp-deploy.sh` | 1 | Preparação (namespace, secrets) |
| `discover-nasp-endpoints.sh` | 2 | Descobrir endpoints NASP |
| `fill_values_production.sh` | 2 | Preparar values-nasp.yaml |
| `validate-helm.sh` | 3 | Validar Helm chart |
| `deploy-trisla-nasp-auto.sh` | 1-4 | Deploy automático completo |
| `deploy-trisla-nasp.sh` | 4 | Deploy manual via Helm |
| `validate-production-real.sh` | 5 | Validação pós-deploy |
| `complete-e2e-test.sh` | 5 | Testes E2E completos |

### Integração Scripts ↔ Ansible ↔ Helm

**Ordem de execução recomendada:**

1. **Scripts de preparação** → Preparam ambiente e valores
2. **Ansible playbooks** → Validam e configuram infraestrutura
3. **Helm charts** → Deployem aplicação

**Exemplo de fluxo integrado:**
```bash
cd ~/gtp5g/trisla

# Preparação via scripts
./scripts/prepare-nasp-deploy.sh
./scripts/discover-nasp-endpoints.sh

# Validação via Ansible
cd ansible
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml

# Deploy via Helm (via script ou Ansible)
cd ..
./scripts/deploy-trisla-nasp-auto.sh
# OU
cd ansible
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml
```

### Validações Automáticas

O fluxo DevOps inclui validações automáticas em cada fase:

- ✅ **Pré-checks**: Cluster, kubectl, helm, conectividade
- ✅ **Preparação**: Namespace, secrets, recursos
- ✅ **Configuração**: Sintaxe YAML, valores obrigatórios
- ✅ **Validação**: Helm lint, template validation
- ✅ **Deploy**: Status dos pods, health checks
- ✅ **Pós-deploy**: Interfaces I-01 a I-07, E2E tests

### Documentação do Fluxo DevOps

Para mais informações sobre o fluxo DevOps:

- **Guia de Deploy**: [`docs/nasp/NASP_DEPLOY_GUIDE.md`](docs/nasp/NASP_DEPLOY_GUIDE.md)
- **Runbook Operacional**: [`docs/nasp/NASP_DEPLOY_RUNBOOK.md`](docs/nasp/NASP_DEPLOY_RUNBOOK.md)
- **Guia de Valores**: [`docs/deployment/VALUES_PRODUCTION_GUIDE.md`](docs/deployment/VALUES_PRODUCTION_GUIDE.md)

---

## 🔌 Interfaces TriSLA (I-01 a I-07)

O TriSLA implementa **7 interfaces padronizadas** que definem o fluxo completo de processamento de SLAs, desde a recepção de intenções até a execução de ações nos controladores NASP.

### Visão Geral das Interfaces

```
┌─────────────┐
│   Tenant    │
│   Portal    │
└──────┬──────┘
       │ I-01 (HTTP/gRPC)
       ▼
┌─────────────┐
│  SEM-CSMF   │ ──I-02 (Kafka)──> ┌─────────────┐
│ (Intent →   │                    │   ML-NSMF   │
│   NEST)     │                    │ (Prediction)│
└─────────────┘                    └──────┬──────┘
                                           │ I-03 (Kafka)
                                           ▼
                                    ┌─────────────┐
                                    │  Decision   │
                                    │   Engine    │
                                    │  (Actions)  │
                                    └──────┬──────┘
                                           │ I-04 (Kafka)
                                           ├───I-05 (gRPC)──> ┌─────────────┐
                                           │                  │  BC-NSSMF   │
                                           │                  │ (Blockchain)│
                                           ├───I-06 (Kafka)──> └─────────────┘
                                           │                  ┌─────────────┐
                                           │                  │ SLA-Agent   │
                                           │                  │   Layer     │
                                           └───I-07 (REST)──> └──────┬──────┘
                                                                     │
                                                                     ▼
                                                              ┌─────────────┐
                                                              │   NASP      │
                                                              │  Adapter    │
                                                              └──────┬──────┘
                                                                     │
                                                                     ▼
                                                              ┌─────────────┐
                                                              │    NASP     │
                                                              │ (RAN/Core/  │
                                                              │ Transport)  │
                                                              └─────────────┘
```

### Interface I-01: Recepção de Intenções

**Módulo:** SEM-CSMF  
**Protocolo:** HTTP REST / gRPC  
**Endpoint:** `POST /api/v1/intents`

**Descrição:** Interface de entrada do TriSLA. Recebe intenções de alto nível dos tenants e inicia o processamento semântico.

**Payload de Entrada:**
```json
{
  "intent_id": "urllc-slice-001",
  "tenant_id": "tenant-abc",
  "service_type": "URLLC",
  "sla_requirements": {
    "latency": "5ms",
    "throughput": "10Mbps",
    "reliability": 0.99999,
    "availability": 0.999
  },
  "slice_config": {
    "domain": "RAN",
    "priority": "high"
  }
}
```

**Resposta:**
```json
{
  "intent_id": "urllc-slice-001",
  "status": "accepted",
  "nest_id": "nest-urllc-001",
  "message": "Intent recebido e processado"
}
```

**Validação:**
- ✅ Sintaxe JSON válida
- ✅ Campos obrigatórios presentes
- ✅ Valores de SLA dentro de limites aceitáveis

---

### Interface I-02: Processamento Semântico → ML

**Módulo:** SEM-CSMF → ML-NSMF  
**Protocolo:** Kafka  
**Topic:** `I-02-intent-to-ml`

**Descrição:** Interface assíncrona que transmite NEST (Network Slice Template) gerado pelo SEM-CSMF para o ML-NSMF para predição de viabilidade.

**Mensagem Kafka:**
```json
{
  "nest_id": "nest-urllc-001",
  "intent_id": "urllc-slice-001",
  "tenant_id": "tenant-abc",
  "nest": {
    "slice_type": "URLLC",
    "requirements": {
      "latency_ms": 5,
      "throughput_mbps": 10,
      "reliability": 0.99999
    },
    "domain_config": {
      "ran": {
        "cell_density": "high",
        "mimo_layers": 4
      },
      "core": {
        "upf_location": "edge",
        "amf_pool_size": 2
      }
    }
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

**Validação:**
- ✅ NEST válido conforme ontologia OWL
- ✅ Requisitos de SLA coerentes
- ✅ Configuração de domínios válida

---

### Interface I-03: Predição ML → Decisão

**Módulo:** ML-NSMF → Decision Engine  
**Protocolo:** Kafka  
**Topic:** `I-03-ml-predictions`

**Descrição:** Interface que transmite predições de viabilidade de SLA (com explicações XAI) do ML-NSMF para o Decision Engine.

**Mensagem Kafka:**
```json
{
  "prediction_id": "pred-urllc-001",
  "nest_id": "nest-urllc-001",
  "intent_id": "urllc-slice-001",
  "viability": {
    "is_viable": true,
    "confidence": 0.92,
    "predicted_latency_ms": 4.2,
    "predicted_throughput_mbps": 11.5,
    "predicted_reliability": 0.99995
  },
  "xai_explanation": {
    "key_factors": [
      {
        "factor": "cell_density",
        "impact": "high",
        "reason": "Alta densidade de células garante latência baixa"
      },
      {
        "factor": "upf_location",
        "impact": "medium",
        "reason": "UPF no edge reduz latência de transporte"
      }
    ],
    "risk_factors": [
      {
        "factor": "network_congestion",
        "risk_level": "low",
        "mitigation": "Monitorar carga de rede"
      }
    ]
  },
  "timestamp": "2025-01-27T10:00:05Z"
}
```

**Validação:**
- ✅ Predição contém viabilidade e confiança
- ✅ Explicação XAI presente
- ✅ Fatores de risco identificados

---

### Interface I-04: Decisão → Ações

**Módulo:** Decision Engine → BC-NSSMF / SLA-Agent Layer  
**Protocolo:** Kafka  
**Topics:** `trisla-i04-decisions`, `trisla-i05-actions`

**Descrição:** Interface que transmite decisões automatizadas do Decision Engine para registro em blockchain (I-05) e execução via SLA-Agent Layer (I-06).

**Mensagem Kafka (Decisão):**
```json
{
  "decision_id": "dec-urllc-001",
  "prediction_id": "pred-urllc-001",
  "nest_id": "nest-urllc-001",
  "intent_id": "urllc-slice-001",
  "decision": {
    "action": "approve",
    "reason": "SLA viável com alta confiança (0.92)",
    "conditions": [
      "Monitorar latência a cada 5 minutos",
      "Alertar se latência > 6ms",
      "Escalar recursos se necessário"
    ]
  },
  "actions": [
    {
      "type": "provision_slice",
      "domain": "RAN",
      "config": {
        "cell_density": "high",
        "mimo_layers": 4
      }
    },
    {
      "type": "provision_slice",
      "domain": "Core",
      "config": {
        "upf_location": "edge",
        "amf_pool_size": 2
      }
    }
  ],
  "timestamp": "2025-01-27T10:00:10Z"
}
```

**Validação:**
- ✅ Decisão clara (approve/reject/modify)
- ✅ Ações específicas por domínio
- ✅ Condições de monitoramento definidas

---

### Interface I-05: Registro em Blockchain

**Módulo:** Decision Engine → BC-NSSMF  
**Protocolo:** gRPC / Kafka  
**Endpoint:** `RegisterSLA`

**Descrição:** Interface que registra SLAs aprovados no blockchain (Hyperledger Besu/GoQuorum) para auditoria imutável.

**Chamada gRPC:**
```protobuf
service BC_NSSMF {
  rpc RegisterSLA(SLARegistrationRequest) returns (SLARegistrationResponse);
}

message SLARegistrationRequest {
  string intent_id = 1;
  string nest_id = 2;
  string decision_id = 3;
  SLARequirements sla_requirements = 4;
  repeated Action actions = 5;
}
```

**Resposta:**
```json
{
  "transaction_hash": "0x1234...",
  "block_number": 12345,
  "contract_address": "0xabcd...",
  "status": "registered",
  "timestamp": "2025-01-27T10:00:15Z"
}
```

**Validação:**
- ✅ Transação blockchain confirmada
- ✅ Hash de transação retornado
- ✅ Endereço do contrato válido

---

### Interface I-06: Execução via SLA-Agent Layer

**Módulo:** Decision Engine → SLA-Agent Layer  
**Protocolo:** Kafka  
**Topic:** `trisla-i06-agent-events`

**Descrição:** Interface que transmite eventos e comandos do Decision Engine para os agentes SLA federados (RAN, Transport, Core).

**Mensagem Kafka:**
```json
{
  "event_id": "evt-urllc-001",
  "decision_id": "dec-urllc-001",
  "intent_id": "urllc-slice-001",
  "domain": "RAN",
  "event_type": "provision_slice",
  "action": {
    "type": "provision_slice",
    "config": {
      "cell_density": "high",
      "mimo_layers": 4,
      "bandwidth_mhz": 20
    }
  },
  "slo_monitoring": {
    "latency_ms": {
      "target": 5,
      "threshold": 6,
      "check_interval_seconds": 300
    }
  },
  "timestamp": "2025-01-27T10:00:20Z"
}
```

**Validação:**
- ✅ Domínio especificado (RAN/Transport/Core)
- ✅ Ação clara e executável
- ✅ SLOs de monitoramento definidos

---

### Interface I-07: Provisionamento NASP

**Módulo:** SLA-Agent Layer → NASP Adapter  
**Protocolo:** REST HTTP  
**Endpoint:** `POST /api/v1/provision`

**Descrição:** Interface final que executa ações reais nos controladores NASP (RAN, Transport, Core) através do NASP Adapter.

**Requisição HTTP:**
```json
{
  "event_id": "evt-urllc-001",
  "domain": "RAN",
  "action": {
    "type": "provision_slice",
    "slice_id": "slice-urllc-001",
    "config": {
      "cell_density": "high",
      "mimo_layers": 4,
      "bandwidth_mhz": 20
    }
  },
  "sla_requirements": {
    "latency_ms": 5,
    "throughput_mbps": 10,
    "reliability": 0.99999
  }
}
```

**Resposta:**
```json
{
  "provision_id": "prov-urllc-001",
  "status": "success",
  "slice_id": "slice-urllc-001",
  "endpoints": {
    "ran_controller": "http://ran-controller.nasp.svc.cluster.local:8080",
    "metrics": "http://ran-metrics.nasp.svc.cluster.local:9090"
  },
  "timestamp": "2025-01-27T10:00:25Z"
}
```

**Validação:**
- ✅ Slice provisionado com sucesso
- ✅ Endpoints retornados
- ✅ Status de provisionamento confirmado

---

### Fluxo Completo das Interfaces

**Sequência temporal:**
1. **I-01** (t=0s): Tenant envia intent → SEM-CSMF
2. **I-02** (t=1s): SEM-CSMF gera NEST → ML-NSMF (Kafka)
3. **I-03** (t=5s): ML-NSMF prediz viabilidade → Decision Engine (Kafka)
4. **I-04** (t=10s): Decision Engine decide → BC-NSSMF + SLA-Agent (Kafka)
5. **I-05** (t=15s): BC-NSSMF registra no blockchain (gRPC)
6. **I-06** (t=20s): SLA-Agent Layer recebe comando → NASP Adapter (Kafka)
7. **I-07** (t=25s): NASP Adapter provisiona slice no NASP (REST)

**Tempo total estimado:** ~25-30 segundos (end-to-end)

---

### Documentação de Interfaces

Para especificações técnicas completas, consulte:

- **Especificações de Interfaces**: [`docs/architecture/interfaces/`](docs/architecture/interfaces/)
- **Diagramas de Sequência**: Diagramas Draw.io em `docs/architecture/`

---

## 🐛 Troubleshooting Básico

Esta seção cobre problemas comuns durante o deploy e operação do TriSLA no NASP.

### Problemas de Deploy

#### 1. Pods em ImagePullBackOff

**Sintoma:**
```bash
kubectl get pods -n trisla
# NAME                    READY   STATUS             RESTARTS   AGE
# trisla-sem-csmf-xxx     0/1     ImagePullBackOff   0          5m
```

**Causa:** Secret GHCR não configurado ou token inválido.

**Solução:**
```bash
# 1. Verificar secret
kubectl get secret ghcr-secret -n trisla

# 2. Criar/atualizar secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_PAT> \
  --namespace=trisla

# 3. Verificar imagens no values-nasp.yaml
grep -A 2 "image:" helm/trisla/values-nasp.yaml

# 4. Reiniciar pods
kubectl delete pods -n trisla -l app.kubernetes.io/name=trisla
```

---

#### 2. Pods em CrashLoopBackOff

**Sintoma:**
```bash
kubectl get pods -n trisla
# NAME                    READY   STATUS             RESTARTS   AGE
# trisla-sem-csmf-xxx     0/1     CrashLoopBackOff   5          10m
```

**Causa:** Erro na aplicação, variáveis de ambiente incorretas, ou dependências não disponíveis.

**Solução:**
```bash
# 1. Ver logs do pod
kubectl logs -n trisla <pod-name> --previous

# 2. Ver eventos do pod
kubectl describe pod -n trisla <pod-name>

# 3. Verificar variáveis de ambiente
kubectl exec -n trisla <pod-name> -- env | grep -E "KAFKA|DATABASE|NASP"

# 4. Verificar dependências (Kafka, PostgreSQL, etc.)
kubectl get pods -n <kafka-namespace>
kubectl get pods -n <postgres-namespace>
```

---

#### 3. Helm Chart Validation Failed

**Sintoma:**
```bash
helm lint ./helm/trisla
# ERROR: values file does not exist
```

**Causa:** Arquivo `values-nasp.yaml` não encontrado ou com sintaxe inválida.

**Solução:**
```bash
# 1. Verificar se arquivo existe
ls -la helm/trisla/values-nasp.yaml

# 2. Validar sintaxe YAML
yamllint helm/trisla/values-nasp.yaml

# 3. Validar template Helm
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug
```

---

### Problemas de Conectividade

#### 4. Kafka Topics Não Criados

**Sintoma:**
```bash
kubectl logs -n trisla <sem-csmf-pod> | grep -i kafka
# ERROR: Topic 'I-02-intent-to-ml' does not exist
```

**Causa:** Kafka não configurado ou tópicos não criados automaticamente.

**Solução:**
```bash
# 1. Verificar Kafka
kubectl get pods -n <kafka-namespace> | grep kafka

# 2. Criar tópicos manualmente
kubectl exec -n <kafka-namespace> <kafka-pod> -- \
  kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --topic I-02-intent-to-ml \
    --partitions 3 \
    --replication-factor 1

# 3. Verificar tópicos criados
kubectl exec -n <kafka-namespace> <kafka-pod> -- \
  kafka-topics --list --bootstrap-server localhost:9092
```

---

#### 5. Conectividade com NASP Falhando

**Sintoma:**
```bash
kubectl logs -n trisla <nasp-adapter-pod> | grep -i error
# ERROR: Connection refused to http://ran-controller.nasp.svc.cluster.local:8080
```

**Causa:** Endpoints NASP incorretos ou serviços não disponíveis.

**Solução:**
```bash
# 1. Verificar endpoints no values-nasp.yaml
grep -A 5 "naspEndpoints:" helm/trisla/values-nasp.yaml

# 2. Testar conectividade
kubectl run -it --rm test-pod --image=curlimages/curl --restart=Never -- \
  curl -v http://ran-controller.nasp.svc.cluster.local:8080/health

# 3. Descobrir endpoints corretos
./scripts/discover-nasp-endpoints.sh

# 4. Atualizar values-nasp.yaml com endpoints corretos
vim helm/trisla/values-nasp.yaml
```

---

### Problemas de Performance

#### 6. Alta Latência nas Interfaces

**Sintoma:** Interfaces I-01 a I-07 demoram mais de 30 segundos.

**Causa:** Recursos insuficientes ou gargalos de rede.

**Solução:**
```bash
# 1. Verificar recursos dos pods
kubectl top pods -n trisla

# 2. Verificar recursos do cluster
kubectl top nodes

# 3. Ajustar recursos no values-nasp.yaml
vim helm/trisla/values-nasp.yaml
# Aumentar CPU/memory limits

# 4. Aplicar mudanças
helm upgrade trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml
```

---

### Problemas de Observabilidade

#### 7. Métricas Não Aparecem no Prometheus

**Sintoma:** Grafana não mostra métricas do TriSLA.

**Causa:** ServiceMonitor não configurado ou Prometheus não scraping.

**Solução:**
```bash
# 1. Verificar ServiceMonitor
kubectl get servicemonitor -n trisla

# 2. Verificar targets no Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Acessar http://localhost:9090/targets

# 3. Verificar métricas expostas
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080
curl http://localhost:8080/metrics
```

---

### Comandos Úteis de Diagnóstico

```bash
# Ver todos os recursos do TriSLA
kubectl get all -n trisla

# Ver eventos recentes
kubectl get events -n trisla --sort-by='.lastTimestamp'

# Ver logs de todos os pods
kubectl logs -n trisla -l app.kubernetes.io/part-of=trisla --tail=100

# Verificar health checks
for pod in $(kubectl get pods -n trisla -o name); do
  echo "=== $pod ==="
  kubectl exec -n trisla $pod -- curl -s http://localhost:8080/health || echo "Health check failed"
done

# Verificar conectividade Kafka
kubectl exec -n <kafka-ns> <kafka-pod> -- \
  kafka-broker-api-versions --bootstrap-server localhost:9092

# Verificar blockchain
kubectl logs -n trisla <bc-nssmf-pod> | grep -i "blockchain\|besu\|transaction"
```

---

### Documentação de Troubleshooting

Para troubleshooting avançado, consulte:

- **Guia Completo**: [`docs/reports/TROUBLESHOOTING_TRISLA.md`](docs/reports/TROUBLESHOOTING_TRISLA.md)
- **Relatórios Técnicos**: [`docs/reports/`](docs/reports/)

---

## 📄 Arquivo Canônico values-nasp.yaml

- **README Ansible**: [`ansible/README.md`](ansible/README.md)

---

## ⚙️ Arquivo Canônico values-nasp.yaml

O arquivo **`helm/trisla/values-nasp.yaml`** é o arquivo de configuração **canônico e padrão** para deploy no ambiente NASP. Este arquivo contém todas as configurações necessárias para o TriSLA operar no ambiente NASP.

### Localização

```
helm/trisla/values-nasp.yaml
```

### Estrutura do Arquivo

O arquivo `values-nasp.yaml` está organizado nas seguintes seções:

#### 1. Network Configuration

```yaml
network:
  interface: "my5g"              # Interface principal do NASP
  nodeIP: "192.168.10.16"       # IP do node1
  gateway: "192.168.10.1"        # Gateway padrão
```

#### 2. Production Settings

```yaml
production:
  enabled: true
  simulationMode: false          # ⚠️ NÃO usar simulação
  useRealServices: true         # ⚠️ Usar serviços REAIS
  executeRealActions: true      # ⚠️ Executar ações REAIS
```

#### 3. NASP Endpoints (⚠️ EDITAR)

```yaml
naspAdapter:
  naspEndpoints:
    ran: "http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_PORT>"
    core_upf: "http://<UPF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<UPF_PORT>"
    transport: "http://<TRANSPORT_SERVICE>.<TRANSPORT_NAMESPACE>.svc.cluster.local:<TRANSPORT_PORT>"
```

**Como descobrir endpoints:**
```bash
./scripts/discover-nasp-endpoints.sh
```

#### 4. Recursos por Módulo

```yaml
semCsmf:
  replicas: 3
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi
```

### O que Deve Ser Editado

**Antes do primeiro deploy, edite:**

1. **Endpoints NASP** (seção `naspAdapter.naspEndpoints`):
   - Substitua `<RAN_SERVICE>`, `<RAN_NAMESPACE>`, `<RAN_PORT>` pelos valores reais
   - Substitua `<UPF_SERVICE>`, `<CORE_NAMESPACE>`, `<UPF_PORT>` pelos valores reais
   - Substitua `<TRANSPORT_SERVICE>`, `<TRANSPORT_NAMESPACE>`, `<TRANSPORT_PORT>` pelos valores reais

2. **Network Configuration** (se necessário):
   - Ajuste `interface`, `nodeIP` e `gateway` se diferentes do padrão

3. **Recursos** (opcional):
   - Ajuste `replicas` e `resources` conforme capacidade do cluster

### Exemplo de Edição

```yaml
# Antes (placeholder)
ran: "http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_PORT>"

# Depois (valor real)
ran: "http://ran-controller.nasp-ran.svc.cluster.local:8080"
```

### Validação do Arquivo

```bash
# Validar sintaxe YAML
yamllint helm/trisla/values-nasp.yaml

# Validar com Helm
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml

# Template dry-run
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml
```

### Documentação Completa

Para guia detalhado sobre valores de produção, consulte:

- **Guia de Valores**: [`docs/deployment/VALUES_PRODUCTION_GUIDE.md`](docs/deployment/VALUES_PRODUCTION_GUIDE.md)

---

## 🧪 Testes E2E

O TriSLA inclui uma suíte completa de testes end-to-end (E2E) que valida todo o fluxo desde a recepção de intenções até a execução de ações nos controladores NASP.

### Executar Testes E2E

```bash
./scripts/complete-e2e-test.sh
```

### O que os Testes Validam

Os testes E2E verificam:

1. **Interface I-01**: Recepção de intenções via SEM-CSMF
2. **Interface I-02**: Processamento semântico e geração de NEST
3. **Interface I-03**: Predição de viabilidade via ML-NSMF
4. **Interface I-04**: Decisão automatizada via Decision Engine
5. **Interface I-05**: Registro em blockchain via BC-NSSMF
6. **Interface I-06/I-07**: Execução via SLA-Agent Layer e NASP Adapter

### Testes Individuais

```bash
# Teste de integração I-02
./scripts/test_i02_integration.sh

# Teste de fluxo E2E
./scripts/test-e2e-flow.sh

# Validação de pipeline E2E
./scripts/validate-e2e-pipeline.sh
```

### Estrutura de Testes

```
tests/
├── unit/              # Testes unitários por módulo
├── integration/       # Testes de integração entre módulos
└── e2e/              # Testes end-to-end completos
```

### Documentação de Testes

Para mais informações sobre testes, consulte:

- **README de Testes**: [`tests/README.md`](tests/README.md)

---

## 🤝 Como Contribuir

O TriSLA é um projeto acadêmico desenvolvido como parte de uma dissertação de mestrado. Contribuições são bem-vindas e apreciadas.

### Processo de Contribuição

1. **Fork o repositório**
2. **Crie uma branch para sua feature**:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
3. **Faça suas alterações** seguindo os padrões do projeto
4. **Execute testes**:
   ```bash
   ./scripts/run-local-tests.sh
   ```
5. **Valide código**:
   ```bash
   ./scripts/validate-code.sh
   ```
6. **Commit suas alterações**:
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   ```
7. **Push para sua branch**:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
8. **Abra um Pull Request**

### Padrões de Código

- **Python**: Seguir PEP 8
- **YAML**: Usar espaços (não tabs), indentação de 2 espaços
- **Markdown**: Seguir convenções do projeto
- **Commits**: Usar Conventional Commits (feat:, fix:, docs:, etc.)

### Documentação para Desenvolvedores

Consulte a documentação completa para desenvolvedores:

- **Guia do Desenvolvedor**: [`docs/deployment/DEVELOPER_GUIDE.md`](docs/deployment/DEVELOPER_GUIDE.md)
- **Guia de Contribuição**: [`docs/deployment/CONTRIBUTING.md`](docs/deployment/CONTRIBUTING.md)

### Contato

Para questões, sugestões ou colaborações, entre em contato através do repositório GitHub.


## 📄 Licença

Este projeto está licenciado sob a **MIT License**.

```
MIT License

Copyright (c) 2025 Abel Lisboa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Veja o arquivo completo: [`LICENSE`](LICENSE)

---

## 🔗 Links Úteis

### Documentação por Categoria

#### 📘 Documentação NASP

- **Guia de Deploy NASP**: [`docs/nasp/NASP_DEPLOY_GUIDE.md`](docs/nasp/NASP_DEPLOY_GUIDE.md)
- **Runbook Operacional**: [`docs/nasp/NASP_DEPLOY_RUNBOOK.md`](docs/nasp/NASP_DEPLOY_RUNBOOK.md)
- **Checklist Pré-Deploy**: [`docs/nasp/NASP_PREDEPLOY_CHECKLIST_v2.md`](docs/nasp/NASP_PREDEPLOY_CHECKLIST_v2.md)
- **Relatório de Contexto NASP**: [`docs/nasp/NASP_CONTEXT_REPORT.md`](docs/nasp/NASP_CONTEXT_REPORT.md)

#### 🚀 Documentação de Deploy

- **Guia de Valores de Produção**: [`docs/deployment/VALUES_PRODUCTION_GUIDE.md`](docs/deployment/VALUES_PRODUCTION_GUIDE.md)
- **Guia do Desenvolvedor**: [`docs/deployment/DEVELOPER_GUIDE.md`](docs/deployment/DEVELOPER_GUIDE.md)
- **Instalação Completa**: [`docs/deployment/INSTALL_FULL_PROD.md`](docs/deployment/INSTALL_FULL_PROD.md)
- **Operações em Produção**: [`docs/deployment/README_OPERATIONS_PROD.md`](docs/deployment/README_OPERATIONS_PROD.md)
- **Guia de Contribuição**: [`docs/deployment/CONTRIBUTING.md`](docs/deployment/CONTRIBUTING.md)

#### 📊 Relatórios Técnicos

- **Relatório de Migração Local**: [`docs/REPORT_MIGRATION_LOCAL_MODE.md`](docs/REPORT_MIGRATION_LOCAL_MODE.md)
- **Auditoria Técnica**: [`docs/reports/AUDIT_REPORT_TECHNICAL_v2.md`](docs/reports/AUDIT_REPORT_TECHNICAL_v2.md)
- **Relatórios por Fase**: [`docs/reports/`](docs/reports/)
  - Fase 1: SEM-CSMF
  - Fase 2: ML-NSMF
  - Fase 3: Decision Engine
  - Fase 4: BC-NSSMF
  - Fase 5: SLA-Agent Layer
  - Fase 6: Validação E2E
  - Fase 7: Preparação Deploy NASP

#### 🏗️ Arquitetura

- **Documentação de Arquitetura**: [`docs/architecture/`](docs/architecture/)
- **Diagramas e Figuras**: Diagramas Draw.io e ilustrações técnicas

#### 🔒 Segurança

- **Hardening de Segurança**: [`docs/security/SECURITY_HARDENING.md`](docs/security/SECURITY_HARDENING.md)

#### 🐛 Troubleshooting

- **Guia de Troubleshooting**: [`docs/reports/TROUBLESHOOTING_TRISLA.md`](docs/reports/TROUBLESHOOTING_TRISLA.md)

### Recursos Adicionais

- **Helm Chart README**: [`helm/trisla/README.md`](helm/trisla/README.md)
- **Ansible README**: [`ansible/README.md`](ansible/README.md)
- **Monitoring README**: [`monitoring/README.md`](monitoring/README.md)
- **Tests README**: [`tests/README.md`](tests/README.md)

---

## 🏷️ TriSLA v3.5.0 — Release Estável NASP Local

### Release v3.5.0

A **TriSLA v3.5.0** representa uma consolidação completa do repositório para operação em produção no ambiente NASP, com deploy totalmente automatizado e local.

**Principais características:**
- ✅ Deploy 100% local no NASP (127.0.0.1)
- ✅ `values-nasp.yaml` como arquivo canônico
- ✅ Release name padronizado: `trisla`
- ✅ Proteções GitHub implementadas
- ✅ Documentação completa e sincronizada
- ✅ Auditoria DevOps completa

**Para mais informações:**
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Relatório de Alinhamento**: [docs/reports/FINAL_ALIGNMENT_REPORT_v3.5.0.md](docs/reports/FINAL_ALIGNMENT_REPORT_v3.5.0.md)

---

## 🏷️ TriSLA v1.0.0 — Release Inicial

Esta é a primeira versão pública e consolidada do TriSLA, alinhada à dissertação de mestrado e ao ambiente operacional NASP.

### Principais Características

- ✅ **Arquitetura modular e extensível**: Componentes independentes e reutilizáveis
- ✅ **Integração completa com NASP**: Adaptador nativo para ambientes 5G/O-RAN
- ✅ **Observabilidade end-to-end**: OpenTelemetry, Prometheus e Grafana
- ✅ **Smart Contracts**: Registro imutável de SLAs em blockchain
- ✅ **Closed-loop assurance**: Automação completa de monitoramento e correção
- ✅ **Pipeline DevOps completo**: Build, test e deploy automatizados
- ✅ **Deploy local simplificado**: Operação direta no node1 do NASP

### Tecnologias Utilizadas

- **Backend**: Python 3.10+, FastAPI, gRPC
- **ML/AI**: TensorFlow/Keras, LSTM, XAI
- **Blockchain**: Solidity, Besu/GoQuorum
- **Frontend**: TypeScript, React, Vite
- **Infraestrutura**: Kubernetes, Helm, Ansible
- **Observabilidade**: OpenTelemetry, Prometheus, Grafana
- **Message Bus**: Apache Kafka

---

**TriSLA v1.0.0** — Desenvolvido como parte da dissertação de mestrado em Engenharia de Sistemas e Computação.

**Autor**: Abel José Rodrigues Lisboa  
**Licença**: MIT  
**Repositório**: [GitHub](https://github.com/abelisboa/TriSLA)

---

*Para mais informações, consulte a [documentação completa](docs/) ou entre em contato através do repositório GitHub.*
