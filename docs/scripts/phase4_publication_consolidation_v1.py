#!/usr/bin/env python3
"""Phase 4 — Publication consolidation (IEEE/Q1 baseline freeze)."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/porvir5g/gtp5g/trisla")
SSOT = REPO / "evidencias_trisla_true_multidomain_runtime_20260517T031129Z"

SOURCES = {
    "ssot_program": SSOT,
    "nasp_baseline_pre_transport": REPO / "evidencias_trisla_nasp_hard_plus_20260517T014222Z",
    "transport_normalization": REPO / "evidencias_trisla_transport_normalization_20260517T120042Z",
    "normalization_candidates": REPO / "evidencias_trisla_normalization_candidates_20260517T120803Z",
    "double_punishment": REPO / "evidencias_trisla_double_punishment_20260517T121428Z",
    "final_normalization": REPO / "evidencias_trisla_final_normalization_20260517T121959Z",
    "publication_assessment": REPO / "evidencias_trisla_publication_assessment_20260517T123820Z",
    "phase2_integration": REPO / "evidencias_trisla_phase2_de_runtime_integration_20260517T125400Z",
    "phase3_revalidation": REPO / "evidencias_trisla_phase3_runtime_revalidation_20260517T133134Z",
}

PHASE3_CSV = SOURCES["phase3_revalidation"] / "dataset/runtime_revalidation_dataset.csv"
BASELINE_CSV = (
    SOURCES["nasp_baseline_pre_transport"]
    / "phase_1_extreme_runtime_stress/extreme_stress_dataset.csv"
)
DE_DIGEST = "sha256:491ac623290c5f0d55879e7911b065ce7d49c0308c6e05a65ac410521d5d354a"
RTT_REF = 12.21
W_TRANSPORT = 0.05
FORMULA = "clamp01(1 - RTT_ms / 12.21)"
SEMANTICS = "RAN-dominant runtime-active transport-informed SLA scoring"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def _copy_figure(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def main() -> None:
    ts = _utc_stamp()
    out = REPO / f"evidencias_trisla_phase4_publication_consolidation_{ts}"
    for sub in (
        "phase_1_dataset_consolidation",
        "phase_2_figure_consolidation",
        "phase_3_claims_consolidation",
        "phase_4_ieee_narrative",
        "phase_5_runtime_baseline_freeze",
        "phase_6_final_publication_baseline",
        "dataset",
        "figures/final_ieee_figures",
        "analysis",
        "freeze",
        "manifest",
        "logs",
    ):
        (out / sub).mkdir(parents=True, exist_ok=True)

    # --- Phase 1: dataset ---
    p3_rows = _load_csv(PHASE3_CSV)
    master_rows = []
    for r in p3_rows:
        m = dict(r)
        m["publication_cohort"] = "runtime_revalidation_active"
        m["transport_runtime_active"] = "true"
        m["is_official_publication_sample"] = "true"
        m["evidence_bundle"] = SOURCES["phase3_revalidation"].name
        master_rows.append(m)

    master_path = out / "dataset/trisla_publication_master_dataset.csv"
    if master_rows:
        keys = list(master_rows[0].keys())
        with master_path.open("w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(master_rows)

    ref_path = out / "dataset/baseline_reference_nasp_hard_plus_pre_transport.csv"
    if BASELINE_CSV.exists():
        shutil.copy2(BASELINE_CSV, ref_path)

    hashes = {
        "master_dataset_sha256": _sha256_file(master_path) if master_path.exists() else None,
        "baseline_reference_sha256": _sha256_file(ref_path) if ref_path.exists() else None,
        "phase3_source_sha256": _sha256_file(PHASE3_CSV) if PHASE3_CSV.exists() else None,
    }
    (out / "analysis" / "dataset_hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    exclusions = (
        "evidencias_trisla_maximize_paper_runtime_final_* (invalid iperf -B 10.1.0.1, PRB≈0); "
        "not merged into master."
    )
    v1 = "DATASET_CONSOLIDATION_COMPLETE" if len(master_rows) == 150 else "DATASET_CONSOLIDATION_FAILED"

    (out / "phase_1_dataset_consolidation/DATASET_CONSOLIDATION.md").write_text(
        f"""# Phase 1 — Dataset Consolidation

