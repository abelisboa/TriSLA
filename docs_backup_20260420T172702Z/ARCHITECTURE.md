# TriSLA Architecture — SLA-Aware Decision and Validation Framework for 5G/O-RAN

## 1. Overview

TriSLA is a distributed architecture designed to evaluate the feasibility of Service Level Agreements (SLAs) in multi-domain 5G/O-RAN environments.

The architecture integrates semantic interpretation, machine learning, policy-based decision-making, blockchain registration, and runtime validation.

---

## 2. Research Problem Alignment

The architecture directly addresses the research question:

"How to determine, at SLA request time, whether sufficient resources will remain available across RAN, Transport, and Core domains during the lifecycle of a network slice?"

TriSLA answers this question through:

- Multi-domain observability
- Predictive modeling (ML-NSMF)
- Policy-governed decision logic (Decision Engine)
- Runtime validation (SLA-Agent)
- Real infrastructure integration (NASP Adapter)

---

## 3. Architectural Layers and Components

TriSLA is structured into seven logical layers.

### 3.1 Interaction Layer (Portal)

Components:

- Portal Frontend
- Portal Backend (API Gateway)

Function:

- Captures user input
- Standardizes SLA submission payloads
- Displays decision/lifecycle/metrics/XAI outputs

### 3.2 Semantic Layer (SEM-CSMF)

Components:

- Intent Processor
- NLP Parser
- Ontology Loader + Semantic Reasoner
- NEST Generator

Function:

- Transforms high-level intent into formal SLA/NEST representation

### 3.3 Prediction Layer (ML-NSMF)

Components:

- Feature extraction/preprocessing
- Feasibility model inference
- Explainability (SHAP/LIME or equivalent)

Function:

- Estimates SLA feasibility and prediction confidence

Output:

- Viability score
- Confidence
- Explanation (XAI)

### 3.4 Decision Layer (Decision Engine)

Components:

- Policy evaluator
- Threshold/decision function
- Decision publisher

Function:

- Combines policy rules, ML prediction, and runtime telemetry

Output:

- ACCEPT
- REJECT
- RENEGOTIATE

### 3.5 Trust Layer (BC-NSSMF)

Components:

- Web3/contract service
- Smart contract executor
- Blockchain connector (Besu)

Function:

- Registers accepted SLA outcomes on-chain for auditability and immutability

### 3.6 Execution and Validation Layer (SLA-Agent)

Components:

- Action consumer (event-driven)
- Domain agents (RAN, Transport, Core)
- SLO evaluator
- Event producer

Function:

- Executes SLA-related actions
- Monitors compliance over time
- Detects risk/violations

### 3.7 Infrastructure Integration Layer (NASP Adapter)

Components:

- REST integration API
- Metrics collector and normalization layer
- Action executor
- NSI integration controller

Function:

- Collects real metrics
- Executes real network actions
- Normalizes heterogeneous multi-domain data

---

## 4. Architecture Tree (Official)

```text
[User]
   |
   v
[Portal Frontend]
   |
   v
[Portal Backend/API Gateway]
   |
   v
-------------------- TriSLA Core --------------------
   |
   +--> [SEM-CSMF] ------+
   |                     |
   +--> [ML-NSMF] -------+--> [Decision Engine]
                                  |
                       +----------+-----------+
                       |                      |
                       v                      v
                 [BC-NSSMF]             [SLA-Agent Layer]
                       |                      |
                       v                      v
                 [Blockchain/Besu]     [Compliance Events]
                                              |
                                              v
                                       [Portal Visualization]
-------------------------------------------------------------
   ^
   |
[NASP Adapter <-> Real Infrastructure (RAN/Transport/Core)]
```

---

## 5. Interfaces and Links

### 5.1 Logical Interface Map

- `I-01` (gRPC): `SEM-CSMF -> Decision Engine` (metadata/semantic payload)
- `I-02` (Kafka): `SEM-CSMF -> ML-NSMF` (NEST/event stream)
- `I-03` (Kafka): `ML-NSMF -> Decision Engine` (risk prediction + explanation)
- `I-04` (Kafka): `Decision Engine -> BC-NSSMF` (decision for trusted registration)
- `I-05` (Kafka): `Decision Engine -> SLA-Agent` (post-admission action trigger)
- `I-06` (Kafka): `SLA-Agent -> lifecycle/compliance events` (risk/violation stream)
- `I-07` (Kafka): `SLA-Agent -> action results` (execution result stream)

### 5.2 API Boundary

- Portal Backend is the northbound API boundary for user-facing submission/status/metrics flows.
- NASP Adapter is the southbound boundary for infrastructure telemetry/action integration.

---

## 6. End-to-End Operational Flow

1. SLA request is submitted via Portal
2. Portal Backend validates and forwards the request
3. SEM-CSMF interprets intent and generates structured NEST
4. ML-NSMF predicts feasibility and explainability
5. Decision Engine computes final admission decision
6. If accepted, BC-NSSMF registers decision on blockchain
7. SLA-Agent executes actions and monitors runtime compliance
8. NASP Adapter continuously provides real-domain telemetry and action execution
9. Results, lifecycle, and evidence are exposed back to Portal

---

## 7. Multi-Domain Model

TriSLA evaluates feasibility across three domains:

- RAN -> resource allocation (PRB utilization and related radio constraints)
- Transport -> latency and jitter behavior
- Core -> computational and memory/network capacity

---

## 8. Decision Model (Conceptual)

Let:

- `D` = decision
- `R` = policy/rules
- `M` = ML prediction
- `T` = real-time telemetry

Then:

`D = f(R, M, T)`

Decision space:

`D ∈ {ACCEPT, REJECT, RENEGOTIATE}`

---

## 9. Data and Evidence Objects

Key artifacts exchanged in the pipeline:

- User-level SLA request payload
- Intent and semantic structure (SEM-CSMF)
- NEST representation
- ML feasibility score and explanation
- Decision outcome and justification
- On-chain registration records
- SLO compliance status and lifecycle events
- Multi-domain normalized telemetry snapshots

---

## 10. Observability and Reproducibility

TriSLA provides:

- Real-time telemetry snapshots
- SLA lifecycle monitoring
- Performance metrics (service/processing behavior)
- Event traces for inter-module flow
- Experimental datasets and campaign-derived evidence

This enables reproducible scientific evaluation of admission feasibility and runtime compliance.

---

## 11. Scientific Contribution

The architecture demonstrates:

- SLA-aware decision-making in multi-domain 5G/O-RAN conditions
- Integration of semantic processing + ML prediction + policy control
- Runtime validation of admitted SLAs (not only admission-time scoring)
- Traceable and auditable lifecycle through blockchain and event evidence

---

## 12. Conclusion

TriSLA is a unified framework that transforms SLA requests into validated, monitored, and auditable network slices, enabling reliable SLA enforcement in 5G/O-RAN environments.

