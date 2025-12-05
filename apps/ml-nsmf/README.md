# ML-NSMF — Machine Learning Network Slice Management Function

**Versão:** 3.7.3  
**Fase:** M (ML-NSMF)  
**Status:** Estabilizado

---

## 📋 Visão Geral

O **ML-NSMF** é o módulo de Machine Learning do TriSLA responsável por:

- **Previsão de risco** de viabilidade de network slices usando modelo Random Forest
- **Explicabilidade (XAI)** usando SHAP e LIME
- **Integração** com SEM-CSMF (I-02) e Decision Engine (I-03) via Kafka
- **Performance** otimizada (< 500ms de latência)

---

## 🏗️ Arquitetura

### Componentes Principais

1. **RiskPredictor** (`src/predictor.py`)
   - Carrega modelo treinado (Random Forest)
   - Normaliza métricas
   - Gera predições de risco
   - Gera explicações XAI (SHAP/LIME)

2. **MetricsConsumer** (`src/kafka_consumer.py`)
   - Consome métricas do SEM-CSMF via Kafka (I-02)
   - Modo offline quando Kafka não está disponível

3. **PredictionProducer** (`src/kafka_producer.py`)
   - Envia previsões para Decision Engine via Kafka (I-03)
   - Modo offline quando Kafka não está disponível

4. **FastAPI Application** (`src/main.py`)
   - Endpoint `/api/v1/predict` para predições HTTP
   - Endpoint `/health` para health check

---

## 🤖 Modelo ML

### Modelo Atual

- **Tipo:** Random Forest
- **Features:** 13 features
  - **Diretas:** latency, throughput, reliability, jitter, packet_loss, cpu_utilization, memory_utilization, network_bandwidth_available, active_slices_count
  - **Derivadas:** latency_throughput_ratio, reliability_packet_loss_ratio, jitter_latency_ratio
  - **Categórica:** slice_type_encoded (URLLC=1, eMBB=2, mMTC=3)

### Performance

- **R² (test):** 0.9028 (90.28%)
- **CV R²:** 0.9094 ± 0.0115
- **Test MAE:** 0.0478
- **Test MSE:** 0.0036

### Top Features por Importância

1. **reliability:** 37.90%
2. **latency_throughput_ratio:** 24.98%
3. **latency:** 12.13%
4. **throughput:** 9.03%
5. **jitter:** 4.81%

---

## 🔍 XAI (Explainable AI)

### SHAP (SHapley Additive exPlanations)

- **TreeExplainer** para Random Forest
- **KernelExplainer** para outros modelos
- Gera valores SHAP para cada feature
- Normaliza importância das features

### LIME (Local Interpretable Model-agnostic Explanations)

- **LimeTabularExplainer** para modelos tabulares
- Fallback quando SHAP não está disponível
- Explica predições locais

### Explicações Geradas

Cada predição inclui:
- **Features importance:** Importância de cada feature (0-1)
- **Reasoning:** Explicação textual detalhada
- **Top factors:** Top 3 fatores que influenciam a predição

---

## 🔌 Interfaces

### I-02 (Kafka Consumer)

- **Tópico:** `nasp-metrics`
- **Origem:** SEM-CSMF
- **Formato:** JSON com métricas de network slice

### I-03 (Kafka Producer)

- **Tópico:** `trisla-ml-predictions`
- **Destino:** Decision Engine
- **Formato:** JSON com predição e explicação

### HTTP API

- **POST `/api/v1/predict`**
  - Recebe métricas JSON
  - Retorna predição e explicação

- **GET `/health`**
  - Health check do serviço

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Kafka (opcional)
KAFKA_ENABLED=true
KAFKA_BROKERS=kafka:9092
KAFKA_REQUIRED=false  # Se true, falha se Kafka não estiver disponível

# OpenTelemetry (opcional)
OTLP_ENABLED=true
OTLP_ENDPOINT=http://otlp-collector:4317

