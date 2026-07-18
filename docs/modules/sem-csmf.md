# SEM-CSMF

## Runtime Position In TriSLA Flow

Runtime position and cross-module flow ordering are defined by [`docs/modules/interfaces.md`](interfaces.md). This module document does not duplicate the full chain.

Canonical interface reference: [docs/modules/interfaces.md](interfaces.md).


## Canonical Governance Reference

Cross-module flow and evidence boundaries are documented in [`docs/modules/interfaces.md`](interfaces.md). SEM-CSMF is the **Governance Metadata Persistence Layer**: it merges allowed governance keys into intent `extra_metadata` through `PATCH /api/v1/intents/{intent_id}/governance-metadata`.

Telemetry canonical reference: [docs/modules/telemetry.md](telemetry.md). SEM-CSMF forwards  and conditional  to Decision Engine.

> **Operational entry point** for the Semantic-Enhanced Communication Service Management Function.
> Deep dives: [`docs/sem-csmf/`](../sem-csmf/README.md) (architecture, pipeline, interfaces, ontology, examples).
> Implementation SSOT: `apps/sem-csmf/`. Digest SSOT: `baseline-registry/OPERATIONAL_BASELINE_REGISTRY.json`.

## Role (frozen architecture)

SEM-CSMF is the **semantic front layer**. It interprets SLA intents, validates them against the ontology, materializes GST/NEST artifacts, and forwards structured input to the Decision Engine via **I-01 HTTP**.

**Does:**

- NL / structured intent interpretation (`POST /api/v1/interpret`)
- Full admission preprocessing + I-01 dispatch (`POST /api/v1/intents`)
- Semantic fill of missing KPI fields (`semantic_resolver.py`)
- GSMA-aligned parallel metadata (`canonical_sla.py`)
- Governance field persistence (`PATCH .../governance-metadata`)
- Intent/NEST persistence and status queries

**Does not:**

- Make final SLA admission decisions (Decision Engine)
- Orchestrate NASP or register on-chain (Portal → NASP Adapter / BC-NSSMF)
- Publish to Kafka in the production `/intents` path (I-02 is **LEGACY** code only)

Position in the frozen chain:

```text
Portal Backend → SEM-CSMF → Decision Engine (I-01 HTTP)
                         ↘ (Portal continues) NASP Adapter → BC-NSSMF → SLA-Agent → Portal
```

## Operational baseline (Phase 47)

| Item | Value |
|------|-------|
| Deployment | `trisla-sem-csmf` |
| Image | `ghcr.io/abelisboa/trisla-sem-csmf` |
| Operational digest | `sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23` |
| Service port | `8080` (cluster: `http://trisla-sem-csmf:8080`) |
| App version | `3.10.0` (`apps/sem-csmf/src/main.py`) |
| Wave 3A | NEST transmission on I-01 — `TRACEABILITY_ONLY` (`SEM_I01_NEST_TRANSMIT=true` default) |

Rollback digest (Wave 3A pin): `sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a`

## REST API (ingress)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/metrics` | Prometheus (HTTP middleware + OTEL) |
| POST | `/api/v1/interpret` | NL interpretation → GST/NEST + `canonical_sla`; **no DB persist, no DE call** |
| POST | `/api/v1/intents` | **Primary admission path** — persist → pipeline → I-01 → `IntentResponse` |
| GET | `/api/v1/intents/{intent_id}` | Intent status (Portal polling) |
| PATCH | `/api/v1/intents/{intent_id}/governance-metadata` | Merge BC/governance keys into `extra_metadata` |
| POST | `/api/v1/intents/register` | Idempotent NASP SLA registration |
| GET | `/api/v1/nests/{nest_id}` | NEST retrieval |
| GET | `/api/v1/slices` | List slices from persisted NESTs |
| POST | `/api/v1/nest` | Stub create endpoint |
| POST | `/api/v1/auth/login` | Dev JWT (optional; `ENABLE_AUTH=false` default) |

**Primary callers:** Portal Backend (`NASPService.call_sem_csmf`) — `POST /api/v1/interpret`, `POST /api/v1/intents`, `GET /api/v1/intents/{id}`.

## Runtime paths (summary)

Detailed lifecycle: [`docs/sem-csmf/pipeline/processing_pipeline.md`](../sem-csmf/pipeline/processing_pipeline.md).

