# SLA-Agent Layer

## 1. Overview

SLA-Agent Layer is the federated compliance and lifecycle validation subsystem
of TriSLA. It evaluates domain-level SLO status (RAN, Transport, Core) and
produces closed-loop evidence for SLA operation.

Its objective is post-decision operational validation and coordination.

## 2. Role in TriSLA Pipeline

$$
Input_{pipeline+telemetry} \rightarrow \text{SLA-Agent Layer} \rightarrow Output_{slo+lifecycle}
$$

Pipeline role:

- Receives pipeline execution events and domain telemetry.
- Computes per-domain and aggregate SLO compliance.
- Produces lifecycle evidence used by Portal Backend and observability paths.

## 3. Input Space (Formal)

Evaluation input:

$$
u_{sla} = \left( E, \mathcal{D}, \Lambda, \rho \right)
$$

Where:

- $E$: pipeline event payload (decision, orchestration, blockchain context).
- $\mathcal{D}$: domain metric observations.
- $\Lambda$: configured SLO target set.
- $\rho$: risk margin parameter from evaluator rules.

Primary endpoints (`apps/sla-agent-layer/src/main.py`):

- `POST /api/v1/ingest/pipeline-event`
- `GET /api/v1/slos`
- domain collect/action endpoints under `/api/v1/agents/*`

## 4. Output Space (Formal)

Compliance output:

$$
y_{sla} = \left( \sigma, \Gamma, \ell \right)
$$

Where:

- $\sigma$: overall status in $\{OK,RISK,VIOLATED\}$
- $\Gamma$: per-domain and per-metric compliance records
- $\ell$: lifecycle and explanation metadata

This output feeds global SLA status and lifecycle closure.

## 5. Runtime Behavior (Detailed)

1. Ingest pipeline event context and establish trace identity.
2. Collect domain metrics via dedicated agents or precomputed snapshots.
3. Load SLO policy definitions and evaluator operators.
4. Evaluate each metric against target and risk margin.
5. Aggregate per-domain status and global compliance rate.
6. Optionally coordinate federated actions/policies.
7. Publish lifecycle/compliance results and explanation artifacts.

Fallback mechanisms:

- Degraded operation when one or more domain data sources are unavailable.
- Partial-domain evaluation with explicit status transparency.

## 6. Data Model (Semantic)

Important fields:

- `status`: aggregate operational SLA state.
- `slos[]`: metric-level tuples (`target`, `current`, `operator`, `compliance`).
- `domain`: ownership boundary of each compliance result.
- `compliance_rate`, `violations`, `risks`: compact compliance summary.
- pipeline event metadata: links decision/execution steps to compliance outcome.

## 7. Mathematical Model

Per-metric evaluator:

$$
SLO_{status}=g(m,t,\rho,op)
$$

For $op = \le$:

- $OK$ if $m \le t$
- $RISK$ if $t < m \le t/\rho$
- $VIOLATED$ if $m > t/\rho$

For $op = \ge$:

- $OK$ if $m \ge t$
- $RISK$ if $t\rho \le m < t$
- $VIOLATED$ if $m < t\rho$

Global aggregation:

$$
Overall=
\begin{cases}
VIOLATED, & \exists\ violation\\
RISK, & \exists\ risk\ \land\ \nexists\ violation\\
OK, & \text{otherwise}
\end{cases}
$$

Interpretation:

- The layer formalizes whether executed service behavior respects contracted SLOs.
- It transforms telemetry observations into lifecycle-meaningful SLA evidence.

## 8. Integration with Decision Engine

SLA-Agent Layer consumes decision-derived pipeline events and evaluates their
operational consequences:

- `AC` paths produce execution-aware compliance states.
- `RENEG`/`REJ` paths are represented as skipped/non-executed operational paths.
- Resulting SLO evidence contextualizes decision quality over time.

## 9. Constraints and Assumptions

