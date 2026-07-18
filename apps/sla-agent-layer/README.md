# SLA-Agent Layer

The SLA-Agent Layer coordinates RAN, transport, and core agents, evaluates runtime SLA state, exposes domain metrics, and manages the actuation request lifecycle.

## Runtime

| Item | Value |
|---|---|
| FastAPI version | `3.11.0` |
| Service | `trisla-sla-agent-layer` |
| Kubernetes type | `ClusterIP` |
| Port | `8084` |
| Health | `GET /health` |
| Metrics | `GET /metrics` |

The health response reports the state of all three domain agents. The live Helm configuration uses `/health` for both liveness and readiness.

## Capabilities

- collect RAN, transport, and core metrics;
- return aggregate real-time metrics and configured SLO evaluation;
- coordinate actions across selected domains;
- evaluate runtime SLA state from telemetry snapshots;
- receive pipeline events and revalidation requests;
- create, authorize, execute, verify, roll back, expire, and list actuation records.

The deployed configuration keeps closed-loop domain mutation disabled by default. Actuation APIs remain available for controlled request-state handling.

## References

- [Application entrypoint](src/main.py)
- [Agent coordinator](src/agent_coordinator.py)
- [Public SLA-Agent documentation](../../docs/sla-agent/README.md)
- [Helm Deployment](../../helm/trisla/templates/deployment-sla-agent-layer.yaml)
