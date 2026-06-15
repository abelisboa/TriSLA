# SEM-CSMF Interfaces

> Specialized reference. Canonical cross-module interface truth: [`docs/modules/interfaces.md`](../../modules/interfaces.md).

> Operational REST catalog: [`docs/modules/sem-csmf.md`](../../modules/sem-csmf.md).
> Pipeline context: [`pipeline/processing_pipeline.md`](../pipeline/processing_pipeline.md).

## 1. Integration Scope

| Interface | Transport | Status |
|-----------|-----------|--------|
| **I-01** | HTTP POST `/evaluate` | **Production SSOT** |
| I-01 | gRPC `:50051` | **TRACEABILITY_ONLY** |
| **I-02** | Kafka `sem-csmf-nests` | **LEGACY** — code present, not wired from `/intents` hot path |
| Ingress | REST `:8080` | **Production** |

Runtime authority (I-01 schema): `interface-registry/i01/I01_SCHEMA_REGISTRY.json`

---

## 2. REST Ingress (SEM-CSMF exposes)

| Method | Path | Caller | Notes |
|--------|------|--------|-------|
| POST | `/api/v1/interpret` | Portal Backend | Interpretation only; no DE call |
| POST | `/api/v1/intents` | Portal Backend | Admission pipeline + I-01 |
| GET | `/api/v1/intents/{intent_id}` | Portal Backend | Status / metadata polling |
| PATCH | `/api/v1/intents/{intent_id}/governance-metadata` | Portal / relay | Merge governance keys (see §7) |
| POST | `/api/v1/intents/register` | NASP integration | Idempotent registration |
| GET | `/api/v1/nests/{nest_id}` | Clients | NEST retrieval |
| GET | `/api/v1/slices` | Clients | Slice listing |
| GET | `/health` | K8s / probes | Liveness |
| GET | `/metrics` | Prometheus | Scraping |

Portal env: `SEM_CSMF_URL=http://trisla-sem-csmf:8080`

---

## 3. I-01 (HTTP — Production SSOT)

### Direction

SEM-CSMF → Decision Engine

### Endpoint

```text
POST http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate
Content-Type: application/json
```

**Client:** `apps/sem-csmf/src/decision_engine_client.py` (`DecisionEngineHTTPClient.send_nest_metadata`)

**Env:** `DECISION_ENGINE_URL` (defaults to URL above)

### Reference Payload (conceptual)

```json
{
  "intent_id": "intent-001",
  "nest_id": "nest-001",
  "intent": {
    "intent_id": "intent-001",
    "tenant_id": "tenant-001",
    "service_type": "URLLC",
    "sla_requirements": { "latency": "10ms", "reliability": 0.999 }
  },
  "metadata": {
    "canonical_sla": { },
    "trace_id": "...",
    "timestamp": "2026-06-12T20:00:00Z"
  },
  "telemetry_snapshot": {
    "ran": { "prb_utilization": 0.42 },
    "transport": { "latency_ms": 5 },
    "core": { "cpu_utilization": 0.3 }
  },
  "context": { "telemetry_features": { } }
}
```

### Wave 3A — NEST transmission

When `SEM_I01_NEST_TRANSMIT=true` (default), payload includes root field `"nest": { ... }` (serialized NEST model).

| Flag | DE behavior (frozen) |
|------|------------------------|
| `NEST_TRANSMISSION` | `TRACEABILITY_ONLY` |
| `NEST_CONSUMPTION` | `NOT WIRED` |

DE echoes NEST; consumption for scoring remains disabled per Wave 3A freeze.

Tests: `apps/sem-csmf/tests/test_i01_nest_transmission.py`

### Operational Notes

- Preserve `intent_id`, `nest_id` for observability
- Root `metadata` sent by SEM; DE echoes under `DecisionResult.metadata.inbound_metadata` (Wave 1 G3-A)
- PRB/telemetry enriched via `PORTAL_PROM_QUERY_URL` when absent in upstream metadata
- HTTP client handles timeout/connection errors with controlled REJECT fallback

---

## 4. I-01 (gRPC — TRACEABILITY_ONLY)

**Not the production transport.** Stubs in `grpc_client.py`, `grpc_server.py`, `proto/` remain for traceability only.

Legacy endpoint: `decision-engine:50051` — `SendNESTMetadata`

Do **not** use gRPC as SSOT for new integrations. See `interface-registry/i01/I01_GOVERNANCE_BASELINE.md`.

---

## 5. I-02 (Kafka — LEGACY)

**Not active in production admission path.**

| Item | Value |
|------|-------|
| Topic | `sem-csmf-nests` |
| Code | `kafka_producer_retry.py` |
| Wired from `main.py` `/intents`? | **No** |

ML-NSMF is invoked by Decision Engine during `/evaluate`, not via Kafka publish from SEM.

Historical reference payload:

```json
{
  "nest_id": "nest-urllc-001",
  "intent_id": "intent-001",
  "slice_type": "URLLC",
  "sla_requirements": { "latency": "10ms", "throughput": "100Mbps", "reliability": 0.99999 },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

---

## 6. Reliability and Observability

- **I-01 HTTP failures:** logged + span `send_nest_metadata_http`; returns structured error to `/intents` caller
- **gRPC / Kafka:** legacy only — not used for production admission troubleshooting
- **OTEL spans (production):** `interpret_intent`, `process_intent`, `validate_semantic`, `generate_gst`, `generate_nest`, `send_nest_metadata_http`
- **HTTP metrics:** `trisla_http_requests_total`, `trisla_http_request_duration_seconds` (middleware in `main.py`)

---

## 7. Governance Metadata (REST)

`PATCH /api/v1/intents/{intent_id}/governance-metadata`

Merge-only persistence into `extra_metadata`. Allowed keys:

`bc_status`, `tx_hash`, `block_number`, `blockchain_tx_hash`, `blockchain_status`, `governance_registration_status`, `governance_registration_tx_hash`, `governance_registration_block_number`, `governance_registration_fallback`, `governance_event_id`, `transaction_receipt`

Does not re-run semantic pipeline or alter I-01 contracts.

---

## 8. Interface Summary

Production wire path: **REST ingress → semantic pipeline → I-01 HTTP POST `/evaluate`**. gRPC and Kafka interfaces exist in the repository as legacy/traceability artifacts only.
