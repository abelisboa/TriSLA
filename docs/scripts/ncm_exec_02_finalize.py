#!/usr/bin/env python3
"""NCM-EXEC-02: Operational contention design (ORCH-01 + UPF-MF-01 companion, design-only)."""

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
NCM01 = ROOT / "evidencias_trisla_ncm_exec_01_operational_contention_mechanism_audit_20260518T012747Z"

FINAL_VERDICT = "NCM_OPERATIONAL_CONTENTION_DESIGN_READY"

# Frozen targets (no threshold edits)
PRESSURE_MIN = 0.30
FEASIBILITY_MAX = 0.55
PRB_LO, PRB_HI, PRB_ABORT = 18.0, 24.0, 24.0
HARD_GATE_STOP_FRAC = 0.25

CAMPAIGN_BLUEPRINT = {
    "campaign_id": "NCM-ORCH-01",
    "mode": "live_planned",
    "primary_mechanism": "NCM-ORCH-01",
    "companion_mechanism": "NCM-UPF-MF-01",
    "tenants": 4,
    "concurrency_in_flight": 4,
    "reps_per_epoch": 12,
    "epochs": 3,
    "stagger_s": 2.0,
    "warmup_s": 60,
    "slice_order": ["URLLC", "eMBB", "mMTC"],
    "triplet_mode": True,
    "upf_companion": {
        "enabled": True,
        "flows": 2,
        "bitrate_fixed": "24M",
        "ladder_forbidden": True,
        "role": "companion_only",
    },
    "stop_rules": {
        "hard_gate_rate_max": HARD_GATE_STOP_FRAC,
        "prb_hard_abort_pct": PRB_ABORT,
        "prb_soft_abort_pct": 23.5,
        "consecutive_orch_failures_max": 5,
    },
    "expected_submits": 144,
    "evidence_outputs": [
        "dataset/raw/all_rows.json",
        "dataset/enriched/ncm_orch_01_dataset.csv",
        "orchestration_evidence.json",
        "campaign_execution_stats.json",
    ],
}

FORBIDDEN_PATHS = [
    "Synthetic telemetry or injected resource_pressure/feasibility",
    "Post-hoc threshold, gate, or weight changes",
    "PRB hard-gate weakening or bypass",
    "Bitrate ladder as primary mechanism (NCM-UPF-LAD-01 frozen)",
    "PFCP/N4 storm without observability (NCM-PFCP-01)",
    "AMF attach storm without stability controls (NCM-AMF-01 deferred)",
    "Kubernetes resource sabotage (CPU limits, pod kill)",
    "Artificial packet loss or tc shaping not in SSOT",
    "Fake admission drift labels or band crossings",
]

CLAIM_MATRIX = {
    "ALLOWED": [
        "NCM operational contention design frozen under active digest",
        "NCM-ORCH-01: real concurrent SLA submits through frozen portal→DE pipeline",
        "NCM-UPF-MF-01: companion multi-flow UPF load at fixed bitrate (not ladder-primary)",
        "Hypothesis: orchestration concurrency elevates pipeline latency and observable pressure",
        "INV-PRB preservation design with hard_gate sovereignty",
    ],
    "PARTIAL": [
        "Core causal admission (requires future campaign evidence)",
        "Balanced multidomain contention",
        "Normative 3GPP/GSMA compliance claims",
    ],
    "FORBIDDEN": [
        "Causal Core admission before NCM campaign execution",
        "Claiming pressure≥0.30 from design documents alone",
        "Ladder-only escalation as sufficient mechanism",
    ],
}


