# ML-NSMF Prediction Pipeline

## Flow

1. Receive NEST (Kafka)
2. Collect real-time metrics
3. Extract features
4. Normalize data
5. Run ML model
6. Generate explanation
7. Send prediction

---

## Domains

- RAN -> PRB utilization
- Transport -> latency, jitter
- Core -> CPU, memory

---

## Detailed Operational Steps

### 1) NEST Intake

- Consumes messages from SEM-CSMF output stream (Kafka I-02)
- Validates payload schema and correlation identifiers (`intent_id`, `nest_id`)

### 2) Runtime Metrics Retrieval

- Queries current multi-domain telemetry
- Aligns metric timestamps to prediction window

### 3) Feature Construction

- Combines SLA requirements from NEST with runtime metrics
- Applies feature engineering and categorical encodings

### 4) Preprocessing

- Applies trained scaler/normalizer
- Ensures compatibility with model training distribution

### 5) Inference

- Executes trained model to compute feasibility score S
- Captures inference metadata (model version, latency)

### 6) Explainability

- Computes feature attribution (SHAP/LIME or fallback)
- Generates interpretable explanation payload

### 7) Output Dispatch

- Publishes score and explanation to Decision Engine (Kafka I-03)

---

## Output

Prediction:

```json
{
  "score": 0.82,
  "decision": "REJECT",
  "explanation": {
    "top_factors": ["latency", "cpu_utilization", "active_slices"],
    "method": "SHAP"
  }
}
```

## Reproducibility Notes

- Keep model and scaler versions pinned per campaign
- Preserve full feature vector and inference metadata in logs
- Track message IDs across I-02 -> prediction -> I-03 for auditability
