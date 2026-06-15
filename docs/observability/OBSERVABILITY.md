# TriSLA Observability Navigation Hub

This document is a navigation hub and specialized reference after DOC-MOD-08 consolidation.

Canonical operational entry point:

```text
docs/modules/observability.md
```

Telemetry canonical reference:

```text
docs/modules/telemetry.md
```

PromQL specialized reference:

```text
docs/PROMQL_SSOT_V2.md
```

## Runtime Boundary

Observability exposes and supports runtime monitoring, dashboards, traces, logs, health checks and evidence. It does not make decisions, execute admission, generate telemetry snapshots, or generate governance.

```text
Prometheus = PRIMARY OBSERVABILITY METRICS SOURCE
OTEL = TRACING AND INSTRUMENTATION
OTEL != telemetry_snapshot source
```

## Official Paths

Metrics path:

```text
Applications
↓
Metrics
↓
Prometheus
↓
Grafana
↓
Operators
```

Tracing path:

```text
Applications
↓
OTEL Instrumentation
↓
OTEL Collector
↓
Tempo
↓
Jaeger
```

## References

| Topic | Canonical / specialized document |
|-------|----------------------------------|
| Operational observability | `docs/modules/observability.md` |
| Runtime telemetry and `telemetry_snapshot` | `docs/modules/telemetry.md` |
| PromQL expressions | `docs/PROMQL_SSOT_V2.md` |
| Grafana dashboards | `grafana/MANIFEST.json`, `grafana/O7E_PROVISIONING.md` |
| Recording rules | `monitoring/o7c-trisla-recording-rules.yaml` |

Historical conceptual descriptions in this file were consolidated into `docs/modules/observability.md` to avoid duplication and contradictions.
