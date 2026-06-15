# Portal Architecture Reference

This page is an architecture reference for the Portal layer. It is not the
operational SSOT for either frontend or backend module behavior.

Canonical module documents:

```text
docs/modules/portal-frontend.md
docs/modules/portal-backend.md
```

## Portal Layer

The Portal layer contains:

1. Portal Frontend: user interface, workflow visualization, and frontend API consumer.
2. Portal Backend: ingress, orchestration relay, response aggregation, and metadata propagation.

## Runtime Flow

```text
Frontend
|
Portal Backend
|
SEM-CSMF
|
Decision Engine
|
BC-NSSMF
|
SLA-Agent
|
Frontend
```

The frontend directly integrates only with Portal Backend. The backend integrates
with the TriSLA control-plane modules according to the canonical runtime flow.

## Documentation Boundaries

Use this page only for the high-level portal architecture summary. Route-level,
field-level, governance, explainability, telemetry, and runtime assurance truth
belong in the canonical module documents.
