# BC-NSSMF — Blockchain-Based SLA Enforcement Layer

## 1. Overview

The BC-NSSMF (Blockchain-enabled Network Slice Subnet Management Function) is responsible for ensuring the immutability, traceability, and enforceability of Service Level Agreements (SLAs) within the TriSLA architecture.

It provides a trust layer that guarantees that SLA decisions are permanently recorded and auditable.

---

## 2. Role in TriSLA

Pipeline:

SEM-CSMF -> ML-NSMF -> Decision Engine -> BC-NSSMF -> Blockchain

The BC-NSSMF is activated only after the SLA decision is made.

---

## 3. Core Function

The module ensures:

- Immutable SLA registration
- SLA lifecycle tracking
- Smart contract-based enforcement
- Auditability of decisions

---

## 4. SLA Lifecycle Representation

Each SLA follows:

REQUESTED -> APPROVED -> ACTIVE -> COMPLETED / VIOLATED

These states are stored on-chain.

---

## 5. Trust Model

The blockchain guarantees:

- Integrity (data cannot be altered)
- Transparency (full history available)
- Non-repudiation (actions are signed)

---

## 6. Relation to Decision Model

The BC-NSSMF does not decide SLA acceptance.

It enforces:

Decision -> Contract -> Immutable Record

---

## 7. Summary

The BC-NSSMF transforms SLA decisions into verifiable, tamper-proof contracts, ensuring trustworthiness in multi-domain network environments.
