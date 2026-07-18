# NASP Adapter

The NASP Adapter connects TriSLA to Kubernetes network-slice resources, core-network services, RAN and transport observations, and platform telemetry.

## Service

- Framework: FastAPI 3.10.0
- HTTP port: `8085`
- Container entry point: `src.main:app`
- Kubernetes service: `trisla-nasp-adapter`

## Primary API groups

| Prefix | Purpose |
|---|---|
| `/api/v1/nsi` | Network Slice Instance creation |
| `/api/v1/nasp` | NASP metrics and actions |
| `/api/v1/sla` | SLA registration |
| `/api/v1/3gpp` | Core and RAN readiness checks |
| `/api/v1/slice-service-binding` | Slice-to-service resolution and observations |

Health is available at `GET /health`; Prometheus output is available at `GET /metrics`.

See the [NASP Adapter documentation](../../docs/nasp-adapter/README.md) for routes, integration behavior, and configuration.

## Source

- [FastAPI application](src/main.py)
- [NASP client](src/nasp_client.py)
- [NSI controller](src/controllers/nsi_controller.py)
- [Metrics collector](src/metrics_collector.py)
- [Action executor](src/action_executor.py)
