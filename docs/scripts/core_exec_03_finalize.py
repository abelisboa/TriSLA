#!/usr/bin/env python3
"""CORE-EXEC-03: Core causality gap analysis (gap-analysis only)."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

OUT = Path(os.environ["OUT"])
ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"
CORE01 = ROOT / "evidencias_trisla_core_exec_01_core_attribution_audit_20260518T002045Z"
CORE02 = ROOT / "evidencias_trisla_core_exec_02_core_runtime_observability_mapping_20260518T002537Z"
NAD15 = ROOT / "evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z"

FINAL_VERDICT = "CORE_CAUSALITY_BLOCKERS_IDENTIFIED"
COMPANION_VERDICT = "CORE_CAUSALITY_PATHS_READY"

# Gap inventory: id, class, severity, description
GAPS: List[Dict[str, str]] = [
    {
        "id": "GAP-01",
        "class": "WEIGHTING_GAP",
        "severity": "primary",
        "description": "No core_goodness / core_weight in score_mode numerator; Core cannot move decision_score directly",
    },
    {
        "id": "GAP-02",
        "class": "PROPAGATION_GAP",
        "severity": "primary",
        "description": "Core reaches admission only via diluted feasibility/headroom (CPU 30% of pressure v1)",
    },
    {
        "id": "GAP-03",
        "class": "CONTENTION_GAP",
        "severity": "primary",
        "description": "No operational AMF/SMF/UPF/PFCP contention mechanism; NAD LIMINAL-03 guards blocked all reps",
    },
    {
        "id": "GAP-04",
        "class": "RUNTIME_GAP",
        "severity": "primary",
        "description": "PRB hard-gate and ran_prb_goodness dominate path before Core indirect terms apply",
    },
    {
        "id": "GAP-05",
        "class": "OBSERVABILITY_GAP",
        "severity": "secondary",
        "description": "Default PromQL uses aggregate process_* not NF-scoped AMF/SMF/UPF series",
    },
    {
        "id": "GAP-06",
        "class": "MATH_GAP",
        "severity": "secondary",
        "description": "pressure v1 excludes memory; feasibility formula dampens Core via (risk+pressure)/2",
    },
    {
        "id": "GAP-07",
        "class": "EXPERIMENTAL_GAP",
        "severity": "primary",
        "description": "NAD campaigns: 0 admission drift; pressure mean ~0.08 max ~0.11 — Core envelope never stressed",
    },
    {
        "id": "GAP-08",
        "class": "ORCHESTRATION_GAP",
        "severity": "secondary",
        "description": "No lifecycle/session arbitration coupling Core load to admission decisions",
    },
    {
        "id": "GAP-09",
        "class": "LIFECYCLE_GAP",
        "severity": "secondary",
        "description": "PDU/session pressure not wired to telemetry_snapshot or DE",
    },
    {
        "id": "GAP-10",
        "class": "FROZEN_LIMITATION",
        "severity": "invariant",
        "description": "INV-PRB: Core-dominant admission forbidden; PRB absorption is by design",
    },
]

NAD_ENVELOPE = {
    "liminal02_n_rows": 210,
    "admission_drift": 0,
    "pressure_mean_approx": 0.08,
    "pressure_max_approx": 0.11,
    "feasibility_min_approx": 0.67,
    "score_min_approx": 0.698,
    "prb_max_pct": 30.9,
}


def _de_image() -> str:
    try:
        return subprocess.check_output(
            [
                "kubectl",
                "-n",
                "trisla",
                "get",
                "deploy",
                "trisla-decision-engine",
                "-o",
                "jsonpath={.spec.template.spec.containers[0].image}",
            ],
            text=True,
        ).strip()
    except Exception:
        return ""


def _mandatory_answers() -> Dict[str, Any]:
    return {
        "Q1_primary_blocker": "CONTENTION_GAP + WEIGHTING_GAP + PRB_RUNTIME_ABSORPTION",
        "Q1_blocker_detail": "Core lacks direct score term and operational stress envelope; PRB path absorbs marginal Core effects",
        "Q2_absence_core_goodness": True,
        "Q2_absence_weighting": True,
        "Q2_absence_contention": True,
        "Q2_absence_runtime_stress": True,
        "Q2_absence_propagation_direct": True,
        "Q3_alters_score_directly": False,
        "Q3_alters_band": False,
        "Q3_alters_admission": False,
        "Q3_alters_path": "indirect_only_when_pressure_active",
        "Q4_feasibility_headroom_sufficient_for_causality": False,
        "Q4_rationale": "CPU contributes ≤30% of pressure; observed pressure too low to move bands",
        "Q5_prb_absorbs_core_effect": True,
        "Q5_rationale": "Hard PRB gates + highest w_prb in score_mode; NAD scores stayed ≥0.70",
        "Q6_reviewer_safe_core_divergence_without_inv_prb": False,
        "Q6_safe_alternative": "Future: bounded core_goodness subordinate to PRB + contention campaign evidence",
        "Q7_upf_contention_runtime": False,
        "Q7_amf_saturation_runtime": False,
        "Q7_smf_bottleneck_runtime": False,
        "Q7_pfcp_n4_congestion": False,
        "Q8_core_state": "observable_and_contributive_not_causal_not_dominant",
        "Q9_minimal_core_informed": "NF-scoped telemetry + core_goodness term (capped) + calibration",
        "Q9_minimal_core_causal": "Q9_informed + operational contention (NCM) + evidence campaign",
        "Q10_reviewer_unsafe": [
            "weakening PRB gates",
            "fake Core pressure / synthetic telemetry",
            "threshold manipulation post-hoc",
            "claiming balanced multidomain without evidence",
            "unbounded core dominance",
        ],
        "Q10_regressive": [
            "removing PRB hard-gate",
            "inflating core weight above RAN without governance",
            "treating XAI metadata as causal proof",
        ],
        "Q10_artificial": [
            "synthetic core_goodness without runtime telemetry",
            "admission divergence from empty datasets",
        ],
    }


def _figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    gaps = [g["id"] for g in GAPS[:6]]
    sev = [1.0 if g["severity"] == "primary" else 0.6 for g in GAPS[:6]]
    colors = ["#e74c3c" if s == 1.0 else "#f39c12" for s in sev]
    ax.barh(gaps, sev, color=colors)
    ax.set_xlim(0, 1.2)
    ax.set_title("Core causality blocker map (primary gaps)")
    fig.savefig(fd / "core_causality_blocker_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    levels = ["PRB hard-gate", "ran_prb_goodness", "risk_inverse", "feas/headroom\n(Core indirect)", "core_goodness"]
    vals = [1.0, 0.85, 0.7, 0.25, 0]
    ax.barh(levels, vals, color=["#c0392b", "#e74c3c", "#e67e22", "#f1c40f", "#bdc3c7"])
    ax.set_xlim(0, 1.1)
    ax.set_title("PRB absorption hierarchy")
    fig.savefig(fd / "prb_absorption_hierarchy.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    stages = ["Core CPU", "pressure×0.3", "feasibility", "headroom term", "Δscore"]
    damping = [1.0, 0.3, 0.5, 0.16, 0.05]
    ax.plot(stages, damping, "o-", lw=2, color="#8e44ad")
    ax.set_ylim(0, 1.1)
    ax.set_title("Core propagation damping graph (illustrative)")
    fig.savefig(fd / "core_propagation_damping_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    domains = ["RAN", "Transport", "Core", "Balanced"]
    balance = [0.9, 0.55, 0.2, 0]
    ax.bar(domains, balance, color=["#27ae60", "#3498db", "#9b59b6", "#95a5a6"])
    ax.set_ylim(0, 1)
    ax.set_title("Multidomain imbalance map (influence, not claim)")
    fig.savefig(fd / "multidomain_imbalance_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    roadmap = [
        "CORE causality roadmap (future)",
        "1. NF-scoped observability (EXEC-04)",
        "2. core_goodness design (capped)",
        "3. NCM contention campaign",
        "4. Evidence: band movement w/o PRB violation",
        "5. Reviewer-safe causal claim",
    ]
    for i, ln in enumerate(roadmap):
        ax.text(0.05, 0.9 - i * 0.16, ln, fontsize=10, family="monospace")
    ax.set_title("Core future causality roadmap")
    fig.savefig(fd / "core_future_causality_roadmap.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_core_causality_gap_inventory",
        "phase_2_runtime_absorption_analysis",
        "phase_3_core_contention_feasibility_analysis",
        "phase_4_score_propagation_gap_analysis",
        "phase_5_multidomain_balance_gap_analysis",
        "phase_6_reviewer_safe_boundary_analysis",
        "phase_7_future_core_causality_paths",
        "phase_8_forbidden_and_regressive_paths",
        "phase_9_final_core_gap_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    answers = _mandatory_answers()
    de_img = _de_image()

    gap_table = "\n".join(
        f"| {g['id']} | {g['class']} | {g['severity']} | {g['description']} |" for g in GAPS
    )
    (OUT / "phase_1_core_causality_gap_inventory/CORE_CAUSALITY_GAP_INVENTORY.md").write_text(
        f"# Phase 1 — Core Causality Gap Inventory\n\n**Verdict:** CORE_CAUSALITY_GAP_INVENTORY_COMPLETE\n\n"
        f"| ID | Class | Severity | Description |\n|----|-------|----------|-------------|\n{gap_table}\n",
        encoding="utf-8",
    )

    (OUT / "phase_2_runtime_absorption_analysis/RUNTIME_ABSORPTION_ANALYSIS.md").write_text(
        f"""# Phase 2 — Runtime Absorption Analysis

