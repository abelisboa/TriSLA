# Patch Group A File Impact Review

Phase: PHASE-I3A PATCH_GROUP_A_IMPLEMENTATION_REVIEW

Execution mode: review only. No code change performed.

## Source

Primary design source: `SEM_CSMF_CODE_PATH_MAP.md`.

## Exact Impact Matrix

| File | Class | Function / endpoint | Responsibility | Future alteration type |
|---|---|---|---|---|
| `apps/sem-csmf/src/main.py` | N/A | `POST /api/v1/interpret` / `interpret_intent` | PNL interpretation, SLA requirement inference, semantic validation, GST/NEST generation, semantic fill, canonical SLA generation, response latency packaging | Add passive timestamps around existing blocks; add additive `semantic_stage_latencies_ms` to response/metadata |
| `apps/sem-csmf/src/main.py` | N/A | `POST /api/v1/intents` / `create_intent` | Intent creation, DB persistence, semantic pipeline, metadata generation, canonical SLA generation, Decision Engine handoff | Add passive timestamps around existing blocks; add additive `semantic_stage_latencies_ms` to metadata and response |
| `apps/sem-csmf/src/main.py` | N/A | `_apply_semantic_fill_pipeline` | Semantic completion/enrichment across Intent/GST/NEST | Surround call site with passive timing; no logic change inside semantic fill |
| `apps/sem-csmf/src/canonical_sla.py` | N/A | `canonicalize_sla_request` | Generate canonical SLA model | Surround call site or helper invocation with passive timing; no semantic/canonical output change |
| `apps/sem-csmf/src/intent_processor.py` | `IntentProcessor` | `validate_semantic` | Validate/enrich intent semantically | Timing boundary only if needed for stage attribution; no validation behavior change |
| `apps/sem-csmf/src/intent_processor.py` | `IntentProcessor` | `generate_gst` | Generate GST representation | Timing boundary only; no GST behavior change |
| `apps/sem-csmf/src/nest_generator_db.py` | `NESTGeneratorDB` | `generate_nest` | Generate and persist NEST from GST | Timing boundary only; no NEST behavior or persistence semantics change |
| `apps/sem-csmf/src/nest_generator.py` | `NESTGenerator` | `generate_nest` | Non-DB NEST generation path | Timing boundary only if path participates in future validation; no NEST behavior change |
| `apps/sem-csmf/src/nest_generator_base.py` | `NESTGeneratorBase` | base contract | Shared NEST generator contract | No change expected; read-only reference for contract preservation |
| `apps/sem-csmf/src/decision_engine_client.py` | client class | `send_nest_metadata` | I-01 handoff to Decision Engine | No decision payload change; may be used only to define `admission_preparation_ms` boundary before call |
| `apps/portal-backend/src/services/nasp.py` | N/A | interpret/submit integration | Preserve SEM latency fields in NASP path | No Patch Group A code change planned unless later reviewed for additive propagation only |
| `apps/portal-backend/src/routers/sla.py` | N/A | `metadata_out["module_latencies_ms"]` and response packaging | Export module latency block to portal response/JSONL | No Patch Group A code change planned unless later reviewed for additive propagation only |

## Endpoint Boundaries

| Endpoint | Existing latency | Future additive stage block |
|---|---|---|
| `/api/v1/interpret` | `sem_csmf_internal_latency_ms` | `semantic_stage_latencies_ms` |
| `/api/v1/intents` | `semantic_latency_ms` | `metadata.semantic_stage_latencies_ms` |

## Implementation Boundary

Allowed future edits are passive timestamp capture, duration calculation, additive metadata/response fields, structured logs, and tests. Forbidden future edits include decision policy, score, thresholds, ML behavior, ontology semantics, GST/NEST semantics, canonical SLA semantics, acceptance policy, architecture, datasets, SSOT, and frozen figures.

## Verdict

```text
FILES_IDENTIFIED = YES
FUNCTIONS_IDENTIFIED = YES
ENDPOINTS_IDENTIFIED = YES
PATCH_SCOPE = SEM_CSMF_PASSIVE_OBSERVABILITY_ONLY
PORTAL_CHANGES_REQUIRED_FOR_PATCH_GROUP_A = NO
DECISION_ENGINE_CHANGES_REQUIRED = NO
```
