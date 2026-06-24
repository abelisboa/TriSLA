# Patch Group A Dataset Evolution Freeze

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

Source: `PATCH_GROUP_A_DATASET_REVIEW.md`

## JSONL Evolution

New raw JSONL field path for future evidence packs:

```text
payload.metadata.semantic_stage_latencies_ms
```

Nested fields:

```text
normalization_ms
semantic_fill_ms
gst_to_nest_ms
canonical_model_generation_ms
semantic_total_ms
admission_preparation_ms
end_to_end_semantic_ms
```

## CSV Evolution

New processed CSV columns for future evidence packs:

```text
normalization_ms
semantic_fill_ms
gst_to_nest_ms
canonical_model_generation_ms
semantic_total_ms
admission_preparation_ms
end_to_end_semantic_ms
```

Context columns to retain:

```text
intent_id
nest_id
execution_id
scenario_id
slice_type
sem_csmf_internal_latency_ms
semantic_parsing_latency_ms
```

## Compatibility

| Area | Compatibility |
|---|---|
| Old datasets | Preserved; no mutation allowed |
| Old JSONL | Preserved; no backfill required |
| Old CSV | Preserved; new columns absent by design |
| Old notebooks | Compatible; no required edits |
| Old figures | Compatible; no regeneration allowed |
| Frozen evidence | Preserved byte-for-byte |
| Future evidence | Must use new evidence pack and schema note |

## Governance Rules

- New telemetry values require future approved implementation plus future campaign/evidence phase.
- Existing `RESULTS_FREEZE_MAIN` datasets are not modified.
- Future datasets must record Git commit, image digest, schema version, timestamp, and campaign parameters.
- Null values are allowed when a stage boundary is not reached.

## Verdict

```text
DATASET_EVOLUTION_FROZEN = YES
JSONL_FIELDS_FROZEN = YES
CSV_FIELDS_FROZEN = YES
OLD_DATASET_COMPATIBILITY = YES
OLD_NOTEBOOK_COMPATIBILITY = YES
FROZEN_EVIDENCE_COMPATIBILITY = YES
```
