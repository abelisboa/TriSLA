# TriSLA: SLA-Aware Architecture for 5G/O-RAN Networks with AI, XAI, and Blockchain

Initial Public Release (v1.0.0)

## Overview

TriSLA is an SLA-aware architecture for 5G/O-RAN networks that integrates Artificial Intelligence (AI), Explainable AI (XAI), and blockchain technologies to enable trustworthy, transparent, and automated SLA validation and enforcement.

The architecture evaluates SLA feasibility before deployment by analyzing multi-domain resource availability across RAN, Transport, and Core domains, while supporting real-time orchestration through NASP and continuous observability.

## Scientific Positioning

TriSLA addresses a critical challenge in 5G/O-RAN systems: validating SLA feasibility at request time under dynamic, multi-domain constraints. Existing approaches are often reactive, weakly explainable, or not auditable end-to-end. TriSLA combines predictive intelligence, explainable decision logic, and immutable governance evidence in a single SLA-aware architecture.

## Architecture

<!-- Architecture image path should be enabled once the PNG is available in the public docs tree. -->
<!-- ![TriSLA Architecture](docs/architecture/trisla_architecture.png) -->

See architecture details in `docs/architecture/trisla_architecture.md`.

### Components

| Component | Description |
|----------|------------|
| SEM-CSMF | Semantic interpretation and SLA intent processing |
| ML-NSMF | Machine learning-based SLA risk prediction |
| Decision Engine | Policy-governed SLA decision (ACCEPT / REJECT / RENEGOTIATE) with XAI |
| NASP Adapter | Integration with NASP orchestration layer |
| SLA-Agent Layer | SLA lifecycle monitoring and telemetry ingestion |
| BC-NSSMF | Blockchain-based SLA registration and auditing |
| Portal Backend | API orchestration and workflow coordination |

## End-to-End Flow

Tenant → SEM-CSMF → ML-NSMF → Decision Engine → NASP Adapter → NASP → Core → SLA-Agent Layer → BC-NSSMF

## Modules

Detailed module documentation is available in:

`docs/modules/`

## NASP Integration

TriSLA integrates with NASP to orchestrate network slice deployment across RAN, Transport, and Core domains.

## Reproducibility

See:

`docs/reproducibility/`

## Documentation structure

- `docs/architecture/` — architecture model and system flow
- `docs/modules/` — module-level technical documentation
- `docs/infrastructure/` — NASP integration model
- `docs/reproducibility/` — setup and validation guidance
- `docs/development/` — runbook references and governance boundaries

## License

Apache License 2.0.
