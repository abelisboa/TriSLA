# Arquitetura — Portal

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `trisla-portal/docs/ARCHITECTURE_v4.0.md`, `trisla-portal/docs/API_ARCHITECTURE.md`

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitetura de Componentes](#arquitetura-de-componentes)
4. [Dataflow](#dataflow)
5. [Integrações](#integrações)

---

## Visão Geral

O **TriSLA Observability Portal v4.0** é uma interface web completa de observabilidade para o TriSLA, fornecendo visualização unificada de métricas, traces e logs, gerenciamento de contratos SLA, criação de SLAs via PLN e Templates NEST, batch SLA request e XAI completo.

### Características Principais

- **Visualização unificada** de métricas, traces e logs
- **Gerenciamento de contratos SLA** (criação, estado, violações, renegociações)
- **Criação de SLAs** via PLN (Processamento de Linguagem Natural) e Templates NEST
- **Batch SLA Request** para criação em massa
- **XAI (Explainable AI)** completo para explicações de decisões
- **Integração completa** com Prometheus, Loki, Tempo e OTEL Collector

---

## Stack Tecnológico

### Frontend

- **Next.js 15** (App Router)
- **Tailwind CSS**
- **Shadcn/UI**
- **Zustand** (state management)
- **TypeScript**

### Backend

- **FastAPI** (Python 3.11)
- **SQLite/PostgreSQL** (contratos)
- **Redis** (cache)
- **OpenTelemetry** (instrumentação)
- **Pydantic** (validação)

### Observabilidade

- **Prometheus** (métricas)
- **Loki** (logs)
- **Tempo** (traces)
- **OTEL Collector**

---

## Arquitetura de Componentes

### Frontend (Next.js)

```
┌─────────────────────────────────────┐
│      TriSLA Portal Frontend         │
│         (Next.js 15)                │
├─────────────────────────────────────┤
│  - Dashboards                       │
│  - Visualizações de métricas        │
│  - XAI Visualization                │
│  - SLA Management                   │
│  - PLN Interface                    │
│  - Batch SLA Creation               │
└─────────────────────────────────────┘
```

### Backend (FastAPI)

```
┌─────────────────────────────────────┐
│    TriSLA Observability API          │
│         (FastAPI)                    │
├─────────────────────────────────────┤
│  - Prometheus Client                │
│  - Loki Client                      │
│  - Tempo Client                     │
│  - TriSLA API Gateway               │
│  - Contract Manager                 │
│  - XAI Engine                       │
│  - PLN Processor                    │
│  - NEST Template Engine             │
│  - Batch SLA Processor              │
└─────────────────────────────────────┘
```

---

## Dataflow

### Fluxo de Métricas

```
Prometheus → OTEL Collector → Backend API → Frontend
```

### Fluxo de Logs

```
Loki → OTEL Collector → Backend API → Frontend
```

### Fluxo de Traces

```
Tempo → OTEL Collector → Backend API → Frontend
```

### Fluxo de SLAs

```
Frontend → Backend API → TriSLA API Gateway → SEM-NSMF → Decision Engine → BC-NSSMF
```

---

## Integrações

### NASP Adapter

- **Protocolo:** HTTP REST
- **Endpoint:** `http://nasp-adapter:8080/api/v1/metrics`
- **Uso:** Coleta de métricas para visualização

### TriSLA Modules

- **SEM-NSMF:** Criação de SLAs via PLN
- **ML-NSMF:** Predições e explicações XAI
- **BC-NSSMF:** Consulta de SLAs registrados on-chain
- **Decision Engine:** Decisões de aceitação/rejeição

### Observability Stack

- **Prometheus:** Métricas
- **Loki:** Logs
- **Tempo:** Traces
- **OTEL Collector:** Agregação

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `trisla-portal/docs/ARCHITECTURE_v4.0.md` — Arquitetura completa do portal
- `trisla-portal/docs/API_ARCHITECTURE.md` — Arquitetura da API

**Última atualização:** 2025-01-27  
**Versão:** S4.0

