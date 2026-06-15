# NASP Integration

> Operational entry: [`docs/modules/nasp-adapter.md`](../../modules/nasp-adapter.md).

## 1. Portal Backend

| Item | Value |
|------|-------|
| Direction | Portal → NASP Adapter |
| Endpoint | `POST /api/v1/nsi/instantiate` |
| Env (Portal) | `NASP_ADAPTER_URL` → `http://trisla-nasp-adapter:8085` |
| Trigger | ACCEPT + `orchestration_required` |
| Code | `apps/portal-backend/src/services/nasp.py` |

Portal orchestrates after Decision Engine response; NASP is not in the SEM→DE admission chain.

## 2. SEM-CSMF

| Item | Value |
|------|-------|
| Direction | NASP Adapter → SEM-CSMF |
| Endpoint | `POST /api/v1/intents/register` |
| Ingress at NASP | `POST /api/v1/sla/register` |
| Env | `SEM_CSMF_URL` |

Relay only — NASP forwards registration payload; SEM persists intent metadata.

## 3. Kubernetes

| Item | Value |
|------|-------|
| API | CustomObjectsApi (in-cluster) |
| CRDs | `NetworkSliceInstance`, `TriSLAReservation` (`trisla.io/v1`) |
| Controller | `NSIController`, `ReservationStore` |
| Watch | `nsi_watch_controller` (background) |

NASP Adapter requires in-cluster credentials for production provisioning.

## 4. Prometheus

| Item | Value |
|------|-------|
| Env | `PROMETHEUS_URL` |
| Default | `http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090` |
| Usage | CPU/mem/UE proxy queries; MDCE multidomain endpoint |
| Export | `trisla_ran_prb_utilization` gauge |

Prometheus metrics feed Portal telemetry collection and SEM PRB resolution (via Portal proxy), not a direct DE→NASP API path.

## 5. Free5GC (Core)

| Item | Value |
|------|-------|
| Mode | `NASP_MODE=real` (default) or `mock` |
| Namespace | `ns-1274485` |
| Endpoints | AMF/SMF SBI via `NASPClient` / `nasp_connectivity.py` |
| Startup | Connectivity probe on boot |

Env overrides: `NASP_CORE_AMF_ENDPOINT`, `NASP_CORE_SMF_ENDPOINT`, `NASP_FREE5GC_NAMESPACE`, etc.

## 6. ONOS (Transport — O5C)

| Item | Value |
|------|-------|
| Adapter | `transport_binding_adapter.py` |
| Default REST | `http://onos.nasp-transport.svc.cluster.local:8181` |
| Env | `TRANSPORT_BINDING_ENABLED`, `ONOS_REST_URL` |

Read-only observation and correlation; `binding_phase: METADATA_ONLY`.

## 7. UERANSIM (RAN — O4C)

| Item | Value |
|------|-------|
| Adapter | `ran_binding_adapter.py` |
| Namespace | `ueransim` (default via `SSB_RAN_NAMESPACE`) |
| Env | `RAN_BINDING_ENABLED` |

RAN binding via AMF NGAP log parse or cluster fetch.

## 8. Integration Summary

NASP Adapter integrates upward with Portal (orchestration) and SEM (registration), and downward with Kubernetes, Prometheus, Free5GC, ONOS, and UERANSIM. Decision Engine integration is **indirect** via Portal orchestration policy, not direct HTTP.
