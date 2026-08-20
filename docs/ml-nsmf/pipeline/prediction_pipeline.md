# ML Prediction Flow

## Scientific Baseline versus Runtime Detail

In the current article, the evaluated ML baseline is a Random Forest classifier
with detailed SHAP attribution executed asynchronously in a background worker.
The article reports a cumulative predictive latency of 231.66 ms, including
118.59 ms of explainability overhead.

The sequence below documents the preserved public runtime implementation. Its
conditional SHAP/LIME/fallback explanation may be assembled on the request path
and must not be presented as the scientific prototype's background SHAP path.

## Processing sequence

1. The FastAPI endpoint receives the JSON feature payload.
2. The active prediction pipeline normalizes the configured feature columns.
3. Derived ratios and pressure values are added where required by the loaded model.
4. The active model produces a viability score.
5. The predictor calculates `risk_score = 1 - viability_score` and clamps it to the `0..1` range.
6. The risk score is mapped to `low`, `medium`, or `high`.
7. An explanation is generated from available model importance data, SHAP, or LIME support.
8. The response includes the prediction, explanation, model identifier, and timing fields.

```text
Feature JSON
    ▼
Normalization
    ▼
Model inference
    ▼
Viability and risk calculation
    ▼
Explanation
    ▼
JSON response
```

## Startup behavior

The model and scaler are required. If either asset cannot be resolved or validated, service initialization fails instead of serving an unbacked prediction.

## Runtime controls

| Variable | Purpose | Default |
|---|---|---|
| `ML_ACTIVE_MODEL_PATH` | Active model file | `/app/models/viability_model.pkl` |
| `ML_ACTIVE_SCALER_PATH` | Active scaler file | `/app/models/scaler.pkl` |
| `ML_MODEL_REGISTRY_DIR` | Optional model registry directory | `/app/models/registry` |
| `KAFKA_ENABLED` | Enable prediction event output | `false` |
| `KAFKA_BROKERS` | Kafka broker list | empty |
