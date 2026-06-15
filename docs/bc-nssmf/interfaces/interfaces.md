# BC-NSSMF Interfaces

> Specialized reference. Canonical cross-module interface truth: [`docs/modules/interfaces.md`](../../modules/interfaces.md).

**Operational reference:** [`docs/modules/bc-nssmf.md`](../../modules/bc-nssmf.md)

## Primary interface — HTTP I-04 (ACTIVE)

| Method | Path | Classification |
|--------|------|----------------|
| **POST** | **`/api/v1/register-sla`** | **SOLE COMMIT INGRESS** |

**Primary caller:** Portal Backend — `apps/portal-backend/src/services/nasp.py`

```text
Portal Backend
    ↓ POST http://trisla-bc-nssmf:8083/api/v1/register-sla
BC-NSSMF
    ↓ SLAContract.registerSLA()
Hyperledger Besu
```

**Not the primary caller:** Decision Engine does **not** call BC-NSSMF HTTP on the production hot path. DE may use `bc_client` for direct Besu Web3 when `BC_ENABLED=true` in the Decision Engine pod — **NOT HOT PATH**, default stub.

## Active REST endpoints

| Method | Path | Notes |
|--------|------|-------|
| GET | `/health` | Liveness probe |
| GET | `/health/ready` | Readiness — RPC + wallet |
| GET | `/metrics` | Prometheus |
| POST | `/api/v1/register-sla` | On-chain SLA registration |
| POST | `/api/v1/update-sla-status` | Status update (not Portal submit path) |
| GET | `/api/v1/get-sla/{sla_id}` | On-chain read |

## Stub

| Method | Path | Status |
|--------|------|--------|
| POST | `/api/v1/execute-contract` | **NOT HOT PATH** — simulated JSON only |

## Not implemented

| Method | Path | Status |
|--------|------|--------|
| POST | `/api/v1/governance-event` | **NOT IMPLEMENTED** |

## Non-hot-path interfaces

| Interface | Status |
|-----------|--------|
| Kafka I-04 (`trisla-i04-decisions`) | **NOT HOT PATH** — `DecisionConsumer` not started |
| gRPC | **NOT HOT PATH** — placeholder |
| Legacy REST `/bc/*` (`api_rest.py`) | **LEGACY / NOT WIRED** |
| MetricsOracle (NASP metrics) | **NOT HOT PATH** — stub only |
