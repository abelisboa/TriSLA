# Patch Group A File Freeze

Phase: PHASE-I3B PATCH_GROUP_A_IMPLEMENTATION_PACKAGE_FREEZE

Source: `PATCH_GROUP_A_FILE_IMPACT.md`

## FILES_TO_MODIFY

| Path | Responsibility | Type of alteration | Expected impact |
|---|---|---|---|
| `apps/sem-csmf/src/main.py` | Owns `/api/v1/interpret`, `/api/v1/intents`, semantic pipeline orchestration, metadata and latency response packaging | Add passive timestamps, duration calculations, additive `semantic_stage_latencies_ms` block, optional structured logging | LOW; observability-only; no decision, ontology, GST/NEST, canonical SLA, ML, threshold, or functional behavior change |

## FILES_TO_READ

| Path | Responsibility | Use in implementation | Expected impact |
|---|---|---|---|
| `apps/sem-csmf/src/canonical_sla.py` | Produces canonical SLA model | Read to preserve canonical output and place timing around caller boundary | NONE if untouched |
| `apps/sem-csmf/src/intent_processor.py` | Owns semantic validation and GST generation | Read to preserve stage semantics and call boundaries | NONE if untouched |
| `apps/sem-csmf/src/nest_generator_db.py` | Generates/persists NEST from GST | Read to preserve GST/NEST timing boundary | NONE if untouched |
| `apps/sem-csmf/src/nest_generator.py` | Non-DB NEST generation path | Read only if validating fallback timing assumptions | NONE if untouched |
| `apps/sem-csmf/src/nest_generator_base.py` | Shared NEST generator contract | Read to preserve NEST contract | NONE |
| `apps/sem-csmf/src/decision_engine_client.py` | I-01 Decision Engine handoff | Read to define handoff boundary; payload must not change | NONE if untouched |
| `apps/portal-backend/src/services/nasp.py` | Portal/NASP SEM latency preservation | Read only if checking downstream propagation; not part of Patch Group A edit scope | NONE |
| `apps/portal-backend/src/routers/sla.py` | Portal SLA response and JSONL packaging | Read only if checking future evidence propagation; not part of Patch Group A edit scope | NONE |

## FILES_UNTOUCHED

| Path / area | Reason |
|---|---|
| `apps/decision-engine/**` | Decision policy, score, thresholds, and reasoning must remain unchanged |
| `apps/ml-nsmf/**` | ML model behavior and inference path must remain unchanged |
| `apps/bc-nssmf/**` | Blockchain governance path out of scope |
| `apps/sla-agent-layer/**` | Runtime assurance path out of scope |
| `helm/**` | No build/deploy/manifest mutation in this phase |
| `docs/**` SSOT/baselines | SSOT and baseline documents must not be changed by implementation |
| Frozen datasets/evidence/figures | Historical scientific evidence is immutable |

## Verdict

```text
FILES_FROZEN = YES
FILES_TO_MODIFY_COUNT = 1
FILES_TO_READ_COUNT = 8
FILES_UNTOUCHED_DEFINED = YES
```
