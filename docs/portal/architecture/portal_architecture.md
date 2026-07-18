# Portal Architecture

## Request flow

```text
Browser
    ▼
Next.js Portal Frontend
    │ /api/v1/* and /nasp/* proxy
    ▼
FastAPI Portal Backend
    ├── SEM-CSMF
    ├── ML-NSMF
    ├── Decision Engine
    ├── BC-NSSMF
    ├── SLA-Agent Layer
    ├── NASP Adapter
    └── Prometheus
```

## Portal Frontend

The frontend uses the Next.js App Router. Browser requests use the same-origin proxy unless `NEXT_PUBLIC_TRISLA_API_BASE_URL` is configured. Server-side requests use `TRISLA_API_BASE_URL` or `BACKEND_URL`, with `http://trisla-portal-backend:8001` as the service default.

The implemented user pages cover platform overview, free-form SLA entry, structured templates, admission and runtime views, monitoring, and administration.

## Portal Backend

The backend mounts four public route groups:

- SLA operations under `/api/v1/sla`
- module status under `/api/v1/modules`
- Prometheus access under `/api/v1/prometheus`
- domain interface metrics under `/api/v1/interfaces`

The SLA submission path validates the portal payload, obtains pre-decision telemetry, coordinates the platform services, and returns a unified response.

## Deployment

The frontend application, container, liveness probe, and readiness probe use port `3000`. Its NodePort service publishes port `80`, forwards to target port `3000`, and uses NodePort `32001`. The backend service uses port `8001`; its health probe uses `/health`, and its readiness probe uses `/nasp/diagnostics`.

Source references: [frontend API client](../../../apps/portal-frontend/src/lib/api.ts) and [backend application](../../../apps/portal-backend/src/main.py).
