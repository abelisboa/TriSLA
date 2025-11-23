# 🛰️ TriSLA — Trustworthy, Reasoned & Intelligent SLA-Aware Architecture

### SLA-Aware Network Slicing for 5G/O-RAN — Semantic, AI-Driven & Smart-Contract-Enforced

TriSLA é uma arquitetura completa, modular e inteligente para validação, decisão e execução automatizada de SLAs em redes 5G/O-RAN.  

A proposta integra três pilares avançados:

- **SEM-CSMF** — Interpretação semântica e mapeamento GST→NEST  
- **ML-NSMF** — Tomada de decisão baseada em IA e previsão de recursos  
- **BC-NSSMF** — Execução contratual automática com Smart Contracts  

Além disso, possui uma **camada unificadora de agentes de SLA**, observabilidade OTLP e integração nativa com plataformas NASP/NWDAF.

---

# 📌 Sumário

1. [Visão Geral](#visão-geral)  
2. [Arquitetura TriSLA](#arquitetura-trisla)  
3. [Módulos da Arquitetura](#módulos-da-arquitetura)  
4. [Dependências e Requisitos](#dependências-e-requisitos)  
5. [Guia Rápido (Local)](#guia-rápido-local)  
6. [Deploy via Helm](#deploy-via-helm)  
7. [🚀 Deploy no NASP](#🚀-deploy-no-nasp)  
8. [Estrutura do Repositório](#estrutura-do-repositório)  
9. [Documentação Completa](#documentação-completa)  
10. [Licença](#licença)

---

# Visão Geral

O TriSLA implementa um pipeline completo de *intent → SLA-aware model → decisão → execução → monitoramento*, conforme exigido por redes 5G/O-RAN modernas, oferecendo:

- Interpretação semântica de intenções em linguagem natural  
- Tradução automatizada de GST→NEST conforme GSMA/3GPP  
- Avaliação de recursos multi-domínio (RAN–TN–Core)  
- Execução contratual com Blockchain  
- Observabilidade automática com métricas, logs e traces  
- Agentes distribuídos de SLA

---

# Arquitetura TriSLA

A arquitetura é estruturada em três módulos principais:

## 1. SEM-CSMF (Semantic Communication Service Management Function)

**Responsabilidade:** Interpretação semântica de intenções de tenant e geração de NEST (Network Slice Template).

- Processamento de linguagem natural (NLP)
- Mapeamento GST (Generic Slice Template) → NEST
- Validação semântica via ontologia OWL
- Interface REST (I-02)

## 2. ML-NSMF (Machine Learning Network Slice Management Function)

**Responsabilidade:** Predição de violações de SLA usando modelos LSTM com explicação (XAI).

- Modelos de ML treinados para predição de recursos
- Explicabilidade (XAI) para transparência
- Interface REST (I-03)
- Integração com Kafka para eventos

## 3. BC-NSSMF (Blockchain Network Slice Subnet Management Function)

**Responsabilidade:** Execução de smart contracts em blockchain para registro imutável de SLAs.

- Smart contracts Solidity
- Integração com GoQuorum/Besu (Ethereum permissionado)
- Registro imutável de SLAs e violações
- Interface REST (I-04)

## 4. Decision Engine

**Responsabilidade:** Motor de decisão automatizado baseado em regras e ML.

- Processamento de regras YAML
- Integração com SEM-CSMF, ML-NSMF e BC-NSSMF
- Interface gRPC (I-01) e REST (I-05)
- Publicação de eventos via Kafka

## 5. SLA-Agent Layer

**Responsabilidade:** Agentes federados para coleta de métricas em RAN, Transport e Core.

- Agentes autônomos por domínio
- Coleta de métricas em tempo real
- Integração com NASP Adapter
- Interface REST (I-06)

## 6. NASP Adapter

**Responsabilidade:** Integração com a plataforma NASP para execução de ações reais.

- Interface unificada com NASP
- Execução de ações em RAN/Core/Transport
- Interface REST (I-07)

## 7. UI Dashboard

**Responsabilidade:** Interface visual para monitoramento e administração.

- Dashboard web para visualização de SLAs
- Métricas e gráficos em tempo real
- Integração com Prometheus/Grafana

---

# Módulos da Arquitetura

```
apps/
├── sem-csmf/         # SEM-CSMF: Interpretação Semântica + Ontologia
├── ml-nsmf/          # ML-NSMF: Predição LSTM + XAI
├── decision-engine/  # Decision Engine: Motor de decisão SLA-aware
├── bc-nssmf/         # BC-NSSMF: Smart Contracts (GoQuorum/Besu)
├── sla-agent-layer/  # SLA-Agent Layer: Agentes federados RAN/Core/Transport
├── nasp-adapter/     # NASP Adapter: Integração com NASP
└── ui-dashboard/     # UI Dashboard: Interface visual
```

---

# Dependências e Requisitos

## Requisitos de Sistema

- **Python:** ≥ 3.10
- **Docker:** ≥ 20.10
- **Kubernetes:** ≥ 1.26
- **Helm:** ≥ 3.12
- **kubectl:** ≥ 1.26

## Dependências Externas

- **Kafka:** Para comunicação assíncrona entre módulos
- **PostgreSQL:** Para persistência de dados
- **GoQuorum/Besu:** Para blockchain permissionado
- **Prometheus/Grafana:** Para observabilidade
- **OTLP Collector:** Para traces e métricas

---

# Guia Rápido (Local)

## Execução Local com Docker Compose

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Visualizar logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## Execução Local (Sandbox)

```bash
# Pipeline completo v8.0
./scripts/TRISLA_AUTO_RUN.sh
```

**Pipeline inclui:**
- ✅ SEM-CSMF
- ✅ ML-NSMF
- ✅ Decision Engine
- ✅ Smart Contracts
- ✅ BC-NSSMF
- ✅ OTLP Collector
- ✅ HEARTBEAT
- ✅ READY REPORT
- ✅ E2E Validator

---

# Deploy via Helm

## Preparação

```bash
# Validar Helm chart
helm lint ./helm/trisla

# Dry-run
helm template trisla-portal ./helm/trisla \
  -f ./helm/trisla/values.yaml \
  --debug
```

## Deploy em Produção Genérica

```bash
# 1. Preencher values-production.yaml
./scripts/fill_values_production.sh

# 2. Deploy
helm upgrade --install trisla-portal ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-production.yaml \
  --create-namespace \
  --wait \
  --timeout 15m
```

## Verificação

```bash
# Status dos pods
kubectl get pods -n trisla

# Status dos serviços
kubectl get svc -n trisla

# Logs
kubectl logs -n trisla -l app=sem-csmf --tail=50
```

---

# 🚀 Deploy no NASP

## Fluxo Oficial para NASP

### 1. Preparar valores NASP

```bash
# Opção 1: Script guiado
export TRISLA_ENV=nasp
./scripts/fill_values_production.sh

# Opção 2: Copiar template e editar
cp docs/nasp/values-nasp.yaml helm/trisla/values-nasp.yaml
vim helm/trisla/values-nasp.yaml
```

**⚠️ IMPORTANTE:** O arquivo canônico para deploy NASP é `helm/trisla/values-nasp.yaml`.  
O arquivo `docs/nasp/values-nasp.yaml` é apenas um template/exemplo.

### 2. Validar configuração

```bash
# Validar Helm chart
helm lint ./helm/trisla

# Dry-run
helm template trisla-portal ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

### 3. Deploy automatizado (Recomendado)

```bash
# No node1 do NASP
./scripts/deploy-trisla-nasp-auto.sh
```

Este script:
- ✅ Valida todos os pré-requisitos
- ✅ Corrige erros automaticamente (namespace, secrets, storage, etc.)
- ✅ Monitora pods em tempo real
- ✅ Valida logs de cada módulo
- ✅ Gera relatório completo em Markdown

**Log completo:** `/tmp/trisla-deploy.log`  
**Relatório:** `/tmp/trisla-deploy-report-*.md`

### 4. Deploy manual (Alternativa)

```bash
# Pré-check do cluster
./scripts/pre-check-nasp.sh

# Deploy com Helm
helm upgrade --install trisla-portal ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --create-namespace \
  --wait \
  --timeout 15m \
  --debug
```

### 5. Deploy com Ansible (Opcional)

```bash
ansible-playbook -i ansible/inventory.yaml \
  ansible/playbooks/deploy-trisla-nasp.yml
```

## Documentação NASP

Consulte a documentação completa em:
- **`docs/nasp/NASP_DEPLOY_RUNBOOK.md`** — Guia operacional completo
- **`docs/nasp/NASP_PREDEPLOY_CHECKLIST_v3.4.md`** — Checklist de pré-deploy
- **`docs/nasp/NASP_DEPLOY_GUIDE.md`** — Guia detalhado de deploy
- **`docs/CONSOLIDATION_SUMMARY.md`** — Resumo da consolidação do fluxo NASP

---

# Estrutura do Repositório

```
TriSLA/
├── apps/                    # Módulos da aplicação
│   ├── sem-csmf/
│   ├── ml-nsmf/
│   ├── decision-engine/
│   ├── bc-nssmf/
│   ├── sla-agent-layer/
│   ├── nasp-adapter/
│   └── ui-dashboard/
├── helm/                    # Helm charts
│   └── trisla/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-production.yaml
│       └── values-nasp.yaml      # ⭐ Arquivo canônico para NASP
├── ansible/                 # Playbooks Ansible
│   ├── inventory.yaml
│   └── playbooks/
│       └── deploy-trisla-nasp.yml
├── scripts/                 # Scripts de automação
│   ├── deploy-trisla-nasp-auto.sh
│   ├── deploy-trisla-nasp.sh
│   ├── pre-check-nasp.sh
│   └── ...
├── monitoring/              # Configurações de observabilidade
│   └── otel-collector/
├── docs/                    # Documentação
│   ├── nasp/                # Documentação específica NASP
│   ├── deployment/          # Guias de deploy
│   ├── architecture/        # Arquitetura do sistema
│   └── api/                 # Documentação de APIs
├── tests/                   # Testes
│   ├── unit/
│   ├── integration/
│   └── load/
├── docker-compose.yml       # Compose para desenvolvimento local
└── README.md               # Este arquivo
```

---

# Documentação Completa

## Documentação Técnica

- **`docs/architecture/`** — Arquitetura do sistema
- **`docs/api/`** — Documentação de APIs (REST, gRPC)
- **`docs/deployment/`** — Guias de deploy e operação

## Documentação NASP

- **`docs/nasp/NASP_DEPLOY_RUNBOOK.md`** — Runbook operacional
- **`docs/nasp/NASP_PREDEPLOY_CHECKLIST_v3.4.md`** — Checklist pré-deploy
- **`docs/nasp/NASP_DEPLOY_GUIDE.md`** — Guia detalhado
- **`docs/nasp/values-nasp.yaml`** — Template de valores (exemplo)

## Guias de Operação

- **`docs/deployment/README_OPERATIONS_PROD.md`** — Operações em produção
- **`docs/deployment/VALUES_PRODUCTION_GUIDE.md`** — Guia de valores
- **`docs/deployment/DEVELOPER_GUIDE.md`** — Guia para desenvolvedores

## Consolidação

- **`docs/CONSOLIDATION_SUMMARY.md`** — Resumo da consolidação do fluxo NASP

---

# Build & Publicação GHCR

## Build de Imagens Docker

```bash
# SEM-CSMF
docker build -t ghcr.io/abelisboa/trisla-sem-csmf:latest apps/sem-csmf/
docker push ghcr.io/abelisboa/trisla-sem-csmf:latest

# ML-NSMF
docker build -t ghcr.io/abelisboa/trisla-ml-nsmf:latest apps/ml-nsmf/
docker push ghcr.io/abelisboa/trisla-ml-nsmf:latest

# Decision Engine
docker build -t ghcr.io/abelisboa/trisla-decision-engine:latest apps/decision-engine/
docker push ghcr.io/abelisboa/trisla-decision-engine:latest

# BC-NSSMF
docker build -t ghcr.io/abelisboa/trisla-bc-nssmf:latest apps/bc-nssmf/
docker push ghcr.io/abelisboa/trisla-bc-nssmf:latest

# SLA-Agent Layer
docker build -t ghcr.io/abelisboa/trisla-sla-agent-layer:latest apps/sla-agent-layer/
docker push ghcr.io/abelisboa/trisla-sla-agent-layer:latest

# NASP Adapter
docker build -t ghcr.io/abelisboa/trisla-nasp-adapter:latest apps/nasp-adapter/
docker push ghcr.io/abelisboa/trisla-nasp-adapter:latest

# UI Dashboard
docker build -t ghcr.io/abelisboa/trisla-ui-dashboard:latest apps/ui-dashboard/
docker push ghcr.io/abelisboa/trisla-ui-dashboard:latest
```

## Script Automatizado

```bash
# Publicar todas as imagens
./scripts/publish_all_images_ghcr.sh
```

## Helm Chart

```bash
# Empacotar
helm package helm/trisla/

# Publicar
helm push trisla-*.tgz oci://ghcr.io/abelisboa/helm-charts
```

---

# Licença

**MIT License**

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

---

# 🏷️ TriSLA v3.4.0 — Release Oficial

Esta é a versão consolidada do TriSLA, alinhada à dissertação de mestrado e ao ambiente operacional NASP.

**Principais características:**
- ✅ Arquitetura modular e extensível
- ✅ Integração completa com NASP
- ✅ Observabilidade end-to-end (OTLP)
- ✅ Smart Contracts para registro imutável de SLAs
- ✅ Closed-loop assurance automatizado
- ✅ Pipeline DevOps completo
- ✅ Deploy automatizado com autocorreção

---

# 🤝 Contribuindo

Este é um projeto acadêmico. Para contribuições, por favor entre em contato através do repositório GitHub.

---

**TriSLA v3.4.0** — Desenvolvido como parte da dissertação de mestrado em Engenharia de Sistemas e Computação.
