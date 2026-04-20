# TriSLA Architecture (SSOT)

TriSLA implements a distributed, SLA-aware architecture for network slice admission control in 5G/O-RAN environments.

---

## 1. Architectural Overview

TriSLA follows a modular pipeline architecture:

SEM-CSMF → ML-NSMF → Decision Engine → NASP Adapter → BC-NSSMF → SLA-Agent

---

## 2. Design Principles

- SLA-aware decision making
- Multi-domain observability (RAN, Transport, Core)
- Explainability (XAI)
- Reproducibility
- Separation of concerns

---

## 3. Core Components

### SEM-CSMF
- Semantic interpretation of SLA intents
- Ontology-based reasoning
- Generates structured SLA requirements

---

### ML-NSMF
- Predicts SLA feasibility risk
- Outputs risk_score and confidence
- Supports XAI explanations

---

### Decision Engine
- Final SLA admission decision
- Combines:
  - ML output
  - real-time metrics
  - policy constraints

Outputs:
- ACCEPT / REJECT / RENEGOTIATE

---

### NASP Adapter
- Integration layer with infrastructure
- Provides normalized metrics
- Abstracts RAN / Transport / Core

---

### BC-NSSMF
- Blockchain-based SLA registration
- Ensures immutability and auditability
- Uses Hyperledger Besu

---

### SLA-Agent Layer
- Lifecycle orchestration
- SLA compliance monitoring
- Multi-domain action coordination

---

## 4. Domain Model

TriSLA operates over three domains:

| Domain | Role |
|------|------|
| RAN | latency, jitter, PRB |
| Transport | throughput, packet loss |
| Core | CPU, memory, availability |

---

## 5. Data Flow

### Request Flow

Portal → SEM-CSMF → ML-NSMF → Decision Engine

---

### Execution Flow

Decision Engine → BC-NSSMF → SLA-Agent → NASP Adapter

---

### Observability Flow

All modules → Prometheus / OpenTelemetry

---

## 6. Communication Patterns

| Type | Protocol | Usage |
|------|--------|------|
| Synchronous | REST | SLA submission |
| Asynchronous | Kafka | events |
| Blockchain | JSON-RPC | SLA registration |

---

## 7. Observability Integration

TriSLA integrates:

- Prometheus (metrics)
- OpenTelemetry (traces)
- Grafana (optional)

See:
→ observability/OBSERVABILITY.md

---

## 8. Deployment Model

- Kubernetes-based
- Helm-managed
- Containerized services
- GHCR images (digest-based)

See:
→ INSTALLATION.md

---

## 9. Reproducibility

TriSLA supports:

- deterministic deployment
- traceable execution
- experimental validation

See:
→ reproducibility/REPRODUCIBILITY.md

---

## 10. Scope and Boundaries

TriSLA:

✔ decides SLA admission  
✔ integrates multi-domain metrics  
✔ provides explainability  

TriSLA does NOT:

✖ simulate network  
✖ replace orchestration platforms  
✖ expose internal infrastructure details  

