# ML-NSMF

## 1. Overview

ML-NSMF is the predictive risk engine of TriSLA. It converts semantic/SLA and
telemetry features into risk estimates and explainability artifacts used by
Decision Engine.

Its role is probabilistic inference and calibration, not final policy action.

## 2. Role in TriSLA Pipeline

\[
Input_{semantic+telemetry} \rightarrow \text{ML-NSMF} \rightarrow Output_{risk}
\]

Pipeline effect:

- Receives feature vectors from submit/evaluation context.
- Produces `risk_score`, confidence metadata, and optional class probabilities.
- Propagates calibrated risk for admission policy evaluation.

## 3. Input Space (Formal)

Define the feature vector:

\[
x=[x_1,\ldots,x_n]
\]

Where \(x\) includes runtime metrics and derived attributes (latency,
throughput, reliability, jitter, packet loss, CPU/MEM utilization, slice
encoding, and ratios).

Primary endpoint (`apps/ml-nsmf/src/main.py`):

- `POST /api/v1/predict`

## 4. Output Space (Formal)

Prediction output:

\[
y_{ml}=(R_{ML},L_{risk},V,C,\Pi,\Xi)
\]

Where:

- \(R_{ML}\): risk score used by Decision Engine
- \(L_{risk}\): categorical risk level
- \(V\): viability score
- \(C\): confidence-related fields
- \(\Pi\): class probabilities / predicted decision class (if classifier active)
- \(\Xi\): explainability metadata (`slice_domain_xai`, feature factors)

## 5. Runtime Behavior (Detailed)

1. Build canonical feature dictionary and derived features.
2. Apply scaler normalization (`scaler.transform`) when model pipeline requires.
3. Compute base viability and convert to regression risk.
4. If classifier is available, compute class probabilities and class-based risk.
5. Apply slice/domain risk adjustment and calibrated score composition.
6. Build structured explanation payload and timing metadata.
7. Return HTTP response and optionally publish prediction events.

Fallback mechanisms:

- Regression-only mode when classifier is unavailable.
- Safe defaults for missing optional features via runtime preprocessing.

## 6. Data Model (Semantic)

Key output fields and semantic impact:

- `risk_score`: final ML risk propagated downstream.
- `raw_risk_score`: pre-adjustment risk baseline.
- `slice_adjusted_risk_score`: risk after slice/domain shaping.
- `predicted_decision_class`: model class hypothesis; influences refinement logic.
- `class_probabilities`: uncertainty distribution for policy-aware usage.
- `slice_domain_xai.dominant_domain`: explanatory attribution to domain pressure.

## 7. Mathematical Model

Regression risk:

\[
R_{reg}=1-\text{viability\_score}
\]

Classifier risk composition:

\[
R_{cls}=\min\left(1,\ 0.5\cdot P(RENEGOTIATE)+1.0\cdot P(REJECT)\right)
\]

Effective ML risk:

\[
R_{ML}=
\begin{cases}
R_{cls}, & \text{if classifier is active}\\
R_{reg}, & \text{otherwise}
\end{cases}
\]

Normalization abstraction:

\[
x_i^{norm}=\frac{x_i-x_i^{min}}{x_i^{max}-x_i^{min}}
\]

Domain stress composition:

\[
domain\_stress(x)=\sum_i w_i x_i^{norm}
\]

Slice-adjusted risk:

\[
R_{adj}=(1-\alpha_s)R_{ML}+\alpha_s\cdot domain\_stress(x)
\]

Interpretation:

- \(R_{ML}\) is model-native uncertainty about SLA feasibility.
- \(R_{adj}\) contextualizes model output to slice/domain operating pressure.
- This risk directly conditions admission boundaries in Decision Engine.

## 8. Integration with Decision Engine

ML-NSMF directly shapes `ACCEPT/RENEG/REJ` outcomes by propagating:

- `risk_score` / `slice_adjusted_risk_score`
- confidence and class probabilities
- domain-level explanatory factors

Decision Engine consumes these fields to apply threshold and policy-governed
logic, including PRB-aware hard gating.

## 9. Constraints and Assumptions

- Prediction quality depends on model/scaler artifacts and feature integrity.
- Missing telemetry can reduce confidence or trigger fallback behavior.
- ML-NSMF does not enforce policy; it supplies probabilistic evidence.

## 10. Relation to Global Model \(\Phi\)

