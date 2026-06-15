#!/usr/bin/env python3
"""Substep 5 — Publication assessment (transport-informed scoring, SSOT-aligned)."""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

SSOT = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_true_multidomain_runtime_20260517T031129Z"
)
FINAL_NORM = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_final_normalization_20260517T121959Z"
)
DOUBLE_PUN = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_double_punishment_20260517T121428Z"
    "/analysis/double_punishment_bundle.json"
)
NASP_RAW = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nasp_hard_plus_20260517T014222Z"
    "/phase_1_extreme_runtime_stress/raw"
)

RTT_REF = 12.21
FINAL_FORMULA = "clamp01(1 - RTT_ms / 12.21)"
SAFE_WEIGHT_MIN = 0.05
SAFE_WEIGHT_MAX = 0.08
SAFE_WEIGHT_HARD_MAX = 0.10
SEMANTICS_ALLOWED = "transport-informed runtime scoring"
PROGRAM_ID = "evidencias_trisla_true_multidomain_runtime_20260517T031129Z"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_nasp_sources() -> Counter:
    c: Counter = Counter()
    for d in NASP_RAW.iterdir():
        if not d.is_dir():
            continue
        for p in d.glob("submit_*.json"):
            row = json.loads(p.read_text(encoding="utf-8")).get("row") or {}
            c[row.get("decision_source") or "unknown"] += 1
    return c


def _freeze(out: Path) -> None:
    for cmd, name in (
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"], "runtime_after.txt"),
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"], "runtime_after.yaml"),
    ):
        fp = out / "freeze" / name
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            fp.write_text(proc.stdout or proc.stderr or "", encoding="utf-8")
        except OSError:
            fp.write_text("kubectl unavailable", encoding="utf-8")


