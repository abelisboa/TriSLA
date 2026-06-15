# TriSLA — Master SSOT Runtime Baseline (V1)

**Status:** OFFICIAL · FROZEN · All future executions MUST follow this document.  
**Effective freeze:** 20260517T150959Z (Phase 6 resource headroom)  
**SSOT controlled execution:** `evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z`

---

## 1. Mission

This is the **official master prompt** for the TriSLA scientific runtime baseline. All future work MUST:

- Consult frozen evidence packs and this document
- Use official bibliography only (`references_4.bib`)
- Preserve reviewer safety, monotonicity, PRB dominance, digest-only deploy, runtime causality
- NOT inflate multidomain claims or alter frozen mathematics / gates / semantics

---

## 2. Mandatory SSOT paths

| Role | Path |
|------|------|
| Master program (transport-informed) | `evidencias_trisla_true_multidomain_runtime_20260517T031129Z` |
| Publication baseline | `evidencias_trisla_phase4_publication_consolidation_20260517T140548Z` |
| Feasibility runtime | `evidencias_trisla_phase5_feasibility_runtime_20260517T150015Z` |
| Resource headroom runtime | `evidencias_trisla_phase6_resource_headroom_runtime_20260517T150959Z` |
| SSOT controlled execution | `evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z` |
| Official bibliography | `evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z/references/references_4.bib` |

Repository root: `/home/porvir5g/gtp5g/trisla` (node006).

---

## 3. Mandatory opening declaration (every new prompt)

Copy and fill at the start of **every** new execution prompt:

```text
SSOT EVIDENCE PATHS:
  - evidencias_trisla_true_multidomain_runtime_20260517T031129Z
  - evidencias_trisla_phase4_publication_consolidation_20260517T140548Z
  - evidencias_trisla_phase5_feasibility_runtime_20260517T150015Z
  - evidencias_trisla_phase6_resource_headroom_runtime_20260517T150959Z
  - evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z

OFFICIAL BIB: evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z/references/references_4.bib

ACTIVE PUBLICATION BASELINE:
  RAN-dominant · feasibility-aware · resource-sustainability-aware · transport-informed · runtime-active SLA scoring

ACTIVE RUNTIME DIGEST (Decision Engine):
  sha256:67659064d35a72656f1554cfbdb7a166a052d1a20a01aa5688baf201023f6be5

ALLOWED CLAIMS: (see §5)
FORBIDDEN CLAIMS: (see §6)
```

---

## 4. Official runtime baseline

**Scientific label (exact):**

> RAN-dominant · feasibility-aware · resource-sustainability-aware · transport-informed · runtime-active SLA scoring

**Official DE digest:**

`sha256:67659064d35a72656f1554cfbdb7a166a052d1a20a01aa5688baf201023f6be5`

**Rollback digest (Phase 5 / pre–Phase 6):**

`sha256:ee594b5cddcdc416702f9f526fb51bbd503e3f0193504e1d4f71b9cf920c761e`

---

## 5. Allowed claims

- RAN-dominant runtime scoring
- Feasibility-aware runtime scoring (`feasibility_goodness`, Phase 5)
- Resource-sustainability-aware runtime scoring (`resource_headroom_goodness`, Phase 6)
- Transport-informed runtime scoring (`transport_rtt_goodness`, frozen RTT_REF)
- Runtime-active SLA scoring (`decision_score_mode`)
- PRB hard gates (`HARD_PRB_RENEGOTIATE`, `HARD_PRB_REJECT`)
- Monotonic runtime behavior (evidence: Phase 6 monotonicity, PRB vs score r ≈ −0.94)
- Multidomain **observability** / **orchestration** / **lifecycle supervision** (architectural)
- Blockchain governance persistence (where evidenced in BC path)
- SLA-aware admission semantics (literature-aligned wording only)
- **Conceptually aligned** with 3GPP / ETSI / O-RAN (cite `references_4.bib`; never normative compliance)

---

## 6. Forbidden claims

- True / balanced multidomain **runtime scoring**
- Transport-assisted **dominance**
- Core **runtime scoring** in score numerator (`core_goodness` latent)
- **Normative compliance** or standards-certified implementation
- **Full slice divergence** (URLLC-only campaign evidence)
- Fully autonomous orchestration without evidence
- Any claim without evidence + bib support → mark `UNSUPPORTED_CLAIM`

---

## 7. Official formulas (frozen — do not alter)

All goodness terms ∈ [0, 1] via `clamp01`.

| Term | Formula | Source |
|------|---------|--------|
| `ran_prb_goodness` | `g_prb = clamp01(1 − PRB_util/100)` | `decision_score_mode.py` |
| `transport_rtt_goodness` | `g_transport = clamp01(1 − RTT_ms / RTT_REF)`; `RTT_REF = 12.21` ms (env) | `decision_score_mode._g_transport_from_rtt` |
| `resource_pressure` (V1) | Weighted mean: PRB_norm×0.4 + RTT_norm×0.3 + CPU_norm×0.3 (renormalize if missing) | `feasibility_runtime.compute_resource_pressure_v1` |
| `feasibility_goodness` | `clamp01(1 − (ml_risk + resource_pressure) / 2)` | `feasibility_runtime.compute_feasibility_score` |
| `resource_headroom_goodness` | `clamp01(1 − resource_pressure)` | `decision_score_mode` (w_press term) |
| `risk_inverse` | `clamp01(1 − final_risk)` | `decision_score_mode.py` |
| **Score** | `decision_score = Σ(wᵢ·gᵢ) / Σwᵢ` over **active** terms only | `decision_score_mode.py` |

