#!/usr/bin/env python3
"""CORE-EXEC-05: Core operational contention design (UPF-first, design-only)."""

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
REFS = {
    "core04": ROOT / "evidencias_trisla_core_exec_04_core_causality_runtime_requirements_20260518T003317Z",
    "core03": ROOT / "evidencias_trisla_core_exec_03_core_causality_gap_analysis_20260518T002934Z",
    "nad15": ROOT / "evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z",
}

FINAL_VERDICT = "CORE_OPERATIONAL_CONTENTION_DESIGN_READY"

# Blueprint: mechanism → metrics → risk → reviewer → dependencies
MECHANISMS: List[Dict[str, str]] = [
    {
        "id": "MEC-UPF-01",
        "mechanism": "Multi-tenant sustained iperf through UPF data path (N tenants, staggered)",
        "metrics_expected": "UPF container_cpu↑, core.cpu_utilization↑, throughput_mbps↑, resource_pressure↑",
        "operational_risk": "MEDIUM_RISK",
        "reviewer_safety": "SAFE",
        "runtime_dependencies": "rantester/iperf; PRB guards; no formula change",
        "tier": "PRIMARY",
    },
    {
        "id": "MEC-UPF-02",
        "mechanism": "UPF queue / GTP user-plane saturation via concurrent UDP/TCP flows",
        "metrics_expected": "UPF memory_working_set↑, packet processing latency proxy",
        "operational_risk": "HIGH_RISK",
        "reviewer_safety": "PARTIAL",
        "runtime_dependencies": "NF-scoped PromQL; pod stability monitoring",
        "tier": "PRIMARY",
    },
    {
        "id": "MEC-UPF-03",
        "mechanism": "Bitrate ladder calibration (low→mid→target) with Core pressure probe",
        "metrics_expected": "Monotonic core.cpu vs bitrate in PRB-bounded corridor",
        "operational_risk": "LOW_RISK",
        "reviewer_safety": "SAFE",
        "runtime_dependencies": "NAD LIMINAL-03 ladder pattern; pressure_guard/feasibility_guard",
        "tier": "PRIMARY",
    },
    {
        "id": "MEC-SESS-01",
        "mechanism": "Concurrent PDU/session establishment load (SMF-adjacent)",
        "metrics_expected": "SMF cpu↑, session count metrics",
        "operational_risk": "HIGH_RISK",
        "reviewer_safety": "PARTIAL",
        "runtime_dependencies": "session generator; not primary path",
        "tier": "SECONDARY",
    },
    {
        "id": "MEC-AMF-01",
        "mechanism": "AMF registration / attach storm",
        "metrics_expected": "AMF cpu↑, attach rate",
        "operational_risk": "HIGH_RISK",
        "reviewer_safety": "PARTIAL",
        "runtime_dependencies": "UE simulator; control-plane instability risk",
        "tier": "FUTURE",
    },
    {
        "id": "MEC-PFCP-01",
        "mechanism": "PFCP/N4 signaling pressure",
        "metrics_expected": "PFCP message rate, SMF/UPF coupling metrics",
        "operational_risk": "HIGH_RISK",
        "reviewer_safety": "FORBIDDEN",
        "runtime_dependencies": "exporter not present on frozen digest",
        "tier": "FUTURE",
    },
    {
        "id": "MEC-FORB-01",
        "mechanism": "Synthetic telemetry / fake core.cpu injection",
        "metrics_expected": "N/A",
        "operational_risk": "HIGH_RISK",
        "reviewer_safety": "FORBIDDEN",
        "runtime_dependencies": "none",
        "tier": "FORBIDDEN",
    },
    {
        "id": "MEC-FORB-02",
        "mechanism": "Weaken PRB hard-gate to allow Core-only crossings",
        "metrics_expected": "N/A",
        "operational_risk": "HIGH_RISK",
        "reviewer_safety": "FORBIDDEN",
        "runtime_dependencies": "none",
        "tier": "FORBIDDEN",
    },
]

NF_COMPARISON = [
    {"nf": "UPF", "data_plane": "yes", "existing_load_tool": "iperf (NAD)", "telemetry_path": "partial", "prb_coupling": "low", "score": 9},
    {"nf": "AMF", "data_plane": "no", "existing_load_tool": "none", "telemetry_path": "no", "prb_coupling": "low", "score": 4},
    {"nf": "SMF", "data_plane": "no", "existing_load_tool": "none", "telemetry_path": "no", "prb_coupling": "low", "score": 5},
    {"nf": "PFCP/N4", "data_plane": "control", "existing_load_tool": "none", "telemetry_path": "no", "prb_coupling": "low", "score": 3},
]

