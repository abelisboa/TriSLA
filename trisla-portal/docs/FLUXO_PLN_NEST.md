# Fluxo PLN + NEST Template - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Fluxo PLN (Processamento de Linguagem Natural)](#fluxo-pln)
3. [Fluxo NEST Template](#fluxo-nest-template)
4. [Integração com SEM-CSMF](#integração-com-sem-csmf)
5. [Validação Semântica](#validação-semântica)

---

## 🎯 Visão Geral

O TriSLA Observability Portal v4.0 suporta criação de SLAs através de dois métodos:

1. **PLN (Processamento de Linguagem Natural)**: Usuário descreve o SLA em linguagem natural
2. **NEST Template**: Usuário preenche formulário baseado em template pré-definido

Ambos os métodos geram NESTs (Network Slice Templates) que são processados pelo SEM-CSMF.

---

## 💬 Fluxo PLN (Processamento de Linguagem Natural)

### Diagrama de Fluxo

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (SLA Creation - PLN)            │
│  Usuário digita:                                             │
│  "Preciso de um slice URLLC com latência máxima de 10ms"    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ POST /api/v1/slas/create/pln
                            │ {
                            │   "intent_text": "...",
                            │   "tenant_id": "tenant-001"
                            │ }
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (PLN Processor)                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Recebe intent em linguagem natural                 │  │
│  │  2. Valida formato                                     │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  NLP Processing (spaCy ou similar)                     │  │
│  │  - Extrai tipo de slice (URLLC, eMBB, mMTC)          │  │
│  │  - Extrai requisitos SLA:                            │  │
│  │    • Latência: "10ms"                                │  │
│  │    • Throughput: "100Mbps"                           │  │
│  │    • Confiabilidade: "99.999%"                       │  │
│  │  - Normaliza valores                                  │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Validação Semântica (Ontologia OWL)                 │  │
│  │  - Valida contra ontologia TriSLA                    │  │
│  │  - Verifica consistência                              │  │
│  │  - Aplica reasoning semântico                        │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Geração de NEST (via SEM-CSMF)                      │  │
│  │  - Chama SEM-CSMF API                                │  │
│  │  - POST /api/v1/intents                              │  │
│  │  - Recebe NEST gerado                                 │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Resposta Formatada                                   │  │
│  │  {                                                     │  │
│  │    "intent_id": "intent-001",                         │  │
│  │    "nest_id": "nest-001",                             │  │
│  │    "nest": {...},                                     │  │
│  │    "status": "generated"                              │  │
│  │  }                                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SEM-CSMF API                             │
│  POST /api/v1/intents                                        │
│  - Processa intent                                          │
│  - Gera NEST                                                 │
│  - Retorna NEST completo                                     │
└─────────────────────────────────────────────────────────────┘
```

### Exemplo de Processamento

**Input (Linguagem Natural):**
```
"Preciso de um slice URLLC com latência máxima de 10ms, 
throughput mínimo de 100Mbps e confiabilidade de 99.999%"
```

**Processamento NLP:**
- Tipo de slice: `URLLC`
- Latência: `10ms`
- Throughput: `100Mbps`
- Confiabilidade: `99.999%`

**NEST Gerado:**
```json
{
  "nest_id": "nest-001",
  "slice_type": "URLLC",
  "sla_requirements": {
    "latency": {"max": "10ms"},
    "throughput": {"min": "100Mbps"},
    "reliability": 0.99999
  },
  "domains": ["RAN", "Transport", "Core"]
}
```

---

## 📋 Fluxo NEST Template

### Diagrama de Fluxo

```
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (SLA Creation - Template)            │
│  1. Usuário seleciona template (ex: "URLLC Basic")         │
│  2. Preenche formulário com valores                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ GET /api/v1/slas/templates
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (NEST Template Engine)                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Lista templates disponíveis                      │  │
│  │  2. Usuário seleciona template                       │  │
│  │  3. Preenche formulário                              │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Template Processing                                  │  │
│  │  - Carrega template NEST                             │  │
│  │  - Substitui placeholders:                            │  │
│  │    {{latency_max}} → "10ms"                          │  │
│  │    {{reliability}} → 0.99999                          │  │
│  │  - Valida NEST gerado                                │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Geração de NEST (via SEM-CSMF)                      │  │
│  │  - Envia NEST para SEM-CSMF                          │  │
│  │  - Recebe NEST validado                              │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Resposta Formatada                                   │  │
│  │  {                                                     │  │
│  │    "intent_id": "intent-001",                         │  │
│  │    "nest_id": "nest-001",                             │  │
│  │    "nest": {...},                                     │  │
│  │    "status": "generated"                              │  │
│  │  }                                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Exemplo de Template

**Template URLLC Basic:**
```json
{
  "template_id": "urllc-basic",
  "name": "URLLC Basic",
  "nest_template": {
    "slice_type": "URLLC",
    "sla_requirements": {
      "latency": {"max": "{{latency_max}}"},
      "reliability": "{{reliability}}"
    }
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

**Formulário Preenchido:**
- `latency_max`: "10ms"
- `reliability`: 0.99999

**NEST Gerado:**
```json
{
  "slice_type": "URLLC",
  "sla_requirements": {
    "latency": {"max": "10ms"},
    "reliability": 0.99999
  }
}
```

---

## 🔗 Integração com SEM-CSMF

### Endpoint Utilizado

**POST** `/api/v1/intents` (SEM-CSMF)

**Request:**
```json
{
  "intent_text": "Preciso de slice URLLC...",
  "tenant_id": "tenant-001"
}
```

ou

```json
{
  "nest": {
    "slice_type": "URLLC",
    "sla_requirements": {...}
  },
  "tenant_id": "tenant-001"
}
```

**Response:**
```json
{
  "intent_id": "intent-001",
  "nest_id": "nest-001",
  "status": "accepted",
  "nest": {...}
}
```

---

## ✅ Validação Semântica

### Processo de Validação

1. **Validação de Sintaxe**
   - Formato JSON válido
   - Campos obrigatórios presentes

2. **Validação Semântica (Ontologia OWL)**
   - Valida contra classes da ontologia TriSLA
   - Verifica consistência de requisitos
   - Aplica reasoning semântico

3. **Validação de Valores**
   - Latência dentro de limites aceitáveis
   - Throughput compatível com tipo de slice
   - Confiabilidade válida

---

## ✅ Conclusão

Os fluxos PLN e NEST Template do TriSLA Observability Portal v4.0 fornecem:

- **Flexibilidade**: Criação via linguagem natural ou formulário
- **Validação**: Validação semântica completa
- **Integração**: Integração direta com SEM-CSMF
- **Usabilidade**: Interface intuitiva para operadores

---

**Status:** ✅ **FLUXOS PLN E NEST TEMPLATE DOCUMENTADOS**







