# BC-NSSMF

## 1. Overview

BC-NSSMF is the immutable SLA state registrar of TriSLA. It persists SLA
lifecycle events on blockchain and returns cryptographic transaction evidence.

Its responsibility is auditability and state integrity, not admission control.

## 2. Role in TriSLA Pipeline

\[
Input_{orchestration/lifecycle\ event} \rightarrow \text{BC-NSSMF} \rightarrow Output_{on\text{-}chain\ state}
\]

Pipeline role:

- Receives SLA registration/update events from successful workflow branches.
- Commits lifecycle transitions on-chain.
- Exposes query/status APIs for verifiable audit trace.

## 3. Input Space (Formal)

Blockchain input:

\[
u_{bc}=(id,\omega,\varsigma,e)
\]

Where:

- \(id\): SLA identity tuple.
- \(\omega\): SLO/value payload to persist.
- \(\varsigma\): requested state transition.
- \(e\): event type (`register`, `update`, or contract execution request).

Primary endpoints (`apps/bc-nssmf/src/main.py`):

- `POST /api/v1/register-sla`
- `POST /api/v1/update-sla-status`
- `POST /api/v1/execute-contract`

## 4. Output Space (Formal)

Commit output:

\[
y_{bc}=(state,tx,b)
\]

Where:

- \(state\): persisted SLA state.
- \(tx\): transaction identifier (`tx_hash`).
- \(b\): block metadata (e.g., block number when available).

This output becomes immutable evidence for lifecycle traceability.

## 5. Runtime Behavior (Detailed)

1. Validate request schema (current and legacy-compatible paths).
2. Normalize SLA payload and status representation.
3. Execute contract interaction for registration or status update.
4. Map semantic status labels to contract-compatible representation.
5. Return commit confirmation and transaction metadata.
6. Expose read API for state retrieval by `sla_id`.

Fallback mechanisms:

- Degraded behavior when blockchain is disabled/unreachable (configuration-driven
  modes in runtime service layer).

## 6. Data Model (Semantic)

Key entities (`apps/bc-nssmf/src/models.py`):

- `SLARegisterRequest`: canonical on-chain registration payload.
- `SLAStatusUpdateRequest`: lifecycle transition request.
- `ContractExecuteRequest`: explicit contract interaction wrapper.

Operational status mapping:

- `CREATED -> 0`
- `ACTIVE -> 1`
- `VIOLATED -> 2`
- `RENEGOTIATED -> 3`
- `CLOSED -> 4`

## 7. Mathematical Model

State space:

\[
SLA_{state}\in\{CREATED,ACTIVE,VIOLATED,RENEGOTIATED,CLOSED\}
\]

Transition operator:

\[
SLA_{state}(t+1)=B(SLA_{state}(t),e_t)
\]

Commit evidence relation:

\[
\operatorname{commit}(e_t)\Rightarrow(tx\_hash,block,\ SLA_{state}(t+1))
\]

Interpretation:

- \(B\) formalizes the contract-level transition function.
- The module ensures lifecycle transitions are auditable and tamper-evident.

## 8. Integration with Decision Engine

BC-NSSMF is indirectly controlled by Decision Engine through orchestration flow:

- `AC` + successful orchestration leads to registration/update paths.
- Non-accepted or failed-execution branches are marked as skipped/non-committed.
- On-chain state therefore encodes realized decision outcomes.

## 9. Constraints and Assumptions

- Depends on blockchain RPC availability and contract deployment health.
- State semantics are constrained by contract status model.
- Write latency is blockchain-dependent and external to control logic.

## 10. Relation to Global Model \(\Phi\)

In:

\[
\Phi(T,x,Policy,Telemetry)\rightarrow(Decision,NSI,SLO,State)
\]

BC-NSSMF realizes the \(State\) projection by persisting lifecycle transitions
as verifiable on-chain state.

## 11. Design Rationale

BC-NSSMF exists to provide immutable, externally verifiable SLA lifecycle
records. It is separated from orchestration and decision logic to preserve
audit guarantees and avoid mixing control decisions with persistence concerns.

Trade-off: blockchain integration adds latency and operational dependencies, but
provides tamper-evident state history required for scientific/audit use cases.

## 12. Evolution and Design Decisions

Current design incorporates:

- explicit status mapping between service-level labels and contract-level
  representation;
- compatibility paths for legacy payloads;
- dedicated write/read API split for lifecycle operations.

These decisions were made to keep backward compatibility while preserving
contract-state consistency.

## 13. Example Walkthrough

Input:

- `register-sla` payload with identity and SLO tuple set
- subsequent `update-sla-status` event

Step 1:

- Validate and normalize registration payload.

Step 2:

- Commit transaction and return `tx_hash`/block metadata.

Step 3:

- Apply status update event and persist new state transition.

Step 4:

- Retrieve `sla_id` to verify immutable lifecycle progression.

## 14. Impact on SLA Decision

BC-NSSMF does not compute admission action, but it determines persistence of
decision consequences in immutable state.

Critical variable:

- lifecycle state transition event (`register`/`update`)

Its presence is decisive for traceability and accountability of accepted flows.

## 15. Operational Considerations

- Requires healthy blockchain RPC and deployed contract artifacts.
- Sensitive to transaction finalization latency.
- Operational monitoring should include commit failures and state-query mismatch
  checks.

## A. Technical Narrative

BC-NSSMF is the immutability and auditability layer of TriSLA. It exists to
persist SLA lifecycle transitions as verifiable blockchain evidence rather than
mutable application-only records.

The module is separated from orchestration and decision components to preserve
clear responsibility boundaries: control modules decide and execute, BC-NSSMF
records and proves what happened. This design strengthens forensic traceability
and non-repudiation.

Its runtime operation validates payloads, maps semantic statuses to contract
state representations, commits transactions, and exposes read paths for
post-event verification.

## B. Operational Perspective

In operational settings, BC-NSSMF introduces a latency-cost trade-off for strong
audit guarantees. Under load, transaction throughput and finalization time become
key constraints, especially for high-frequency lifecycle updates.

Despite this overhead, the module improves governance resilience by providing
tamper-evident history across decision and execution branches.

## C. Telecom Context

For 5G slicing SLA management, disputes often concern whether a state transition
actually occurred and when. BC-NSSMF addresses this by anchoring SLA lifecycle
events in an immutable ledger, supporting transparent cross-domain accountability.

This is particularly relevant in multi-actor telecom ecosystems where trust
boundaries are explicit.

## D. Intuitive Explanation

A simple analogy is a notarized ledger: modules may report events, but BC-NSSMF
is where those events are irreversibly recorded and later proven.

Conceptually, it answers: "Can we cryptographically verify this SLA lifecycle
history?"

## E. End-to-End Role Narrative

Before BC-NSSMF, the pipeline has execution outcomes and lifecycle intent. After
BC-NSSMF, those outcomes become immutable state evidence (`tx_hash`, block
context), which can be consumed by audits and long-term governance workflows.

This positions BC-NSSMF as the trust-preserving backbone of the end-to-end flow.