ENVELOPE_DESIGN = {
    "target_pressure_min": 0.30,
    "target_feasibility_max": 0.55,
    "nad_observed_pressure_max": 0.11,
    "design_ladder_mbps": ["20M", "24M", "28M", "32M"],
    "concurrent_tenants": 2,
    "stagger_s": 3,
    "prb_corridor_pct": [18, 24],
    "prb_hard_abort_pct": 24.0,
    "warmup_s": 120,
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
        "Q1_why_upf_first": [
            "User-plane load already exercised in NAD (iperf) without control-plane redesign",
            "Lowest PRB coupling vs RAN stress paths",
            "Direct path to UPF container metrics (REQ-CONT-01)",
            "Reviewer can attribute pressure to measurable traffic, not synthetic labels",
        ],
        "Q2_operational_mechanisms": [m["id"] for m in MECHANISMS if m["tier"] == "PRIMARY"],
        "Q3_runtime_supports": {
            "throughput_contention": True,
            "session_contention": False,
            "queue_contention": "partial_design_only",
            "pfcp_pressure": False,
        },
        "Q4_lowest_regression_risk": "MEC-UPF-03 (calibration ladder + guards)",
        "Q5_inv_prb_preservation": "PRB hard-gate first; abort if PRB>24%; score_mode only in 18-24% corridor",
        "Q6_avoid_fake_pressure": "Probe real snapshot before triplet; reject if pressure/feasibility guards fail (NAD LIMINAL-03 pattern)",
        "Q7_metrics_must_rise": [
            "telemetry_snapshot.core.cpu_utilization",
            "container_cpu_usage_seconds_total{upf}",
            "resource_pressure (derived)",
            "optional: throughput_mbps (summary PromQL)",
        ],
        "Q8_forbidden": [m["id"] for m in MECHANISMS if m["tier"] == "FORBIDDEN"],
        "Q9_envelope_sufficient": ENVELOPE_DESIGN,
        "Q10_roadmap": [
            "CORE-EXEC-06: runtime control implementation (scripts only)",
            "CORE-EXEC-07+: validation campaigns",
            "NCM-EXEC: operational contention track",
            "Then core_goodness + causal proof (REQ-CAU-01)",
        ],
    }


def _blueprint_md() -> str:
    rows = "\n".join(
        f"| {m['id']} | {m['mechanism'][:45]}… | {m['metrics_expected'][:40]}… | "
        f"{m['operational_risk']} | {m['reviewer_safety']} | {m['runtime_dependencies'][:35]}… |"
        for m in MECHANISMS
        if m["tier"] != "FORBIDDEN"
    )
    return (
        "| ID | Mechanism | Metrics expected | Risk | Reviewer | Dependencies |\n"
        "|----|-----------|------------------|------|----------|-------------|\n" + rows
    )


