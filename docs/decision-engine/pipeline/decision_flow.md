# Decision Flow

> **Operational SSOT:** [`docs/modules/decision-engine.md`](../../modules/decision-engine.md) — § Production hot path, § Admission logic SSOT

Minimal summary (details in canonical doc):

```text
SEM-CSMF → POST /evaluate
  → telemetry_snapshot + intent → ML-NSMF /api/v1/predict
  → engine._apply_decision_rules → DecisionResult
  → explainability pipeline → echo metadata/NEST → SEM-CSMF
```

Portal orchestration (NASP Adapter) and BC registration occur **after** DE returns ACCEPT — not inside the DE hot path.
