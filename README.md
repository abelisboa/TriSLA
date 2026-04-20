# TriSLA: SLA-Aware Architecture for 5G/O-RAN Networks with AI, XAI, and Blockchain

Initial Public Release (v1.0.0)

## Overview

TriSLA is an SLA-aware architecture for 5G/O-RAN networks that integrates Artificial Intelligence (AI), Explainable AI (XAI), and blockchain technologies to enable trustworthy, transparent, and automated SLA validation and enforcement.

The architecture evaluates SLA feasibility before deployment by analyzing multi-domain resource availability across RAN, Transport, and Core, while supporting real-time orchestration and continuous observability.

## Scientific Positioning

### Research Problem

SLA feasibility validation at request time remains difficult in 5G/O-RAN environments due to dynamic multi-domain resources, fragmented orchestration paths, and limited trust mechanisms for decision governance.

### Why Existing Approaches Are Insufficient

Common SLA pipelines are typically reactive, domain-isolated, or non-explainable. They often do not combine predictive AI, policy-governed control, explainability, and immutable auditing in one coherent lifecycle.

### TriSLA Contribution

- **AI (`ML-NSMF`)** for predictive SLA feasibility estimation.
- **XAI (`Decision Engine`)** for interpretable decision outputs.
- **Blockchain (`BC-NSSMF`)** for immutable SLA governance evidence.
- **Semantic reasoning (`SEM-CSMF`)** for intent-to-technical mapping.
- **Real orchestration (`NASP Adapter`)** for multi-domain execution.

## Architecture Overview

The reference architecture is documented in `docs/architecture/trisla_architecture.md`.

Core modules:

- `SEM-CSMF`
- `ML-NSMF`
- `Decision Engine`
- `NASP Adapter`
- `SLA-Agent Layer`
- `BC-NSSMF`
- `Portal Backend`

## End-to-End Flow

Canonical E2E flow:

**Tenant → SEM-CSMF → ML-NSMF → Decision Engine → NASP Adapter → NASP → Core → SLA-Agent → BC-NSSMF**

ASCII equivalent:

`Tenant -> SEM-CSMF -> ML-NSMF -> Decision Engine -> NASP Adapter -> NASP -> Core -> SLA-Agent -> BC-NSSMF`

Decision states are standardized as: `ACCEPT`, `REJECT`, `RENEGOTIATE`.

## Modules

Detailed module documentation is available in:

- `docs/modules/README.md`
- `docs/modules/sem-csmf.md`
- `docs/modules/ml-nsmf.md`
- `docs/modules/decision-engine.md`
- `docs/modules/nasp-adapter.md`
- `docs/modules/sla-agent-layer.md`
- `docs/modules/bc-nssmf.md`
- `docs/modules/portal-backend.md`

## NASP Integration

The NASP integration model (RAN, Transport, Core, telemetry, orchestration boundary) is documented in:

- `docs/infrastructure/nasp_integration.md`

## Reproducibility

Reproducible setup and validation steps are documented in:

- `docs/reproducibility/setup_guide.md`

## Documentation Structure

- `docs/architecture/` — architecture and E2E system model.
- `docs/modules/` — module-level technical behavior.
- `docs/infrastructure/` — NASP integration and domain coupling.
- `docs/reproducibility/` — setup, deploy, and validation guidance.
- `docs/development/` — runbook references and governance boundaries.

## License

Apache License 2.0.
