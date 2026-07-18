# TriSLA Portal

The TriSLA Portal provides a web interface and an HTTP gateway for submitting SLA requests, viewing admission results, checking platform health, and inspecting runtime telemetry.

## Components

| Component | Runtime | Role |
|---|---|---|
| Portal Frontend | Next.js | Browser interface and same-origin API proxy |
| Portal Backend | FastAPI on `8001` | SLA gateway, status API, and service coordination |

The frontend proxies `/api/v1/*` and `/nasp/*` requests to the backend. The backend calls SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer, NASP Adapter, and Prometheus as required by each operation.

## User workflow

1. Enter free-form SLA text or select a structured template.
2. Review the interpreted service type and SLA requirements.
3. Submit the SLA for admission.
4. Review the decision, reasoning, service status, and telemetry.
5. For accepted SLAs, inspect runtime lifecycle information and request telemetry revalidation when needed.

## Documentation

- [Portal Backend API](backend/README.md)

## Implementation

- [Portal Backend](../../apps/portal-backend/src/main.py)
- [Portal Frontend](../../apps/portal-frontend/src/app/page.tsx)
