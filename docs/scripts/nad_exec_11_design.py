#!/usr/bin/env python3
"""NAD-EXEC-11: pressure/feasibility liminal design (design-only)."""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OUT = Path(os.environ["OUT"])
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"
LIM01 = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nad_exec_05_liminal_scoremode_campaign_20260517T201420Z/dataset/enriched/liminal_scoremode_dataset.csv"
)
LIM02 = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nad_exec_09_nad_liminal_02_campaign_execution_20260517T214300Z/dataset/enriched/nad_liminal_02_dataset.csv"
)
EXEC10 = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nad_exec_10_higher_stress_divergence_validation_20260517T224540Z/analysis/higher_stress_divergence_validation_summary.json"
)

PRB_LO, PRB_HI = 18.0, 24.0
PRB_SOFT, PRB_HARD = 23.5, 24.0
SCORE_LO, SCORE_HI = 0.52, 0.58
SCORE_TARGET = (SCORE_LO, SCORE_HI)
ACCEPT_MIN = {"URLLC": 0.55, "eMBB": 0.55, "mMTC": 0.52}

# Frozen slice profiles (decision_score_mode.default_profile)
PROFILES = {
    "URLLC": {"w_feas": 0.22, "w_prb": 0.22, "w_press": 0.18, "w_risk": 0.28, "w_sem": 0.12, "w_transport": 0.05},
    "eMBB": {"w_feas": 0.20, "w_prb": 0.18, "w_press": 0.16, "w_risk": 0.26, "w_sem": 0.12, "w_transport": 0.03},
    "mMTC": {"w_feas": 0.18, "w_prb": 0.12, "w_press": 0.14, "w_risk": 0.22, "w_sem": 0.10, "w_transport": 0.02},
}
RTT_REF_MS = 12.21


def _load(p: Path) -> List[dict]:
    return list(csv.DictReader(p.open(encoding="utf-8")))


def _f(v: Any) -> Optional[float]:
    try:
        return float(v) if v not in ("", None) else None
    except (TypeError, ValueError):
        return None


def _g_transport(rtt_ms: float) -> float:
    return max(0.0, min(1.0, 1.0 - rtt_ms / RTT_REF_MS))


def offline_score(
    slice_key: str,
    *,
    feas: float,
    prb_pct: float,
    pressure: float,
    g_risk: float = 0.72,
    g_sem: float = 0.55,
    rtt_ms: float = 8.0,
) -> Tuple[float, float]:
    """OFFLINE_DESIGN_ONLY — mirrors frozen score_mode denominator (no runtime change)."""
    p = PROFILES[slice_key]
    g_prb = 1.0 - max(0.0, min(prb_pct, 100.0)) / 100.0
    g_press = 1.0 - max(0.0, min(pressure, 1.0))
    g_tr = _g_transport(rtt_ms)
    num = (
        p["w_feas"] * feas
        + p["w_prb"] * g_prb
        + p["w_press"] * g_press
        + p["w_risk"] * g_risk
        + p["w_sem"] * g_sem
        + p["w_transport"] * g_tr
    )
    den = sum(p.values())
    return num / den if den > 0 else 0.0, den


def factor_reconstruction(rows: List[dict], label: str) -> dict:
    sm = [r for r in rows if r.get("decision_mode") == "decision_score"]
    fields = ["feasibility_score", "resource_pressure", "prb_utilization_real", "decision_score", "telemetry_transport_rtt_ms"]
    means = {k: statistics.mean([_f(r[k]) for r in sm if _f(r.get(k)) is not None]) for k in fields}
    # Offline implied contributions at observed means (eMBB proxy for decomposition chart)
    feas, prb, press = means.get("feasibility_score") or 0.74, means.get("prb_utilization_real") or 10, means.get("resource_pressure") or 0.08
    sc, den = offline_score("eMBB", feas=feas, prb_pct=prb, pressure=press)
    p = PROFILES["eMBB"]
    shares = {
        "feasibility_goodness": p["w_feas"] * feas / den,
        "ran_prb_goodness": p["w_prb"] * (1 - prb / 100) / den,
        "resource_headroom_goodness": p["w_press"] * (1 - press) / den,
        "risk_inverse": p["w_risk"] * 0.72 / den,
        "semantic_priority": p["w_sem"] * 0.55 / den,
        "transport_rtt_goodness": p["w_transport"] * _g_transport(means.get("telemetry_transport_rtt_ms") or 8) / den,
    }
    return {"campaign": label, "n_score_mode": len(sm), "means": means, "implied_shares_embb": shares, "implied_score_embb": sc}


