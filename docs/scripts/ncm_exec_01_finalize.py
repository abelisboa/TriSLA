#!/usr/bin/env python3
"""NCM-EXEC-01: Operational contention mechanism audit (analysis-only)."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

OUT = Path(os.environ["OUT"])
ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"
PRESSURE_REQ = 0.30
FEASIBILITY_REQ = 0.55

# Frozen upstream references
UPSTREAM = {
    "nad15": "evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z",
    "core09": "evidencias_trisla_core_exec_09_core_track_final_freeze_20260518T012114Z",
    "core07": "evidencias_trisla_core_exec_07_core_contention_campaign_execution_20260518T004652Z",
}

ENV_COMPONENTS = [
    {"domain": "CORE", "component": "free5GC (AMF/SMF/UPF/NRF/…)", "namespace": "ns-1274485", "status": "Running", "stress_tool": "indirect"},
    {"domain": "RAN", "component": "UERANSIM (gNB+UE)", "namespace": "ueransim", "status": "Running", "stress_tool": "iperf3 exec"},
    {"domain": "RAN", "component": "RANTester", "namespace": "ns-1274485", "status": "Running", "stress_tool": "chart workload"},
    {"domain": "TRANSPORT", "component": "ONOS", "namespace": "nasp-transport", "status": "Partial (1 Running, 1 Error)", "stress_tool": "intents (legacy)"},
    {"domain": "TRANSPORT", "component": "Mininet", "namespace": "nasp-transport", "status": "Error", "stress_tool": "unavailable"},
    {"domain": "TRISLA", "component": "decision-engine / portal-backend", "namespace": "trisla", "status": "Running", "stress_tool": "SLA HTTP submits"},
    {"domain": "TRISLA", "component": "nasp-adapter", "namespace": "trisla", "status": "Running", "stress_tool": "orchestration API"},
    {"domain": "TRISLA", "component": "ran-ue-upf-proxy", "namespace": "trisla", "status": "Running", "stress_tool": "PRB probe"},
    {"domain": "TRISLA", "component": "iperf3-client", "namespace": "trisla", "status": "Running", "stress_tool": "optional client"},
]

MECHANISMS: List[Dict[str, Any]] = [
    {
        "id": "NCM-UPF-MF-01",
        "name": "Multi-flow multi-tenant UPF user-plane saturation",
        "domains": ["transport", "core_upf"],
        "pressure_potential": "high",
        "feasibility_potential": "medium",
        "prb_coupling": "low_medium",
        "regression_risk": "medium",
        "reviewer_safety": "allowed",
        "env_ready": True,
        "notes": "Extends proven iperf path; not ladder-only; 2–4 parallel flows + stagger",
    },
    {
        "id": "NCM-ORCH-01",
        "name": "Concurrent guarded SLA submission orchestration",
        "domains": ["orchestration", "lifecycle"],
        "pressure_potential": "medium",
        "feasibility_potential": "medium",
        "prb_coupling": "low",
        "regression_risk": "low",
        "reviewer_safety": "allowed",
        "env_ready": True,
        "notes": "Portal→DE pipeline; telemetry lock; no NF storm",
    },
    {
        "id": "NCM-LC-01",
        "name": "Repeated slice lifecycle loops (SEM/portal intents)",
        "domains": ["lifecycle", "orchestration"],
        "pressure_potential": "medium",
        "feasibility_potential": "low_medium",
        "prb_coupling": "low",
        "regression_risk": "medium",
        "reviewer_safety": "partial",
        "env_ready": True,
        "notes": "Requires controlled lifecycle hooks; audit before load",
    },
    {
        "id": "NCM-SESS-01",
        "name": "PDU session churn (establish/release cycles)",
        "domains": ["core_smf", "lifecycle", "control_plane"],
        "pressure_potential": "high",
        "feasibility_potential": "high",
        "prb_coupling": "low",
        "regression_risk": "high",
        "reviewer_safety": "partial",
        "env_ready": "partial",
        "notes": "UERANSIM/rantester capable; stability risk; needs design phase",
    },
    {
        "id": "NCM-AMF-01",
        "name": "Registration / attach storm",
        "domains": ["core_amf", "control_plane"],
        "pressure_potential": "high",
        "feasibility_potential": "medium",
        "prb_coupling": "low",
        "regression_risk": "high",
        "reviewer_safety": "partial",
        "env_ready": "partial",
        "notes": "Can destabilize core; defer to NCM-EXEC-04+",
    },
    {
        "id": "NCM-PFCP-01",
        "name": "PFCP / N4 signaling storm",
        "domains": ["core_pfcp", "control_plane"],
        "pressure_potential": "high",
        "feasibility_potential": "unknown",
        "prb_coupling": "low",
        "regression_risk": "high",
        "reviewer_safety": "forbidden",
        "env_ready": False,
        "notes": "No PFCP rate exporter on frozen digest",
    },
    {
        "id": "NCM-UPF-LAD-01",
        "name": "Bitrate ladder only (20–32 Mbps)",
        "domains": ["transport"],
        "pressure_potential": "exhausted",
        "feasibility_potential": "exhausted",
        "prb_coupling": "medium",
        "regression_risk": "medium",
        "reviewer_safety": "forbidden_primary",
        "env_ready": True,
        "notes": "CORE-EXEC-07: p_max=0.264; frozen as insufficient alone",
    },
    {
        "id": "NCM-FORB-01",
        "name": "Synthetic telemetry / threshold / PRB weakening",
        "domains": [],
        "pressure_potential": "n/a",
        "feasibility_potential": "n/a",
        "prb_coupling": "n/a",
        "regression_risk": "critical",
        "reviewer_safety": "forbidden",
        "env_ready": False,
        "notes": "Absolute prohibition",
    },
]

ROADMAP = [
    ("NCM-EXEC-02", "Operational contention design (selected mechanisms)"),
    ("NCM-EXEC-03", "Runtime controls implementation (scripts only)"),
    ("NCM-EXEC-04", "Pre-campaign regression / guard self-test"),
    ("NCM-EXEC-05", "Live campaign NCM-CONTENTION-01"),
    ("NCM-EXEC-06", "Runtime validation & gap analysis"),
    ("NCM-EXEC-07", "Track freeze or NCM-EXEC-08 continuation decision"),
]

FIRST_AUTHORIZED = "NCM-ORCH-01"
FIRST_AUTHORIZED_RATIONALE = (
    "Lowest regression risk with direct TriSLA pipeline observability; elevates orchestration "
    "and concurrent decision-path load without control-plane storms. Pair with NCM-UPF-MF-01 "
    "in NCM-EXEC-02 design as secondary simultaneous stress (not ladder escalation)."
)


def _kubectl_inventory() -> Dict[str, Any]:
    inv: Dict[str, Any] = {"captured_utc": datetime.now(timezone.utc).isoformat(), "lines": []}
    try:
        out = subprocess.check_output(
            ["kubectl", "get", "pods", "-A", "--no-headers"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        keys = ("free5gc", "ueransim", "rantester", "trisla-decision", "trisla-portal", "nasp", "onos", "mininet", "iperf")
        for line in out.splitlines():
            if any(k in line.lower() for k in keys):
                inv["lines"].append(line.strip())
    except Exception as e:
        inv["error"] = str(e)
    return inv


def answer_questions() -> Dict[str, Any]:
    allowed = [m["id"] for m in MECHANISMS if m["reviewer_safety"] == "allowed"]
    forbidden = [m["id"] for m in MECHANISMS if m["reviewer_safety"] == "forbidden"]
    return {
        "Q1_mechanisms_in_environment": [m["id"] for m in MECHANISMS if m.get("env_ready")],
        "Q2_contention_domains": {
            "core": ["NCM-SESS-01", "NCM-AMF-01", "NCM-UPF-MF-01"],
            "orchestration": ["NCM-ORCH-01", "NCM-LC-01"],
            "lifecycle": ["NCM-LC-01", "NCM-SESS-01"],
            "transport": ["NCM-UPF-MF-01"],
            "control_plane": ["NCM-SESS-01", "NCM-AMF-01", "NCM-PFCP-01"],
        },
        "Q3_lowest_risk_highest_potential": "NCM-ORCH-01 (risk) + NCM-UPF-MF-01 (pressure potential)",
        "Q4_pressure_feasibility_without_inv_prb": "conditionally_yes",
        "Q4_rationale": (
            "Frozen resource_pressure_v1 allows RTT+CPU rise with weak PRB coupling for UPF/multi-flow; "
            "feasibility≤0.55 requires combined pressure≈0.50+ at typical ml_risk OR higher orchestration load. "
            "Achievable only with PRB corridor observability restored and guards enforced — not via ladder alone."
        ),
        "Q5_core_stress_components": {
            "UPF": "ready (iperf user-plane)",
            "AMF": "partial (UERANSIM attach; high risk)",
            "SMF": "partial (session churn)",
            "PFCP_N4": "not ready (no exporter)",
            "session_lifecycle": "partial (UERANSIM/rantester)",
        },
        "Q6_environment_supports": {
            "churn": "partial",
            "session_storms": "partial",
            "multi_flow_orchestration": True,
            "repeated_slice_lifecycle": True,
        },
        "Q7_reviewer_safe": allowed,
        "Q8_dangerous": forbidden + ["NCM-AMF-01", "NCM-UPF-LAD-01"],
        "Q9_ncm_sequence": [r[0] for r in ROADMAP],
        "Q10_first_authorized_mechanism": FIRST_AUTHORIZED,
    }


def _figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    mechs = [m["id"].replace("NCM-", "") for m in MECHANISMS if m["id"] != "NCM-FORB-01"]
    scores = []
    for m in MECHANISMS:
        if m["id"] == "NCM-FORB-01":
            continue
        p = {"high": 3, "medium": 2, "low": 1, "low_medium": 1.5, "exhausted": 0, "unknown": 0}.get(
            str(m["pressure_potential"]), 1
        )
        r = {"low": 3, "medium": 2, "high": 0.5, "critical": 0}.get(str(m["regression_risk"]), 1)
        scores.append(p * r)
    y = np.arange(len(mechs))
    ax.barh(y, scores, color=["#2ecc71" if m["reviewer_safety"] == "allowed" else "#e74c3c" if m["reviewer_safety"] == "forbidden" else "#f39c12" for m in MECHANISMS if m["id"] != "NCM-FORB-01"])
    ax.set_yticks(y)
    ax.set_yticklabels(mechs, fontsize=7)
    ax.set_xlabel("Potential × safety (qualitative)")
    ax.set_title("Operational contention mechanism map")
    fig.savefig(fd / "operational_contention_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.text(
        0.5,
        0.55,
        "UPF (iperf) ──► transport RTT\n"
        "SMF/SESS churn ──► core CPU (30%)\n"
        "RAN PRB ──► weak / proxy gap\n"
        "Portal submits ──► orchestration path",
        ha="center",
        fontsize=10,
        family="monospace",
    )
    ax.axis("off")
    ax.set_title("Core contention pathways (frozen pressure_v1)")
    fig.savefig(fd / "core_contention_pathways.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.annotate("", xy=(0.7, 0.5), xytext=(0.1, 0.5), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(0.05, 0.5, "Portal\nSEM", va="center", fontsize=9)
    ax.text(0.75, 0.5, "DE\nscore_mode", va="center", fontsize=9)
    ax.text(0.4, 0.7, "NCM-ORCH-01\nconcurrent tenants", ha="center", fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Orchestration contention flow")
    fig.savefig(fd / "orchestration_contention_flow.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.axvspan(18, 24, color="#2ecc71", alpha=0.3, label="PRB corridor")
    ax.axvline(24, color="red", ls="--", label="hard abort")
    ax.bar(["UPF-MF", "ORCH", "SESS", "AMF", "Ladder"], [0.2, 0.1, 0.15, 0.35, 0.5], color="#3498db")
    ax.set_ylabel("PRB leakage risk (qualitative)")
    ax.set_title("PRB isolation strategy per mechanism")
    ax.legend(fontsize=7)
    fig.savefig(fd / "prb_isolation_strategy.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 5))
    steps = [r[0] for r in ROADMAP]
    ax.plot(range(len(steps)), [1] * len(steps), "o-", color="#8e44ad", markersize=10)
    for i, (s, desc) in enumerate(ROADMAP):
        ax.text(i, 1.08, s.replace("NCM-EXEC-", ""), ha="center", fontsize=8)
        ax.text(i, 0.85, desc.split("(")[0].strip()[:18], ha="center", fontsize=6, rotation=15)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("NCM execution roadmap")
    fig.savefig(fd / "ncm_execution_roadmap.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_environment_inventory",
        "phase_2_operational_mechanism_inventory",
        "phase_3_contention_capability_mapping",
        "phase_4_risk_mapping",
        "phase_5_prb_governance_impact",
        "phase_6_operational_feasibility_analysis",
        "phase_7_reviewer_safe_mechanisms",
        "phase_8_execution_roadmap",
        "phase_9_final_ncm_decision",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    k8s_inv = _kubectl_inventory()
    (OUT / "analysis" / "kubectl_inventory_snapshot.json").write_text(
        json.dumps(k8s_inv, indent=2), encoding="utf-8"
    )
    answers = answer_questions()

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

    env_table = "\n".join(
        f"| {c['domain']} | {c['component']} | {c['namespace']} | {c['status']} | {c['stress_tool']} |"
        for c in ENV_COMPONENTS
    )
    (OUT / "phase_1_environment_inventory" / "ENVIRONMENT_INVENTORY.md").write_text(
        "# Phase 1 — Environment Inventory\n\n**Verdict:** ENVIRONMENT_CAPABILITIES_MAPPED\n\n"
        f"| Domain | Component | Namespace | Status | Stress tool |\n|--------|-----------|-----------|--------|-------------|\n"
        f"{env_table}\n\nDigest: `{ACTIVE_DIGEST}`\n",
        encoding="utf-8",
    )

    mech_rows = "\n".join(
        f"| {m['id']} | {m['name']} | {m['reviewer_safety']} | {m['env_ready']} | {m['pressure_potential']} |"
        for m in MECHANISMS
    )
    (OUT / "phase_2_operational_mechanism_inventory" / "OPERATIONAL_MECHANISMS.md").write_text(
        "# Phase 2 — Operational Mechanism Inventory\n\n**Verdict:** OPERATIONAL_CONTENTION_MECHANISMS_IDENTIFIED\n\n"
        f"| ID | Mechanism | Reviewer | Ready | Pressure potential |\n|----|-----------|----------|-------|--------------------|\n"
        f"{mech_rows}\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_contention_capability_mapping" / "CONTENTION_CAPABILITY_MAPPING.md").write_text(
        "# Phase 3 — Contention Capability Mapping\n\n**Verdict:** CONTENTION_CAPABILITY_CLASSIFIED\n\n"
        "| Mechanism | Pressure↑ | Feasibility↓ | Core | Orchestration |\n|-----------|-----------|--------------|------|---------------|\n"
        + "\n".join(
            f"| {m['id']} | {m['pressure_potential']} | {m['feasibility_potential']} | "
            f"{'yes' if 'core' in str(m['domains']) else 'partial'} | "
            f"{'yes' if 'orchestration' in m['domains'] else 'no'} |"
            for m in MECHANISMS
            if m["id"] != "NCM-FORB-01"
        )
        + "\n",
        encoding="utf-8",
    )

    (OUT / "phase_4_risk_mapping" / "RISK_MAPPING.md").write_text(
        "# Phase 4 — Risk Mapping\n\n**Verdict:** CONTENTION_RISK_MAP_COMPLETE\n\n"
        "**Low risk:** NCM-ORCH-01\n**Medium:** NCM-UPF-MF-01, NCM-LC-01\n"
        "**High:** NCM-SESS-01, NCM-AMF-01, NCM-PFCP-01\n"
        "**Frozen insufficient:** NCM-UPF-LAD-01\n**Forbidden:** NCM-FORB-01, NCM-PFCP-01\n",
        encoding="utf-8",
    )

    (OUT / "phase_5_prb_governance_impact" / "PRB_GOVERNANCE_IMPACT.md").write_text(
        "# Phase 5 — PRB Governance Impact\n\n**Verdict:** INV_PRB_PROTECTION_STRATEGY_DEFINED\n\n"
        "- **Isolation:** score_mode only inside 18–24% corridor; hard abort ≥24%\n"
        "- **Transport leakage:** multi-flow may raise RTT without PRB — monitor proxy PRB each rep\n"
        "- **PRB contamination:** session/AMF storms risk indirect PRB — defer high-risk mechanisms\n"
        "- **Strategy:** reuse `core_contention_runtime_controls` guards; fix PRB proxy sampling in NCM-EXEC-03\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_operational_feasibility_analysis" / "OPERATIONAL_FEASIBILITY_ANALYSIS.md").write_text(
        "# Phase 6 — Operational Feasibility\n\n**Verdict:** OPERATIONAL_CONTENTION_FEASIBILITY_DEFINED\n\n"
        f"Targets: pressure ≥ {PRESSURE_REQ}, feasibility ≤ {FEASIBILITY_REQ}\n\n"
        f"**Q4:** {answers['Q4_pressure_feasibility_without_inv_prb']} — {answers['Q4_rationale']}\n\n"
        "Realistic path: **NCM-ORCH-01 + NCM-UPF-MF-01** under frozen guards (not ladder-only).\n",
        encoding="utf-8",
    )

    allowed = [m for m in MECHANISMS if m["reviewer_safety"] == "allowed"]
    partial = [m for m in MECHANISMS if m["reviewer_safety"] == "partial"]
    forbidden = [m for m in MECHANISMS if m["reviewer_safety"] in ("forbidden", "forbidden_primary")]
    (OUT / "phase_7_reviewer_safe_mechanisms" / "REVIEWER_SAFE_MECHANISMS.md").write_text(
        "# Phase 7 — Reviewer-Safe Mechanisms\n\n**Verdict:** REVIEWER_SAFE_NCM_MECHANISMS_DEFINED\n\n"
        "## Allowed\n" + "\n".join(f"- **{m['id']}**: {m['name']}" for m in allowed) + "\n\n"
        "## Partial\n" + "\n".join(f"- **{m['id']}**: {m['name']}" for m in partial) + "\n\n"
        "## Forbidden\n" + "\n".join(f"- **{m['id']}**: {m['name']}" for m in forbidden) + "\n",
        encoding="utf-8",
    )

    road = "\n".join(f"{i+1}. **{s}** — {d}" for i, (s, d) in enumerate(ROADMAP))
    (OUT / "phase_8_execution_roadmap" / "NCM_EXECUTION_ROADMAP.md").write_text(
        f"# Phase 8 — Execution Roadmap\n\n**Verdict:** NCM_EXECUTION_SEQUENCE_DEFINED\n\n{road}\n\n"
        f"**First authorized mechanism:** `{FIRST_AUTHORIZED}`\n\n{FIRST_AUTHORIZED_RATIONALE}\n",
        encoding="utf-8",
    )

    final = "NCM_EXEC_READY"
    (OUT / "phase_9_final_ncm_decision" / "FINAL_NCM_DECISION.md").write_text(
        f"# Phase 9 — Final NCM Decision\n\n# **{final}**\n\n"
        f"**First mechanism authorized:** `{FIRST_AUTHORIZED}`\n\n"
        f"**Companion (design phase):** `NCM-UPF-MF-01`\n\n"
        "## Mandatory Q&A\n```json\n{json.dumps(answers, indent=2)}\n```\n",
        encoding="utf-8",
    )

    _figures()

    summary = {
        "phase": "NCM-EXEC-01",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final,
        "active_digest": ACTIVE_DIGEST,
        "upstream_packs": UPSTREAM,
        "environment": ENV_COMPONENTS,
        "mechanisms": MECHANISMS,
        "mandatory_questions": answers,
        "first_authorized_mechanism": FIRST_AUTHORIZED,
        "first_authorized_rationale": FIRST_AUTHORIZED_RATIONALE,
        "roadmap": [{"phase": s, "description": d} for s, d in ROADMAP],
        "phase_verdicts": {
            "phase_1": "ENVIRONMENT_CAPABILITIES_MAPPED",
            "phase_2": "OPERATIONAL_CONTENTION_MECHANISMS_IDENTIFIED",
            "phase_3": "CONTENTION_CAPABILITY_CLASSIFIED",
            "phase_4": "CONTENTION_RISK_MAP_COMPLETE",
            "phase_5": "INV_PRB_PROTECTION_STRATEGY_DEFINED",
            "phase_6": "OPERATIONAL_CONTENTION_FEASIBILITY_DEFINED",
            "phase_7": "REVIEWER_SAFE_NCM_MECHANISMS_DEFINED",
            "phase_8": "NCM_EXECUTION_SEQUENCE_DEFINED",
            "phase_9": final,
        },
        "next_prompt": "PROMPT_TRISLA_NCM_EXEC_02_OPERATIONAL_CONTENTION_DESIGN_V1",
        "approval_required": "NCM_EXEC_01_APPROVED",
        "hard_stop": True,
        "global_program_state": "NCM_EXEC_AUDIT_PENDING_APPROVAL",
        "runtime_freeze_ok": freeze_ok,
    }
    (OUT / "analysis" / "ncm_operational_contention_audit_summary.json").write_text(
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