**Verdict:** PRB_ABSORPTION_ANALYSIS_COMPLETE

## Mechanism

1. **PRB hard-gate** runs before score_mode (`engine.py`) — can REJECT/RENEGOTIATE without Core input.
2. **ran_prb_goodness** weight 0.12–0.22 per slice vs Core indirect via w_press 0.14–0.18.
3. **NAD envelope:** scores ≥{NAD_ENVELOPE['score_min_approx']}; PRB max {NAD_ENVELOPE['prb_max_pct']}% — decisions driven by RAN/transport terms.
4. **Feasibility damping:** `feas = 1 - (risk+pressure)/2` — Core CPU (≤30% of pressure) cannot alone cross accept/reneg thresholds.
5. **Denominator:** active terms only — Core adds no weight when feasibility/pressure missing (`INPUT_DEGRADED`).

**Conclusion:** PRB dominance **absorbs** marginal Core elasticity; not a math bug — **FROZEN_LIMITATION** (INV-PRB).
""",
        encoding="utf-8",
    )

    (OUT / "phase_3_core_contention_feasibility_analysis/CORE_CONTENTION_FEASIBILITY_ANALYSIS.md").write_text(
        f"""# Phase 3 — Core Contention Feasibility Analysis

**Verdict:** CORE_CONTENTION_FEASIBILITY_ANALYZED

