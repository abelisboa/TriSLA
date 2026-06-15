# NASP Adapter Architecture

> Operational catalog and endpoints: [`docs/modules/nasp-adapter.md`](../../modules/nasp-adapter.md).
> Integration targets: [`integration/nasp_integration.md`](../integration/nasp_integration.md).

## 1. Architectural Position

NASP Adapter sits between TriSLA control-plane modules and physical/virtual infrastructure. Its primary production responsibility is **post-ACCEPT NSI provisioning** invoked by Portal Backend.

```text
Portal Backend → NASP Adapter → Kubernetes (NSI CRD)
                              → Free5GC / Prometheus / binding adapters
```

Admission evaluation occurs upstream (Portal → SEM-CSMF → Decision Engine). NASP Adapter does not re-evaluate SLA decisions.

## 2. Main Components

| Component | File / package | Role |
|-----------|----------------|------|
| FastAPI app | `main.py` | REST surface, startup bootstrap |
| **NSIController** | `controllers/nsi_controller.py` | Create/manage `NetworkSliceInstance` CRDs |
| **NSI Watch Controller** | `controllers/nsi_watch_controller.py` | Background CRD watch (daemon thread) |
| **ReservationStore** | `reservation_store.py` | `TriSLAReservation` CRD ledger |
| **Capacity accounting** | `capacity_accounting.py`, `cost_model.py` | Pre-instantiate headroom check |
| **NASPClient** | `nasp_client.py`, `nasp_connectivity.py` | Free5GC AMF/SMF/RAN/transport probes |
| **MetricsCollector** | `metrics_collector.py` | NASP + Prometheus multidomain collection |
| **Multidomain exporter** | `multidomain_metrics_exporter.py` | O6 optional background export |
| **ActionExecutor** | `action_executor.py` | Platform actions via I-07 |
| **3GPP Gate** | `gate_3gpp.py` | Pre-provision validation |
| **Slice service binding** | `slice_service_binding.py`, `nssf_adapter.py`, `*_binding_adapter.py`, `*_correlation.py` | O1C–O5C metadata chain |
| **K8s auth** | `controllers/k8s_auth.py` | In-cluster config validation |

## 3. Persistence Model

No SQL database. State is held in Kubernetes CRDs:

| CRD | Kind | Purpose |
|-----|------|---------|
| `trisla.io/v1` | `NetworkSliceInstance` | Provisioned slice instance |
| `trisla.io/v1` | `TriSLAReservation` | Capacity ledger (PENDING → ACTIVE) |

NSI annotations store slice-service-binding metadata (`trisla.io/*` keys).

## 4. Processing Layers

### 4.1 Input Layer

- REST on port `8085`
- Primary payload: NSI spec (`nsiId`, `serviceProfile`, `nssai`, `sla`, `tenantId`, `nestId`)
- Payload sanitization: `_sanitize_nsi_payload()` in `main.py`

### 4.2 Guard Layer

- Optional **3GPP gate** (`GATE_3GPP_ENABLED`)
- **Capacity ledger** check + reservation (`CAPACITY_ACCOUNTING_ENABLED`)

### 4.3 Provisioning Layer

- `NSIController.create_nsi()` — real K8s CRD creation
- Enrichment via slice-service-binding annotations during create

### 4.4 Observability Layer

- Prometheus HTTP middleware + domain gauges
- OTEL spans on all major routes
- MDCE endpoint for structured multidomain export

## 5. Background Services (startup)

| Service | Trigger | Role |
|---------|---------|------|
| NSI Watch Controller | `startup_event` | Reconcile NSI CRD events |
| Capacity reconciler | `CAPACITY_ACCOUNTING_ENABLED` | Expire PENDING reservations; detect orphans |
| NASP connectivity probe | `startup_event` | AMF/SMF reachability (`NASPClient.connect()`) |
| O6 metrics exporter | `MULTIDOMAIN_METRICS_EXPORT_ENABLED` | Periodic multidomain push (default off) |

## 6. Instantiate Flow (summary)

Provisioning lifecycle detail lives here (no separate pipeline doc):

1. Receive `POST /api/v1/nsi/instantiate`
2. Sanitize NSI payload (RFC1123 `nsiId`, SLA normalization)
3. Optional 3GPP gate → FAIL blocks with 422
4. Optional capacity ledger → reservation PENDING
5. `NSIController.create_nsi()` → K8s CRD
6. Activate reservation or rollback on failure
7. Return NSI + binding annotations in response

Full operational context: [`docs/modules/nasp-adapter.md`](../../modules/nasp-adapter.md).

## 7. Architecture Summary

NASP Adapter isolates infrastructure complexity from Portal and SEM-CSMF. By confining provisioning, metrics, and binding metadata to a dedicated module, the architecture preserves the frozen admission boundary while enabling real-world slice instantiation on Kubernetes.
