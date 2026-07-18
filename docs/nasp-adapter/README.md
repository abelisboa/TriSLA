# NASP Adapter

The NASP Adapter is the platform integration service for network-slice provisioning and domain observations. It creates Kubernetes Network Slice Instance resources, communicates with core-network services, exposes telemetry, and provides optional RAN and transport correlation operations.

## Runtime contract

- HTTP service: `8085`
- Health: `GET /health`
- Metrics: `GET /metrics`
- NSI creation: `POST /api/v1/nsi/instantiate`
- Kubernetes service: `trisla-nasp-adapter`

The live service reports connectivity to AMF, SMF, and NRF through its health response. The Helm deployment supplies an in-cluster service account and enables the core readiness check and capacity accounting settings.

## Documentation

- [Architecture](architecture/nasp_adapter_architecture.md)
- [Integration](integration/nasp_integration.md)
- [HTTP interface](interfaces/interfaces.md)
- [SLA normalization](model/metric_normalization_model.md)
- [Observability](observability/observability.md)

## Implementation

- [Application](../../apps/nasp-adapter/src/main.py)
- [NASP client](../../apps/nasp-adapter/src/nasp_client.py)
- [NSI controller](../../apps/nasp-adapter/src/controllers/nsi_controller.py)
