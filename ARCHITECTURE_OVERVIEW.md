# TriSLA — Visão Geral da Arquitetura

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
2. **Predição Inteligente**: Machine Learning (LSTM) com Explainable AI (XAI) para prever violações
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

### 2.1 Diagrama Arquitetural (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA DE APLICAÇÃO                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    UI Dashboard (React)                              │  │
│  │                    Porta: 3001                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ REST API
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE ORQUESTRAÇÃO                                │
│                                                                             │
│  ┌──────────────────┐         ┌──────────────────┐                       │
│  │   SEM-CSMF        │         │  Decision Engine  │                       │
│  │   (Semantic)      │────────▶│  (Core Logic)     │                       │
│  │   Porta: 8080     │  I-01   │  Porta: 50051     │                       │
│  │                   │  gRPC   │  (gRPC)           │                       │
│  └────────┬──────────┘         └───────┬───────────┘                       │
│           │                             │                                   │
│           │ I-02                        │                                   │
│           │ REST                        │                                   │
│           ▼                             │                                   │
│  ┌──────────────────┐                  │                                   │
│  │   ML-NSMF         │                  │                                   │
│  │   (AI/ML)         │                  │                                   │
│  │   Porta: 8081     │                  │                                   │
│  └────────┬──────────┘                  │                                   │
│           │                              │                                   │
│           │ I-03                         │                                   │
│           │ Kafka                        │                                   │
│           │                              │                                   │
│           └──────────────────────────────┘                                   │
│                                      │                                       │
│                                      │ I-04, I-05                            │
│                                      │ Kafka                                 │
│                                      ▼                                       │
│  ┌──────────────────┐         ┌──────────────────┐                       │
│  │   BC-NSSMF        │         │  SLA-Agent Layer  │                       │
│  │   (Blockchain)    │         │  (Federated)      │                       │
│  │   Porta: 8083     │         │  Porta: 8084     │                       │  │
│  └───────────────────┘         └───────┬───────────┘                       │
│                                        │                                     │
│                                        │ I-06                                │
│                                        │ REST                                │
│                                        ▼                                     │
│                              ┌──────────────────┐                            │
│                              │  NASP Adapter    │                            │
│                              │  Porta: 8085     │                            │
│                              └───────┬──────────┘                            │
│                                      │                                        │
│                                      │ I-07                                  │
│                                      │ REST + mTLS                           │
│                                      ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE INFRAESTRUTURA                              │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                     │
│  │   NASP       │  │   NASP       │  │   NASP       │                     │
│  │   RAN        │  │  Transport   │  │   Core       │                     │
│  │   Domain     │  │   Domain     │  │   Domain     │                     │
│  └──────────────┘  └──────────────┘  └──────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE MENSAGERIA                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                         Apache Kafka                                │  │
│  │  Tópicos:                                                            │  │
│  │  - trisla-ml-predictions (I-03)                                     │  │
│  │  - trisla-i04-decisions (I-04)                                      │  │
│  │  - trisla-i05-actions (I-05)                                       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE OBSERVABILIDADE                            │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │ OTLP         │  │  Prometheus   │  │   Grafana    │                    │
│  │ Collector    │  │  Porta: 9090  │  │  Porta: 3000 │                    │
│  │ Porta: 4317  │  │               │  │               │                    │
│  └──────┬───────┘  └───────┬──────┘  └───────┬──────┘                    │
│         │                  │                  │                             │
│         └──────────────────┴──────────────────┘                             │
│                          OTLP Protocol                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE PERSISTÊNCIA                               │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐                                       │
│  │  PostgreSQL  │  │  Blockchain  │                                       │
│  │  Porta: 5432│  │  (Besu/      │                                       │
│  │              │  │  GoQuorum)   │                                       │
│  └──────────────┘  └──────────────┘                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
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

### 3.1 SEM-CSMF (Semantic-enhanced Communication Service Management Function)

**Propósito:**
O SEM-CSMF é responsável por receber intents de tenants, interpretá-los semanticamente usando ontologias OWL, e gerar Network Slice Templates (NEST) que descrevem os requisitos de rede de forma estruturada.

**Funcionalidades principais:**

1. **Recepção de Intents:**
   - API REST para receber intents em linguagem natural ou estruturada
   - Validação de formato e campos obrigatórios

2. **Interpretação Semântica:**
   - Parsing de ontologias OWL para extrair conceitos de rede
   - Matching semântico entre intents e templates de serviço
   - Validação de requisitos de SLA contra capacidades disponíveis

3. **Geração de NEST:**
   - Criação de Network Slice Templates baseados em intents validados
   - Mapeamento de requisitos de SLA para recursos de rede
   - Geração de subconjuntos de NEST para diferentes domínios

4. **Persistência:**
   - Armazenamento de intents e NESTs em PostgreSQL
   - Histórico de gerações para auditoria

**Tecnologias:**
- **Framework**: FastAPI (Python)
- **Ontologia**: RDFLib para parsing de OWL
- **Banco de dados**: PostgreSQL com SQLAlchemy
- **Comunicação**: gRPC (I-01) para Decision Engine, REST para ML-NSMF (I-02)

