# BC-NSSMF

## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

Canonical interface reference: [docs/modules/interfaces.md](interfaces.md).

> **Operational entry point** for the TriSLA Blockchain-enabled Network Slice Subnet Management Function.
> Deep dives: [`docs/bc-nssmf/`](../bc-nssmf/README.md) (Besu integration, interfaces, research contract model).
> Implementation SSOT: `apps/bc-nssmf/`. Digest SSOT: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.


## Canonical Governance Reference

For cross-module governance ownership, metadata propagation, lineage classification, and rendering boundaries, use [`docs/modules/governance.md`](governance.md). BC-NSSMF is the **On-Chain Evidence Authority**: it produces `tx_hash`, `block_number`, and `bc_status`; it does not produce `governance_registration_*` metadata.

## Role (frozen architecture)

BC-NSSMF is the **On-Chain Evidence Authority**. It receives SLA registration requests from the Portal Backend, encodes SLOs, submits signed transactions to Hyperledger Besu, and returns on-chain evidence (`tx_hash`, `block_number`, `bc_status`).

**BC-NSSMF does not decide SLA.**  
**BC-NSSMF does not generate governance.**  
**BC-NSSMF does not compose governance metadata.**  
**BC-NSSMF registers on-chain evidence.**

**Does:**

- Commit SLA records via `POST /api/v1/register-sla` (**sole commit ingress**)
- Sign and submit transactions to Besu through `SLAContract.registerSLA()`
- Return transaction receipt fields to the caller
- Expose health, readiness, and HTTP Prometheus metrics

**Does not:**

- Make admission decisions (Decision Engine)
- Compose `governance_registration_*` fields (Portal Backend)
- Persist governance metadata to SEM (Portal → SEM PATCH)
- Accept Kafka as production ingress (consumer not started)
- Emit `governance_registration` blocks in HTTP responses (`governance_lineage.py` not wired)

Position in the frozen chain:

```text
Portal Backend → SEM-CSMF → Decision Engine (via SEM /intents)
Portal Backend → NASP Adapter (orchestration, if ACCEPT)
Portal Backend → BC-NSSMF POST /api/v1/register-sla (if ACCEPT + orchestration SUCCESS)
Portal Backend → SEM PATCH /api/v1/intents/{id}/governance-metadata (10G.4)
Portal Backend → SLA-Agent ingest (conditional, if COMMITTED)
Portal Backend → Frontend (Governance Panel, 10G.8)
```

## Operational baseline (Phase 47)

| Item | Value |
|------|-------|
| Deployment | `trisla-bc-nssmf` |
| Image | `ghcr.io/abelisboa/trisla-bc-nssmf` |
| Operational digest | `sha256:b0db5eef2128baddee2c1c3ea72fb5fec421afb1d87407e5f4a6aadd75f9f95a` |
| HTTP port | `8083` (cluster: `http://trisla-bc-nssmf:8083`) |
| App version | `3.10.0` (`apps/bc-nssmf/src/main.py`) |
| Blockchain | **Hyperledger Besu** (Helm `besu.enabled: true`) |
| Chain ID | `1337` |
| Consensus | **QBFT** |
| Wave 1 / Wave 3A | **Unchanged** at operational freeze |

Source: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.

## REST API catalog

### Active

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness — `status`, `enabled`, `rpc_connected` |
| GET | `/health/ready` | Readiness — RPC + wallet; 503 if degraded |
| GET | `/metrics` | Prometheus scrape (`trisla_http_*`) |
| **POST** | **`/api/v1/register-sla`** | **SOLE COMMIT INGRESS** — register SLA on-chain |
| POST | `/api/v1/update-sla-status` | Update on-chain SLA status (not Portal hot path) |
| GET | `/api/v1/get-sla/{sla_id}` | Read SLA from chain (not Portal hot path) |

**Primary caller:** Portal Backend — `apps/portal-backend/src/services/nasp.py` → `POST {bc_nssmf_url}/api/v1/register-sla` when `decision == ACCEPT` and `nasp_orchestration_status == SUCCESS`.

### Stub — NOT HOT PATH

| Method | Path | Status |
|--------|------|--------|
| POST | `/api/v1/execute-contract` | **NOT HOT PATH** — returns simulated JSON; does **not** submit chain transactions |

### Not implemented

| Method | Path | Status |
|--------|------|--------|
| POST | `/api/v1/governance-event` | **NOT IMPLEMENTED** — no handler in `main.py`; do not document as operational |

## Commit hot path

