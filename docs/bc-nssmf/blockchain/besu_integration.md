# Besu Blockchain Integration

Canonical module reference: [`docs/modules/bc-nssmf.md`](../../modules/bc-nssmf.md).
Canonical interface reference: [`docs/modules/interfaces.md`](../../modules/interfaces.md).

## Overview

TriSLA uses Hyperledger Besu to store SLA transactions.

---

## Configuration

- Consensus: IBFT2
- RPC: 8545
- Network ID: 1337

---

## Flow

BC-NSSMF -> RPC -> Besu -> Transaction -> Block

---

## Guarantees

- Deterministic execution
- Fast finality
- Permissioned control

