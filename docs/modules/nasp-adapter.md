# NASP Adapter

## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

Canonical interface reference: [docs/modules/interfaces.md](interfaces.md).

Telemetry canonical reference: [docs/modules/telemetry.md](telemetry.md). NASP Adapter contributes Prometheus/MDCE signals, but MDCE is a capacity context, not the primary admission telemetry object.

> **Operational entry point** for the TriSLA NASP Adapter (Network Slice orchestration and infrastructure integration).
> Deep dives: [`docs/nasp-adapter/`](../nasp-adapter/README.md) (architecture, integration, interfaces, model, observability).
> Implementation SSOT: `apps/nasp-adapter/`. Digest SSOT: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.

## Role (frozen architecture)

NASP Adapter is the **post-admission orchestration and infrastructure integration layer**. It provisions Network Slice Instances (NSI) on Kubernetes, exposes multidomain metrics, and relays SLA registration to SEM-CSMF.

**Does:**

- Execute slice provisioning after Portal receives ACCEPT (`POST /api/v1/nsi/instantiate`)
- Collect and normalize multidomain metrics (RAN, transport, core)
- Forward SLA registration to SEM-CSMF (`POST /api/v1/sla/register`)
- Manage capacity reservations and optional 3GPP gate checks
- Annotate NSI CRDs with slice-service-binding metadata (O1C–O5C)

**Does not:**

- Make SLA admission decisions (Decision Engine via SEM-CSMF)
- Register on-chain (BC-NSSMF — Portal relay after orchestration)
- Receive direct admission requests from Decision Engine

Position in the frozen chain:

```text
Portal → SEM-CSMF → Decision Engine → ACCEPT
Portal → NASP Adapter (orchestration) → BC-NSSMF → SLA-Agent → Portal
```

## Operational baseline (Phase 47)

| Item | Value |
|------|-------|
| Deployment | `trisla-nasp-adapter` |
| Image | `ghcr.io/abelisboa/trisla-nasp-adapter` |
| Operational digest | `sha256:00dff9fbd57b1bdc36f5dd4ceb1274a38ce4d7f62355a341bcfde7082c99cb31` |
| Service port | `8085` (cluster: `http://trisla-nasp-adapter:8085`) |
| App version | `3.10.0` (`apps/nasp-adapter/src/main.py`) |
| Wave | Pre-wave (unchanged Wave 1 / Wave 3A / RC-P19 / RC-P20) |

## REST API catalog

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness + NASP connectivity detail |
| GET | `/metrics` | Prometheus scrape |
| **POST** | **`/api/v1/nsi/instantiate`** | **Primary orchestration** — create NSI CRD |
| POST | `/api/v1/sla/register` | Relay SLA registration → SEM-CSMF |
| GET | `/api/v1/nasp/metrics` | NASP real metrics (I-07) |
| GET | `/api/v1/metrics/multidomain` | MDCE SSOT schema |
| POST | `/api/v1/nasp/actions` | Platform actions (I-07) |
| GET/POST | `/api/v1/3gpp/gate` | 3GPP pre-provision gate |
| GET | `/api/v1/slice-service-binding/ssot` | SSB mapping config (read-only) |
| GET | `/api/v1/slice-service-binding/resolve` | SSB resolve preview |
| POST | `/api/v1/slice-service-binding/nssf/select` | O1C NSSF selection |
| GET | `/api/v1/slice-service-binding/nssf/status/{nsi_id}` | O1C NSSF status |
| POST | `/api/v1/slice-service-binding/amf/observe` | O2C AMF observe |
| POST | `/api/v1/slice-service-binding/smf/observe` | O2C SMF observe |
| POST | `/api/v1/slice-service-binding/pdu/correlate` | O2C PDU correlate |
| POST | `/api/v1/slice-service-binding/upf/observe` | O3C UPF observe |
| POST | `/api/v1/slice-service-binding/user-plane/correlate` | O3C user-plane correlate |
| POST | `/api/v1/slice-service-binding/ran/observe` | O4C RAN observe |
| POST | `/api/v1/slice-service-binding/access/correlate` | O4C access correlate |
| POST | `/api/v1/slice-service-binding/transport/observe` | O5C transport observe |
| POST | `/api/v1/slice-service-binding/transport/correlate` | O5C transport correlate |
| GET | `/api/v1/slice-service-binding/binding/status/{nsi_id}` | Full binding status |