**Classification: SOLE COMMIT INGRESS**

```text
Portal Backend (NASPService.submit pipeline)
    ↓ POST /api/v1/register-sla
BC-NSSMF (main.register_sla → BCService.register_sla)
    ↓ SLAContract.registerSLA()
Hyperledger Besu
    ↓ receipt
tx_hash, block_number, bc_status=COMMITTED
    ↓ HTTP response
Portal Backend (sla.py — governance metadata composition)
    ↓ PATCH SEM /api/v1/intents/{id}/governance-metadata
Frontend (Governance Panel — Sprint 10G.8)
```

**Preconditions (Portal):**

- `decision == ACCEPT`
- NASP orchestration `SUCCESS` → BC call attempted
- Orchestration failure → `bc_status: SKIPPED_ORCH_FAILED` (no BC call)
- Non-ACCEPT → `bc_status: SKIPPED`

**Degraded BC:** `BC_ENABLED=false` or RPC offline → HTTP **503** with `{tx_hash: null, status: "ERROR"}`; Portal sets `BLOCKCHAIN_FAILED` / `DEGRADED_FALLBACK`.

Detailed interface contract: [`docs/bc-nssmf/interfaces/interfaces.md`](../bc-nssmf/interfaces/interfaces.md).

## Request contract — `POST /api/v1/register-sla`

Portal sends (among others):

| Field | Role |
|-------|------|
| `intent_id` | Customer key / correlation |
| `nest_id` | NEST reference |
| `sla_requirements` | Dict (`latency`, `throughput`, `reliability`, `template_id`) → flattened to SLOs |
| `decision` | e.g. `ACCEPT` → `service_name` fallback |
| `metadata` | Passed through; **not** used by BC to compose governance blocks |

Also accepts schema v1.0 (`slo_set`) or legacy `slos[]`.

## Response contract — success

| Field | Description |
|-------|-------------|
| `status` | `"COMMITTED"` |
| `bc_status` | `"COMMITTED"` |
| `tx_hash` | Transaction hash (hex) |
| `block_number` | Block number |
| `sla_id` | Set to `customer` string (intent_id), not numeric on-chain ID |
| `correlation_id` | From `correlation_id` / `intent_id` |

**Not returned by BC:** `governance_registration_id`, `lifecycle_lineage`, `governance_registration_status` — these are composed by Portal.

## Smart contracts

| Contract | Status |
|----------|--------|
| **`SLAContract.sol`** | **ACTIVE** — sole on-chain contract |
| Penalty contracts | **TRACEABILITY_ONLY** — not in runtime |
| Compensation contracts | **TRACEABILITY_ONLY** — not in runtime |
| Registry contracts | **TRACEABILITY_ONLY** — NOT RUNTIME; lineage helpers are Python-only and unwired |

### SLAContract.sol — active functions

| Function | Used by | Purpose |
|----------|---------|---------|
| `registerSLA(customer, serviceName, slaHash, slos)` | `BCService.register_sla` | Create on-chain SLA record |
| `updateSLAStatus(slaId, newStatus)` | `BCService.update_status` | Status transition |
| `getSLA(slaId)` | `BCService.get_sla` | Read on-chain SLA |

Solidity enum: `REQUESTED, APPROVED, REJECTED, ACTIVE, COMPLETED`.

**Known inconsistency:** REST `update-sla-status` maps string statuses (`CREATED`, `ACTIVE`, `VIOLATED`, `RENEGOTIATED`, `CLOSED`) to integers that do not align 1:1 with the Solidity enum — **LEGACY / not Portal hot path**.

Research-only alternate struct: [`docs/bc-nssmf/contracts/sla_contract_model.md`](../bc-nssmf/contracts/sla_contract_model.md).

## Runtime transaction flow

```text
BCService.register_sla()
    ↓ encode registerSLA(...) transaction data
build_and_send_signed_tx()          (apps/bc-nssmf/src/blockchain/tx_sender.py)
    ↓ load_account() — BC_PRIVATE_KEY
    ↓ pending nonce (BC_TX_QUEUE_ENABLED=true)
    ↓ gas estimate + BC_MIN_GAS_PRICE_WEI floor
send_raw_transaction
    ↓ retry on nonce/replacement errors (up to 3, gas bump BC_GAS_BUMP_PERCENT)
wait_for_transaction_receipt        (timeout BC_TX_RECEIPT_TIMEOUT, default 60s)
    ↓ receipt.status == 1 required
tx_hash + block_number → HTTP response
```

