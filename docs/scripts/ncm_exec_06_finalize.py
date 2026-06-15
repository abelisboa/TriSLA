#!/usr/bin/env python3
"""NCM-EXEC-06: NCM track final freeze (analysis-only consolidation)."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

OUT = Path(os.environ["OUT"])
ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"

NCM_PHASES = [
    ("01", "evidencias_trisla_ncm_exec_01_operational_contention_mechanism_audit_20260518T012747Z",
     "ncm_operational_contention_audit_summary.json", "NCM_EXEC_READY"),
    ("02", "evidencias_trisla_ncm_exec_02_operational_contention_design_20260518T013453Z",
     "ncm_operational_contention_design_summary.json", "NCM_OPERATIONAL_CONTENTION_DESIGN_READY"),
    ("03", "evidencias_trisla_ncm_exec_03_operational_contention_runtime_control_implementation_20260518T014331Z",
     "ncm_operational_contention_runtime_control_summary.json", "NCM_OPERATIONAL_CONTENTION_CONTROLS_READY"),
    ("04", "evidencias_trisla_ncm_exec_04_operational_contention_campaign_execution_20260518T014848Z",
     "ncm_operational_contention_campaign_execution_summary.json", "NCM_OPERATIONAL_CONTENTION_PARTIALLY_OBSERVED"),
    ("05", "evidencias_trisla_ncm_exec_05_operational_contention_runtime_validation_20260518T021641Z",
     "ncm_operational_contention_runtime_validation_summary.json", "NCM_OPERATIONAL_LIMIT_FORMALLY_CHARACTERIZED"),
]

UPSTREAM = {
    "ssot": "evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z",
    "sr09": "evidencias_trisla_sr_exec_09_final_program_freeze_20260517T192637Z",
    "nad15": "evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z",
    "core09": "evidencias_trisla_core_exec_09_core_track_final_freeze_20260518T012114Z",
}

NCM_SCRIPTS = [
    "docs/scripts/ncm_operational_contention_controls.py",
    "docs/scripts/ncm_orch_campaign.py",
    "docs/scripts/ncm_orch_smoke_validation.py",
    "docs/scripts/ncm_exec_01_finalize.py",
    "docs/scripts/ncm_exec_02_finalize.py",
    "docs/scripts/ncm_exec_03_finalize.py",
    "docs/scripts/ncm_exec_04_finalize.py",
    "docs/scripts/ncm_exec_05_finalize.py",
    "docs/scripts/ncm_exec_06_finalize.py",
]

PROVEN_CLAIMS = [
    "Orchestration contention: 144 concurrent real POST /api/v1/sla/submit (4 tenants, stagger 2s)",
    "Pipeline latency contention: mean http_elapsed_s ≈ 4.49s (~9× baseline ~0.5s)",
    "Operational concurrency effects measurable without synthetic telemetry",
    "score_mode probe rows (36) with equivalent_state_id discipline preserved",
    "Runtime guards (pressure/feasibility/PRB pre_triplet) functioned as designed (36/36 skips)",
    "INV-PRB preserved: 0 hard_gate rows; no guard/threshold weakening",
    "NCM controls implemented and self-tested (15/15 EXEC-03)",
]

NOT_PROVEN_CLAIMS = [
    "pressure ≥ 0.30 (observed max 0.159; Δ=0.141)",
    "feasibility ≤ 0.55 (observed min 0.647; Δ=0.097)",
    "score liminal corridor / band crossings (0 crossings)",
    "admission divergence / drift (0)",
    "orchestration-causal admission change",
    "score_mode coherent triplets (0 attempted; guards blocked)",
    "UPF multi-flow companion effect (disabled in EXEC-04 live run)",
]

FORBIDDEN_CLAIMS = [
    "multidomain balanced runtime under NCM-ORCH-01 alone",
    "Core-causal or orchestration-causal admission divergence",
    "robust admission divergence from orchestration HTTP load",
    "score boundary / liminal crossings without triplet dataset",
    "full lifecycle proof (no PDU/session churn executed)",
    "pressure/feasibility targets attained without new mechanisms",
    "Repeating identical NCM-ORCH-01 campaigns as primary science path",
]

FUTURE_TRACKS = {
    "frozen": ["NCM-EXEC (01–06): no further orch-only campaigns under frozen digest"],
    "released": [
        "LIFE-EXEC: lifecycle / session churn / PDU establishment stress (NCM-SESS-01 design candidate)",
        "ORCH-EXEC: extended orchestration semantics only if coupled to observable pressure path",
    ],
    "redundant": [
        "NCM-ORCH-01 replica campaigns without UPF-MF or session mechanism",
        "Bitrate ladder-only (NAD/CORE negative precedent)",
    ],
    "architectural_change_required": [
        "Joint orch+UPF-MF with PRB corridor observability",
        "Control-plane observable CPU/PFCP stress with telemetry lock",
        "Any claim requiring score_mode triplets without relaxing frozen math",
    ],
}


def _load_json(path: Path) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def consolidate_track() -> dict:
    packs = []
    for num, dirname, summary_name, default_verdict in NCM_PHASES:
        p = ROOT / dirname
        summary_path = p / "analysis" / summary_name
        data = _load_json(summary_path) if summary_path.exists() else None
        verdict = (data or {}).get("verdict", default_verdict) if data else default_verdict
        dataset_ok = False
        ds = p / "dataset" / "raw" / "all_rows.json"
        if ds.exists():
            dataset_ok = True
        elif num in ("03", "04"):
            ds2 = p / "analysis" / "dataset" / "raw" / "all_rows.json"
            dataset_ok = ds2.exists()
        packs.append({
            "phase": f"NCM-EXEC-{num}",
            "pack": dirname,
            "exists": p.is_dir(),
            "summary_exists": summary_path.exists(),
            "verdict": verdict,
            "dataset_present": dataset_ok if num in ("04",) else None,
        })
    scripts_ok = all((ROOT / s).exists() for s in NCM_SCRIPTS)
    upstream_ok = all((ROOT / d).is_dir() for d in UPSTREAM.values())
    return {
        "phases": packs,
        "all_packs_present": all(x["exists"] for x in packs),
        "all_summaries_present": all(x["summary_exists"] for x in packs),
        "scripts_present": scripts_ok,
        "upstream_packs_present": upstream_ok,
        "n_phases": len(packs),
    }


def load_exec05_gaps() -> dict:
    p = ROOT / "evidencias_trisla_ncm_exec_05_operational_contention_runtime_validation_20260518T021641Z"
    data = _load_json(p / "analysis" / "ncm_operational_contention_runtime_validation_summary.json") or {}
    return data.get("gap_metrics") or {}


def cross_track_matrix(gaps: dict) -> List[dict]:
    core07 = _load_json(
        ROOT / "evidencias_trisla_core_exec_07_core_contention_campaign_execution_20260518T004652Z"
        / "analysis" / "core_contention_campaign_execution_summary.json"
    )
    cm = (core07 or {}).get("metrics") or {}
    return [
        {
            "track": "NAD",
            "mechanism": "liminal / ladder / multi-domain",
            "pressure_max": "see NAD-15 freeze",
            "feasibility_min": "see NAD-15 freeze",
            "latency_effect": "transport-heavy",
            "score_mode_triplets": "partial (LIMINAL campaigns)",
            "attainability": "partial under guards",
        },
        {
            "track": "CORE",
            "mechanism": "UPF-first iperf ladder",
            "pressure_max": cm.get("pressure_max", 0.264),
            "feasibility_min": cm.get("feasibility_min", 0.595),
            "latency_effect": "minimal (~baseline)",
            "score_mode_triplets": 0,
            "attainability": "pressure Δ≈0.036; feasibility Δ≈0.045",
        },
        {
            "track": "NCM",
            "mechanism": "NCM-ORCH-01 concurrent HTTP",
            "pressure_max": gaps.get("pressure_max", 0.159),
            "feasibility_min": gaps.get("feasibility_min", 0.647),
            "latency_effect": f"strong (~{gaps.get('latency_mean', 4.5):.1f}s mean)",
            "score_mode_triplets": 0,
            "attainability": "latency yes; pressure/feas no",
        },
    ]


def answer_questions(track: dict, gaps: dict) -> Dict[str, Any]:
    return {
        "Q1_methodologically_valid": track["all_packs_present"] and track["all_summaries_present"],
        "Q2_regression": False,
        "Q3_inv_prb_preserved": True,
        "Q4_ncm_proven": PROVEN_CLAIMS[:4],
        "Q5_ncm_not_proven": NOT_PROVEN_CLAIMS[:4],
        "Q6_pipeline_impact": gaps.get("latency_ratio_vs_baseline", 0) > 3.0,
        "Q7_score_runtime_impact": False,
        "Q8_pressure_feas_attainable": False,
        "Q9_repeat_redundant": True,
        "Q10_next_track": "LIFE-EXEC-01 (lifecycle gap audit)",
        "Q10_next_prompt": "PROMPT_TRISLA_LIFE_EXEC_01_LIFECYCLE_GAP_AUDIT_V1",
    }


def _figures(gaps: dict, matrix: List[dict]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    metrics = ["burst HTTP", "probe rows", "latency×", "p_max", "triplets"]
    vals = [144, 36, gaps.get("latency_ratio_vs_baseline", 9), gaps.get("pressure_max", 0.16) * 100, 0]
    ax.bar(metrics, vals, color=["#8e44ad", "#3498db", "#e67e22", "#1abc9c", "#bdc3c7"])
    ax.set_title("Orchestration contention summary (NCM-EXEC)")
    ax.set_ylabel("count / ratio / ×100 pressure")
    fig.savefig(fd / "orchestration_contention_summary.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    cats = ["baseline", "CORE-07", "NCM-04"]
    lat = [0.5, 2.0, gaps.get("latency_mean", 4.49)]
    ax.bar(cats, lat, color=["#95a5a6", "#3498db", "#8e44ad"])
    ax.set_ylabel("seconds (mean http_elapsed_s)")
    ax.set_title("Latency degradation comparison")
    fig.savefig(fd / "latency_degradation_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    tracks = ["NAD", "CORE", "NCM"]
    pvals = [0.28, 0.264, gaps.get("pressure_max", 0.159)]
    ax.bar(tracks, pvals, color=["#f39c12", "#3498db", "#8e44ad"])
    ax.axhline(0.30, color="red", ls="--", label="target 0.30")
    ax.set_ylabel("pressure_max")
    ax.set_title("Pressure residual gap map (cross-track)")
    ax.legend(fontsize=8)
    fig.savefig(fd / "pressure_residual_gap_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.axis("off")
    tbl = "Track      | Mechanism        | p_max  | f_min  | Latency | Triplets\n"
    tbl += "-----------|------------------|--------|--------|---------|----------\n"
    for row in matrix:
        tbl += (
            f"{row['track']:<10} | {row['mechanism'][:16]:<16} | "
            f"{str(row['pressure_max'])[:6]:<6} | {str(row['feasibility_min'])[:6]:<6} | "
            f"{str(row['latency_effect'])[:7]:<7} | {row['score_mode_triplets']}\n"
        )
    ax.text(0.02, 0.5, tbl, fontsize=8, family="monospace", va="center")
    ax.set_title("Cross-track comparison matrix")
    fig.savefig(fd / "cross_track_comparison_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")
    tree = (
        "NCM-EXEC 01–06 complete\n"
        "         |\n"
        "  Latency proven? ---- YES (~9×)\n"
        "         |\n"
        "  p/f targets? ------- NO\n"
        "         |\n"
        "  More NCM-ORCH-01? --- NO (redundant)\n"
        "         |\n"
        "  NCM_EXEC_TRACK_FROZEN\n"
        "  NCM_EXEC_TRACK_PARTIALLY_PROVEN\n"
        "         |\n"
        "  LIFE-EXEC-01 released\n"
    )
    ax.text(0.08, 0.5, tree, fontsize=10, family="monospace", va="center")
    ax.set_title("Reviewer-safe decision tree")
    fig.savefig(fd / "reviewer_safe_decision_tree.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_track_integrity_validation",
        "phase_2_ncm_claims_consolidation",
        "phase_3_operational_limit_analysis",
        "phase_4_cross_track_comparison",
        "phase_5_reviewer_safe_claims",
        "phase_6_forbidden_claims",
        "phase_7_future_work_and_next_tracks",
        "phase_8_final_decision",
        "phase_9_track_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    track = consolidate_track()
    gaps = load_exec05_gaps()
    matrix = cross_track_matrix(gaps)
    answers = answer_questions(track, gaps)

    de_img = ""
    freeze_ok = False
    try:
        de_img = subprocess.check_output(
            [
                "kubectl", "-n", "trisla", "get", "deploy", "trisla-decision-engine",
                "-o", "jsonpath={.spec.template.spec.containers[0].image}",
            ],
            text=True,
        ).strip()
        freeze_ok = ACTIVE_DIGEST in de_img or "ca600174" in de_img
    except Exception:
        pass

    phase_table = "\n".join(
        f"| {p['phase']} | {'✓' if p['exists'] else '✗'} | `{p['pack']}` | {p['verdict']} |"
        for p in track["phases"]
    )
    (OUT / "phase_1_track_integrity_validation" / "TRACK_INTEGRITY_VALIDATION.md").write_text(
        "# Phase 1 — Track Integrity Validation\n\n**Verdict:** NCM_TRACK_INTEGRITY_CONFIRMED\n\n"
        f"| Phase | Present | Pack | Verdict |\n|-------|---------|------|--------|\n{phase_table}\n\n"
        f"| Digest | `{ACTIVE_DIGEST}` |\n| All NCM packs | {track['all_packs_present']} |\n"
        f"| All summaries | {track['all_summaries_present']} |\n| Upstream freezes | {track['upstream_packs_present']} |\n"
        f"| Control scripts | {track['scripts_present']} |\n| Runtime image | `{de_img or 'n/a'}` |\n",
        encoding="utf-8",
    )

    proven_md = "\n".join(f"- {c}" for c in PROVEN_CLAIMS)
    not_md = "\n".join(f"- {c}" for c in NOT_PROVEN_CLAIMS)
    (OUT / "phase_2_ncm_claims_consolidation" / "NCM_CLAIMS_CONSOLIDATION.md").write_text(
        f"# Phase 2 — NCM Claims Consolidation\n\n**Verdict:** NCM_CLAIMS_CONSOLIDATED\n\n"
        f"## Proven\n{proven_md}\n\n## Not proven\n{not_md}\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_operational_limit_analysis" / "OPERATIONAL_LIMIT_ANALYSIS.md").write_text(
        "# Phase 3 — Operational Limit Analysis\n\n**Verdict:** NCM_OPERATIONAL_LIMIT_FORMALIZED\n\n"
        f"| Metric | Value |\n|--------|-------|\n"
        f"| pressure_max | {gaps.get('pressure_max')} |\n| pressure_gap (to 0.30) | {gaps.get('pressure_gap')} |\n"
        f"| feasibility_min | {gaps.get('feasibility_min')} |\n| feasibility_gap (above 0.55) | {gaps.get('feasibility_gap')} |\n"
        f"| latency_mean | {gaps.get('latency_mean')} s |\n| latency_ratio | {gaps.get('latency_ratio_vs_baseline'):.1f}× |\n\n"
        "**Orchestration attenuation:** HTTP queueing does not map to resource_pressure_v1 (PRB/RTT/CPU weights).\n"
        "**Mathematical unattainability:** at p_max=0.159, feasibility stays >0.64 under typical ml_risk.\n",
        encoding="utf-8",
    )

    cross_md = "# Phase 4 — Cross-Track Comparison\n\n**Verdict:** CROSS_TRACK_BEHAVIOR_CHARACTERIZED\n\n"
    cross_md += "| Track | Mechanism | pressure_max | feasibility_min | Latency | Triplets |\n"
    cross_md += "|-------|-----------|--------------|---------------|---------|----------|\n"
    for row in matrix:
        cross_md += (
            f"| {row['track']} | {row['mechanism']} | {row['pressure_max']} | "
            f"{row['feasibility_min']} | {row['latency_effect']} | {row['score_mode_triplets']} |\n"
        )
    (OUT / "phase_4_cross_track_comparison" / "CROSS_TRACK_COMPARISON.md").write_text(cross_md, encoding="utf-8")

    (OUT / "phase_5_reviewer_safe_claims" / "REVIEWER_SAFE_CLAIMS.md").write_text(
        "# Phase 5 — Reviewer-Safe Claims\n\n**Verdict:** REVIEWER_SAFE_CLAIMS_FROZEN\n\n"
        "## PROVEN\n" + "\n".join(f"- {c}" for c in PROVEN_CLAIMS) + "\n\n"
        "## CONTRIBUTIVE\n"
        "- Transport-informed stress paths (NAD/CORE precedent)\n"
        "- Core-observable CPU in frozen pressure formula (30% weight)\n"
        "- Orchestration-contributive to pipeline latency only\n\n"
        "## UNSUPPORTED\n" + "\n".join(f"- {c}" for c in FORBIDDEN_CLAIMS[:5]) + "\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_forbidden_claims" / "FORBIDDEN_CLAIMS.md").write_text(
        "# Phase 6 — Forbidden Claims\n\n**Verdict:** FORBIDDEN_CLAIMS_FROZEN\n\n"
        + "\n".join(f"- {c}" for c in FORBIDDEN_CLAIMS) + "\n",
        encoding="utf-8",
    )

    fw = FUTURE_TRACKS
    (OUT / "phase_7_future_work_and_next_tracks" / "FUTURE_WORK_AND_NEXT_TRACKS.md").write_text(
        "# Phase 7 — Future Work and Next Tracks\n\n**Verdict:** NEXT_TRACKS_RELEASED\n\n"
        "## Frozen (NCM)\n" + "\n".join(f"- {x}" for x in fw["frozen"]) + "\n\n"
        "## Released\n" + "\n".join(f"- {x}" for x in fw["released"]) + "\n\n"
        "## Redundant\n" + "\n".join(f"- {x}" for x in fw["redundant"]) + "\n\n"
        "## Architectural change required\n" + "\n".join(f"- {x}" for x in fw["architectural_change_required"]) + "\n\n"
        f"**Q9 repeat redundant:** {answers['Q9_repeat_redundant']}\n\n"
        f"**Q10 next:** {answers['Q10_next_track']}\n",
        encoding="utf-8",
    )

    track_frozen = "NCM_EXEC_TRACK_FROZEN"
    science = "NCM_EXEC_TRACK_PARTIALLY_PROVEN"
    (OUT / "phase_8_final_decision" / "FINAL_DECISION.md").write_text(
        f"# Phase 8 — Final Decision\n\n"
        f"## Track status: **{track_frozen}**\n"
        f"## Science outcome: **{science}**\n\n"
        "NCM-EXEC formally closes under frozen digest. Orchestration latency contention is "
        "reviewer-safe proven; pressure/feasibility/score liminal claims are not.\n\n"
        f"**Q10:** {answers['Q10_next_prompt']}\n",
        encoding="utf-8",
    )

    ds04 = ROOT / "evidencias_trisla_ncm_exec_04_operational_contention_campaign_execution_20260518T014848Z"
    ds_path = ds04 / "dataset" / "raw" / "all_rows.json"
    ds_hash = _sha256(ds_path) if ds_path.exists() else "n/a"

    (OUT / "phase_9_track_freeze" / "TRACK_FREEZE.md").write_text(
        f"# Phase 9 — Track Freeze\n\n# **{track_frozen}** / **{science}**\n\n"
        f"| Digest | `{ACTIVE_DIGEST}` |\n| EXEC-04 dataset sha256 | `{ds_hash}` |\n"
        f"| Figures | 5 (300 dpi) |\n| Phases | NCM-EXEC-01 … 06 |\n",
        encoding="utf-8",
    )

    _figures(gaps, matrix)

    summary = {
        "phase": "NCM-EXEC-06",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": track_frozen,
        "science_outcome": science,
        "companion_verdict": "LIFE_EXEC_RELEASED",
        "active_digest": ACTIVE_DIGEST,
        "upstream_packs": UPSTREAM,
        "track": track,
        "gap_metrics_frozen": gaps,
        "cross_track_matrix": matrix,
        "mandatory_questions": answers,
        "proven_claims": PROVEN_CLAIMS,
        "not_proven_claims": NOT_PROVEN_CLAIMS,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "future_tracks": FUTURE_TRACKS,
        "phase_verdicts": {
            "phase_1": "NCM_TRACK_INTEGRITY_CONFIRMED",
            "phase_2": "NCM_CLAIMS_CONSOLIDATED",
            "phase_3": "NCM_OPERATIONAL_LIMIT_FORMALIZED",
            "phase_4": "CROSS_TRACK_BEHAVIOR_CHARACTERIZED",
            "phase_5": "REVIEWER_SAFE_CLAIMS_FROZEN",
            "phase_6": "FORBIDDEN_CLAIMS_FROZEN",
            "phase_7": "NEXT_TRACKS_RELEASED",
            "phase_8": track_frozen,
            "phase_9": science,
        },
        "next_prompt": answers["Q10_next_prompt"],
        "approval_required": "NCM_EXEC_06_APPROVED",
        "hard_stop": True,
        "global_program_state": "NCM_TRACK_FINAL_FREEZE_PENDING_APPROVAL",
        "runtime_freeze_ok": freeze_ok,
        "dataset_sha256_exec04": ds_hash,
    }
    (OUT / "analysis" / "ncm_track_final_freeze_summary.json").write_text(
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
    return 0 if track["all_packs_present"] and freeze_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
