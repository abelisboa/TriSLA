# Portal Frontend

The Portal Frontend is a Next.js application that presents platform health, SLA creation, admission results, runtime status, and domain telemetry.

## User pages

| Path | Purpose |
|---|---|
| `/` | Platform overview |
| `/pnl` | Free-form SLA entry |
| `/template` | Structured SLA entry |
| `/sla-lifecycle?view=admission` | Admission result |
| `/sla-lifecycle?view=runtime` | Runtime lifecycle for accepted SLAs |
| `/monitoring` | Domain telemetry |
| `/administration` | Platform administration view |

`/metrics` redirects to `/monitoring`; `/defense` redirects to `/`.

## Backend communication

The frontend proxies `/api/v1/*` and `/nasp/*` to the Portal Backend. Browser calls use same-origin paths by default.

Configuration precedence:

1. Browser override: `NEXT_PUBLIC_TRISLA_API_BASE_URL`
2. Server override: `TRISLA_API_BASE_URL`
3. Server service URL: `BACKEND_URL`
4. Default: `http://trisla-portal-backend:8001`

The request timeout used by the shared API client is 30 seconds. Optional dashboard data may be shown as unavailable without blocking the rest of the page.

## Runtime

The Next.js standalone server and container listen on port `3000`. Kubernetes liveness and readiness probes use port `3000`. The service publishes port `80`, forwards to target port `3000`, and uses NodePort `32001`.

## Source

- [API client](../../../apps/portal-frontend/src/lib/api.ts)
- [Endpoint catalog](../../../apps/portal-frontend/src/lib/endpoints.ts)
- [API proxy](../../../apps/portal-frontend/src/app/api/v1/%5B...path%5D/route.ts)
- [Navigation](../../../apps/portal-frontend/src/components/layout/Sidebar.tsx)
