# ML-NSMF

ML-NSMF provides the prediction service used by the Decision Engine. It normalizes an SLA feature payload, runs the active model, derives risk values, and returns an explanation.

## Runtime contract

- HTTP service: `8081`
- Health: `GET /health`
- Metrics: `GET /metrics`
- Prediction: `POST /api/v1/predict`
- Kubernetes service: `trisla-ml-nsmf`

The service requires a valid model and scaler at startup. The container includes the model assets used by the active predictor. Kafka output is optional and controlled by `KAFKA_ENABLED`.

## Documentation

- [Architecture](architecture/ml_nsmf_architecture.md)
- [HTTP interface](interfaces/interfaces.md)
- [Prediction flow](pipeline/prediction_pipeline.md)
- [Usage examples](examples/usage_examples.md)

## Implementation

- [Application](../../apps/ml-nsmf/src/main.py)
- [Predictor](../../apps/ml-nsmf/src/predictor.py)
- [Prediction pipeline](../../apps/ml-nsmf/src/prediction_pipeline.py)
