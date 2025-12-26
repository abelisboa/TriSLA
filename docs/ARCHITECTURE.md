# TriSLA — Visão Geral da Arquitetura

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `docs/architecture` (consolidado)

---

## 📋 Sumário

1. [Introdução](#1-introdução)
2. [Visão de Alto Nível](#2-visão-de-alto-nível-da-arquitetura)
3. [Descrição Detalhada dos Módulos](#3-descrição-detalhada-dos-módulos)
4. [Fluxo Operacional Completo](#4-fluxo-operacional-completo-intent--sla--slice)
5. [Interação entre Domínios](#5-interação-entre-domínios)
6. [Interfaces Internas (I-01 a I-07)](#6-visão-das-interfaces-internas-i-01-a-i-07)
7. [Observabilidade](#7-observabilidade)
8. [Blockchain](#8-blockchain)
9. [Escalabilidade e Resiliência](#10-considerações-sobre-escalabilidade-e-resiliência)

---

## 1. Introdução

### 1.1 O que é a Arquitetura TriSLA

**TriSLA** (Triple-SLA) é uma arquitetura distribuída e inteligente para gerenciamento automatizado de Service Level Agreements (SLAs) em redes 5G/O-RAN. A arquitetura integra interpretação semântica, machine learning explicável, decisão automatizada, blockchain e agentes federados para fornecer garantia de SLA de forma auditável e em laço fechado (closed-loop assurance).

A arquitetura é baseada em microserviços, utilizando comunicação síncrona (gRPC) e assíncrona (Kafka), com observabilidade completa via OpenTelemetry e integração nativa com plataformas NASP (Network Automation & Slicing Platform).

### 1.2 Motivação e Contexto 5G/O-RAN

**Desafios em redes 5G/O-RAN:**
- **Complexidade de gerenciamento**: Redes 5G introduzem network slicing, múltiplos domínios (RAN, Transport, Core) e requisitos de SLA rigorosos
- **Heterogeneidade**: Integração de múltiplos fornecedores e tecnologias (O-RAN, 5G Core, Transport SDN)
- **Dinamicidade**: Requisitos de SLA variam por aplicação (eMBB, URLLC, mMTC) e contexto temporal
- **Auditabilidade**: Necessidade de rastreabilidade e compliance regulatório
- **Automação**: Requisito de resposta rápida a violações e otimização contínua

**Solução TriSLA:**

A arquitetura TriSLA aborda esses desafios através de:

1. **Interpretação Semântica**: Uso de ontologias OWL para interpretação precisa de intents de tenants
2. **Predição Inteligente**: Machine Learning (Random Forest) com Explainable AI (XAI) para prever violações
3. **Decisão Automatizada**: Motor de decisão baseado em regras e ML para aceitar/rejeitar/negociar SLAs
4. **Blockchain**: Registro imutável de SLAs e decisões para auditoria e compliance
5. **Agentes Federados**: Coleta e execução distribuída nos domínios RAN, Transport e Core
6. **Integração NASP**: Conectividade direta com plataformas de automação de rede reais

### 1.3 Princípios Arquiteturais

**Desacoplamento:**
- Módulos independentes com interfaces bem definidas
- Comunicação via APIs padronizadas (gRPC, REST, Kafka)

**Observabilidade:**
- Instrumentação completa com OpenTelemetry
- Métricas, traces e logs centralizados

**Resiliência:**
- Tolerância a falhas em componentes individuais
- Retry automático e circuit breakers

**Escalabilidade:**
- Arquitetura stateless quando possível
- Suporte a múltiplas réplicas

**Segurança:**
- Autenticação e autorização em todas as interfaces
- Criptografia em trânsito (TLS/mTLS)
- Zero Trust principles

---

## 2. Visão de Alto Nível da Arquitetura

### 2.1 Diagrama Arquitetural

```
┌─────────────────────────────────────────────────────────────────┐
│                    TriSLA Architecture                          │
│              (Trustworthy, Reasoned, Intelligent SLA)           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Tenant     │  ──I-01──>  ┌──────────────┐
│   Portal     │             │  SEM-NSMF    │  (Semantic Interpretation)
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
│  OpenTelemetry Collector → Prometheus, Jaeger, Loki          │
│  → Grafana (Dashboards + SLO Reports)                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Message Bus (Kafka)                         │
│  Topics: I-02, I-03, I-04, I-05, I-06, I-07                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Camadas da Arquitetura

**Camada de Aplicação:**
- Interface de usuário para visualização e administração
- Dashboard para monitoramento de SLAs e métricas

**Camada de Orquestração:**
- Módulos principais do TriSLA
- Lógica de negócio e processamento

**Camada de Infraestrutura:**
- Domínios de rede (RAN, Transport, Core)
- Integração com NASP

**Camada de Mensageria:**
- Comunicação assíncrona entre módulos
- Event-driven architecture

**Camada de Observabilidade:**
- Coleta e visualização de métricas, traces e logs
- Alertas e dashboards

**Camada de Persistência:**
- Armazenamento de dados estruturados (PostgreSQL)
- Ledger imutável (Blockchain)

---

## 3. Descrição Detalhada dos Módulos

### 3.1 SEM-NSMF (Semantic-enhanced Network Slice Management Function)

**Propósito:**
O SEM-NSMF é responsável por receber intents de tenants, interpretá-los semanticamente usando ontologias OWL, e gerar Network Slice Templates (NEST) que descrevem os requisitos de rede de forma estruturada.

**Funcionalidades principais:**
1. **Recepção de Intents**: API REST para receber intents em linguagem natural ou estruturada
2. **Interpretação Semântica**: Parsing de ontologias OWL para extrair conceitos de rede
3. **Geração de NEST**: Criação de Network Slice Templates baseados em intents validados
4. **Persistência**: Armazenamento de intents e NESTs em PostgreSQL

**Tecnologias:**
- Framework: FastAPI (Python)
- Ontologia: RDFLib para parsing de OWL
- Banco de dados: PostgreSQL com SQLAlchemy
- Comunicação: gRPC (I-01) para Decision Engine, REST para ML-NSMF (I-02)

**Documentação completa:** [`sem-csmf/SEM_CSMF_COMPLETE_GUIDE.md`](sem-csmf/SEM_CSMF_COMPLETE_GUIDE.md)

### 3.2 ML-NSMF (Machine Learning Network Slice Management Function)

**Propósito:**
O ML-NSMF utiliza machine learning para prever a viabilidade de SLAs e possíveis violações, fornecendo explicações através de técnicas de Explainable AI (XAI) para transparência nas decisões.

**Funcionalidades principais:**
1. **Análise de Viabilidade**: Recebe NESTs do SEM-NSMF via REST (I-02)
2. **Predição de Violações**: Modelo Random Forest treinado com dados históricos
3. **Explainable AI (XAI)**: Explicação de predições usando SHAP values
4. **Publicação de Predições**: Envio de predições para Decision Engine via Kafka (I-03)

**Tecnologias:**
- Framework: FastAPI (Python)
- ML: scikit-learn (Random Forest), numpy, pandas
- XAI: SHAP
- Comunicação: REST (I-02), Kafka (I-03)

**Documentação completa:** [`ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md`](ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md)

### 3.3 Decision Engine (Motor de Decisão)

**Propósito:**
O Decision Engine é o núcleo decisório do TriSLA, agregando informações de múltiplas fontes (SEM-NSMF, ML-NSMF) e tomando decisões automatizadas sobre aceitar, rejeitar ou negociar SLAs.

**Funcionalidades principais:**
1. **Agregação de Dados**: Recebe metadados de NEST via gRPC (I-01) e predições ML via Kafka (I-03)
2. **Motor de Regras**: Aplicação de regras de negócio configuráveis
3. **Decisão Híbrida**: Combinação de regras baseadas em políticas e predições ML
4. **Publicação de Decisões**: Envio de decisões para BC-NSSMF (I-04) e ações para SLA-Agent Layer (I-05)

**Tecnologias:**
- Framework: FastAPI + gRPC (Python)
- Comunicação: gRPC (I-01), Kafka (I-03, I-04, I-05)
- Motor de regras: Implementação customizada em Python

### 3.4 BC-NSSMF (Blockchain-enabled Network Slice Subnet Management Function)

**Propósito:**
O BC-NSSMF registra SLAs aprovados e decisões em blockchain para garantir imutabilidade, auditabilidade e rastreabilidade completa do ciclo de vida de SLAs.

**Funcionalidades principais:**
1. **Registro de SLAs**: Recebe decisões do Decision Engine via Kafka (I-04)
2. **Smart Contracts**: Contrato Solidity para armazenamento de SLAs
3. **Atualização de Status**: Atualização de status de SLA (active, violated, terminated)
4. **Consulta e Auditoria**: API REST para consulta de SLAs registrados

**Tecnologias:**
- Framework: FastAPI (Python)
- Blockchain: Hyperledger Besu / GoQuorum (Ethereum permissionado)
- Smart Contracts: Solidity
- Cliente: Web3.py
- Comunicação: Kafka (I-04), REST para consultas

**Documentação completa:** [`bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md`](bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md)

### 3.5 SLA-Agent Layer (Camada de Agentes SLA)

**Propósito:**
O SLA-Agent Layer implementa agentes federados que coletam métricas e executam ações corretivas nos domínios RAN, Transport e Core de forma distribuída.

**Funcionalidades principais:**
1. **Agentes por Domínio**: RAN Agent, Transport Agent, Core Agent
2. **Coleta de Métricas**: Polling periódico de métricas de cada domínio
3. **Execução de Ações**: Recebe ações do Decision Engine via Kafka (I-05)
4. **Monitoramento em Tempo Real**: API REST para métricas em tempo real

**Tecnologias:**
- Framework: FastAPI (Python)
- Comunicação: Kafka (I-05), REST (I-06)
- Agentes: Implementação customizada por domínio

### 3.6 NASP Adapter (Adaptador NASP)

**Propósito:**
O NASP Adapter atua como ponte entre o TriSLA e a plataforma NASP real, traduzindo ações do SLA-Agent Layer em chamadas de API do NASP e coletando métricas dos domínios de rede.

**Funcionalidades principais:**
1. **Tradução de Ações**: Recebe ações do SLA-Agent Layer via REST (I-06)
2. **Coleta de Métricas**: Consulta APIs do NASP para métricas de RAN, Transport e Core
3. **Gerenciamento de Conexões**: Autenticação mTLS com NASP
4. **Abstração de Domínios**: Interface unificada para múltiplos domínios

**Tecnologias:**
- Framework: FastAPI (Python)
- Comunicação: REST (I-06, I-07)
- Segurança: mTLS, OAuth2

---

## 4. Fluxo Operacional Completo (Intent → SLA → Slice)

### 4.1 Fluxo End-to-End

O fluxo completo desde a recepção de intent até a execução no NASP:

1. **Tenant** envia intent → **SEM-NSMF** (I-01)
2. **SEM-NSMF** gera NEST → **ML-NSMF** (I-02)
3. **ML-NSMF** prediz viabilidade → **Decision Engine** (I-03)
4. **Decision Engine** decide → **BC-NSSMF** (I-04) e **SLA-Agent Layer** (I-05)
5. **SLA-Agent Layer** executa ações → **NASP Adapter** (I-06)
6. **NASP Adapter** provisiona slice → **NASP** (I-07)

**Tempo total estimado:** ~25-30 segundos (end-to-end)

### 4.2 Estados do SLA

```
CREATED → VALIDATED → PENDING_DECISION → ACCEPTED → PROVISIONED → ACTIVE
                                                      │
                                                      ▼
                                                 VIOLATED
                                                      │
                                                      ▼
                                                 TERMINATED
```

---

## 5. Interação entre Domínios

### 5.1 Domínio RAN (Radio Access Network)

**Responsabilidades:**
- Gerenciamento de recursos de rádio (PRB - Physical Resource Blocks)
- Alocação de espectro e frequências
- Controle de handover e mobilidade

**Métricas coletadas:**
- PRB utilization (%)
- Throughput (Mbps)
- Latency (ms)
- Active UEs (User Equipment)

### 5.2 Domínio Transport

**Responsabilidades:**
- Gerenciamento de conectividade entre RAN e Core
- Alocação de bandwidth e QoS
- Roteamento e switching

**Métricas coletadas:**
- Bandwidth utilization (%)
- Packet loss rate (%)
- Jitter (ms)
- Latency (ms)

### 5.3 Domínio Core

**Responsabilidades:**
- Gerenciamento de sessões e conexões
- Políticas de rede e QoS
- Autenticação e autorização

**Métricas coletadas:**
- Active sessions count
- Session establishment latency (ms)
- Authentication success rate (%)
- Policy enforcement rate (%)

---

## 6. Visão das Interfaces Internas (I-01 a I-07)

### 6.1 Interfaces Principais

| Interface | Protocolo | Direção | Descrição |
|-----------|-----------|---------|-----------|
| **I-01** | gRPC | SEM-NSMF → Decision Engine | Transmissão de metadados de NEST |
| **I-02** | REST | SEM-NSMF → ML-NSMF | Transmissão de NEST completo |
| **I-03** | Kafka | ML-NSMF → Decision Engine | Transmissão de predições ML |
| **I-04** | Kafka | Decision Engine → BC-NSSMF | Transmissão de decisões |
| **I-05** | Kafka | Decision Engine → SLA-Agent Layer | Transmissão de ações |
| **I-06** | REST | SLA-Agent Layer → NASP Adapter | Transmissão de ações |
| **I-07** | REST + mTLS | NASP Adapter → NASP | Execução real no NASP |

### 6.2 Padrões de Comunicação

**Síncrona (I-01, I-02, I-06, I-07):**
- Requisição-resposta imediata
- Timeout configurável
- Retry com backoff exponencial

**Assíncrona (I-03, I-04, I-05):**
- Mensageria via Kafka
- Exactly-once semantics
- Retenção configurável (7-30 dias)

---

## 7. Observabilidade

### 7.1 OpenTelemetry (OTLP)

Todos os módulos TriSLA são instrumentados com OpenTelemetry para coleta de:
- **Métricas**: Contadores, histogramas, gauges
- **Traces**: Spans distribuídos para rastreabilidade
- **Logs**: Logs estruturados

### 7.2 Prometheus

- OTLP Collector exporta métricas para Prometheus
- Scraping a cada 15 segundos (configurável)
- Armazenamento em time-series database

### 7.3 Grafana Dashboards

Dashboards principais:
1. **TriSLA Overview**: Taxa de intents processados, decisões por tipo
2. **SLA Monitoring**: SLAs ativos, taxa de violações, compliance rate
3. **Module Health**: Status de cada módulo, taxa de erros
4. **Blockchain Metrics**: Transações registradas, latência

---

## 8. Blockchain

### 8.1 Papel dos Smart Contracts

**Registro imutável:**
- Todas as decisões de SLA são registradas em blockchain
- Histórico completo e auditável
- Prova criptográfica de integridade

**Enforcement automatizado:**
- Smart contracts podem executar ações automáticas
- Validação de condições de SLA
- Disparo de eventos para outros módulos

### 8.2 Arquitetura Blockchain

**Blockchain permissionado:**
- Hyperledger Besu ou GoQuorum
- Apenas nós autorizados podem participar
- Consenso: IBFT 2.0 ou QBFT

**Smart Contracts:**
- Solidity para lógica de negócio
- Deploy via Hardhat
- Testes automatizados

---

## 10. Considerações sobre Escalabilidade e Resiliência

### 10.1 Escalabilidade

**Escalabilidade horizontal:**
- Todos os módulos são stateless quando possível
- Suporte a múltiplas réplicas via Kubernetes
- Load balancing automático

**Bottlenecks potenciais:**
- **Blockchain**: Limitação de throughput de transações
- **PostgreSQL**: Escala vertical ou sharding
- **Kafka**: Particionamento adequado de tópicos

### 10.2 Resiliência

**Tolerância a falhas:**
- Circuit breakers em chamadas externas
- Retry com backoff exponencial
- Timeouts configuráveis
- Health checks e readiness probes

### 10.3 Disponibilidade

**SLA de disponibilidade:**
- **Objetivo**: 99.9% uptime (8.76 horas de downtime/ano)
- **Estratégia**: Múltiplas réplicas, health checks, auto-recovery

---

## Conclusão

A arquitetura TriSLA representa uma solução completa e moderna para gerenciamento automatizado de SLAs em redes 5G/O-RAN. Através da integração de interpretação semântica, machine learning, blockchain e agentes federados, a arquitetura fornece:

- **Automação completa**: Do intent à execução
- **Inteligência**: Predições ML com explicações
- **Auditabilidade**: Registro imutável em blockchain
- **Observabilidade**: Métricas, traces e logs completos
- **Integração**: Conectividade nativa com NASP
- **Escalabilidade**: Arquitetura preparada para crescimento
- **Resiliência**: Tolerância a falhas e recuperação automática

---

**Última atualização:** 2025-01-27  
**Versão do documento:** S4.0  
**Versão da arquitetura:** 3.7.10

**Referências:**
- [README.md](README.md): Visão geral da documentação
- [METHODOLOGY.md](METHODOLOGY.md): Metodologia de validação
- [sem-csmf/SEM_CSMF_COMPLETE_GUIDE.md](sem-csmf/SEM_CSMF_COMPLETE_GUIDE.md): Guia completo do SEM-NSMF
- [ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md](ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md): Guia completo do ML-NSMF
- [bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md](bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md): Guia completo do BC-NSSMF

