# Traffic Exporter

Traffic Exporter is a FastAPI service that publishes Prometheus metrics without participating in SLA decisions.

## Runtime contract

| Item | Value |
|---|---|
| Application version | `3.10.8` |
| Service | `trisla-traffic-exporter` |
| Kubernetes type | `ClusterIP` |
| Port | `9105` |
| Health | `GET /health` |
| Metrics | `GET /metrics` |

Both Kubernetes probes use `/health` on port `9105`. The live response reports service name, version, and status.

## Metrics behavior

The exporter sets an availability gauge at startup and increments a request counter when `/metrics` is requested. Optional SLA and slice labels use `unknown` when values are absent.

Prometheus process and Python runtime metrics are included in the scrape output by the client library.

## References

- [Application source](app/main.py)
- [Helm workload](../../helm/trisla/templates/traffic-exporter.yaml)
- [Observability guide](../../docs/observability/OBSERVABILITY.md)