**Fluxo interno:**

```
Intent Recebido
    │
    ▼
Validação de Formato
    │
    ▼
Parsing de Ontologia OWL
    │
    ▼
Matching Semântico
    │
    ▼
Geração de GST (Generation Service Template)
    │
    ▼
Geração de NEST (Network Slice Template)
    │
    ├─── Metadados → I-01 → Decision Engine
    └─── NEST Completo → I-02 → ML-NSMF
```

### 3.2 ML-NSMF (Machine Learning Network Slice Management Function)

**Propósito:**
O ML-NSMF utiliza machine learning para prever a viabilidade de SLAs e possíveis violações, fornecendo explicações através de técnicas de Explainable AI (XAI) para transparência nas decisões.

**Funcionalidades principais:**

1. **Análise de Viabilidade:**
   - Recebe NESTs do SEM-CSMF via REST (I-02)
   - Analisa requisitos de SLA contra métricas históricas
   - Calcula score de viabilidade (0.0 a 1.0)

2. **Predição de Violações:**
   - Modelo LSTM treinado com dados históricos de SLAs
   - Predição de probabilidade de violação
   - Identificação de fatores de risco

3. **Explainable AI (XAI):**
   - Explicação de predições usando SHAP values
   - Identificação de features mais importantes
   - Visualização de contribuições de cada fator

4. **Publicação de Predições:**
   - Envio de predições para Decision Engine via Kafka (I-03)
   - Formato estruturado com scores e explicações

**Tecnologias:**
- **Framework**: FastAPI (Python)
- **ML**: scikit-learn, numpy, pandas
- **XAI**: SHAP (quando disponível)
- **Comunicação**: REST (I-02), Kafka (I-03)

**Modelo de ML:**

```
Input Features:
  - CPU utilization
  - Memory utilization
  - Network bandwidth available
  - Active slices count
  - Historical violation rate
  - SLA requirements (latency, throughput, reliability)

Model: LSTM (Long Short-Term Memory)
  ↓
Output:
  - Viability Score (0.0 - 1.0)
  - Recommendation (ACCEPT/REJECT/RENEGOTIATE)
  - Confidence (0.0 - 1.0)
  - Explanation (SHAP values, top features)
```

### 3.3 Decision Engine (Motor de Decisão)

**Propósito:**
O Decision Engine é o núcleo decisório do TriSLA, agregando informações de múltiplas fontes (SEM-CSMF, ML-NSMF) e tomando decisões automatizadas sobre aceitar, rejeitar ou negociar SLAs.

**Funcionalidades principais:**

1. **Agregação de Dados:**
   - Recebe metadados de NEST via gRPC (I-01) do SEM-CSMF
   - Recebe predições ML via Kafka (I-03) do ML-NSMF
   - Consulta métricas atuais de recursos disponíveis

2. **Motor de Regras:**
   - Aplicação de regras de negócio configuráveis
   - Validação de requisitos de SLA contra políticas
   - Verificação de disponibilidade de recursos

3. **Decisão Híbrida:**
   - Combinação de regras baseadas em políticas e predições ML
   - Peso configurável entre regras e ML
   - Geração de decisão final: ACCEPT, REJECT ou RENEGOTIATE

4. **Publicação de Decisões:**
   - Envio de decisões para BC-NSSMF via Kafka (I-04) para registro em blockchain
   - Envio de ações para SLA-Agent Layer via Kafka (I-05) para execução

**Tecnologias:**
- **Framework**: FastAPI + gRPC (Python)
- **Comunicação**: gRPC (I-01), Kafka (I-03, I-04, I-05)
- **Motor de regras**: Implementação customizada em Python

**Algoritmo de decisão:**

```
Input:
  - NEST Metadata (I-01)
  - ML Prediction (I-03)
  - Current Resource Metrics

Process:
  1. Apply Rule Engine:
     - Check SLA requirements vs policies
     - Verify resource availability
     - Validate tenant permissions
  
  2. Apply ML Score:
     - Viability score > 0.7 → Positive indicator
     - Confidence > 0.8 → High reliability
  
  3. Combine Results:
     - Rules: 60% weight
     - ML: 40% weight
     - Final decision = weighted combination

Output:
  - Decision: ACCEPT / REJECT / RENEGOTIATE
  - Reason: Detailed explanation
  - Actions: List of actions to execute
```

### 3.4 BC-NSSMF (Blockchain-enabled Network Slice Subnet Management Function)

**Propósito:**
O BC-NSSMF registra SLAs aprovados e decisões em blockchain para garantir imutabilidade, auditabilidade e rastreabilidade completa do ciclo de vida de SLAs.

**Funcionalidades principais:**

1. **Registro de SLAs:**
   - Recebe decisões do Decision Engine via Kafka (I-04)
   - Valida assinatura digital da decisão
   - Cria transação no smart contract

2. **Smart Contracts:**
   - Contrato Solidity para armazenamento de SLAs
   - Estrutura de dados imutável para cada SLA
   - Eventos on-chain para auditoria

