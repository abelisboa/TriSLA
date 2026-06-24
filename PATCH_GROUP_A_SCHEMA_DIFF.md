# Patch Group A Schema Diff

Phase: PHASE-I4A PATCH_GROUP_A_IMPLEMENTATION

## JSON Response

New optional additive field on `/api/v1/interpret`:

```text
semantic_stage_latencies_ms
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

Backward compatibility: existing fields are preserved and unchanged.

## Metadata

New optional additive metadata field on `/api/v1/intents` response metadata:

```text
metadata.semantic_stage_latencies_ms
```

The same block is passed as additive metadata to the Decision Engine handoff. It is observational only and must not be used for decision logic.

## Telemetry Snapshot

```text
TELEMETRY_SNAPSHOT_CHANGE = NONE
```

No telemetry snapshot schema was changed.

## Dataset Schema

No dataset was modified.

Future processed datasets may add the already-frozen nullable columns:

```text
normalization_ms
semantic_fill_ms
gst_to_nest_ms
canonical_model_generation_ms
semantic_total_ms
admission_preparation_ms
end_to_end_semantic_ms
```

## Prometheus Export

```text
PROMETHEUS_EXPORT = NONE
```

No Prometheus metric was added in this phase.

## Verdict

```text
BACKWARD_COMPATIBLE = YES
JSON_RESPONSE_COMPATIBLE = YES
METADATA_COMPATIBLE = YES
TELEMETRY_SNAPSHOT_UNCHANGED = YES
DATASET_SCHEMA_UNCHANGED = YES
PROMETHEUS_EXPORT_UNCHANGED = YES
```
