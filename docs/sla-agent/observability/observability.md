# SLA-Agent Observability

## Health

`GET /health` returns the service status and the health of the RAN, transport, and core agents. Helm uses this endpoint for both liveness and readiness.

## Metrics

`GET /metrics` returns Prometheus text format. The FastAPI middleware records HTTP request counts and request duration.

`GET /api/v1/metrics/realtime` is an application API, not a Prometheus scrape endpoint. It collects current values from all three domain agents and returns an aggregate JSON response.

## Traces

The application instruments FastAPI requests and can export traces through OTLP. Trace export is non-blocking: failure to initialize the exporter does not prevent the API from starting.

## Operational checks

```bash
curl http://trisla-sla-agent-layer:8084/health
curl http://trisla-sla-agent-layer:8084/metrics
```

## References

- [Application entrypoint](../../../apps/sla-agent-layer/src/main.py)
- [Metric definitions](../../../apps/sla-agent-layer/src/observability/metrics.py)
- [Deployment template](../../../helm/trisla/templates/deployment-sla-agent-layer.yaml)
