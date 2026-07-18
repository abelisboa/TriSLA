# Decision Engine Architecture

## Responsibilities

The Decision Engine accepts SLA evaluation requests, prepares a decision input, requests an ML-NSMF prediction, applies the configured decision logic, and returns a structured result.

## Components

| Component | Source | Responsibility |
|---|---|---|
| FastAPI application | [`src/main.py`](../../../apps/decision-engine/src/main.py) | HTTP endpoints, health, metrics, and process lifecycle |
| Request models | [`src/models.py`](../../../apps/decision-engine/src/models.py) | Input validation and response serialization |
| Decision service | [`src/service.py`](../../../apps/decision-engine/src/service.py) | Coordinates prediction and evaluation |
| Decision engine | [`src/engine.py`](../../../apps/decision-engine/src/engine.py) | Produces the admission action and explanation |
| ML client | [`src/ml_client.py`](../../../apps/decision-engine/src/ml_client.py) | Calls ML-NSMF at `/api/v1/predict` |
| NEST resolver | [`src/nest_input_resolver.py`](../../../apps/decision-engine/src/nest_input_resolver.py) | Normalizes the optional NEST input |

## Request path

```text
SEM-CSMF
    │ POST /evaluate
    ▼
FastAPI validation
    ▼
DecisionService
    ├── ML-NSMF POST /api/v1/predict
    └── DecisionEngine evaluation
    ▼
DecisionResult
```

The telemetry snapshot may contain RAN, transport, and core measurements. The service adds it to the evaluation context before calling the decision logic.

## Deployment

The Helm chart deploys the service as a `ClusterIP` endpoint on port `8082`, configures health probes on `/health`, and supplies the ML-NSMF service URL. The application also starts its gRPC listener on port `50051`; public HTTP clients use `/evaluate`.
