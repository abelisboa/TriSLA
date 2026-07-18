# Decision Evaluation Flow

## Processing sequence

1. FastAPI validates the request as `SLAEvaluateInput`.
2. The service reads the optional RAN, transport, and core telemetry values.
3. The NEST resolver normalizes the optional NEST payload.
4. `DecisionService` creates a `DecisionInput` from the intent, NEST, telemetry, and context.
5. The ML client derives the ML feature payload and calls `POST /api/v1/predict` on ML-NSMF.
6. The decision logic combines SLA constraints, telemetry, the NEST, and the prediction.
7. The result is serialized as `DecisionResult` and retained in the process decision store.

```text
SLAEvaluateInput
    ▼
Input and NEST normalization
    ▼
ML-NSMF prediction
    ▼
Decision evaluation
    ▼
AC | RENEG | REJ
```

## Failure behavior

If the ML-NSMF HTTP call fails, the ML client returns a medium-risk fallback prediction so the decision path can complete. Request validation errors are returned by FastAPI. Unhandled evaluation errors return an HTTP server error.

## Runtime controls

| Variable | Purpose | Default |
|---|---|---|
| `ML_NSMF_HTTP_URL` | ML-NSMF base URL | `http://127.0.0.1:8081` |
| `HTTP_PORT` | HTTP configuration value | `8082` |
| `GRPC_PORT` | gRPC listener | `50051` |
| `KAFKA_ENABLED` | Enable Kafka components | `false` |
| `OTLP_ENABLED` | Enable OTLP span export | `false` |

The deployed HTTP command binds to `0.0.0.0:8082`.
