# Portal Backend Developer Reference

This file is a developer reference for the Portal Backend implementation. It is
not the operational SSOT.

Canonical operational documentation lives at:

```text
docs/modules/portal-backend.md
```

## Scope

Use this README for local development orientation only. Runtime truth,
authority boundaries, active API classification, governance, admission, runtime
assurance, explainability, persistence, and evidence alignment are defined in
the canonical module document.

## Official Runtime Role

Portal Backend provides:

- Ingress
- Orchestration relay
- Response aggregation
- Metadata propagation
- Frontend backend API layer

Portal Backend does not decide SLA, does not execute admission logic, does not
produce governance, and does not produce runtime assurance.

## Canonical Admission Path

```text
Frontend
|
Portal Backend
|
SEM-CSMF
|
Decision Engine (internal orchestration)
|
SEM-CSMF
|
Portal Backend
|
Frontend
```

Portal Backend does not call `/evaluate` as the canonical admission path.

## Active API Groups

The public runtime API surface is the set mounted by
`apps/portal-backend/src/main.py`:

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

Implemented routers that are not mounted by `main.py` are not public APIs.

## Local Development Notes

Common local development tasks may include installing dependencies, running the
FastAPI application, and exercising mounted routes. Keep local scripts and
port-forward instructions subordinate to the canonical runtime documentation.
Do not use this file to redefine module authority, deployment truth, or SSOT
state.

## References

- Canonical module document: `docs/modules/portal-backend.md`
- Navigation hub: `docs/portal/backend/README.md`
- Observability module: `docs/modules/observability.md`