In:

\[
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
\]

ML-NSMF implements the predictive kernel \(f(x)\) that maps normalized features
to risk evidence consumed by the policy-decision stage.

## 11. Design Rationale

ML-NSMF is separated from Decision Engine to keep probabilistic inference
independent from policy enforcement. This enables controlled evolution of models
without changing admission contracts.

The dual-path design (regression + classifier) is intentional: regression keeps
continuous viability semantics, while classification provides direct policy-class
evidence. Trade-off: higher model complexity vs better decision support and
fallback robustness.

## 12. Evolution and Design Decisions

Two key runtime decisions were consolidated:

- classifier-optional behavior with regression fallback, avoiding hard failure
  when classifier artifacts are unavailable;
- slice/domain risk adjustment layer to align raw model output with
  domain-specific operational pressure.

These decisions reflect a reliability-first strategy for production-like runs.

## 13. Example Walkthrough

Input (feature payload fields):

- latency: operational latency metric
- reliability: operational reliability metric
- PRB-related pressure through telemetry-derived features
- slice type: `eMBB`

Step 1:

- Features are normalized via scaler/runtime normalizers.

Step 2:

- Model computes `R_reg=1-viability_score`.
- If classifier is active, computes class probabilities and `R_cls`.

Step 3:

- Effective risk \(R_{ML}\) is selected and adjusted into `R_adj`.

Step 4:

- ML payload exports `risk_score`, confidence, and domain XAI factors to
  Decision Engine.

## 14. Impact on SLA Decision

ML-NSMF has direct impact on `ACCEPT/RENEG/REJ` boundaries through:

- `risk_score` and `slice_adjusted_risk_score`
- confidence/class probabilities used by refinement logic

The critical variable is the calibrated risk propagated as decision evidence.

## 15. Operational Considerations

- Requires consistent model/scaler artifacts and compatible feature schema.
- Telemetry incompleteness can reduce confidence and increase fallback usage.
- Explainability generation adds computational overhead; this is a precision vs
  latency trade-off at runtime.

## A. Technical Narrative

ML-NSMF plays a central role in transforming multidomain telemetry and
SLA-related features into quantitative risk evidence. It operationalizes the
probabilistic layer of TriSLA by producing calibrated risk scores, confidence
signals, and explanatory factors that can be consumed by policy logic.

The module exists as a dedicated inference service to keep model evolution
independent from decision policy. This separation permits controlled updates to
predictive behavior while preserving stable downstream action semantics.
Technically, it combines regression-based viability interpretation with
classifier-based decision propensity, then projects both into a risk contract.

Its runtime interaction model is explicit: SEM-derived context and telemetry are
converted into normalized features, inference is performed, and enriched risk
payloads are exported to Decision Engine. In this sense, ML-NSMF is the system
component that quantifies uncertainty before policy commits to action.

## B. Operational Perspective

In production-like environments, ML-NSMF must sustain predictable inference
latency under variable telemetry load. During congestion episodes, feature
profiles usually shift toward higher stress signatures, which drives risk
escalation and increases the probability of restrictive actions downstream.

Operationally, the main tension is computational: richer explainability improves
diagnostics, but can increase per-request processing time. Fallback modes (for
classifier or partial features) are therefore essential to preserve service
continuity during degraded conditions.

## C. Telecom Context

In 5G slicing and O-RAN-oriented operations, SLA feasibility depends on dynamic
resource and quality indicators across domains. ML-NSMF provides the predictive
abstraction that maps these indicators into admission-relevant risk, enabling
SLA-aware control loops beyond static thresholding.

It therefore acts as the quantitative bridge between network behavior and SLA
governance decisions.

## D. Intuitive Explanation

A useful intuition is to view ML-NSMF as a "risk thermometer" for each incoming
slice request. It reads system signals, estimates how likely the request is to
fail SLA objectives, and explains which factors most contributed to that risk.

It does not decide the final action by itself; it provides the calibrated
evidence that decision policy uses.

## E. End-to-End Role Narrative

Before ML-NSMF, the pipeline has semantic intent and telemetry-derived features
but no quantified uncertainty. After ML-NSMF, the pipeline has structured risk
evidence (`risk_score`, confidence, explanatory factors) that directly feeds
Decision Engine thresholds and policy gates.

Consequently, ML-NSMF is the predictive pivot between semantic interpretation
and operational admission control.