**Primary production caller:** Portal Backend — `POST /api/v1/nsi/instantiate` when decision is ACCEPT and `orchestration_required` is true (`apps/portal-backend/src/services/nasp.py`).

## Runtime paths

### Admission (orchestration trigger — not decided here)

```text
Portal Backend → SEM-CSMF → Decision Engine → ACCEPT
Portal Backend → NASP Adapter POST /api/v1/nsi/instantiate
```

NASP Adapter runs **after** admission; it does not participate in the DE evaluation path.

### Provisioning

```text
POST /api/v1/nsi/instantiate
  → [GATE_3GPP_ENABLED] run_gate()
  → [CAPACITY_ACCOUNTING_ENABLED] ledger_check → TriSLAReservation PENDING
  → NSIController.create_nsi() → NetworkSliceInstance CRD
  → reservation ACTIVE (or rollback on failure)
```

Detail: [`docs/nasp-adapter/architecture/nasp_adapter_architecture.md`](../nasp-adapter/architecture/nasp_adapter_architecture.md)

### SLA registration

```text
POST /api/v1/sla/register (NASP Adapter)
  → POST {SEM_CSMF_URL}/api/v1/intents/register (SEM-CSMF)
```

## Integrations

| System | Direction | Mechanism |
|--------|-----------|-----------|
| **Portal Backend** | Portal → NASP | `POST /api/v1/nsi/instantiate` |
| **SEM-CSMF** | NASP → SEM | `POST /api/v1/intents/register` (via `/sla/register`) |
| **Kubernetes** | NASP → K8s API | NSI + TriSLAReservation CRDs (`trisla.io/v1`) |
| **Prometheus** | NASP → Prom | `PROMETHEUS_URL` queries; PRB gauge export |
| **Free5GC** | NASP → AMF/SMF SBI | `NASPClient` (`ns-1274485`, real mode) |
| **ONOS** | Binding adapter | Transport observe/correlate (O5C, env-gated) |
| **UERANSIM** | Binding adapter | RAN observe/correlate (O4C, env-gated) |

Decision Engine does **not** call NASP Adapter directly in the production admission path.

## Capacity accounting

When `CAPACITY_ACCOUNTING_ENABLED=true` (default):

| Stage | Action |
|-------|--------|
| Pre-instantiate | `ledger_check()` against multidomain headroom |
| Reserve | `ReservationStore.create_pending()` → CRD `TriSLAReservation` status PENDING |
| Success | `activate(reservation_id, nsi_id)` |
| Failure | `release(reservation_id, reason=...)` rollback |
| Background | Reconciler expires PENDING TTL + marks orphaned reservations |

Env: `RESERVATION_TTL_SECONDS` (default `300`), `RECONCILE_INTERVAL_SECONDS` (default `60`).

Code: `reservation_store.py`, `capacity_accounting.py`, `cost_model.py`

## 3GPP gate

When `GATE_3GPP_ENABLED=true`, `POST /api/v1/nsi/instantiate` runs `run_gate(nsi_spec)` before provisioning. Gate FAIL → HTTP 422, instantiate blocked.

Endpoints: `GET/POST /api/v1/3gpp/gate` for standalone validation.

Default: `GATE_3GPP_ENABLED=false`.

## Slice service binding (operational view)

Metadata-only binding chain stored as NSI CRD annotations (`binding_phase: METADATA_ONLY` by default):

