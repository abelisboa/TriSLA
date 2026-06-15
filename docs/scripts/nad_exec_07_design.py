#!/usr/bin/env python3
"""NAD-EXEC-07: higher-stress liminal campaign design (design-only)."""

from __future__ import annotations

import csv
import json
import os
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

OUT = Path(os.environ["OUT"])
SR05 = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_sr_exec_05_tri_slice_nasp_hardplus_campaign_20260517T182121Z/dataset/enriched/tri_slice_runtime_dataset.csv"
)
LIM01 = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nad_exec_05_liminal_scoremode_campaign_20260517T201420Z/dataset/enriched/liminal_scoremode_dataset.csv"
)
NAD06 = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nad_exec_06_liminal_admission_divergence_validation_20260517T212719Z/analysis/liminal_admission_divergence_validation_summary.json"
)
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"

PRB_LO, PRB_HI, PRB_SOFT_ABORT, PRB_HARD_ABORT = 18.0, 24.0, 23.5, 24.0
HARD_RENEG = 25.0
SCORE_LO, SCORE_HI = 0.52, 0.58

# Frozen NAD-LIMINAL-02 design parameters
IPERF_LADDER = [
    {"label": "22Mbps", "bitrate": "22M", "role": "calibration_low"},
    {"label": "26Mbps", "bitrate": "26M", "role": "calibration_mid"},
    {"label": "28Mbps", "bitrate": "28M", "role": "primary_target"},
    {"label": "30Mbps", "bitrate": "30M", "role": "primary_upper"},
    {"label": "28Mbps-fallback", "bitrate": "28M", "role": "fallback_stable"},
]
REPS_PER_REGIME = 20
WARMUP_S = 120
WARMUP_CALIBRATION_S = 90
SIGMA_MAX = 2.0
FORBIDDEN_BITRATES = ["40M", "70M", "100M", "130M"]


def _load(p: Path) -> List[dict]:
    return list(csv.DictReader(p.open(encoding="utf-8")))


def _regime_stats(rows: List[dict]) -> Dict[str, Any]:
    by: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        by[r.get("regime_mbps", r.get("regime_label", "?"))].append(r)
    out = {}
    for reg, sub in sorted(by.items()):
        prb = [float(r["prb_utilization_real"]) for r in sub if r.get("prb_utilization_real")]
        sc = [
            float(r["decision_score"])
            for r in sub
            if r.get("decision_score") and r.get("decision_mode") == "decision_score"
        ]
        modes = Counter(r.get("decision_mode") for r in sub)
        out[reg] = {
            "n": len(sub),
            "prb_mean": statistics.mean(prb) if prb else None,
            "prb_max": max(prb) if prb else None,
            "score_mean": statistics.mean(sc) if sc else None,
            "hard_gate_pct": modes.get("hard_prb_gate", 0) / len(sub) if sub else 0,
            "score_mode_n": modes.get("decision_score", 0),
        }
    return out


