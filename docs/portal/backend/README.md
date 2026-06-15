# Portal Backend Navigation Hub

This README is a navigation hub for Portal Backend documentation. It is not the
operational SSOT. The canonical operational module reference is:

```text
docs/modules/portal-backend.md
```

## Runtime Identity

Portal Backend is the frontend-facing API layer for TriSLA. It provides:

- Ingress
- Orchestration relay
- Response aggregation
- Metadata propagation
- Frontend backend API layer

Portal Backend does not decide SLA, does not produce governance, and does not
produce runtime assurance.

## Canonical Flow

```text
Frontend
|
Portal Backend
|
SEM-CSMF
|
Decision Engine
|
Portal Backend
|
BC-NSSMF
|
SLA-Agent
|
Frontend
```

Portal Backend calls SEM-CSMF in the canonical admission path. Decision Engine
is reached indirectly through SEM-CSMF internal orchestration.

## Active API Groups

Only APIs mounted by `apps/portal-backend/src/main.py` are public runtime APIs:

```text
/api/v1/sla/*
/api/v1/modules/*
/api/v1/prometheus/*
/api/v1/interfaces/*
/health
/api/v1/health
/api/v1/health/global
/metrics
/nasp/diagnostics
```

Routers such as `contracts`, `health`, `intents`, `loki`, `slas`, `slos`,
`tempo`, and `xai` may exist in the codebase, but they are not public Portal
Backend APIs unless mounted by `main.py`.

## References

- Canonical module document: `docs/modules/portal-backend.md`
- Observability module: `docs/modules/observability.md`
- Runtime/architecture SSOT references: `MASTER_SSOT_POINTER.md`,
  `docs/TRISLA_MASTER_RUNBOOK.md`, `docs/TRISLA_INFRA_SSOT.md`,
  `docs/TRISLA_E2E_FLOW_CANONICAL.md`
- Developer reference: `apps/portal-backend/README_BACKEND.md`