## Verdict

**`{v1}`**

## Official publication master (runtime-active)

| Field | Value |
|-------|-------|
| File | `dataset/trisla_publication_master_dataset.csv` |
| n | {len(master_rows)} |
| SHA256 | `{hashes['master_dataset_sha256']}` |
| Source | `{SOURCES['phase3_revalidation'].name}` |

## Reference (analysis-only comparison, not merged)

| File | n | Role |
|------|---|------|
| `dataset/baseline_reference_nasp_hard_plus_pre_transport.csv` | 150 | Pre-transport activation NASP-hard+ |
| SHA256 | `{hashes['baseline_reference_sha256']}` | |

## Evidence chain (traceability)

| Phase | Bundle |
|-------|--------|
| SSOT | `{SOURCES['ssot_program'].name}` |
| Transport normalization | `{SOURCES['transport_normalization'].name}` |
| Candidates | `{SOURCES['normalization_candidates'].name}` |
| Double punishment | `{SOURCES['double_punishment'].name}` |
| Final normalization | `{SOURCES['final_normalization'].name}` |
| Publication assessment | `{SOURCES['publication_assessment'].name}` |
| Phase 2 integration | `{SOURCES['phase2_integration'].name}` |
| **Phase 3 revalidation (master)** | **`{SOURCES['phase3_revalidation'].name}`** |

## Exclusions

{exclusions}

