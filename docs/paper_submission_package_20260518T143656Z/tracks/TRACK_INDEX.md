# TriSLA Program — Track Index

Generated: 2026-05-18T14:36:56.919180+00:00
Active digest: `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`
Submission package: `docs/paper_submission_package_20260518T143656Z`

## SR

- **Objective:** Slice-aware runtime admission (NASP-hard+, score_mode)
- **Final verdict:** `FINAL_PROGRAM_BASELINE_FROZEN`
- **Evidence pack:** `evidencias_trisla_sr_exec_09_final_program_freeze_20260517T192637Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- RAN-dominant hybrid SLA admission with PRB hard gates (n=450 NASP-hard+).
- Feasibility- and resource-headroom-aware continuous decision_score_mode.
- Transport-informed scoring with P2 slice-specific w_transport (0.05/0.03/0.02).
- Runtime tri-slice score differentiation under same network_state_id (score_mode, n=44 triplets).
- Conceptual alignment with 3GPP TS 28.541, ETSI ZSM, O-RAN (references_4.bib).

### Forbidden claims
- Balanced multidomain runtime dominance.
- Robust tri-slice admission divergence without path stratification.
- Normative 3GPP/ETSI/O-RAN compliance.
- Core-driven or orchestration-differentiated admission (unproven).

## NAD

- **Objective:** Admission boundary / liminal divergence
- **Final verdict:** `NAD_EXEC_TRACK_FROZEN`
- **Evidence pack:** `evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- (see freeze summary JSON in `freezes/`)

### Forbidden claims
- (see freeze summary JSON in `freezes/`)

## CORE

- **Objective:** Core contention attribution
- **Final verdict:** `CORE_EXEC_TRACK_FROZEN`
- **Evidence pack:** `evidencias_trisla_core_exec_09_core_track_final_freeze_20260518T012114Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- (see freeze summary JSON in `freezes/`)

### Forbidden claims
- (see freeze summary JSON in `freezes/`)

## NCM

- **Objective:** Operational contention (orchestration latency)
- **Final verdict:** `NCM_EXEC_TRACK_FROZEN`
- **Evidence pack:** `evidencias_trisla_ncm_exec_06_ncm_track_final_freeze_20260518T022058Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- Orchestration contention: 144 concurrent real POST /api/v1/sla/submit (4 tenants, stagger 2s)
- Pipeline latency contention: mean http_elapsed_s ≈ 4.49s (~9× baseline ~0.5s)
- Operational concurrency effects measurable without synthetic telemetry
- score_mode probe rows (36) with equivalent_state_id discipline preserved
- Runtime guards (pressure/feasibility/PRB pre_triplet) functioned as designed (36/36 skips)
- INV-PRB preserved: 0 hard_gate rows; no guard/threshold weakening
- NCM controls implemented and self-tested (15/15 EXEC-03)

### Forbidden claims
- multidomain balanced runtime under NCM-ORCH-01 alone
- Core-causal or orchestration-causal admission divergence
- robust admission divergence from orchestration HTTP load
- score boundary / liminal crossings without triplet dataset
- full lifecycle proof (no PDU/session churn executed)
- pressure/feasibility targets attained without new mechanisms
- Repeating identical NCM-ORCH-01 campaigns as primary science path

## LIFE

