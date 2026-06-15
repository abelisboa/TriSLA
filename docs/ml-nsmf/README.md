# ML-NSMF — Documentation Index

**Operational reference:** [`docs/modules/ml-nsmf.md`](../modules/ml-nsmf.md)

This directory holds specialized references only. Inference path, models, XAI, training, and integrations are documented in the operational module doc — not duplicated here.

## Contents

| Document | Purpose |
|----------|---------|
| [`interfaces/interfaces.md`](interfaces/interfaces.md) | HTTP I-05 primary contract; conditional Kafka |
| [`architecture/ml_nsmf_architecture.md`](architecture/ml_nsmf_architecture.md) | Pointer to canonical architecture |
| [`model/ml_model.md`](model/ml_model.md) | Research model — **NOT OPERATIONAL SSOT** |
| [`pipeline/prediction_pipeline.md`](pipeline/prediction_pipeline.md) | Hot path summary / pointer |
| [`examples/usage_examples.md`](examples/usage_examples.md) | Offline training and local predictor checks |

## External SSOT (read-only)

- `apps/ml-nsmf/src/` — implementation
- `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json` — operational digest
- `model-registry/traceability/MODEL_TRACEABILITY_MATRIX.json` — prod vs scientific models
