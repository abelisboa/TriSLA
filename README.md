# TriSLA — Trustworthy, Reasoned and Intelligent SLA Architecture

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/abelisboa/TriSLA)
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
│       ├── values-nasp.yaml      # ⭐ Valores para NASP (canônico)
│       ├── values-production.yaml # Valores de produção
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
│   ├── fill_values_production.sh     # ⭐ Preencher values
│   ├── discover-nasp-endpoints.sh    # Descobrir endpoints NASP
│   ├── prepare-nasp-deploy.sh        # Preparar ambiente
│   ├── pre-check-nasp.sh             # Pré-verificações
│   ├── complete-e2e-test.sh          # Testes E2E
│   └── ...                         # Outros scripts utilitários
│
├── docs/                          # Documentação completa
│   ├── nasp/                     # Documentação NASP
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

O deploy do TriSLA no ambiente NASP é realizado **localmente no node1**, sem necessidade de SSH ou acesso remoto. Todas as operações são executadas diretamente no node onde o cluster Kubernetes está rodando.

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

```bash
./scripts/fill_values_production.sh
```

**O que este script faz:**
- Copia `helm/trisla/values-nasp.yaml` para `helm/trisla/values-production.yaml`
- Prepara o arquivo com valores padrão do ambiente NASP
- Mantém placeholders para endpoints que devem ser descobertos

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
helm status trisla-portal -n trisla
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
helm upgrade --install trisla-portal ./helm/trisla \
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
helm template trisla-portal ./helm/trisla -f ./helm/trisla/values-nasp.yaml
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

---

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

## 🏷️ TriSLA v1.0.0 — Release Oficial

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

**Autor**: Abel Lisboa  
**Licença**: MIT  
**Repositório**: [GitHub](https://github.com/abelisboa/TriSLA)

---

*Para mais informações, consulte a [documentação completa](docs/) ou entre em contato através do repositório GitHub.*
