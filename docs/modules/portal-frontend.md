# Portal Frontend

## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

Canonical interface reference: [docs/modules/interfaces.md](interfaces.md).

> Implementation SSOT: `apps/portal-frontend/`. Digest SSOT: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.
>
> Operational Entry Point. This document is the canonical Portal Frontend
> module reference after DOC-MOD-10. It reflects the real implementation,
> frozen runtime, approved evidence, and implementation-first responsibility
> split.


## Canonical Governance Reference

For the cross-module governance contract, use [`docs/modules/governance.md`](governance.md). Portal Frontend is the **Governance Visualization Layer**: it renders governance evidence and metadata, but does not generate them.

## Official Identity

Portal Frontend is the user-facing web interface for TriSLA workflows. Its
official responsibility is:

- User Interface Layer
- Workflow Visualization
- Decision Presentation
- Governance Visualization
- Runtime Visualization
- Frontend API Consumer

Portal Frontend does not decide SLA.

Portal Frontend does not produce governance.

Portal Frontend does not produce runtime assurance.

Portal Frontend does not produce explainability.

Portal Frontend does not produce telemetry.

It renders, gates, formats, and visualizes data received from Portal Backend and
its proxied API surface.

## Runtime Architecture Truth

Canonical runtime flow:

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

The only direct operational integration from Portal Frontend is:

```text
Frontend
|
Portal Backend
```

Portal Frontend does not call SEM-CSMF, Decision Engine, BC-NSSMF, or SLA-Agent
directly. Those modules are reached through Portal Backend and the frozen TriSLA
control-plane flow.

## Frontend Runtime Truth

| Runtime item | Classification | Evidence |
| --- | --- | --- |
| Next.js 15 App Router | ACTIVE | `apps/portal-frontend/src/app/**`, `package.json` |
| React 18 | ACTIVE | `package.json` |
| React Context | ACTIVE | `PortalNavProvider`, `usePortalNavContext` |
| `sessionStorage` | ACTIVE | Admission operational snapshot cache after submit |
| Zustand | NOT IMPLEMENTED | No runtime dependency or store implementation |

Portal Frontend uses client-side React state, React Context for navigation
context, and `sessionStorage` for an operational post-submit snapshot cache. The
official admission decision still comes from backend/status payloads, not from
session storage.

## Active Routes

| Route | Classification | Runtime view |
| --- | --- | --- |
| `/` | ACTIVE | Platform Overview |
| `/pnl` | ACTIVE | Natural Language SLA |
| `/template` | ACTIVE | Structured SLA |
| `/sla-lifecycle?view=admission` | ACTIVE | Admission Analysis |
| `/sla-lifecycle?view=runtime` | ACTIVE | Runtime Lifecycle |
| `/monitoring` | ACTIVE | Domain Analytics |
| `/administration` | ACTIVE | Administration |
| `/metrics` | AUXILIARY | Operational metrics helper, outside main menu |
| `/defense` | RESERVED | Active route, out of main menu, not hot path |

`/api/v1/[...path]` and `/nasp/[...path]` are Next.js server routes used as
backend proxy surfaces. They are not independent TriSLA control-plane modules.

## Navigation Runtime Truth

### Active Navigation Surface

```text
Sidebar
```

Main navigation entries:

```text
Overview
PNL
Template
Admission Analysis
Runtime Lifecycle
Domain Analytics
```

`Runtime Lifecycle` appears only when the current navigation context allows it:

```text
ACCEPT
or
runtime state known before final decision context is set
```

For `REJECT` and `RENEGOTIATE`, the UI remains admission-only and does not expose
runtime supervision as an active lifecycle path.

## API Consumption Runtime Truth

### Active Portal Backend APIs Consumed

```text
/api/v1/health/global
/api/v1/health
/api/v1/prometheus/summary
/api/v1/interfaces/*
/api/v1/modules/*
/api/v1/sla/interpret
/api/v1/sla/submit
/api/v1/sla/status/{id}
/api/v1/sla/revalidate-telemetry
/nasp/diagnostics
```

Frontend consumes Portal Backend.

Frontend does not call:

```text
SEM-CSMF
Decision Engine
BC-NSSMF
SLA-Agent
```

`NEXT_PUBLIC_TRISLA_API_BASE_URL`, `TRISLA_API_BASE_URL`, and `BACKEND_URL` only
select the Portal Backend root or proxy path. They do not authorize direct
module-to-module frontend calls.

## Governance Runtime Truth

