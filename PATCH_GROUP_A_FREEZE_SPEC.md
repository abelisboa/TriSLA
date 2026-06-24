# PATCH_GROUP_A Freeze Specification

Phase: PHASE-I2A PATCH_GROUP_A_DESIGN_FREEZE

Scope: SEM-CSMF Passive Timing and Semantic Processing Traceability.

## File-Level Patch Specification

| File | Function | Type of modification | Metric added | Field exported | Risk |
|---|---|---|---|---|---|
| `apps/sem-csmf/src/main.py` | `interpret_intent` | add passive timing boundaries and response metadata | all SEM stage metrics where endpoint applies | `semantic_stage_latencies_ms` | LOW |
| `apps/sem-csmf/src/main.py` | `create_intent` | add passive timing boundaries and metadata propagation | all SEM stage metrics plus `admission_preparation_ms` | `metadata.semantic_stage_latencies_ms` | LOW |
| `apps/sem-csmf/src/main.py` | `_apply_semantic_fill_pipeline` call sites | wrap call with timer | `semantic_fill_ms` | nested metric block | LOW |
| `apps/sem-csmf/src/canonical_sla.py` | `canonicalize_sla_request` call sites only | no semantic change; call wrapped externally | `canonical_model_generation_ms` | nested metric block | LOW |
| `apps/sem-csmf/src/intent_processor.py` | `generate_gst` call sites only | no semantic change; call wrapped externally | part of `gst_to_nest_ms` | nested metric block | LOW |
| `apps/sem-csmf/src/nest_generator_db.py` | `generate_nest` call sites only | no semantic change; call wrapped externally | part of `gst_to_nest_ms` | nested metric block | LOW |
| `apps/portal-backend/src/services/nasp.py` | SEM response merge | preserve/forward new SEM metric block | no new calculation unless needed | response metadata | LOW |
| `apps/portal-backend/src/routers/sla.py` | module latency packaging | optionally copy new block into raw metadata | no new calculation | `metadata_out.semantic_stage_latencies_ms` | LOW |

## Estimated Patch Size

```text
FILES_IMPACTED_ESTIMATE = 2_TO_4
LOC_ADDED_ESTIMATE = 60_TO_120
LOC_ALTERED_ESTIMATE = 10_TO_30
```

## Test Requirements

- unit test for new metric block shape;
- unit test that all durations are non-negative;
- regression test that existing `sem_csmf_internal_latency_ms` remains present;
- regression test that decisions/scores are unchanged for equivalent inputs;
- processed dataset validation once a future campaign exists.

## Freeze Verdict

```text
PATCH_GROUP_A_FREEZE_SPEC_STATUS = FROZEN
PATCH_GROUP_A_IMPLEMENTATION_READY = YES
```
