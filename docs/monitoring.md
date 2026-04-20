# Monitoring in TriSLA

## Overview

TriSLA provides comprehensive monitoring capabilities through the Portal UI and Kafka-based observability.

## Portal Dashboard

### SLA Statistics

- Total SLAs processed
- Accepted / Rejected / Renegotiation counts
- Decision distribution (pie chart)
- Service type distribution (bar chart)

### Real-time Metrics

- Latency (ms)
- Throughput (Mbps)
- Packet Loss (%)
- SLA Compliance (%)

## Kafka Observability

### Decision Events Topic

`trisla-decision-events`

Every SLA decision is published to Kafka for:
- Audit trail
- Event replay
- External integrations
- Analytics

### Event Schema

```json
{
  "sla_id": "uuid",
  "intent_id": "uuid",
  "decision": "ACCEPT",
  "slice_type": "eMBB",
  "timestamp_utc": "2026-01-31T00:00:00Z",
  "system_xai": {
    "decision": "ACCEPT",
    "explanation": "...",
    "domains_evaluated": ["RAN", "Transport", "Core"]
  }
}
```

## Observability Stack

| Component | Purpose |
|-----------|---------|
| Kafka | Event streaming |
| OpenTelemetry | Distributed tracing |
| Prometheus | Metrics collection |
| Grafana | Visualization |
