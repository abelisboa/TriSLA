# NASP Adapter Interfaces

> Specialized reference. Canonical cross-module interface truth: [`docs/modules/interfaces.md`](../../modules/interfaces.md).

> Operational REST catalog: [`docs/modules/nasp-adapter.md`](../../modules/nasp-adapter.md).
> Architecture: [`architecture/nasp_adapter_architecture.md`](../architecture/nasp_adapter_architecture.md).

## 1. Primary Operational Caller

**Portal Backend → NASP Adapter**

Production orchestration is triggered by Portal after SLA ACCEPT:

```text
POST http://trisla-nasp-adapter.trisla.svc.cluster.local:8085/api/v1/nsi/instantiate
```

Client: `apps/portal-backend/src/services/nasp.py` (`NASPService.submit_template_to_nasp`)

Conditions: decision `ACCEPT` and `orchestration_required=true` (or legacy ACCEPT fallback when DE authority flags absent).

Decision Engine does **not** call NASP Adapter directly in the admission path.

## 2. Core Production Endpoints

### POST `/api/v1/nsi/instantiate`

Creates a `NetworkSliceInstance` CRD on Kubernetes.

**Request (conceptual):**

```json
{
  "nsiId": "nsi-intent-001",
  "serviceProfile": "URLLC",
  "tenantId": "tenant-001",
  "nestId": "nest-001",
  "nssai": { "sst": 2, "sd": "000001" },
  "sla": { "latency": "10ms", "reliability": 0.999 }
}
```

**Response (success):**

```json
{
  "success": true,
  "nsi": { },
  "binding_phase": "METADATA_ONLY",
  "message": "NSI instantiated successfully"
}
```

Pre-checks when enabled: 3GPP gate (`GATE_3GPP_ENABLED`), capacity ledger (`CAPACITY_ACCOUNTING_ENABLED`).

### POST `/api/v1/sla/register`

Idempotent SLA registration relay to SEM-CSMF.

```text
NASP Adapter POST /api/v1/sla/register
  → SEM-CSMF POST /api/v1/intents/register
```

Payload SSOT: `sla_id`, `status`, `slice_type`, `template`, `created_at`, `source`.

Env: `SEM_CSMF_URL` (default `http://trisla-sem-csmf.trisla.svc.cluster.local:8080`).

## 3. Metrics and Actions (I-07)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/nasp/metrics` | NASP infrastructure metrics |
| GET | `/api/v1/metrics/multidomain` | MDCE SSOT schema export |
| POST | `/api/v1/nasp/actions` | Execute platform action |

## 4. 3GPP Gate

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/3gpp/gate` | Gate status (no payload) |
| POST | `/api/v1/3gpp/gate` | Validate SLA/NSI pre-conditions |

When `GATE_3GPP_ENABLED=true`, failed gate on instantiate returns HTTP 422.

## 5. Slice Service Binding (O1C–O5C)

Operational endpoints for metadata binding and status. See full list in [`docs/modules/nasp-adapter.md`](../../modules/nasp-adapter.md).

Aggregate status: `GET /api/v1/slice-service-binding/binding/status/{nsi_id}`

## 6. Health and Observability

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness + `nasp_connected` detail |
| GET | `/metrics` | Prometheus scrape |

## 7. Interface Summary

Production wire path: **Portal Backend → POST `/api/v1/nsi/instantiate`**. Metrics endpoints support observability and MDCE; SLA register relays to SEM-CSMF. No direct Decision Engine ingress.
