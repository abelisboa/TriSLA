# NASP Adapter Integration

## Portal Backend

The Portal Backend calls `POST /api/v1/nsi/instantiate` after an accepted SLA requires orchestration. It may also read NASP metrics and submit supported NASP actions.

## SEM-CSMF

`POST /api/v1/sla/register` forwards an SLA registration to SEM-CSMF `POST /api/v1/intents/register`. The `SEM_CSMF_URL` variable selects the SEM-CSMF service.

## Kubernetes

The adapter uses the Kubernetes Custom Objects API to manage `NetworkSliceInstance` resources in the `trisla.io/v1` API group. The deployment uses an in-cluster service account and starts a resource watch thread with the application.

## Core network

In `NASP_MODE=real`, the NASP client resolves AMF, SMF, NRF, and optional UPF service endpoints. The health response reports the configured core namespace and connectivity probe results.

## RAN and transport

Optional endpoints can observe and correlate RAN access, core sessions, user-plane data, and transport state. Their corresponding Helm flags are disabled by default unless explicitly enabled.

## Prometheus

`PROMETHEUS_URL` configures metric queries. The adapter exposes service metrics at `/metrics`, collected NASP measurements at `/api/v1/nasp/metrics`, and a multidomain view at `/api/v1/metrics/multidomain`.

## Main configuration

| Variable | Purpose |
|---|---|
| `SEM_CSMF_URL` | SEM-CSMF base URL |
| `NASP_MODE` | Select real or mock endpoint resolution |
| `NASP_CORE_AMF_ENDPOINT` | AMF service endpoint |
| `NASP_CORE_SMF_ENDPOINT` | SMF service endpoint |
| `NASP_CORE_NRF_ENDPOINT` | NRF service endpoint |
| `PROMETHEUS_URL` | Prometheus service URL |
| `GATE_3GPP_ENABLED` | Require readiness checks before instantiation |
| `CAPACITY_ACCOUNTING_ENABLED` | Enable capacity reservations |
