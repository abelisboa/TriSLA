# Portal Backend Module

## Overview

Portal Backend is the API gateway and orchestration entrypoint between user-facing requests and the TriSLA core pipeline.

## Core Responsibilities

- Validate and normalize SLA submission payloads
- Route requests through semantic interpretation and decision workflow
- Aggregate module outcomes into a unified response contract
- Expose status and metrics endpoints for lifecycle visibility

## Main SLA Endpoints

- `POST /api/v1/sla/interpret`
- `POST /api/v1/sla/submit`
- `GET /api/v1/sla/status/{sla_id}`
- `GET /api/v1/sla/metrics/{sla_id}`

## Functional Boundaries

Portal Backend does not:

- interpret intent semantics (SEM-CSMF)
- perform risk prediction (ML-NSMF)
- enforce blockchain contracts (BC-NSSMF)
- execute domain actions (SLA-Agent / NASP Adapter)

It orchestrates and exposes results.

## Formal Gateway View

`S = f(U)` maps user inputs `U` to structured SLA submission `S`.

`Y = g(S, module_outputs)` returns a unified response with decision, branch status, and lifecycle evidence.

## References

- `docs/portal/README.md`
- `docs/portal/architecture/portal_architecture.md`
- `docs/portal/model/interaction_model.md`
- `docs/portal/experimental/workload_injection.md`
