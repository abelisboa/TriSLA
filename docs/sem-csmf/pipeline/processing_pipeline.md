# SEM-CSMF Processing Pipeline

> Components and layers: [`architecture/sem_csmf_architecture.md`](../architecture/sem_csmf_architecture.md).
> Operational endpoints and digest: [`docs/modules/sem-csmf.md`](../../modules/sem-csmf.md).

This document is the **single in-depth pipeline reference** for SEM-CSMF.

## 1. Canonical Flow

```text
Intent → NLP → Ontology → Validation → GST → NEST → Semantic Fill → Canonical SLA → I-01 HTTP
```

Formal projection:

$$
NEST = T(F(V(O(P(I)))))
$$

where `F` = semantic fill, `T` = NEST transformation, `V` = validation, `O` = ontology mapping, `P` = NLP parsing, `I` = raw intent.

## 2. Runtime Paths

### Path A — `POST /api/v1/interpret` (interpretation only)

Used by Portal for pre-submit interpretation. **Does not persist intent or call Decision Engine.**

1. NLP parse (optional) + keyword fallback for slice type
2. Default SLA by slice type if NLP yields nothing
3. `validate_semantic(intent, intent_text)`
4. `generate_gst(validated)` → `NESTGeneratorDB.generate_nest(gst)`
5. `_apply_semantic_fill_pipeline()` — priority: explicit → ontology → GST → NEST
6. `canonicalize_sla_request()` → included in response
7. Return `{intent_id, nest_id, service_type, sla_requirements, canonical_sla, sem_csmf_internal_latency_ms}`

### Path B — `POST /api/v1/intents` (admission pipeline)

**Production admission path.** Portal submits structured intent; SEM orchestrates semantic processing and I-01 dispatch.

1. **Intent reception** — `IntentRequest`; `generate_default_sla()` if `sla_requirements` absent
2. **Persist** — `IntentModel` to database
3. **NLP extraction** — when `intent` text present, merge extracted fields
4. **Ontology validation** — `validate_semantic()` via loader/reasoner/matcher
5. **GST generation** — `generate_gst()` with slice-specific QoS templates
6. **NEST generation** — `NESTGeneratorDB.generate_nest()`; persist NEST + slices
7. **Semantic fill** — `apply_semantic_fill_to_intent_sla()`; update `sla_requirements`
8. **Metadata** — `generate_metadata()`; merge upstream Portal `metadata`
9. **Canonical SLA** — `canonicalize_sla_request()` → `metadata.canonical_sla`
10. **I-01 dispatch** — `DecisionEngineHTTPClient.send_nest_metadata()`:
    - HTTP POST `/evaluate`
    - `telemetry_snapshot` + `context.telemetry_features` (PRB via Portal Prometheus proxy)
    - optional `nest` body when `SEM_I01_NEST_TRANSMIT=true` (Wave 3A echo)
11. **Response** — `IntentResponse` with DE decision fields; `distributed_trace` merged into metadata; persist `extra_metadata`

ML-NSMF participates **inside Decision Engine** on this path — not via Kafka from SEM.

### Path C — Auxiliary (non-admission)

| Endpoint | Role |
|----------|------|
| `POST /api/v1/intents/register` | Idempotent NASP SLA registration |
| `GET /api/v1/intents/{id}` | Status polling for Portal |
| `PATCH .../governance-metadata` | Merge BC/governance keys (persistence only) |

## 3. Semantic Fill Detail

Code: `apps/sem-csmf/src/services/semantic_resolver.py`

KPI fields: `latency`, `throughput`, `reliability`, `availability`, `coverage`, `device_density`, `jitter`

| Priority | Source |
|----------|--------|
| 1 | Explicit value in request |
| 2 | Ontology slice-type individuals (`trisla_complete.owl` / `trisla.ttl`) |
| 3 | GST template (`qos` / `sla`) |
| 4 | NEST primary slice resources |

Internal provenance stored in `metadata._semantic_sources` (not returned in public API).

## 4. Canonical SLA Detail

Code: `apps/sem-csmf/src/canonical_sla.py`

Produces GSMA-aligned block (`slice_service_type`, `sst`, `sd`, `service_requirements`, `semantic_context`, `legacy_input`) **in parallel** with legacy `sla_requirements` sent to DE.

## 5. Failure Modes and Guardrails

- **Parsing ambiguity:** fallback to structured constraints and slice-type defaults
- **Ontology mismatch / load failure:** degraded mode; matcher continues with fallbacks
- **I-01 HTTP failure:** controlled REJECT response; span + log diagnostics
- **Persistence failure:** rollback; HTTP 500
- **Legacy gRPC/Kafka:** not on production hot path — do not use for admission troubleshooting

## 6. Reproducibility Notes

- Pin ontology file (`trisla_complete.owl` preferred) and app digest for campaign runs
- Preserve `intent_id`, `nest_id` across logs and I-01 payload
- Record `metadata.canonical_sla` and dispatch timestamps for cross-module correlation

## 7. Pipeline Summary

The SEM-CSMF pipeline converts human-level intent into machine-level contractual artifacts suitable for SLA-aware decisioning. Production dispatch is **I-01 HTTP only**; Kafka I-02 remains legacy code in the repository.
