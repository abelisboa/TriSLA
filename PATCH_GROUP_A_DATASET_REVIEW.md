# Patch Group A Dataset Review

Phase: PHASE-I3A PATCH_GROUP_A_IMPLEMENTATION_REVIEW

Execution mode: review only. No dataset modification performed.

## Source

Primary design source: `SEM_CSMF_DATASET_IMPACT.md`.

## Impact Review

| Area | Impact | Future handling | Verdict |
|---|---|---|---|
| JSONL | LOW | Add nested `payload.metadata.semantic_stage_latencies_ms` only in future evidence packs | SAFE |
| CSV | LOW | Add nullable float columns only in future processed campaign datasets | SAFE |
| Notebooks | LOW | Existing notebooks remain unchanged; future notebooks may consume added columns | SAFE |
| Figures | LOW | Existing official figures remain frozen; future figures require new phase approval | SAFE |
| Results | LOW | Results claims must remain evidence-bound and cannot use old datasets for new fields | SAFE |
| Rastreabilidade | MEDIUM | Stage boundaries must be documented with timestamp semantics | ACCEPTABLE |
| Evidence packs | LOW | New evidence pack required for any future generated dataset | SAFE |
| Frozen datasets | NONE | No mutation allowed | PRESERVED |

## Future Dataset Columns

Candidate processed columns:

```text
intent_id
nest_id
execution_id
scenario_id
slice_type
normalization_ms
semantic_fill_ms
gst_to_nest_ms
canonical_model_generation_ms
semantic_total_ms
admission_preparation_ms
end_to_end_semantic_ms
sem_csmf_internal_latency_ms
semantic_parsing_latency_ms
```

## Dataset Governance

Future dataset evolution must:

- use a new evidence pack directory;
- preserve all frozen datasets byte-for-byte;
- record schema version and column dictionary;
- record campaign timestamp and Git/container digest;
- explicitly distinguish new telemetry from `RESULTS_FREEZE_MAIN`;
- avoid regenerating old figures or notebooks.

## Verdict

```text
BACKWARD_COMPATIBLE = YES
DATASET_EVOLUTION_SAFE = YES
FROZEN_DATASETS_PRESERVED = YES
EXISTING_NOTEBOOKS_UNCHANGED = YES
EXISTING_FIGURES_UNCHANGED = YES
NEW_CAMPAIGN_REQUIRED_FOR_NEW_DATASET_VALUES = YES
```
