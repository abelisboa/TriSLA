# Arquitetura da API - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Estrutura da API](#estrutura-da-api)
3. [Endpoints Detalhados](#endpoints-detalhados)
4. [Autenticação e Segurança](#autenticação-e-segurança)
5. [Rate Limiting](#rate-limiting)
6. [Versionamento](#versionamento)
7. [Error Handling](#error-handling)

---

## 🎯 Visão Geral

A API do TriSLA Observability Portal v4.0 é construída com **FastAPI** e fornece endpoints RESTful para:

- Observabilidade (métricas, logs, traces)
- Gerenciamento de contratos SLA
- Criação de SLAs (PLN, Template, Batch)
- Explicações XAI
- Integração com módulos TriSLA

### Base URL

- **Local**: `http://localhost:8000`
- **NASP**: `http://trisla-portal-backend.trisla.svc.cluster.local:8000`

### Formato de Resposta

Todas as respostas são em **JSON** com Content-Type `application/json`.

---

## 🏗️ Estrutura da API

### Organização por Módulos

```
/api/v1/
├── health/              # Saúde e status
├── modules/             # Gerenciamento de módulos
├── prometheus/          # Queries Prometheus
├── logs/                # Logs do Loki
├── traces/              # Traces do Tempo
├── intents/             # Gerenciamento de intents
├── contracts/           # Ciclo de vida de contratos
├── slas/                # Criação de SLAs
├── xai/                 # Explicações XAI
└── slos/                # Service Level Objectives
```

---

## 🔌 Endpoints Detalhados

### Health & Status

#### `GET /api/v1/health/global`

Retorna saúde global do TriSLA.

**Response 200:**
```json
{
  "status": "healthy",
  "modules": [
    {
      "name": "sem-csmf",
      "status": "UP",
      "latency": 5.2,
      "error_rate": 0.001,
      "throughput": 150.5
    }
  ],
  "timestamp": "2025-01-19T10:30:00Z"
}
```

#### `GET /api/v1/modules`

Lista todos os módulos.

**Response 200:**
```json
[
  {
    "name": "sem-csmf",
    "status": "UP",
    "latency": 5.2,
    "error_rate": 0.001,
    "pods": [
      {
        "name": "sem-csmf-pod-1",
        "status": "Running",
        "ready": true,
        "restarts": 0
      }
    ]
  }
]
```

### Observabilidade

#### `GET /api/v1/prometheus/query`

Executa query Prometheus.

**Query Parameters:**
- `query` (required): Query PromQL
- `time` (optional): Timestamp para instant query

**Response 200:**
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {"job": "sem-csmf"},
        "value": [1705658400, "1"]
      }
    ]
  }
}
```

#### `GET /api/v1/logs`

Retorna logs do Loki.

**Query Parameters:**
- `module` (optional): Filtrar por módulo
- `level` (optional): Filtrar por nível (INFO, ERROR, etc.)
- `start` (optional): Timestamp inicial
- `end` (optional): Timestamp final

**Response 200:**
```json
[
  {
    "stream": {"job": "sem-csmf"},
    "values": [
      ["1705658400000000000", "log message"]
    ]
  }
]
```

#### `GET /api/v1/traces`

Lista traces do Tempo.

**Query Parameters:**
- `service` (optional): Filtrar por serviço
- `operation` (optional): Filtrar por operação
- `status` (optional): Filtrar por status

**Response 200:**
```json
[
  {
    "trace_id": "abc123",
    "spans": [...],
    "duration": 150.5,
    "service_name": "sem-csmf"
  }
]
```

### Contracts

#### `POST /api/v1/contracts`

Cria um novo contrato.

**Request Body:**
```json
{
  "tenant_id": "tenant-001",
  "intent_id": "intent-001",
  "nest_id": "nest-001",
  "decision_id": "decision-001",
  "sla_requirements": {
    "latency": {"max": "10ms"},
    "throughput": {"min": "100Mbps"},
    "reliability": 0.99999
  },
  "domains": ["RAN", "Transport", "Core"],
  "metadata": {
    "service_type": "URLLC",
    "priority": "high"
  }
}
```

**Response 201:**
```json
{
  "id": "contract-001",
  "tenant_id": "tenant-001",
  "status": "CREATED",
  "version": 1,
  "created_at": "2025-01-19T10:00:00Z"
}
```

#### `GET /api/v1/contracts/{id}/violations`

Retorna violações de um contrato.

**Response 200:**
```json
[
  {
    "id": "violation-001",
    "contract_id": "contract-001",
    "violation_type": "LATENCY",
    "metric_name": "latency",
    "expected_value": "10ms",
    "actual_value": "15ms",
    "severity": "HIGH",
    "detected_at": "2025-01-19T11:00:00Z",
    "status": "DETECTED"
  }
]
```

### SLAs

#### `POST /api/v1/slas/create/pln`

Cria SLA via Processamento de Linguagem Natural.

**Request Body:**
```json
{
  "intent_text": "Preciso de um slice URLLC com latência máxima de 10ms",
  "tenant_id": "tenant-001"
}
```

**Response 200:**
```json
{
  "intent_id": "intent-001",
  "nest_id": "nest-001",
  "nest": {
    "slice_type": "URLLC",
    "sla_requirements": {
      "latency": {"max": "10ms"}
    }
  },
  "status": "generated"
}
```

#### `POST /api/v1/slas/create/batch`

Cria SLAs em lote via arquivo.

**Request:**
- `file` (multipart/form-data): Arquivo CSV ou JSON
- `tenant_id` (form-data): ID do tenant

**Response 200:**
```json
{
  "batch_id": "batch-001",
  "tenant_id": "tenant-001",
  "total_slas": 150,
  "processed_slas": 0,
  "successful_slas": 0,
  "failed_slas": 0,
  "status": "PENDING",
  "created_at": "2025-01-19T10:00:00Z"
}
```

### XAI

#### `POST /api/v1/xai/explain`

Gera explicação XAI.

**Request Body:**
```json
{
  "prediction_id": "pred-001"
}
```

**Response 200:**
```json
{
  "explanation_id": "expl-001",
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
    "throughput": 0.10
  },
  "reasoning": "Viabilidade 0.87 (ACCEPT). Feature mais importante: latency (40%)."
}
```

---

## 🔐 Autenticação e Segurança

### Autenticação (Futuro)

A API suportará autenticação via **JWT Bearer Token**:

```
Authorization: Bearer <token>
```

### CORS

CORS configurado para permitir:
- `http://localhost:3000` (desenvolvimento)
- `http://localhost:3001` (desenvolvimento alternativo)
- Domínios configuráveis via `CORS_ORIGINS`

