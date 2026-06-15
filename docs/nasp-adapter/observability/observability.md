# NASP Adapter Observability

> Operational entry: [`docs/modules/nasp-adapter.md`](../../modules/nasp-adapter.md).

## Prometheus

### HTTP middleware (all routes)

| Metric | Labels |
|--------|--------|
| `trisla_http_requests_total` | `service`, `method`, `path`, `status` |
| `trisla_http_request_duration_seconds` | `service`, `method`, `path` |

Scrape endpoint: `GET /metrics` (GET and HEAD supported).

### Domain gauges

| Metric | Description |
|--------|-------------|
| `trisla_ran_prb_utilization` | RAN PRB utilization (percent 0–100) from NASP RAN metrics |

Exported by `metrics_collector.py`; consumed by Portal/Prometheus queries for admission telemetry enrichment.

### Placeholder

| Metric | Notes |
|--------|-------|
| `trisla_process_cpu_seconds_total` | Standardization gauge in `main.py` |

## OpenTelemetry (OTEL)

- FastAPI auto-instrumentation via `_trisla_attach_observability()`
- Default exporter: `OTEL_EXPORTER_OTLP_ENDPOINT` → gRPC OTLP collector
- Legacy block: `OTLP_ENABLED=false` by default (separate optional path)

Representative spans:

- `instantiate_nsi`
- `collect_nasp_metrics`
- `get_metrics_multidomain`
- `register_sla_nasp`
- `reservation_create_pending`
- `connect_nasp`

## MDCE

Structured multidomain export:

```text
GET /api/v1/metrics/multidomain
```

Returns MDCE SSOT schema with `reasons[]` for unavailable fields. Used by capacity ledger and external observability tooling.

## PRB Metrics

RAN PRB collection path:

1. `MetricsCollector` queries NASP RAN metrics / Prometheus
2. Updates `trisla_ran_prb_utilization` gauge
3. Portal and SEM resolve PRB via Prometheus proxy (not direct DE→NASP call)

## Logs

Structured logging for:

- `[BOOTSTRAP]` — NSI watch, reconciler, connectivity, O6 exporter
- `[NSI]` / `[NSI_TRACE]` — instantiate lifecycle
- `[CAPACITY]` — ledger, reservation, rollback
- `[GATE]` — 3GPP gate failures
- `[REGISTER]` — SLA register relay

## Health

```text
GET /health
```

Returns `nasp_connected` and `nasp_connectivity` detail from startup probe.