3. **Atualização de Status:**
   - Atualização de status de SLA (active, violated, terminated)
   - Registro de violações detectadas
   - Histórico completo de mudanças

4. **Consulta e Auditoria:**
   - API REST para consulta de SLAs registrados
   - Verificação de integridade via hash
   - Exportação de provas criptográficas

**Tecnologias:**
- **Framework**: FastAPI (Python)
- **Blockchain**: Hyperledger Besu / GoQuorum (Ethereum permissionado)
- **Smart Contracts**: Solidity
- **Cliente**: Web3.py
- **Comunicação**: Kafka (I-04), REST para consultas

**Estrutura do Smart Contract:**

```solidity
contract SLAContract {
    struct SLA {
        string decisionId;
        string intentId;
        string tenantId;
        string decision;  // ACCEPT, REJECT, RENEGOTIATE
        string reason;
        uint256 timestamp;
        bytes32 signature;
        SLAStatus status;
    }
    
    mapping(string => SLA) public slas;
    
    function registerSLA(SLA memory sla) public returns (bool);
    function updateStatus(string memory decisionId, SLAStatus status) public;
    event SLARegistered(string indexed decisionId, string decision);
    event SLAStatusUpdated(string indexed decisionId, SLAStatus status);
}
```

### 3.5 SLA-Agent Layer (Camada de Agentes SLA)

**Propósito:**
O SLA-Agent Layer implementa agentes federados que coletam métricas e executam ações corretivas nos domínios RAN, Transport e Core de forma distribuída.

**Funcionalidades principais:**

1. **Agentes por Domínio:**
   - **RAN Agent**: Coleta métricas de RAN (PRB utilization, latency, throughput)
   - **Transport Agent**: Coleta métricas de transporte (bandwidth, jitter, packet loss)
   - **Core Agent**: Coleta métricas de core (session count, connection latency)

2. **Coleta de Métricas:**
   - Polling periódico de métricas de cada domínio
   - Agregação e normalização de dados
   - Publicação de métricas para observabilidade

3. **Execução de Ações:**
   - Recebe ações do Decision Engine via Kafka (I-05)
   - Filtra ações por domínio (RAN, Transport, Core)
   - Executa ações via NASP Adapter (I-06)

4. **Monitoramento em Tempo Real:**
   - API REST para métricas em tempo real
   - Endpoint de SLOs ativos
   - Detecção de violações

**Tecnologias:**
- **Framework**: FastAPI (Python)
- **Comunicação**: Kafka (I-05), REST (I-06)
- **Agentes**: Implementação customizada por domínio

**Arquitetura de Agentes:**

```
SLA-Agent Layer
    │
    ├─── RAN Agent
    │    ├─── Collect Metrics (PRB, latency, throughput)
    │    └─── Execute Actions (slice provisioning, scaling)
    │
    ├─── Transport Agent
    │    ├─── Collect Metrics (bandwidth, jitter, packet loss)
    │    └─── Execute Actions (connection setup, QoS adjustment)
    │
    └─── Core Agent
         ├─── Collect Metrics (sessions, connections, latency)
         └─── Execute Actions (session management, policy updates)
```

### 3.6 NASP Adapter (Adaptador NASP)

**Propósito:**
O NASP Adapter atua como ponte entre o TriSLA e a plataforma NASP real, traduzindo ações do SLA-Agent Layer em chamadas de API do NASP e coletando métricas dos domínios de rede.

**Funcionalidades principais:**

1. **Tradução de Ações:**
   - Recebe ações do SLA-Agent Layer via REST (I-06)
   - Traduz para formato de API do NASP
   - Executa chamadas para NASP (I-07)

2. **Coleta de Métricas:**
   - Consulta APIs do NASP para métricas de RAN, Transport e Core
   - Normaliza dados para formato interno
   - Disponibiliza via API REST

3. **Gerenciamento de Conexões:**
   - Autenticação mTLS com NASP
   - Gerenciamento de tokens OAuth2
   - Retry e circuit breakers

4. **Abstração de Domínios:**
   - Interface unificada para múltiplos domínios
   - Tratamento de diferenças entre fornecedores
   - Fallback em caso de falhas

**Tecnologias:**
- **Framework**: FastAPI (Python)
- **Comunicação**: REST (I-06, I-07)
- **Segurança**: mTLS, OAuth2
- **Cliente HTTP**: httpx ou requests

**Mapeamento de Ações:**

```
TriSLA Action          →  NASP API Call
─────────────────────────────────────────────
PROVISION_SLICE        →  POST /api/v1/slices
SCALE_SLICE            →  PUT /api/v1/slices/{id}/scale
RECONFIGURE_SLICE      →  PUT /api/v1/slices/{id}/config
TERMINATE_SLICE        →  DELETE /api/v1/slices/{id}
COLLECT_METRICS        →  GET /api/v1/metrics/{domain}
```

---

## 4. Fluxo Operacional Completo (Intent → SLA → Slice)

### 4.1 Fluxo End-to-End

