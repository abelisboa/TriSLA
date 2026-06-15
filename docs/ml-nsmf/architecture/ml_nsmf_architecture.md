# ML-NSMF Architecture

> **Operational SSOT:** [`docs/modules/ml-nsmf.md`](../../modules/ml-nsmf.md)

Architecture, inference hot path, model inventory, and integration boundaries are maintained in the canonical module document to avoid duplication.

## Quick reference

| Layer | Module | Hot path |
|-------|--------|----------|
| HTTP ingress | `main.py` → `POST /api/v1/predict` | Yes |
| Orchestration | `dual_load_service.py` → `DualLoadService` | Yes |
| Inference | `prediction_pipeline.py` → `build_active_prediction` | Yes |
| Model | `predictor.py` → `RiskPredictor` | Yes |
| Slice XAI | `slice_risk_adjustment.py` | Yes |
| Explain | `predictor.explain` (SHAP/LIME/fallback) | Yes (conditional) |
| Kafka producer | `kafka_producer.py` | Conditional side effect |
| Kafka consumer | `kafka_consumer.py` | No |
| Prometheus client | `nasp_prometheus_client.py` | No |
| Legacy | `ml_nsmf.py` | No |

Frozen position: Decision Engine calls ML-NSMF synchronously; ML returns scores; DE decides SLA outcome.
