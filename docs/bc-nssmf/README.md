# BC-NSSMF — Documentation Index

**Operational reference:** [`docs/modules/bc-nssmf.md`](../modules/bc-nssmf.md)

This directory holds specialized references only. Commit path, governance truth, smart contracts, transaction flow, and integrations are documented in the operational module doc — not duplicated here.

## Contents

| Document | Purpose |
|----------|---------|
| [`interfaces/interfaces.md`](interfaces/interfaces.md) | HTTP I-04 primary contract; Portal as caller |
| [`blockchain/besu_integration.md`](blockchain/besu_integration.md) | Besu/QBFT cluster configuration |
| [`contracts/sla_contract_model.md`](contracts/sla_contract_model.md) | Research model — **NOT RUNTIME SLAContract.sol** |
| [`architecture/bc_nssmf_architecture.md`](architecture/bc_nssmf_architecture.md) | Pointer to canonical architecture |
| [`pipeline/sla_lifecycle.md`](pipeline/sla_lifecycle.md) | Non-hot-path summary / pointer |

## External SSOT (read-only)

- `apps/bc-nssmf/src/` — implementation
- `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json` — operational digest `sha256:b0db5eef…`
- `apps/portal-backend/src/services/nasp.py` — production BC caller
