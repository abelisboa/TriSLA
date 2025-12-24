# Explainable AI (XAI) — ML-NSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `ML_NSMF_COMPLETE_GUIDE.md` (seção Predição e XAI)

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Métodos XAI](#métodos-xai)
3. [SHAP (Preferencial)](#shap-preferencial)
4. [LIME (Fallback)](#lime-fallback)
5. [Fallback](#fallback)
6. [Explicação Gerada](#explicação-gerada)
7. [Uso no ML-NSMF](#uso-no-ml-nsmf)

---

## Visão Geral

O ML-NSMF utiliza Explainable AI (XAI) para fornecer explicações transparentes das predições de viabilidade. As explicações ajudam a entender quais features mais contribuem para a decisão e por que um SLA foi classificado como viável ou inviável.

### Objetivos

1. **Transparência**: Explicar como o modelo chegou à predição
2. **Confiança**: Aumentar confiança nas decisões automatizadas
3. **Debugging**: Identificar problemas no modelo ou dados
4. **Compliance**: Atender requisitos de explicabilidade (GDPR, etc.)

### Hierarquia de Métodos

1. **SHAP** (preferencial) — Mais preciso e completo
2. **LIME** (fallback) — Alternativa quando SHAP não disponível
3. **Fallback** — Feature importance do modelo quando XAI não disponível

---

## Métodos XAI

### SHAP (SHapley Additive exPlanations)

**Preferencial** — Método mais preciso e completo

**Vantagens:**
- Baseado em teoria de jogos (Shapley values)
- Explicações consistentes e aditivas
- Funciona com qualquer modelo

**Desvantagens:**
- Pode ser lento para modelos grandes
- Requer mais recursos computacionais

### LIME (Local Interpretable Model-agnostic Explanations)

**Fallback** — Alternativa quando SHAP não disponível

**Vantagens:**
- Mais rápido que SHAP
- Explicações locais (vizinhança da predição)
- Funciona com qualquer modelo

**Desvantagens:**
- Explicações podem variar entre execuções
- Menos preciso que SHAP

### Fallback (Feature Importance)

**Último recurso** — Quando nem SHAP nem LIME disponíveis

**Vantagens:**
- Sempre disponível (vem do modelo)
- Muito rápido

**Desvantagens:**
- Explicações globais (não específicas da predição)
- Menos preciso que SHAP/LIME

---

## SHAP (Preferencial)

### Implementação

```python
import shap
from predictor import RiskPredictor

predictor = RiskPredictor()

# Gerar explicação SHAP
explanation = await predictor.explain_shap(
    prediction=prediction,
    features=normalized_features,
    model=model
)
```

### Resultado

```json
{
    "method": "SHAP",
    "features_importance": {
        "latency": 0.40,
        "throughput": 0.30,
        "packet_loss": 0.20,
        "jitter": 0.10,
        "cpu_utilization": 0.05,
        "memory_utilization": 0.03,
        "network_bandwidth_available": 0.02
    },
    "reasoning": "Risk level high devido principalmente a latency (importância: 40.00%) e throughput (importância: 30.00%). Requisitos de latência e throughput são muito restritivos para a infraestrutura atual.",
    "shap_available": true,
    "lime_available": false
}
```

### Shapley Values

SHAP calcula Shapley values para cada feature, representando a contribuição média de cada feature para a predição:

- **Valores positivos**: Aumentam o score de viabilidade (reduzem risco)
- **Valores negativos**: Diminuem o score de viabilidade (aumentam risco)

### Visualização

SHAP fornece visualizações úteis:
- **Summary plot**: Importância de features
- **Waterfall plot**: Contribuição de cada feature
- **Force plot**: Explicação individual da predição

---

## LIME (Fallback)

### Implementação

```python
from lime.lime_tabular import LimeTabularExplainer
from predictor import RiskPredictor

predictor = RiskPredictor()

# Gerar explicação LIME
explanation = await predictor.explain_lime(
    prediction=prediction,
    features=normalized_features,
    model=model
)
```

### Resultado

```json
{
    "method": "LIME",
    "features_importance": {
        "latency": 0.38,
        "throughput": 0.32,
        "packet_loss": 0.18,
        "jitter": 0.12
    },
    "reasoning": "Risk level high devido principalmente a latency e throughput. Requisitos são muito restritivos.",
    "shap_available": false,
    "lime_available": true
}
```

### Explicação Local

LIME gera explicações locais (vizinhança da predição):
- Cria modelo interpretável localmente
- Explica por que a predição foi feita para esta instância específica
- Pode variar entre execuções (aleatoriedade)

---

## Fallback

### Implementação

Quando nem SHAP nem LIME estão disponíveis, o sistema usa feature importance do modelo:

```python
from predictor import RiskPredictor

predictor = RiskPredictor()

# Gerar explicação fallback
explanation = await predictor.explain_fallback(
    prediction=prediction,
    model=model
)
```

### Resultado

```json
{
    "method": "fallback",
    "features_importance": {
        "latency": 0.4,
        "throughput": 0.3,
        "packet_loss": 0.2,
        "jitter": 0.1
    },
    "reasoning": "Risk level high devido principalmente à latência (importância: 40%) e throughput (importância: 30%)."
}
```

### Feature Importance

Feature importance vem diretamente do modelo Random Forest:
- Calculada durante o treinamento
- Representa importância global (não específica da predição)
- Sempre disponível

---

## Explicação Gerada

### Estrutura da Explicação

Toda explicação XAI inclui:

1. **Método usado**: SHAP, LIME ou fallback
2. **Feature importance**: Ranking de importância de features
3. **Reasoning textual**: Explicação em linguagem natural
4. **Disponibilidade**: Status de SHAP e LIME

### Exemplo Completo

```json
{
    "prediction_id": "pred-001",
    "nest_id": "nest-urllc-001",
    "viability_score": 0.75,
    "risk_level": "high",
    "confidence": 0.85,
    "recommendation": "REJECT",
    "xai_explanation": {
        "method": "SHAP",
        "features_importance": {
            "latency": 0.40,
            "throughput": 0.30,
            "packet_loss": 0.20,
            "jitter": 0.10,
            "cpu_utilization": 0.05,
            "memory_utilization": 0.03,
            "network_bandwidth_available": 0.02
        },
        "reasoning": "Risk level high devido principalmente a latency (importância: 40.00%) e throughput (importância: 30.00%). Requisitos de latência e throughput são muito restritivos para a infraestrutura atual. CPU e memória estão em níveis aceitáveis, mas bandwidth disponível é limitado.",
        "shap_available": true,
        "lime_available": false
    },
    "timestamp": "2025-01-27T10:00:00Z"
}
```

### Reasoning Textual

O reasoning textual é gerado automaticamente com base na feature importance:

- **Alta importância (> 0.3)**: Mencionada explicitamente
- **Média importância (0.1-0.3)**: Mencionada se relevante
- **Baixa importância (< 0.1)**: Omitida ou mencionada brevemente

---

## Uso no ML-NSMF

### Integração no Pipeline

1. **Predição**: Modelo gera score de viabilidade
2. **XAI**: Sistema gera explicação (SHAP/LIME/fallback)
3. **Envio**: Predição + explicação enviada ao Decision Engine (I-03)

### Código de Exemplo

```python
from predictor import RiskPredictor

predictor = RiskPredictor()

# Predição
prediction = await predictor.predict(normalized_features)

# Explicação XAI
explanation = await predictor.explain(
    prediction=prediction,
    features=normalized_features,
    model=model
)

# Combinar predição e explicação
result = {
    "prediction": prediction,
    "explanation": explanation
}

# Enviar ao Decision Engine
await producer.send_prediction(result)
```

### Performance

- **SHAP**: ~200-500ms por predição
- **LIME**: ~100-300ms por predição
- **Fallback**: < 10ms (instantâneo)

### Configuração

```bash
# Habilitar/desabilitar XAI
XAI_ENABLED=true
XAI_METHOD=SHAP  # SHAP, LIME, ou AUTO
XAI_TIMEOUT=500  # ms
```

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `ML_NSMF_COMPLETE_GUIDE.md` — Seção "Predição e XAI"

**Última atualização:** 2025-01-27  
**Versão:** S4.0

