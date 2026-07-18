# SEM-CSMF

SEM-CSMF accepts SLA intents, validates and enriches their requirements, generates GST and NEST representations, stores intent data, and sends the resulting request to the Decision Engine.

## Service

- Framework: FastAPI 3.10.0
- HTTP port: `8080`
- Container entry point: `src.main:app`
- Kubernetes service: `trisla-sem-csmf`

## Primary HTTP API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service status |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/api/v1/interpret` | Interpret free-form intent text |
| `POST` | `/api/v1/intents` | Process an SLA intent and request a decision |
| `GET` | `/api/v1/intents/{intent_id}` | Retrieve a stored intent |
| `GET` | `/api/v1/nests/{nest_id}` | Retrieve a generated NEST |
| `GET` | `/api/v1/slices` | List generated slices |

See the [SEM-CSMF documentation](../../docs/sem-csmf/README.md) for the supported client API, examples, and processing flow.

## Source

- [FastAPI application](src/main.py)
- [Intent models](src/models/intent.py)
- [NEST models](src/models/nest.py)
- [Intent processor](src/intent_processor.py)
- [Decision Engine client](src/decision_engine_client.py)
