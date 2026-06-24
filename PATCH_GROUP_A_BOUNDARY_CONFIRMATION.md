# Patch Group A Boundary Confirmation

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

## PODE ALTERAR

Future implementation may alter only:

| Area | Allowed change |
|---|---|
| timestamps | Add monotonic timing points inside SEM-CSMF endpoint flow |
| metric calculations | Add passive duration calculations from frozen timestamp boundaries |
| metadata | Add optional `semantic_stage_latencies_ms` block |
| logging | Add optional structured observability logs |
| export schema | Add backward-compatible fields for future JSONL/CSV evidence |

## NAO PODE ALTERAR

Future implementation must not alter:

| Area | Restriction |
|---|---|
| score | No score formula or value change |
| decisao | No admission decision behavior change |
| threshold | No threshold change |
| ontologia | No ontology source, fallback, rule, or semantic meaning change |
| regras de negocio | No acceptance/business rule change |
| ML | No model, feature, prediction, latency behavior, or confidence change |
| comportamento funcional | Existing API behavior and outputs must remain equivalent except additive observability fields |
| arquitetura | No new service, queue, database, deployment, or runtime architecture change |
| datasets | No mutation of existing datasets |
| SSOT | No SSOT/baseline mutation during implementation |
| artigo | No article/dissertation text change |

## Equivalence Requirements

```text
FUNCTIONAL_OUTPUT_EQUIVALENCE_REQUIRED = YES
DECISION_EQUIVALENCE_REQUIRED = YES
THRESHOLD_CHANGE_ALLOWED = NO
ML_BEHAVIOR_CHANGE_ALLOWED = NO
ONTOLOGY_CHANGE_ALLOWED = NO
ARCHITECTURE_CHANGE_ALLOWED = NO
```

## Verdict

```text
IMPLEMENTATION_BOUNDARY_CONFIRMED = YES
SCIENTIFIC_BASELINE_PRESERVED = YES
FUNCTIONAL_BEHAVIOR_CHANGE_ALLOWED = NO
ARCHITECTURE_CHANGE_ALLOWED = NO
```
