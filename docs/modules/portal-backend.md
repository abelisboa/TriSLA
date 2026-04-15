# Portal Backend

## 1. Overview

Portal Backend is the external orchestration gateway of TriSLA. It exposes
client-facing APIs, coordinates the module chain, and returns lifecycle-rich
responses grounded in runtime evidence.

## 2. Role in TriSLA Pipeline

\[
Input_{tenant\ request} \rightarrow \text{Portal Backend} \rightarrow Output_{unified\ lifecycle\ response}
\]

Pipeline role:

- Entry API for interpretation/submission.
- Orchestration wrapper for SEM-CSMF, Decision path, NASP, BC-NSSMF, SLA-Agent.
- Aggregator of telemetry and lifecycle status into a single response contract.

## 3. Input Space (Formal)

Gateway input:

\[
u_{pb} = \left( template\_id, form\_values, tenant\_id, context \right)
\]

Core endpoints:

- App-level: `GET /`, `GET /health`, `GET /api/v1/health`, `GET /api/v1/health/global`, `GET /nasp/diagnostics`, `GET /metrics`
- SLA router: `POST /api/v1/sla/interpret`, `POST /api/v1/sla/submit`, `GET /api/v1/sla/status/{sla_id}`, `GET /api/v1/sla/metrics/{sla_id}`
- Mounted routers: `/api/v1/modules/*`, `/api/v1/prometheus/*`, `/api/v1/contracts/*`, `/api/v1/slas/*`, `/api/v1/slos/*`, `/api/v1/xai/*`, `/api/v1/intents/*`, `/api/v1/tempo/*`, `/api/v1/loki/*`

## 4. Output Space (Formal)

Unified output:

\[
y_{pb} = \left( d, o, b, s, \lambda, \mu \right)
\]

Where:

- \(d\): decision outcome
- \(o\): orchestration status
- \(b\): blockchain status
- \(s\): SLA-Agent status
- \(\lambda\): lifecycle state machine output
- \(\mu\): telemetry and module-latency metadata

## 5. Runtime Behavior (Detailed)

For `POST /api/v1/sla/submit`:

1. Validate request schema and normalize submit template.
2. Execute semantic processing through SEM-CSMF interpretation/intents path.
3. Resolve decision package from the runtime decision flow.
4. If decision is `ACCEPT`, request NSI orchestration in NASP Adapter.
5. If orchestration succeeds, register SLA state in BC-NSSMF.
6. Trigger SLA-Agent pipeline-event ingestion according to lifecycle rules.
7. Build and return a unified response with module statuses, telemetry flags,
   and lifecycle state.

Fallback mechanisms:

- Degraded module statuses (`UP`/`DOWN` patterns, skipped branches).
- Lifecycle-marked skip semantics for non-accepted or failed branches.

## 6. Data Model (Semantic)

Core schema definitions (`apps/portal-backend/src/schemas/sla.py`):

- `SLAInterpretRequest(intent_text, tenant_id)`
- `SLASubmitRequest(template_id, form_values, tenant_id)`
- `SLASubmitResponse` with decision, reason/justification, IDs, module statuses,
  lifecycle, orchestration, telemetry, and latency metadata.
- `SLAStatusResponse` and `SLAMetricsResponse` for post-submit tracking.

Semantically critical fields:

- `decision`: controls execution branch.
- `orchestration_status` / `lifecycle_state`: branch observability.
- `telemetry_complete` and metadata block: data-quality context.

## 7. Mathematical Model

Gateway composition:

\[
G(u_{pb})=\left(Decision,\ Orchestration,\ Blockchain,\ SLO,\ Lifecycle\right)
\]

Branch semantics:

\[
Decision=ACCEPT \Rightarrow Orchestrate\_NSI \Rightarrow Register\_Blockchain \Rightarrow Ingest\_SLA\_Agent
\]

\[
Decision\in\{RENEGOTIATE,REJECT\} \Rightarrow Orchestration=SKIPPED
\]

Optional response completeness abstraction:

\[
Q_{resp}=h(module\_status,\ telemetry\_complete,\ lifecycle\_state)
\]

Interpretation:

- Portal Backend implements the deterministic orchestration wrapper of the
  global pipeline.
- It is the integration point where module-level outcomes become client-visible
  system state.

## 8. Integration with Decision Engine

Portal Backend is the primary consumer of Decision Engine output in the external
API flow:

- receives final action and explanatory metadata,
- activates downstream side effects only when action allows execution,
- returns decision and propagated evidence to clients.

## 9. Constraints and Assumptions

- Behavior depends on availability of downstream modules and observability stack.
- Some endpoints forward raw backend payloads (e.g., Prometheus routers).
- Lifecycle semantics rely on consistent branch-status propagation.

## 10. Relation to Global Model \(\Phi\)

In:

\[
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
\]

Canonical global function: Φ(T, x, Policy, Telemetry) → (Decision, NSI, SLO, State).

Portal Backend provides the orchestrating wrapper that exposes this mapping to
external clients and materializes branch-wise lifecycle observability.

## 11. Design Rationale

Portal Backend exists to provide a single client-facing contract over a
multi-module control pipeline. It centralizes validation, orchestration, and
lifecycle response construction while keeping module internals decoupled.

Alternative direct client-to-module chaining was not adopted because it would
fragment contracts and weaken traceability.

## 12. Evolution and Design Decisions

Key design decisions present in current runtime:

- unified submit orchestration path with branch-aware lifecycle metadata;
- explicit module status propagation for observability;
- downstream execution only on admissible decision branches.

This design improves operational diagnostics and reproducibility of experiments.

## 13. Example Walkthrough

Input:

- `template_id`
- `form_values` including SLA-related values
- `tenant_id`

Processing:

- The backend validates the SLA request and forwards semantic interpretation to
  SEM-CSMF.
- It receives risk estimation and decision process outputs, then evaluates
  branch semantics for orchestration and lifecycle progression.
- If `ACCEPT`, it triggers NASP execution and subsequent BC-NSSMF and SLA-Agent
  stages under the configured branch conditions.

Output:

- The module returns a unified response with decision, orchestration status,
  lifecycle state, and module-level observability evidence.

Impact:

- Portal Backend preserves end-to-end contract coherence, ensuring the SLA
  request receives a traceable and reproducible runtime outcome.

## 14. Impact on SLA Decision

Portal Backend does not compute decision policy, but it strongly influences
decision observability and execution consequences by:

- preserving decision payload fidelity to clients;
- enforcing branch semantics (`executed` vs `skipped`);
- coordinating downstream side effects tied to decision action.

Critical propagated variable is `decision`.

## 15. Operational Considerations

- Requires stable connectivity to SEM-CSMF, Decision flow, NASP, BC-NSSMF, and
  SLA-Agent endpoints.
- Depends on observability backends for complete telemetry summaries.
- Must maintain schema stability for external consumers and reproducibility
  scripts.

## A. Technical Narrative

Portal Backend is the compositional gateway that presents TriSLA as a coherent
service to external clients. It exists to unify validation, orchestration, and
response semantics across multiple internal modules with distinct responsibilities.

Without this layer, clients would need to coordinate internal contracts and
branch semantics directly. By centralizing orchestration, Portal Backend improves
interface stability, end-to-end traceability, and operational diagnosability.

Its runtime behavior is branch-oriented: it collects upstream outputs, triggers
downstream side effects conditionally, and returns a lifecycle-rich response that
captures decision, execution, and observability context in a single artifact.

## B. Operational Perspective

In real deployments, Portal Backend is the operational choke point for request
volume and user-perceived latency. Under high load, its value is in preserving
deterministic branch semantics and clear status reporting even when some
downstream services are degraded.

Network impact is indirect but systemic: this layer governs how quickly decisions
translate into orchestration calls and how reliably lifecycle status is exposed
to operators and automation clients.

## C. Telecom Context

In 5G slicing operations, service consumers typically require a unified SLA
interface rather than raw module endpoints. Portal Backend provides that
northbound contract while internally coordinating semantic interpretation, risk,
decision, execution, immutability, and monitoring.

This is aligned with telecom service orchestration patterns that separate
customer-facing API surfaces from domain-internal control logic.

## D. Intuitive Explanation

An intuitive analogy is an "airline operations desk": it receives one customer
request, coordinates many internal teams, and returns one authoritative status
with all relevant context.

Conceptually, Portal Backend is the system narrator: it explains what the system
did, why it did it, and what happened next.

## E. End-to-End Role Narrative

Before Portal Backend orchestration, the user has only a request payload. After
Portal Backend completes processing, the user receives a consolidated response
containing decision, branch execution status, and lifecycle evidence.

This makes Portal Backend the end-to-end integration envelope for TriSLA.