def _figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.text(0.5, 0.85, "UE / iperf tenants", ha="center", fontsize=10, bbox=dict(boxstyle="round", fc="#3498db"))
    ax.annotate("", xy=(0.5, 0.65), xytext=(0.5, 0.78), arrowprops=dict(arrowstyle="->"))
    ax.text(0.5, 0.55, "UPF (user plane)", ha="center", fontsize=11, bbox=dict(boxstyle="round", fc="#e67e22"))
    ax.annotate("", xy=(0.5, 0.35), xytext=(0.5, 0.48), arrowprops=dict(arrowstyle="->"))
    ax.text(0.5, 0.25, "Prometheus → snapshot.core", ha="center", fontsize=9, bbox=dict(boxstyle="round", fc="#9b59b6"))
    ax.annotate("", xy=(0.5, 0.08), xytext=(0.5, 0.18), arrowprops=dict(arrowstyle="->"))
    ax.text(0.5, 0.02, "pressure / feasibility → DE", ha="center", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("UPF-first architecture path")
    fig.savefig(fd / "upf_first_architecture_path.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    ids = [m["id"].replace("MEC-", "") for m in MECHANISMS if m["tier"] in ("PRIMARY", "SECONDARY")]
    risk_map = {"LOW_RISK": 0.3, "MEDIUM_RISK": 0.6, "HIGH_RISK": 0.9}
    vals = [risk_map.get(m["operational_risk"], 0.5) for m in MECHANISMS if m["tier"] in ("PRIMARY", "SECONDARY")]
    ax.barh(ids, vals, color="#16a085")
    ax.set_xlim(0, 1)
    ax.set_title("Core contention mechanism map")
    fig.savefig(fd / "core_contention_mechanism_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    levels = ["Traffic\n(UPF)", "Core CPU\nin pressure", "feasibility", "headroom", "score"]
    vals = [1.0, 0.3, 0.15, 0.12, 0.08]
    ax.barh(levels, vals, color=["#e67e22", "#9b59b6", "#f1c40f", "#f39c12", "#2ecc71"])
    ax.set_xlim(0, 1.1)
    ax.set_title("Pressure generation hierarchy (damping)")
    fig.savefig(fd / "pressure_generation_hierarchy.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    order = ["HARD_PRB", "PRB corridor", "Core load", "score_mode", "merge"]
    ax.bar(range(len(order)), [1, 0.9, 0.5, 0.4, 0.2], color="#c0392b")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=20, ha="right")
    ax.set_title("PRB preservation arbitration")
    fig.savefig(fd / "prb_preservation_arbitration.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    steps = [
        "CORE-EXEC-05 DESIGN (this)",
        "→ EXEC-06 runtime controls",
        "→ EXEC-07+ campaigns",
        "→ NCM-EXEC contention",
        "→ core_goodness + causal proof",
    ]
    for i, s in enumerate(steps):
        ax.text(0.05, 0.9 - i * 0.15, s, fontsize=10, family="monospace")
    ax.set_title("Core future contention roadmap")
    fig.savefig(fd / "core_future_contention_roadmap.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_upf_first_justification",
        "phase_2_operational_contention_mechanisms",
        "phase_3_runtime_contention_feasibility",
        "phase_4_pressure_generation_paths",
        "phase_5_prb_preservation_model",
        "phase_6_reviewer_safe_boundaries",
        "phase_7_future_contention_roadmap",
        "phase_8_forbidden_contention_paths",
        "phase_9_final_contention_design_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    answers = _mandatory_answers()
    nf_rows = "\n".join(
        f"| {r['nf']} | {r['data_plane']} | {r['existing_load_tool']} | {r['telemetry_path']} | {r['prb_coupling']} | {r['score']}/10 |"
        for r in NF_COMPARISON
    )

    (OUT / "phase_1_upf_first_justification/UPF_FIRST_JUSTIFICATION.md").write_text(
        f"# Phase 1 — UPF-First Justification\n\n**Verdict:** UPF_FIRST_PATH_JUSTIFIED\n\n"
        f"## NF comparison\n\n| NF | Data plane | Load tool today | Telemetry | PRB coupling | Score |\n"
        f"|----|------------|-----------------|-----------|--------------|-------|\n{nf_rows}\n\n"
        f"## Q1 rationale\n\n{chr(10).join('- ' + x for x in answers['Q1_why_upf_first'])}\n",
        encoding="utf-8",
    )

    (OUT / "phase_2_operational_contention_mechanisms/OPERATIONAL_CONTENTION_MECHANISMS.md").write_text(
        f"# Phase 2 — Operational Contention Mechanisms\n\n**Verdict:** OPERATIONAL_CONTENTION_MECHANISMS_DEFINED\n\n"
        f"{_blueprint_md()}\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_runtime_contention_feasibility/RUNTIME_CONTENTION_FEASIBILITY.md").write_text(
        f"""# Phase 3 — Runtime Contention Feasibility

**Verdict:** RUNTIME_CONTENTION_FEASIBILITY_DEFINED

## Q3 — Runtime supports (frozen digest)

| Capability | Supported |
|------------|-----------|
| Throughput contention (iperf) | **Yes** — NAD-proven |
| Session contention | **No** — design only |
| Queue contention | **Partial** — requires NF metrics |
| PFCP pressure | **No** |

**Stability constraints:** PRB abort ≤24%; pod restart monitoring; 120s warmup; no K8s limit changes in design phase.
""",
        encoding="utf-8",
    )

    (OUT / "phase_4_pressure_generation_paths/PRESSURE_GENERATION_PATHS.md").write_text(
        f"""# Phase 4 — Pressure Generation Paths

**Verdict:** PRESSURE_GENERATION_PATHS_DEFINED

## Target envelope (Q9)

- `resource_pressure` ≥ {ENVELOPE_DESIGN['target_pressure_min']}
- `feasibility` ≤ {ENVELOPE_DESIGN['target_feasibility_max']}
- PRB in corridor {ENVELOPE_DESIGN['prb_corridor_pct']}% (hard abort {ENVELOPE_DESIGN['prb_hard_abort_pct']}%)

## Design ladder (offline)

Bitrate steps: {', '.join(ENVELOPE_DESIGN['design_ladder_mbps'])} with {ENVELOPE_DESIGN['concurrent_tenants']} tenants, {ENVELOPE_DESIGN['stagger_s']}s stagger.

**Path:** UPF traffic → core.cpu_utilization → pressure v1 (w_cpu=0.3) → feasibility → headroom → score (indirect until core_goodness).

**Gap from NAD:** pressure max ~{ENVELOPE_DESIGN['nad_observed_pressure_max']} — ladder must push Core CPU norm without exceeding PRB hard gate.
""",
        encoding="utf-8",
    )

    (OUT / "phase_5_prb_preservation_model/PRB_PRESERVATION_MODEL.md").write_text(
        """# Phase 5 — PRB Preservation Model

**Verdict:** PRB_PRESERVATION_MODEL_FROZEN

## Arbitration order

1. HARD_PRB_REJECT / HARD_PRB_RENEGOTIATE (engine.py)
2. PRB corridor enforcement (18–24% for attribution stratum)
3. Core contention load (UPF iperf tenants)
4. Pre-submit probe: pressure ≥0.30 AND feasibility ≤0.55 (else skip rep)
5. score_mode decision
6. slice_multidomain severity merge (cannot weaken PRB reject)

**Bounded Core:** contention raises pressure only; does not bypass gates or inflate scores synthetically.
""",
        encoding="utf-8",
    )

    (OUT / "phase_6_reviewer_safe_boundaries/REVIEWER_SAFE_BOUNDARIES.md").write_text(
        """# Phase 6 — Reviewer-Safe Boundaries

**Verdict:** REVIEWER_SAFE_CONTENTION_BOUNDARIES_DEFINED

| Class | Mechanisms |
|-------|------------|
| **SAFE** | MEC-UPF-01, MEC-UPF-03 |
| **PARTIAL** | MEC-UPF-02, MEC-SESS-01, MEC-AMF-01 (needs NF telemetry + stability proof) |
| **FORBIDDEN** | MEC-FORB-01, MEC-FORB-02, MEC-PFCP-01 (no observability) |
""",
        encoding="utf-8",
    )

    (OUT / "phase_7_future_contention_roadmap/FUTURE_CONTENTION_ROADMAP.md").write_text(
        f"""# Phase 7 — Future Contention Roadmap

**Verdict:** FUTURE_CONTENTION_ROADMAP_DEFINED

{chr(10).join('- ' + x for x in answers['Q10_roadmap'])}

**NCM-EXEC** may run parallel operational campaigns once EXEC-06 controls exist.
""",
        encoding="utf-8",
    )

    (OUT / "phase_8_forbidden_contention_paths/FORBIDDEN_CONTENTION_PATHS.md").write_text(
        f"""# Phase 8 — Forbidden Contention Paths

**Verdict:** FORBIDDEN_CONTENTION_PATHS_FROZEN

{chr(10).join('- ' + x for x in answers['Q8_forbidden'])}

Also forbidden: K8s sabotage, artificial packet loss, threshold manipulation, fake feasibility, orchestration hacks.
""",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_contention_design_freeze/FINAL_CONTENTION_DESIGN_FREEZE.md").write_text(
        f"# Phase 9 — Final Contention Design Freeze\n\n# **{FINAL_VERDICT}**\n\n"
        f"Primary mechanism: **MEC-UPF-01 + MEC-UPF-03** (sustained multi-tenant iperf + calibration ladder).\n\n"
        f"Digest frozen: `{ACTIVE_DIGEST}`\n",
        encoding="utf-8",
    )

    (OUT / "analysis/CONTENTION_BLUEPRINT.md").write_text(
        f"# Core Operational Contention Blueprint\n\n{_blueprint_md()}\n", encoding="utf-8"
    )

    _figures()

    summary = {
        "phase": "CORE-EXEC-05",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": FINAL_VERDICT,
        "design_only": True,
        "active_digest": ACTIVE_DIGEST,
        "decision_engine_image": _de_image(),
        "references": {k: str(v) for k, v in REFS.items()},
        "mechanisms": MECHANISMS,
        "nf_comparison": NF_COMPARISON,
        "envelope_design": ENVELOPE_DESIGN,
        "mandatory_answers": answers,
        "phase_verdicts": {
            "phase1": "UPF_FIRST_PATH_JUSTIFIED",
            "phase2": "OPERATIONAL_CONTENTION_MECHANISMS_DEFINED",
            "phase3": "RUNTIME_CONTENTION_FEASIBILITY_DEFINED",
            "phase4": "PRESSURE_GENERATION_PATHS_DEFINED",
            "phase5": "PRB_PRESERVATION_MODEL_FROZEN",
            "phase6": "REVIEWER_SAFE_CONTENTION_BOUNDARIES_DEFINED",
            "phase7": "FUTURE_CONTENTION_ROADMAP_DEFINED",
            "phase8": "FORBIDDEN_CONTENTION_PATHS_FROZEN",
            "phase9": FINAL_VERDICT,
        },
        "next_prompt": "PROMPT_TRISLA_CORE_EXEC_06_CORE_CONTENTION_RUNTIME_CONTROL_IMPLEMENTATION_V1",
        "approval_required": "CORE_EXEC_05_APPROVED",
        "hard_stop": True,
    }
    (OUT / "analysis/core_operational_contention_design_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (OUT / "analysis/contention_mechanisms.json").write_text(
        json.dumps(MECHANISMS, indent=2), encoding="utf-8"
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
