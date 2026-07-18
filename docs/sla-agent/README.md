# SLA-Agent Layer

The SLA-Agent Layer provides cross-domain metric collection, SLO evaluation, runtime state evaluation, coordination, and controlled actuation-state management.

## Runtime contract

| Item | Value |
|---|---|
| Service | `trisla-sla-agent-layer` |
| Kubernetes type | `ClusterIP` |
| Port | `8084` |
| Liveness | `GET /health` |
| Readiness | `GET /health` |
| Metrics | `GET /metrics` |

The running service reports healthy RAN, transport, and core agents.

## Functional areas

| Area | API prefix |
|---|---|
| Domain collection and actions | `/api/v1/agents` |
| Aggregate metrics and SLOs | `/api/v1/metrics`, `/api/v1/slos` |
| Coordination | `/api/v1/coordinate`, `/api/v1/policies/federated` |
| Runtime evaluation | `/api/v1/runtime-assurance/evaluate` |
| Revalidation | `/api/v1/agent/revalidate-telemetry` |
| Pipeline events | `/api/v1/ingest/pipeline-event` |
| Admission and actuation records | `/api/v1/admission`, `/api/v1/actuation` |

## Documentation

- [Architecture](architecture/sla_agent_architecture.md)
- [REST interfaces](interfaces/interfaces.md)
- [Lifecycle execution](pipeline/lifecycle_execution.md)
- [Observability](observability/observability.md)
- [Application source](../../apps/sla-agent-layer/src/main.py)
