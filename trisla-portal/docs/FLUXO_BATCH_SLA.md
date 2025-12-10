# Fluxo Batch SLA Creation - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura Batch](#arquitetura-batch)
3. [Processamento de Arquivo](#processamento-de-arquivo)
4. [Workers Assíncronos](#workers-assíncronos)
5. [Tracking de Progresso](#tracking-de-progresso)

---

## 🎯 Visão Geral

O módulo Batch SLA Creation permite criar múltiplos SLAs simultaneamente através de upload de arquivo (CSV ou JSON), ideal para:

- **Criação em massa**: > 100 SLAs de uma vez
- **Migração de dados**: Importação de SLAs existentes
- **Provisionamento inicial**: Setup inicial de múltiplos tenants

### Limites

- **Máximo de SLAs por batch**: 1000
- **Formatos suportados**: CSV, JSON
- **Tamanho máximo de arquivo**: 10MB

---

## 🏗️ Arquitetura Batch

```
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (SLA Batch Creation)                  │
│  Usuário faz upload de arquivo CSV/JSON                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ POST /api/v1/slas/create/batch
                            │ multipart/form-data
                            │ file: batch.csv
                            │ tenant_id: tenant-001
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (Batch SLA Processor)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Recebe arquivo                                     │  │
│  │  2. Valida formato (CSV/JSON)                          │  │
│  │  3. Parse do arquivo                                   │  │
│  │  4. Valida cada SLA individual                        │  │
│  │  5. Cria batch job                                     │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Batch Job Queue (Redis/RabbitMQ)                     │  │
│  │  - Adiciona jobs à fila                                │  │
│  │  - Retorna batch_id                                    │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Workers Assíncronos (Celery/Background Tasks)        │  │
│  │  - Processa cada SLA em paralelo                       │  │
│  │  - Chama PLN Processor ou Template Engine             │  │
│  │  - Registra resultados (sucesso/erro)                │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Status Tracking                                       │  │
│  │  - Armazena status de cada SLA                        │  │
│  │  - Progress: X/Y processados                          │  │
│  │  - Resultados: sucesso/erro por SLA                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ GET /api/v1/slas/batch/{batch_id}/status
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Progress Tracking)                   │
│  - Exibe progress bar                                       │
│  - Mostra resultados em tempo real                          │
│  - Permite download de relatório                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📄 Processamento de Arquivo

### Formato CSV

```csv
tenant_id,intent_text,service_type
tenant-001,Slice URLLC com latência 10ms,URLLC
tenant-002,Slice eMBB para streaming,eMBB
tenant-003,Slice mMTC para IoT,mMTC
```

### Formato JSON

```json
[
  {
    "tenant_id": "tenant-001",
    "intent_text": "Slice URLLC com latência 10ms",
    "service_type": "URLLC"
  },
  {
    "tenant_id": "tenant-002",
    "intent_text": "Slice eMBB para streaming",
    "service_type": "eMBB"
  }
]
```

### Validação

1. **Validação de Formato**
   - CSV: Verifica separadores, headers
   - JSON: Valida estrutura JSON

2. **Validação de Dados**
   - Campos obrigatórios presentes
   - Valores dentro de limites
   - Tenant ID válido

3. **Validação de Limites**
   - Máximo 1000 SLAs por batch
   - Arquivo < 10MB

---

## ⚙️ Workers Assíncronos

### Processamento Paralelo

- **Workers**: 5 workers simultâneos (configurável)
- **Timeout**: 30 segundos por SLA
- **Retry**: 3 tentativas em caso de falha

### Fluxo de Processamento

```
Para cada SLA no arquivo:
  1. Valida SLA individual
  2. Chama PLN Processor ou Template Engine
  3. Registra resultado:
     - Sucesso: intent_id, nest_id
     - Erro: mensagem de erro
  4. Atualiza progresso do batch
```

### Exemplo de Resultado

```json
{
  "batch_id": "batch-001",
  "status": "COMPLETED",
  "total_slas": 150,
  "processed_slas": 150,
  "successful_slas": 145,
  "failed_slas": 5,
  "results": [
    {
      "sla_index": 0,
      "status": "success",
      "intent_id": "intent-001",
      "nest_id": "nest-001"
    },
    {
      "sla_index": 1,
      "status": "error",
      "error": "Invalid intent format"
    }
  ]
}
```

---

## 📊 Tracking de Progresso

### Endpoints

#### `GET /api/v1/slas/batch/{batch_id}`

Retorna status atual do batch.

**Response:**
```json
{
  "batch_id": "batch-001",
  "status": "PROCESSING",
  "total_slas": 150,
  "processed_slas": 75,
  "successful_slas": 72,
  "failed_slas": 3,
  "progress": 50.0
}
```

#### `GET /api/v1/slas/batch/{batch_id}/results`

Retorna resultados completos do batch.

**Response:**
```json
{
  "results": [
    {
      "sla_index": 0,
      "tenant_id": "tenant-001",
      "status": "success",
      "intent_id": "intent-001",
      "nest_id": "nest-001"
    }
  ]
}
```

### Frontend - Progress Bar

```tsx
<div className="w-full bg-gray-200 rounded-full h-2.5">
  <div 
    className="bg-primary h-2.5 rounded-full" 
    style={{ width: `${progress}%` }}
  />
</div>
<div className="text-sm text-muted-foreground">
  {processed_slas} / {total_slas} processados
</div>
```

---

## ✅ Conclusão

O fluxo Batch SLA Creation do TriSLA Observability Portal v4.0 fornece:

- **Processamento em massa**: > 100 SLAs simultaneamente
- **Formato flexível**: CSV ou JSON
- **Tracking em tempo real**: Progresso e resultados
- **Processamento assíncrono**: Não bloqueia interface
- **Relatórios**: Download de resultados

---

**Status:** ✅ **FLUXO BATCH SLA DOCUMENTADO**







