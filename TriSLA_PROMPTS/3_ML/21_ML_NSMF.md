# 21 – Implementação Completa do ML-NSMF  

**TriSLA – Módulo de Machine Learning para Previsão de Viabilidade de SLAs**

---

## 🎯 Objetivo Geral

Implementar o módulo **ML-NSMF (Machine Learning Network Slice Management Function)** que utiliza técnicas de **Machine Learning** para prever a viabilidade de aceitação de SLAs baseado em:

- **Métricas históricas** do NASP
- **Características do NEST** gerado pelo SEM-CSMF
- **Estado atual dos recursos** da infraestrutura
- **Padrões de uso** anteriores

O módulo fornece:
- **Score de viabilidade** (0-1)
- **Explicabilidade (XAI)** das previsões
- **Recomendações** de ajuste de requisitos
- **Interface I-03** (Kafka) para comunicação com Decision Engine

---

## 📋 Requisitos Funcionais

### 1. Coleta de Dados

- Receber **métricas do NASP** (RAN, Transport, Core)
- Receber **NEST** do SEM-CSMF via interface I-02
- Coletar **métricas históricas** de slices anteriores
- Armazenar **datasets** para treinamento contínuo

### 2. Preprocessamento

- **Normalização** de features
- **Feature engineering** (extração de características relevantes)
- **Handling de dados faltantes**
- **Balanceamento** de classes (se necessário)

### 3. Modelo de ML

- **Modelo LSTM ou GRU** para séries temporais
- **Alternativa:** Random Forest ou XGBoost para features estáticas
- **Treinamento** com dados históricos
- **Validação cruzada** e métricas de avaliação
- **Persistência** do modelo treinado (model.h5 ou pickle)

### 4. Previsão

- **Score de viabilidade** (probabilidade de aceitação)
- **Threshold** configurável (ex: 0.7)
- **Tempo de resposta** < 500ms

### 5. Explicabilidade (XAI)

- **SHAP values** para explicação de features
- **LIME** para explicação local
- **Feature importance** ranking
- **Logs explicáveis** para auditoria

### 6. Interface I-03 (Kafka)

- **Producer** para enviar previsões ao Decision Engine
- **Consumer** para receber NESTs do SEM-CSMF
- **Retry logic** para mensagens falhadas
- **Dead letter queue** para mensagens problemáticas

---

## 🏗️ Arquitetura do Módulo

```
apps/ml-nsmf/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── predictor.py        # Modelo de ML
│   │   ├── preprocessor.py     # Preprocessamento
│   │   └── explainer.py        # XAI (SHAP/LIME)
│   ├── training/
│   │   ├── train.py            # Script de treinamento
│   │   ├── data_loader.py      # Carregador de dados
│   │   ├── feature_engineering.py
│   │   └── evaluator.py        # Avaliação do modelo
│   ├── kafka/
│   │   ├── producer.py         # Producer Kafka I-03
│   │   ├── consumer.py         # Consumer Kafka I-02
│   │   └── schemas.py          # Schemas Avro/JSON
│   ├── data/
│   │   ├── datasets/           # Datasets históricos
│   │   └── models/             # Modelos treinados (model.h5)
│   ├── observability/
│   │   ├── otlp_exporter.py    # Exportador OTLP
│   │   └── metrics.py          # Métricas Prometheus
│   └── config.py               # Configurações
├── tests/
│   ├── unit/
│   ├── integration/
│   └── training/
├── notebooks/                  # Jupyter notebooks para análise
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔧 Implementação Técnica

### 1. Modelo de Machine Learning

**Opção 1: LSTM/GRU (Séries Temporais)**

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(timesteps, features)),
    Dropout(0.2),
    LSTM(64, return_sequences=False),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Score de viabilidade
])
```

**Opção 2: Random Forest / XGBoost (Features Estáticas)**

```python
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

model = XGBClassifier(
    n_estimators=100,
    max_depth=10,
    learning_rate=0.1,
    objective='binary:logistic'
)
```

**Escolha baseada em:**
- Se há dependência temporal → LSTM/GRU
- Se features são estáticas → Random Forest/XGBoost

### 2. Features (Inputs)

**Do NEST:**
- `sliceType` (eMBB/URLLC/mMTC)
- `latency_requirement`
- `throughput_requirement`
- `reliability_requirement`
- `coverage_area`

**Do NASP (Métricas atuais):**
- `cpu_utilization`
- `memory_utilization`
- `network_bandwidth_available`
- `active_slices_count`
- `prb_utilization` (RAN)

**Históricas:**
- `success_rate_last_30_days`
- `average_latency_last_7_days`
- `violation_rate_last_month`

### 3. Preprocessamento

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Normalização
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Feature engineering
features['resource_ratio'] = features['required_cpu'] / features['available_cpu']
features['latency_margin'] = features['max_latency'] - features['current_latency']
```

### 4. Treinamento

**Script:** `apps/ml-nsmf/src/training/train.py`

```python
def train_model():
    # Carregar dados
    X_train, y_train = load_training_data()
    
    # Preprocessar
    X_train_scaled = preprocess(X_train)
    
    # Treinar modelo
    model.fit(X_train_scaled, y_train, epochs=50, validation_split=0.2)
    
    # Avaliar
    metrics = evaluate_model(model, X_test, y_test)
    
    # Salvar modelo
    model.save('data/models/model.h5')
    save_scaler(scaler, 'data/models/scaler.pkl')