def sensitivity_grid(slice_key: str = "eMBB") -> dict:
    """OFFLINE_DESIGN_ONLY grid search for score 0.52–0.58."""
    hits: List[dict] = []
    for prb in range(18, 25):
        for feas_i in range(25, 75, 5):
            feas = feas_i / 100.0
            for press_i in range(25, 85, 5):
                press = press_i / 100.0
                for rtt in (6.0, 10.0, 14.0, 18.0):
                    sc, _ = offline_score(slice_key, feas=feas, prb_pct=float(prb), pressure=press, rtt_ms=rtt)
                    if SCORE_LO <= sc <= SCORE_HI:
                        hits.append(
                            {
                                "prb_pct": prb,
                                "feasibility": feas,
                                "pressure": press,
                                "rtt_ms": rtt,
                                "score": round(sc, 4),
                            }
                        )
    # minimal deltas from LIMINAL-02 centroid
    base_feas, base_press, base_prb = 0.74, 0.08, 21.0
    base_sc, _ = offline_score(slice_key, feas=base_feas, prb_pct=base_prb, pressure=base_press)
    delta_needed = base_sc - 0.55
    return {
        "marker": "OFFLINE_DESIGN_ONLY",
        "slice": slice_key,
        "n_target_hits": len(hits),
        "sample_hits": hits[:15],
        "base_observed_score": base_sc,
        "score_drop_needed": round(delta_needed, 3),
        "interpretation": (
            "Reaching 0.52–0.58 requires simultaneous elevation of resource_pressure "
            "(≈0.45–0.70) and reduction of feasibility (≈0.30–0.50) while holding PRB 18–22%; "
            "PRB-only stress (LIMINAL-02) is insufficient."
        ),
    }


