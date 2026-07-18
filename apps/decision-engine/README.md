# Decision Engine

The Decision Engine evaluates a normalized SLA request and returns one of three actions: `AC`, `RENEG`, or `REJ`. It combines SLA constraints, an optional NEST, telemetry, and the ML-NSMF prediction.

## Service

- Framework: FastAPI 3.10.0
- HTTP port: `8082`
- Container entry point: `src.main:app`
- Kubernetes service: `trisla-decision-engine`

## HTTP API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service, Kafka, and gRPC listener status |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/evaluate` | Evaluate an SLA request |

See the [Decision Engine documentation](../../docs/decision-engine/README.md) for payloads, processing, and configuration.

## Source

- [FastAPI application](src/main.py)
- [Request and response models](src/models.py)
- [Decision service](src/service.py)
- [Decision logic](src/engine.py)
- [ML-NSMF client](src/ml_client.py)
