#!/usr/bin/env python3
"""CORE-EXEC-04: Core causality runtime requirements (design-only)."""

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
    "core01": ROOT / "evidencias_trisla_core_exec_01_core_attribution_audit_20260518T002045Z",
    "core02": ROOT / "evidencias_trisla_core_exec_02_core_runtime_observability_mapping_20260518T002537Z",
    "core03": ROOT / "evidencias_trisla_core_exec_03_core_causality_gap_analysis_20260518T002934Z",
    "nad15": ROOT / "evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z",
}

FINAL_VERDICT = "CORE_CAUSALITY_RUNTIME_REQUIREMENTS_DEFINED"

# Requirement matrix: id, purpose, runtime_dependency, tier, risk, reviewer_impact
REQUIREMENTS: List[Dict[str, str]] = [
    {
        "id": "REQ-INF-01",
        "requirement": "NF-scoped PromQL for AMF/SMF/UPF CPU and memory",
        "purpose": "Core-informed telemetry with semantic unit contract",
        "runtime_dependency": "portal promql_ssot + collector; Prometheus series non-empty",
        "tier": "REQUIRED_FOR_INFORMED",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Enables observable Core at NF granularity",
    },
    {
        "id": "REQ-INF-02",
        "requirement": "telemetry_snapshot.core.* populated with validated % units",
        "purpose": "Propagation to DE context without unit mismatch",
        "runtime_dependency": "SEM-CSMF normalization (PHASE11 pattern)",
        "tier": "REQUIRED_FOR_INFORMED",
        "risk": "LOW_RISK",
        "reviewer_impact": "Removes false core_risk saturation",
    },
    {
        "id": "REQ-INF-03",
        "requirement": "Documented core field → consumer map (frozen SSOT)",
        "purpose": "Traceability for informed admission claims",
        "runtime_dependency": "docs/telemetry contract v2 only",
        "tier": "REQUIRED_FOR_INFORMED",
        "risk": "LOW_RISK",
        "reviewer_impact": "Supports CORE-EXEC-02 style mapping",
    },
    {
        "id": "REQ-CAU-01",
        "requirement": "Explicit core_goodness term in score_mode numerator (capped weight)",
        "purpose": "Direct Core propagation to decision_score",
        "runtime_dependency": "decision_score_mode.py change (future digest)",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Must not exceed PRB term weight cap",
    },
    {
        "id": "REQ-CAU-02",
        "requirement": "Operational Core contention mechanism (NCM track)",
        "purpose": "Real stress envelope — not synthetic",
        "runtime_dependency": "campaign controls; no formula-only change",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Evidence chain for causal attribution",
    },
    {
        "id": "REQ-CAU-03",
        "requirement": "Campaign evidence: admission band movement attributable to Core",
        "purpose": "Reviewer-safe causal proof",
        "runtime_dependency": "controlled experiment; same-state triplets",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Cannot claim without dataset",
    },
    {
        "id": "REQ-CAU-04",
        "requirement": "resource_pressure includes calibrated Core CPU+memory in DE v1 or v2 parity",
        "purpose": "Strengthen indirect path if direct term delayed",
        "runtime_dependency": "feasibility_runtime + portal parity",
        "tier": "OPTIONAL",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Insufficient alone per CORE-EXEC-03",
    },
    {
        "id": "REQ-CAU-05",
        "requirement": "Causal attribution audit pack (before/after Core stress)",
        "purpose": "Isolate Core from RAN/transport confounders",
        "runtime_dependency": "PRB-held stratum or PRB-bounded corridor",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "LOW_RISK",
        "reviewer_impact": "Mandatory for paper-grade claim",
    },
    {
        "id": "REQ-CONT-01",
        "requirement": "UPF throughput / queue saturation observable",
        "purpose": "UPF congestion path",
        "runtime_dependency": "iperf + UPF metrics; NCM design",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Primary contention candidate",
    },
    {
        "id": "REQ-CONT-02",
        "requirement": "AMF registration / attach rate stress",
        "purpose": "AMF saturation path",
        "runtime_dependency": "load tool + AMF metrics",
        "tier": "FUTURE_WORK",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Optional second contention axis",
    },
    {
        "id": "REQ-CONT-03",
        "requirement": "SMF session / PDU pressure",
        "purpose": "SMF bottleneck path",
        "runtime_dependency": "session generator + SMF metrics",
        "tier": "FUTURE_WORK",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Lifecycle coupling",
    },
    {
        "id": "REQ-CONT-04",
        "requirement": "PFCP/N4 congestion proxy",
        "purpose": "Control-plane bottleneck visibility",
        "runtime_dependency": "free5GC exporter or custom probe",
        "tier": "FUTURE_WORK",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Observability prerequisite",
    },
    {
        "id": "REQ-NF-01",
        "requirement": "Per-NF cpu_utilization and memory_utilization in snapshot",
        "purpose": "NF-level causal telemetry",
        "runtime_dependency": "TELEMETRY_PROMQL_CORE_* scoped",
        "tier": "REQUIRED_FOR_INFORMED",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Replaces aggregate process_*",
    },
    {
        "id": "REQ-NF-02",
        "requirement": "Instant-query validation before collector cutover",
        "purpose": "Non-empty series guarantee",
        "runtime_dependency": "validate_telemetry.py pattern",
        "tier": "REQUIRED_FOR_INFORMED",
        "risk": "LOW_RISK",
        "reviewer_impact": "Prevents INPUT_DEGRADED-only path",
    },
    {
        "id": "REQ-PRB-01",
        "requirement": "HARD_PRB gates remain first in decision pipeline",
        "purpose": "INV-PRB preservation",
        "runtime_dependency": "engine.py order unchanged",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "LOW_RISK",
        "reviewer_impact": "Non-negotiable invariant",
    },
    {
        "id": "REQ-PRB-02",
        "requirement": "core_goodness weight cap ≤ min(w_prb, w_transport) per slice profile",
        "purpose": "Bounded Core contribution",
        "runtime_dependency": "env DE_SLICE_WEIGHT_PROFILES",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Prevents Core dominance",
    },
    {
        "id": "REQ-PRB-03",
        "requirement": "Monotonicity: Core↑ → score↓ holding PRB/transport fixed",
        "purpose": "INV-MONO extension to Core stratum",
        "runtime_dependency": "campaign validation",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Scientific defensibility",
    },
    {
        "id": "REQ-ENV-01",
        "requirement": "Achieve resource_pressure ≥ 0.30 with PRB < hard_gate reneg threshold",
        "purpose": "NAD LIMINAL-03 unattained envelope",
        "runtime_dependency": "contention + calibration ladder",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Operational not mathematical",
    },
    {
        "id": "REQ-ENV-02",
        "requirement": "Achieve feasibility ≤ 0.55 under frozen viability formula",
        "purpose": "Liminal corridor for score_mode",
        "runtime_dependency": "ml_risk + pressure joint envelope",
        "tier": "REQUIRED_FOR_CAUSAL",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Paired with REQ-ENV-01",
    },
    {
        "id": "REQ-ENV-03",
        "requirement": "PRB corridor 18–24% optional stratum for Core-only attribution",
        "purpose": "Isolate Core effect from PRB hard reject",
        "runtime_dependency": "NAD-style campaign controls",
        "tier": "OPTIONAL",
        "risk": "MEDIUM_RISK",
        "reviewer_impact": "Inherited from NAD methodology",
    },
    {
        "id": "REQ-FORB-01",
        "requirement": "Weaken HARD_PRB or remove hard-gate precedence",
        "purpose": "N/A",
        "runtime_dependency": "none",
        "tier": "FORBIDDEN",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Breaks INV-PRB and SR-EXEC-09",
    },
    {
        "id": "REQ-FORB-02",
        "requirement": "Synthetic Core pressure / fake telemetry injection",
        "purpose": "N/A",
        "runtime_dependency": "none",
        "tier": "FORBIDDEN",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Reviewer-unsafe",
    },
    {
        "id": "REQ-FORB-03",
        "requirement": "Claim balanced multidomain without campaign proof",
        "purpose": "N/A",
        "runtime_dependency": "none",
        "tier": "FORBIDDEN",
        "risk": "HIGH_RISK",
        "reviewer_impact": "CORE-EXEC-03 boundary",
    },
    {
        "id": "REQ-FORB-04",
        "requirement": "Unbounded core_goodness weight",
        "purpose": "N/A",
        "runtime_dependency": "none",
        "tier": "FORBIDDEN",
        "risk": "HIGH_RISK",
        "reviewer_impact": "Core dominance forbidden",
    },
]

