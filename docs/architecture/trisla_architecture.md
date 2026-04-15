# TriSLA Architecture (SSOT-Derived, Dissertation/IEEE Level)

## 1. Scope, SSOT, and Scientific Positioning

This document formalizes TriSLA architecture from executable runtime behavior in
`apps/*/src`. Code is the Single Source of Truth (SSOT), and all pipeline,
interface, and mathematical statements are constrained to implemented paths.

SSOT modules considered:

- `apps/sem-csmf/src`
- `apps/ml-nsmf/src`
- `apps/decision-engine/src`
- `apps/nasp-adapter/src`
- `apps/bc-nssmf/src`
- `apps/sla-agent-layer/src`
- `apps/portal-backend/src`

## 2. End-to-End Runtime Pipeline

Implemented control/data pipeline:

$$
\text{SEM-CSMF} \rightarrow \text{ML-NSMF} \rightarrow \text{Decision Engine} \rightarrow \text{NASP Adapter} \rightarrow \text{BC-NSSMF} \rightarrow \text{SLA-Agent Layer}
$$

Operational sequence:

1. Portal Backend receives tenant submission and calls SEM-CSMF.
2. SEM-CSMF derives semantic/NEST context and SLA requirement structures.
3. ML-NSMF computes calibrated risk and explainability metadata.
4. Decision Engine applies threshold and policy-governed risk logic.
5. If decision permits execution, NASP Adapter attempts NSI instantiation.
6. On successful execution branch, BC-NSSMF commits SLA state on blockchain.
7. SLA-Agent Layer ingests pipeline event and computes SLO/lifecycle evidence.

## 3. Global Mathematical Model

### 3.1 Input Space

Define the global input tuple:

$$
\mathcal{I} = \left( T, x, \Pi, \Upsilon \right)
$$

Where:

- $T$: tenant intent (text/structured request)
- $x = \left[ x_1, \ldots, x_n \right]$: telemetry and SLA feature vector
- $\Pi$: policy/threshold configuration
- $\Upsilon$: runtime telemetry context across RAN/Core/Transport

A canonical feature abstraction is:

$$
x = \left[ PRB, CPU, MEM, Latency, Reliability, Features_{ML} \right]
$$

### 3.2 Normalization Layer

TriSLA uses model-based and explicit normalization:

$$
x_i^{norm}=\frac{x_i-x_i^{min}}{x_i^{max}-x_i^{min}}
$$

with clipping/bounding in runtime helper logic.

### 3.3 ML Risk Layer

ML-NSMF predictive function:

$$
R_{ML}=f(x)
$$

Regression path:

$$
R_{reg}=1-viability\_score
$$

Classifier path:

$$
R_{cls}=\min\left(1,\ 0.5\cdot P(RENEGOTIATE)+1.0\cdot P(REJECT)\right)
$$

Selection rule:

$$
R_{ML}=
\begin{cases}
R_{cls}, & \text{classifier active}\\
R_{reg}, & \text{fallback}
\end{cases}
$$

### 3.4 Slice/Domain Stress Composition

$$
domain\_stress(x)=\sum_i w_i x_i^{norm}
$$

with slice-profile weighting (`URLLC`, `eMBB`, `mMTC`) implemented in
`slice_risk_adjustment.py`.

Slice-adjusted risk:

$$
R_{adj} = \left( 1 - \alpha_s \right) R_{ML} + \alpha_s \cdot domain\_stress\left( x \right)
$$

### 3.5 Decision Risk and Thresholding

PRB shaping:

$$
PRB_{norm}=\operatorname{clip}(PRB/100,0,1)
$$

$$
R_{final}=\min(1,\ R_{adj}+\alpha_{prb}\cdot PRB_{norm})
$$

Slice-specific threshold pairs:

$$
(T_{acc},T_{reneg})=
\begin{cases}
(0.48,0.72), & URLLC\\
(0.56,0.78), & eMBB\\
(0.54,0.76), & mMTC
\end{cases}
$$

Decision rule:

$$
Decision=
\begin{cases}
ACCEPT,& R_{final}<T_{acc}\\
RENEGOTIATE,& T_{acc}\le R_{final}<T_{reneg}\\
REJECT,& R_{final}\ge T_{reneg}
\end{cases}
$$

Hard policy gates:

- $PRB \ge 95 \Rightarrow REJECT$
- $85 \le PRB < 95 \Rightarrow RENEGOTIATE$

### 3.6 Acceptance Probability Interpretation

$$
P(ACCEPT)=1-R_{final}
$$

This interpretation is consistent with risk-as-failure semantics used in
predictive and decision stages.

### 3.7 Global Pipeline Function

$$
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
$$

Canonical notation:

