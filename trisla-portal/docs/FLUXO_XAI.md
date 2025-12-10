# Fluxo XAI (Explainable AI) - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura XAI](#arquitetura-xai)
3. [Fluxo de Explicação ML](#fluxo-de-explicação-ml)
4. [Fluxo de Explicação de Decisão](#fluxo-de-explicação-de-decisão)
5. [Métodos de Explicabilidade](#métodos-de-explicabilidade)
6. [Visualizações](#visualizações)

---

## 🎯 Visão Geral

O módulo XAI (Explainable AI) do TriSLA Observability Portal fornece explicações completas e interpretáveis para:

- **Predições ML**: Explicações de viabilidade de SLA do ML-NSMF
- **Decisões**: Explicações de decisões do Decision Engine

### Objetivos

1. **Transparência**: Explicar como e por que decisões foram tomadas
2. **Confiabilidade**: Aumentar confiança nas predições e decisões
3. **Auditoria**: Permitir auditoria de decisões automatizadas
4. **Compliance**: Atender requisitos de explicabilidade em IA

---

## 🏗️ Arquitetura XAI

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (XAI Viewer)                    │
│  Usuário solicita explicação                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ POST /api/v1/xai/explain
                            │ { "prediction_id": "pred-001" }
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (XAI Engine)                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Recebe request                                    │  │
│  │  2. Identifica tipo (predição ou decisão)            │  │
│  │  3. Busca dados originais                              │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                    │
│        ┌──────────────────┴──────────────────┐               │
│        │                                     │               │
│        ▼                                     ▼               │
│  ┌──────────────┐                  ┌──────────────┐          │
│  │  ML-NSMF     │                  │  Decision     │          │
│  │  API         │                  │  Engine API   │          │
│  └──────┬───────┘                  └──────┬───────┘          │
│         │                                   │                  │
│         │ GET /predictions/{id}             │ GET /decisions/{id}│
│         │                                   │                  │
│         ▼                                   ▼                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Processamento XAI                                    │   │
│  │  - Extrai explicação (SHAP/LIME)                     │   │
│  │  - Formata para apresentação                         │   │
│  │  - Gera visualizações                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Resposta Formatada                                   │   │
│  │  {                                                     │   │
│  │    "explanation_id": "...",                           │   │
│  │    "method": "SHAP",                                  │   │
│  │    "features_importance": {...},                      │   │
│  │    "reasoning": "...",                                │   │
│  │    "visualizations": {...}                            │   │
│  │  }                                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ JSON Response
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (XAI Viewer)                    │
│  - Exibe explicação textual                                 │
│  - Renderiza gráfico de feature importance                  │
│  - Mostra SHAP values                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Explicação ML

### Passo a Passo

1. **Usuário solicita explicação**
   - Frontend: `POST /api/v1/xai/explain` com `prediction_id`

2. **Backend identifica tipo**
   - XAI Engine identifica que é predição ML

3. **Busca predição do ML-NSMF**
   - `GET /api/v1/predictions/{prediction_id}` no ML-NSMF
   - Recebe predição com explicação XAI

4. **Processa explicação**
   - Extrai SHAP values ou LIME
   - Identifica features mais importantes
   - Gera reasoning textual

5. **Formata resposta**
   - Estrutura dados para apresentação
   - Prepara visualizações

6. **Retorna ao frontend**
   - Frontend exibe explicação completa

### Exemplo de Resposta

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
    "throughput": 0.10,
    "reliability": 0.05,
    "jitter": 0.02
  },
  "reasoning": "Viabilidade 0.87 (ACCEPT). Feature mais importante: latency (40%). SLA viável com alta confiança devido a latência dentro dos limites aceitáveis."
}
```

---

## 🔄 Fluxo de Explicação de Decisão

### Passo a Passo

1. **Usuário solicita explicação**
   - Frontend: `POST /api/v1/xai/explain` com `decision_id`

2. **Backend identifica tipo**
   - XAI Engine identifica que é decisão

3. **Busca decisão do Decision Engine**
   - `GET /api/v1/decisions/{decision_id}` no Decision Engine
   - Recebe decisão com regras aplicadas

4. **Processa explicação**
   - Identifica regras aplicadas
   - Extrai fatores de decisão
   - Gera reasoning textual

5. **Formata resposta**
   - Estrutura dados para apresentação

6. **Retorna ao frontend**
   - Frontend exibe explicação completa

### Exemplo de Resposta

```json
{
  "explanation_id": "expl-002",
  "type": "decision",
  "decision_id": "decision-001",
  "method": "rules",
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
  "reasoning": "Decisão ACCEPT baseada em regra 'High Priority Acceptance' (priority='high' e viability_score=0.87 > 0.7) e predição ML (viability_score: 0.87, recommendation: ACCEPT)."
}
```

---

## 🧠 Métodos de Explicabilidade

### 1. SHAP (SHapley Additive exPlanations)

**Prioridade**: Alta (método preferencial)

**Características:**
- Valores de importância de features
- Contribuição de cada feature para a predição
- Visualizações de SHAP values

**Quando usado:**
- Predições ML do ML-NSMF
- Modelo Random Forest disponível

### 2. LIME (Local Interpretable Model-agnostic Explanations)

**Prioridade**: Média (fallback se SHAP não disponível)

**Características:**
- Explicações locais
- Modelo-agnóstico
- Interpretação textual

**Quando usado:**
- SHAP não disponível
- Modelos não suportados por SHAP

### 3. Feature Importance (Fallback)

**Prioridade**: Baixa (último recurso)

**Características:**
- Importância de features do modelo
- Sem valores SHAP
- Explicação básica

**Quando usado:**
- SHAP e LIME não disponíveis
- Modelo não suporta explicações avançadas

---

## 📊 Visualizações

### 1. Feature Importance Chart

Gráfico de barras mostrando importância de cada feature:

```
latency      ████████████████████ 40%
throughput   ██████████████ 30%
reliability  ██████████ 20%
jitter        █████ 10%
```

### 2. SHAP Values Plot

Visualização de contribuições SHAP (futuro):
- Waterfall plot
- Summary plot
- Force plot

### 3. Reasoning Textual

Explicação em linguagem natural:
- Viabilidade do SLA
- Features mais importantes
- Justificativa da recomendação

---

## ✅ Conclusão

O fluxo XAI do TriSLA Observability Portal v4.0 fornece:

- **Explicações completas** para predições ML e decisões
- **Múltiplos métodos** (SHAP, LIME, fallback)
- **Visualizações** claras e interpretáveis
- **Transparência** total nas decisões automatizadas

---

**Status:** ✅ **FLUXO XAI DOCUMENTADO**