- **Objective:** Lifecycle persistence and reconciliation
- **Final verdict:** `LIFE_EXEC_TRACK_FROZEN`
- **Evidence pack:** `evidencias_trisla_life_exec_06_lifecycle_track_final_freeze_20260518T024647Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- SEM SQLite semantic persistence (intents/nests/slices; replay via intent_id)
- NASP NSI watch + capacity reconciler (continuous/periodic; CRD ORPHANED/EXPIRED evidence)
- BC-NSSMF on-chain immutable governance at submit
- Portal synchronous submit with sla_lifecycle timestamps in response metadata
- DE authoritative admission/score at decision time under frozen digest
- NASP runtime-authoritative slice/reservation state (10k+ CRDs)
- Reconciliation decoupled from admission (no feedback loop; reviewer-safe negative)
- Fragmented but real lifecycle artifacts across SEM/CRD/BC/portal response

### Forbidden claims
- continuous lifecycle governance
- runtime autonomous SLA reevaluation
- closed-loop lifecycle causality
- lifecycle-causal admission divergence
- multidomain balanced lifecycle runtime
- Kafka continuous lifecycle without implementation evidence
- Repeating LIFE audit phases as substitute for new mechanisms

## ORCH

- **Objective:** Orchestration causality boundaries
- **Final verdict:** `ORCH_EXEC_TRACK_FROZEN`
- **Evidence pack:** `evidencias_trisla_orch_exec_04_orchestration_track_final_freeze_20260518T030553Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- Orchestration persistence via TriSLAReservation + NetworkSliceInstance CRDs (10k+ / 9k+)
- NASP runtime authority: instantiate, capacity ledger, NSI watch, 60s reconciler
- Reconciliation continuity (TTL expire PENDING + orphan mark; detached from admission)
- Admission-before-orchestration (DE score/admission precedes Portal→NASP instantiate)
- Detached orchestration runtime (no feedback to DE, score, pressure, feasibility, reevaluation)
- Portal synchronous orchestration executor (POST /api/v1/nsi/instantiate after ACCEPT)
- DE orchestration authority semantic-only (orchestration_intent metadata; does not execute NASP)

### Forbidden claims
- orchestration-driven admission
- orchestration-driven pressure
- orchestration-driven score
- orchestration-driven reevaluation
- closed-loop orchestration
- autonomous orchestration causality
- runtime orchestration causality
- reconciliation→admission recomputation under frozen digest
- synthetic orchestration callbacks

## PAPER CONSOLIDATION

- **Objective:** Reviewer-safe unified taxonomy
- **Final verdict:** `FINAL_REVIEWER_SAFE_PROGRAM_READY`
- **Evidence pack:** `evidencias_trisla_paper_consolidation_track_01_master_reviewer_safe_consolidation_20260518T031427Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- Preventive SLA-aware admission under frozen digest (score_mode + PRB hard gates; SR-09)
- RAN-dominant hybrid admission with feasibility/resource-headroom awareness (n=450 NASP-hard+)
- Transport-informed scoring (w_transport P2) without multidomain-balanced causality
- Runtime tri-slice score differentiation under same network_state_id (score_mode triplets)
- DE authoritative admission/score before orchestration (ORCH admission-before-orchestration)
- Detached orchestration: Portal→NASP→CRD without feedback to DE/pressure/score (ORCH-04)
- NASP NSI watch + 60s capacity reconciler with 10k+ reservation CRDs (LIFE/ORCH)
- BC-NSSMF immutable governance lineage at submit (LIFE)
- SEM SQLite semantic persistence (intents/nests/slices)
- Scientific characterization of non-causal multidomain/runtime limits (negative-results contribution)
- Orchestration HTTP latency observable under operational contention (~9× baseline, NCM-06)
- Core domain observability without admission-causal effect (CORE-09)

### Forbidden claims
- closed-loop causality (orchestration or lifecycle)
- autonomous runtime SLA reevaluation
- orchestration-driven admission/pressure/score/reevaluation
- core-driven admission divergence
- multidomain balanced causality
- robust admission divergence without stratification
- continuous lifecycle governance
- runtime orchestration causality
- synthetic callbacks or fake telemetry under frozen digest
- weakened PRB guards or post-hoc threshold tuning

## PAPER WRITING

- **Objective:** Camera-ready manuscript integration
- **Final verdict:** `CAMERA_READY_MANUSCRIPT_FINAL`
- **Evidence pack:** `evidencias_trisla_paper_writing_track_03_camera_ready_manuscript_integration_20260518T142540Z`
- **Digest:** `sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6`

### Proven / allowed claims
- (see freeze summary JSON in `freezes/`)

### Forbidden claims
- (see freeze summary JSON in `freezes/`)
