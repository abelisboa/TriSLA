# Portal Backend

The Portal Backend is the HTTP gateway used by the TriSLA web application. It validates portal requests, coordinates SLA submission, exposes service and telemetry status, and forwards work to the platform services.

## Service

- Framework: FastAPI 1.0.2
- HTTP port: `8001`
- Container entry point: `src.main:app`
- Kubernetes service: `trisla-portal-backend`

## Primary API groups

| Prefix | Purpose |
|---|---|
| `/api/v1/sla` | Interpret, submit, inspect, and revalidate SLAs |
| `/api/v1/modules` | Platform module status and metrics |
| `/api/v1/prometheus` | Prometheus queries and summaries |
| `/api/v1/interfaces` | RAN, transport, and core interface metrics |

Service health is available at `GET /health`; platform-wide health is available at `GET /api/v1/health/global`; Prometheus output is available at `GET /metrics`.

See the [Portal Backend documentation](../../docs/portal/backend/README.md) for the complete client route table and request examples.

## Source

- [FastAPI application](src/main.py)
- [SLA routes](src/routers/sla.py)
- [SLA schemas](src/schemas/sla.py)
- [Service configuration](src/config.py)
- [NASP client service](src/services/nasp.py)