- Compliance quality depends on telemetry completeness and domain agent health.
- SLO semantics are operator-dependent and configuration-sensitive.
- The module evaluates and coordinates; it does not issue admission decisions.

## 10. Relation to Global Model $\Phi$

In:

$$
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
$$

Canonical global function: Φ(T, x, Policy, Telemetry) → (Decision, NSI, SLO, State).

SLA-Agent Layer realizes the $SLO$ component by mapping runtime telemetry and
pipeline context into formal compliance and lifecycle evidence.

## 11. Design Rationale

SLA-Agent Layer exists to separate post-decision compliance validation from
admission control. This protects decision latency while enabling richer
domain-specific SLO analysis and federated coordination.

Alternative monolithic design (Decision + compliance in one service) was not
chosen due to coupling, reduced observability, and weaker maintainability.

## 12. Evolution and Design Decisions

Current runtime reflects three important decisions:

- explicit per-domain agent decomposition (RAN/Transport/Core);
- unified SLO status lattice (`OK`, `RISK`, `VIOLATED`);
- pipeline-event ingestion to connect execution outcomes to compliance evidence.

These decisions improved traceability between decision output and operational SLA
behavior.

## 13. Example Walkthrough

Input:

- pipeline event with decision/orchestration context
- domain telemetry snapshots
- configured SLO targets/operators

Processing:

- The module ingests the event, binds trace context, and evaluates metric-level
  SLOs across RAN, Transport, and Core domains.
- Per-domain compliance states are aggregated into a global SLA compliance
  status.

Output:

- The layer publishes lifecycle and compliance evidence for Portal Backend and
  observability pipelines.

Impact:

- The output does not alter the original decision process, but it determines
  whether the realized network slice remains compliant over time.

## 14. Impact on SLA Decision

The layer does not alter the initial admission action, but it determines whether
an accepted SLA remains operationally compliant over time.

Critical variables:

- metric-to-target deviations
- risk-margin parameter $\rho$

Its outputs influence renegotiation and lifecycle governance in subsequent cycles.

## 15. Operational Considerations

- Requires domain telemetry availability and synchronized metric timestamps.
- Depends on correctly versioned SLO configuration files.
- In partial telemetry conditions, outputs remain valid but carry degraded
  confidence semantics.

## A. Technical Narrative

SLA-Agent Layer provides continuous post-decision governance by converting
runtime telemetry into compliance evidence. It exists to ensure that an admitted
service remains within contracted objectives after deployment.

The module is separated from Decision Engine because admission and compliance are
different control problems: one is prospective (should we admit?), the other is
retrospective/continuous (is the service still compliant?).

Its operation combines domain-specific evaluators and aggregation logic,
producing `OK/RISK/VIOLATED` states and lifecycle metadata that connect
operational reality with SLA governance.

## B. Operational Perspective

In real networks, SLA-Agent Layer is most valuable under dynamic load and domain
instability. As congestion or degradation appears in one domain, the module
surfaces risk/violation status before full SLA collapse.

Its impact is operational continuity: it enables earlier corrective workflows and
reduces blind spots between admission-time estimates and runtime service quality.

## C. Telecom Context

In 5G slicing and O-RAN contexts, service quality emerges from multiple domains
with different failure modes. SLA-Agent Layer explicitly models this by
evaluating RAN, transport, and core objectives separately and then aggregating
them into SLA-level status.

This is central to SLA management in multi-domain mobile infrastructures.

## D. Intuitive Explanation

An intuitive view is that SLA-Agent Layer is a "continuous quality inspector."
Decision Engine grants entry, but SLA-Agent keeps checking whether the service
continues to meet the promised operating envelope.

It translates many low-level metrics into a small, actionable compliance state.

## E. End-to-End Role Narrative

Before SLA-Agent Layer, the pipeline has decision and execution outcomes. After
SLA-Agent Layer, the system obtains formal compliance evidence and lifecycle
status suitable for dashboards, audits, and corrective policies.

This closes the end-to-end loop from intent admission to observed SLA behavior.