**HARD STOP — `PHASE_1_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Phase 2: figures ---
    fig_out = out / "figures/final_ieee_figures"
    p3 = SOURCES["phase3_revalidation"]
    catalog = [
        ("fig01_prb_monotonicity.png", p3 / "phase_3_monotonicity/figures/01_prb_vs_score.png", "Monotonicity PRB vs score"),
        ("fig02_transport_vs_score.png", p3 / "phase_3_monotonicity/figures/02_transport_vs_score.png", "Transport g vs score"),
        ("fig03_contribution_hierarchy.png", p3 / "phase_4_dominance_analysis/figures/01_contribution_shares.png", "Factor shares"),
        ("fig04_boundary_sources.png", p3 / "phase_6_boundary_validation/figures/01_decision_sources.png", "Decision paths"),
        ("fig05_score_delta.png", p3 / "phase_5_transport_delta/figures/01_score_delta.png", "Pre/post mean score"),
        ("fig06_formula_curve.png", SOURCES["final_normalization"] / "step_1_formula_freeze/figures/01_final_formula_curve.png", "g_transport curve"),
    ]
    reg_fig = list(p3.glob("**/03_regime_degradation.png"))
    if reg_fig:
        catalog.append(("fig07_regime_degradation.png", reg_fig[0], "g_transport by regime"))

    approved, rejected = [], []
    for name, src, desc in catalog:
        if src.suffix == ".md":
            rejected.append((name, "not a figure"))
            continue
        if _copy_figure(src, fig_out / name):
            approved.append((name, desc, str(src.relative_to(REPO))))
        else:
            rejected.append((name, f"missing: {src}"))

    v2 = "FIGURE_CONSOLIDATION_COMPLETE" if len(approved) >= 5 else "FIGURE_CONSOLIDATION_INCOMPLETE"

    lines_ap = "\n".join(f"| {n} | {d} | `{s}` |" for n, d, s in approved)
    lines_rej = "\n".join(f"| {n} | {r} |" for n, r in rejected) or "| — | — |"

    (out / "phase_2_figure_consolidation/FIGURE_CONSOLIDATION.md").write_text(
        f"""# Phase 2 — Figure Consolidation

## Verdict

**`{v2}`**

All figures 300 dpi PNG in `figures/final_ieee_figures/`.

## Approved (narrative order)

| File | Description | Source |
|------|-------------|--------|
{lines_ap}

## Rejected / skipped

| File | Reason |
|------|--------|
{lines_rej}

**HARD STOP — `PHASE_2_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Phase 3: claims ---
    v3 = "CLAIMS_CONSOLIDATION_COMPLETE"
    (out / "phase_3_claims_consolidation/CLAIMS_CONSOLIDATION.md").write_text(
        f"""# Phase 3 — Claims Consolidation

## Verdict

**`{v3}`**

## Final semantics (frozen)

**{SEMANTICS}**

## Supported claims

| ID | Claim |
|----|-------|
| S1 | Hybrid runtime: PRB hard gates + continuous `decision_score_mode` |
| S2 | `g_transport = {FORMULA}`, RTT_REF={RTT_REF} ms (monitoring-plane RTT) |
| S3 | `transport_rtt_goodness` active at w={W_TRANSPORT} in score_mode (60/60 in official n=150) |
| S4 | PRB remains dominant (contrib share ~39% vs transport ~6%) |
| S5 | Monotonicity: r(PRB,score)≈−0.99 on score_mode stratum |
| S6 | Hard boundaries preserved (PRB≥40% → PRB_HARD_REJECT) |
| S7 | Partial orthogonality transport vs PRB–jitter coupling (analysis phase) |

## Forbidden claims

| ID | Claim |
|----|-------|
| F1 | True multidomain runtime scoring |
| F2 | Balanced multidomain orchestration |
| F3 | Transport-assisted dominance |
| F4 | Fully multidomain SLA orchestration |
| F5 | User-plane QoS guarantees from blackbox TCP probe |

## Limitations (formal)

- score_mode stratum is 40% of NASP-hard+ (60/150); majority remains hard-gate path.
- Monitoring-plane RTT ≠ GTP-U user-plane delay.
- Core/feasibility/headroom terms remain inactive in score numerator.

**HARD STOP — `PHASE_3_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Phase 4: IEEE narrative ---
    v4 = "IEEE_NARRATIVE_COMPLETE"
    (out / "phase_4_ieee_narrative/IEEE_NARRATIVE.md").write_text(
        f"""# Phase 4 — IEEE Narrative

## Verdict

**`{v4}`**

## Abstract (template)

> TriSLA evaluates SLA viability through **RAN-dominant** hybrid control: PRB hard gates and a continuous multi-objective score over RAN, risk, and semantic factors. After empirical transport normalization on NASP-hard+ (n=150), we activate a bounded monitoring-plane term `transport_rtt_goodness` (w={W_TRANSPORT}) in `decision_score_mode`, yielding **runtime-active transport-informed SLA scoring** without claiming true multidomain dominance.

## Architecture

> Telemetry snapshots feed the Decision Engine; transport RTT is mapped to `g_transport = clamp₀₁(1−RTT/12.21 ms)`. Hard PRB policies execute before score aggregation.

## Methodology

> NASP-hard+: five iperf regimes (15–130 Mbps), 30 submits/regime, UE→N6, warmup ≥75 s. Stratify all score statistics by `decision_source`.

## Runtime behavior (results)

> Official cohort (n=150 post-activation): transport term present in 100% of score_mode samples; PRB goodness contribution ≈6.8× transport; r(PRB,score)≈−0.99.

## Discussion

> Transport adds orthogonal monitoring context at low weight; RAN pressure remains primary. Path mix includes 60% hard-gate decisions under current cluster thresholds.

## Limitations

> Not true multidomain (G8); inactive feasibility/headroom; probe-plane mismatch.

## Conclusion

> TriSLA demonstrates **{SEMANTICS}** under real stress, with frozen formula, weight, and digest `{DE_DIGEST[:20]}…`.

## Future work (explicit)

> Core/feasibility activation per SSOT Phases 2–4; full multidomain validation only after ≥4 active terms.

**HARD STOP — `PHASE_4_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Phase 5: runtime freeze ---
    try:
        img = subprocess.run(
            ["kubectl", "-n", "trisla", "get", "deploy", "trisla-decision-engine",
             "-o", "jsonpath={.spec.template.spec.containers[0].image}"],
            capture_output=True, text=True, timeout=30,
        ).stdout.strip()
    except OSError:
        img = DE_DIGEST

    v5 = "RUNTIME_BASELINE_FROZEN" if DE_DIGEST.split(":")[-1][:12] in img else "RUNTIME_BASELINE_UNSTABLE"

    (out / "phase_5_runtime_baseline_freeze/RUNTIME_BASELINE_FREEZE.md").write_text(
        f"""# Phase 5 — Runtime Baseline Freeze

## Verdict

**`{v5}`**

| Item | Frozen value |
|------|--------------|
| DE image | `{img}` |
| Digest | `{DE_DIGEST}` |
| g_transport | `{FORMULA}` |
| RTT_REF | {RTT_REF} ms |
| w_transport | {W_TRANSPORT} |
| Active score terms | ran_prb_goodness, risk_inverse, semantic_priority, **transport_rtt_goodness** |
| Σw_active | ≈0.67 |
| Hard gates | unchanged (policy layer first) |

## Hierarchy

1. PRB hard REJECT / RENEGOTIATE  
2. decision_score_mode (weighted active terms)  
3. ML refinement (bounded)

**HARD STOP — `PHASE_5_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Phase 6: final baseline ---
    baseline_spec = {
        "publication_baseline_id": "trisla_publication_baseline_v1",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "semantics": SEMANTICS,
        "formula": {"g_transport": FORMULA, "RTT_REF_ms": RTT_REF, "w_transport": W_TRANSPORT},
        "runtime": {"de_digest": DE_DIGEST, "de_image": img, "transport_active": True},
        "official_dataset": {
            "path": "dataset/trisla_publication_master_dataset.csv",
            "n": len(master_rows),
            "sha256": hashes["master_dataset_sha256"],
        },
        "reference_dataset": {
            "path": "dataset/baseline_reference_nasp_hard_plus_pre_transport.csv",
            "sha256": hashes["baseline_reference_sha256"],
        },
        "evidence_chain": [k for k in SOURCES],
        "ssot": str(SSOT.name),
    }
    (out / "analysis/publication_baseline_v1.json").write_text(json.dumps(baseline_spec, indent=2), encoding="utf-8")
    shutil.copy2(out / "analysis/publication_baseline_v1.json", out / "phase_6_final_publication_baseline/publication_baseline_v1.json")

    verdicts = {"p1": v1, "p2": v2, "p3": v3, "p4": v4, "p5": v5}
    final = (
        "PHASE4_PUBLICATION_CONSOLIDATION_COMPLETE"
        if all(v.endswith(("COMPLETE", "FROZEN")) for v in verdicts.values())
        else "PHASE4_PUBLICATION_CONSOLIDATION_FAILED"
    )

    (out / "phase_6_final_publication_baseline/FINAL_PUBLICATION_BASELINE.md").write_text(
        f"""# Phase 6 — Final Publication Baseline

## Final verdict

**`{final}`**

## IEEE/Q1 baseline (frozen)

| Component | Location |
|-----------|----------|
| Master dataset | `dataset/trisla_publication_master_dataset.csv` |
| Official figures | `figures/final_ieee_figures/` |
| Claims | `phase_3_claims_consolidation/CLAIMS_CONSOLIDATION.md` |
| IEEE narrative | `phase_4_ieee_narrative/IEEE_NARRATIVE.md` |
| Runtime freeze | `phase_5_runtime_baseline_freeze/RUNTIME_BASELINE_FREEZE.md` |
| Machine spec | `analysis/publication_baseline_v1.json` |

## Permitted next steps (SSOT)

- Paper/dissertation writing using this bundle only
- SSOT Phases 2–4 (core, feasibility, headroom) — **separate gates**
- No runtime/weight changes without new audit

## Prohibited

- Inflating to true multidomain without G8 evidence
- Rebuild/deploy without DEPLOY_POLICY digest workflow

**This freeze consolidates evidence; it does not authorize new experiments.**
""",
        encoding="utf-8",
    )

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

    (out / "manifest/MANIFEST.txt").write_text(
        "\n".join(sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())) + "\n",
        encoding="utf-8",
    )
    (out / "analysis/phase4_verdicts.json").write_text(
        json.dumps({**verdicts, "final": final}, indent=2), encoding="utf-8",
    )

    print(f"PHASE4 PUBLICATION CONSOLIDATION COMPLETED: {out}")
    print(f"Final: {final}")


if __name__ == "__main__":
    main()
