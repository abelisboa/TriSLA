# TriSLA: An SLA-Aware Architecture Based on AI, Ontology, and Smart Contracts for SLA Assurance in 5G/O-RAN Networks

TriSLA is an SLA (Service Level Agreement)-aware architecture that integrates AI (Artificial Intelligence), ontology-based reasoning, and smart contracts to support trustworthy SLA admission control and assurance in 5G/O-RAN environments.

## 1. Quick Start

For installation and deployment steps, use:

- `docs/INSTALLATION.md`

## 2. Overview

TriSLA addresses the problem of evaluating SLA feasibility at request time under dynamic multi-domain conditions. The platform combines semantic interpretation, predictive intelligence, and policy-driven decisions to determine whether requested service guarantees can be admitted and maintained.

TriSLA also incorporates XAI (Explainable Artificial Intelligence) outputs to make model-driven decisions interpretable for operators and researchers.

TriSLA works across network domains including RAN (Radio Access Network), Transport, and Core, and integrates with NASP (Network Automation and Service Platform) for infrastructure-facing actions.

## 3. Architecture

Canonical pipeline:

`SEM-CSMF → ML-NSMF → Decision Engine → NASP Adapter → BC-NSSMF → SLA-Agent`

Architecture reference:

- `docs/ARCHITECTURE.md`

## 4. Core Modules

| Module | Documentation |
|--------|-------------|
| SEM-CSMF | `docs/sem-csmf/` |
| ML-NSMF | `docs/ml-nsmf/` |
| Decision Engine | `docs/decision-engine/` |
| NASP Adapter | `docs/nasp-adapter/` |
| BC-NSSMF | `docs/bc-nssmf/` |
| SLA-Agent | `docs/sla-agent/` |
| Portal | `docs/portal/` |

## 5. Observability

Observability uses Prometheus and OpenTelemetry (OTEL - OpenTelemetry) to expose runtime metrics and traces for pipeline validation, correlation tracking, and operational diagnostics.

Observability reference:

- `docs/observability/OBSERVABILITY.md`

## 6. Reproducibility

Reproducibility guidance is documented in:

- `docs/reproducibility/REPRODUCIBILITY.md`

## 7. Deployment Model

TriSLA uses Kubernetes (container orchestration platform) as the runtime environment and Helm (Kubernetes package manager) for release management and repeatable deployments.

Container images are consumed from GHCR using chart-managed image references.

## 8. Documentation Structure

Module documentation follows a domain-first layout and standardized internal sections such as:

- `docs/<module>/architecture/`
- `docs/<module>/interfaces/`
- `docs/<module>/pipeline/`

This structure keeps conceptual design, contracts, and runtime flow documentation separated but consistent.

## 9. Design Principles

- SLA-aware decision-making
- Multi-domain intelligence
- XAI (Explainable Artificial Intelligence)
- Reproducibility
- Separation of concerns

## 10. Scope

### What TriSLA does

- Evaluates SLA admission feasibility using semantic, predictive, and policy inputs
- Integrates multi-domain telemetry and infrastructure actions
- Provides explainable decision support and auditable lifecycle evidence

### What TriSLA does not do

- Simulate the full network data plane
- Replace external orchestration platforms
- Expose private infrastructure internals in public documentation

## 11. Author

Abel Lisboa

## 12. Status

- [x] Canonical installation guide in place (`docs/INSTALLATION.md`)
- [x] Canonical architecture guide in place (`docs/ARCHITECTURE.md`)
- [x] Observability documentation consolidated (`docs/observability/OBSERVABILITY.md`)
- [x] Reproducibility documentation consolidated (`docs/reproducibility/REPRODUCIBILITY.md`)
- [x] Module documentation organized by domain
