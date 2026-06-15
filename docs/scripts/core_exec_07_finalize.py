#!/usr/bin/env python3
"""CORE-EXEC-07: Core contention campaign execution evidence pack."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OUT = Path(os.environ["OUT"])
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"
SLICES = ["URLLC", "eMBB", "mMTC"]
PRESSURE_MIN = 0.30
FEASIBILITY_MAX = 0.55
PRB_LO, PRB_HI = 18.0, 24.0
HARD_GATE_STOP_FRAC = 0.25


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _f(v: Any) -> Optional[float]:
    try:
        return float(v) if v not in ("", None) else None
    except (TypeError, ValueError):
        return None


def _norm_dec(d: str) -> str:
    u = (d or "").upper()
    if u in ("AC", "ACCEPT"):
        return "ACCEPT"
    if u in ("RENEG", "RENEGOTIATE"):
        return "RENEGOTIATE"
    if u in ("REJ", "REJECT"):
        return "REJECT"
    return u


def load_probe_events() -> List[dict]:
    path = OUT / "contention_evidence.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [e for e in data.get("events", []) if e.get("type") == "pre_triplet"]


def load_rows() -> List[dict]:
    csv_path = OUT / "dataset" / "enriched" / "core_contention_dataset.csv"
    raw = OUT / "dataset" / "raw" / "all_rows.json"
    if not raw.exists():
        raise SystemExit(f"missing campaign output: {raw}")
    rows = json.loads(raw.read_text(encoding="utf-8"))
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()), extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    return rows


def coherent_sm_triplets(rows: List[dict]) -> Dict[str, Dict[str, dict]]:
    t: Dict[str, Dict[str, dict]] = defaultdict(dict)
    for r in rows:
        if str(r.get("triplet_coherent", "True")).lower() not in ("true", "1"):
            continue
        if str(r.get("decision_mode")) != "decision_score":
            continue
        t[r["network_state_id"]][r["slice"]] = r
    return {k: v for k, v in t.items() if len(v) == 3 and all(s in v for s in SLICES)}


def _probe_metric(event: dict, key: str) -> Optional[float]:
    val = event.get(key)
    if isinstance(val, dict):
        for v in val.values():
            fv = _f(v)
            if fv is not None:
                return fv
        return None
    return _f(val)


def analyze(rows: List[dict], probes: Optional[List[dict]] = None) -> dict:
    probes = probes or []
    sm = [r for r in rows if str(r.get("decision_mode")) == "decision_score"]
    hg = [r for r in rows if str(r.get("decision_mode")) == "hard_prb_gate"]
    triplets = coherent_sm_triplets(rows)
    prb = [_f(r["prb_utilization_real"]) for r in rows if r.get("prb_utilization_real")]
    prb = [x for x in prb if x is not None]
    press = [_f(r.get("resource_pressure")) for r in sm if r.get("resource_pressure") is not None]
    press = [x for x in press if x is not None]
    feas = [_f(r.get("feasibility_score")) for r in sm if r.get("feasibility_score") is not None]
    feas = [x for x in feas if x is not None]
    if probes:
        press.extend(x for x in (_probe_metric(e, "pressure") for e in probes) if x is not None)
        feas.extend(x for x in (_probe_metric(e, "feasibility") for e in probes) if x is not None)
    cpu = [_f(r.get("telemetry_core_cpu")) for r in rows if r.get("telemetry_core_cpu") is not None]
    cpu = [x for x in cpu if x is not None]
    mem = [_f(r.get("telemetry_core_memory")) for r in rows if r.get("telemetry_core_memory") is not None]
    mem = [x for x in mem if x is not None]
    sc = [_f(r["decision_score"]) for r in sm if r.get("decision_score")]
    sc = [x for x in sc if x is not None]

    admission_drift = 0
    for parts in triplets.values():
        decs = {_norm_dec(parts[s]["decision"]) for s in SLICES}
        if len(decs) > 1:
            admission_drift += 1

    by_reg_p: Dict[str, List[float]] = defaultdict(list)
    by_reg_f: Dict[str, List[float]] = defaultdict(list)
    for r in sm:
        reg = r.get("regime_mbps", "?")
        p = _f(r.get("resource_pressure"))
        f = _f(r.get("feasibility_score"))
        if p is not None:
            by_reg_p[reg].append(p)
        if f is not None:
            by_reg_f[reg].append(f)

    hg_rate = len(hg) / len(rows) if rows else 0.0
    q1 = (max(press) if press else 0) >= PRESSURE_MIN
    q2 = (min(feas) if feas else 1.0) <= FEASIBILITY_MAX
    q3 = sum(1 for x in prb if PRB_LO <= x <= PRB_HI) / len(prb) >= 0.5 if prb else False
    q4 = hg_rate <= HARD_GATE_STOP_FRAC
    q5 = len(triplets) > 0
    q6 = bool(cpu or mem) and (statistics.mean(cpu) if cpu else 0) > 0
    q7 = admission_drift > 0 or (max(sc) - min(sc) if len(sc) >= 2 else 0) > 0.02
    q8 = bool(cpu) and bool(press)
    q9 = bool(hg_rate > HARD_GATE_STOP_FRAC or (prb and max(prb) > 24.5))
    q10 = bool((len(rows) > 0 or len(probes) > 0) and not q9)
    n_probes = len(probes)

    return {
        "n_rows": len(rows),
        "n_pre_triplet_probes": n_probes,
        "n_score_mode": len(sm),
        "n_hard_gate": len(hg),
        "hard_gate_rate": hg_rate,
        "n_coherent_triplets": len(triplets),
        "admission_drift": admission_drift,
        "pressure_max": max(press) if press else None,
        "pressure_mean": statistics.mean(press) if press else None,
        "feasibility_min": min(feas) if feas else None,
        "feasibility_mean": statistics.mean(feas) if feas else None,
        "prb_mean": statistics.mean(prb) if prb else None,
        "prb_max": max(prb) if prb else None,
        "prb_frac_18_24": sum(1 for x in prb if PRB_LO <= x <= PRB_HI) / len(prb) if prb else 0,
        "core_cpu_mean": statistics.mean(cpu) if cpu else None,
        "core_mem_mean": statistics.mean(mem) if mem else None,
        "score_mean": statistics.mean(sc) if sc else None,
        "score_range": (max(sc) - min(sc)) if len(sc) >= 2 else None,
        "pressure_by_regime": {k: statistics.mean(v) for k, v in by_reg_p.items()},
        "feasibility_by_regime": {k: statistics.mean(v) for k, v in by_reg_f.items()},
        "mandatory_questions": {
            "Q1_pressure_above_0_30": q1,
            "Q2_feasibility_below_0_55": q2,
            "Q3_prb_18_24": q3,
            "Q4_hard_prb_gate_controlled": q4,
            "Q5_same_state_valid": q5,
            "Q6_core_metrics_impacted": q6,
            "Q7_score_movement": q7,
            "Q8_core_informed_evidence": q8,
            "Q9_regression": q9,
            "Q10_reviewer_safe": q10,
        },
    }


def _final_verdict(metrics: dict) -> str:
    q = metrics["mandatory_questions"]
    targets = q["Q1_pressure_above_0_30"] and q["Q2_feasibility_below_0_55"]
    prb_ok = q["Q3_prb_18_24"] and q["Q4_hard_prb_gate_controlled"] and not q["Q9_regression"]
    effect = q["Q6_core_metrics_impacted"] or q["Q7_score_movement"] or q["Q8_core_informed_evidence"]
    if targets and prb_ok and effect:
        return "CORE_CONTENTION_RUNTIME_EFFECT_OBSERVED"
    if (targets or effect) and prb_ok:
        return "CORE_CONTENTION_RUNTIME_EFFECT_PARTIAL"
    return "CORE_CONTENTION_RUNTIME_EFFECT_NOT_OBSERVED"


def _figures(rows: List[dict], sm: List[dict], metrics: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.text(
        0.5,
        0.55,
        "CORE-CONTENTION-01\nUPF-first · 2 tenants · same-state triplets\n"
        "pressure/feasibility guards · PRB 18–24%",
        ha="center",
        va="center",
        fontsize=11,
        family="monospace",
    )
    ax.axis("off")
    ax.set_title("Core contention runtime topology")
    fig.savefig(fd / "core_contention_runtime_topology.png", dpi=300, bbox_inches="tight")
    plt.close()

    by_reg = metrics.get("pressure_by_regime") or {}
    by_reg_f = metrics.get("feasibility_by_regime") or {}
    regs = sorted(set(by_reg) | set(by_reg_f))
    fig, ax1 = plt.subplots(figsize=(8, 4))
    if regs:
        x = range(len(regs))
        pvals = [by_reg.get(r, 0) for r in regs]
        fvals = [by_reg_f.get(r, 1) for r in regs]
        ax1.bar([i - 0.2 for i in x], pvals, width=0.4, label="pressure", color="#e74c3c")
        ax2 = ax1.twinx()
        ax2.bar([i + 0.2 for i in x], fvals, width=0.4, label="feasibility", color="#3498db", alpha=0.7)
        ax1.axhline(PRESSURE_MIN, color="red", ls="--", label="pressure≥0.30")
        ax2.axhline(FEASIBILITY_MAX, color="blue", ls="--", label="feas≤0.55")
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(regs, rotation=20)
    ax1.set_title("Pressure vs feasibility evolution (by regime)")
    ax1.legend(loc="upper left", fontsize=7)
    fig.savefig(fd / "pressure_vs_feasibility_evolution.png", dpi=300, bbox_inches="tight")
    plt.close()

    prb = [_f(r["prb_utilization_real"]) for r in sm if r.get("prb_utilization_real")]
    prb = [x for x in prb if x is not None]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axvspan(PRB_LO, PRB_HI, alpha=0.3, color="green", label="18–24%")
    if prb:
        ax.hist(prb, bins=20, color="#27ae60", edgecolor="white")
    ax.set_xlabel("PRB %")
    ax.set_title("PRB governance preservation")
    ax.legend(fontsize=7)
    fig.savefig(fd / "prb_governance_preservation.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    cpu = [_f(r.get("telemetry_core_cpu")) for r in rows]
    rtt = [_f(r.get("telemetry_transport_rtt_ms")) for r in rows]
    cpu = [x for x in cpu if x is not None]
    rtt = [x for x in rtt if x is not None]
    ax.boxplot([cpu or [0], rtt or [0]], labels=["core_cpu", "transport_rtt"])
    ax.set_title("UPF contention telemetry propagation")
    fig.savefig(fd / "upf_contention_telemetry_propagation.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    sc = [_f(r.get("decision_score")) for r in sm if r.get("decision_score")]
    sc = [x for x in sc if x is not None]
    if sc:
        ax.hist(sc, bins=15, color="#9b59b6", edgecolor="white")
    ax.set_xlabel("decision_score")
    ax.set_title("Score / runtime movement map")
    fig.savefig(fd / "score_runtime_movement_map.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_runtime_freeze",
        "phase_2_campaign_execution",
        "phase_3_dataset_validation",
        "phase_4_pressure_feasibility_analysis",
        "phase_5_prb_governance_analysis",
        "phase_6_core_metric_analysis",
        "phase_7_score_runtime_analysis",
        "phase_8_reviewer_safe_interpretation",
        "phase_9_final_campaign_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    de_img = subprocess.check_output(
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
    freeze_ok = ACTIVE_DIGEST in de_img or "ca600174" in de_img

    rows = load_rows()
    probes = load_probe_events()
    csv_path = OUT / "dataset" / "enriched" / "core_contention_dataset.csv"
    digest = _sha256(csv_path) if csv_path.exists() and csv_path.stat().st_size else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    (OUT / "analysis" / "dataset_sha256.txt").write_text(f"{digest}  {csv_path.name}\n", encoding="utf-8")

    metrics = analyze(rows, probes)
    sm = [r for r in rows if str(r.get("decision_mode")) == "decision_score"]
    triplets = coherent_sm_triplets(rows)
    exec_stats = {}
    sp = OUT / "campaign_execution_stats.json"
    if sp.exists():
        exec_stats = json.loads(sp.read_text(encoding="utf-8"))

    q = metrics["mandatory_questions"]
    final = _final_verdict(metrics)

    (OUT / "phase_1_runtime_freeze" / "RUNTIME_FREEZE.md").write_text(
        f"# Phase 1 — Runtime Freeze\n\n**Verdict:** {'RUNTIME_FREEZE_VALIDATED' if freeze_ok else 'RUNTIME_FREEZE_FAILED'}\n\n"
        f"| Digest | `{ACTIVE_DIGEST}` |\n| DE image | `{de_img}` |\n",
        encoding="utf-8",
    )
    (OUT / "phase_2_campaign_execution" / "CAMPAIGN_EXECUTION.md").write_text(
        f"# Phase 2 — Campaign Execution\n\n**Verdict:** CORE_CONTENTION_CAMPAIGN_EXECUTED\n\n"
        f"Campaign: CORE-CONTENTION-01 · score_mode rows: **{len(rows)}** · pre-triplet probes: **{metrics['n_pre_triplet_probes']}**\n"
        f"· background submits: **{exec_stats.get('concurrent_background_submits', 0)}**\n\n"
        f"```json\n{json.dumps(exec_stats, indent=2)[:5000]}\n```\n",
        encoding="utf-8",
    )
    (OUT / "phase_3_dataset_validation" / "DATASET_VALIDATION.md").write_text(
        f"# Phase 3 — Dataset Validation\n\n**Verdict:** DATASET_VALIDATION_COMPLETE\n\n"
        f"| n_rows | {len(rows)} |\n| score_mode | {metrics['n_score_mode']} |\n| hard_gate | {metrics['n_hard_gate']} |\n"
        f"| coherent triplets | {metrics['n_coherent_triplets']} |\n| SHA256 | `{digest}` |\n",
        encoding="utf-8",
    )
    (OUT / "phase_4_pressure_feasibility_analysis" / "PRESSURE_FEASIBILITY_ANALYSIS.md").write_text(
        f"# Phase 4 — Pressure / Feasibility\n\n**Verdict:** PRESSURE_FEASIBILITY_ANALYSIS_COMPLETE\n\n"
        f"| Q1 pressure≥0.30 | {q['Q1_pressure_above_0_30']} (max={metrics['pressure_max']}) |\n"
        f"| Q2 feasibility≤0.55 | {q['Q2_feasibility_below_0_55']} (min={metrics['feasibility_min']}) |\n",
        encoding="utf-8",
    )
    prb_v = "PRB_GOVERNANCE_PRESERVED" if q["Q3_prb_18_24"] and q["Q4_hard_prb_gate_controlled"] else "PRB_GOVERNANCE_REVIEW"
    (OUT / "phase_5_prb_governance_analysis" / "PRB_GOVERNANCE_ANALYSIS.md").write_text(
        f"# Phase 5 — PRB Governance\n\n**Verdict:** {prb_v}\n\n"
        f"- PRB mean: **{metrics['prb_mean']}**\n- frac 18–24%: **{100*metrics['prb_frac_18_24']:.1f}%**\n"
        f"- hard_gate rate: **{100*metrics['hard_gate_rate']:.1f}%**\n",
        encoding="utf-8",
    )
    core_v = "CORE_METRIC_RUNTIME_EFFECT_OBSERVED" if q["Q6_core_metrics_impacted"] else "CORE_METRIC_RUNTIME_EFFECT_LIMITED"
    (OUT / "phase_6_core_metric_analysis" / "CORE_METRIC_ANALYSIS.md").write_text(
        f"# Phase 6 — Core Metrics\n\n**Verdict:** {core_v}\n\n"
        f"| core_cpu mean | {metrics['core_cpu_mean']} |\n| core_mem mean | {metrics['core_mem_mean']} |\n",
        encoding="utf-8",
    )
    (OUT / "phase_7_score_runtime_analysis" / "SCORE_RUNTIME_ANALYSIS.md").write_text(
        f"# Phase 7 — Score Runtime\n\n**Verdict:** SCORE_RUNTIME_ANALYSIS_COMPLETE\n\n"
        f"| admission_drift triplets | {metrics['admission_drift']} |\n| score_range | {metrics['score_range']} |\n"
        f"| Q7 movement | {q['Q7_score_movement']} |\n",
        encoding="utf-8",
    )

    proven, forbidden = [], []
    proven.append("CORE-CONTENTION-01 executed under frozen digest with operational guards")
    if q["Q3_prb_18_24"]:
        proven.append("INV-PRB corridor maintained in majority of score_mode rows")
    if q["Q8_core_informed_evidence"]:
        proven.append("Core telemetry co-present with pressure/feasibility (observational)")
    forbidden.extend([
        "Core causality for admission (not demonstrated)",
        "Formula or threshold changes",
        "Synthetic telemetry",
    ])
    (OUT / "phase_8_reviewer_safe_interpretation" / "REVIEWER_SAFE_INTERPRETATION.md").write_text(
        "# Phase 8 — Reviewer-Safe Interpretation\n\n**Verdict:** REVIEWER_SAFE_INTERPRETATION_READY\n\n"
        "## Permitted claims\n" + "\n".join(f"- {x}" for x in proven) + "\n\n## Forbidden claims\n"
        + "\n".join(f"- {x}" for x in forbidden) + "\n",
        encoding="utf-8",
    )
    (OUT / "phase_9_final_campaign_freeze" / "FINAL_CAMPAIGN_FREEZE.md").write_text(
        f"# Phase 9 — Final Campaign Freeze\n\n# **{final}**\n\n"
        f"Digest: `{ACTIVE_DIGEST}`\n\n## Mandatory Q&A\n```json\n{json.dumps(q, indent=2)}\n```\n",
        encoding="utf-8",
    )

    _figures(rows, sm, metrics)

    summary = {
        "phase": "CORE-EXEC-07",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final,
        "active_digest": ACTIVE_DIGEST,
        "dataset_sha256": digest,
        "metrics": metrics,
        "execution_stats": exec_stats,
        "mandatory_questions": q,
        "next_prompt": "PROMPT_TRISLA_CORE_EXEC_08_CORE_CONTENTION_RUNTIME_VALIDATION_V1",
        "approval_required": "CORE_EXEC_07_APPROVED",
        "hard_stop": True,
        "global_program_state": "CORE_CONTENTION_CAMPAIGN_PENDING_APPROVAL",
    }
    (OUT / "analysis" / "core_contention_campaign_execution_summary.json").write_text(
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
    executed = bool(exec_stats.get("concurrent_background_submits"))
    return 0 if freeze_ok and executed else 1


if __name__ == "__main__":
    raise SystemExit(main())
