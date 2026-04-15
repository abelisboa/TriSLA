# SEM-CSMF

## 1. Overview

SEM-CSMF is the semantic entry point of TriSLA. It transforms user intent into
machine-actionable slice semantics and NEST-aligned metadata consumed by
downstream modules.

Its core responsibility is not decision-making, but semantic interpretation and
contract preparation for risk and policy evaluation stages.

## 2. Role in TriSLA Pipeline

Pipeline position:

$$
Input_{tenant} \rightarrow \text{SEM-CSMF} \rightarrow Output_{semantic}
$$

Runtime sequence contribution:

- Receives tenant intent and optional SLA hints.
- Produces `intent_id`, `nest_id`, `service_type`, `slice_type`, and normalized
  SLA requirement fields.
- Supplies context for ML-NSMF and Decision Engine.

## 3. Input Space (Formal)

Let the semantic input be:

$$
u_{sem} = \left( T, \tau, \Theta_0 \right)
$$

Where:

- $T$: tenant intent text or structured intent payload.
- $\tau$: tenant identity/context (`tenant_id`).
- $\Theta_0$: optional SLA requirements provided at request time.

Primary ingress endpoints (SSOT from `apps/sem-csmf/src/main.py`):

- `POST /api/v1/interpret`
- `POST /api/v1/intents`
- `POST /api/v1/nest`

## 4. Output Space (Formal)

Semantic output:

$$
y_{sem} = \left( \iota, n, s, \Theta, \eta \right)
$$

Where:

- $\iota$: `intent_id`
- $n$: `nest_id`
- $s \in \{URLLC, eMBB, mMTC\}$: inferred slice class
- $\Theta$: normalized SLA requirement set
- $\eta$: semantic metadata (parsing, reasoning, and timing context)

This output is propagated to decision/risk processing and lifecycle tracking.

## 5. Runtime Behavior (Detailed)

1. Parse intent text using semantic/NLP parsing routines.
2. Infer service and slice type via rule/keyword and ontology-assisted matching.
3. Build canonical SLA requirement structure (`SLARequirements`).
4. Generate NEST-compatible context and assign semantic identifiers.
5. Persist/retrieve intent/NEST entities for subsequent lookups.
6. Return semantic package for submission orchestration.
7. Apply deterministic fallback behavior (default slice semantics) when parser
   confidence or ontology resolution is insufficient.

Fallback mechanisms:

- Rule-based fallback when ontology execution is unavailable.
- Deterministic defaulting to keep pipeline continuity.

## 6. Data Model (Semantic)

Relevant entities (`apps/sem-csmf/src/models/intent.py`,
`apps/sem-csmf/src/models/nest.py`):

- `intent`: natural-language or structured request; origin is tenant input;
  impacts inferred service class.
- `slice_type`: semantic class; origin is parser/reasoner output; impacts ML and
  threshold profiles.
- `sla_requirements`: QoS target set; origin is request + semantic completion;
  impacts risk modeling and final decision strictness.
- `intent_id`, `nest_id`: traceability identifiers; origin is SEM-CSMF runtime;
  impact cross-module correlation.

## 6.1 Ontology Model

SEM-CSMF includes an explicit ontology layer (TTL + OWL artifacts) that models
service intent, slice types, SLA/SLO/SLI concepts, network domains, and
3GPP-aligned characteristics (e.g., QoS and slice profile concepts).

From a structural perspective, the ontology is extensive and semantically rich,
covering core concepts for slicing and SLA reasoning.

Although the ontology model is structurally rich, its runtime usage within the
SEM-CSMF pipeline is currently limited to a subset of concepts, primarily slice
types and core SLA metrics.

## 6.2 Ontology-Assisted Semantic Interpretation

The runtime implementation follows a **hybrid semantic interpretation combining
NLP, rule-based extraction, and ontology-assisted validation**.

Observed runtime sequence:

1. NLP/regex extracts candidate requirements and tentative slice hints.
2. Ontology-assisted parser/reasoner performs complementary inference/validation
   when ontology support is available.
