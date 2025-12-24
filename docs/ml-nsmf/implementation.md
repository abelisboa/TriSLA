# Implementação — ML-NSMF

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `ML_NSMF_COMPLETE_GUIDE.md` (seções Arquitetura, Integração, Interface I-03, Observabilidade, Troubleshooting)

---

## 📋 Sumário

1. [Arquitetura do Módulo](#arquitetura-do-módulo)
2. [Componentes Principais](#componentes-principais)
3. [Interfaces de Comunicação](#interfaces-de-comunicação)
4. [Configuração](#configuração)
5. [Exemplos de Implementação](#exemplos-de-implementação)
6. [Troubleshooting](#troubleshooting)

---

## Arquitetura do Módulo

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
│   ├── scaler.pkl              # Scaler para normalização
│   └── model_metadata.json     # Metadados do modelo
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

### Tecnologias Utilizadas

- **Framework**: FastAPI (Python 3.10+)
- **ML**: scikit-learn (Random Forest)
- **XAI**: SHAP, LIME
- **Comunicação**: Kafka (kafka-python)
- **Observabilidade**: OpenTelemetry

---

## Componentes Principais

### 1. RiskPredictor

**Arquivo:** `src/predictor.py`

**Responsabilidades:**
- Carregar modelo treinado
- Normalizar features
- Gerar predições
- Gerar explicações XAI

**Métodos principais:**
```python
class RiskPredictor:
    def __init__(self):
        """Inicializa predictor e carrega modelo"""
        
    async def predict(self, features: np.ndarray) -> Dict:
        """Gera predição de viabilidade"""
        
    async def explain(self, prediction: Dict, features: np.ndarray) -> Dict:
        """Gera explicação XAI"""
        
    async def predict_from_nest(self, nest: Dict, metrics: Dict) -> Dict:
        """Predição completa a partir de NEST e métricas"""
```

### 2. NESTConsumer

**Arquivo:** `src/kafka_consumer.py`

**Responsabilidades:**
- Consumir NESTs do SEM-NSMF (I-02)
- Processar mensagens assíncronas
- Disparar predições

**Métodos principais:**
```python
class NESTConsumer:
    def __init__(self):
        """Inicializa consumer Kafka"""
        
    async def consume_nests(self):
        """Consome NESTs do tópico sem-csmf-nests"""
        
    async def process_nest(self, nest: Dict):
        """Processa NEST e dispara predição"""
```

### 3. MetricsCollector

**Arquivo:** `src/metrics_collector.py`

**Responsabilidades:**
- Coletar métricas atuais via NASP Adapter
- Agregar métricas de RAN, Transport, Core
- Cache de métricas

**Métodos principais:**
```python
class MetricsCollector:
    async def collect_metrics(self) -> Dict:
        """Coleta métricas atuais"""
        
    async def get_domain_metrics(self, domain: str) -> Dict:
        """Obtém métricas de um domínio específico"""
```

### 4. FeatureExtractor

**Arquivo:** `src/feature_extractor.py`

**Responsabilidades:**
- Extrair features do NEST
- Extrair features das métricas
- Feature engineering (ratios, combinações)

**Métodos principais:**
```python
class FeatureExtractor:
    def extract_from_nest(self, nest: Dict) -> np.ndarray:
        """Extrai features do NEST"""
        
    def extract_from_metrics(self, metrics: Dict) -> np.ndarray:
        """Extrai features das métricas"""
        
    def engineer_features(self, features: np.ndarray) -> np.ndarray:
        """Feature engineering"""
```

### 5. XAIExplainer

**Arquivo:** `src/xai_explainer.py`

**Responsabilidades:**
- Gerar explicações SHAP
- Gerar explicações LIME (fallback)
- Gerar explicações fallback (feature importance)

**Métodos principais:**
```python
class XAIExplainer:
    async def explain_shap(self, model, features: np.ndarray) -> Dict:
        """Gera explicação SHAP"""
        
    async def explain_lime(self, model, features: np.ndarray) -> Dict:
        """Gera explicação LIME"""
        
    async def explain_fallback(self, model) -> Dict:
        """Gera explicação fallback"""
```

### 6. PredictionProducer

**Arquivo:** `src/kafka_producer.py`

**Responsabilidades:**
- Enviar predições ao Decision Engine (I-03)
- Serialização JSON
- Retry automático

**Métodos principais:**
```python
class PredictionProducer:
    async def send_prediction(self, prediction: Dict) -> bool:
        """Envia predição ao Decision Engine"""
```

---

## Interfaces de Comunicação

### Interface I-02 (Kafka) — Entrada

**Protocolo:** Kafka  
**Direção:** SEM-NSMF → ML-NSMF  
**Tópico:** `sem-csmf-nests`  
**Partições:** 3  
**Replicação:** 1

**Implementação:**
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'sem-csmf-nests',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    nest = message.value
    # Processar NEST
    prediction = await predictor.predict_from_nest(nest, metrics)
```

### Interface I-03 (Kafka) — Saída

**Protocolo:** Kafka  
**Direção:** ML-NSMF → Decision Engine  
**Tópico:** `ml-nsmf-predictions`  
**Partições:** 3  
**Replicação:** 1

**Schema da Mensagem:**
```json
{
  "prediction_id": "pred-001",
  "nest_id": "nest-urllc-001",
  "intent_id": "intent-001",
  "viability_score": 0.75,
  "risk_level": "high",
  "confidence": 0.85,
  "recommendation": "REJECT",
  "xai_explanation": {
    "method": "SHAP",
    "features_importance": {...},
    "reasoning": "..."
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

**Implementação:**
```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('ml-nsmf-predictions', value=prediction_data)
```

### NASP Adapter (HTTP REST)

**Protocolo:** HTTP REST  
**Direção:** ML-NSMF → NASP Adapter  
**Endpoint:** `http://nasp-adapter:8080/api/v1/metrics`

**Implementação:**
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://nasp-adapter:8080/api/v1/metrics")
    metrics = response.json()
```

---

## Configuração

### Variáveis de Ambiente

```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_NEST=sem-csmf-nests
KAFKA_TOPIC_PREDICTION=ml-nsmf-predictions
KAFKA_RETRY_ATTEMPTS=3

# Modelo
MODEL_PATH=models/viability_model.pkl
SCALER_PATH=models/scaler.pkl
MODEL_METADATA_PATH=models/model_metadata.json

# XAI
XAI_ENABLED=true
XAI_METHOD=SHAP  # SHAP, LIME, ou AUTO
XAI_TIMEOUT=500  # ms

# NASP Adapter
NASP_ADAPTER_URL=http://nasp-adapter:8080
NASP_ADAPTER_TIMEOUT=5.0

# OpenTelemetry
OTLP_ENDPOINT=http://otlp-collector:4317
OTLP_PROTOCOL=grpc
```

### Dependências

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.1.1
shap==0.43.0
lime==0.2.0.1
kafka-python==2.0.2
httpx==0.25.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
pydantic==2.5.0
```

---

## Exemplos de Implementação

### Exemplo 1: Predição Completa

```python
from predictor import RiskPredictor
from feature_extractor import FeatureExtractor
from metrics_collector import MetricsCollector

predictor = RiskPredictor()
extractor = FeatureExtractor()
collector = MetricsCollector()

# Coletar métricas
metrics = await collector.collect_metrics()

# Extrair features
nest_features = extractor.extract_from_nest(nest)
metrics_features = extractor.extract_from_metrics(metrics)
features = np.concatenate([nest_features, metrics_features])

# Predição
prediction = await predictor.predict(features)

# Explicação XAI
explanation = await predictor.explain(prediction, features)
```

### Exemplo 2: Consumer Kafka

```python
from kafka_consumer import NESTConsumer
from predictor import RiskPredictor

consumer = NESTConsumer()
predictor = RiskPredictor()

async def process_nest(nest: Dict):
    # Predição
    prediction = await predictor.predict_from_nest(nest, metrics)
    
    # Enviar ao Decision Engine
    await producer.send_prediction(prediction)

# Consumir NESTs
async for nest in consumer.consume_nests():
    await process_nest(nest)
```

### Exemplo 3: API REST Endpoint

```python
from fastapi import FastAPI
from predictor import RiskPredictor

app = FastAPI()
predictor = RiskPredictor()

@app.post("/api/v1/predict")
async def predict_viability(nest: Dict, metrics: Dict):
    prediction = await predictor.predict_from_nest(nest, metrics)
    return prediction
```

---

## Troubleshooting

### Problema 1: Modelo não carrega

**Sintoma:** `FileNotFoundError: models/viability_model.pkl`

**Solução:**
- Verificar se modelo existe: `ls models/viability_model.pkl`
- Treinar modelo: `python training/train_model.py`
- Verificar `MODEL_PATH` nas variáveis de ambiente

### Problema 2: SHAP não funciona

**Sintoma:** `ImportError: shap is not installed`

**Solução:**
```bash
pip install shap==0.43.0
```

### Problema 3: Kafka não recebe mensagens

**Sintoma:** Consumer não recebe NESTs

**Solução:**
- Verificar se Kafka está rodando
- Verificar `KAFKA_BOOTSTRAP_SERVERS`
- Verificar tópico existe: `kafka-topics --list`
- Verificar consumer group: `kafka-consumer-groups --describe`

### Problema 4: Métricas não coletadas

**Sintoma:** `httpx.ConnectError` ao consultar NASP Adapter

**Solução:**
- Verificar se NASP Adapter está rodando
- Verificar `NASP_ADAPTER_URL`
- Verificar conectividade de rede
- Verificar timeout: `NASP_ADAPTER_TIMEOUT`

### Problema 5: Predição muito lenta

**Sintoma:** Predição demora > 1 segundo

**Solução:**
- Desabilitar XAI temporariamente: `XAI_ENABLED=false`
- Usar LIME em vez de SHAP: `XAI_METHOD=LIME`
- Verificar recursos computacionais (CPU, memória)
- Otimizar feature extraction

---

## Observabilidade

### Métricas Prometheus

O módulo expõe métricas via endpoint `/metrics`:

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `trisla_predictions_total` | Counter | Total de predições realizadas |
| `trisla_prediction_duration_seconds` | Histogram | Duração de predição |
| `trisla_prediction_accuracy` | Gauge | Acurácia do modelo (quando disponível) |
| `trisla_xai_explanations_total` | Counter | Total de explicações XAI geradas |
| `trisla_xai_duration_seconds` | Histogram | Duração de geração de explicação |
| `trisla_kafka_messages_received_total` | Counter | Total de mensagens Kafka recebidas (I-02) |
| `trisla_kafka_messages_sent_total` | Counter | Total de mensagens Kafka enviadas (I-03) |

### Traces OpenTelemetry

Traces distribuídos são gerados para rastreabilidade:

- **Span:** `ml_nsmf.receive_nest` — Recepção de NEST (I-02)
- **Span:** `ml_nsmf.collect_metrics` — Coleta de métricas
- **Span:** `ml_nsmf.extract_features` — Extração de features
- **Span:** `ml_nsmf.predict_viability` — Predição de viabilidade
- **Span:** `ml_nsmf.generate_xai` — Geração de explicação XAI
- **Span:** `ml_nsmf.send_prediction` — Envio de predição (I-03)

### Logs Estruturados

Logs estruturados incluem:
- `prediction_id`: Identificador da predição
- `nest_id`: Referência ao NEST
- `viability_score`: Score de viabilidade
- `confidence`: Confiança da predição
- `processing_time`: Tempo de processamento
- `xai_method`: Método XAI usado (SHAP/LIME/fallback)

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `ML_NSMF_COMPLETE_GUIDE.md` — Seções "Arquitetura do Módulo", "Integração com Outros Módulos", "Interface I-03", "Observabilidade", "Troubleshooting"

**Última atualização:** 2025-01-27  
**Versão:** S4.0