def answer_questions() -> Dict[str, Any]:
    return {
        "Q1_orch_reviewer_safe": (
            "Concurrent real HTTP POST /api/v1/sla/submit per tenant with frozen templates; "
            "record http_elapsed_s, metadata.sla_metrics, telemetry_snapshot; "
            "equivalent-state epochs; no synthetic labels; guards abort on PRB/pressure/feasibility."
        ),
        "Q2_combine_orch_upf_without_inv_prb": (
            "ORCH-primary: contention on decision path; UPF-MF companion at fixed 24M with "
            "max 2 flows and PRB pre-triplet validation; abort regime if PRB≥24%; "
            "score_mode analysis only inside 18–24% corridor; companion disabled if PRB proxy unstable."
        ),
        "Q3_metrics_must_rise": [
            "http_elapsed_s (pipeline latency)",
            "portal/DE processing queue proxy (concurrent in-flight count)",
            "resource_pressure (sla_metrics / normalized_inputs)",
            "feasibility_score",
            "telemetry_snapshot.core.cpu_utilization",
            "telemetry_snapshot.transport.rtt_ms",
            "optional: collector elapsed_ms",
        ],
        "Q4_measure_pressure_feasibility_latency": {
            "pressure": "metadata.sla_metrics.resource_pressure or normalized_inputs.resource_pressure",
            "feasibility": "metadata.sla_metrics.feasibility_score",
            "latency": "HTTP wall time submit→response; span orch_submit_latency_ms in evidence JSON",
            "prb": "ran.prb_utilization in snapshot + proxy_prb_at_submit",
        },
        "Q5_same_or_equivalent_state": (
            "equivalent_state_id = {digest_prefix}-{epoch}-{rep:03d}; "
            "triplet URLLC→eMBB→mMTC within 1.5s pause; "
            "concurrent tenants use staggered starts but share frozen template_id set and score_mode path."
        ),
        "Q6_avoid_artificial_load_test": (
            "Every submit is full SLA intent through production API; success criteria include "
            "telemetry_snapshot presence and decision_mode score_mode; "
            "reject epochs with >50% HTTP errors or missing snapshots."
        ),
        "Q7_blocked_mechanisms": [
            "NCM-PFCP-01",
            "NCM-FORB-01",
            "NCM-UPF-LAD-01",
            "NCM-AMF-01",
            "NCM-SESS-01 (until NCM-EXEC-05+)",
        ],
        "Q8_campaign_size": {
            "minimum": "3 epochs × 12 reps × 4 slices triplet = 144 score-path submits",
            "rationale": "Comparable to CORE-CONTENTION-01 attempt depth with orchestration dimension",
        },
        "Q9_success_failure_block": {
            "success": "pressure_max≥0.30 AND feasibility_min≤0.55 AND prb_frac_18_24≥0.5 AND hard_gate_rate≤0.25",
            "partial": "either target met with INV-PRB preserved",
            "blocked": "hard_gate_rate>0.25 OR prb_abort OR >50% orchestration HTTP failures",
            "failure": "no targets met but valid negative campaign",
        },
        "Q10_next_phase": "PROMPT_TRISLA_NCM_EXEC_03_OPERATIONAL_CONTENTION_RUNTIME_CONTROL_IMPLEMENTATION_V1",
    }