3. If ontology loading/reasoning fails, SEM-CSMF continues with heuristic and
   rule-based fallback paths.

## 7. Mathematical Model

Semantic transformation:

$$
I: (T,\tau,\Theta_0) \mapsto (\iota,n,s,\Theta,\eta)
$$

Slice inference abstraction:

$$
\hat{s} = \arg\max_{s \in S} \operatorname{match}(T,\Theta_0,s)
$$

Normalized requirement projection:

$$
\Theta = \mathcal{N}_{sem}(\Theta_0, T, \hat{s})
$$

Interpretation:

- $I$ maps human intent into deterministic machine semantics.
- $\hat{s}$ selects the operational slice profile for downstream risk policy.
- $\Theta$ harmonizes request semantics with runtime-compatible fields.
- Ontology-assisted reasoning can participate in this transformation, but it is
  not a mandatory execution dependency for $I(T)\to(s,\theta,\eta)$.

## 8. Integration with Decision Engine

SEM-CSMF influences decision outcomes indirectly by defining the semantic frame
used by ML-NSMF and Decision Engine:

- `slice_type` selects threshold family in Decision Engine.
- `sla_requirements` define expected QoS operating region.
- `intent_id`/`nest_id` preserve traceability through `ACCEPT/RENEG/REJ` paths.

## 9. Constraints and Assumptions

- Semantic quality depends on parser/rule and ontology availability.
- Fallback defaults preserve liveness but may reduce semantic specificity.
- SEM-CSMF does not execute orchestration or policy enforcement directly.

## 10. Relation to Global Model $\Phi$

Within:

$$
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
$$

Canonical global function: Φ(T, x, Policy, Telemetry) → (Decision, NSI, SLO, State).

SEM-CSMF is the front-end realization of $T \mapsto (\Theta,s,\eta)$, i.e., it
produces semantic operands consumed by risk, policy, and orchestration layers.

## 11. Design Rationale

SEM-CSMF exists to isolate semantic interpretation from numerical risk modeling.
This separation prevents coupling natural-language variability to ML internals
and preserves a stable contract (`slice_type`, `sla_requirements`, IDs) for all
downstream stages.

Alternative considered in architecture discussions was embedding text parsing in
ML or Decision Engine. The chosen decomposition improves maintainability and
traceability, at the cost of one additional inter-module boundary.

An additional design rationale is to avoid rigid ontology coupling. SEM-CSMF is
kept operationally robust even when ontology dependencies (e.g., `owlready2`,
ontology loading, or reasoning execution) are unavailable. This improves fault
tolerance and reduces hard dependency risk in real deployments.

## 12. Evolution and Design Decisions

The module evolved toward deterministic fallbacks to keep submission liveness
when ontology or richer semantic resolution is unavailable. The current design
prioritizes runtime continuity and reproducibility over maximal semantic
expressiveness in degraded conditions.

Critical design decision: keep semantic IDs (`intent_id`, `nest_id`) as
first-class outputs to support end-to-end traceability in lifecycle and audit
paths.

## 13. Example Walkthrough

Input:

- intent text: "URLLC slice with strict latency"
- tenant: `tenant-a`
- optional SLA hints: latency/reliability fields

Processing:

- The module performs semantic interpretation of the SLA request using the
  hybrid path (NLP/regex, rule logic, and ontology-assisted validation when
  available).
- The pipeline infers `slice_type=URLLC` and builds normalized SLA requirement
  fields together with `intent_id` and `nest_id`.

Output:

- Structured semantic context is forwarded to ML-NSMF and then to the decision
  process as formal input.

Impact:

- The semantic interpretation stage reduces ambiguity in the SLA request before
  risk estimation and policy evaluation.

## 14. Impact on SLA Decision

SEM-CSMF impacts `ACCEPT/REJECT` indirectly but materially:

- `slice_type` selects threshold family in Decision Engine.
- `sla_requirements` shape feature expectations consumed by ML-NSMF.
- semantic completeness improves confidence and reduces fallback-triggered noise.

