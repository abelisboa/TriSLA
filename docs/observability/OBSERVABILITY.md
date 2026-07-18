# Observability

TriSLA exposes application health, Prometheus metrics, and optional OTLP traces. The public chart also contains selected Prometheus Operator resources.

## Application endpoints

| Component | Port | Health | Metrics |
|---|---:|---|---|
| BC-NSSMF | `8083` | `/health`, `/health/ready` | `/metrics` |
| SLA-Agent Layer | `8084` | `/health` | `/metrics` |
| NASP Adapter | `8085` | `/health` | `/metrics` |
| Traffic Exporter | `9105` | `/health` | `/metrics` |

Other FastAPI services also expose `/health` and `/metrics` according to their module documentation.

## Metrics collection

The main Helm chart renders:

- the Traffic Exporter Deployment and Service;
- a ServiceMonitor for SEM-CSMF;
- a metrics Service for NASP Adapter;
- Prometheus recording rules used by the platform.

The Prometheus, Grafana, OpenTelemetry Collector, Jaeger, and Tempo workloads visible in the live environment are separate operational deployments. The main chart does not render those workloads.

## Traces

Instrumented services can export spans through OTLP. Export initialization is designed not to block service startup when the collector is unavailable. Trace storage and query interfaces depend on the separately deployed monitoring stack.

## Verification commands

```bash
kubectl get pods -n monitoring
kubectl get servicemonitors -n trisla
kubectl get prometheusrules -n trisla
```

For a service reachable through cluster networking, query `/health` before `/metrics`.

## References

- [Traffic Exporter source](../../apps/traffic-exporter/app/main.py)
- [Traffic Exporter Helm template](../../helm/trisla/templates/traffic-exporter.yaml)
- [Recording rules](../../helm/trisla/templates/prometheusrule-trisla-recording.yaml)
- [SEM-CSMF ServiceMonitor](../../helm/trisla/templates/servicemonitor-sem-csmf.yaml)