## Runtime capability (frozen digest)

| Mechanism | Attainable today? |
|-----------|-------------------|
| UPF queue / GTP stress observable | **No** — not in default snapshot |
| AMF registration storm | **No** — no campaign hook |
| SMF session bottleneck | **No** |
| PFCP/N4 congestion metric | **No** |
| PDU/session pressure in DE | **No** |
| CPU/memory from process_* aggregate | **Partial** — observable but low dynamic range |

NAD-EXEC-15: **NEW_OPERATIONAL_CONTENTION_MECHANISM_REQUIRED** — same class of blocker for Core causality.

**Conclusion:** Runtime **cannot** produce real Core contention without new mechanism (NCM track) — **CONTENTION_GAP** primary.
""",
        encoding="utf-8",
    )

    (OUT / "phase_4_score_propagation_gap_analysis/SCORE_PROPAGATION_GAP_ANALYSIS.md").write_text(
        """# Phase 4 — Score Propagation Gap Analysis

**Verdict:** SCORE_PROPAGATION_GAP_ANALYZED

## Breakpoints

| Stage | Core influence |
|-------|----------------|
| contributing_factors | **Absent** — no core_* factor |
| Numerator | **No direct term** |
| Denominator | Core adds **zero** weight |
| Indirect | feasibility_goodness + resource_headroom_goodness only |
| XAI | core_cpu_input present — **non-causal** |
| slice_md merge | core_risk — rarely upgrades (NAD: 0 drift) |

**PROPAGATION_GAP:** influence dies in pressure dilution before band thresholds.
""",
        encoding="utf-8",
    )

    (OUT / "phase_5_multidomain_balance_gap_analysis/MULTIDOMAIN_BALANCE_GAP_ANALYSIS.md").write_text(
        """# Phase 5 — Multidomain Balance Gap Analysis

**Verdict:** MULTIDOMAIN_BALANCE_GAP_ANALYZED

TriSLA is **not** balanced multidomain at admission time:

- **RAN:** hard-gates + highest explicit score weight
- **Transport:** explicit `transport_rtt_goodness` (frozen 0.02–0.05)
- **Core:** indirect only; no arbitration across domains

**Forbidden claim:** balanced multidomain runtime admission (CORE-EXEC-01/02, NAD-EXEC-15).
""",
        encoding="utf-8",
    )

    (OUT / "phase_6_reviewer_safe_boundary_analysis/REVIEWER_SAFE_BOUNDARY_ANALYSIS.md").write_text(
        """# Phase 6 — Reviewer-Safe Boundary Analysis

**Verdict:** REVIEWER_SAFE_CORE_BOUNDARY_FROZEN