```
┌─────────────┐
│   Tenant    │
└──────┬──────┘
       │
       │ 1. POST /api/v1/intents
       │    {"intent": "Criar slice para AR com latência < 10ms"}
       ▼
┌─────────────────────────────────────────────────────────────┐
│  SEM-CSMF                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. Recebe Intent                                     │  │
│  │ 3. Valida Formato                                     │  │
│  │ 4. Parse Ontologia OWL                                │  │
│  │ 5. Matching Semântico                                  │  │
│  │ 6. Gera NEST (Network Slice Template)                 │  │
│  └──────┬───────────────────────────────────────────────┘  │
│         │                                                   │
│         │ 7. I-01 (gRPC): Envia Metadados NEST             │
│         ▼                                                   │
└─────────────────────────────────────────────────────────────┘
         │
         │ 8. I-02 (REST): Envia NEST Completo
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ML-NSMF                                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 9. Recebe NEST                                        │  │
│  │ 10. Analisa Requisitos de SLA                         │  │
│  │ 11. Consulta Métricas Históricas                      │  │
│  │ 12. Executa Modelo LSTM                               │  │
│  │ 13. Calcula Viability Score                           │  │
│  │ 14. Gera Explicação (XAI)                             │  │
│  └──────┬───────────────────────────────────────────────┘  │
│         │                                                   │
│         │ 15. I-03 (Kafka): Envia Predição                │
│         ▼                                                   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Decision Engine                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 16. Recebe Metadados NEST (I-01)                       │  │
│  │ 17. Recebe Predição ML (I-03)                          │  │
│  │ 18. Aplica Motor de Regras                            │  │
│  │ 19. Combina Regras + ML                                │  │
│  │ 20. Toma Decisão: ACCEPT/REJECT/RENEGOTIATE           │  │
│  └──────┬───────────────────────────────────────────────┘  │
│         │                                                   │
│         ├─── 21. I-04 (Kafka): Envia Decisão ──────────────┐
│         │                                                   │ │
│         └─── 22. I-05 (Kafka): Envia Ações ────────────────┤
│                                                             │ │
└─────────────────────────────────────────────────────────────┘ │
         │                                                       │
         │                                                       │
         ▼                                                       │
┌─────────────────────────────────────────────────────────────┐ │
│  BC-NSSMF                                                    │ │
│  ┌──────────────────────────────────────────────────────┐  │ │
│  │ 23. Recebe Decisão (I-04)                            │  │ │
│  │ 24. Valida Assinatura                                 │  │ │
│  │ 25. Cria Transação Blockchain                        │  │ │
│  │ 26. Registra SLA em Smart Contract                   │  │ │
│  │ 27. Emite Evento On-Chain                            │  │ │
│  └──────────────────────────────────────────────────────┘  │ │
└─────────────────────────────────────────────────────────────┘ │
                                                                 │
         │                                                       │
         │                                                       │
         ▼                                                       │
┌─────────────────────────────────────────────────────────────┐ │
│  SLA-Agent Layer                                             │ │
│  ┌──────────────────────────────────────────────────────┐  │ │
│  │ 28. Recebe Ações (I-05)                              │  │ │
│  │ 29. Filtra por Domínio (RAN/Transport/Core)         │  │ │
│  │ 30. Prepara Ações para Execução                      │  │ │
│  └──────┬───────────────────────────────────────────────┘  │ │
│         │                                                   │ │
│         │ 31. I-06 (REST): Envia Ações                     │ │
│         ▼                                                   │ │
└─────────────────────────────────────────────────────────────┘ │
         │                                                       │
         │                                                       │
         ▼                                                       │
┌─────────────────────────────────────────────────────────────┐ │
│  NASP Adapter                                               │ │
│  ┌──────────────────────────────────────────────────────┐  │ │
│  │ 32. Recebe Ações (I-06)                               │  │ │
│  │ 33. Traduz para Formato NASP                          │  │ │
│  │ 34. Autentica com NASP (mTLS + OAuth2)               │  │ │
│  │ 35. Executa Chamadas NASP (I-07)                      │  │ │
│  └──────┬───────────────────────────────────────────────┘  │ │
│         │                                                   │ │
│         │ 36. I-07 (REST + mTLS): Provisiona Slice         │ │
│         ▼                                                   │ │
└─────────────────────────────────────────────────────────────┘ │
         │                                                       │
         │                                                       │
         ▼                                                       │
┌─────────────────────────────────────────────────────────────┐ │
│  NASP Platform                                              │ │
│  ┌──────────────────────────────────────────────────────┐  │ │
│  │ 37. Recebe Requisição de Provisionamento              │  │ │
│  │ 38. Valida Permissões                                 │  │ │
│  │ 39. Aloca Recursos (RAN/Transport/Core)              │  │ │
│  │ 40. Provisiona Network Slice                          │  │ │
│  │ 41. Retorna Confirmação                               │  │ │
│  └──────────────────────────────────────────────────────┘  │ │
└─────────────────────────────────────────────────────────────┘ │
                                                                 │
         │                                                       │
         │ 42. Resposta Cascata (NASP → Adapter → Agent)       │
         │                                                       │
         ▼                                                       │
┌─────────────────────────────────────────────────────────────┐ │
│  Observabilidade (OTLP)                                      │ │
│  ┌──────────────────────────────────────────────────────┐  │ │
│  │ 43. Métricas Coletadas em Todas as Etapas            │  │ │
│  │ 44. Traces Gerados para Rastreabilidade              │  │ │
│  │ 45. Logs Estruturados                                 │  │ │
│  │ 46. Exportação para Prometheus/Grafana                │  │ │
│  └──────────────────────────────────────────────────────┘  │ │
└─────────────────────────────────────────────────────────────┘ │
                                                                 │
         │                                                       │
         │ 47. SLA Registrado e Ativo                           │
         │                                                       │
         ▼                                                       │
┌─────────────────────────────────────────────────────────────┐ │
│  Tenant                                                      │ │
│  ┌──────────────────────────────────────────────────────┐  │ │
│  │ 48. Recebe Confirmação de SLA Ativo                   │  │ │
│  │ 49. Network Slice Disponível para Uso                 │  │ │
│  └──────────────────────────────────────────────────────┘  │ │
└─────────────────────────────────────────────────────────────┘ │
```

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

