# NASP Adapter Observability

## Health

`GET /health` reports:

- service status;
- NASP connection state;
- selected NASP mode and core namespace;
- AMF, SMF, and NRF probe endpoints and results.

## Metrics endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/metrics` | Prometheus text format |
| `HEAD` | `/metrics` | Scraper compatibility |
| `GET` | `/api/v1/nasp/metrics` | Current measurements collected from NASP services |
| `GET` | `/api/v1/metrics/multidomain` | RAN, transport, and core measurement view |

Unavailable measurements are returned as null values with reason information rather than fabricated values.

## Telemetry configuration

| Variable | Purpose | Default |
|---|---|---|
| `PROMETHEUS_URL` | Prometheus query endpoint | cluster monitoring service |
| `OTLP_ENABLED` | Enable OTLP span export | `false` |
| `OTLP_ENDPOINT` | OTLP collector address | `http://otlp-collector:4317` |
| `MULTIDOMAIN_METRICS_EXPORT_ENABLED` | Enable background metric refresh | `false` |
| `MULTIDOMAIN_METRICS_REFRESH_SECONDS` | Refresh interval | `30` |

The Helm chart also creates a metrics service and ServiceMonitor when their values are enabled.
