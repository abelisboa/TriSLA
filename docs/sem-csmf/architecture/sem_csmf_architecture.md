# SEM-CSMF Architecture

## Responsibilities

SEM-CSMF turns an SLA request into validated service requirements and a NEST. For the main submission endpoint, it also sends the normalized request to the Decision Engine and returns the resulting action.

## Components

| Component | Source | Responsibility |
|---|---|---|
| FastAPI application | [`src/main.py`](../../../apps/sem-csmf/src/main.py) | HTTP endpoints, persistence calls, and request coordination |
| Intent models | [`src/models/intent.py`](../../../apps/sem-csmf/src/models/intent.py) | Input and output validation |
| Intent processor | [`src/intent_processor.py`](../../../apps/sem-csmf/src/intent_processor.py) | Text parsing, requirement validation, and GST generation |
| Ontology loader | [`src/ontology/loader.py`](../../../apps/sem-csmf/src/ontology/loader.py) | Loads OWL or TTL resources and supports queries |
| NEST generator | [`src/nest_generator_db.py`](../../../apps/sem-csmf/src/nest_generator_db.py) | Creates and retrieves persisted NEST objects |
| Decision client | [`src/decision_engine_client.py`](../../../apps/sem-csmf/src/decision_engine_client.py) | Calls Decision Engine `POST /evaluate` |
| Repository | [`src/repository.py`](../../../apps/sem-csmf/src/repository.py) | Intent and NEST persistence |

## Main request path

```text
Client
    │ POST /api/v1/intents
    ▼
Input validation and persistence
    ▼
Requirement validation and fill
    ▼
GST generation
    ▼
NEST generation and persistence
    ▼
Decision Engine POST /evaluate
    ▼
IntentResponse
```

`POST /api/v1/interpret` performs text interpretation, requirement generation, validation, GST generation, and NEST generation without calling the Decision Engine.

## Deployment

The Helm chart deploys SEM-CSMF as a `ClusterIP` service on port `8080` and configures liveness and readiness probes on `/health`. The container starts Uvicorn with `src.main:app`.