def _figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    boxes = [
        (0.05, 0.55, "Portal\n/api/v1/sla/submit"),
        (0.28, 0.55, "SEM-CSMF"),
        (0.48, 0.55, "Decision\nEngine"),
        (0.68, 0.55, "NASP\nAdapter"),
        (0.85, 0.55, "SLA-Agent"),
    ]
    for x, y, t in boxes:
        ax.add_patch(mpatches.FancyBboxPatch((x, y), 0.16, 0.25, boxstyle="round", fc="#d6eaf8", ec="black"))
        ax.text(x + 0.08, y + 0.12, t, ha="center", va="center", fontsize=7)
    for i in range(len(boxes) - 1):
        ax.annotate("", xy=(boxes[i + 1][0], 0.67), xytext=(boxes[i][0] + 0.16, 0.67), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(0.4, 0.25, "NCM-ORCH-01: N concurrent tenants → pipeline contention", ha="center", fontsize=9, style="italic")
    ax.text(0.4, 0.12, "Companion: NCM-UPF-MF-01 (fixed 24M, ≤2 flows)", ha="center", fontsize=8, color="#e67e22")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("NCM orchestration contention architecture")
    fig.savefig(fd / "ncm_orchestration_contention_architecture.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 4))
    t = np.linspace(0, 20, 100)
    for i in range(4):
        ax.plot(t, (t - i * 2).clip(0, 15), label=f"tenant-{i}")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("in-flight")
    ax.set_title("Concurrent tenant execution flow (stagger=2s)")
    ax.legend(fontsize=7, ncol=4)
    fig.savefig(fd / "concurrent_tenant_execution_flow.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 5))
    guards = ["pressure≥0.30", "feas≤0.55", "PRB 18–24%", "hard_gate≤25%", "snapshot OK"]
    y = np.arange(len(guards))
    ax.barh(y, [1, 1, 1, 1, 1], color="#27ae60")
    ax.set_yticks(y)
    ax.set_yticklabels(guards)
    ax.set_xlim(0, 1.2)
    ax.set_title("Pressure / feasibility guard map")
    fig.savefig(fd / "pressure_feasibility_guard_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.axvspan(PRB_LO, PRB_HI, alpha=0.3, color="green")
    ax.axvline(PRB_ABORT, color="red", ls="--", label="abort")
    ax.bar(["ORCH-only", "ORCH+UPF-MF"], [0.15, 0.35], color=["#3498db", "#e67e22"])
    ax.set_ylabel("PRB leakage risk (qualitative)")
    ax.set_title("PRB preservation strategy")
    ax.legend(fontsize=7)
    fig.savefig(fd / "prb_preservation_strategy.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    steps = [
        "Warmup 60s",
        "Optional UPF-MF start",
        "Epoch loop",
        "Concurrent triplet submits",
        "Guard check",
        "Evidence write",
        "Stop rule eval",
    ]
    ax.plot(range(len(steps)), [1] * len(steps), "s-", color="#8e44ad", markersize=8)
    for i, s in enumerate(steps):
        ax.text(i, 1.06, s, ha="center", fontsize=7, rotation=20)
    ax.set_title("NCM-ORCH-01 campaign blueprint")
    ax.axis("off")
    fig.savefig(fd / "ncm_campaign_blueprint.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_design_scope",
        "phase_2_orchestration_contention_design",
        "phase_3_upf_multiflow_companion_design",
        "phase_4_metric_and_guard_design",
        "phase_5_prb_preservation_design",
        "phase_6_campaign_blueprint",
        "phase_7_reviewer_safe_claims",
        "phase_8_forbidden_paths",
        "phase_9_final_design_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    answers = answer_questions()
    bp = CAMPAIGN_BLUEPRINT

    de_img = ""
    freeze_ok = False
    try:
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
    except Exception:
        pass

    (OUT / "phase_1_design_scope" / "DESIGN_SCOPE.md").write_text(
        "# Phase 1 — Design Scope\n\n**Verdict:** NCM_DESIGN_SCOPE_DEFINED\n\n"
        "## In scope\n"
        "- **NCM-ORCH-01** (primary): concurrent SLA orchestration contention\n"
        "- **NCM-UPF-MF-01** (companion): fixed-bitrate multi-flow UPF load\n"
        "- Guards, metrics, campaign blueprint for NCM-EXEC-03 implementation\n\n"
        "## Out of scope\n"
        "- Live campaign execution (NCM-EXEC-05+)\n"
        "- Formula/threshold/gate/weight changes\n"
        "- PFCP/AMF/session storms\n\n"
        f"Upstream: `{NCM01.name}`\nDigest: `{ACTIVE_DIGEST}`\n",
        encoding="utf-8",
    )

    (OUT / "phase_2_orchestration_contention_design" / "ORCHESTRATION_CONTENTION_DESIGN.md").write_text(
        "# Phase 2 — Orchestration Contention Design\n\n**Verdict:** NCM_ORCH_01_DESIGN_READY\n\n"
        "## NCM-ORCH-01\n\n"
        "### Mechanism\n"
        "- **API:** `POST {TRISLA_BACKEND_URL}/api/v1/sla/submit` (frozen portal path)\n"
        "- **Concurrency:** up to **4** in-flight submits across tenants\n"
        "- **Tenants:** `ncm-{epoch}-{rep}-{slice}-{slot}` unique intent_id\n"
        "- **Stagger:** **2.0s** between tenant slot starts within an epoch\n"
        "- **Triplet:** URLLC → eMBB → mMTC sequential with **1.5s** pause (reuse CORE barrier timing)\n"
        "- **Equivalent-state ID:** `ncm-{run_tag}-ep{epoch:02d}-rep{rep:03d}`\n\n"
        "### Observability per submit\n"
        "- `http_elapsed_s`, `decision_mode`, `decision_score`, `decision`\n"
        "- `metadata.sla_metrics.resource_pressure`, `feasibility_score`\n"
        "- `metadata.telemetry_snapshot` (ran, transport, core)\n"
        "- `orch_concurrent_in_flight` at submit time\n\n"
        "### Reviewer-safe constraints\n"
        f"- {answers['Q1_orch_reviewer_safe']}\n"
        f"- {answers['Q6_avoid_artificial_load_test']}\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_upf_multiflow_companion_design" / "UPF_MULTIFLOW_COMPANION_DESIGN.md").write_text(
        "# Phase 3 — UPF Multi-Flow Companion\n\n**Verdict:** NCM_UPF_MF_01_DESIGN_READY\n\n"
        "## NCM-UPF-MF-01 (companion only)\n\n"
        f"- **Flows:** {bp['upf_companion']['flows']} parallel iperf3 UDP clients (ueransim pod)\n"
        f"- **Bitrate:** fixed **{bp['upf_companion']['bitrate_fixed']}** — **no ladder**\n"
        "- **Role:** elevate transport RTT component of pressure_v1 without dominating campaign\n"
        "- **Start:** after orchestration warmup; stop before epoch teardown\n"
        "- **Block:** if `NCM-UPF-LAD-01` pattern detected (bitrate sweep as primary)\n\n"
        f"**Q2 combination:** {answers['Q2_combine_orch_upf_without_inv_prb']}\n",
        encoding="utf-8",
    )

    (OUT / "phase_4_metric_and_guard_design" / "METRIC_AND_GUARD_DESIGN.md").write_text(
        "# Phase 4 — Metric and Guard Design\n\n**Verdict:** NCM_METRIC_GUARD_DESIGN_READY\n\n"
        "| Guard | Threshold | Action |\n|-------|-----------|--------|\n"
        f"| pressure | ≥ {PRESSURE_MIN} (pre-triplet probe) | skip rep if below |\n"
        f"| feasibility | ≤ {FEASIBILITY_MAX} | skip rep if above |\n"
        f"| PRB corridor | {PRB_LO}–{PRB_HI}% | skip if outside |\n"
        f"| PRB hard | ≥ {PRB_ABORT}% | **abort regime** |\n"
        f"| hard_gate rate | > {HARD_GATE_STOP_FRAC} | stop campaign |\n"
        "| snapshot | required fields present | discard row |\n"
        "| orch HTTP | status 200 + JSON | retry once then skip |\n\n"
        f"**Q3:** {', '.join(answers['Q3_metrics_must_rise'])}\n\n"
        f"**Q4:** ```json\n{json.dumps(answers['Q4_measure_pressure_feasibility_latency'], indent=2)}\n```\n",
        encoding="utf-8",
    )

    (OUT / "phase_5_prb_preservation_design" / "PRB_PRESERVATION_DESIGN.md").write_text(
        "# Phase 5 — PRB Preservation\n\n**Verdict:** INV_PRB_PRESERVATION_DESIGN_READY\n\n"
        "- **Sovereignty:** `hard_prb_gate` unchanged; score_mode only when PRB < 25% reneg path\n"
        "- **Abort:** proxy PRB ≥ 24% → regime abort (reuse `prb_abort_check`)\n"
        "- **Separation:** orchestration effect rows tagged `contention_source=orch`; "
        "companion rows tagged `contention_source=upf_mf`\n"
        "- **Contamination:** epochs with >25% hard_gate submits discarded from primary analysis\n"
        "- **RAN decoupling:** do not attribute orch latency to PRB monotonicity claims\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_campaign_blueprint" / "CAMPAIGN_BLUEPRINT.md").write_text(
        "# Phase 6 — Campaign Blueprint\n\n**Verdict:** NCM_CAMPAIGN_BLUEPRINT_READY\n\n"
        f"```json\n{json.dumps(bp, indent=2)}\n```\n\n"
        f"**Q5:** {answers['Q5_same_or_equivalent_state']}\n\n"
        f"**Q8:** ```json\n{json.dumps(answers['Q8_campaign_size'], indent=2)}\n```\n\n"
        f"**Q9:** ```json\n{json.dumps(answers['Q9_success_failure_block'], indent=2)}\n```\n",
        encoding="utf-8",
    )

    claims_md = "# Phase 7 — Reviewer-Safe Claims\n\n**Verdict:** REVIEWER_SAFE_NCM_CLAIMS_DEFINED\n\n"
    for cat, items in CLAIM_MATRIX.items():
        claims_md += f"\n## {cat}\n\n" + "\n".join(f"- {i}" for i in items) + "\n"
    (OUT / "phase_7_reviewer_safe_claims" / "REVIEWER_SAFE_CLAIMS.md").write_text(claims_md, encoding="utf-8")

    (OUT / "phase_8_forbidden_paths" / "FORBIDDEN_PATHS.md").write_text(
        "# Phase 8 — Forbidden Paths\n\n**Verdict:** FORBIDDEN_NCM_PATHS_FROZEN\n\n"
        + "\n".join(f"- {p}" for p in FORBIDDEN_PATHS)
        + "\n\n"
        f"**Q7 blocked:** {answers['Q7_blocked_mechanisms']}\n",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_design_freeze" / "FINAL_DESIGN_FREEZE.md").write_text(
        f"# Phase 9 — Final Design Freeze\n\n# **{FINAL_VERDICT}**\n\n"
        f"Primary: **NCM-ORCH-01** · Companion: **NCM-UPF-MF-01**\n\n"
        f"Next: **{answers['Q10_next_phase']}**\n\n"
        f"```json\n{json.dumps(answers, indent=2)}\n```\n",
        encoding="utf-8",
    )

    (OUT / "analysis" / "ncm_design_blueprint.json").write_text(json.dumps(bp, indent=2), encoding="utf-8")

    _figures()

    summary = {
        "phase": "NCM-EXEC-02",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": FINAL_VERDICT,
        "active_digest": ACTIVE_DIGEST,
        "upstream_ncm01": str(NCM01.name),
        "campaign_blueprint": bp,
        "mandatory_questions": answers,
        "claim_matrix": CLAIM_MATRIX,
        "forbidden_paths": FORBIDDEN_PATHS,
        "phase_verdicts": {
            "phase_1": "NCM_DESIGN_SCOPE_DEFINED",
            "phase_2": "NCM_ORCH_01_DESIGN_READY",
            "phase_3": "NCM_UPF_MF_01_DESIGN_READY",
            "phase_4": "NCM_METRIC_GUARD_DESIGN_READY",
            "phase_5": "INV_PRB_PRESERVATION_DESIGN_READY",
            "phase_6": "NCM_CAMPAIGN_BLUEPRINT_READY",
            "phase_7": "REVIEWER_SAFE_NCM_CLAIMS_DEFINED",
            "phase_8": "FORBIDDEN_NCM_PATHS_FROZEN",
            "phase_9": FINAL_VERDICT,
        },
        "next_prompt": answers["Q10_next_phase"],
        "approval_required": "NCM_EXEC_02_APPROVED",
        "hard_stop": True,
        "global_program_state": "NCM_DESIGN_PENDING_APPROVAL",
        "runtime_freeze_ok": freeze_ok,
    }
    (OUT / "analysis" / "ncm_operational_contention_design_summary.json").write_text(
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
    return 0 if freeze_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