The critical propagated variable is `slice_type`.

## 15. Operational Considerations

- Requires semantic parser services and optional ontology resources.
- Must preserve schema compatibility with downstream modules.
- In degraded mode, deterministic defaults preserve service continuity but may
  reduce semantic granularity for complex intents.

## 15.1 Fallback and Degraded Operation Mode

SEM-CSMF explicitly supports degraded operation when ontology support is
partially or fully unavailable, including:

- `owlready2` not installed or not importable.
- ontology file loading failure.
- reasoning execution failure (e.g., Pellet/reasoning errors).

In these conditions, the module continues through NLP/regex and rule-based
heuristics, preserving pipeline liveness.

The SEM-CSMF module is designed to operate even in the absence of ontology
support, relying on heuristic and rule-based mechanisms.

## 16. Ontology Usage Scope and Limitations

Current ontology usage scope in runtime:

- semantic validation of selected SLA/slice constraints;
- complementary slice inference/consistency checks.

Current ontology limitations in runtime usage:

- not used as the single source of decision semantics;
- not a mandatory runtime dependency for SEM-CSMF execution;
- broad ontology vocabulary is only partially exercised in the active pipeline.

## 17. Future Ontology Integration Enhancements

Based on current runtime behavior, ontology integration may evolve toward:

- broader runtime use of ontology concepts beyond core slice/SLA metrics;
- deeper semantic inference in the semantic validation path;
- gradual reduction of heuristic dominance where ontology-backed inference is
  proven stable and cost-effective.

## A. Technical Narrative

SEM-CSMF is the semantic ingress of TriSLA, where human service intention is
translated into machine-consumable control artifacts. Its technical value is to
convert heterogeneous intent expressions into stable operational descriptors such
as slice type, normalized SLA requirements, and traceable identifiers.

The module exists because downstream components operate on structured variables,
not linguistic ambiguity. By isolating semantic parsing and ontology-guided
matching, TriSLA preserves a clean contract between language interpretation and
numerical decision logic. This decoupling improves reproducibility and reduces
cross-layer coupling.

Operationally, SEM-CSMF acts as a deterministic semantic preprocessor for the
entire pipeline. It receives tenant context, resolves intent semantics, and
exports context that directly conditions ML and policy stages. Its interaction
model is therefore foundational: every downstream decision depends on its
semantic normalization quality.

## B. Operational Perspective

In real deployments, SEM-CSMF behaves as a low-latency front gate that must
remain stable under bursty request arrivals. Under load, deterministic fallback
behavior is essential to preserve throughput and avoid pipeline stalls when
ontology resources are partially unavailable.

Network impact is indirect but significant: semantic misclassification can route
traffic into an inappropriate slice profile, which then alters risk estimation
and admission outcomes. For this reason, operational monitoring should track
semantic confidence proxies and fallback frequency.

## C. Telecom Context

In 5G slicing, service intent is often expressed at business/application level,
while network realization requires slice-aware technical descriptors. SEM-CSMF
implements this translation boundary, bridging human SLA language and
network-oriented semantics used by O-RAN/core/transport-aware modules.

Within SLA management, it formalizes the request contract that will later be
evaluated against risk, policy, and multidomain observability constraints.

## D. Intuitive Explanation

A practical analogy is that SEM-CSMF works as a "technical interpreter" between
the tenant and the network control stack. The tenant says what service behavior
is desired; SEM-CSMF rewrites that request into a precise technical form that
other modules can compute on.

Conceptually, it does not decide whether a request is accepted. It ensures the
request is understandable, consistent, and traceable before decision logic
begins.

## E. End-to-End Role Narrative

Before SEM-CSMF, the system has only user-provided intent text and optional SLA
hints. After SEM-CSMF, the pipeline receives structured semantic context
(`slice_type`, requirements, IDs) suitable for ML risk inference and policy
evaluation.

This positioning makes SEM-CSMF the semantic anchor of the end-to-end flow: it
defines the problem representation that all subsequent modules consume.
