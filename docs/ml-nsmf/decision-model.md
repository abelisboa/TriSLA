# Modelo de Decisão — ML-NSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `ML_NSMF_COMPLETE_GUIDE.md` (seções Treinamento do Modelo, Funcionamento do Módulo)

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Modelo ML](#modelo-ml)
3. [Features](#features)
4. [Feature Engineering](#feature-engineering)
5. [Treinamento](#treinamento)
6. [Avaliação](#avaliação)
7. [Interpretação de Predições](#interpretação-de-predições)

---

## Visão Geral

O modelo de decisão do ML-NSMF utiliza Machine Learning (Random Forest Regressor) para prever a viabilidade de aceitação de SLAs. O modelo recebe features extraídas do NEST e métricas atuais da infraestrutura, e retorna um score de viabilidade (0.0 a 1.0).

### Objetivo

Prever se um SLA pode ser atendido com base em:
- Requisitos de SLA do NEST (latência, throughput, confiabilidade, etc.)
- Estado atual da infraestrutura (CPU, memória, bandwidth, slices ativos)
- Histórico de violações (quando disponível)

### Score de Viabilidade

- **0.0 - 0.4**: Baixo risco → **ACCEPT**
- **0.4 - 0.7**: Risco médio → **CONDITIONAL_ACCEPT** ou **RENEGOTIATE**
- **0.7 - 1.0**: Alto risco → **REJECT**

---

## Modelo ML

### Tipo de Modelo

**Algoritmo:** Random Forest Regressor

**Parâmetros:**
- `n_estimators`: 100
- `max_depth`: 10
- `min_samples_split`: 5
- `min_samples_leaf`: 2
- `random_state`: 42
- `n_jobs`: -1 (paralelização)

### Arquivos do Modelo

- **Modelo treinado:** `apps/ml-nsmf/models/viability_model.pkl`
- **Scaler:** `apps/ml-nsmf/models/scaler.pkl`
- **Metadados:** `apps/ml-nsmf/models/model_metadata.json`

### Carregamento

```python
import pickle
import json

# Carregar modelo
with open("models/viability_model.pkl", "rb") as f:
    model = pickle.load(f)

# Carregar scaler
with open("models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# Carregar metadados
with open("models/model_metadata.json", "r") as f:
    metadata = json.load(f)
```

---

## Features

### Features do Dataset (13 features)

| Feature | Tipo | Descrição | Fonte |
|---------|------|-----------|-------|
| `latency` | float | Latência requerida (ms) | NEST |
| `throughput` | float | Throughput requerido (Mbps) | NEST |
| `reliability` | float | Confiabilidade requerida (0-1) | NEST |
| `jitter` | float | Jitter requerido (ms) | NEST |
| `packet_loss` | float | Taxa de perda de pacotes (0-1) | NEST |
| `cpu_utilization` | float | Utilização de CPU (0-1) | Métricas NASP |
| `memory_utilization` | float | Utilização de memória (0-1) | Métricas NASP |
| `network_bandwidth_available` | float | Bandwidth disponível (Mbps) | Métricas NASP |
| `active_slices_count` | int | Número de slices ativos | Métricas NASP |
| `slice_type_encoded` | int | Tipo de slice (1=eMBB, 2=URLLC, 3=mMTC) | NEST |
| `latency_throughput_ratio` | float | Ratio latência/throughput | Feature engineering |
| `reliability_packet_loss_ratio` | float | Ratio confiabilidade/perda | Feature engineering |
| `jitter_latency_ratio` | float | Ratio jitter/latência | Feature engineering |

### Target

**Variável alvo:** `viability_score` (0.0 a 1.0)

- **0.0**: SLA totalmente viável
- **1.0**: SLA totalmente inviável

---

## Feature Engineering

### Features Derivadas

O modelo utiliza feature engineering para criar features derivadas que capturam relações entre requisitos e métricas:

```python
# Features derivadas
features['latency_throughput_ratio'] = features['latency'] / (features['throughput'] + 0.001)
features['reliability_packet_loss_ratio'] = features['reliability'] / (features['packet_loss'] + 0.001)
features['jitter_latency_ratio'] = features['jitter'] / (features['latency'] + 0.001)
```

### Normalização

Todas as features são normalizadas usando **StandardScaler** antes da predição:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### Extração de Features do NEST

```python
def extract_features_from_nest(nest: Dict, metrics: Dict) -> np.ndarray:
    """Extrai features do NEST e métricas"""
    features = np.array([
        nest['sla_requirements']['latency'],
        nest['sla_requirements']['throughput'],
        nest['sla_requirements']['reliability'],
        nest['sla_requirements']['jitter'],
        nest['sla_requirements']['packet_loss'],
        metrics['cpu_utilization'],
        metrics['memory_utilization'],
        metrics['network_bandwidth_available'],
        metrics['active_slices_count'],
        encode_slice_type(nest['slice_type']),
        nest['sla_requirements']['latency'] / (nest['sla_requirements']['throughput'] + 0.001),
        nest['sla_requirements']['reliability'] / (nest['sla_requirements']['packet_loss'] + 0.001),
        nest['sla_requirements']['jitter'] / (nest['sla_requirements']['latency'] + 0.001)
    ])
    return features
```

---

## Treinamento

### Dataset de Treinamento

**Arquivo:** `apps/ml-nsmf/data/datasets/trisla_ml_dataset.csv`

**Estrutura:**
- 13 features (colunas de entrada)
- 1 target (`viability_score`)
- Formato CSV

### Script de Treinamento

**Arquivo:** `apps/ml-nsmf/training/train_model.py`

**Processo:**
1. Carregar dataset
2. Feature engineering
3. Separar features e target
4. Split train/test (80/20)
5. Normalização (StandardScaler)
6. Treinar modelo (Random Forest)
7. Avaliar modelo
8. Cross-validation (5-fold)
9. Salvar modelo, scaler e metadados

**Executar:**
```bash
cd apps/ml-nsmf
python training/train_model.py
```

### Parâmetros de Treinamento

- **Test size:** 0.2 (20% para teste)
- **Random state:** 42 (reprodutibilidade)
- **Cross-validation:** 5-fold
- **Scoring:** R² score

---

## Avaliação

### Métricas de Avaliação

**Objetivos:**
- **R² Score:** > 0.85
- **MAE (Mean Absolute Error):** < 0.05
- **MSE (Mean Squared Error):** < 0.01
- **Cross-Validation:** CV score > 0.85

**Exemplo de saída:**
```
Modelo treinado e salvo com sucesso!
Test R²: 0.9028
Test MAE: 0.0464
```

### Feature Importance

O modelo calcula importância de features automaticamente. Exemplo:

```json
{
  "reliability": 0.370,
  "latency_throughput_ratio": 0.254,
  "latency": 0.130,
  "throughput": 0.089,
  "cpu_utilization": 0.052,
  "memory_utilization": 0.038,
  "packet_loss": 0.025,
  "jitter": 0.020,
  "network_bandwidth_available": 0.015,
  "active_slices_count": 0.004,
  "slice_type_encoded": 0.002,
  "reliability_packet_loss_ratio": 0.001,
  "jitter_latency_ratio": 0.000
}
```

### Retreinamento

**Quando retreinar:**
1. Novos dados disponíveis (acumular novos exemplos)
2. Degradação de performance (R² < 0.80)
3. Mudanças no ambiente (novos tipos de slice, mudanças na infraestrutura)
4. Período regular (mensal ou trimestral)

**Processo:**
1. Coletar novos dados do NASP
2. Adicionar ao dataset existente
3. Executar script de treinamento
4. Validar novo modelo
5. Se melhor, substituir modelo antigo
6. Se pior, manter modelo atual

---

## Interpretação de Predições

### Score de Viabilidade

O modelo retorna um score de viabilidade (0.0 a 1.0):

- **0.0 - 0.4**: Baixo risco
  - SLA provavelmente será atendido
  - Recomendação: **ACCEPT**

- **0.4 - 0.7**: Risco médio
  - SLA pode ser atendido com condições
  - Recomendação: **CONDITIONAL_ACCEPT** ou **RENEGOTIATE**

- **0.7 - 1.0**: Alto risco
  - SLA provavelmente não será atendido
  - Recomendação: **REJECT**

### Exemplo de Predição

```python
from predictor import RiskPredictor

predictor = RiskPredictor()

# Predição
prediction = await predictor.predict(normalized_features)

# Resultado
{
    "viability_score": 0.75,
    "risk_level": "high",
    "confidence": 0.85,
    "recommendation": "REJECT",
    "timestamp": "2025-01-27T10:00:00Z"
}
```

### Confiança da Predição

A confiança é calculada com base na variância das predições das árvores do Random Forest:

- **Alta confiança (> 0.8)**: Predição confiável
- **Média confiança (0.5-0.8)**: Predição moderadamente confiável
- **Baixa confiança (< 0.5)**: Predição pouco confiável (considerar retreinar modelo)

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `ML_NSMF_COMPLETE_GUIDE.md` — Seções "Treinamento do Modelo", "Funcionamento do Módulo"
- `ML_NSMF_COMPLETE_GUIDE.md` — Seção "Predição e XAI" (interpretação de predições)

**Última atualização:** 2025-01-27  
**Versão:** S4.0

