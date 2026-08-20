# TriSLA Helm Charts

This directory contains the Helm charts used to render TriSLA application
workloads. See the [repository overview](../README.md) for prerequisites,
installation guidance, and the current runtime flow.

## Charts

### `trisla`

The [`trisla`](trisla/) chart renders the main TriSLA services, including
SEM-CSMF, ML-NSMF, Decision Engine, NASP Adapter, SLA-Agent, Traffic Exporter,
and the RAN/UE/UPF proxy. Kafka is included as optional event transport.

The chart also preserves compatibility workloads. Its current templates render
BC-NSSMF and the earlier UI dashboard even when their corresponding values are
set to disabled. Besu is conditional and enabled by default. Review rendered
manifests before deploying when these components are not required.

### `trisla-portal`

The [`trisla-portal`](trisla-portal/) chart deploys the Portal frontend and
backend. The Portal is packaged separately from the main `trisla` chart.

### `trisla-besu`

The [`trisla-besu`](trisla-besu/) chart preserves the standalone Hyperledger
Besu deployment used by the BC-NSSMF compatibility path.

## Important deployment notes

- The charts do not deploy external RAN, transport-network, or 5GC
  infrastructure.
- The main chart does not deploy Prometheus, Grafana, OpenTelemetry Collector,
  Jaeger, Loki, or Tempo workloads. It can render monitoring custom resources
  that require the corresponding operators and backends to exist.
- A repository-supported current-core-only values profile is
  **EVIDENCE NOT AVAILABLE**. Inspect the rendered resources and provide
  environment-specific values before installation.

## Validation

From the repository root, run the read-only chart checks:

```bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
helm lint ./helm/trisla-portal
```
