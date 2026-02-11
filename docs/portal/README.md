# TriSLA Portal

This folder documents the public Portal components used to submit SLA requests and visualize outcomes.

## Components
- **Portal Backend** — REST API gateway for SLA submissions
- **Portal Frontend** — UI for operators and evaluators

## API endpoints (backend)

The Portal Backend exposes the following under prefix **`/api/v1/sla`** (singular):

- `POST /api/v1/sla/interpret` — PLN interpretation
- `POST /api/v1/sla/submit` — Full pipeline (SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF → SLA-Agent)
- `GET /api/v1/sla/status/{sla_id}` — SLA status
- `GET /api/v1/sla/metrics/{sla_id}` — SLA metrics (latency_ms, jitter_ms, throughput_ul/dl, timestamps)

The frontend calls these via same-origin `/api/v1` (e.g. `/api/v1/sla/metrics/{id}`). Do not use `/api/v1/slas/*` (plural); the backend does not expose that path.

## Metrics and charts

- Metrics page: `/slas/metrics?id={sla_id}`. Data comes from the backend (SLA-Agent Layer). When no data is available, cards show **"Dados ainda em coleta"** (never a blank chart).
- Latency, Jitter, and Throughput cards are always visible; each shows either a time-series chart or the fallback message.

## XAI (explainable decision)

- The decision result (including XAI) is returned in the `POST /api/v1/sla/submit` response (fields `xai`, `confidence`, `explanation`).
- The frontend stores the full result in sessionStorage and redirects to `/slas/result`. The result page always shows an **XAI block** when a result exists; if no explanation is provided, it shows "Explicação não disponível para esta decisão."

## Typical flow
1. User submits a SLA request via the Portal UI
2. Portal Backend forwards the request to the Decision Engine pipeline
3. The decision outcome (including XAI) is returned and displayed in the UI; metrics are available at `/slas/metrics?id={sla_id}`
