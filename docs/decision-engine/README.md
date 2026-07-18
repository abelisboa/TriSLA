# Decision Engine

The Decision Engine is the admission component for TriSLA. SEM-CSMF calls `POST /evaluate` with a normalized intent, an optional NEST, and an optional telemetry snapshot. The service obtains an ML-NSMF prediction and returns an admission action with supporting metadata.

## Runtime contract

- HTTP service: `8082`
- gRPC listener: `50051`
- Health: `GET /health`
- Metrics: `GET /metrics`
- Evaluation: `POST /evaluate`
- Kubernetes service: `trisla-decision-engine`

The Helm chart configures `ML_NSMF_HTTP_URL` with the in-cluster ML-NSMF service address. Kafka processing is controlled by `KAFKA_ENABLED`; the HTTP evaluation path does not require a client to use Kafka.

## Documentation

- [Architecture](architecture/decision_engine_architecture.md)
- [HTTP interface](interfaces/interfaces.md)
- [Evaluation flow](pipeline/decision_flow.md)

## Implementation

- [Application](../../apps/decision-engine/src/main.py)
- [Models](../../apps/decision-engine/src/models.py)
- [Service](../../apps/decision-engine/src/service.py)
- [Engine](../../apps/decision-engine/src/engine.py)