# Porta do serviço
PORT=8081
```

### Modo Offline

Se Kafka não estiver disponível, o serviço funciona em **modo offline**:
- Métricas simuladas são retornadas
- Previsões são geradas normalmente
- XAI funciona normalmente

---

## 🧪 Testes

### Testes Unitários

```bash
pytest tests/unit/test_ml_nsmf_predictor.py -v
```

**Cobertura:**
- Normalização de métricas
- Predição de risco
- Explicação XAI (SHAP/LIME)
- Diferentes tipos de slice
- Valores extremos
- Performance

### Testes de Integração

```bash
pytest tests/integration/test_ml_nsmf_kafka.py -v
```

**Cobertura:**
- Kafka Consumer (I-02)
- Kafka Producer (I-03)
- Modo offline

### Testes E2E

```bash
pytest tests/integration/test_ml_nsmf_e2e.py -v
```

**Cobertura:**
- Fluxo completo: Intent → ML → Predição
- Múltiplos intents
- Performance E2E

---

## 📊 Performance

### Latência de Predição

- **Normalização:** < 10ms
- **Predição:** < 50ms
- **XAI (SHAP):** < 500ms
- **XAI (LIME):** < 1000ms
- **Total:** < 2000ms (com XAI completo)

### Otimizações

- Modelo Random Forest otimizado (n_estimators=100, max_depth=10)
- Cache de explainers SHAP/LIME
- Normalização eficiente usando StandardScaler

---

## 📦 Estrutura de Diretórios

```
apps/ml-nsmf/
├── src/
│   ├── main.py              # FastAPI application
│   ├── predictor.py         # RiskPredictor (ML + XAI)
│   ├── kafka_consumer.py    # Kafka Consumer (I-02)
│   └── kafka_producer.py    # Kafka Producer (I-03)
├── models/
│   ├── viability_model.pkl  # Modelo treinado
│   ├── scaler.pkl           # StandardScaler
│   └── model_metadata.json  # Metadados do modelo
├── training/
│   └── train_model.py       # Script de treinamento
├── data/
│   └── datasets/            # Datasets de treinamento
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Uso

### Exemplo de Requisição HTTP

```bash
curl -X POST http://localhost:8081/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "latency": 10.0,
    "throughput": 100.0,
    "reliability": 0.99,
    "jitter": 2.0,
    "packet_loss": 0.001,
    "slice_type": "eMBB"
  }'
```

### Resposta

```json
{
  "prediction": {
    "risk_score": 0.25,
    "risk_level": "low",
    "viability_score": 0.75,
    "confidence": 0.85,
    "timestamp": "2025-01-27T00:00:00Z",
    "model_used": true
  },
  "explanation": {
    "method": "SHAP",
    "features_importance": {
      "reliability": 0.38,
      "latency_throughput_ratio": 0.25,
      "latency": 0.12
    },
    "reasoning": "Risk level low (score: 0.25). viability: 0.75. Principal fator: reliability (37.9%). Outros fatores: latency_throughput_ratio (25.0%), latency (12.1%).",
    "shap_available": true,
    "lime_available": false
  }
}
```

---

## 📝 Changelog

### v3.7.3 (FASE M)

- ✅ XAI totalmente integrado (SHAP/LIME)
- ✅ Testes unitários completos (8 testes)
- ✅ Testes de integração completos
- ✅ Testes E2E completos
- ✅ Performance validada (< 2000ms com XAI)
- ✅ Documentação completa
- ✅ Correções de datetime (timezone-aware)

---

## 🔗 Referências

- **Roadmap:** `TRISLA_PROMPTS_v3.5/roadmap/FASE_M_PLANO_EXECUCAO.md`
- **Progresso:** `TRISLA_PROMPTS_v3.5/roadmap/FASE_M_PROGRESSO.md`
- **Tabela NASP:** `TRISLA_PROMPTS_v3.5/roadmap/05_TABELA_CONSOLIDADA_NASP.md`

---

**Status:** ✅ Estabilizado — Pronto para produção