**Transições:**

- **CREATED**: Intent recebido pelo SEM-CSMF
- **VALIDATED**: NEST gerado e validado
- **PENDING_DECISION**: Aguardando decisão do Decision Engine
- **ACCEPTED**: Decisão ACCEPT, aguardando provisionamento
- **PROVISIONED**: Slice provisionado no NASP
- **ACTIVE**: Slice ativo e operacional
- **VIOLATED**: Violação de SLA detectada
- **TERMINATED**: SLA encerrado

---

## 5. Interação entre Domínios

### 5.1 Domínio RAN (Radio Access Network)

**Responsabilidades:**
- Gerenciamento de recursos de rádio (PRB - Physical Resource Blocks)
- Alocação de espectro e frequências
- Controle de handover e mobilidade
- Otimização de cobertura e capacidade

**Métricas coletadas:**
- PRB utilization (%)
- Throughput (Mbps)
- Latency (ms)
- Active UEs (User Equipment)
- Handover success rate (%)

**Ações executadas:**
- Provisionamento de slice RAN
- Escalonamento de recursos PRB
- Ajuste de parâmetros de rádio
- Reconfiguração de células

**Integração NASP:**
- API: `POST /api/v1/ran/slices`
- Métricas: `GET /api/v1/ran/metrics`
- Ações: `PUT /api/v1/ran/slices/{id}/reconfigure`

### 5.2 Domínio Transport

**Responsabilidades:**
- Gerenciamento de conectividade entre RAN e Core
- Alocação de bandwidth e QoS
- Roteamento e switching
- Gerenciamento de links de transporte

**Métricas coletadas:**
- Bandwidth utilization (%)
- Packet loss rate (%)
- Jitter (ms)
- Latency (ms)
- Throughput (Mbps)

**Ações executadas:**
- Provisionamento de conexões de transporte
- Ajuste de bandwidth e QoS
- Reconfiguração de rotas
- Escalonamento de links

**Integração NASP:**
- API: `POST /api/v1/transport/connections`
- Métricas: `GET /api/v1/transport/metrics`
- Ações: `PUT /api/v1/transport/connections/{id}/qos`

### 5.3 Domínio Core

**Responsabilidades:**
- Gerenciamento de sessões e conexões
- Políticas de rede e QoS
- Autenticação e autorização
- Gerenciamento de mobilidade

**Métricas coletadas:**
- Active sessions count
- Session establishment latency (ms)
- Authentication success rate (%)
- Policy enforcement rate (%)
- Connection throughput (Mbps)

**Ações executadas:**
- Provisionamento de sessões
- Atualização de políticas
- Reconfiguração de QoS
- Gerenciamento de mobilidade

**Integração NASP:**
- API: `POST /api/v1/core/sessions`
- Métricas: `GET /api/v1/core/metrics`
- Ações: `PUT /api/v1/core/policies/{id}`

### 5.4 Coordenação entre Domínios

**Orquestração:**
O Decision Engine coordena ações entre domínios para garantir consistência:

```
Decision: ACCEPT
    │
    ├─── RAN: Provision slice with 50 PRBs
    ├─── Transport: Allocate 1Gbps bandwidth
    └─── Core: Create 1000 sessions capacity
```

**Sincronização:**
- Ações são executadas em paralelo quando possível
- Dependências são respeitadas (ex: Transport antes de Core)
- Rollback automático em caso de falha parcial

---

## 6. Visão das Interfaces Internas (I-01 a I-07)

### 6.1 Visão Integrada das Interfaces

As interfaces internas do TriSLA (I-01 a I-07) formam uma rede de comunicação que permite o fluxo de dados e decisões entre módulos. A seguir, uma visão integrada sem repetir detalhes técnicos já documentados em `INTERNAL_INTERFACES_I01_I07.md`.

**I-01 (gRPC): SEM-CSMF → Decision Engine**
- **Papel**: Transmissão síncrona de metadados de NEST
- **Criticidade**: Alta (entrada do fluxo de decisão)
- **Latência**: < 50ms p99