def _figures(sr_stats: dict, lim_stats: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    # 1 operating point reconstruction
    fig, ax = plt.subplots(figsize=(9, 5))
    regs = ["15Mbps", "LIMINAL-01", "40Mbps(sm)", "130Mbps(sm)"]
    prb_vals = [
        sr_stats.get("15Mbps", {}).get("prb_mean") or 13.2,
        lim_stats.get("liminal-00", {}).get("prb_mean") or 8.9,
        26.3,
        sr_stats.get("130Mbps", {}).get("prb_max") or 22.1,
    ]
    ax.bar(regs, prb_vals, color=["#3498db", "#9b59b6", "#e74c3c", "#2ecc71"])
    ax.axhspan(PRB_LO, PRB_HI, alpha=0.25, color="green", label="target 18–24%")
    ax.axhline(PRB_HARD_ABORT, color="orange", ls="--", label="abort 24%")
    ax.set_ylabel("PRB %")
    ax.set_title("Operating-point reconstruction map")
    ax.legend(fontsize=7)
    fig.savefig(fd / "operating_point_reconstruction_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 2 higher-stress corridor
    fig, ax = plt.subplots(figsize=(8, 4))
    ladder_mbps = [22, 26, 28, 30, 28]
    ax.plot(ladder_mbps, [16, 19, 21, 23, 20], "o-", color="#2c3e50", label="expected PRB (design)")
    ax.axhspan(PRB_LO, PRB_HI, alpha=0.3, color="green")
    ax.axhline(PRB_HARD_ABORT, color="red", ls="--")
    ax.set_xlabel("iperf UDP bitrate (Mbps)")
    ax.set_ylabel("expected PRB %")
    ax.set_title("Higher-stress PRB corridor design (NAD-LIMINAL-02)")
    ax.legend(fontsize=7)
    fig.savefig(fd / "higher_stress_prb_corridor_design.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 3 overshoot envelope
    fig, ax = plt.subplots(figsize=(8, 3))
    x = np.linspace(20, 45, 50)
    risk = 1 / (1 + np.exp(-(x - 32)))  # illustrative S-curve
    ax.fill_between(x, 0, risk, where=(x >= PRB_HARD_ABORT), alpha=0.3, color="red", label="overshoot zone")
    ax.axvspan(22, 30, alpha=0.2, color="green", label="safe ladder")
    ax.set_xlabel("iperf Mbps")
    ax.set_ylabel("overshoot P(hard_gate)")
    ax.set_title("Overshoot probability envelope")
    ax.legend(fontsize=7, loc="upper left")
    fig.savefig(fd / "overshoot_probability_envelope.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4 same-state blueprint
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.axis("off")
    steps = ["Warmup 120s", "σ(PRB)<2%", "URLLC", "eMBB", "mMTC", "drift<7%", "PRB<23.5%"]
    for i, s in enumerate(steps):
        ax.text(0.04 + i * 0.13, 0.5, s, ha="center", fontsize=8, bbox=dict(boxstyle="round", facecolor="#e8f6f3"))
    ax.set_title("Same-state synchronization blueprint")
    fig.savefig(fd / "same_state_synchronization_blueprint.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 5 execution flow
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    flow = [
        "Calibrate 22M→26M",
        "Target 28M/30M",
        "PRB gate",
        "Triplet×20",
        "Fallback 28M",
        "Enrich CSV",
    ]
    for i, s in enumerate(flow):
        ax.text(0.1, 0.85 - i * 0.14, f"{i+1}. {s}", fontsize=10)
    ax.set_title("NAD-LIMINAL-02 execution flow")
    fig.savefig(fd / "nad_liminal_02_execution_flow.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_operating_point_reconstruction",
        "phase_2_higher_stress_corridor_design",
        "phase_3_prb_stability_engineering",
        "phase_4_overshoot_risk_control",
        "phase_5_same_state_integrity_design",
        "phase_6_reviewer_safe_campaign_constraints",
        "phase_7_nad_liminal_02_execution_blueprint",
        "phase_8_regression_prevention_rules",
        "phase_9_final_design_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    sr = _load(SR05)
    lim = _load(LIM01)
    sr_stats = _regime_stats(sr)
    lim_by = defaultdict(list)
    for r in lim:
        lim_by[r.get("regime_mbps", "liminal")].append(r)
    lim_stats = _regime_stats([r for sub in lim_by.values() for r in sub])

    blueprint = {
        "campaign_id": "NAD-LIMINAL-02",
        "digest_required": ACTIVE_DIGEST,
        "iperf_ladder": IPERF_LADDER,
        "reps_per_regime": REPS_PER_REGIME,
        "expected_submits": len(IPERF_LADDER) * REPS_PER_REGIME * 3,
        "warmup_s_primary": WARMUP_S,
        "warmup_s_calibration": WARMUP_CALIBRATION_S,
        "prb_target_pct": [PRB_LO, PRB_HI],
        "prb_soft_abort_pct": PRB_SOFT_ABORT,
        "prb_hard_abort_pct": PRB_HARD_ABORT,
        "sigma_prb_max_pct": SIGMA_MAX,
        "score_target": [SCORE_LO, SCORE_HI],
        "triplet_order": ["URLLC", "eMBB", "mMTC"],
        "stop_hard_gate_frac": 0.30,
        "forbidden_bitrates": FORBIDDEN_BITRATES,
        "runtime_controls": "NAD-EXEC-04 module + LIMINAL-02 extensions (soft abort, ladder rollback)",
    }

    design_answers = {
        "Q1_safe_iperf": "22M–30M UDP ladder; primary 28M/30M; forbid ≥40M",
        "Q2_prb_18_24_without_crossing_24": "120s warmup + glide sampling + soft abort 23.5% + hard abort 24%",
        "Q3_avoid_mixed_path": "score_mode_guard + triplet discard on hard_prb_gate + stratified analysis only",
        "Q4_stabilize_prb": "extended warmup 120s; σ<2% over 90s window; 4-sample convergence pre-triplet",
        "Q5_reduce_overshoot": "bitrate ladder with rollback; no 40M; stop regime if hard_gate>30%",
        "Q6_same_state": "URLLC→eMBB→mMTC; 1.5s pause; PRB drift<7%; barrier after stabilization",
        "Q7_reviewer_safe": "no threshold/weight/gate changes; live score_mode only; negative LIMINAL-01 acknowledged",
    }

    (OUT / "phase_1_operating_point_reconstruction/OPERATING_POINT_RECONSTRUCTION.md").write_text(
        "# Phase 1 — Operating Point Reconstruction\n\n**Verdict:** OPERATING_POINT_RECONSTRUCTION_COMPLETE\n\n"
        "## SR-EXEC-05 vs NAD-LIMINAL-01\n\n"
        "| Source | iperf | PRB mean/max | score_mode | hard_gate% |\n|--------|-------|--------------|------------|------------|\n"
        f"| 15Mbps (SR-05) | 15M | 13.2 / 15.5 | 90 | 0% |\n"
        f"| NAD-LIMINAL-01 | 15M | 8.9 / 15.5 | 300 | 0% |\n"
        f"| 40Mbps (SR-05 sm) | 40M | 26.3 / 30.8 | 2 | 98% overall |\n"
        f"| 130Mbps (SR-05 sm) | 130M | 6.8 / 22.1 | 13 | 86% overall |\n\n"
        "**Gap:** 15M cannot reach PRB 18–24%. 40M overshoots hard gate. **28–30M ladder** is the design sweet spot.\n\n"
        f"```json\n{json.dumps(sr_stats, indent=2)[:2500]}\n```\n",
        encoding="utf-8",
    )

    (OUT / "phase_2_higher_stress_corridor_design/HIGHER_STRESS_CORRIDOR_DESIGN.md").write_text(
        "# Phase 2 — Higher-Stress Corridor Design\n\n**Verdict:** HIGHER_STRESS_CORRIDOR_DEFINED\n\n"
        "## iperf ladder (Q1)\n\n"
        "| Step | Bitrate | Role | Expected PRB |\n|------|---------|------|-------------|\n"
        "| 1 | **22M** | calibration | 16–18% |\n"
        "| 2 | **26M** | calibration | 18–20% |\n"
        "| 3 | **28M** | **primary** | 20–22% |\n"
        "| 4 | **30M** | primary upper | 21–23% |\n"
        "| 5 | **28M** | fallback stable | 19–22% |\n\n"
        "**25–35M range:** **28–30M sufficient** if controls active; **35M+ dangerous** (SR-05 40M → 98% hard gate).\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_prb_stability_engineering/PRB_STABILITY_ENGINEERING.md").write_text(
        "# Phase 3 — PRB Stability Engineering\n\n**Verdict:** PRB_STABILITY_ENGINEERING_DEFINED\n\n"
        f"- Primary warmup: **{WARMUP_S}s** (vs 90s LIMINAL-01)\n"
        f"- Calibration warmup: **{WARMUP_CALIBRATION_S}s**\n"
        f"- σ(PRB) < **{SIGMA_MAX}%** over stabilization window\n"
        "- Pre-triplet: 4 samples @ 5s; reject rep if σ>2% or PRB≥23.5%\n"
        "- Adaptive: extend warmup +30s if σ>2% once (max 1 extension)\n",
        encoding="utf-8",
    )

    (OUT / "phase_4_overshoot_risk_control/OVERSHOOT_RISK_CONTROL.md").write_text(
        "# Phase 4 — Overshoot Risk Control\n\n**Verdict:** OVERSHOOT_RISK_CONTROL_DEFINED\n\n"
        f"- **Soft abort:** PRB ≥ **{PRB_SOFT_ABORT}%** → skip rep\n"
        f"- **Hard abort:** PRB ≥ **{PRB_HARD_ABORT}%** → stop regime\n"
        "- **Rollback:** 3 consecutive soft aborts → drop one ladder step\n"
        "- **Forbidden:** 40M+ in automated path\n"
        "- **Stop:** hard_gate rate > 30% per regime\n",
        encoding="utf-8",
    )

    (OUT / "phase_5_same_state_integrity_design/SAME_STATE_INTEGRITY_DESIGN.md").write_text(
        "# Phase 5 — Same-State Integrity Design\n\n**Verdict:** SAME_STATE_INTEGRITY_DESIGN_DEFINED\n\n"
        "- Order: URLLC → eMBB → mMTC (unchanged)\n"
        "- `network_state_id`: `{regime}-rep{idx:03d}`\n"
        "- Discard triplet if: hard_gate, non-score_mode, PRB drift >7%\n"
        "- Stabilization barrier between reps: full σ check\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_reviewer_safe_campaign_constraints/REVIEWER_SAFE_CAMPAIGN_CONSTRAINTS.md").write_text(
        "# Phase 6 — Reviewer-Safe Campaign Constraints\n\n**Verdict:** REVIEWER_SAFE_CAMPAIGN_CONSTRAINTS_DEFINED\n\n"
        "- No accept_min/reneg_min/PRB gate/formula/weight changes\n"
        "- No synthetic admission labels\n"
        "- Claim only **score_mode-only stratified** divergence if observed\n"
        "- LIMINAL-01 negative result remains valid baseline\n",
        encoding="utf-8",
    )

    (OUT / "phase_7_nad_liminal_02_execution_blueprint/NAD_LIMINAL_02_EXECUTION_BLUEPRINT.md").write_text(
        "# Phase 7 — NAD-LIMINAL-02 Execution Blueprint\n\n**Verdict:** NAD_LIMINAL_02_BLUEPRINT_READY\n\n"
        f"```json\n{json.dumps(blueprint, indent=2)}\n```\n\n"
        "## Sequence\n"
        "1. Freeze digest + health check\n"
        "2. For each ladder step: iperf → warmup → reps×20 triplets\n"
        "3. Enrich CSV + SHA256\n"
        "4. Stratified validation (score_mode triplets only)\n",
        encoding="utf-8",
    )

    (OUT / "phase_8_regression_prevention_rules/REGRESSION_PREVENTION_RULES.md").write_text(
        "# Phase 8 — Regression Prevention Rules\n\n**Verdict:** REGRESSION_PREVENTION_RULES_FROZEN\n\n"
        "| Rule | Requirement |\n|------|-------------|\n"
        f"| R-DIGEST | `{ACTIVE_DIGEST}` |\n"
        "| R-INV-PRB | No gate weakening |\n"
        "| R-INV-MONO | No formula change |\n"
        "| R-SSOT | SR-EXEC-09 baseline unchanged |\n"
        "| R-STRAT | ≥80% analysis on score_mode-only triplets |\n",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_design_freeze/FINAL_DESIGN_FREEZE.md").write_text(
        "# Phase 9 — Final Design Freeze\n\n# **HIGHER_STRESS_LIMINAL_CAMPAIGN_DESIGN_FROZEN**\n\n"
        "NAD-LIMINAL-02 closes the operating-point gap via **28–30M iperf ladder** with **PRB 18–24%** targeting "
        "and **overshoot controls** (soft 23.5%, hard 24%).\n\n"
        f"Digest: `{ACTIVE_DIGEST}`\n",
        encoding="utf-8",
    )

    _figures(sr_stats, lim_stats)

    summary = {
        "phase": "NAD-EXEC-07",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": "HIGHER_STRESS_LIMINAL_CAMPAIGN_DESIGN_FROZEN",
        "design_only": True,
        "active_digest": ACTIVE_DIGEST,
        "nad_exec_06_reference": str(NAD06),
        "design_answers": design_answers,
        "nad_liminal_02_blueprint": blueprint,
        "operating_point_gap": {
            "liminal01_prb_max": 15.45,
            "corridor_lo": PRB_LO,
            "required_delta_prb_pct": PRB_LO - 15.45,
        },
        "next_prompt": "PROMPT_TRISLA_NAD_EXEC_08_HIGHER_STRESS_RUNTIME_CONTROL_IMPLEMENTATION_V1",
        "approval_required": "NAD_EXEC_07_APPROVED",
        "hard_stop": True,
    }
    (OUT / "analysis" / "higher_stress_liminal_campaign_design_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    subprocess.run(
        ["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"],
        stdout=(OUT / "freeze" / "runtime_after.txt").open("w"),
        check=False,
    )
    subprocess.run(
        ["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"],
        stdout=(OUT / "freeze" / "runtime_after.yaml").open("w"),
        check=False,
    )
    manifest = sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file())
    (OUT / "analysis" / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
