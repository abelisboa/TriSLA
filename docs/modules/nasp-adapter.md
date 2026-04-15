# NASP Adapter

## 1. Overview

NASP Adapter is TriSLA's infrastructure actuation and multidomain telemetry
bridge. It converts decision authorization into concrete NSI operations under
3GPP gate and capacity-accounting constraints.

It is the execution boundary between control-plane logic and runtime substrate.

## 2. Role in TriSLA Pipeline

$$
Input_{decision} \rightarrow \text{NASP Adapter} \rightarrow Output_{nsi+telemetry}
$$

Pipeline role:

- Consumes accepted decision paths for NSI instantiation.
- Exposes multidomain telemetry snapshots to control modules.
- Returns orchestration status used by blockchain and lifecycle stages.

## 3. Input Space (Formal)

Actuation input:

$$
u_{nasp} = \left( a, \nu, g, c \right)
$$

Where:

- $a$: decision action from Decision Engine.
- $\nu$: NSI payload (`nsiId`, `serviceProfile`, `tenantId`, `nssai`, `sla`).
- $g$: 3GPP gate state.
- $c$: capacity accounting state.

Primary endpoints (`apps/nasp-adapter/src/main.py`):

- `POST /api/v1/nsi/instantiate`
- `GET/POST /api/v1/3gpp/gate`
- `GET /api/v1/metrics/multidomain`

## 4. Output Space (Formal)

Execution output:

$$
y_{nasp} = \left( o, \mu, \kappa \right)
$$

Where:

- $o$: orchestration result (`success`, `failed`, `skipped`)
- $\mu$: multidomain metrics payload
- $\kappa$: structured reason/error metadata

This output determines whether blockchain registration and lifecycle progression
are executed or skipped.

## 5. Runtime Behavior (Detailed)

1. Collect RAN/Core/Transport telemetry from NASP/Prometheus-backed paths.
2. Normalize and expose multidomain metrics with explicit availability reasons.
3. On NSI instantiation request:
   - sanitize payload to runtime-compatible naming/schema constraints;
   - evaluate 3GPP gate (when enabled);
   - evaluate capacity reservation/accounting (when enabled);
   - instantiate NSI and activate flow, or rollback reservation on failure.
4. Return orchestration state and detail payload.

Fallback mechanisms:

- Degraded telemetry mode with `reasons` fields for missing domains.
- Safe failure path on gate/capacity violation without partial commit.

## 6. Data Model (Semantic)

Semantically central fields:

- `nsiId`: orchestration identity for lifecycle traceability.
- `serviceProfile` / `nssai`: execution profile for network slice realization.
- `sla`: runtime SLA constraints coupled to actuation.
- `core.upf.*`, `ran.ue.active_count`, `transport.rtt_p95_ms`: domain pressure
  observables influencing policy and validation.
- `reasons`: explicit telemetry quality indicators.

## 7. Mathematical Model

Orchestration feasibility:

$$
NSI=\operatorname{instantiate} \iff (a=ACCEPT)\land(Gate3GPP=PASS)\land(Capacity=PASS)
$$

Telemetry projection:

$$
\mu = \mathcal{M}(core,ran,transport,timestamp,reasons)
$$

Optional pressure normalization:

$$
z_i^{norm}=\frac{z_i-z_i^{min}}{z_i^{max}-z_i^{min}}
$$

Interpretation:

- NASP Adapter is a constrained executor: decision approval is necessary but not
  sufficient; gate and capacity constraints are jointly required.
- This module operationalizes the transition from symbolic decision to physical
  network state.

## 8. Integration with Decision Engine

Direct coupling:

- `AC` enables orchestration attempt.
- `RENEG`/`REJ` paths skip NSI instantiation by design.
- Telemetry exposed by NASP Adapter can be fed back into risk/policy evaluation.

Thus, NASP Adapter is the first physical consequence of Decision Engine output.

## 9. Constraints and Assumptions

- Depends on NASP controllers, Kubernetes API access, and telemetry services.
- Gate and capacity features are configuration-dependent.
- NSI naming/CRD compatibility constraints are enforced at runtime.

