# SLA-Agent Layer Module

The SLA-Agent Layer coordinates RAN, transport, and core agents and provides runtime SLA evaluation, domain metrics, pipeline integration, and actuation record management.

## Public contract

| Item | Value |
|---|---|
| Service | `trisla-sla-agent-layer` |
| Port | `8084` |
| Health and probes | `/health` |
| Prometheus metrics | `/metrics` |

The service reports each domain agent in its health response. The deployed service is available only through the cluster service unless another component proxies it.

## Main operations

- collect and aggregate domain telemetry;
- evaluate SLO and runtime state;
- coordinate selected domain agents;
- ingest lifecycle events and revalidate telemetry;
- manage actuation request states;
- expose health, metrics, and OpenAPI.

## References

- [SLA-Agent documentation](../sla-agent/README.md)
- [Application source](../../apps/sla-agent-layer/src/main.py)
- [Helm Deployment](../../helm/trisla/templates/deployment-sla-agent-layer.yaml)