| Category | Allowed |
|----------|---------|
| **reviewer-safe** | Core-observable; Core-contributive (indirect); RAN-dominant; transport-informed |
| **unsupported** | Core-causal admission; Core-driven divergence; balanced multidomain |
| **forbidden** | Fake Core pressure; weakening PRB; XAI-as-proof of causality |
| **future-work-only** | core_goodness; NF-scoped metrics; NCM contention campaigns |
""",
        encoding="utf-8",
    )

    (OUT / "phase_7_future_core_causality_paths/FUTURE_CORE_CAUSALITY_PATHS.md").write_text(
        """# Phase 7 — Future Core Causality Paths

**Verdict:** FUTURE_CORE_CAUSALITY_PATHS_DEFINED

1. **Observability** — AMF/SMF/UPF scoped PromQL (CORE-EXEC-04)
2. **Weighting** — `core_goodness` with cap subordinate to PRB
3. **Contention** — NCM operational campaigns (UPF/AMF/SMF)
4. **Evidence** — measurable band movement attributable to Core with PRB held
5. **Arbitration** — optional lifecycle coupling (design only)

→ Enables **CORE_CAUSALITY_PATHS_READY** for EXEC-04+ without breaking INV-PRB.
""",
        encoding="utf-8",
    )

    (OUT / "phase_8_forbidden_and_regressive_paths/FORBIDDEN_AND_REGRESSIVE_PATHS.md").write_text(
        """# Phase 8 — Forbidden and Regressive Paths

**Verdict:** FORBIDDEN_CORE_PATHS_FROZEN

- Weakening PRB / HARD_PRB thresholds
- Synthetic Core pressure or metric injection
- Post-hoc threshold/gate changes
- Artificial admission divergence
- Unbounded core dominance in numerator
- Claiming multidomain balance without campaign proof
- Reinterpreting observability as causality
""",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_core_gap_freeze/FINAL_CORE_GAP_FREEZE.md").write_text(
        f"# Phase 9 — Final Core Gap Freeze\n\n# **{FINAL_VERDICT}**\n\n"
        f"Companion: **{COMPANION_VERDICT}** (design paths frozen; not runtime-attained)\n\n"
        f"References: CORE-EXEC-01, CORE-EXEC-02, NAD-EXEC-15\n\n"
        f"Primary blocker (Q1): **{answers['Q1_primary_blocker']}**\n",
        encoding="utf-8",
    )

    _figures()

    summary = {
        "phase": "CORE-EXEC-03",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": FINAL_VERDICT,
        "companion_verdict": COMPANION_VERDICT,
        "gap_analysis_only": True,
        "active_digest": ACTIVE_DIGEST,
        "decision_engine_image": de_img,
        "references": {
            "core_exec_01": str(CORE01),
            "core_exec_02": str(CORE02),
            "nad_exec_15": str(NAD15),
        },
        "gaps": GAPS,
        "nad_envelope": NAD_ENVELOPE,
        "mandatory_answers": answers,
        "phase_verdicts": {
            "phase1": "CORE_CAUSALITY_GAP_INVENTORY_COMPLETE",
            "phase2": "PRB_ABSORPTION_ANALYSIS_COMPLETE",
            "phase3": "CORE_CONTENTION_FEASIBILITY_ANALYZED",
            "phase4": "SCORE_PROPAGATION_GAP_ANALYZED",
            "phase5": "MULTIDOMAIN_BALANCE_GAP_ANALYZED",
            "phase6": "REVIEWER_SAFE_CORE_BOUNDARY_FROZEN",
            "phase7": "FUTURE_CORE_CAUSALITY_PATHS_DEFINED",
            "phase8": "FORBIDDEN_CORE_PATHS_FROZEN",
            "phase9": FINAL_VERDICT,
        },
        "next_prompt": "PROMPT_TRISLA_CORE_EXEC_04_CORE_CAUSALITY_RUNTIME_REQUIREMENTS_V1",
        "approval_required": "CORE_EXEC_03_APPROVED",
        "hard_stop": True,
    }
    (OUT / "analysis/core_causality_gap_analysis_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (OUT / "analysis/gap_inventory.json").write_text(json.dumps(GAPS, indent=2), encoding="utf-8")

    subprocess.run(
        ["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"],
        stdout=(OUT / "freeze/runtime_after.txt").open("w"),
        check=False,
    )
    subprocess.run(
        ["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"],
        stdout=(OUT / "freeze/runtime_after.yaml").open("w"),
        check=False,
    )
    manifest = sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file())
    (OUT / "analysis/MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
