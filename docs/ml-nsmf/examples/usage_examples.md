# ML-NSMF Usage Examples

> **Operational SSOT:** [`docs/modules/ml-nsmf.md`](../../modules/ml-nsmf.md)  
> Production inference is **HTTP only** — `POST /api/v1/predict` called by Decision Engine.

## 1. Offline training

```bash
cd apps/ml-nsmf
python training/train_model.py
```

Training is **offline only** — no runtime retraining.

## 2. Predictor load check (local)

```bash
cd apps/ml-nsmf
python -c "from src.predictor import RiskPredictor; p = RiskPredictor(); print('Model loaded successfully!')"
```

## 3. HTTP predict (mirrors production caller)

```bash
curl -s -X POST http://localhost:8081/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id": "intent-demo",
    "latency": 12.0,
    "throughput": 120.0,
    "reliability": 0.999,
    "jitter": 2.1,
    "packet_loss": 0.001,
    "slice_type": "URLLC",
    "slice_type_encoded": 1,
    "cpu_utilization": 0.1,
    "memory_utilization": 0.1,
    "network_bandwidth_available": 10000.0,
    "active_slices_count": 1
  }'
```

## 4. Troubleshooting

- **Model artifact missing:** verify `viability_model.pkl` and `scaler.pkl` (BUNDLE-OP-001 paths)
- **Startup failure:** S34.2 requires model + scaler — no mock fallback
- **Unexpected scores:** verify feature schema matches training; check `slice_adjusted_risk_score` in response
- **XAI method `feature_importance`:** SHAP/LIME may have failed — check logs; not an admission failure

## 5. Reproducibility checklist

- Pin operational digest: `sha256:b0922b2199830a766a6fd999213583973bc8209862f39a949de2d18010017187`
- Record `model_used`, `classifier_loaded`, and `risk_formula` from response
- Correlate `intent_id` across DE logs and ML `[ML_PREDICT]` lines