**I-02 (REST): SEM-CSMF → ML-NSMF**
- **Papel**: Transmissão de NEST completo para análise ML
- **Criticidade**: Média (suporte à decisão)
- **Latência**: < 100ms p99

**I-03 (Kafka): ML-NSMF → Decision Engine**
- **Papel**: Transmissão assíncrona de predições ML
- **Criticidade**: Alta (insumo crítico para decisão)
- **Latência**: < 10ms (produção)

**I-04 (Kafka): Decision Engine → BC-NSSMF**
- **Papel**: Transmissão de decisões para registro em blockchain
- **Criticidade**: Alta (auditoria e compliance)
- **Latência**: < 10ms (produção)

**I-05 (Kafka): Decision Engine → SLA-Agent Layer**
- **Papel**: Transmissão de ações para execução nos domínios
- **Criticidade**: Alta (execução do SLA)
- **Latência**: < 10ms (produção)

**I-06 (REST): SLA-Agent Layer → NASP Adapter**
- **Papel**: Transmissão de ações para tradução e execução no NASP
- **Criticidade**: Alta (integração com infraestrutura)
- **Latência**: < 200ms p99

**I-07 (REST + mTLS): NASP Adapter → NASP**
- **Papel**: Execução real de ações na plataforma NASP
- **Criticidade**: Crítica (execução final)
- **Latência**: < 500ms p99

### 6.2 Padrões de Comunicação

**Síncrona (I-01, I-02, I-06, I-07):**
- Requisição-resposta imediata
- Timeout configurável
- Retry com backoff exponencial

**Assíncrona (I-03, I-04, I-05):**
- Mensageria via Kafka
- Exactly-once semantics
- Retenção configurável (7-30 dias)

### 6.3 Garantias de Entrega

**At-least-once:**
- I-01, I-02, I-06, I-07 (REST/gRPC)
- Cliente responsável por idempotência

**Exactly-once:**
- I-03, I-04, I-05 (Kafka)
- Garantido por transações e idempotência do producer

---

## 7. Observabilidade

### 7.1 OpenTelemetry (OTLP)

**Instrumentação:**
Todos os módulos TriSLA são instrumentados com OpenTelemetry para coleta de:

- **Métricas**: Contadores, histogramas, gauges
- **Traces**: Spans distribuídos para rastreabilidade
- **Logs**: Logs estruturados (quando disponível)

**Exportação:**
- **Protocolo**: OTLP (gRPC ou HTTP)
- **Endpoint**: OTLP Collector (porta 4317 gRPC, 4318 HTTP)
- **Formato**: Protocol Buffers

**Métricas principais:**

| Módulo | Métricas Principais |
|--------|---------------------|
| SEM-CSMF | `trisla_intents_total`, `trisla_nests_generated_total`, `trisla_intent_processing_duration_seconds` |
| ML-NSMF | `trisla_predictions_total`, `trisla_prediction_duration_seconds`, `trisla_prediction_accuracy` |
| Decision Engine | `trisla_decisions_total`, `trisla_decision_latency_seconds`, `trisla_decision_by_type` |
| BC-NSSMF | `trisla_blockchain_transactions_total`, `trisla_transaction_duration_seconds` |
| SLA-Agent Layer | `trisla_actions_executed_total`, `trisla_action_duration_seconds` |
| NASP Adapter | `trisla_nasp_requests_total`, `trisla_nasp_request_duration_seconds` |

### 7.2 Prometheus

**Coleta:**
- OTLP Collector exporta métricas para Prometheus
- Scraping a cada 15 segundos (configurável)
- Armazenamento em time-series database

**Queries (PromQL):**

```promql
# Taxa de intents processados por segundo
rate(trisla_intents_total[5m])

# Latência p99 de decisões
histogram_quantile(0.99, trisla_decision_latency_seconds_bucket)

# Taxa de violações de SLA
rate(trisla_sla_violations_total[5m])
```

### 7.3 Grafana Dashboards

**Dashboards principais:**

1. **TriSLA Overview:**
   - Taxa de intents processados
   - Taxa de decisões por tipo
   - Latência de processamento

2. **SLA Monitoring:**
   - SLAs ativos por tenant
   - Taxa de violações
   - Compliance rate

3. **Module Health:**
   - Status de cada módulo
   - Taxa de erros
   - Throughput

4. **Blockchain Metrics:**
   - Transações registradas
   - Latência de transações
   - Taxa de falhas

### 7.4 Alertas

**Alertmanager:**
- Configuração de alertas baseados em métricas
- Notificações via email, Slack, PagerDuty
- Agrupamento e supressão de alertas

**Alertas críticos:**
- Módulo indisponível
- Taxa de violações > threshold
- Latência p99 > SLA
- Falhas de transação blockchain

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

**Compliance e auditoria:**
- Rastreabilidade completa do ciclo de vida
- Evidências para auditoria regulatória
- Transparência para tenants

### 8.2 Validação e Rastreabilidade

**Validação de assinaturas:**
- Decisões são assinadas digitalmente antes do registro
- Validação de assinatura no smart contract
- Prevenção de registros não autorizados

