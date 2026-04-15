# Decision Engine

## 1. Overview

Decision Engine is the policy authority of TriSLA. It fuses semantic intent,
ML-derived risk, and operational telemetry to emit final admission actions:
`AC`, `RENEG`, or `REJ`.

It is the module that materializes the acceptance/rejection boundary.

## 2. Role in TriSLA Pipeline

$$
Input_{semantic+risk+telemetry} \rightarrow \text{Decision Engine} \rightarrow Output_{decision}
$$

Pipeline role:

- Consumes SEM-CSMF context and ML-NSMF risk package.
- Applies slice-specific thresholds and PRB-aware policy logic.
- Emits decision plus explanatory metadata for orchestration/lifecycle stages.

## 3. Input Space (Formal)

Decision input tuple:

$$
u_{de} = \left( \eta_{sem}, y_{ml}, \tau_{ops}, \pi \right)
$$

Where:

- $\eta_{sem}$: semantic context (`intent`, `nest`, `slice_type`).
- $y_{ml}$: ML risk outputs (`risk_score`, confidence, class metadata).
- $\tau_{ops}$: telemetry snapshot, notably PRB and domain stress factors.
- $\pi$: policy configuration flags and thresholds.

Primary endpoint (`apps/decision-engine/src/main.py`):

- `POST /evaluate`

## 4. Output Space (Formal)

Decision output:

$$
y_{de} = \left( a, r, c, m \right)
$$

Where:

- $a \in \{AC, RENEG, REJ\}$: final action
- $r$: textual/structured reasoning
- $c$: confidence and threshold decision metadata
- $m$: propagated decision context (`ml_risk_score`, thresholds, PRB factors)

This output controls NASP orchestration gating and downstream lifecycle flow.

## 5. Runtime Behavior (Detailed)

1. Parse and validate `SLAEvaluateInput`.
2. Resolve semantic context and extract slice profile.
3. Query ML-NSMF and ingest calibrated risk package.
4. Compute PRB-normalized and policy-shaped final risk.
5. Execute threshold decision (`ACCEPT`, `RENEGOTIATE`, `REJECT`).
6. Apply hard policy gates in policy-governed mode.
7. Optionally perform ML confidence-based refinement under configuration gates.
8. Return `DecisionResult` with action, reasoning, and decision metadata.

Fallback mechanisms:

- Threshold-only decision when optional refinement signals are absent.
- Conservative hard gating when PRB overload thresholds are exceeded.

## 6. Data Model (Semantic)

Main schema entities (`apps/decision-engine/src/models.py`):

- `SLAEvaluateInput`: semantic and telemetry decision payload.
- `DecisionResult`: action + explanatory and traceability fields.
- `MLPrediction`: embedded ML evidence structure.
- `DecisionAction`: constrained action codomain (`AC`, `RENEG`, `REJ`).

Semantically critical fields:

- `ml_risk_score`: main continuous decision driver.
- `telemetry_snapshot`/PRB-derived values: policy overrides.
- `final_decision`, `threshold_decision`: reveal pre/post-policy action path.

## 7. Mathematical Model

Slice-dependent thresholds:

$$
(T_{acc},T_{reneg})=
\begin{cases}
(0.48,0.72), & URLLC\\
(0.56,0.78), & eMBB\\
(0.54,0.76), & mMTC
\end{cases}
$$

PRB normalization:

$$
PRB_{norm}=\operatorname{clip}(PRB/100,0,1)
$$

Final risk:

$$
R_{final}=\min(1,\ R_{adj}+\alpha_{prb}\cdot PRB_{norm})
$$

Primary decision function:

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

Interpretation:

- Decision Engine implements a constrained risk-to-action mapping under policy.
- It is the module where probabilistic evidence becomes contractual action.

## 8. Integration with Decision Engine

This module is itself the decision nexus. Integration semantics:

- Upstream influence: SEM-CSMF (semantic class) + ML-NSMF (risk evidence).
- Downstream impact: NASP Adapter execution eligibility, BC-NSSMF registration
  eligibility, and SLA-Agent lifecycle branch (`executed` vs `skipped` paths).

## 9. Constraints and Assumptions

- Correctness depends on telemetry freshness and ML payload integrity.
- Policy flags alter runtime branch behavior and must be controlled in studies.
- Decision Engine does not instantiate NSI directly; it authorizes that path.

## 10. Relation to Global Model $\Phi$

