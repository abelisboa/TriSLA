# ML-NSMF Architecture

## Responsibilities

ML-NSMF exposes a single prediction operation. It validates the availability of the active model bundle at startup, transforms the request into the model feature vector, runs inference, derives risk values, and builds an explanation.

## Components

| Component | Source | Responsibility |
|---|---|---|
| FastAPI application | [`src/main.py`](../../../apps/ml-nsmf/src/main.py) | Health, metrics, and prediction endpoint |
| Prediction pipeline | [`src/prediction_pipeline.py`](../../../apps/ml-nsmf/src/prediction_pipeline.py) | Normalization, inference, and response assembly |
| Predictor | [`src/predictor.py`](../../../apps/ml-nsmf/src/predictor.py) | Model loading, scoring, risk mapping, and explanations |
| Model loader | [`src/model_loader.py`](../../../apps/ml-nsmf/src/model_loader.py) | Resolves and validates model assets |
| Kafka producer | [`src/kafka_producer.py`](../../../apps/ml-nsmf/src/kafka_producer.py) | Optional prediction event output |

## Request path

```text
Decision Engine
    │ POST /api/v1/predict
    ▼
Feature normalization
    ▼
Active model inference
    ▼
Risk mapping and explanation
    ▼
Prediction response
```

The prediction response is always produced by the active model. The health response reports whether its model and scaler are valid.

## Deployment

The Helm chart deploys ML-NSMF as a `ClusterIP` service on port `8081`, sets `/health` probes, and configures optional Kafka and telemetry endpoints. The deployment template defaults to one replica unless `mlNsmf.replicaCount` is supplied.