| Path | Trigger | DE call? |
|------|---------|----------|
| Interpret | `POST /api/v1/interpret` | No |
| Admission | `POST /api/v1/intents` | Yes — I-01 HTTP |

Admission path (abbreviated): persist intent → validate → GST → NEST → **semantic fill** → **canonical_sla** → I-01 HTTP → merge DE response + distributed trace.

## Key runtime features

### Semantic fill

Missing KPI fields are filled without overwriting explicit values. Priority: **explicit → ontology → GST → NEST**.

- Code: `apps/sem-csmf/src/services/semantic_resolver.py`, `_apply_semantic_fill_pipeline()` in `main.py`
- Internal trace: `metadata._semantic_sources` (not exposed in public API responses)

### Canonical SLA

GSMA-aligned parallel block produced by `canonicalize_sla_request()` (`apps/sem-csmf/src/canonical_sla.py`):

- Returned on `/api/v1/interpret`
- Injected as `metadata.canonical_sla` on `/api/v1/intents` (legacy `sla_requirements` unchanged for DE)

### Governance metadata

`PATCH /api/v1/intents/{intent_id}/governance-metadata` merges allowed keys only:

`bc_status`, `tx_hash`, `block_number`, `blockchain_tx_hash`, `blockchain_status`, `governance_registration_status`, `governance_registration_tx_hash`, `governance_registration_block_number`, `governance_registration_fallback`, `governance_event_id`, `transaction_receipt`

Persistence only — does not alter the semantic pipeline.

### I-01 HTTP (production)

SEM → Decision Engine: `POST {DECISION_ENGINE_URL}` default `http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate`

Client: `apps/sem-csmf/src/decision_engine_client.py`

Payload includes `telemetry_snapshot`, `context.telemetry_features`, optional `nest` body (Wave 3A), and `metadata.canonical_sla`.

Contract detail: [`docs/sem-csmf/interfaces/interfaces.md`](../sem-csmf/interfaces/interfaces.md)

### I-02 Kafka (LEGACY)

Topic `sem-csmf-nests` / `kafka_producer_retry.py` exist in repo but are **not invoked** from the production `/intents` hot path. ML-NSMF is reached via Decision Engine orchestration, not Kafka from SEM.

### I-01 gRPC (TRACEABILITY_ONLY)

`grpc_client.py`, `grpc_server.py`, proto stubs — not the production wire path.

## Environment variables (operational)

| Variable | Default / role |
|----------|----------------|
| `DECISION_ENGINE_URL` | I-01 HTTP endpoint |
| `SEM_I01_NEST_TRANSMIT` | `true` — include NEST body on I-01 (Wave 3A echo) |
| `PORTAL_PROM_QUERY_URL` | Prometheus proxy for PRB/telemetry enrichment |
| `SEM_PRB_PROM_TIMEOUT` | `3.0` — PRB query timeout (seconds) |
| `SEM_PRB_JOB_PRIORITY` | RAN PRB job preference chain |
| `DATABASE_URL` | SQLite dev / PostgreSQL prod |
| `ENABLE_AUTH` | `false` |
| `ENABLE_RATE_LIMIT` | `true` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL collector |

## Specialized documentation

| Topic | Location |
|-------|----------|
| Components and layers | [`docs/sem-csmf/architecture/`](../sem-csmf/architecture/sem_csmf_architecture.md) |
| Full processing lifecycle | [`docs/sem-csmf/pipeline/`](../sem-csmf/pipeline/processing_pipeline.md) |
| I-01/I-02 contracts | [`docs/sem-csmf/interfaces/`](../sem-csmf/interfaces/interfaces.md) |
| OWL model | [`docs/sem-csmf/ontology/`](../sem-csmf/ontology/README.md) |
| Examples and tests | [`docs/sem-csmf/examples/`](../sem-csmf/examples/usage_and_reproducibility.md) |

## Tests (repository)

```bash
pytest apps/sem-csmf/tests/test_canonical_sla.py
pytest apps/sem-csmf/tests/test_i01_nest_transmission.py
pytest apps/sem-csmf/tests/test_semantic_resolver.py
```

## Canonical Telemetry Reference

Canonical telemetry reference: docs/modules/telemetry.md defines telemetry_snapshot as the runtime telemetry input forwarded through SEM-CSMF workflows.

## Canonical Observability Reference

Canonical observability reference: docs/modules/observability.md defines SEM-CSMF metrics, OTEL tracing, health, dashboards, and alerting boundaries.