Within:

$$
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
$$

Canonical global function: Φ(T, x, Policy, Telemetry) → (Decision, NSI, SLO, State).

Decision Engine realizes the $Decision$ projection by combining semantic
operands, normalized risk, and policy constraints into final admission action.

## 11. Design Rationale

Decision Engine exists as a dedicated policy boundary to keep admission logic
explicit, auditable, and independent from ML model internals.

Key design rationale:

- enforce deterministic thresholds per slice profile;
- combine probabilistic evidence with hard operational gates (PRB policy);
- preserve explainability fields for every decision.

Alternative (pure ML action selection) was not adopted because it weakens policy
control and operational predictability.

## 12. Evolution and Design Decisions

Critical runtime decisions consolidated in the current design:

- adoption of slice-specific threshold pairs rather than a single global
  threshold;
- PRB hard gating (`>=95` reject, `85-95` renegotiate) to prioritize overload
  protection;
- confidence-gated ML refinement controlled by runtime flags.

These decisions prioritize policy safety and interpretability over purely
statistical optimization.

## 13. Example Walkthrough

Input:

- slice type: `eMBB`
- thresholds: $T_{acc}=0.56,\ T_{reneg}=0.78$
- PRB: `88%` (inside hard renegotiate band)
- ML output: risk in decision interval

Processing:

- The module receives semantic interpretation context and ML risk estimation
  outputs for the SLA request.
- It computes $R_{final}$ from $R_{adj}$ and PRB shaping, then evaluates the
  threshold decision.
- PRB policy gating is applied on top of the threshold decision.

Output:

- The decision process emits `RENEG` with explicit reasoning and confidence
  metadata, including policy-path evidence.

Impact:

- The emitted decision controls downstream orchestration behavior, determining
  whether the network slice execution path is triggered or skipped.

## 14. Impact on SLA Decision

This module is the direct source of `AC`/`RENEG`/`REJ`.

Most critical variables:

- `R_final` (risk after policy shaping)
- PRB bands (hard override)
- slice-dependent threshold pair

Decision Engine is therefore the dominant determinant of admission outcome.

## 15. Operational Considerations

- Requires upstream semantic and ML services with stable contracts.
- Policy flags must be version-controlled in experiments.
- Telemetry freshness is operationally critical; stale PRB can distort gating.

## A. Technical Narrative

Decision Engine is the contract boundary where probabilistic evidence becomes
operational action. It exists to combine semantic context, ML risk, and explicit
policy constraints into an auditable decision function that produces
`AC`/`RENEG`/`REJ`.

This module is intentionally separated from ML-NSMF because prediction quality
and policy governance evolve under different constraints. The former is
statistical; the latter is normative and safety-critical. Decision Engine
consolidates these dimensions in a deterministic control point.

Its operation is policy-centered: it receives calibrated risk, applies
slice-specific thresholds, enforces PRB hard gates, and returns a traceable
decision payload. This design ensures that final action semantics remain
explainable under both nominal and stressed conditions.

## B. Operational Perspective

In real networks, Decision Engine is the principal governor of admission
pressure. Under heavy RAN utilization, PRB-aware gates can override otherwise
favorable ML outputs to prevent overload propagation.

From an operations standpoint, this module stabilizes system behavior during
traffic bursts by trading admission aggressiveness for SLA protection. The
observed impact is a controlled increase in `RENEG/REJ` decisions when
infrastructure pressure crosses configured guard bands.

## C. Telecom Context

In 5G slicing, admission decisions must balance tenant demand with dynamic radio
and transport constraints. Decision Engine realizes this balance by combining
SLA-aware thresholds and real-time resource pressure (notably PRB), aligning
policy enforcement with O-RAN-aware operational safety.

It is therefore the module that maps telecom control objectives into explicit
admission actions.

## D. Intuitive Explanation

An intuitive analogy is an air-traffic controller: ML provides forecasts, but
the controller applies hard safety rules before authorizing takeoff. Decision
Engine plays this role for slice admission.

In conceptual terms, it is the "final arbiter" that turns model evidence into a
network action while guaranteeing policy compliance.

## E. End-to-End Role Narrative

Before Decision Engine, the system has semantic interpretation plus quantified
risk. After Decision Engine, the system has a definitive action that controls
whether orchestration side effects should be executed.

This transition marks the key phase change in the TriSLA pipeline: from
assessment to commitment.
