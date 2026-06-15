# SLA Lifecycle Execution

**Canonical pipeline reference:** [`docs/modules/sla-agent-layer.md`](../../modules/sla-agent-layer.md)

## Primary runtime path

```text
Portal
↓
Revalidate
↓
Runtime Assurance
↓
Portal
```

Expanded operational path:

```text
Portal
    ↓
POST /sla/revalidate-telemetry
    ↓
SLA-Agent
POST /api/v1/agent/revalidate-telemetry
    ↓
Prometheus Collector
    ↓
Compliance
    ↓
Explainability
    ↓
Runtime Assurance
    ↓
Portal
```

## Conditional ingest path

```text
Portal
    ↓
ACCEPT
+
ORCHESTRATION SUCCESS
+
BC COMMITTED
    ↓
POST /api/v1/ingest/pipeline-event
    ↓
Runtime Assurance
    ↓
Portal
```

## Removed as primary documentation path

```text
Decision Engine
↓
Kafka
↓
SLA-Agent
```

Kafka and federated/domain-agent execution are not documented as the production hot path for DOC-MOD-06.
