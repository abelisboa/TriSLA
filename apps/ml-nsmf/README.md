# ML-NSMF

ML-NSMF converts SLA and resource features into a viability score, a risk score, a risk level, and an explanation. The Decision Engine calls the service over HTTP during SLA evaluation.

## Service

- Framework: FastAPI 3.10.0
- HTTP port: `8081`
- Container entry point: `src.main:app`
- Kubernetes service: `trisla-ml-nsmf`

## HTTP API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service and active model status |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/api/v1/predict` | Generate a risk prediction |

See the [ML-NSMF documentation](../../docs/ml-nsmf/README.md) for request fields, examples, and runtime behavior.

## Source

- [FastAPI application](src/main.py)
- [Prediction pipeline](src/prediction_pipeline.py)
- [Predictor](src/predictor.py)
- [Model bundle loader](src/model_loader.py)


## Public Model Behavior

The public runtime loads only the active model and scaler configured by `ML_ACTIVE_MODEL_PATH` and `ML_ACTIVE_SCALER_PATH`. Candidate promotion, replay, shadow validation, and registry-governance workflows are not included.

Offline training requires an operator-supplied dataset path in `TRISLA_ML_TRAINING_DATASET`. The training command does not synthesize fallback data.
