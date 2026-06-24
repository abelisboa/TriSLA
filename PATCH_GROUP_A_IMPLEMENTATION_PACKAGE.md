# Patch Group A Implementation Package

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

Package: SEM-CSMF Passive Timing and Semantic Processing Traceability

Execution mode: package freeze only. No implementation, code change, build, deploy, campaign, dataset change, SSOT change, article change, architecture change, or functional behavior change performed.

## FILES_TO_MODIFY

```text
apps/sem-csmf/src/main.py
```

Allowed changes: passive timestamps, duration calculations, additive metadata/response fields, optional structured logs.

## FUNCTIONS_TO_MODIFY

```text
interpret_intent
create_intent
```

## FUNCTIONS_TO_WRAP

```text
request/SLA normalization blocks
_apply_semantic_fill_pipeline call site
intent_processor.generate_gst + nest_generator.generate_nest envelope
canonicalize_sla_request call site
metadata/admission preparation before send_nest_metadata
```

## FIELDS_TO_ADD

```text
semantic_stage_latencies_ms.normalization_ms
semantic_stage_latencies_ms.semantic_fill_ms
semantic_stage_latencies_ms.gst_to_nest_ms
semantic_stage_latencies_ms.canonical_model_generation_ms
semantic_stage_latencies_ms.semantic_total_ms
semantic_stage_latencies_ms.admission_preparation_ms
semantic_stage_latencies_ms.end_to_end_semantic_ms
```

## METRICS_TO_ADD

```text
normalization_ms = T2 - T1
semantic_fill_ms = T4 - T3
gst_to_nest_ms = T6 - T5
canonical_model_generation_ms = T8 - T7
semantic_total_ms = T8 - T0
admission_preparation_ms = T9 - T8
end_to_end_semantic_ms = T9 - T0
```

## PAYLOAD_CHANGES

Add optional, backward-compatible block:

```json
{
  "semantic_stage_latencies_ms": {
    "normalization_ms": 0.0,
    "semantic_fill_ms": 0.0,
    "gst_to_nest_ms": 0.0,
    "canonical_model_generation_ms": 0.0,
    "semantic_total_ms": 0.0,
    "admission_preparation_ms": 0.0,
    "end_to_end_semantic_ms": 0.0
  }
}
```

Existing fields must not be removed, renamed, or redefined.

## DATASET_CHANGES

No existing dataset changes are allowed.

Future evidence packs may add:

```text
normalization_ms
semantic_fill_ms
gst_to_nest_ms
canonical_model_generation_ms
semantic_total_ms
admission_preparation_ms
end_to_end_semantic_ms
```

## PROMETHEUS_EXPORTS

```text
PROMETHEUS_EXPORTS = NONE_FOR_PATCH_GROUP_A_INITIAL_IMPLEMENTATION
PROMETHEUS_STATUS = DEFERRED
```

## LOC_ESTIMATE

```text
LOC_ADDED_ESTIMATE = 60_TO_120
LOC_ALTERED_ESTIMATE = 10_TO_30
FILES_IMPACTED_ESTIMATE = 1_MODIFY_8_READ
COMPLEXITY = LOW
```

## BUILD_PROCESS

```text
GitHub Commit
-> Build
-> SHA256 Digest
-> GHCR registration
```

Registry:

```text
ghcr.io/abelisboa/trisla-sem-csmf
```

## DEPLOY_PROCESS

```text
Deploy remoto por digest only
Namespace = trisla
Deployment = trisla-sem-csmf
Image = ghcr.io/abelisboa/trisla-sem-csmf@sha256:<full_digest>
```

## ROLLBACK_PROCESS

Rollback digest:

```text
sha256:38fb2396aec9de4bcf9ba430dce70bed0791976e3c6975160ea89101af5c830a
```

Current runtime digest:

```text
sha256:1af16f60f1414a5a630f8792caa6540b52e42d1a4f4da8631069efb2f9bb3b23
```

## Final Verdict

```text
IMPLEMENTATION_SCOPE_LOCKED = YES
FILES_FROZEN = YES
FUNCTIONS_FROZEN = YES
PAYLOAD_FROZEN = YES
DATASET_EVOLUTION_FROZEN = YES
BUILD_PROCESS_FROZEN = YES
DEPLOY_PROCESS_FROZEN = YES
ROLLBACK_PROCESS_FROZEN = YES
SCIENTIFIC_BASELINE_PRESERVED = YES
DIGEST_BASELINE_FROZEN = YES
NO_CODE_CHANGE_PERFORMED = TRUE
NO_BUILD_PERFORMED = TRUE
NO_DEPLOY_PERFORMED = TRUE
NO_CAMPAIGN_EXECUTED = TRUE
MANUAL_APPROVAL_REQUIRED = YES
NEXT_ALLOWED_PHASE = PATCH_GROUP_A_IMPLEMENTATION_AUTHORIZATION
```
