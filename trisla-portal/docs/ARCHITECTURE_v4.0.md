# TriSLA Observability Portal v4.0 - Arquitetura Completa

**Versão:** 4.0  
**Data:** 2025-01-XX  
**Alinhado com:** FASE_6_RELATORIO_TECNICO_FINAL.md

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Diagrama Textual do Portal](#diagrama-textual-do-portal)
3. [Dataflow Completo](#dataflow-completo)
4. [Mapeamento das Telas](#mapeamento-das-telas)
5. [Mapeamento dos Endpoints da API](#mapeamento-dos-endpoints-da-api)
6. [Tabelas e Schemas dos Contratos](#tabelas-e-schemas-dos-contratos)
7. [Arquitetura XAI](#arquitetura-xai)
8. [Arquitetura PLN + Templates NEST](#arquitetura-pln--templates-nest)
9. [Arquitetura Batch SLA Creation](#arquitetura-batch-sla-creation)
10. [Mapeamento com FASE 6](#mapeamento-com-fase-6)

---

## 🎯 Visão Geral

O **TriSLA Observability Portal v4.0** é uma interface web completa de observabilidade para o TriSLA, fornecendo:

- **Visualização unificada** de métricas, traces e logs
- **Gerenciamento de contratos SLA** (criação, estado, violações, renegociações)
- **Criação de SLAs** via PLN (Processamento de Linguagem Natural) e Templates NEST
- **Batch SLA Request** para criação em massa
- **XAI (Explainable AI)** completo para explicações de decisões
- **Integração completa** com Prometheus, Loki, Tempo e OTEL Collector

### Stack Tecnológico

**Frontend:**
- Next.js 15 (App Router)
- Tailwind CSS
- Shadcn/UI
- Zustand (state management)
- TypeScript

**Backend:**
- FastAPI (Python 3.11)
- SQLite/PostgreSQL (contratos)
- Redis (cache)
- OpenTelemetry (instrumentação)
- Pydantic (validação)

**Observabilidade:**
- Prometheus (métricas)
- Loki (logs)
- Tempo (traces)
- OTEL Collector

---

## 🏗️ Diagrama Textual do Portal

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TriSLA Observability Portal v4.0                      │
│                         (Next.js 15 Frontend)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              TriSLA Observability API (FastAPI Backend)                  │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  Prometheus     │  │  Loki            │  │  Tempo           │       │
│  │  Client         │  │  Client          │  │  Client          │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  TriSLA API     │  │  Contract        │  │  XAI Engine      │       │
│  │  Gateway        │  │  Manager        │  │                  │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  PLN Processor  │  │  NEST Template  │  │  Batch SLA      │       │
│  │                  │  │  Engine         │  │  Processor       │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  Prometheus   │         │  Loki         │         │  Tempo        │
│  (monitoring) │         │  (monitoring) │         │  (monitoring) │
└───────────────┘         └───────────────┘         └───────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │    OTEL Collector             │
                    │    (trisla namespace)         │
                    └───────────────┬───────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  SEM-CSMF     │         │  ML-NSMF      │         │  Decision     │
│  (8080)       │         │  (8081)       │         │  Engine       │
│               │         │               │         │  (8082)       │
└───────────────┘         └───────────────┘         └───────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  BC-NSSMF     │         │  SLA-Agent    │         │  NASP         │
│  (8083)       │         │  Layer        │         │  Adapter      │
│               │         │  (8084)       │         │  (8085)       │
└───────────────┘         └───────────────┘         └───────────────┘
```

---

## 🔄 Dataflow Completo

### Dataflow: UI ↔ API ↔ Observabilidade ↔ TriSLA Modules

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                            │
│                                                                         │
│  User Action → Component → Zustand Store → API Client                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI Observability API)                  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Request Handler                                             │      │
│  │  - Validação (Pydantic)                                      │      │
│  │  - Autenticação (JWT)                                        │      │
│  │  - Rate Limiting                                             │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│        ┌──────────────────┼──────────────────┐                          │
│        │                  │                  │                          │
│        ▼                  ▼                  ▼                          │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐                      │
│  │Prometheus│      │  Loki    │      │  Tempo   │                      │
│  │ Service  │      │ Service  │      │ Service  │                      │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘                      │
│       │                 │                  │                            │
│       │ HTTP API        │ HTTP API        │ HTTP API                   │
│       │ /api/v1/query   │ /loki/api/v1/   │ /api/traces                │
│       │                 │                 │                            │
│       ▼                 ▼                 ▼                            │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  Prometheus (monitoring namespace)                    │             │
│  │  - Métricas dos módulos TriSLA                       │             │
│  │  - ServiceMonitors configurados                      │             │
│  └──────────────────────────────────────────────────────┘             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  Loki (monitoring namespace)                         │             │
│  │  - Logs agregados dos módulos                        │             │
│  └──────────────────────────────────────────────────────┘             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  Tempo (monitoring namespace)                        │             │
│  │  - Traces distribuídos via OTEL                      │             │
│  └──────────────────────────────────────────────────────┘             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  TriSLA API Gateway                                   │             │
│  │  - SEM-CSMF (8080)                                    │             │
│  │  - ML-NSMF (8081)                                     │             │
│  │  - Decision Engine (8082)                             │             │
│  │  - BC-NSSMF (8083)                                    │             │
│  │  - SLA-Agent Layer (8084)                             │             │
│  └──────────────────────────────────────────────────────┘             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  Contract Manager                                      │             │
│  │  - SQLite/PostgreSQL (contratos)                      │             │
│  │  - Redis (cache)                                      │             │
│  └──────────────────────────────────────────────────────┘             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  XAI Engine                                           │             │
│  │  - Consulta ML-NSMF para explicações                │             │
│  │  - Processa SHAP/LIME values                         │             │
│  └──────────────────────────────────────────────────────┘             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  PLN Processor + NEST Template Engine                 │             │
│  │  - Processa linguagem natural                         │             │
│  │  - Gera NESTs via SEM-CSMF                           │             │
│  └──────────────────────────────────────────────────────┘             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │  Batch SLA Processor                                  │             │
│  │  - Processa múltiplos SLAs em lote                    │             │
│  │  - Workers assíncronos                                │             │
│  └──────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ OTLP / HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    OTEL Collector (trisla namespace)                    │
│  - Recebe traces dos módulos TriSLA                                     │
│  - Encaminha para Tempo                                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  SEM-CSMF     │         │  ML-NSMF      │         │  Decision     │
│  - /metrics   │         │  - /metrics   │         │  Engine       │
│  - OTLP       │         │  - OTLP       │         │  - /metrics   │
│  - Traces     │         │  - Traces     │         │  - OTLP       │
└───────────────┘         └───────────────┘         └───────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐
│  BC-NSSMF     │         │  SLA-Agent    │
│  - /metrics   │         │  Layer        │
│  - OTLP       │         │  - /metrics   │
│  - Traces     │         │  - OTLP       │
└───────────────┘         └───────────────┘
```

### Fluxo de Dados por Tipo

**1. Métricas (Prometheus):**
```
TriSLA Modules → /metrics endpoint → Prometheus (ServiceMonitor) 
→ Observability API → Frontend
```

**2. Traces (OTEL → Tempo):**
```
TriSLA Modules → OTLP → OTEL Collector → Tempo 
→ Observability API → Frontend
```

**3. Logs (Loki):**
```
TriSLA Modules → stdout/stderr → Loki (via Promtail) 
→ Observability API → Frontend
```

**4. Contratos (Database):**
```
Frontend → Observability API → Contract Manager → PostgreSQL/SQLite 
→ Observability API → Frontend
```

**5. XAI (ML-NSMF):**
```
Frontend → Observability API → XAI Engine → ML-NSMF API 
→ Observability API → Frontend
```

---

## 📱 Mapeamento das Telas

### 1. Overview (`/`)
- **Descrição:** Dashboard global do TriSLA
- **Componentes:**
  - Cards de saúde por módulo (SEM, ML, DE, BC, SLA, NASP, UI)
  - Gráficos de SLOs principais
  - Alertas recentes
  - Métricas agregadas (latência, throughput, erro)
- **Dados:**
  - `GET /api/v1/health/global`
  - `GET /api/v1/slos/summary`

### 2. Modules (`/modules`)
- **Descrição:** Visão detalhada por módulo
- **Sub-telas:**
  - `/modules/sem-csmf`
  - `/modules/ml-nsmf`
  - `/modules/decision-engine`
  - `/modules/bc-nssmf`
  - `/modules/sla-agent-layer`
  - `/modules/nasp-adapter`
  - `/modules/ui-dashboard`
- **Componentes:**
  - Status de pods (Kubernetes)
  - Métricas principais do módulo
  - Tabela de erros recentes
  - Gráficos de performance
- **Dados:**
  - `GET /api/v1/modules`
  - `GET /api/v1/modules/{module}/metrics`
  - `GET /api/v1/modules/{module}/status`

### 3. Details (`/details`)
- **Descrição:** Detalhes de um recurso específico
- **Parâmetros:** `?type=intent|contract|trace&id={id}`
- **Componentes:**
  - Informações completas do recurso
  - Timeline de eventos
  - Métricas relacionadas
- **Dados:**
  - `GET /api/v1/intents/{id}`
  - `GET /api/v1/contracts/{id}`
  - `GET /api/v1/traces/{id}`

### 4. Intents (`/intents`)
- **Descrição:** Lista e detalhes de intents
- **Componentes:**
  - Tabela de intents recentes
  - Filtros (status, tipo, tenant)
  - Timeline de uma intent selecionada
- **Dados:**
  - `GET /api/v1/intents`
  - `GET /api/v1/intents/{id}/trace`

### 5. Traces Viewer (`/traces`)
- **Descrição:** Visualizador de traces distribuídos
- **Componentes:**
  - Árvore de spans
  - Timeline de execução
  - Filtros (serviço, operação, status)
  - Detalhes de cada span
- **Dados:**
  - `GET /api/v1/traces`
  - `GET /api/v1/traces/{trace_id}`

### 6. SLOs (`/slos`)
- **Descrição:** Visualização de SLOs e SLA compliance
- **Componentes:**
  - Tabela de SLOs por módulo
  - Gráficos de latência (P95, P99)
  - Taxa de erro
  - Disponibilidade
  - Violações de SLO
- **Dados:**
  - `GET /api/v1/slos`
  - `GET /api/v1/slos/{module}`

### 7. Logs (`/logs`)
- **Descrição:** Visualização de logs (Loki)
- **Componentes:**
  - Visualizador de logs
  - Filtros (módulo, nível, tempo)
  - Busca por texto
- **Dados:**
  - `GET /api/v1/logs`
  - `GET /api/v1/logs/query`

### 8. Contract List (`/contracts`)
- **Descrição:** Lista de contratos SLA
- **Componentes:**
  - Tabela de contratos
  - Filtros (status, tenant, tipo)
  - Ações (visualizar, comparar, renegociar)
- **Dados:**
  - `GET /api/v1/contracts`

### 9. Contract Details (`/contracts/{id}`)
- **Descrição:** Detalhes completos de um contrato
- **Componentes:**
  - Informações do contrato
  - Estado atual
  - Histórico de violações
  - Histórico de renegociações
  - Penalidades aplicadas
  - Timeline de eventos
- **Dados:**
  - `GET /api/v1/contracts/{id}`
  - `GET /api/v1/contracts/{id}/violations`
  - `GET /api/v1/contracts/{id}/renegotiations`
  - `GET /api/v1/contracts/{id}/penalties`

### 10. Contract Comparison (`/contracts/compare`)
- **Descrição:** Comparação de versões de contratos
- **Componentes:**
  - Seleção de contratos/versões
  - Diff visual
  - Tabela comparativa
- **Dados:**
  - `GET /api/v1/contracts/{id}/versions`
  - `GET /api/v1/contracts/compare`

### 11. Contract Analytics (`/contracts/analytics`)
- **Descrição:** Analytics de contratos
- **Componentes:**
  - Gráficos de distribuição
  - Taxa de violação
  - Tendências
  - Análise por tenant
- **Dados:**
  - `GET /api/v1/contracts/analytics`

### 12. SLA Creation - PLN (`/slas/create/pln`)
- **Descrição:** Criação de SLA via Processamento de Linguagem Natural
- **Componentes:**
  - Editor de texto (intent em linguagem natural)
  - Preview do NEST gerado
  - Validação semântica
  - Botão de criação
- **Dados:**
  - `POST /api/v1/slas/create/pln`
  - `POST /api/v1/slas/validate`

### 13. SLA Creation - Template (`/slas/create/template`)
- **Descrição:** Criação de SLA via Template NEST
- **Componentes:**
  - Seleção de template
  - Formulário de preenchimento
  - Preview do NEST
  - Botão de criação
- **Dados:**
  - `GET /api/v1/slas/templates`
  - `POST /api/v1/slas/create/template`

### 14. SLA Batch Creation (`/slas/create/batch`)
- **Descrição:** Criação em lote de SLAs
- **Componentes:**
  - Upload de arquivo (CSV/JSON)
  - Preview dos SLAs
  - Progress bar
  - Resultados (sucesso/erro)
- **Dados:**
  - `POST /api/v1/slas/create/batch`
  - `GET /api/v1/slas/batch/{batch_id}/status`

### 15. XAI Viewer (`/xai`)
- **Descrição:** Visualizador de explicações XAI
- **Componentes:**
  - Seleção de predição/decisão
  - Explicação textual
  - Feature importance (gráfico)
  - SHAP values (se disponível)
- **Dados:**
  - `GET /api/v1/xai/explanations`
  - `GET /api/v1/xai/explanations/{id}`

---

## 🔌 Mapeamento dos Endpoints da API

### Observabilidade

#### Health & Status
- `GET /api/v1/health/global` - Saúde global do TriSLA
- `GET /api/v1/health/modules` - Saúde por módulo
- `GET /api/v1/modules` - Lista de módulos
- `GET /api/v1/modules/{module}` - Detalhes de um módulo
- `GET /api/v1/modules/{module}/metrics` - Métricas de um módulo
- `GET /api/v1/modules/{module}/status` - Status (pods, deployments)

#### Prometheus
- `GET /api/v1/prometheus/query` - Query Prometheus
- `GET /api/v1/prometheus/query_range` - Query range Prometheus
- `GET /api/v1/prometheus/targets` - Targets do Prometheus

#### Loki
- `GET /api/v1/logs` - Logs (query Loki)
- `GET /api/v1/logs/query` - Query customizada Loki
- `GET /api/v1/logs/labels` - Labels disponíveis

#### Tempo
- `GET /api/v1/traces` - Lista de traces
- `GET /api/v1/traces/{trace_id}` - Detalhes de um trace
- `GET /api/v1/traces/search` - Busca de traces

#### SLOs
- `GET /api/v1/slos` - Lista de SLOs
- `GET /api/v1/slos/summary` - Resumo de SLOs
- `GET /api/v1/slos/{module}` - SLOs de um módulo
- `GET /api/v1/slos/{module}/violations` - Violações de SLO

### TriSLA API Gateway

#### SEM-CSMF
- `GET /api/v1/trisla/sem-csmf/intents` - Lista de intents
- `GET /api/v1/trisla/sem-csmf/intents/{id}` - Detalhes de intent
- `POST /api/v1/trisla/sem-csmf/intents` - Criar intent
- `GET /api/v1/trisla/sem-csmf/nests` - Lista de NESTs

#### ML-NSMF
- `GET /api/v1/trisla/ml-nsmf/predictions` - Lista de predições
- `GET /api/v1/trisla/ml-nsmf/predictions/{id}` - Detalhes de predição
- `POST /api/v1/trisla/ml-nsmf/predict` - Fazer predição

#### Decision Engine
- `GET /api/v1/trisla/decision-engine/decisions` - Lista de decisões
- `GET /api/v1/trisla/decision-engine/decisions/{id}` - Detalhes de decisão

#### BC-NSSMF
- `GET /api/v1/trisla/bc-nssmf/contracts` - Lista de contratos blockchain
- `GET /api/v1/trisla/bc-nssmf/contracts/{id}` - Detalhes de contrato

#### SLA-Agent Layer
- `GET /api/v1/trisla/sla-agent-layer/actions` - Lista de ações
- `GET /api/v1/trisla/sla-agent-layer/actions/{id}` - Detalhes de ação

### SLA Management

#### PLN
- `POST /api/v1/slas/create/pln` - Criar SLA via PLN
- `POST /api/v1/slas/validate` - Validar intent PLN

#### Templates
- `GET /api/v1/slas/templates` - Lista de templates NEST
- `GET /api/v1/slas/templates/{id}` - Detalhes de template
- `POST /api/v1/slas/create/template` - Criar SLA via template

#### Batch
- `POST /api/v1/slas/create/batch` - Criar SLAs em lote
- `GET /api/v1/slas/batch/{batch_id}` - Status de batch
- `GET /api/v1/slas/batch/{batch_id}/results` - Resultados do batch

### XAI

- `GET /api/v1/xai/explanations` - Lista de explicações
- `GET /api/v1/xai/explanations/{id}` - Detalhes de explicação
- `POST /api/v1/xai/explain` - Gerar explicação

### Contract Lifecycle

- `GET /api/v1/contracts` - Lista de contratos
- `GET /api/v1/contracts/{id}` - Detalhes de contrato
- `POST /api/v1/contracts` - Criar contrato
- `PUT /api/v1/contracts/{id}` - Atualizar contrato
- `GET /api/v1/contracts/{id}/violations` - Violações
- `POST /api/v1/contracts/{id}/renegotiate` - Renegociar
- `GET /api/v1/contracts/{id}/renegotiations` - Histórico de renegociações
- `GET /api/v1/contracts/{id}/penalties` - Penalidades
- `GET /api/v1/contracts/{id}/versions` - Versões do contrato
- `GET /api/v1/contracts/compare` - Comparar contratos
- `GET /api/v1/contracts/analytics` - Analytics

---

## 📊 Tabelas e Schemas dos Contratos

### Schema: Contract

```typescript
interface Contract {
  id: string;                    // UUID
  tenant_id: string;             // ID do tenant
  intent_id: string;             // ID do intent original
  nest_id: string;               // ID do NEST gerado
  decision_id: string;           // ID da decisão do Decision Engine
  blockchain_tx_hash?: string;   // Hash da transação blockchain (BC-NSSMF)
  
  // Estado
  status: ContractStatus;       // CREATED | ACTIVE | VIOLATED | RENEGOTIATED | TERMINATED
  version: number;               // Versão do contrato (incrementa em renegociações)
  
  // SLA Requirements
  sla_requirements: SLARequirements;
  
  // Domínios
  domains: string[];             // ["RAN", "Transport", "Core"]
  
  // Timestamps
  created_at: string;            // ISO 8601
  activated_at?: string;
  terminated_at?: string;
  
  // Metadata
  metadata: {
    service_type: string;       // "eMBB" | "URLLC" | "mMTC"
    priority: string;           // "low" | "medium" | "high"
    [key: string]: any;
  };
}

enum ContractStatus {
  CREATED = "CREATED",
  ACTIVE = "ACTIVE",
  VIOLATED = "VIOLATED",
  RENEGOTIATED = "RENEGOTIATED",
  TERMINATED = "TERMINATED"
}

interface SLARequirements {
  latency?: {
    max: string;                 // "10ms"
    p95?: string;
    p99?: string;
  };
  throughput?: {
    min: string;                 // "100Mbps"
    guaranteed?: string;
  };
  reliability?: number;          // 0.99999
  availability?: number;        // 0.999
  jitter?: string;              // "2ms"
  packet_loss?: number;         // 0.001
}
```

### Schema: Violation

```typescript
interface Violation {
  id: string;                    // UUID
  contract_id: string;
  violation_type: ViolationType; // LATENCY | THROUGHPUT | RELIABILITY | AVAILABILITY
  metric_name: string;           // "latency", "throughput", etc.
  expected_value: any;           // Valor esperado
  actual_value: any;            // Valor real medido
  severity: Severity;            // LOW | MEDIUM | HIGH | CRITICAL
  detected_at: string;          // ISO 8601
  resolved_at?: string;
  status: ViolationStatus;      // DETECTED | ACKNOWLEDGED | RESOLVED | IGNORED
}

enum ViolationType {
  LATENCY = "LATENCY",
  THROUGHPUT = "THROUGHPUT",
  RELIABILITY = "RELIABILITY",
  AVAILABILITY = "AVAILABILITY",
  JITTER = "JITTER",
  PACKET_LOSS = "PACKET_LOSS"
}

enum Severity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL"
}

enum ViolationStatus {
  DETECTED = "DETECTED",
  ACKNOWLEDGED = "ACKNOWLEDGED",
  RESOLVED = "RESOLVED",
  IGNORED = "IGNORED"
}
```

### Schema: Renegotiation

```typescript
interface Renegotiation {
  id: string;                    // UUID
  contract_id: string;
  previous_version: number;
  new_version: number;
  reason: RenegotiationReason;   // VIOLATION | TENANT_REQUEST | OPTIMIZATION
  changes: ContractDiff;        // Diff entre versões
  status: RenegotiationStatus;  // PENDING | ACCEPTED | REJECTED
  requested_at: string;         // ISO 8601
  completed_at?: string;
  requested_by: string;         // "tenant" | "system"
}

enum RenegotiationReason {
  VIOLATION = "VIOLATION",
  TENANT_REQUEST = "TENANT_REQUEST",
  OPTIMIZATION = "OPTIMIZATION"
}

enum RenegotiationStatus {
  PENDING = "PENDING",
  ACCEPTED = "ACCEPTED",
  REJECTED = "REJECTED"
}

interface ContractDiff {
  sla_requirements: {
    added: Partial<SLARequirements>;
    removed: Partial<SLARequirements>;
    modified: {
      [key: string]: {
        old: any;
        new: any;
      };
    };
  };
}
```

### Schema: Penalty

```typescript
interface Penalty {
  id: string;                    // UUID
  contract_id: string;
  violation_id: string;
  penalty_type: PenaltyType;     // REFUND | CREDIT | TERMINATION
  amount?: number;              // Valor monetário (se aplicável)
  percentage?: number;          // Percentual (se aplicável)
  applied_at: string;           // ISO 8601
  status: PenaltyStatus;        // PENDING | APPLIED | WAIVED
}

enum PenaltyType {
  REFUND = "REFUND",
  CREDIT = "CREDIT",
  TERMINATION = "TERMINATION"
}

enum PenaltyStatus {
  PENDING = "PENDING",
  APPLIED = "APPLIED",
  WAIVED = "WAIVED"
}
```

### Tabelas SQL (PostgreSQL)

```sql
-- Contratos
CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    intent_id VARCHAR(255) NOT NULL,
    nest_id VARCHAR(255) NOT NULL,
    decision_id VARCHAR(255) NOT NULL,
    blockchain_tx_hash VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    sla_requirements JSONB NOT NULL,
    domains TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activated_at TIMESTAMP WITH TIME ZONE,
    terminated_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- Violações
CREATE TABLE violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    violation_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    expected_value JSONB,
    actual_value JSONB,
    severity VARCHAR(50) NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    INDEX idx_contract_id (contract_id),
    INDEX idx_detected_at (detected_at),
    INDEX idx_status (status)
);

-- Renegociações
CREATE TABLE renegotiations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    previous_version INTEGER NOT NULL,
    new_version INTEGER NOT NULL,
    reason VARCHAR(50) NOT NULL,
    changes JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    requested_by VARCHAR(50) NOT NULL,
    INDEX idx_contract_id (contract_id),
    INDEX idx_status (status)
);

-- Penalidades
CREATE TABLE penalties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    violation_id UUID NOT NULL REFERENCES violations(id) ON DELETE CASCADE,
    penalty_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2),
    percentage DECIMAL(5, 2),
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) NOT NULL,
    INDEX idx_contract_id (contract_id),
    INDEX idx_violation_id (violation_id)
);
```

---

## 🧠 Arquitetura XAI

### Fluxo de Explicabilidade

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (XAI Viewer)                          │
│  Usuário solicita explicação de uma predição/decisão                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ GET /api/v1/xai/explanations/{id}
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (XAI Engine)                                 │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  1. Recebe request de explicação                              │      │
│  │  2. Identifica tipo (predição ML ou decisão DE)              │      │
│  │  3. Busca dados originais (métricas, NEST, etc.)             │      │
│  └───────────────────────┬────────────────────────────────────┘      │
│                          │                                              │
│        ┌──────────────────┴──────────────────┐                          │
│        │                                     │                          │
│        ▼                                     ▼                          │
│  ┌──────────────┐                  ┌──────────────┐                   │
│  │  ML-NSMF     │                  │  Decision     │                   │
│  │  XAI         │                  │  Engine       │                   │
│  │              │                  │  XAI          │                   │
│  └──────┬───────┘                  └──────┬───────┘                   │
│         │                                   │                            │
│         │ GET /api/v1/predictions/{id}      │ GET /api/v1/decisions/{id} │
│         │                                   │                            │
│         ▼                                   ▼                            │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  ML-NSMF API                                         │              │
│  │  - Retorna predição com SHAP values                  │              │
│  │  - Feature importance                               │              │
│  │  - Reasoning textual                                │              │
│  └──────────────────────────────────────────────────────┘              │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  Processamento XAI                                   │              │
│  │  - Agrega explicações de múltiplas fontes            │              │
│  │  - Formata para apresentação                         │              │
│  │  - Gera visualizações (feature importance charts)     │              │
│  └──────────────────────────────────────────────────────┘              │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  Resposta Formatada                                   │              │
│  │  {                                                     │              │
│  │    "explanation_id": "...",                           │              │
│  │    "method": "SHAP",                                  │              │
│  │    "features_importance": {...},                      │              │
│  │    "reasoning": "...",                                │              │
│  │    "visualizations": {...}                            │              │
│  │  }                                                     │              │
│  └──────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ JSON Response
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (XAI Viewer)                               │
│  - Exibe explicação textual                                            │
│  - Renderiza gráfico de feature importance                            │
│  - Mostra SHAP values (se disponível)                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tipos de Explicação

**1. Explicação de Predição ML (ML-NSMF):**
- **Método:** SHAP (SHapley Additive exPlanations) ou LIME
- **Dados:**
  - Feature importance (latency, throughput, reliability, etc.)
  - SHAP values por feature
  - Reasoning textual
- **Formato:**
```json
{
  "type": "ml_prediction",
  "prediction_id": "pred-001",
  "method": "SHAP",
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "features_importance": {
    "latency": 0.40,
    "throughput": 0.30,
    "reliability": 0.20,
    "jitter": 0.10
  },
  "shap_values": {
    "latency": 0.15,
    "throughput": 0.10,
    "reliability": 0.05,
    "jitter": 0.02
  },
  "reasoning": "Viabilidade 0.87 (ACCEPT). Feature mais importante: latency (40%). SLA viável com alta confiança."
}
```

**2. Explicação de Decisão (Decision Engine):**
- **Método:** Regras aplicadas + ML input
- **Dados:**
  - Regras que foram aplicadas
  - Input do ML-NSMF
  - Fatores de decisão
- **Formato:**
```json
{
  "type": "decision",
  "decision_id": "decision-001",
  "decision": "ACCEPT",
  "rules_applied": [
    {
      "rule_id": "rule-001",
      "rule_name": "High Priority Acceptance",
      "condition": "priority == 'high' AND viability_score > 0.7",
      "result": "ACCEPT"
    }
  ],
  "ml_input": {
    "viability_score": 0.87,
    "recommendation": "ACCEPT"
  },
  "reasoning": "Decisão ACCEPT baseada em regra 'High Priority Acceptance' e predição ML (viability_score: 0.87)."
}
```

---

## 💬 Arquitetura PLN + Templates NEST

### Fluxo PLN (Processamento de Linguagem Natural)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (SLA Creation - PLN)                        │
│  Usuário digita intent em linguagem natural:                            │
│  "Preciso de um slice URLLC com latência máxima de 10ms"               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ POST /api/v1/slas/create/pln
                                    │ { "intent_text": "..." }
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (PLN Processor)                             │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  1. Recebe intent em linguagem natural                        │      │
│  │  2. Valida formato                                             │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  NLP Processing (spaCy ou similar)                           │      │
│  │  - Extrai tipo de slice (URLLC, eMBB, mMTC)                 │      │
│  │  - Extrai requisitos SLA (latency, throughput, etc.)          │      │
│  │  - Normaliza valores                                          │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Validação Semântica (Ontologia OWL)                         │      │
│  │  - Valida contra ontologia TriSLA                            │      │
│  │  - Verifica consistência                                     │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Geração de NEST (via SEM-CSMF)                              │      │
│  │  - Chama SEM-CSMF API                                        │      │
│  │  - Recebe NEST gerado                                        │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Resposta Formatada                                           │      │
│  │  {                                                             │      │
│  │    "intent_id": "...",                                        │      │
│  │    "nest_id": "...",                                          │      │
│  │    "nest": {...},                                             │      │
│  │    "status": "generated"                                       │      │
│  │  }                                                             │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SEM-CSMF API                                        │
│  POST /api/v1/intents                                                   │
│  - Processa intent                                                      │
│  - Gera NEST                                                            │
│  - Retorna NEST completo                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Fluxo Templates NEST

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  FRONTEND (SLA Creation - Template)                     │
│  Usuário seleciona template e preenche formulário                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ GET /api/v1/slas/templates
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (NEST Template Engine)                        │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  1. Lista templates disponíveis                               │      │
│  │  2. Usuário seleciona template                                 │      │
│  │  3. Preenche formulário com valores                            │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Template Processing                                          │      │
│  │  - Carrega template NEST                                      │      │
│  │  - Substitui placeholders pelos valores do formulário        │      │
│  │  - Valida NEST gerado                                          │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Geração de NEST (via SEM-CSMF)                              │      │
│  │  - Envia NEST para SEM-CSMF                                   │      │
│  │  - Recebe NEST validado                                       │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Resposta Formatada                                           │      │
│  │  {                                                             │      │
│  │    "intent_id": "...",                                        │      │
│  │    "nest_id": "...",                                          │      │
│  │    "nest": {...},                                             │      │
│  │    "status": "generated"                                       │      │
│  │  }                                                             │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Templates NEST Disponíveis

**1. Template URLLC:**
```json
{
  "template_id": "urllc-basic",
  "name": "URLLC Basic",
  "description": "Template básico para slice URLLC",
  "service_type": "URLLC",
  "nest_template": {
    "slice_type": "URLLC",
    "sla_requirements": {
      "latency": {
        "max": "{{latency_max}}",
        "p99": "{{latency_p99}}"
      },
      "reliability": "{{reliability}}",
      "availability": "{{availability}}"
    },
    "domains": ["RAN", "Transport", "Core"]
  },
  "form_fields": [
    {
      "name": "latency_max",
      "label": "Latência Máxima",
      "type": "string",
      "default": "10ms",
      "required": true
    },
    {
      "name": "reliability",
      "label": "Confiabilidade",
      "type": "number",
      "default": 0.99999,
      "required": true
    }
  ]
}
```

**2. Template eMBB:**
```json
{
  "template_id": "embb-basic",
  "name": "eMBB Basic",
  "description": "Template básico para slice eMBB",
  "service_type": "eMBB",
  "nest_template": {
    "slice_type": "eMBB",
    "sla_requirements": {
      "throughput": {
        "min": "{{throughput_min}}",
        "guaranteed": "{{throughput_guaranteed}}"
      },
      "latency": {
        "max": "{{latency_max}}"
      }
    },
    "domains": ["RAN", "Transport", "Core"]
  }
}
```

**3. Template mMTC:**
```json
{
  "template_id": "mmtc-basic",
  "name": "mMTC Basic",
  "description": "Template básico para slice mMTC",
  "service_type": "mMTC",
  "nest_template": {
    "slice_type": "mMTC",
    "sla_requirements": {
      "throughput": {
        "min": "{{throughput_min}}"
      },
      "latency": {
        "max": "{{latency_max}}"
      },
      "packet_loss": "{{packet_loss}}"
    },
    "domains": ["RAN", "Transport", "Core"]
  }
}
```

---

## 📦 Arquitetura Batch SLA Creation

### Fluxo Batch

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  FRONTEND (SLA Batch Creation)                          │
│  Usuário faz upload de arquivo CSV/JSON com múltiplos SLAs              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ POST /api/v1/slas/create/batch
                                    │ multipart/form-data (file)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (Batch SLA Processor)                         │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  1. Recebe arquivo                                             │      │
│  │  2. Valida formato (CSV/JSON)                                  │      │
│  │  3. Parse do arquivo                                           │      │
│  │  4. Valida cada SLA individual                                 │      │
│  │  5. Cria batch job                                             │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Batch Job Queue (Redis/RabbitMQ)                             │      │
│  │  - Adiciona jobs à fila                                        │      │
│  │  - Retorna batch_id                                            │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Workers Assíncronos (Celery/Background Tasks)               │      │
│  │  - Processa cada SLA em paralelo                               │      │
│  │  - Chama PLN Processor ou Template Engine                     │      │
│  │  - Registra resultados (sucesso/erro)                         │      │
│  └───────────────────────┬──────────────────────────────────────┘      │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Status Tracking                                               │      │
│  │  - Armazena status de cada SLA                                │      │
│  │  - Progress: X/Y processados                                  │      │
│  │  - Resultados: sucesso/erro por SLA                          │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ GET /api/v1/slas/batch/{batch_id}/status
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Progress Tracking)                         │
│  - Exibe progress bar                                                   │
│  - Mostra resultados em tempo real                                      │
│  - Permite download de relatório                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Formato de Arquivo CSV

```csv
tenant_id,service_type,intent_text,latency_max,throughput_min,reliability
tenant-001,URLLC,Preciso de slice URLLC,10ms,100Mbps,0.99999
tenant-002,eMBB,Slice eMBB para streaming,50ms,1Gbps,0.99
tenant-003,mMTC,Slice mMTC para IoT,100ms,10Mbps,0.95
```

### Formato de Arquivo JSON

```json
[
  {
    "tenant_id": "tenant-001",
    "service_type": "URLLC",
    "intent_text": "Preciso de slice URLLC",
    "sla_requirements": {
      "latency": {"max": "10ms"},
      "throughput": {"min": "100Mbps"},
      "reliability": 0.99999
    }
  },
  {
    "tenant_id": "tenant-002",
    "service_type": "eMBB",
    "template_id": "embb-basic",
    "form_values": {
      "throughput_min": "1Gbps",
      "latency_max": "50ms"
    }
  }
]
```

### Schema: Batch Job

```typescript
interface BatchJob {
  batch_id: string;              // UUID
  tenant_id: string;
  total_slas: number;
  processed_slas: number;
  successful_slas: number;
  failed_slas: number;
  status: BatchStatus;           // PENDING | PROCESSING | COMPLETED | FAILED
  created_at: string;
  completed_at?: string;
  results: BatchResult[];
}

enum BatchStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED"
}

interface BatchResult {
  sla_index: number;             // Índice no arquivo original
  tenant_id: string;
  status: "success" | "error";
  intent_id?: string;
  nest_id?: string;
  error?: string;
}
```

---

## 🔗 Mapeamento com FASE 6

### Alinhamento com FASE_6_RELATORIO_TECNICO_FINAL.md

**1. Módulos Instrumentados:**
- ✅ SEM-CSMF (porta 8080) - `/api/v1/modules/sem-csmf`
- ✅ ML-NSMF (porta 8081) - `/api/v1/modules/ml-nsmf`
- ✅ Decision Engine (porta 8082) - `/api/v1/modules/decision-engine`
- ✅ BC-NSSMF (porta 8083) - `/api/v1/modules/bc-nssmf`
- ✅ SLA-Agent Layer (porta 8084) - `/api/v1/modules/sla-agent-layer`
- ✅ NASP Adapter (porta 8085) - `/api/v1/modules/nasp-adapter`
- ✅ UI Dashboard (porta 3000) - `/api/v1/modules/ui-dashboard`

**2. Stack de Observabilidade:**
- ✅ Prometheus (namespace `monitoring`) - `/api/v1/prometheus/*`
- ✅ OTEL Collector (namespace `trisla`) - Integrado via Tempo
- ✅ ServiceMonitors (6 configurados) - `/api/v1/prometheus/targets`
- ✅ Grafana (opcional) - Links de atalho

**3. Métricas Prometheus:**
- ✅ Endpoints `/metrics` - Consumidos via Prometheus API
- ✅ Métricas customizadas (`trisla_*`, `intent_*`, etc.) - Visualizadas no portal
- ✅ ServiceMonitors - Status exibido em `/modules`

**4. Traces OpenTelemetry:**
- ✅ OTLP_ENDPOINT configurado - Traces coletados via OTEL Collector
- ✅ Visualização de traces - `/traces` e `/intents/{id}/trace`
- ✅ Integração com Tempo - `/api/v1/traces/*`

**5. SLOs Definidos:**
- ✅ Latência P95/P99 - `/slos` e `/modules/{module}`
- ✅ Disponibilidade - `/slos` e `/modules/{module}`
- ✅ Taxa de erro - `/slos` e `/modules/{module}`
- ✅ Violações de SLO - `/slos/{module}/violations`

**6. Validações Realizadas:**
- ✅ Endpoints `/metrics` funcionando - Status em `/modules/{module}/status`
- ✅ ServiceMonitors configurados - Lista em `/prometheus/targets`
- ✅ OTEL Collector deployado - Status em `/infrastructure`
- ✅ Tráfego gerado - Visualizado em `/intents` e `/traces`

---

## ✅ Conclusão

A arquitetura do **TriSLA Observability Portal v4.0** está completamente definida e alinhada com:

- ✅ Relatório Técnico FASE 6
- ✅ Arquitetura TriSLA v3.7.10
- ✅ Especificações NASP
- ✅ Requisitos de observabilidade completa

**Próximos Passos:**
- FASE 2: Implementação do Frontend (Next.js 15)
- FASE 3: Implementação do Backend (FastAPI)

---

**Status:** ✅ **FASE 1 CONCLUÍDA - ARQUITETURA COMPLETA GERADA**