## 10. Relation to Global Model $\Phi$

In:

$$
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
$$

Canonical global function: Φ(T, x, Policy, Telemetry) → (Decision, NSI, SLO, State).

NASP Adapter realizes the $NSI$ component and contributes telemetry feedback
that conditions later compliance and lifecycle state.

## 11. Design Rationale

NASP Adapter exists to decouple decision logic from infrastructure-specific
actuation details (controllers, CRD interactions, telemetry aggregation).

This separation preserves a clean control-to-execution boundary and allows
infrastructure evolution without altering decision mathematics. Trade-off:
additional integration complexity in exchange for stronger modularity.

## 12. Evolution and Design Decisions

Important design decisions reflected in runtime:

- explicit 3GPP gate integration before execution;
- capacity accounting checks to prevent overcommitment;
- payload sanitization and rollback paths for safe failure handling.

These decisions were made to reduce execution-side inconsistency and preserve
lifecycle correctness under partial failures.

## 13. Example Walkthrough

Input:

- Decision action: `AC`
- PRB context available from multidomain telemetry
- NSI payload: `nsiId`, `serviceProfile`, `tenantId`, `nssai`, `sla`

Processing:

- The module validates and sanitizes the network slice payload, then evaluates
  3GPP gate and capacity-accounting constraints.
- The orchestration branch is resolved by execution feasibility rather than by
  semantic intent alone.

Output:

- If all constraints pass, NSI instantiation is executed; otherwise, the module
  returns a blocked orchestration state with explicit reason metadata.

Impact:

- NASP Adapter determines whether an accepted SLA request becomes an active
  network slice in runtime infrastructure.

## 14. Impact on SLA Decision

NASP Adapter does not generate `AC`/`REJ`, but it determines whether an accepted
decision becomes an executed service instance.

Critical variables:

- gate pass/fail state
- capacity pass/fail state

Therefore it controls execution feasibility of `AC` outcomes.

## 15. Operational Considerations

- Requires Kubernetes/NASP control-plane reachability.
- Depends on multidomain telemetry paths for richer feedback.
- Gate/capacity behavior is configuration-dependent and must be explicitly set in
  reproducibility setups.

## A. Technical Narrative

NASP Adapter is the infrastructure realization layer of TriSLA. It exists to
translate approved control intents into concrete NSI actions while preserving
domain-specific execution safety through gate and capacity constraints.

The module is separated from Decision Engine to avoid mixing policy semantics
with platform-specific actuation complexity. This decomposition protects the
mathematical decision model from infrastructure heterogeneity and enables
independent evolution of execution connectors.

Operationally, NASP Adapter validates execution preconditions, sanitizes payloads,
evaluates gate/capacity policies, and commits or rejects orchestration attempts
with explicit reasons. It is the first stage where decision intent acquires
physical network effect.

## B. Operational Perspective

In real environments, NASP Adapter behavior is strongly influenced by control
plane availability and current resource headroom. Under load, capacity checks can
block overcommitment and convert accepted intents into safely rejected execution
attempts.

Its network impact is immediate: successful calls instantiate or update slice
resources; failed checks preserve stability by preventing unsafe allocations.

## C. Telecom Context

For 5G slicing and O-RAN-aligned operations, this module anchors the transition
from logical slice decisions to executable network slice instances. It also
contributes multidomain observability (RAN/Core/Transport) needed for SLA-aware
closed-loop behavior.

In SLA management terms, NASP Adapter is where contractual intent is tested
against real infrastructure feasibility.

## D. Intuitive Explanation

A practical analogy is that NASP Adapter functions as a "deployment control
tower": even when a request is authorized, it checks runway conditions (gate and
capacity) before allowing execution.

Conceptually, it answers: "Can this accepted decision be safely materialized on
the network right now?"

## E. End-to-End Role Narrative

Before NASP Adapter, the system has a decision action but no physical service
realization. After NASP Adapter, the pipeline has execution evidence
(`success/failed/skipped`) and multidomain state that govern downstream
blockchain and lifecycle branches.

This makes NASP Adapter the execution hinge of the complete pipeline.