| Mechanism | Detail |
|-----------|--------|
| **Retry** | Up to `_MAX_RETRIES = 3` on replacement/nonce errors |
| **Nonce locking** | `threading.Lock` per sender when `BC_TX_QUEUE_ENABLED=true` |
| **Gas bump** | `BC_GAS_BUMP_PERCENT` (default 20%) on retry |
| **Timeout** | `BC_TX_RECEIPT_TIMEOUT` seconds (default 60) |
| **Balance check** | Zero balance → `BCBusinessError` (422) before send |
| **Receipt validation** | `receipt.status != 1` → `BCInfrastructureError` (503) |

Fallback path (no local wallet): `contract.functions.*.transact({"from": account})` via `eth_accounts` — **LEGACY**.

## Governance runtime truth

**Governance metadata = Portal Backend** — not BC-NSSMF.

### BC-NSSMF produces

| Field | Where |
|-------|-------|
| `tx_hash` | HTTP response |
| `block_number` | HTTP response |
| `bc_status` | HTTP response (`COMMITTED` or error) |

### Portal composes

| Field | Source |
|-------|--------|
| `governance_registration_status` | `sla.py` from `bc_status` + DE `governance_event` flags |
| `governance_registration_tx_hash` | Copied from BC `tx_hash` when committed |
| `governance_registration_fallback` | `true` when BC not committed or tx absent |
| `governance_registration_block_number` | From BC response |
| `governance_event_id`, `portal_governance_role` | Relay from DE metadata when authority flags set |

Code: `apps/portal-backend/src/routers/sla.py` (FASE 4 relay), `apps/portal-backend/src/services/governance_metadata.py`.

### Portal persists

```text
PATCH http://trisla-sem-csmf:8080/api/v1/intents/{intent_id}/governance-metadata
```

Sprint **10G.4** — `NASPService.persist_intent_governance_metadata` → SEM merges into `extra_metadata`.

### Frontend renders

Governance Panel — Sprint **10G.8** / **10G.9** — reads submit/status metadata (`tx_hash`, `bc_status`, `governance_registration_*`).

## Governance lineage module

| Component | Status |
|-----------|--------|
| `apps/bc-nssmf/src/governance_lineage.py` | **NOT WIRED** |

Helpers exist (`normalize_governance_event`, `build_governance_registration_id`, `build_lifecycle_lineage`, `build_governance_response_block`) but are **not imported** by `main.py`. Do **not** document as active runtime behavior.

## Blockchain runtime truth

### Active

| Component | Detail |
|-----------|--------|
| **Hyperledger Besu** | Private chain, Helm deployment, RPC `:8545` |
| **Web3 HTTPProvider** | `BESU_RPC_URL` / `TRISLA_RPC_URL` / `BC_RPC_URL` |
| **BC_PRIVATE_KEY** | Secret `bc-nssmf-wallet` — local signing |
| **Signed transactions** | `build_and_send_signed_tx` primary path |
| **Contract loading** | `contract_address.json` (ConfigMap mount) |

### Not operational

| Technology | Status |
|------------|--------|
| Ethereum Mainnet | **NOT OPERATIONAL** |
| Hyperledger Fabric | **NOT OPERATIONAL** |
| Ganache runtime | **NOT OPERATIONAL** (dev compose only) |
| Hardhat runtime | **NOT OPERATIONAL** |
| Mock blockchain | **NOT OPERATIONAL** — degraded mode returns 503, not fake tx |

Besu details: [`docs/bc-nssmf/blockchain/besu_integration.md`](../bc-nssmf/blockchain/besu_integration.md).

## Integrations

| Integration | Status |
|-------------|--------|
| **Portal Backend** | **ACTIVE** — sole production caller of `register-sla` |
| **Hyperledger Besu** | **ACTIVE** — when `besu.enabled` + `BC_ENABLED=true` |
| **SLAContract** | **ACTIVE** — on-chain registration |
| **SLA-Agent notification** | **CONDITIONAL** — Portal `_notify_sla_agent_pipeline` after COMMITTED; requires `SLA_AGENT_PIPELINE_INGEST_URL` |
| **Decision Engine `bc_client`** | **NOT HOT PATH** — direct Web3 to Besu when `BC_ENABLED=true` in DE; default stub (`BC_ENABLED=false`); bypasses BC-NSSMF HTTP |
| **Kafka Consumer** (`DecisionConsumer`) | **NOT HOT PATH** — instantiated when BC enabled; loop never started; `KAFKA_ENABLED=false` default |
| **gRPC Server** | **NOT HOT PATH** — placeholder in `api_grpc_server.py` |
| **MetricsOracle** | **NOT HOT PATH** — hardcoded stub metrics; only referenced by execute-contract stub |
| **SEM-CSMF direct** | **NOT HOT PATH** — no direct SEM → BC call |

