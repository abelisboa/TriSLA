# README - Módulo Machine Learning (ML-NSMF)

**TriSLA – Machine Learning Network Slice Management Function**

---

## 🎯 Função do Módulo

O **ML-NSMF** é responsável por:

1. **Receber NEST** do SEM-CSMF via interface I-02
2. **Coletar métricas** do NASP (RAN, Transport, Core)
3. **Prever viabilidade** de aceitação do SLA
4. **Fornecer explicação** (XAI) das previsões
5. **Enviar previsões** ao Decision Engine via interfaces I-02 e I-03

---

## 📥 Entradas

### 1. NEST do SEM-CSMF

```json
{
  "nestId": "nest-urllc-001",
  "sliceType": "URLLC",
  "requirements": {...}
}
```

### 2. Métricas do NASP

```json
{
  "cpu_utilization": 0.65,
  "memory_utilization": 0.70,
  "network_bandwidth_available": 500,
  "active_slices_count": 15,
  "prb_utilization": 0.45
}
```

### 3. Métricas Históricas

- Taxa de sucesso de slices anteriores
- Latência média dos últimos 7 dias
- Taxa de violação do último mês

---

## 📤 Saídas

### 1. Previsão de Viabilidade

```json
{
  "nest_id": "nest-urllc-001",
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "confidence": 0.92,
  "explanation": {
    "top_features": [
      {"feature": "latency_margin", "importance": 0.35},
      {"feature": "resource_ratio", "importance": 0.28}
    ],
    "shap_values": {...}
  },
  "timestamp": "2025-01-19T10:30:00Z"
}
```

### 2. Score de Risco

- **Score:** 0.0 a 1.0 (probabilidade de aceitação)
- **Threshold:** 0.7 (configurável)
- **Recomendação:** ACCEPT / REJECT / RENEGOTIATE

---

## 🔗 Integrações

### Interface I-02 (Kafka)

**Tópico:** `sem-csmf-nests`

**Fluxo:**
1. SEM-CSMF publica NEST no Kafka
2. ML-NSMF consome NEST
3. ML-NSMF processa e prevê viabilidade
4. ML-NSMF publica previsão no tópico `ml-nsmf-predictions`

### Interface I-03 (Kafka)

**Tópico:** `ml-nsmf-predictions`

**Fluxo:**
1. ML-NSMF publica previsão
2. Decision Engine consome previsão
3. Decision Engine usa previsão na decisão final

---

## 🎯 Responsabilidades

1. **Coleta de dados** do NASP e histórico
2. **Preprocessamento** e feature engineering
3. **Previsão** de viabilidade usando modelos de ML
4. **Explicabilidade** (XAI) com SHAP e LIME
5. **Treinamento contínuo** do modelo
6. **Observabilidade** (métricas, traces, logs)

---

## 🔄 Relação com Decision Engine

O ML-NSMF é **provedor de inteligência** para o Decision Engine:

- **Envia:** Previsão de viabilidade via I-02 e I-03 (Kafka)
- **Não recebe:** Decisões do Decision Engine
- **Relação:** Unidirecional (ML-NSMF → Decision Engine)

---

## 📋 Requisitos Técnicos

### Tecnologias

- **Python 3.12+**
- **TensorFlow/Keras** ou **scikit-learn** - Modelos de ML
- **SHAP / LIME** - Explicabilidade (XAI)
- **Apache Kafka** - Interfaces I-02 e I-03
- **PostgreSQL** - Armazenamento de datasets
- **OTLP** - Observabilidade

### Dependências

- **2_SEMANTICA** - Recebe NEST via I-02
- **6_NASP** - Coleta métricas do NASP

---

## 📚 Referências à Dissertação

- **Capítulo 4** - Arquitetura e Design
- **Capítulo 5** - Implementação e Validação
- **Machine Learning** - Previsão de viabilidade
- **XAI** - Explicabilidade das previsões

---

## ✔ Módulo Completo e Documentado