ENVELOPE_TARGETS = {
    "resource_pressure_min": 0.30,
    "feasibility_max": 0.55,
    "nad_observed_pressure_mean": 0.08,
    "nad_observed_pressure_max": 0.11,
    "nad_observed_feasibility_min": 0.67,
    "gap_to_pressure": 0.30 - 0.11,
    "gap_to_feasibility": 0.67 - 0.55,
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
        "Q1_minimal_core_informed": [
            "REQ-INF-01",
            "REQ-INF-02",
            "REQ-INF-03",
            "REQ-NF-01",
            "REQ-NF-02",
        ],
        "Q2_core_causal_requirements": [
            "REQ-CAU-01",
            "REQ-CAU-02",
            "REQ-CAU-03",
            "REQ-CAU-05",
            "REQ-PRB-01",
            "REQ-PRB-02",
            "REQ-ENV-01",
            "REQ-ENV-02",
        ],
        "Q3_operational_contention": "NCM track: UPF-primary (REQ-CONT-01); AMF/SMF/PFCP as FUTURE_WORK",
        "Q4_runtime_supports_today": {
            "amf_saturation": False,
            "smf_bottleneck": False,
            "upf_congestion": False,
            "pfcp_n4_overload": False,
        },
        "Q5_nf_telemetry_needed": [
            "AMF cpu/mem %",
            "SMF cpu/mem %",
            "UPF cpu/mem % + throughput",
            "PFCP/N4 proxy (future)",
        ],
        "Q6_minimal_core_goodness_path": "REQ-CAU-01 + REQ-PRB-02 + REQ-PRB-01 + NF telemetry + contention evidence",
        "Q7_inv_prb_preservation": "REQ-PRB-01 hard-gate first; REQ-PRB-02 weight cap; REQ-PRB-03 monotonicity tests",
        "Q8_operational_envelope": ENVELOPE_TARGETS,
        "Q9_dependencies": "Core causality depends on NCM contention; lifecycle/orchestration optional; multidomain-causal is FUTURE_WORK after Core-causal proof",
        "Q10_forbidden": ["REQ-FORB-01", "REQ-FORB-02", "REQ-FORB-03", "REQ-FORB-04"],
    }