def main() -> None:
    ts = _utc_stamp()
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_publication_assessment_{ts}")
    steps = {
        1: out / "step_1_claims_matrix",
        2: out / "step_2_runtime_scope",
        3: out / "step_3_reviewer_risk",
        4: out / "step_4_ieee_wording",
        5: out / "step_5_final_publication_freeze",
    }
    for p in list(steps.values()) + [out / "analysis", out / "figures", out / "freeze"]:
        p.mkdir(parents=True, exist_ok=True)

    dp = json.loads(DOUBLE_PUN.read_text(encoding="utf-8"))
    sources = _load_nasp_sources()
    n_total = sum(sources.values())
    n_score = sources.get("decision_score_mode", 0)
    n_reneg = sources.get("PRB_HARD_RENEGOTIATE_THRESHOLD", 0)
    n_reject = sources.get("PRB_HARD_REJECT_THRESHOLD", 0)

    # --- Step 1 claims matrix figure ---
    s1f = steps[1] / "figures"
    s1f.mkdir(exist_ok=True)
    claims = [
        ("Transport-informed scoring (A, w≤0.10)", "supported"),
        ("g_transport bounded monotone in RTT", "supported"),
        ("RTT_REF from NASP P99 tail", "supported"),
        ("Partial orthogonality to PRB–jitter", "supported"),
        ("Transport-assisted multidomain", "forbidden"),
        ("True multidomain runtime scoring", "forbidden"),
        ("Balanced multidomain orchestration", "forbidden"),
        ("Jitter-primary g_transport", "forbidden"),
        ("≥4 active score domains today", "unsupported"),
        ("Transport dominates decision_score", "unsupported"),
        ("SLA-aware full profile Σw=1.02 live", "unsupported"),
        ("Runtime adaptation via transport", "partial"),
        ("Causal E2E PRB→decision", "supported"),
        ("Monitoring-plane = user-plane QoS", "forbidden"),
    ]
    colors = {"supported": "#2ca02c", "partial": "#ff7f0e", "unsupported": "#bcbd22", "forbidden": "#d62728"}
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(claims))
    for i, (label, status) in enumerate(claims):
        ax.barh(i, 1, color=colors[status], alpha=0.85)
        ax.text(0.02, i, f"{label}  [{status}]", va="center", fontsize=8, color="white" if status == "forbidden" else "black")
    ax.set_yticks([])
    ax.set_xlim(0, 1)
    ax.set_title("Claims classification (transport track)")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=colors[k], label=k) for k in colors], loc="lower right")
    plt.tight_layout()
    plt.savefig(s1f / "01_claims_matrix.png", dpi=300)
    plt.close()

    step1_verdict = "CLAIMS_MATRIX_DEFINED"

    (steps[1] / "CLAIMS_MATRIX.md").write_text(
        f"""# Step 1 — Claims Matrix

**SSOT:** `{PROGRAM_ID}`  
**Transport freeze:** `evidencias_trisla_final_normalization_20260517T121959Z`  
**UTC:** {datetime.now(timezone.utc).isoformat()}

## Verdict

**`{step1_verdict}`**

---

## Scientifically supported

| Claim | Evidence |
|-------|----------|
| `g_transport = {FINAL_FORMULA}`, RTT_REF={RTT_REF} ms | Formula freeze + NASP-hard+ n={dp['n']} |
| Bounded [0,1], monotone decreasing in RTT | Grid proof (Step 1 normalization) |
| **{SEMANTICS_ALLOWED}** at w∈[{SAFE_WEIGHT_MIN},{SAFE_WEIGHT_MAX}] | Double-punishment + weight safety audits |
| partial r(PRB,g\|jitter) ≈ {dp['coupling_A']['partial_prb_g_given_jitter']:.2f} | Double punishment Step 2 |
| PRB causal E2E on NASP-hard+ | Prior `evidencias_trisla_e2e_prb_propagation_*` |
| Hard PRB gates at ~25% / ~40% unchanged | Boundary audits; no deploy in this track |

## Partially supported (conditional wording only)

| Claim | Condition |
|-------|-----------|
| Future runtime may include transport term | **Only after** `PHASE_1_APPROVED` + digest deploy per DEPLOY_POLICY |
| Transport adds operational context | Counterfactual n={dp['n_score_mode']} score_mode; not decision flips observed |
| Multidomain **architecture** present | Telemetry snapshot fields exist; **not** score numerator today |

## Unsupported (do not claim)

| Claim | Why |
|-------|-----|
| True multidomain runtime scoring | G8: need ≥4 active terms; baseline Σw_active=0.62, 3 terms |
| Transport dominates score | 113/{n_total} decisions via PRB_HARD_*; score_mode n={n_score} |
| Full URLLC profile active | `feasibility`, `resource_headroom` inactive |
| Balanced multidomain orchestration | No orchestration loop driven by g_transport |

## Forbidden

| Claim | Risk |
|-------|------|
| transport-assisted multidomain dominance | Double punishment / inflation |
| Jitter/hybrid g_transport as production | Rejected Candidate F (r(PRB,g)≈{dp['coupling_F']['pearson_prb_g']:.2f}) |
| User-plane QoS from blackbox probe | Measurement plane mismatch |
| "Fully multidomain" / "adaptive multidomain orchestration" | Exceeds evidence (SCIENTIFIC_GUARDS G8) |

## Extrapolation watchlist

- Extending NASP tail (130 Mbps) to general SLA guarantees.
- Implying decision changes when all score_mode samples remained ACCEPT.
- Mixed-path correlation without `decision_source` stratification.

**HARD STOP — await `STEP_1_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 2 runtime scope ---
    s2f = steps[2] / "figures"
    s2f.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["score_mode\n(active score)", "PRB hard\nreneg", "PRB hard\nreject"]
    sizes = [n_score, n_reneg, n_reject]
    colors_pie = ["#1f77b4", "#ff7f0e", "#d62728"]
    ax.pie(sizes, labels=labels, autopct="%1.0f%%", colors=colors_pie, startangle=90)
    ax.set_title(f"NASP-hard+ decision paths (n={n_total})")
    plt.tight_layout()
    plt.savefig(s2f / "01_decision_path_share.png", dpi=300)
    plt.close()

    domains = [
        ("ran_prb_goodness", "runtime-active", 0.22),
        ("risk_inverse", "runtime-active", 0.28),
        ("semantic_priority", "runtime-active", 0.12),
        ("g_transport (frozen spec)", "runtime-latent", 0.0),
        ("feasibility", "runtime-latent", 0.22),
        ("resource_headroom", "runtime-latent", 0.18),
        ("core_cpu/memory", "observational-only", 0.0),
        ("transport RTT/jitter snapshot", "observational-only", 0.0),
    ]
    fig, ax = plt.subplots(figsize=(9, 4))
    names = [d[0] for d in domains]
    status = [d[1] for d in domains]
    sc = {"runtime-active": "#2ca02c", "runtime-latent": "#ff7f0e", "observational-only": "#9467bd"}
    ax.barh(names, [d[2] for d in domains], color=[sc[s] for s in status])
    ax.set_xlabel("configured weight (profile)")
    ax.set_title("Domain map vs score_mode numerator")
    plt.tight_layout()
    plt.savefig(s2f / "02_domain_map.png", dpi=300)
    plt.close()

    step2_verdict = "RUNTIME_SCOPE_DEFINED"

    (steps[2] / "RUNTIME_SCOPE.md").write_text(
        f"""# Step 2 — Runtime Scope

## Verdict

**`{step2_verdict}`**

---

## Decision path map (NASP-hard+ n={n_total})

| Path | n | Share | Role |
|------|--:|------:|------|
| `decision_score_mode` | {n_score} | {100*n_score/n_total:.1f}% | Weighted viability (Σw_active=0.62) |
| `PRB_HARD_RENEGOTIATE_THRESHOLD` | {n_reneg} | {100*n_reneg/n_total:.1f}% | Hard gate |
| `PRB_HARD_REJECT_THRESHOLD` | {n_reject} | {100*n_reject/n_total:.1f}% | Hard gate |

## Domain classification (MASTER_PLAN + audits)

| Domain / term | Class | In score numerator today? |
|---------------|-------|---------------------------|
| `ran_prb_goodness` | **runtime-active** | Yes (w=0.22) |
| `risk_inverse` | **runtime-active** | Yes (w=0.28) |
| `semantic_priority` | **runtime-active** | Yes (w=0.12) |
| `g_transport` (frozen) | **runtime-latent** | **No** — spec only |
| `feasibility` | **runtime-latent** | No (null inputs) |
| `resource_headroom` | **runtime-latent** | No (null inputs) |
| Core CPU/memory | observational-only | Composite path only |
| Transport RTT/jitter | observational-only | Snapshot/metadata |

## Why transport is NOT multidomain dominance

1. **113/{n_total}** decisions never consult `decision_score` transport term.
2. RAN hard gates are **policy layer** (SCIENTIFIC_GUARDS G4) — unchanged.
3. Frozen g_transport is **not deployed**; counterfactual shift <0.02 mean @ w≤0.08.
4. G8 threshold (≥4 active terms) **not met** — accurate label per SSOT: **RAN-driven** with transport **spec ready**.

## Limitations

- Scope validated on NASP-hard+ proxy PRB path only.
- score_mode stratum is minority ({n_score}/{n_total}).

**HARD STOP — await `STEP_2_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 3 reviewer risk ---
    s3f = steps[3] / "figures"
    s3f.mkdir(exist_ok=True)
    risks = [
        ("Double punishment", "Medium", "Use A not F; w≤0.10; cite partial r"),
        ("Fake multidomain", "High if mis-worded", "Forbidden claims list; G8"),
        ("PRB duplication", "Low for A", "Spearman(PRB,g_A)≈0; partial control"),
        ("Instability / collapse", "Low @ w≤0.10", "0% below ACCEPT counterfactual"),
        ("Probe ≠ user plane", "Medium", "Limitations paragraph mandatory"),
        ("Stratification omission", "High", "Always filter decision_source"),
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(risks))
    risk_col = {"Low": 0.2, "Medium": 0.5, "High if mis-worded": 0.85, "High": 0.9}
    vals = [risk_col.get(r[1].split()[0], 0.5) for r in risks]
    ax.barh(y, vals, color="#d62728", alpha=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in risks], fontsize=9)
    ax.set_xlabel("Reviewer attack severity (qualitative)")
    ax.set_xlim(0, 1)
    plt.tight_layout()
    plt.savefig(s3f / "01_reviewer_risk.png", dpi=300)
    plt.close()

    step3_verdict = "REVIEWER_RISK_DEFINED"

    (steps[3] / "REVIEWER_RISK.md").write_text(
        f"""# Step 3 — Reviewer Risk

## Verdict

**`{step3_verdict}`**

---

## Attack surface

| Reviewer claim | Valid? | Mitigation |
|----------------|:------:|------------|
| Double punishment | Partially if F/jitter used | **Frozen: A only**; partial r≈−0.09; weight cap |
| Fake multidomain | **Yes if overclaimed** | Use "{SEMANTICS_ALLOWED}" only; cite G8 not met |
| PRB duplication | Weak for A | Spearman≈0; transport is RTT plateau not jitter |
| Instability | Unlikely @ w≤0.10 | Publish weight sweep table |
| Wrong correlation | **Yes if unstratified** | Mandate decision_source filter |

## Mitigations (reviewer-safe)

1. State **RAN-driven** baseline explicitly (MASTER_PLAN §2).
2. Separate **architectural multidomain** (telemetry) from **runtime-active** (3 terms).
3. Report hard-gate share ({100*(n_reneg+n_reject)/n_total:.0f}% of NASP-hard+).
4. Limitations: probe plane, tail-sparse RTT_REF, score_mode n={n_score}.

## Safe claims under review

- Frozen formula and refs (analysis-only freeze).
- Transport-**informed** (not assisted) with w∈[{SAFE_WEIGHT_MIN},{SAFE_WEIGHT_MAX}].
- Future Phase 1 activation is **hypothesis** until PHASE_1_APPROVED + deploy digest.

**HARD STOP — await `STEP_3_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 4 IEEE wording ---
    step4_verdict = "IEEE_WORDING_DEFINED"

    (steps[4] / "IEEE_WORDING.md").write_text(
        f"""# Step 4 — IEEE Wording

## Verdict

**`{step4_verdict}`**

---

## Abstract (recommended)

> TriSLA evaluates SLA viability through a hybrid runtime model combining PRB hard gates and a continuous decision score over RAN, risk, and semantic factors (Σw_active=0.62). Transport monitoring-plane RTT is normalized into a bounded goodness term g_transport = clamp₀₁(1−RTT/12.21 ms), empirically derived from NASP stress campaigns. **This work reports transport-informed scoring semantics** and validates orthogonality to RAN–jitter coupling; **runtime activation of g_transport is not claimed** in the current deployment baseline.

## Architecture

> **Recommended:** "Architecturally, transport metrics are captured in the telemetry snapshot; a frozen g_transport specification is defined for optional future inclusion in decision_score_mode at low weight (w≤0.10)."

> **Forbidden:** "TriSLA performs balanced multidomain runtime orchestration across RAN, transport, and core."

## Runtime behavior

> **Recommended:** "Under decision_score_mode (n={n_score}/{n_total} on NASP-hard+), decisions are driven primarily by ran_prb_goodness, risk_inverse, and semantic_priority; PRB hard gates handle the majority of stress outcomes."

> **Forbidden:** "Transport dominates runtime SLA decisions."

## Results

> **Recommended:** "Counterfactual analysis shows that adding g_transport at w∈[0.05,0.08] preserves PRB–score correlation and does not collapse the ACCEPT band in the observed score_mode stratum."

> **Forbidden:** "Transport-assisted multidomain scoring improves SLA outcomes."

## Limitations

> Monitoring-plane TCP RTT ≠ GTP-U user-plane delay; RTT_REF anchored to P99 tail (130 Mbps regime); jitter excluded from g_transport to avoid PRB-aligned double penalty (r(PRB,jitter)≈0.79).

## Conclusion

> **Recommended:** "TriSLA remains RAN-driven at runtime with a publication-grade, transport-informed extension path; true multidomain scoring awaits activation of latent terms per phased validation (SSOT `{PROGRAM_ID}`)."

## Phrase blacklist

- fully multidomain / true multidomain scoring (runtime)
- transport-assisted / transport-dominant
- balanced multidomain runtime
- adaptive multidomain orchestration

**HARD STOP — await `STEP_4_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 5 final freeze ---
    spec = {
        "publication_baseline": "trisla_transport_informed_v1",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "ssot_program": PROGRAM_ID,
        "formula": {"g_transport": FINAL_FORMULA, "RTT_REF_ms": RTT_REF},
        "weight_policy": {
            "recommended": [SAFE_WEIGHT_MIN, SAFE_WEIGHT_MAX],
            "hard_max": SAFE_WEIGHT_HARD_MAX,
        },
        "semantics_allowed": SEMANTICS_ALLOWED,
        "semantics_forbidden": [
            "true multidomain runtime scoring",
            "transport-assisted multidomain orchestration",
            "balanced multidomain runtime scoring",
        ],
        "runtime_status": "NOT_ACTIVATED",
        "deploy_authorized": False,
        "evidence_chain": [
            "evidencias_trisla_transport_normalization_*",
            "evidencias_trisla_normalization_candidates_*",
            "evidencias_trisla_double_punishment_*",
            "evidencias_trisla_final_normalization_20260517T121959Z",
            f"evidencias_trisla_publication_assessment_{ts}",
        ],
        "permitted_next_steps": [
            "PHASE_0_APPROVED gate (if not yet) on true_multidomain program",
            "PHASE_1 design + digest deploy only after PHASE_1_APPROVED",
            "Paper text using IEEE_WORDING.md templates only",
        ],
        "forbidden_next_steps": [
            "Silent runtime activation",
            ":latest deploy",
            "Changing RTT_REF without new campaign",
            "Candidate F as primary g_transport",
        ],
    }
    (steps[5] / "publication_baseline_v1.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    (out / "analysis" / "publication_baseline_v1.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")

    s5f = steps[5] / "figures"
    s5f.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axis("off")
    txt = (
        f"PUBLICATION BASELINE v1\\n"
        f"{'='*40}\\n"
        f"g = clamp01(1 - RTT/12.21)\\n"
        f"w ∈ [{SAFE_WEIGHT_MIN}, {SAFE_WEIGHT_MAX}] (max {SAFE_WEIGHT_HARD_MAX})\\n"
        f"Semantics: {SEMANTICS_ALLOWED}\\n"
        f"Runtime: NOT ACTIVATED\\n"
        f"Deploy: NOT AUTHORIZED"
    )
    ax.text(0.5, 0.5, txt, ha="center", va="center", fontsize=11, family="monospace",
            bbox=dict(boxstyle="round", facecolor="#e8f4e8"))
    plt.savefig(s5f / "01_publication_baseline_card.png", dpi=200)
    plt.close()

    final_verdict = "PUBLICATION_ASSESSMENT_DEFINED"

    (steps[5] / "FINAL_PUBLICATION_FREEZE.md").write_text(
        f"""# Step 5 — Final Publication Freeze

## Final verdict

**`{final_verdict}`**

---

## Consolidated baseline

| Field | Frozen value |
|-------|--------------|
| Formula | `{FINAL_FORMULA}` |
| RTT_REF | {RTT_REF} ms |
| w_transport | {SAFE_WEIGHT_MIN}–{SAFE_WEIGHT_MAX} (hard max {SAFE_WEIGHT_HARD_MAX}) |
| Semantics | **{SEMANTICS_ALLOWED}** |
| Runtime activation | **NO** |
| Deploy | **NO** |

## SSOT alignment

| Document | Status |
|----------|--------|
| MASTER_PLAN.md | Phases 1–8; transport = Phase 1 **after** gate |
| PHASE_SEQUENCE.md | No skip; publication = Phase 8 |
| SCIENTIFIC_GUARDS.md | G1–G8 respected; G8 **not** satisfied today |
| DEPLOY_POLICY.md | Digest-only; not triggered |
| VALIDATION_POLICY.md | L7 claims ⊆ this freeze |
| FINAL_FREEZE.md (normalization) | Incorporated |

## Claims summary

- **Supported:** transport-informed semantics, frozen formula, orthogonality evidence, RAN-driven baseline.
- **Forbidden:** true/assisted/balanced multidomain runtime claims.
- **Conditional:** Phase 1 runtime activation post `PHASE_1_APPROVED`.

## Deployment restrictions

1. No DE/SEM/helm change without phase gate + digest record.
2. No weight > {SAFE_WEIGHT_HARD_MAX} without re-audit.
3. Stratify all score statistics by `decision_source`.

## Authorized next steps

1. Operator sign-off: `STEP_1_APPROVED` … `STEP_5_APPROVED` on this assessment.
2. `PHASE_1_APPROVED` on program `{PROGRAM_ID}` when ready for **implementation** phase (separate prompt).
3. Dissertation/paper sections using `IEEE_WORDING.md` verbatim templates.

## Artifacts

- `publication_baseline_v1.json`
- Prior chain: normalization → candidates → double punishment → final normalization

**This document does NOT authorize deploy or runtime activation.**
""",
        encoding="utf-8",
    )

    # Also write master PUBLICATION_ASSESSMENT.md at root of OUT for prompt compatibility
    (out / "PUBLICATION_ASSESSMENT.md").write_text(
        (steps[5] / "FINAL_PUBLICATION_FREEZE.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    bundle = {"ts": ts, "verdicts": {
        "step1": step1_verdict, "step2": step2_verdict, "step3": step3_verdict,
        "step4": step4_verdict, "final": final_verdict,
    }, "nasp_sources": dict(sources), "spec": spec}
    (out / "analysis" / "publication_bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    _freeze(out)
    (out / "analysis" / "MANIFEST.txt").write_text(
        "\n".join(sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())) + "\n",
        encoding="utf-8",
    )

    print(f"PUBLICATION ASSESSMENT COMPLETED: {out}")
    print(f"Final: {final_verdict}")


if __name__ == "__main__":
    main()