**URLLC profile weights (frozen):** w_feas=0.22, w_prb=0.22, w_press=0.18, w_risk=0.28, w_sem=0.12, w_transport=0.05 (Σw=1.07 when all terms active).

---

## 8. Official runtime hierarchy (mean contribution share, score_mode stratum)

From Phase 6 freeze dataset (`20260517T150959Z`, n=60 score_mode):

| Rank | Factor | Mean \|contrib\| share |
|------|--------|------------------------:|
| 1 | `risk_inverse` | 0.241 (w_risk=0.28 URLLC) |
| 2 | `feasibility_goodness` | 0.231 |
| 3 | `ran_prb_goodness` | 0.223 |
| 4 | `resource_headroom_goodness` | 0.194 |
| 5 | `semantic_priority` | 0.078 |
| 6 | `transport_rtt_goodness` | 0.034 |

Transport remains **auxiliary**; PRB **hard gates** dominate global mix (90/150 paths).

---

## 9. Official hard gates

| Env | Value |
|-----|------:|
| `HARD_PRB_RENEGOTIATE` | 0.25 |
| `HARD_PRB_REJECT` | 0.40 |

---

## 10. Runtime feature flags (frozen)

| Env | Value |
|-----|-------|
| `TRISLA_FEASIBILITY_RUNTIME_ENABLED` | `true` |
| `TRISLA_RESOURCE_HEADROOM_RUNTIME_ENABLED` | `true` |
| `TRISLA_TRANSPORT_RTT_GOODNESS_ENABLED` | `true` |
| `TRISLA_TRANSPORT_RTT_REF_MS` | `12.21` |
| `TRISLA_TRANSPORT_SCORE_WEIGHT` | `0.05` |

---

## 11. Deployment policy

**Required:** `build → push GHCR → obtain digest → deploy by sha256 → rollout → smoke → freeze`

**Forbidden:** `:latest`, mutable tags, undeclared deploys, local-only images.

---

## 12. Dataset policy

**Official dataset:** `evidencias_trisla_phase6_resource_headroom_runtime_20260517T150959Z/dataset/resource_headroom_runtime_dataset.csv`  
**SHA256 (frozen):** `ef553baf2db7968c12ca59399ca153d6a340bb521428a116a044578c353ddb64`

- NASP-hard+ · 150 submits · regimes 15/40/70/100/130 Mbps · 30 submits/regime
- **No new campaigns** unless real functional / mathematical / runtime change.

Reuse declaration: `PHASE6_SKIP_CAMPAIGN=1` when consolidating evidence only.

---

## 13. Phase execution pattern

Every phase MUST follow:

1. Audit  
2. Documentation  
3. Validation  
4. Monotonicity  
5. Dominance  
6. Publication reassessment  
7. Freeze  

**HARD STOP** after each phase until explicit `PHASE_N_APPROVED`.

---

## 14. Authorized future phases

- Results / Discussion / Limitations sections  
- Camera-ready baseline · IEEE narrative refinement  
- Figures · bibliography consolidation  
- Slice semantics evolution (evidence-bound)

---

## 15. Restricted future phases (require full scientific audit first)

- `core_goodness` runtime activation  
- Balanced multidomain runtime scoring  
- Autonomous orchestration · dynamic policy adaptation  

---

## 16. Golden rule

Every statement MUST trace to: **evidence · freeze · dataset · live runtime · bibliography**.

Unsupported → `UNSUPPORTED_CLAIM`.

---

## 17. SSOT controlled execution status

| Phase | Document | Verdict |
|-------|----------|---------|
| 1 | `phase_1_runtime_baseline_validation/RUNTIME_BASELINE_VALIDATION.md` | `RUNTIME_BASELINE_VALIDATED` |
| 2 | `phase_2_formula_definition_validation_20260517T164452Z/…/FORMULA_DEFINITION_VALIDATION.md` | `FORMULA_BASELINE_VALIDATED` |
| 3 | `phase_3_digest_runtime_validation_20260517T164931Z/…/DIGEST_RUNTIME_VALIDATION.md` | `DIGEST_RUNTIME_VALIDATED` |
| 4 | `phase_4_dataset_reuse_validation_20260517T165318Z/…/DATASET_REUSE_VALIDATION.md` | `DATASET_REUSE_VALIDATED` |
| 5 | `phase_5_monotonicity_confirmation_20260517T165549Z/…/MONOTONICITY_CONFIRMATION.md` | `MONOTONICITY_CONFIRMED` |
| 6 | `phase_6_dominance_confirmation_20260517T165928Z/…/DOMINANCE_CONFIRMATION.md` | `DOMINANCE_CONFIRMED` |
| 7 | `phase_7_slice_semantics_confirmation_20260517T170335Z/…/SLICE_SEMANTICS_CONFIRMATION.md` | `SLICE_SEMANTICS_CONFIRMED` |
| 8 | `phase_8_standards_alignment_confirmation_20260517T170746Z/…/STANDARDS_ALIGNMENT_CONFIRMATION.md` | `STANDARDS_ALIGNMENT_CONFIRMED` |
| 9 | `phase_9_publication_claims_freeze_20260517T171217Z/…/PUBLICATION_CLAIMS_FREEZE.md` | `PUBLICATION_CLAIMS_FROZEN` |
| 10 | `phase_10_final_ssot_freeze_20260517T171557Z/…/FINAL_SSOT_BASELINE_FREEZE.md` | `FINAL_SSOT_BASELINE_FROZEN` — **HARD STOP FINAL** (no auto phases) |

---

*End of Master SSOT Runtime Baseline V1*