```

### 5. Previsão

```python
def predict_viability(nest: dict, nasp_metrics: dict) -> dict:
    # Extrair features
    features = extract_features(nest, nasp_metrics)
    
    # Preprocessar
    features_scaled = scaler.transform([features])
    
    # Prever
    score = model.predict(features_scaled)[0][0]
    
    # Explicar (XAI)
    explanation = explainer.explain(features_scaled[0])
    
    return {
        'viability_score': float(score),
        'recommendation': 'ACCEPT' if score > threshold else 'REJECT',
        'explanation': explanation,
        'confidence': calculate_confidence(score)
    }
```

### 6. Explicabilidade (XAI)

**SHAP (SHapley Additive exPlanations):**

```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(features)

# Visualização
shap.summary_plot(shap_values, features)
```

**LIME (Local Interpretable Model-agnostic Explanations):**

```python
from lime import lime_tabular

explainer = lime_tabular.LimeTabularExplainer(
    training_data,
    feature_names=feature_names,
    mode='classification'
)
explanation = explainer.explain_instance(features, model.predict)
```

### 7. Interface Kafka I-03

**Producer (Enviar previsão):**

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

message = {
    'nest_id': nest_id,
    'viability_score': score,
    'recommendation': recommendation,
    'explanation': explanation,
    'timestamp': datetime.now().isoformat()
}

producer.send('ml-nsmf-predictions', value=message)
```

**Consumer (Receber NEST):**

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'sem-csmf-nests',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    nest = message.value
    prediction = predict_viability(nest, get_nasp_metrics())
    send_to_decision_engine(prediction)
```

---

## 📊 Persistência

### Armazenamento de Modelos

- **Modelo treinado:** `data/models/model.h5` (TensorFlow) ou `model.pkl` (scikit-learn)
- **Scaler:** `data/models/scaler.pkl`
- **Feature names:** `data/models/feature_names.json`
- **Metadata:** `data/models/metadata.json` (versão, acurácia, data de treinamento)

### Datasets

- **Treinamento:** `data/datasets/training_data.csv`
- **Validação:** `data/datasets/validation_data.csv`
- **Teste:** `data/datasets/test_data.csv`

---

## 🔍 Observabilidade

### Métricas Prometheus

- `ml_nsmf_predictions_total` - Total de previsões realizadas
- `ml_nsmf_prediction_duration_seconds` - Tempo de previsão
- `ml_nsmf_model_accuracy` - Acurácia do modelo
- `ml_nsmf_viability_scores` - Histograma de scores
- `ml_nsmf_training_duration_seconds` - Tempo de treinamento

### Traces OTLP

- Trace completo: Recepção NEST → Previsão → Envio ao Decision Engine
- Spans para cada etapa (preprocessamento, predição, explicação)

---

## 🧪 Testes

### Testes Unitários

- Preprocessamento de features
- Predição do modelo
- Explicabilidade (XAI)
- Validação de inputs

### Testes de Integração

- Fluxo completo: NEST → Previsão → Kafka
- Comunicação com NASP para métricas
- Persistência de modelos

### Testes de Treinamento

- Validação cruzada
- Métricas de avaliação (accuracy, precision, recall, F1)
- Overfitting detection

---

## 📝 Exemplos

### Exemplo 1: Previsão de Viabilidade

**Input (NEST):**
```json
{
  "nestId": "nest-urllc-001",
  "sliceType": "URLLC",
  "requirements": {
    "latency": {"max": 10, "unit": "ms"},
    "reliability": 0.99999
  }
}
```

**Input (Métricas NASP):**
```json
{
  "cpu_utilization": 0.65,
  "memory_utilization": 0.70,
  "network_bandwidth_available": 500,
  "active_slices_count": 15
}
```

**Output:**
```json
{
  "nest_id": "nest-urllc-001",
  "viability_score": 0.87,
  "recommendation": "ACCEPT",
  "confidence": 0.92,
  "explanation": {
    "top_features": [
      {"feature": "latency_margin", "importance": 0.35},
      {"feature": "resource_ratio", "importance": 0.28},
      {"feature": "reliability_requirement", "importance": 0.22}
    ],
    "shap_values": {...}
  },
  "timestamp": "2025-01-19T10:30:00Z"
}
```

---

## ✅ Critérios de Sucesso

- ✅ Modelo treinado com acurácia > 85%
- ✅ Previsão em < 500ms
- ✅ Explicabilidade (XAI) funcionando
- ✅ Interface Kafka I-03 operacional
- ✅ Retry logic implementado
- ✅ Observabilidade completa
- ✅ Testes passando (unit, integration, training)
- ✅ Modelo versionado e persistido

---

## 🚀 Deploy

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código e modelo
COPY . .
COPY data/models/model.h5 data/models/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

- Deployment com 2 replicas
- Service para REST API (port 8000)
- ConfigMap para configurações do modelo
- PersistentVolume para modelos e datasets

---

## 📚 Referências

- TensorFlow / Keras - Deep Learning Framework
- scikit-learn - Machine Learning Library
- SHAP - Explainable AI
- LIME - Local Interpretable Model-agnostic Explanations
- Apache Kafka - Distributed Streaming Platform

---

## ✔ Pronto para implementação no Cursor