def _matrix_md() -> str:
    rows = "\n".join(
        f"| {r['id']} | {r['requirement'][:50]}… | {r['purpose'][:40]}… | "
        f"{r['runtime_dependency'][:35]}… | {r['tier']} | {r['risk']} | {r['reviewer_impact'][:40]}… |"
        for r in REQUIREMENTS
    )
    header = (
        "| ID | Requirement | Purpose | Runtime dep | Tier | Risk | Reviewer impact |\n"
        "|----|-------------|---------|-------------|------|------|-----------------|"
    )
    return f"{header}\n{rows}"


def _figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    tiers = ["INFORMED", "CAUSAL", "OPTIONAL", "FUTURE", "FORBIDDEN"]
    counts = [
        sum(1 for r in REQUIREMENTS if "INFORMED" in r["tier"]),
        sum(1 for r in REQUIREMENTS if "CAUSAL" in r["tier"]),
        sum(1 for r in REQUIREMENTS if r["tier"] == "OPTIONAL"),
        sum(1 for r in REQUIREMENTS if r["tier"] == "FUTURE_WORK"),
        sum(1 for r in REQUIREMENTS if r["tier"] == "FORBIDDEN"),
    ]
    ax.bar(tiers, counts, color=["#3498db", "#e74c3c", "#f1c40f", "#9b59b6", "#c0392b"])
    ax.set_title("Core causality requirements map")
    fig.savefig(fd / "core_causality_requirements_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 4))
    chain = ["AMF", "SMF", "UPF", "Prom", "snapshot", "DE"]
    ax.plot(range(len(chain)), [1] * len(chain), "o-", lw=2)
    ax.set_xticks(range(len(chain)))
    ax.set_xticklabels(chain)
    ax.set_title("NF telemetry propagation chain (target state)")
    fig.savefig(fd / "nf_telemetry_propagation_chain.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    levels = ["HARD_PRB", "ran_prb_goodness", "core_goodness\n(capped)", "transport", "merge"]
    vals = [1.0, 0.9, 0.4, 0.3, 0.2]
    ax.barh(levels, vals, color=["#c0392b", "#e74c3c", "#9b59b6", "#3498db", "#95a5a6"])
    ax.set_xlim(0, 1.1)
    ax.set_title("PRB preservation hierarchy")
    fig.savefig(fd / "prb_preservation_hierarchy.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    phases = ["UPF\ncontention", "NF\ntelemetry", "core_\ngoodness", "Campaign", "Proof"]
    ax.bar(phases, [1, 0.8, 0.6, 0.9, 0.7], color="#16a085")
    ax.set_ylim(0, 1.2)
    ax.set_title("Operational contention roadmap (CORE-EXEC-05+)")
    fig.savefig(fd / "operational_contention_roadmap.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    deps = [
        "Core evolution dependencies",
        "observable → informed: REQ-INF*, REQ-NF*",
        "informed → causal: REQ-CAU-01,02,03 + NCM",
        "causal → multidomain: FUTURE_WORK",
        "INV-PRB gates all paths",
    ]
    for i, ln in enumerate(deps):
        ax.text(0.05, 0.9 - i * 0.16, ln, fontsize=10, family="monospace")
    ax.set_title("Core evolution dependency graph")
    fig.savefig(fd / "core_evolution_dependency_graph.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_core_informed_requirements",
        "phase_2_core_causal_requirements",
        "phase_3_operational_contention_requirements",
        "phase_4_nf_telemetry_requirements",
        "phase_5_prb_preservation_requirements",
        "phase_6_runtime_envelope_requirements",
        "phase_7_future_runtime_paths",
        "phase_8_forbidden_paths_and_risks",
        "phase_9_final_requirements_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    answers = _mandatory_answers()
    matrix = _matrix_md()

    (OUT / "phase_1_core_informed_requirements/CORE_INFORMED_REQUIREMENTS.md").write_text(
        f"# Phase 1 — Core-Informed Requirements\n\n**Verdict:** CORE_INFORMED_REQUIREMENTS_DEFINED\n\n"
        f"## Minimal set (Q1)\n\n{chr(10).join('- ' + x for x in answers['Q1_minimal_core_informed'])}\n\n"
        f"**Goal:** Core metrics visible, unit-correct, mapped to DE consumers — **without** claiming causal admission.\n",
        encoding="utf-8",
    )

    (OUT / "phase_2_core_causal_requirements/CORE_CAUSAL_REQUIREMENTS.md").write_text(
        f"# Phase 2 — Core-Causal Requirements\n\n**Verdict:** CORE_CAUSAL_REQUIREMENTS_DEFINED\n\n"
        f"## Minimal set (Q2)\n\n{chr(10).join('- ' + x for x in answers['Q2_core_causal_requirements'])}\n\n"
        f"**Proof chain:** contention → snapshot → score term → band movement → audit pack (REQ-CAU-03,05).\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_operational_contention_requirements/OPERATIONAL_CONTENTION_REQUIREMENTS.md").write_text(
        f"""# Phase 3 — Operational Contention Requirements

**Verdict:** OPERATIONAL_CONTENTION_REQUIREMENTS_DEFINED

## Q3 — Minimum mechanism

{answers['Q3_operational_contention']}

| Path | Tier | Notes |
|------|------|-------|
| UPF throughput / queue | REQUIRED_FOR_CAUSAL | Aligns with NAD iperf methodology; extend to Core NF metrics |
| AMF attach storm | FUTURE_WORK | REQ-CONT-02 |
| SMF PDU/session | FUTURE_WORK | REQ-CONT-03 |
| PFCP/N4 | FUTURE_WORK | REQ-CONT-04 |

**Constraint:** No synthetic pressure injection (REQ-FORB-02). Real runtime stress only.
""",
        encoding="utf-8",
    )

    (OUT / "phase_4_nf_telemetry_requirements/NF_TELEMETRY_REQUIREMENTS.md").write_text(
        f"""# Phase 4 — NF Telemetry Requirements

**Verdict:** NF_TELEMETRY_REQUIREMENTS_DEFINED

## Q5 — Required NF telemetry

{chr(10).join('- ' + x for x in answers['Q5_nf_telemetry_needed'])}

Replace default `process_*` aggregates with scoped `container_*` @ free5GC namespace (promql_ssot documented cutover).

**Validation:** REQ-NF-02 instant-query non-empty before collector switch.
""",
        encoding="utf-8",
    )

    (OUT / "phase_5_prb_preservation_requirements/PRB_PRESERVATION_REQUIREMENTS.md").write_text(
        f"""# Phase 5 — PRB Preservation Requirements

**Verdict:** PRB_PRESERVATION_REQUIREMENTS_DEFINED

## Q7 — INV-PRB with Core contribution

1. **Precedence:** HARD_PRB gates execute before score_mode (REQ-PRB-01).
2. **Cap:** `w_core_goodness ≤ min(w_prb, w_transport)` per slice (REQ-PRB-02).
3. **Monotonicity:** Core↑ → score↓ with PRB/transport fixed (REQ-PRB-03).
4. **Merge:** slice_multidomain may upgrade severity but never bypass PRB reject.

Core contribution is **bounded and subordinate** — not dominant.
""",
        encoding="utf-8",
    )

    (OUT / "phase_6_runtime_envelope_requirements/RUNTIME_ENVELOPE_REQUIREMENTS.md").write_text(
        f"""# Phase 6 — Runtime Envelope Requirements

**Verdict:** RUNTIME_ENVELOPE_REQUIREMENTS_DEFINED

## Q8 — Operational envelope (frozen targets)

| Metric | Target | NAD observed | Gap |
|--------|--------|--------------|-----|
| resource_pressure | ≥ {ENVELOPE_TARGETS['resource_pressure_min']} | max ~{ENVELOPE_TARGETS['nad_observed_pressure_max']} | ~{ENVELOPE_TARGETS['gap_to_pressure']:.2f} |
| feasibility | ≤ {ENVELOPE_TARGETS['feasibility_max']} | min ~{ENVELOPE_TARGETS['nad_observed_feasibility_min']} | ~{ENVELOPE_TARGETS['gap_to_feasibility']:.2f} |

Achieving both **without** PRB hard-gate abort requires contention design (CORE-EXEC-05) — not formula edits alone.
""",
        encoding="utf-8",
    )

    (OUT / "phase_7_future_runtime_paths/FUTURE_RUNTIME_PATHS.md").write_text(
        """# Phase 7 — Future Runtime Paths

**Verdict:** FUTURE_RUNTIME_PATHS_DEFINED

```
observable/contributive (today)
    → Core-informed (REQ-INF*, REQ-NF*)
    → Core-causal (REQ-CAU* + NCM contention + envelope)
    → multidomain-causal (FUTURE_WORK — after Core proof)
```

**Next track:** CORE-EXEC-05 operational contention **design** (no implementation in EXEC-04).
""",
        encoding="utf-8",
    )

    (OUT / "phase_8_forbidden_paths_and_risks/FORBIDDEN_PATHS_AND_RISKS.md").write_text(
        f"""# Phase 8 — Forbidden Paths and Risks

**Verdict:** FORBIDDEN_CORE_CAUSALITY_PATHS_FROZEN

## Q10 — Prohibited / reviewer-unsafe

{chr(10).join('- ' + x for x in answers['Q10_forbidden'])}

See REQ-FORB-* in requirements matrix. HIGH_RISK items require explicit governance review if ever proposed.
""",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_requirements_freeze/FINAL_REQUIREMENTS_FREEZE.md").write_text(
        f"# Phase 9 — Final Requirements Freeze\n\n# **{FINAL_VERDICT}**\n\n"
        f"Digest: `{ACTIVE_DIGEST}`\n\n"
        f"References: CORE-EXEC-01…03, NAD-EXEC-15\n\n"
        f"## Full requirements matrix\n\n{matrix}\n",
        encoding="utf-8",
    )

    (OUT / "analysis/REQUIREMENTS_MATRIX.md").write_text(
        f"# Core Causality Runtime Requirements Matrix\n\n{matrix}\n", encoding="utf-8"
    )

    _figures()

    summary = {
        "phase": "CORE-EXEC-04",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": FINAL_VERDICT,
        "design_only": True,
        "active_digest": ACTIVE_DIGEST,
        "decision_engine_image": _de_image(),
        "references": {k: str(v) for k, v in REFS.items()},
        "requirements": REQUIREMENTS,
        "envelope_targets": ENVELOPE_TARGETS,
        "mandatory_answers": answers,
        "phase_verdicts": {
            "phase1": "CORE_INFORMED_REQUIREMENTS_DEFINED",
            "phase2": "CORE_CAUSAL_REQUIREMENTS_DEFINED",
            "phase3": "OPERATIONAL_CONTENTION_REQUIREMENTS_DEFINED",
            "phase4": "NF_TELEMETRY_REQUIREMENTS_DEFINED",
            "phase5": "PRB_PRESERVATION_REQUIREMENTS_DEFINED",
            "phase6": "RUNTIME_ENVELOPE_REQUIREMENTS_DEFINED",
            "phase7": "FUTURE_RUNTIME_PATHS_DEFINED",
            "phase8": "FORBIDDEN_CORE_CAUSALITY_PATHS_FROZEN",
            "phase9": FINAL_VERDICT,
        },
        "next_prompt": "PROMPT_TRISLA_CORE_EXEC_05_CORE_OPERATIONAL_CONTENTION_DESIGN_V1",
        "approval_required": "CORE_EXEC_04_APPROVED",
        "hard_stop": True,
    }
    (OUT / "analysis/core_causality_runtime_requirements_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (OUT / "analysis/requirements_matrix.json").write_text(
        json.dumps(REQUIREMENTS, indent=2), encoding="utf-8"
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
