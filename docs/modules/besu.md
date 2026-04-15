# Besu

## Role of Blockchain

Besu provides the blockchain runtime used by TriSLA for immutable SLA lifecycle
evidence. It is the execution substrate for BC-NSSMF contract interactions.

## SLA Lifecycle Persistence

SLA registration and status transition events are persisted via on-chain
transactions, producing verifiable identifiers (e.g., transaction hash and block
metadata where available).

## Immutability

Once committed, lifecycle records become tamper-evident. This supports
trustworthy audit trails across decision and orchestration branches.

## Auditability

Besu-backed persistence enables post-event verification of SLA state history,
which is essential for governance, compliance review, and scientific traceability
in end-to-end experiments.
