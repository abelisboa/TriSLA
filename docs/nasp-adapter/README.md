# NASP Adapter — Documentation Index

Integration and orchestration layer connecting TriSLA to Kubernetes, Free5GC, Prometheus, and multidomain infrastructure.

## Operational reference

**[`docs/modules/nasp-adapter.md`](../modules/nasp-adapter.md)** — REST catalog, runtime paths, digest pin, integrations, capacity accounting, env vars.

Use that document for operations, integration, and freeze alignment. This directory holds specialized references only.

## Documentation map

| Directory | Content |
|-----------|---------|
| [`architecture/`](architecture/nasp_adapter_architecture.md) | Components, K8s CRDs, background services |
| [`integration/`](integration/nasp_integration.md) | Free5GC, Prometheus, Portal, SEM, K8s |
| [`interfaces/`](interfaces/interfaces.md) | REST ingress and caller contracts |
| [`model/`](model/metric_normalization_model.md) | MDCE / multidomain metric model |
| [`observability/`](observability/observability.md) | Prometheus, OTEL, PRB, MDCE |

## Scope boundary

NASP Adapter **does not** perform SLA admission. Decision authority remains in the Decision Engine (via SEM-CSMF); on-chain registration is handled by BC-NSSMF after successful orchestration.

Implementation: `apps/nasp-adapter/src/`