---

## ⚡ Rate Limiting

Rate limiting implementado (futuro):
- **100 requests/minuto** por IP
- **1000 requests/hora** por IP
- Headers de resposta:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

---

## 📌 Versionamento

A API utiliza versionamento semântico:

- **Versão atual**: `v1`
- **Base URL**: `/api/v1/`
- **Futuras versões**: `/api/v2/`, `/api/v3/`, etc.

---

## ❌ Error Handling

### Formato de Erro

```json
{
  "error": "ResourceNotFound",
  "message": "Contract with id 'contract-123' not found",
  "status_code": 404
}
```

### Códigos HTTP

- **200 OK**: Sucesso
- **201 Created**: Recurso criado
- **400 Bad Request**: Requisição inválida
- **404 Not Found**: Recurso não encontrado
- **500 Internal Server Error**: Erro do servidor
- **503 Service Unavailable**: Serviço indisponível

---

## 📊 Documentação Interativa

A API fornece documentação interativa via **Swagger UI**:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## ✅ Conclusão

A arquitetura da API do TriSLA Observability Portal v4.0 fornece:

- **50+ endpoints** organizados por módulos
- **Documentação interativa** via Swagger
- **Error handling** consistente
- **Versionamento** semântico
- **Integração completa** com observabilidade e módulos TriSLA

---

**Status:** ✅ **ARQUITETURA DA API DOCUMENTADA**







