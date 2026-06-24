# Patch Group A Metric Freeze Confirmation

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

Source: `SEM_CSMF_METRIC_FREEZE.md`

## Final Metrics

| Metric | Type | Unit | Origin | Formula | Final field |
|---|---|---|---|---|---|
| `normalization_ms` | float/null | milliseconds | SEM-CSMF request/SLA normalization block | `T2 - T1` | `semantic_stage_latencies_ms.normalization_ms` |
| `semantic_fill_ms` | float/null | milliseconds | `_apply_semantic_fill_pipeline` call boundary | `T4 - T3` | `semantic_stage_latencies_ms.semantic_fill_ms` |
| `gst_to_nest_ms` | float/null | milliseconds | GST generation plus NEST generation envelope | `T6 - T5` | `semantic_stage_latencies_ms.gst_to_nest_ms` |
| `canonical_model_generation_ms` | float/null | milliseconds | `canonicalize_sla_request` call boundary | `T8 - T7` | `semantic_stage_latencies_ms.canonical_model_generation_ms` |
| `semantic_total_ms` | float/null | milliseconds | SEM-CSMF semantic processing envelope | `T8 - T0` | `semantic_stage_latencies_ms.semantic_total_ms` |
| `admission_preparation_ms` | float/null | milliseconds | SEM-CSMF metadata/admission handoff preparation | `T9 - T8` | `semantic_stage_latencies_ms.admission_preparation_ms` |
| `end_to_end_semantic_ms` | float/null | milliseconds | Full SEM path before external admission decision | `T9 - T0` | `semantic_stage_latencies_ms.end_to_end_semantic_ms` |

## Measurement Rules

- Use monotonic runtime clock for durations.
- Report milliseconds.
- Round consistently to 4 decimal places when emitted.
- Preserve existing `sem_csmf_internal_latency_ms`.
- Preserve existing `semantic_parsing_latency_ms`.
- Preserve existing `admission_time_total_ms` ownership in Portal/submit path.
- Missing stage values may be null on partial failure paths.

## Verdict

```text
METRICS_FROZEN = YES
METRIC_COUNT = 7
METRIC_UNIT = milliseconds
METRIC_SCOPE = PASSIVE_OBSERVABILITY_ONLY
```
