# SLA-Agent Interfaces

> Specialized reference. Canonical cross-module interface truth: [`docs/modules/interfaces.md`](../../modules/interfaces.md).

**Canonical reference:** [`docs/modules/sla-agent-layer.md`](../../modules/sla-agent-layer.md)

## Primary interface

| Caller | Method | Path | Classification |
|--------|--------|------|----------------|
| Portal Backend | POST | `/api/v1/agent/revalidate-telemetry` | PRIMARY / SOLE REVALIDATE AUTHORITY |

Portal Backend exposes its public revalidation route and delegates the reassessment to the SLA-Agent internal endpoint. The SLA-Agent then collects telemetry, evaluates compliance, generates explainability, runs runtime assurance, and returns the result to the Portal.

```text
Portal Backend
    -> POST /api/v1/agent/revalidate-telemetry
SLA-Agent
    -> Prometheus Collector
    -> Compliance
    -> Explainability
    -> Runtime Assurance
    -> Portal Backend
```

## Conditional pipeline interface

| Caller | Method | Path | Classification |
|--------|--------|------|----------------|
| Portal Backend | POST | `/api/v1/ingest/pipeline-event` | CONDITIONAL |

Active only after:

```text
ACCEPT
+
ORCHESTRATION SUCCESS
+
BC COMMITTED
```

## Other runtime interfaces

| Method | Path | Classification |
|--------|------|----------------|
| GET | `/health` | ACTIVE |
| GET | `/metrics` | ACTIVE |
| POST | `/api/v1/runtime-assurance/evaluate` | ACTIVE |
| POST | `/api/v1/agents/ran/collect` | CONDITIONAL / NOT HOT PATH |
| POST | `/api/v1/agents/transport/collect` | CONDITIONAL / NOT HOT PATH |
| POST | `/api/v1/agents/core/collect` | CONDITIONAL / NOT HOT PATH |
| POST | `/api/v1/coordinate` | CONDITIONAL / NOT HOT PATH |
| GET | `/api/v1/slos` | CONDITIONAL / NOT HOT PATH |
| `/api/v1/actuation/*` | CONDITIONAL / NOT WIRED |
| POST | `/api/v1/s29/create-snapshot` | RESEARCH / NOT HOT PATH |
| POST | `/api/v1/s29/generate-explanation` | RESEARCH / NOT HOT PATH |

## Non-primary interfaces

| Interface | Status |
|-----------|--------|
| Legacy Kafka action ingress | NOT STARTED as production ingress |
| Kafka I-06 / I-07 | NOT HOT PATH |
| Legacy Kafka-mediated SLA-Agent chain | NOT PRIMARY |
| Domain agents as primary interface | NOT PRIMARY |