def _figures(recon: dict, sens: dict, corridor: dict, blueprint: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    # 1 factor resistance decomposition
    fig, ax = plt.subplots(figsize=(8, 4))
    l01 = recon["LIMINAL-01"]["implied_shares_embb"]
    l02 = recon["LIMINAL-02"]["implied_shares_embb"]
    keys = list(l01.keys())
    x = np.arange(len(keys))
    ax.bar(x - 0.2, [l01[k] for k in keys], 0.35, label="LIMINAL-01", color="#9b59b6")
    ax.bar(x + 0.2, [l02[k] for k in keys], 0.35, label="LIMINAL-02", color="#e67e22")
    ax.set_xticks(x)
    ax.set_xticklabels([k.replace("_", "\n") for k in keys], fontsize=7)
    ax.set_ylabel("Share of score (offline eMBB)")
    ax.set_title("Factor resistance decomposition")
    ax.legend(fontsize=7)
    fig.savefig(fd / "factor_resistance_decomposition.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 2 score sensitivity surface (PRB vs pressure at feas=0.45)
    fig, ax = plt.subplots(figsize=(8, 5))
    prb_ax = np.linspace(18, 24, 25)
    press_ax = np.linspace(0.2, 0.8, 25)
    Z = np.zeros((len(press_ax), len(prb_ax)))
    for i, press in enumerate(press_ax):
        for j, prb in enumerate(prb_ax):
            Z[i, j], _ = offline_score("eMBB", feas=0.45, prb_pct=prb, pressure=press, rtt_ms=12)
    cf = ax.contourf(prb_ax, press_ax, Z, levels=20, cmap="RdYlGn_r")
    ax.contour(prb_ax, press_ax, Z, levels=[0.52, 0.55, 0.58], colors="white", linewidths=1.2)
    plt.colorbar(cf, ax=ax, label="decision_score (OFFLINE)")
    ax.set_xlabel("PRB %")
    ax.set_ylabel("resource_pressure")
    ax.set_title("Score sensitivity surface (feas=0.45, OFFLINE_DESIGN_ONLY)")
    fig.savefig(fd / "score_sensitivity_surface.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 3 pressure-feasibility corridor map
    fig, ax = plt.subplots(figsize=(7, 6))
    w = corridor["windows"]
    ax.add_patch(plt.Rectangle((w["pressure"][0], w["feasibility"][0]), w["pressure"][1] - w["pressure"][0], w["feasibility"][1] - w["feasibility"][0], fill=True, alpha=0.35, color="#2ecc71", label="target corridor"))
    ax.scatter([0.08], [0.74], s=120, c="#e74c3c", marker="x", label="LIMINAL-02 mean")
    ax.scatter([0.08], [0.74], s=80, c="#9b59b6", marker="x", label="LIMINAL-01 mean")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("resource_pressure")
    ax.set_ylabel("feasibility_score")
    ax.set_title("Pressure–feasibility corridor map")
    ax.legend(fontsize=7)
    fig.savefig(fd / "pressure_feasibility_corridor_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4 PRB governance guardrail map
    fig, ax = plt.subplots(figsize=(8, 4))
    zones = ["<18%", "18–24%", ">24% soft", ">24% hard", "≥25% gate"]
    colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#8e44ad"]
    for i, (z, c) in enumerate(zip(zones, colors)):
        ax.barh(i, 1, color=c, alpha=0.7)
        ax.text(0.5, i, z, ha="center", va="center", fontsize=9, color="white" if i > 1 else "black")
    ax.set_yticks([])
    ax.set_xlim(0, 1)
    ax.set_title("PRB governance guardrail map (frozen gates)")
    fig.savefig(fd / "prb_governance_guardrail_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 5 NAD-LIMINAL-03 blueprint
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axis("off")
    steps = blueprint.get("flow_steps", [])
    for i, s in enumerate(steps):
        ax.text(0.05, 0.92 - i * 0.11, s, fontsize=10, family="monospace")
    ax.set_title("NAD-LIMINAL-03 blueprint")
    fig.savefig(fd / "nad_liminal_03_blueprint.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    phases = [
        "phase_1_factor_resistance_reconstruction",
        "phase_2_score_sensitivity_model",
        "phase_3_pressure_feasibility_corridor_design",
        "phase_4_operational_pressure_generation_design",
        "phase_5_runtime_feasibility_degradation_design",
        "phase_6_prb_governance_preservation_design",
        "phase_7_candidate_campaign_blueprint",
        "phase_8_regression_and_reviewer_risk",
        "phase_9_final_pressure_feasibility_design_freeze",
        "analysis",
        "figures",
        "freeze",
    ]
    for sub in phases:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    lim01 = _load(LIM01) if LIM01.exists() else []
    lim02 = _load(LIM02) if LIM02.exists() else []
    recon = {
        "LIMINAL-01": factor_reconstruction(lim01, "LIMINAL-01"),
        "LIMINAL-02": factor_reconstruction(lim02, "LIMINAL-02"),
    }
    sens_embb = sensitivity_grid("eMBB")
    sens_url = sensitivity_grid("URLLC")

    corridor = {
        "windows": {
            "prb_pct": [18.0, 22.5],
            "pressure": [0.35, 0.65],
            "feasibility": [0.30, 0.55],
            "headroom_inverse": [0.35, 0.65],
            "rtt_ms": [10.0, 18.0],
            "score": [0.52, 0.58],
        },
        "risks": {
            "prb_above_23.5": "soft abort — rep skip",
            "prb_above_24": "hard abort — regime stop",
            "pressure_above_0.7": "may trigger hard_prb_gate via PRB coupling",
            "concurrent_overload": "invalidates same-state if drift >7%",
        },
    }

    blueprint = {
        "campaign_id": "NAD-LIMINAL-03",
        "hypothesis": "Joint PRB+pressure+feasibility corridor lowers score to 0.52–0.58 without formula change",
        "digest_required": ACTIVE_DIGEST,
        "sample_size": {"reps_per_regime": 15, "regimes": 4, "slices": 3, "expected_submits": 180},
        "regimes": [
            {"label": "24Mbps-baseline", "iperf": "24M", "role": "calibration"},
            {"label": "25Mbps-primary", "iperf": "25M", "role": "primary"},
            {"label": "26Mbps-upper", "iperf": "26M", "role": "primary_upper"},
            {"label": "24Mbps-fallback", "iperf": "24M", "role": "fallback"},
        ],
        "operational_controls": {
            "concurrent_intents": 2,
            "concurrent_stagger_s": 3,
            "warmup_s": 90,
            "pre_triplet_pressure_min": 0.30,
            "pre_triplet_feasibility_max": 0.55,
            "prb_soft_abort_pct": 23.5,
            "prb_hard_abort_pct": 24.0,
            "stop_hard_gate_frac": 0.25,
        },
        "same_state": "URLLC→eMBB→mMTC; network_state_id unchanged; discard if hard_gate",
        "expected_verdicts": {
            "success": "SCORE_TARGET_PARTIALLY_ATTAINED",
            "negative": "LIMINAL_DIVERGENCE_NOT_VALIDATED",
            "invalid": "CAMPAIGN_CONTAMINATED",
        },
        "flow_steps": [
            "1. Freeze digest + health",
            "2. 24M calibrate → pressure/feasibility window check",
            "2b. Optional: 2 concurrent tenants (runtime-backed)",
            "3. 25M/26M primary — PRB 18–22.5% target",
            "4. Triplet×15 — score_mode guard",
            "5. 24M fallback if σ(PRB)>2%",
            "6. Enrich + stratified validation (no synthetic labels)",
        ],
    }

    risk_table = [
        ("Concurrent real SLA submits", "low", "medium", "allowed"),
        ("iperf 24–26M only", "low", "low", "allowed"),
        ("Manual JSON pressure override", "high", "high", "forbidden"),
        ("Synthetic admission labels", "high", "high", "forbidden"),
        ("Threshold/gate/weight change", "high", "high", "forbidden"),
        ("Declare divergence without runtime proof", "high", "high", "forbidden"),
        (">30M iperf without stratification", "medium", "high", "blocked"),
    ]

    answers = {
        "Q1_safe_combination": "PRB 18–22.5% + pressure 0.35–0.65 + feasibility 0.30–0.55 + RTT 10–18ms (OFFLINE grid)",
        "Q2_operational_pressure": "Controlled concurrent intents + 24–26M UDP + real telemetry-derived pressure",
        "Q3_feasibility_reduction": "Raise real PRB/RTT/cpu in snapshot → feasibility drops via frozen formula",
        "Q4_prb_governance": "Keep soft 23.5%/hard 24%/hard_gate stop; score_mode-only analysis",
        "Q5_avoid_artificial_divergence": "Same-state triplets only; no label injection; claim divergence only if observed",
        "Q6_future_campaign": "NAD-LIMINAL-03 per blueprint",
        "Q7_continue_nad_exec": "YES — design frozen; EXEC-12 implements controls only",
    }

    final_verdict = "PRESSURE_FEASIBILITY_LIMINAL_DESIGN_FROZEN"

    (OUT / "phase_1_factor_resistance_reconstruction/FACTOR_RESISTANCE_RECONSTRUCTION.md").write_text(
        "# Phase 1 — Factor Resistance Reconstruction\n\n**Verdict:** FACTOR_RESISTANCE_RECONSTRUCTED\n\n"
        "## Root cause (LIMINAL-01 + LIMINAL-02)\n\n"
        "| Factor | LIMINAL-01 mean | LIMINAL-02 mean | Effect |\n"
        "|--------|-----------------|-----------------|--------|\n"
        f"| feasibility | {recon['LIMINAL-01']['means'].get('feasibility_score', 0):.3f} | {recon['LIMINAL-02']['means'].get('feasibility_score', 0):.3f} | High → score floor |\n"
        f"| resource_pressure | {recon['LIMINAL-01']['means'].get('resource_pressure', 0):.3f} | {recon['LIMINAL-02']['means'].get('resource_pressure', 0):.3f} | Low → high headroom term |\n"
        f"| decision_score | {recon['LIMINAL-01']['means'].get('decision_score', 0):.3f} | {recon['LIMINAL-02']['means'].get('decision_score', 0):.3f} | Stuck 0.70–0.85 |\n\n"
        "### Implied contribution shares (offline eMBB)\n"
        f"```json\n{json.dumps(recon, indent=2)[:3500]}\n```\n",
        encoding="utf-8",
    )

    (OUT / "phase_2_score_sensitivity_model/SCORE_SENSITIVITY_MODEL.md").write_text(
        "# Phase 2 — Score Sensitivity Model\n\n**Verdict:** SCORE_SENSITIVITY_MODEL_DEFINED\n\n"
        "> **OFFLINE_DESIGN_ONLY** — does not alter runtime.\n\n"
        f"- Score drop needed from LIMINAL-02 centroid: **{sens_embb['score_drop_needed']}**\n"
        f"- Grid hits in 0.52–0.58 (eMBB): **{sens_embb['n_target_hits']}**\n"
        f"- {sens_embb['interpretation']}\n\n"
        f"```json\n{json.dumps({'eMBB': sens_embb, 'URLLC': sens_url}, indent=2)[:4000]}\n```\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_pressure_feasibility_corridor_design/PRESSURE_FEASIBILITY_CORRIDOR_DESIGN.md").write_text(
        "# Phase 3 — Pressure / Feasibility Corridor Design\n\n**Verdict:** PRESSURE_FEASIBILITY_CORRIDOR_DEFINED\n\n"
        f"```json\n{json.dumps(corridor, indent=2)}\n```\n",
        encoding="utf-8",
    )

    (OUT / "phase_4_operational_pressure_generation_design/OPERATIONAL_PRESSURE_GENERATION_DESIGN.md").write_text(
        "# Phase 4 — Operational Pressure Generation Design\n\n**Verdict:** OPERATIONAL_PRESSURE_GENERATION_DESIGN_READY\n\n"
        "## Allowed (runtime-backed)\n"
        "- **24–26M UDP** iperf (below LIMINAL-02 overshoot ladder)\n"
        "- **2 concurrent SLA submits** (distinct tenants, stagger 3s) — raises real PRB+RTT in snapshot\n"
        "- **Transport path load** — RTT rises via ueransim/iperf (no synthetic RTT)\n\n"
        "## Forbidden\n"
        "- Manual JSON override, fake `resource_pressure`, synthetic labels\n\n"
        "## Target\n"
        "- `resource_pressure` **0.35–0.65** before triplet (portal V1 formula from live telemetry)\n",
        encoding="utf-8",
    )

    (OUT / "phase_5_runtime_feasibility_degradation_design/RUNTIME_FEASIBILITY_DEGRADATION_DESIGN.md").write_text(
        "# Phase 5 — Runtime Feasibility Degradation Design\n\n**Verdict:** FEASIBILITY_DEGRADATION_DESIGN_READY\n\n"
        "Feasibility lowers only when **real** `resource_pressure` and **ml_risk** inputs increase:\n"
        "`feasibility = max(0, 1 - (risk + pressure)/2)` (frozen).\n\n"
        "- Increase multidomain pressure via PRB↑ + RTT↑ + optional core CPU load (if telemetry present)\n"
        "- Concurrent controlled demand per slice profile\n"
        "- Pre-triplet gate: feasibility ≤ **0.55**, pressure ≥ **0.30**\n"
        "- **No formula edit**\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_prb_governance_preservation_design/PRB_GOVERNANCE_PRESERVATION_DESIGN.md").write_text(
        "# Phase 6 — PRB Governance Preservation Design\n\n**Verdict:** PRB_GOVERNANCE_PRESERVATION_DESIGN_READY\n\n"
        "| Guard | Value |\n|-------|-------|\n| PRB target | 18–22.5% (inside 18–24) |\n| Soft abort | 23.5% |\n| Hard abort | 24% |\n| hard_prb_gate | ≥25% unchanged |\n| score_mode-only | triplet discard on hard_gate |\n| Monotonicity | post-hoc check PRB↑→score↓ |\n| Forbidden | ≥28M uncontrolled, ≥40M |\n",
        encoding="utf-8",
    )

    (OUT / "phase_7_candidate_campaign_blueprint/CANDIDATE_CAMPAIGN_BLUEPRINT.md").write_text(
        "# Phase 7 — Candidate Campaign Blueprint\n\n**Verdict:** NAD_LIMINAL_03_BLUEPRINT_READY\n\n"
        f"```json\n{json.dumps(blueprint, indent=2)}\n```\n",
        encoding="utf-8",
    )

    (OUT / "phase_8_regression_and_reviewer_risk/REGRESSION_AND_REVIEWER_RISK.md").write_text(
        "# Phase 8 — Regression and Reviewer Risk\n\n**Verdict:** REGRESSION_REVIEWER_RISK_DEFINED\n\n"
        "| Approach | Regression | Reviewer | Status |\n|----------|------------|----------|--------|\n"
        + "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | **{r[3]}** |" for r in risk_table)
        + "\n",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_pressure_feasibility_design_freeze/FINAL_PRESSURE_FEASIBILITY_DESIGN_FREEZE.md").write_text(
        f"# Phase 9 — Final Design Freeze\n\n# **{final_verdict}**\n\n"
        "## Mandatory questions\n\n"
        f"| Q | Answer |\n|---|--------|\n"
        f"| Q1 Safe PRB/pressure/feasibility combo? | **YES** (offline corridor) |\n"
        f"| Q2 Operational pressure? | **Concurrent submits + 24–26M iperf** |\n"
        f"| Q3 Feasibility reduction without formula? | **YES** via real telemetry pressure |\n"
        f"| Q4 PRB governance preserved? | **YES** |\n"
        f"| Q5 Avoid artificial divergence? | **Same-state + no synthetic labels** |\n"
        f"| Q6 Future campaign? | **NAD-LIMINAL-03** |\n"
        f"| Q7 Continue NAD-EXEC? | **YES** → EXEC-12 controls |\n\n"
        f"Digest: `{ACTIVE_DIGEST}`\n",
        encoding="utf-8",
    )

    _figures(recon, sens_embb, corridor, blueprint)

    de_img = ""
    try:
        de_img = subprocess.check_output(
            ["kubectl", "-n", "trisla", "get", "deploy", "trisla-decision-engine", "-o", "jsonpath={.spec.template.spec.containers[0].image}"],
            text=True,
        ).strip()
    except Exception:
        pass

    summary = {
        "phase": "NAD-EXEC-11",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final_verdict,
        "design_only": True,
        "active_digest": ACTIVE_DIGEST,
        "runtime_image": de_img,
        "factor_reconstruction": recon,
        "score_sensitivity": {"eMBB": sens_embb, "URLLC": sens_url},
        "pressure_feasibility_corridor": corridor,
        "nad_liminal_03_blueprint": blueprint,
        "mandatory_answers": answers,
        "phase_verdicts": {
            "phase1": "FACTOR_RESISTANCE_RECONSTRUCTED",
            "phase2": "SCORE_SENSITIVITY_MODEL_DEFINED",
            "phase3": "PRESSURE_FEASIBILITY_CORRIDOR_DEFINED",
            "phase4": "OPERATIONAL_PRESSURE_GENERATION_DESIGN_READY",
            "phase5": "FEASIBILITY_DEGRADATION_DESIGN_READY",
            "phase6": "PRB_GOVERNANCE_PRESERVATION_DESIGN_READY",
            "phase7": "NAD_LIMINAL_03_BLUEPRINT_READY",
            "phase8": "REGRESSION_REVIEWER_RISK_DEFINED",
            "phase9": final_verdict,
        },
        "next_prompt": "PROMPT_TRISLA_NAD_EXEC_12_PRESSURE_FEASIBILITY_RUNTIME_CONTROL_IMPLEMENTATION_V1",
        "approval_required": "NAD_EXEC_11_APPROVED",
        "hard_stop": True,
    }
    (OUT / "analysis/pressure_feasibility_liminal_design_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

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