**Rastreabilidade:**
- Cada SLA possui histórico completo de mudanças
- Eventos on-chain para cada transição de estado
- Consulta de histórico via API REST

**Provas criptográficas:**
- Hash de cada decisão registrado
- Verificação de integridade via Merkle proofs
- Exportação de provas para auditoria externa

### 8.3 Arquitetura Blockchain

**Blockchain permissionado:**
- Hyperledger Besu ou GoQuorum
- Apenas nós autorizados podem participar
- Consenso: IBFT 2.0 ou QBFT

**Smart Contracts:**
- Solidity para lógica de negócio
- Deploy via Hardhat
- Testes automatizados

**Integração:**
- Cliente Web3.py para interação
- Eventos assíncronos para notificações
- Fallback em caso de indisponibilidade

---

## 9. Diagrama Final da Arquitetura End-to-End

### 9.1 Diagrama Completo (ASCII)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              TENANT / OPERATOR                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    UI Dashboard (Porta: 3001)                        │   │
│  │  - Visualização de SLAs                                              │   │
│  │  - Métricas e Dashboards                                             │   │
│  │  - Administração                                                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ REST API
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE ORQUESTRAÇÃO                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  SEM-CSMF (Semantic CSMF)                                            │   │
│  │  Porta: 8080                                                         │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ • Recebe Intents                                              │   │   │
│  │  │ • Interpretação Semântica (OWL)                              │   │   │
│  │  │ • Geração de NEST                                             │   │   │
│  │  │ • Persistência (PostgreSQL)                                   │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │         │ I-01 (gRPC)        │ I-02 (REST)                         │   │
│  │         ▼                     ▼                                      │   │
│  └─────────┼─────────────────────┼────────────────────────────────────┘   │
│            │                     │                                           │
│            │                     │                                           │
│  ┌─────────▼─────────────────────▼─────────────────────────────────────┐   │
│  │  Decision Engine (Core Decision Logic)                               │   │
│  │  Porta: 50051 (gRPC), 50052 (REST)                                  │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ • Agrega Dados (NEST + ML Prediction)                        │   │   │
│  │  │ • Motor de Regras                                             │   │   │
│  │  │ • Decisão Híbrida (Rules + ML)                               │   │   │
│  │  │ • Publicação de Decisões e Ações                              │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │         │ I-03 (Kafka)        │ I-04 (Kafka)      │ I-05 (Kafka)   │   │
│  └─────────┼──────────────────────┼──────────────────┼─────────────────┘   │
│            │                      │                  │                      │
│            │                      │                  │                      │
│  ┌─────────▼──────────────────────▼──────────────────▼─────────────────┐   │
│  │  ML-NSMF (Machine Learning)     BC-NSSMF          SLA-Agent Layer     │   │
│  │  Porta: 8081                    Porta: 8083      Porta: 8084         │   │
│  │  ┌──────────────────────────┐  ┌──────────────┐  ┌─────────────────┐ │   │
│  │  │ • Análise de Viabilidade │  │ • Registro  │  │ • RAN Agent     │ │   │
│  │  │ • Predição LSTM          │  │   Blockchain │  │ • Transport     │ │   │
│  │  │ • XAI (SHAP)             │  │ • Smart      │  │   Agent         │ │   │
│  │  │ • Publicação Kafka       │  │   Contracts  │  │ • Core Agent   │ │   │
│  │  └──────────────────────────┘  └──────────────┘  └────────┬────────┘ │   │
│  └───────────────────────────────────────────────────────────┼───────────┘   │
│                                                              │ I-06 (REST)  │
│                                                              ▼              │
│                                                    ┌─────────────────────┐ │
│                                                    │  NASP Adapter        │ │
│                                                    │  Porta: 8085         │ │
│                                                    │  ┌─────────────────┐ │ │
│                                                    │  │ • Tradução      │ │ │
│                                                    │  │ • Autenticação  │ │ │
│                                                    │  │ • Execução NASP │ │ │
│                                                    │  └─────────────────┘ │ │
│                                                    │         │ I-07        │ │
│                                                    └─────────┼────────────┘ │
│                                                              │ REST + mTLS  │
└──────────────────────────────────────────────────────────────┼──────────────┘
                                                               │
                                                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE INFRAESTRUTURA                             │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  NASP RAN        │  │  NASP Transport  │  │  NASP Core       │          │
