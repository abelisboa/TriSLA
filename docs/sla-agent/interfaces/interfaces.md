# SLA-Agent REST Interfaces

Base service address inside the cluster:

```text
http://trisla-sla-agent-layer:8084
```

## Health and metrics

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Report service and domain-agent health |
| `GET` | `/metrics` | Return Prometheus metrics |

## Domain and coordination APIs

| Method | Path |
|---|---|
| `POST` | `/api/v1/agents/ran/collect` |
| `POST` | `/api/v1/agents/ran/action` |
| `POST` | `/api/v1/agents/transport/collect` |
| `POST` | `/api/v1/agents/transport/action` |
| `POST` | `/api/v1/agents/core/collect` |
| `POST` | `/api/v1/agents/core/action` |
| `GET` | `/api/v1/metrics/realtime` |
| `GET` | `/api/v1/slos` |
| `POST` | `/api/v1/coordinate` |
| `POST` | `/api/v1/policies/federated` |

## Runtime and pipeline APIs

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/runtime-assurance/evaluate` | Evaluate current telemetry against SLA requirements |
| `POST` | `/api/v1/agent/revalidate-telemetry` | Revalidate a telemetry snapshot |
| `POST` | `/api/v1/ingest/pipeline-event` | Receive a pipeline lifecycle event |
| `GET` | `/api/v1/admission/gate` | Return the current admission gate state |

## Actuation record APIs

| Method | Path |
|---|---|
| `POST` | `/api/v1/actuation/request` |
| `POST` | `/api/v1/actuation/authorize` |
| `POST` | `/api/v1/actuation/execute` |
| `POST` | `/api/v1/actuation/verify` |
| `POST` | `/api/v1/actuation/rollback` |
| `POST` | `/api/v1/actuation/expire` |
| `GET` | `/api/v1/actuation/records/{request_id}` |
| `GET` | `/api/v1/actuation/records` |

## Read-only checks

```bash
curl http://trisla-sla-agent-layer:8084/health
curl http://trisla-sla-agent-layer:8084/api/v1/slos
```

OpenAPI is available at `/openapi.json` when the service is reachable. Request schemas for state-changing endpoints are defined there.

## Source

- [FastAPI implementation](../../../apps/sla-agent-layer/src/main.py)
