# Patch Group A Function Freeze

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

## FUNCTIONS_TO_MODIFY

| File | Function / endpoint | Reason | Metric associated |
|---|---|---|---|
| `apps/sem-csmf/src/main.py` | `interpret_intent` / `POST /api/v1/interpret` | Add passive timing envelope and additive JSON response field | `normalization_ms`, `semantic_fill_ms`, `gst_to_nest_ms`, `canonical_model_generation_ms`, `semantic_total_ms`, `end_to_end_semantic_ms` |
| `apps/sem-csmf/src/main.py` | `create_intent` / `POST /api/v1/intents` | Add passive timing envelope and additive metadata/response field | `normalization_ms`, `semantic_fill_ms`, `gst_to_nest_ms`, `canonical_model_generation_ms`, `semantic_total_ms`, `admission_preparation_ms`, `end_to_end_semantic_ms` |

## FUNCTIONS_TO_WRAP

| File | Function / call boundary | Reason | Metric associated |
|---|---|---|---|
| `apps/sem-csmf/src/main.py` | request/SLA normalization blocks inside `interpret_intent` and `create_intent` | Capture normalization duration without extracting or changing logic | `normalization_ms` |
| `apps/sem-csmf/src/main.py` | `_apply_semantic_fill_pipeline(...)` call site | Measure semantic fill duration without changing function behavior | `semantic_fill_ms` |
| `apps/sem-csmf/src/main.py` | `intent_processor.generate_gst(...)` plus `nest_generator.generate_nest(...)` call envelope | Measure GST-to-NEST stage duration | `gst_to_nest_ms` |
| `apps/sem-csmf/src/main.py` | `canonicalize_sla_request(...)` call site | Measure canonical SLA model generation duration | `canonical_model_generation_ms` |
| `apps/sem-csmf/src/main.py` | metadata preparation before `send_nest_metadata(...)` | Measure admission preparation duration before external Decision Engine call | `admission_preparation_ms` |

## FUNCTIONS_TO_OBSERVE

| File | Function | Reason | Metric associated |
|---|---|---|---|
| `apps/sem-csmf/src/intent_processor.py` | `validate_semantic` | Preserve semantic validation behavior and boundary assumptions | `semantic_total_ms` envelope |
| `apps/sem-csmf/src/intent_processor.py` | `generate_gst` | Preserve GST output and boundary assumptions | `gst_to_nest_ms` |
| `apps/sem-csmf/src/nest_generator_db.py` | `generate_nest` | Preserve NEST generation and persistence behavior | `gst_to_nest_ms` |
| `apps/sem-csmf/src/canonical_sla.py` | `canonicalize_sla_request` | Preserve canonical SLA output | `canonical_model_generation_ms` |
| `apps/sem-csmf/src/decision_engine_client.py` | `send_nest_metadata` | Preserve I-01 payload and Decision Engine handoff semantics | `admission_preparation_ms` boundary only |

## FUNCTIONS_NOT_ALLOWED_TO_CHANGE

| File / area | Function | Reason |
|---|---|---|
| `apps/decision-engine/**` | Any scoring/evaluation function | Score, decision, thresholds, and policy are out of scope |
| `apps/ml-nsmf/**` | Any prediction/model loading function | ML behavior must remain unchanged |
| `apps/sem-csmf/src/canonical_sla.py` | `canonicalize_sla_request` semantics | Canonical SLA output must remain equivalent |
| `apps/sem-csmf/src/intent_processor.py` | `validate_semantic`, `generate_gst` semantics | Ontology/GST behavior must remain equivalent |
| `apps/sem-csmf/src/nest_generator*.py` | `generate_nest` semantics | NEST output must remain equivalent |
| `apps/sem-csmf/src/decision_engine_client.py` | `send_nest_metadata` payload semantics | Decision Engine input contract must not change |

## Verdict

```text
FUNCTIONS_FROZEN = YES
FUNCTIONS_TO_MODIFY_COUNT = 2
FUNCTIONS_TO_WRAP_COUNT = 5
FUNCTIONS_TO_OBSERVE_COUNT = 5
FUNCTIONS_NOT_ALLOWED_TO_CHANGE_DEFINED = YES
```