| Track | Scope | Key endpoints |
|-------|-------|---------------|
| **O1C** | NSSF selection | `/nssf/select`, `/nssf/status/{nsi_id}` |
| **O2C** | AMF/SMF PDU | `/amf/observe`, `/smf/observe`, `/pdu/correlate` |
| **O3C** | UPF user plane | `/upf/observe`, `/user-plane/correlate` |
| **O4C** | RAN access | `/ran/observe`, `/access/correlate` |
| **O5C** | Transport (ONOS) | `/transport/observe`, `/transport/correlate` |

Status aggregate: `GET /api/v1/slice-service-binding/binding/status/{nsi_id}`

Feature flags: `SLICE_SERVICE_BINDING_ENABLED`, per-domain `*_BINDING_ENABLED` env vars.

## Observability

| Layer | Detail |
|-------|--------|
| Prometheus | `trisla_http_requests_total`, `trisla_http_request_duration_seconds`; `trisla_ran_prb_utilization` gauge |
| OTEL | FastAPI instrumentor; spans per route (`instantiate_nsi`, `collect_nasp_metrics`, etc.) |
| MDCE | `GET /api/v1/metrics/multidomain` — schema aligned with MDCE SSOT |
| PRB | RAN PRB exported via `metrics_collector.py` for Portal/Prometheus consumption |

Detail: [`docs/nasp-adapter/observability/observability.md`](../nasp-adapter/observability/observability.md)

## Environment variables (operational)

| Variable | Default | Role |
|----------|---------|------|
| `CAPACITY_ACCOUNTING_ENABLED` | `true` | Ledger + reservation before instantiate |
| `GATE_3GPP_ENABLED` | `false` | Block instantiate on gate FAIL |
| `SEM_CSMF_URL` | `http://trisla-sem-csmf...:8080` | SLA register relay |
| `PROMETHEUS_URL` | monitoring Prometheus | MDCE / CPU / mem queries |
| `NASP_MODE` | `real` | `mock` for dev |
| `RESERVATION_TTL_SECONDS` | `300` | PENDING reservation TTL |
| `RECONCILE_INTERVAL_SECONDS` | `60` | Background reconciler interval |
| `SLICE_SERVICE_BINDING_ENABLED` | config | O1C–O5C chain |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | otel collector | Trace export |
| `MULTIDOMAIN_METRICS_EXPORT_ENABLED` | off | O6 background exporter |

## Specialized documentation

| Topic | Location |
|-------|----------|
| Components and layers | [`docs/nasp-adapter/architecture/`](../nasp-adapter/architecture/nasp_adapter_architecture.md) |
| Infrastructure integration | [`docs/nasp-adapter/integration/`](../nasp-adapter/integration/nasp_integration.md) |
| REST contracts | [`docs/nasp-adapter/interfaces/`](../nasp-adapter/interfaces/interfaces.md) |
| Metric / MDCE model | [`docs/nasp-adapter/model/`](../nasp-adapter/model/metric_normalization_model.md) |
| Observability detail | [`docs/nasp-adapter/observability/`](../nasp-adapter/observability/observability.md) |

## Tests (repository)

```bash
cd apps/nasp-adapter
pytest tests/test_nasp_connectivity.py
pytest tests/test_slice_service_binding.py
pytest tests/test_nssf_adapter.py
pytest tests/test_amf_smf_binding.py
pytest tests/test_upf_binding.py
pytest tests/test_ran_binding.py
pytest tests/test_transport_binding.py
pytest tests/test_multidomain_metrics_exporter.py
```

## Canonical Telemetry Reference

Canonical telemetry reference: docs/modules/telemetry.md defines MDCE as NASP capacity context, not as the runtime telemetry_snapshot source.

## Canonical Observability Reference

Canonical observability reference: docs/modules/observability.md defines NASP Adapter metrics, OTEL tracing, health, dashboards, and alerting boundaries.
