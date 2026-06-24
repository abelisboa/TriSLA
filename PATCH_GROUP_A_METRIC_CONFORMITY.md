# Patch Group A Metric Conformity

Phase: PHASE-I4B PATCH_GROUP_A_POST_IMPLEMENTATION_AUDIT

Source freeze: `PATCH_GROUP_A_METRIC_FREEZE_CONFIRMATION.md`

## Expected Metrics

```text
normalization_ms
semantic_fill_ms
gst_to_nest_ms
canonical_model_generation_ms
semantic_total_ms
admission_preparation_ms
end_to_end_semantic_ms
```

## Found Metrics

| Metric | Status |
|---|---|
| `normalization_ms` | FOUND |
| `semantic_fill_ms` | FOUND |
| `gst_to_nest_ms` | FOUND |
| `canonical_model_generation_ms` | FOUND |
| `semantic_total_ms` | FOUND |
| `admission_preparation_ms` | FOUND |
| `end_to_end_semantic_ms` | FOUND |

The fields are emitted under:

```text
semantic_stage_latencies_ms
```

## Verdict

```text
METRIC_COUNT_EXPECTED = 7
METRIC_COUNT_FOUND = 7
PATCH_GROUP_A_METRIC_CONFORMITY = PASS
```