| Field | Classification | Rendered through |
| --- | --- | --- |
| `tx_hash` | ACTIVE | `OnChainEvidenceDetails`, `BlockchainCommitCard`, `GovernancePanel` |
| `block_number` | ACTIVE | `OnChainEvidenceDetails`, `BlockchainCommitCard`, `GovernancePanel` |
| `bc_status` | ACTIVE | `BlockchainCommitCard`, `GovernancePanel`, status labels |
| `governance_registration_status` | ACTIVE | `GovernancePanel`, registration evidence panels |
| `lineage` | PARTIAL | Governance event, lifecycle timeline, auditability metadata, technical payload |

Portal Frontend visualizes governance. It does not produce governance evidence.
BC-NSSMF and upstream backend metadata remain the source of governance values.
This aligns with 10G.8 expectations for visible blockchain/governance evidence.

## Explainability Runtime Truth

| Field | Classification | Runtime behavior |
| --- | --- | --- |
| `decision_evidence` | ACTIVE | Rendered by `DecisionEvidencePanel`, Admission Overview, Why Rejected |
| `domain_compliance` | ACTIVE | Rendered by compliance/runtime panels |
| `domain_explainability` | ACTIVE | Parsed for per-domain/per-metric compliance views |
| `top_factors` | NOT IMPLEMENTED | Not consumed or rendered as a runtime field |
| `dominant_domain` | NOT IMPLEMENTED | Not consumed or rendered as a runtime field |
| `bottleneck_domain` | ACTIVE | Rendered as the active domain-level runtime indicator |

Portal Frontend presents explainability returned by backend/runtime payloads. It
does not generate explainability. This preserves the 6A, 6B, 6C, 6D, and 6E
explainability evidence boundary.

## Runtime Assurance Runtime Truth

| Field | Classification | Runtime view |
| --- | --- | --- |
| `violations` | ACTIVE | Runtime Assurance |
| `warnings` | ACTIVE | Runtime Assurance |
| `recommendation` | ACTIVE | Runtime Assurance |
| `drift_detected` | ACTIVE | Runtime Assurance |
| `bottleneck_domain` | ACTIVE | Runtime Assurance |
| `sla_compliance` | ACTIVE | Compliance Evaluation |
| `runtime_compliance` | ACTIVE | Compliance Evaluation |

Portal Frontend visualizes runtime assurance data received through Portal
Backend. It does not produce runtime assurance. This aligns with 10D, 10E, and
10F evidence expectations.

## Lifecycle Runtime Truth

| Admission decision | Frontend behavior |
| --- | --- |
| ACCEPT | Runtime Lifecycle Enabled |
| REJECT | Admission Only |
| RENEGOTIATE | Admission Only |

For `REJECT`, the UI renders `Why Rejected` and admission-time decision evidence.
For `RENEGOTIATE`, the UI renders `Renegotiation Proposal`. Runtime supervision
is gated by `ACCEPT`, preserving the 10C and 10D lifecycle boundary.

## Implemented But Not Hot Path

| Component | Classification |
| --- | --- |
| `SubmitResultPanelsF2` | IMPLEMENTED, NOT HOT PATH |
| `RuntimeSupervisionSection` | IMPLEMENTED, NOT HOT PATH |
| `RuntimeSupervisionPanels` | IMPLEMENTED, NOT HOT PATH |
| `DomainExplainabilityPanel` | IMPLEMENTED, NOT HOT PATH |

These components exist in the source tree but are not the canonical rendered
hot path for the current operational workflow. Documentation must not promote
them as primary runtime screens unless the implementation changes.

## Observability Runtime Truth

Portal Frontend renders observability data consumed from Portal Backend:
platform health, Prometheus summary, interface metrics, module metrics, and NASP
diagnostics. For the system-level observability contract, see:

```text
docs/modules/observability.md
```

## Telemetry Runtime Truth

Portal Frontend displays telemetry snapshots and domain analytics returned by
Portal Backend. It does not collect or produce telemetry. For the telemetry
module contract, see:

```text
docs/modules/telemetry.md
```

## Implementation and Evidence Alignment

This document aligns Portal Frontend with the frozen runtime and evidence chain:

- Portal Frontend is the UI and API consumer layer.
- Portal Backend is the only direct operational integration target.
- Next.js App Router routes are the active routing truth.
- Runtime Lifecycle is gated by accepted admission state.
- Governance, explainability, telemetry, and runtime assurance are displayed as
  propagated data, not generated by the frontend.
- Phase 47, Results Freeze, Runtime Freeze, 6A-6E, 10C, 10D-10F, and 10G.8
  alignment is preserved because this page changes documentation only.

## Documentation Boundaries

- Canonical operational module document: `docs/modules/portal-frontend.md`.
- Portal Frontend navigation hub: `docs/portal/frontend/README.md`.
- Portal architecture reference: `docs/portal/architecture/portal_architecture.md`.

Do not create new `runtime/`, `governance/`, `baseline/`, `freeze/`, or
`operational/` document trees for this module.
