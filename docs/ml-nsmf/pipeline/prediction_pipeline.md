# ML-NSMF Prediction Pipeline

> **Operational SSOT:** [`docs/modules/ml-nsmf.md`](../../modules/ml-nsmf.md)

## Hot path (production)

```text
Decision Engine
    ↓ HTTP POST /api/v1/predict
DualLoadService.predict
    ↓
RiskPredictor.normalize → predict (RandomForest)
    ↓ optional predict_decision_class
    ↓ compute_slice_adjusted_risk
    ↓ explain (SHAP / LIME / metadata fallback)
    ↓ HTTP response { prediction, explanation }
Decision Engine admission rules
```

**Not in this path:** Kafka NEST intake, Prometheus queries, SEM direct push, candidate model output.

## Offline / validation paths (not hot)

- Candidate bundle load when `ML_DUAL_LOAD_ENABLED=true`
- Shadow logger (metadata events)
- Offline replay engine (golden vectors)

See canonical module doc § Dual load.
