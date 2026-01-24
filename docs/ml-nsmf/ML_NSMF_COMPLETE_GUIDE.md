# Guia Completo of Módulo ML-NSMF

**Versão:** 3.5.0  
**Data:** 2025-01-27  
**Módulo:** Machine Learning Network Slice Management Function

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura of Módulo](#arquitetura-do-módulo)
3. [Funcionamento of Módulo](#funcionamento-do-módulo)
4. [Treinamento of Modelo](#treinamento-do-modelo)
5. [Predição e XAI](#predição-e-xai)
6. [Integração com Outros Módulos](#integração-com-outros-módulos)
7. [Interface I-03 (Kafka)](#interface-i-03-kafka)
8. [Observabilidade](#observabilidade)
9. [Exemplos de Uso](#exemplos-de-uso)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **ML-NSMF (Machine Learning Network Slice Management Function)** é responsável por prever a viabilidade de aceitação de SLAs baseado in métricas históricas, características of NEST e estado atual dos recursos of infraestrutura.

### Objetivos

1. **Predição de Viabilidade:** Prever se um SLA pode ser atendido (score 0-1)
2. **Explicabilidade (XAI):** Fornecer explicações das predições usando SHAP e LIME
3. **Recomendações:** Sugerir ajustes de requisitos quando necessário
4. **Integração:** Comunicar-se com Decision Engine via interface I-03 (Kafka)

### Características Principais

- **Modelo ML:** Random Forest (atual) ou LSTM/GRU (futuro)
- **XAI:** SHAP e LIME for explicações
- **Tempo de Resposta:** < 500ms
- **Acurácia:** > 85% (modelo treinado)

---

## 🏗️ Arquitetura of Módulo

### Estrutura de Diretórios

```
apps/ml-nsmf/
├── src/
│   ├── main.py                 # Aplicação FastAPI
│   ├── predictor.py            # Classe RiskPredictor (predição)
│   ├── kafka_consumer.py       # Consumer Kafka (recebe NESTs)
│   ├── kafka_producer.py       # Producer Kafka (envia predições)
│   └── __init__.py
├── models/
│   ├── viability_model.pkl    # Modelo treinado (Random Forest)
│   ├── scaler.pkl              # Scaler for normalização
│   └── model_metadata.json     # Metadados of modelo
├── data/
│   ├── datasets/
│   │   └── trisla_ml_dataset.csv  # Dataset de treinamento
│   └── training/               # Scripts de treinamento
├── tests/
│   └── unit/                   # Testes unitários
├── Dockerfile
├── requirements.txt
└── README.md
```

### Componentes Principais

1. **RiskPredictor** — Classe principal for predição
2. **MetricsConsumer** — Consome métricas of NASP via Kafka
3. **PredictionProducer** — Envia predições ao Decision Engine via Kafka
4. **Modelo ML** — Modelo treinado (Random Forest ou LSTM/GRU)
5. **XAI Explainer** — Explicador usando SHAP/LIME

---

## ⚙️ Funcionamento of Módulo

### Pipeline de Processamento

```
┌─────────────────┐
│  Recebe NEST    │  (via Kafka I-02)
│  of SEM-CSMF    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Coleta Métricas│  (do NASP via NASP Adapter)
│  Atuais         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extrai Features│  (do NEST + métricas)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Normaliza      │  (usando scaler treinado)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Predição ML    │  (modelo treinado)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Explicação XAI │  (SHAP/LIME)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Envia ao       │  (via Kafka I-03)
│  Decision Engine│
└─────────────────┘
```

### Fluxo Detalhado

1. **Recepção de NEST**
   - Consumer Kafka recebe NEST of SEM-CSMF
   - Tópico: `sem-csmf-nests`

2. **Coleta de Métricas**
   - Consulta NASP Adapter for métricas atuais
   - Domínios: RAN, Transport, Core

3. **Extração de Features**
   - Do NEST: `sliceType`, `latency_requirement`, `throughput_requirement`, `reliability_requirement`
   - Das métricas: `cpu_utilization`, `memory_utilization`, `network_bandwidth_available`, `active_slices_count`
   - Feature engineering: `latency_throughput_ratio`, `reliability_packet_loss_ratio`, etc.

4. **Normalização**
   - Usa `scaler.pkl` treinado
   - Normalização StandardScaler ou MinMaxScaler

5. **Predição**
   - Modelo ML gera score de viabilidade (0-1)
   - Threshold configurável (ex: 0.7)

6. **Explicação (XAI)**
   - SHAP ou LIME gera explicação
   - Feature importance ranking
   - Reasoning textual

7. **Envio ao Decision Engine**
   - Producer Kafka envia predição
   - Tópico: `ml-nsmf-predictions`

---

## 🎓 Treinamento of Modelo

### 1. Preparação dos Dados

#### Dataset de Treinamento

**Arquivo:** `apps/ml-nsmf/data/datasets/trisla_ml_dataset.csv`

**Estrutura of Dataset:**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `latency` | float | Latência requerida (ms) |
| `throughput` | float | Throughput requerido (Mbps) |
| `reliability` | float | Confiabilidade requerida (0-1) |
| `jitter` | float | Jitter requerido (ms) |
| `packet_loss` | float | Perda de pacotes (0-1) |
| `cpu_utilization` | float | Utilização de CPU (0-1) |
| `memory_utilization` | float | Utilização de memória (0-1) |
| `network_bandwidth_available` | float | Largura de banda disponível (Mbps) |
| `active_slices_count` | int | Número de slices ativos |
| `slice_type_encoded` | int | Tipo de slice codificado (1=eMBB, 2=URLLC, 3=mMTC) |
| `viability_score` | float | Score de viabilidade (0-1) - **TARGET** |

**Feature Engineering:**

```python
# Features derivadas
features['latency_throughput_ratio'] = features['latency'] / features['throughput']
features['reliability_packet_loss_ratio'] = features['reliability'] / (features['packet_loss'] + 0.001)
features['jitter_latency_ratio'] = features['jitter'] / (features['latency'] + 0.001)
features['resource_ratio'] = features['required_cpu'] / features['available_cpu']
```

### 2. Script de Treinamento

**Arquivo:** `apps/ml-nsmf/training/train_model.py` (a ser criado)

```python
"""
Script de Treinamento of Modelo ML-NSMF
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
import json
from datetime import datetime
import os

# Carregar dataset
def load_dataset(path: str) -> pd.DataFrame:
    """Carrega dataset de treinamento"""
    df = pd.read_csv(path)
    return df

# Feature engineering
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cria features derivadas"""
    df['latency_throughput_ratio'] = df['latency'] / (df['throughput'] + 0.001)
    df['reliability_packet_loss_ratio'] = df['reliability'] / (df['packet_loss'] + 0.001)
    df['jitter_latency_ratio'] = df['jitter'] / (df['latency'] + 0.001)
    return df

# Treinar modelo
def train_model(X_train, y_train):
    """Treina modelo Random Forest"""
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    return model

# Avaliar modelo
def evaluate_model(model, X_test, y_test):
    """Avalia modelo"""
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {
        "mse": mse,
        "mae": mae,
        "r2": r2
    }

# Função principal
def main():
    # 1. Carregar dataset
    dataset_path = "data/datasets/trisla_ml_dataset.csv"
    df = load_dataset(dataset_path)
    
    # 2. Feature engineering
    df = engineer_features(df)
    
    # 3. Separar features e target
    feature_columns = [
        "latency", "throughput", "reliability", "jitter", "packet_loss",
        "cpu_utilization", "memory_utilization", "network_bandwidth_available",
        "active_slices_count", "slice_type_encoded",
        "latency_throughput_ratio", "reliability_packet_loss_ratio",
        "jitter_latency_ratio"
    ]
    
    X = df[feature_columns]
    y = df['viability_score']
    
    # 4. Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 5. Normalização
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 6. Treinar modelo
    model = train_model(X_train_scaled, y_train)
    
    # 7. Avaliar modelo
    train_metrics = evaluate_model(model, X_train_scaled, y_train)
    test_metrics = evaluate_model(model, X_test_scaled, y_test)
    
    # 8. Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    
    # 9. Feature importance
    feature_importance = dict(zip(feature_columns, model.feature_importances_))
    
    # 10. Salvar modelo
    os.makedirs("models", exist_ok=True)
    
    # Salvar modelo
    with open("models/viability_model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    # Salvar scaler
    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    
    # Salvar metadados
    metadata = {
        "model_type": "random_forest",
        "feature_columns": feature_columns,
        "training_history": {
            "model_type": "random_forest",
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_mse": train_metrics["mse"],
            "test_mse": test_metrics["mse"],
            "train_mae": train_metrics["mae"],
            "test_mae": test_metrics["mae"],
            "train_r2": train_metrics["r2"],
            "test_r2": test_metrics["r2"],
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "feature_importance": feature_importance,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "model_path": "viability_model.pkl",
        "scaler_path": "scaler.pkl"
    }
    
    with open("models/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("Modelo treinado e salvo com sucesso!")
    print(f"Test R²: {test_metrics['r2']:.4f}")
    print(f"Test MAE: {test_metrics['mae']:.4f}")

if __name__ == "__main__":
    main()
```

### 3. Executar Treinamento

**Comando:**
```bash
cd apps/ml-nsmf
python training/train_model.py
```

**Saída Esperada:**
```
Modelo treinado e salvo com sucesso!
Test R²: 0.9028
Test MAE: 0.0464
```

### 4. Validação of Modelo

**Métricas de Avaliação:**

- **R² Score:** > 0.85 (objetivo)
- **MAE (Mean Absolute Error):** < 0.05
- **MSE (Mean Squared Error):** < 0.01
- **Cross-Validation:** CV score > 0.85

**Feature Importance:**

O modelo calcula importância de features automaticamente. Exemplo:

```json
{
  "reliability": 0.370,
  "latency_throughput_ratio": 0.254,
  "latency": 0.130,
  "throughput": 0.089,
  ...
}
```

### 5. Retreinamento

**Quando Retreinar:**

1. **Novos dados disponíveis:** Acumular novos exemplos
2. **Degradação de performance:** R² < 0.80
3. **Mudanças no ambiente:** Novos tipos de slice, mudanças na infraestrutura
4. **Período regular:** Mensal ou trimestral

**Processo de Retreinamento:**

1. Coletar novos dados of NASP
2. Adicionar ao dataset existente
3. Executar script de treinamento
4. Validar novo modelo
5. Se melhor, substituir modelo antigo
6. Se pior, manter modelo atual

---

## 🔮 Predição e XAI

### 1. Predição de Viabilidade

**Classe:** `RiskPredictor`

**Método:** `predict()`

```python
from predictor import RiskPredictor
import numpy as np

predictor = RiskPredictor()

# Métricas normalizadas
normalized_metrics = np.array([0.15, 0.5, 0.001, 0.2])

# Predição
prediction = await predictor.predict(normalized_metrics)

# Resultado
{
    "risk_score": 0.75,
    "risk_level": "high",
    "confidence": 0.85,
    "timestamp": "2025-01-27T10:00:00Z"
}
```

**Interpretação of Score:**

- **0.0 - 0.4:** Baixo risco (ACCEPT)
- **0.4 - 0.7:** Risco médio (CONDITIONAL_ACCEPT)
- **0.7 - 1.0:** Alto risco (REJECT)

### 2. Explicabilidade (XAI)

**Método:** `explain()`

**SHAP (SHapley Additive exPlanations):**

```python
explanation = await predictor.explain(prediction, normalized_metrics, model)

# Resultado
{
    "method": "SHAP",
    "features_importance": {
        "latency": 0.40,
        "throughput": 0.30,
        "packet_loss": 0.20,
        "jitter": 0.10
    },
    "reasoning": "Risk level high devido principalmente a latency (importância: 40.00%)",
    "shap_available": True,
    "lime_available": False
}
```

**LIME (Local Interpretable Model-agnostic Explanations):**

Se SHAP não estiver disponível, usa LIME:

```python
{
    "method": "LIME",
    "features_importance": {...},
    "reasoning": "...",
    "shap_available": False,
    "lime_available": True
}
```

**Fallback:**

Se nem SHAP nem LIME estiverem disponíveis:

```python
{
    "method": "fallback",
    "features_importance": {
        "latency": 0.4,
        "throughput": 0.3,
        "packet_loss": 0.2,
        "jitter": 0.1
    },
    "reasoning": "Risk level high devido principalmente à latência"
}
```

---

## 🔗 Integração com Outros Módulos

### 1. SEM-CSMF (Interface I-02)

**Tipo:** Kafka Consumer  
**Tópico:** `sem-csmf-nests`  
**Payload:** NEST (Network Slice Template)

**Código:**
```python
from kafka_consumer import MetricsConsumer

consumer = MetricsConsumer()

# Consumir NESTs
for message in consumer.consume_nests():
    nest = message.value
    # Processar NEST
    prediction = await predictor.predict_from_nest(nest)
```

### 2. Decision Engine (Interface I-03)

**Tipo:** Kafka Producer  
**Tópico:** `ml-nsmf-predictions`  
**Payload:** Predição + Explicação

**Código:**
```python
from kafka_producer import PredictionProducer

producer = PredictionProducer()

# Enviar predição
await producer.send_prediction(prediction, explanation)
```

### 3. NASP Adapter

**Tipo:** HTTP REST  
**Endpoint:** `http://nasp-adapter:8080/api/v1/metrics`

**Código:**
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://nasp-adapter:8080/api/v1/metrics")
    metrics = response.json()
```

---

## 📡 Interface I-03 (Kafka)

### Tópico Kafka

**Nome:** `ml-nsmf-predictions`

### Schema of Mensagem

```json
{
  "nest_id": "nest-001",
  "intent_id": "intent-001",
  "viability_score": 0.75,
  "risk_level": "high",
  "confidence": 0.85,
  "explanation": {
    "method": "SHAP",
    "features_importance": {
      "latency": 0.40,
      "throughput": 0.30,
      "packet_loss": 0.20,
      "jitter": 0.10
    },
    "reasoning": "Risk level high devido principalmente a latency"
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### Producer Kafka

**Arquivo:** `apps/ml-nsmf/src/kafka_producer.py`

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Enviar predição
producer.send('ml-nsmf-predictions', value=prediction_data)
```

---

## 📊 Observabilidade

### Métricas Prometheus

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `ml_nsmf_predictions_total` | Counter | Total de predições realizadas |
| `ml_nsmf_prediction_duration_seconds` | Histogram | Tempo de predição |
| `ml_nsmf_model_accuracy` | Gauge | Acurácia of modelo |
| `ml_nsmf_viability_scores` | Histogram | Distribuição de scores |
| `ml_nsmf_training_duration_seconds` | Histogram | Tempo de treinamento |

### Traces OTLP

**Spans:**
- `predict_risk` — Predição completa
- `normalize_metrics` — Normalização
- `explain_prediction` — Explicação XAI
- `send_prediction` — Envio ao Decision Engine

---

## 💡 Exemplos de Uso

### Exemplo 1: Predição Simples

```python
from predictor import RiskPredictor

predictor = RiskPredictor()

# Métricas of NEST
metrics = {
    "latency": 15.0,
    "throughput": 500.0,
    "packet_loss": 0.001,
    "jitter": 2.0
}

# Normalizar
normalized = await predictor.normalize(metrics)

# Predizer
prediction = await predictor.predict(normalized)

print(f"Score: {prediction['risk_score']}")
print(f"Level: {prediction['risk_level']}")
```

### Exemplo 2: Predição com Explicação

```python
# Predição
prediction = await predictor.predict(normalized)

# Explicação
explanation = await predictor.explain(prediction, normalized)

print(f"Method: {explanation['method']}")
print(f"Top Feature: {max(explanation['features_importance'].items(), key=lambda x: x[1])}")
print(f"Reasoning: {explanation['reasoning']}")
```

### Exemplo 3: Treinamento of Modelo

```bash
# 1. Preparar dataset
python scripts/prepare_dataset.py

# 2. Treinar modelo
cd apps/ml-nsmf
python training/train_model.py

# 3. Validar modelo
python scripts/validate_model.py

# 4. Deploy modelo
cp models/viability_model.pkl /path/to/production/models/
cp models/scaler.pkl /path/to/production/models/
```

---

## 🔧 Troubleshooting

### Problema 1: Modelo não carrega

**Sintoma:** `FileNotFoundError: models/viability_model.pkl`

**solution:**
```bash
# Verificar se modelo existe
ls -la apps/ml-nsmf/models/

# Se não existir, treinar modelo
cd apps/ml-nsmf
python training/train_model.py
```

### Problema 2: SHAP/LIME não disponível

**Sintoma:** `ImportError: No module named 'shap'`

**solution:**
```bash
pip install shap==0.43.0 lime==0.2.0.1
```

### Problema 3: Predição muito lenta

**Sintoma:** Tempo de predição > 500ms

**Soluções:**
1. Otimizar modelo (reduzir número de árvores)
2. Usar modelo mais simples (Linear Regression)
3. Cache de predições similares

### Problema 4: Acurácia baixa

**Sintoma:** R² < 0.80

**Soluções:**
1. Coletar mais dados de treinamento
2. Feature engineering adicional
3. Ajustar hiperparâmetros of modelo
4. Tentar modelo diferente (XGBoost, Neural Network)

---

## 📚 Referências

- **scikit-learn:** https://scikit-learn.org/
- **SHAP:** https://shap.readthedocs.io/
- **LIME:** https://github.com/marcotcr/lime
- **Kafka Python:** https://kafka-python.readthedocs.io/
- **Random Forest:** https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html

---

## 🎯 Conclusão

O ML-NSMF fornece predições de viabilidade de SLA com explicações usando XAI. O módulo:

- ✅ **Prediz viabilidade** de SLAs baseado in métricas
- ✅ **Explica predições** usando SHAP/LIME
- ✅ **Integra-se** com SEM-CSMF e Decision Engine
- ✅ **Observável** via Prometheus e OpenTelemetry
- ✅ **Treinável** com novos dados

Para mais informações, consulte:
- `apps/ml-nsmf/src/predictor.py` — Classe principal
- `apps/ml-nsmf/models/model_metadata.json` — Metadados of modelo
- `apps/ml-nsmf/README.md` — README of módulo

---

**Fim of Guia**

