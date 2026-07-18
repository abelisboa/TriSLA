# Observability Module

TriSLA uses health endpoints, Prometheus-format metrics, and OTLP trace export to expose runtime state without changing service decisions.

## Public surfaces

- `/health` on application services;
- `/metrics` on instrumented services;
- Traffic Exporter on port `9105`;
- Prometheus Operator resources rendered by the main chart;
- trace export to a configured OTLP collector.

The main chart deploys the Traffic Exporter and selected metrics discovery resources. Prometheus, Grafana, the OpenTelemetry Collector, Jaeger, and Tempo are operated separately in the current environment.

## Boundaries

Health endpoints report component readiness or dependencies. Metrics endpoints use Prometheus text format. OTLP export failure does not replace application health checks and should not prevent the API process from starting.

## References

- [Observability guide](../observability/OBSERVABILITY.md)
- [Traffic Exporter](../../apps/traffic-exporter/README.md)
- [Helm recording rules](../../helm/trisla/templates/prometheusrule-trisla-recording.yaml)