│  │  Domain          │  │  Domain          │  │  Domain          │          │
│  │                  │  │                  │  │                  │          │
│  │ • PRB Management│  │ • Bandwidth      │  │ • Session Mgmt   │          │
│  │ • Radio Control │  │ • QoS Control    │  │ • Policy Control │          │
│  │ • Handover      │  │ • Routing        │  │ • Auth/Authz     │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE MENSAGERIA                                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Apache Kafka                                       │   │
│  │  Porta: 29092 (host), 9092 (container)                               │   │
│  │                                                                       │   │
│  │  Tópicos:                                                             │   │
│  │  • trisla-ml-predictions (I-03)                                      │   │
│  │  • trisla-i04-decisions (I-04)                                       │   │
│  │  • trisla-i05-actions (I-05)                                         │   │
│  │                                                                       │   │
│  │  Configuração:                                                        │   │
│  │  • Partitions: 3                                                      │   │
│  │  • Replication: 3                                                    │   │
│  │  • Retention: 7-30 dias                                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE OBSERVABILIDADE                             │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │  OTLP Collector   │  │  Prometheus       │  │  Grafana          │        │
│  │  Porta: 4317/4318 │  │  Porta: 9090      │  │  Porta: 3000      │        │
│  │                   │  │                   │  │                   │        │
│  │ • Recebe OTLP     │  │ • Scrapes Metrics │  │ • Dashboards      │        │
│  │ • Exporta Metrics │  │ • Time-Series DB  │  │ • Visualização    │        │
│  │ • Traces          │  │ • Alerting Rules  │  │ • Alerting        │        │
│  └────────┬──────────┘  └────────┬──────────┘  └────────┬──────────┘        │
│           │                     │                       │                    │
│           └─────────────────────┴───────────────────────┘                    │
│                          OTLP Protocol                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE PERSISTÊNCIA                                 │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                              │
│  │  PostgreSQL       │  │  Blockchain       │                              │
│  │  Porta: 5432      │  │  (Besu/GoQuorum) │                              │
│  │                   │  │                   │                              │
│  │ • Intents         │  │ • SLA Registry    │                              │
│  │ • NESTs           │  │ • Decisions       │                              │
│  │ • Metadata        │  │ • Audit Trail     │                              │
│  └──────────────────┘  └──────────────────┘                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Fluxo de Dados Completo

**Entrada:**
- Intent do tenant → SEM-CSMF

**Processamento:**
- SEM-CSMF → NEST → Decision Engine (I-01)
- SEM-CSMF → NEST → ML-NSMF (I-02)
- ML-NSMF → Predição → Decision Engine (I-03)
- Decision Engine → Decisão → BC-NSSMF (I-04)
- Decision Engine → Ações → SLA-Agent Layer (I-05)
- SLA-Agent Layer → Ações → NASP Adapter (I-06)
- NASP Adapter → Execução → NASP (I-07)

**Saída:**
- Network Slice provisionado e ativo
- SLA registrado em blockchain
- Métricas e observabilidade disponíveis

---

## 10. Considerações sobre Escalabilidade e Resiliência

### 10.1 Escalabilidade

**Escalabilidade horizontal:**
- Todos os módulos são stateless quando possível
- Suporte a múltiplas réplicas via Kubernetes
- Load balancing automático

**Escalabilidade por módulo:**

| Módulo | Estratégia de Escala |
|--------|---------------------|
| SEM-CSMF | Horizontal (múltiplas réplicas) |
| ML-NSMF | Horizontal (com cache de modelos) |
| Decision Engine | Horizontal (stateless) |
| BC-NSSMF | Vertical (limitação de blockchain) |
| SLA-Agent Layer | Horizontal (por domínio) |
| NASP Adapter | Horizontal (com pool de conexões) |

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

**Estratégias por componente:**

**SEM-CSMF:**
- Retry em falhas de gRPC (I-01)
- Fallback para processamento assíncrono
- Cache de ontologias

**ML-NSMF:**
- Modelo em cache para disponibilidade
- Fallback para regras simples em caso de falha do modelo
- Timeout em predições longas

**Decision Engine:**
- Decisão baseada apenas em regras se ML indisponível
- Queue de decisões pendentes
- Idempotência em reprocessamento

**BC-NSSMF:**
- Queue de transações pendentes
- Retry automático em falhas de blockchain
- Fallback para armazenamento temporário

**SLA-Agent Layer:**
- Agentes independentes por domínio
- Falha de um domínio não afeta outros
- Retry em ações falhadas

**NASP Adapter:**
- Circuit breaker em falhas do NASP
- Queue de ações pendentes
- Notificação de indisponibilidade

### 10.3 Disponibilidade

**SLA de disponibilidade:**
- **Objetivo**: 99.9% uptime (8.76 horas de downtime/ano)
- **Estratégia**: Múltiplas réplicas, health checks, auto-recovery

**Recuperação automática:**
- Kubernetes liveness/readiness probes
- Restart automático de containers
- Failover automático

**Backup e disaster recovery:**
- Backup periódico do PostgreSQL
- Snapshot do blockchain
- Configurações versionadas

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

A arquitetura é projetada para ser modular, extensível e mantível, permitindo evolução contínua e adaptação a novos requisitos e tecnologias.

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão da arquitetura:** 1.0.0

**Referências:**
- `README.md`: Visão geral do projeto
- `DEVELOPER_GUIDE.md`: Guia para desenvolvedores
- `API_REFERENCE.md`: Referência de APIs
- `INTERNAL_INTERFACES_I01_I07.md`: Documentação de interfaces internas
- `README_OPERATIONS_PROD.md`: Guia de operações em produção
- `SECURITY_HARDENING.md`: Guia de segurança
- `TROUBLESHOOTING_TRISLA.md`: Guia de troubleshooting


