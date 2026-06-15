# SLA-Agent Layer Architecture

**Canonical architecture reference:** [`docs/modules/sla-agent-layer.md`](../../modules/sla-agent-layer.md)

The SLA-Agent is the Temporal Reassessment and Runtime Assurance Authority. This file is intentionally minimal to avoid duplicating the canonical operational document.

## Runtime summary

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

## Boundary summary

| Component / path | Status |
|------------------|--------|
| Portal Backend caller | ACTIVE |
| Prometheus Collector | PRIMARY |
| Domain Agents | CONDITIONAL / SECONDARY |
| Kafka Consumer | NOT STARTED |
| Federated Policies | NOT HOT PATH |
| Actuation | CONDITIONAL / NOT WIRED |
| Research S29 endpoints | RESEARCH / NOT HOT PATH |

Do not document `Legacy Kafka-mediated SLA-Agent chain` or domain agents as the primary runtime architecture.