## Persistence

| Store | Role |
|-------|------|
| **On-chain** | `SLAContract` storage on Besu ledger |
| **ConfigMap** | `trisla-bc-contract-address` → `contract_address.json` (address + ABI) |
| **Secret** | `bc-nssmf-wallet` → `BC_PRIVATE_KEY` |

**NO SQL · NO ORM · NO CACHE · NO LOCAL DATABASE**

BC-NSSMF holds no application database, snapshots, or offline ledger beyond the Besu node.

## Observability

| Layer | Status |
|-------|--------|
| **HTTP Prometheus metrics** | **ACTIVE** — `trisla_http_requests_total`, `trisla_http_request_duration_seconds`; `GET /metrics` |
| **Health / Readiness** | **ACTIVE** — `/health`, `/health/ready` (K8s probes) |
| **OTEL traces** | **PARTIAL** — FastAPI instrumentor; spans on register/update; OTLP optional (`OTLP_ENABLED`) |
| **`trisla_bc_transactions_total`** | **NOT WIRED** — defined in `observability/metrics.py`, not called from hot path |

## Legacy and non-hot paths

| Component | Status |
|-----------|--------|
| `api_rest.py` router `/bc/register`, `/bc/update`, `/bc/{sla_id}` | **LEGACY / NOT WIRED** in `main.py` |
| `service.register_sla_on_chain(decision_result)` | **NOT HOT PATH** — I-06 helper for Kafka/DE integration; unused in production HTTP flow |
| DE → BC direct (`bc_client.register_sla_on_chain`) | **NOT HOT PATH** — parallel path; stub by default |
| Kafka `trisla-i04-decisions` | **NOT HOT PATH** — consumer code present; not started |
| `execute-contract` DEPLOY/EXECUTE | **NOT HOT PATH** — stub responses |
| Status enum REST vs Solidity mismatch | **LEGACY** — update-sla-status mapping |

## Key environment variables

| Variable | Default / Helm | Role |
|----------|----------------|------|
| `BC_ENABLED` | `true` when Besu enabled | Enable Web3 + contract loading |
| `BESU_RPC_URL` / `TRISLA_RPC_URL` | Besu service `:8545` | RPC for `BCService` |
| `BC_RPC_URL` | Same Besu URL | RPC for `tx_sender` |
| `BC_PRIVATE_KEY` | Secret mount | Transaction signing |
| `CONTRACT_INFO_PATH` / `CONTRACT_ADDRESS_PATH` | `/app/src/contracts/contract_address.json` | Contract ABI + address |
| `BC_TX_QUEUE_ENABLED` | `true` | Sequential nonce lock |
| `BC_TX_RECEIPT_TIMEOUT` | `60` | Receipt wait seconds |
| `BC_GAS_BUMP_PERCENT` | `20` | Retry gas increase |
| `BC_MIN_GAS_PRICE_WEI` | `1000000000` | Gas price floor |
| `KAFKA_ENABLED` | `false` | Kafka consumer (off) |
| `OTLP_ENABLED` | `false` | Legacy OTLP span exporter |

## Related documentation

| Topic | Location |
|-------|----------|
| HTTP interface (I-04) | [`docs/bc-nssmf/interfaces/interfaces.md`](../bc-nssmf/interfaces/interfaces.md) |
| Besu integration | [`docs/bc-nssmf/blockchain/besu_integration.md`](../bc-nssmf/blockchain/besu_integration.md) |
| Research contract model | [`docs/bc-nssmf/contracts/sla_contract_model.md`](../bc-nssmf/contracts/sla_contract_model.md) — **NOT RUNTIME SSOT** |
| Portal governance relay | [`docs/modules/portal-backend.md`](portal-backend.md) |
| Decision Engine (no BC HTTP) | [`docs/modules/decision-engine.md`](decision-engine.md) |
| E2E flow | [`docs/TRISLA_E2E_FLOW_CANONICAL.md`](../TRISLA_E2E_FLOW_CANONICAL.md) |

## Canonical Observability Reference

Canonical observability reference: docs/modules/observability.md defines BC-NSSMF metrics, OTEL tracing, health/readiness, dashboards, and alerting boundaries.