$$
\Phi(T, x, Policy, Telemetry) \rightarrow (Decision, NSI, SLO, State)
$$

Where:

- `Decision`: policy-constrained admission action
- `NSI`: orchestration outcome from NASP Adapter
- `SLO`: compliance/lifecycle evidence from SLA-Agent Layer
- `State`: immutable blockchain lifecycle state from BC-NSSMF

## 4. Inter-Module Contract Semantics

- SEM-CSMF -> ML/Decision: hybrid semantic processing combining NLP, rule-based
  extraction, and ontology-assisted reasoning, producing semantic identifiers,
  slice class, and SLA requirement normalization.
- ML-NSMF -> Decision: calibrated risk, confidence, class probabilities, domain
  explainability.
- Decision -> NASP Adapter: execution eligibility and payload branch.
- NASP -> BC-NSSMF: realized execution state for immutable registration/update.
- Pipeline -> SLA-Agent Layer: event-level evidence for SLO/lifecycle evaluation.

The ontology layer provides structured domain knowledge but is not a strict
runtime dependency, allowing the system to operate under degraded conditions.

## 5. Runtime Branch Semantics

Acceptance branch:

$$
ACCEPT \Rightarrow NSI\_instantiate \Rightarrow BC\_register \Rightarrow SLA\_ingest
$$

Non-acceptance branch:

$$
Decision\in\{RENEGOTIATE,REJECT\} \Rightarrow execution\_side\_effects=SKIPPED
$$

Failure branch (post-acceptance):

$$
ACCEPT \land orchestration\_failure \Rightarrow BC/SLA\_branch\_conditioned\_by\_lifecycle
$$

## 6. Observability, Traceability, and Experimental Rigor

Runtime responses propagate:

- module latencies (`module_latencies_ms`)
- telemetry completeness indicators
- orchestration/blockchain/SLA-Agent statuses
- lifecycle state outputs (`IN_PROGRESS`, `COMPLETED`, `FAILED`, `SKIPPED`)

These fields support reproducibility and code-to-model traceability in
dissertation-grade and IEEE-style evaluation workflows.

## 7. End-to-End Scenario (Reference Runtime Walkthrough)

This scenario uses configured runtime boundaries already documented in SSOT.

Input:

- intent: eMBB-oriented tenant request
- slice threshold pair: $T_{acc}=0.56,\ T_{reneg}=0.78$
- PRB observed at decision time: $88\%$ (policy hard-band interval $85\le PRB<95$)

Processing:

- Portal Backend receives the SLA request and forwards semantic interpretation
  to SEM-CSMF.
- SEM-CSMF produces semantic context; ML-NSMF consumes telemetry features and
  performs risk estimation (`R_{ML}` and `R_{adj}`) for the decision process.
- Decision Engine computes $R_{final}$, applies threshold logic, and enforces
  PRB hard policy ($88\%\Rightarrow RENEGOTIATE$).
- NASP Adapter branch execution is skipped because the final action is not
  `ACCEPT`, while BC-NSSMF and SLA-Agent Layer follow lifecycle-conditioned
  branch semantics.

Output:

- The pipeline returns a `RENEGOTIATE` decision with traceable lifecycle and
  observability evidence across modules.

Impact:

- The walkthrough shows how semantic interpretation, risk estimation, and policy
  constraints jointly control network slice admission behavior without
  introducing non-SSOT assumptions.

## 8. Design Principles

TriSLA architecture follows these system-level principles:

- **SLA-aware decision**: action is derived from risk under explicit SLA
  thresholds and policy constraints.
- **Explainability by construction**: risk and decision outputs carry explanatory
  fields for audit and scientific interpretation.
- **Multi-domain integration**: RAN/Core/Transport observables are integrated in
  risk, actuation, and compliance phases.
- **Separation of concerns**: semantic interpretation, prediction, policy,
  orchestration, immutability, and compliance are modularized.

## 9. System-Level Trade-offs

- **Precision vs latency**: richer predictive/XAI processing improves diagnostic
  quality but increases inference overhead.
- **ML evidence vs hard policy**: policy gates (e.g., PRB bands) can override
  probabilistic confidence to preserve operational safety.
- **Centralization vs modularity**: Portal Backend centralizes orchestration for
  client simplicity, while module decomposition preserves maintainability and
  independent evolution.

## 10. Observability and Explainability

Observability and explainability are first-class architectural artifacts:

- ML stage exports feature/domain attribution metadata.
- Decision stage exports threshold and policy-path metadata.
- Portal responses propagate lifecycle status, telemetry completeness, and module
  latency evidence.
- Blockchain and SLA-Agent layers provide immutable and operational traceability,
  respectively.

Together, these mechanisms support reproducible experiments, post-hoc diagnosis,
and dissertation/paper-grade interpretability of system behavior.
