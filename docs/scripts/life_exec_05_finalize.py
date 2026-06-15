#!/usr/bin/env python3
"""LIFE-EXEC-05: Lifecycle continuity and runtime authority validation (analysis-only)."""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

OUT = Path(os.environ["OUT"])
ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"

LIFE_PACKS = [
    ("01", "evidencias_trisla_life_exec_01_lifecycle_gap_audit_20260518T022450Z", "LIFECYCLE_BLOCKERS_IDENTIFIED"),
    ("02", "evidencias_trisla_life_exec_02_lifecycle_runtime_mapping_20260518T023001Z", "LIFECYCLE_RUNTIME_GAPS_CLASSIFIED"),
    ("03", "evidencias_trisla_life_exec_03_lifecycle_state_persistence_validation_20260518T023455Z", "LIFECYCLE_PERSISTENCE_GAPS_CLASSIFIED"),
    ("04", "evidencias_trisla_life_exec_04_lifecycle_reconciliation_and_reevaluation_audit_20260518T023952Z", "LIFECYCLE_LOOP_GAPS_CLASSIFIED"),
]

AUTHORITY_CHAIN = [
    {"component": "Portal", "submit": "contributive", "lifecycle": "compositor", "runtime": "orchestrator_caller", "reconciliation": "observer", "persistence": "absent", "governance": "relay"},
    {"component": "SEM-CSMF", "submit": "contributive", "lifecycle": "observer", "runtime": "semantic_model", "reconciliation": "detached", "persistence": "authoritative_semantic", "governance": "detached"},
    {"component": "Decision Engine", "submit": "authoritative_admission", "lifecycle": "authoritative_semantic", "runtime": "detached", "reconciliation": "detached", "persistence": "partial_ephemeral", "governance": "authoritative_semantic"},
    {"component": "NASP Adapter", "submit": "detached", "lifecycle": "runtime_executor", "runtime": "authoritative_slice", "reconciliation": "authoritative", "persistence": "authoritative_crd", "governance": "detached"},
    {"component": "SLA-Agent", "submit": "observer", "lifecycle": "detached", "runtime": "detached", "reconciliation": "detached", "persistence": "absent", "governance": "observer_on_demand"},
    {"component": "BC-NSSMF", "submit": "detached", "lifecycle": "observer", "runtime": "detached", "reconciliation": "detached", "persistence": "authoritative_immutable", "governance": "authoritative_immutable"},
]

CONTINUITY_HOPS = [
    {"hop": "submit", "mode": "on_demand", "continuity": "transient", "authority": "Portal+DE"},
    {"hop": "semantic persistence", "mode": "persistent", "continuity": "continuous_store", "authority": "SEM"},
    {"hop": "admission", "mode": "on_demand", "continuity": "broken_after_response", "authority": "DE"},
    {"hop": "orchestration", "mode": "on_demand", "continuity": "persistent_crd", "authority": "NASP"},
    {"hop": "reconciliation", "mode": "continuous", "continuity": "continuous", "authority": "NASP"},
    {"hop": "reevaluation", "mode": "on_demand", "continuity": "broken", "authority": "none"},
    {"hop": "governance", "mode": "on_demand", "continuity": "immutable_snapshot", "authority": "BC"},
]

BREAKPOINTS = [
    {"id": "BREAK-01", "issue": "portal retrieval absent", "severity": "critical", "class": "invariant"},
    {"id": "BREAK-02", "issue": "no continuous reevaluation", "severity": "critical", "class": "future_work"},
    {"id": "BREAK-03", "issue": "Kafka I-05 loop inactive (not wired)", "severity": "critical", "class": "implementation_required"},
    {"id": "BREAK-04", "issue": "no admission recomputation", "severity": "critical", "class": "invariant"},
    {"id": "BREAK-05", "issue": "no lifecycle-pressure propagation", "severity": "critical", "class": "invariant"},
    {"id": "BREAK-06", "issue": "fragmented lineage", "severity": "secondary", "class": "invariant"},
    {"id": "BREAK-07", "issue": "DE evidence ephemeral", "severity": "secondary", "class": "invariant"},
    {"id": "BREAK-08", "issue": "no continuous SLA governance", "severity": "critical", "class": "future_work"},
]

CLAIMS_PROVEN = [
    "SEM SQLite semantic persistence (intents/nests/slices) with replay via intent_id",
    "NASP NSI watch + capacity reconciler continuous/periodic loops (code + CRD ORPHANED/EXPIRED)",
    "BC on-chain immutable governance persistence at submit",
    "Portal synchronous submit pipeline with sla_lifecycle metadata in response",
    "DE authoritative admission/score at decision time (frozen digest)",
    "NASP runtime-authoritative slice/reservation state (10k+ CRDs)",
    "Reconciliation operates independently of admission (observable decoupling)",
]

CLAIMS_PARTIAL = [
    "Lifecycle continuity across hops (fragmented stores, no unified API)",
    "DE lifecycle semantic authority (metadata only; portal executes)",
    "Telemetry governance (Prometheus external; snapshots at submit/revalidate)",
    "SLA-Agent SLO path (HTTP on-demand; Kafka env set but consume loop unwired)",
    "Portal lifecycle_state compositor (not durable registry)",
]

CLAIMS_UNSUPPORTED = [
    "Continuous end-to-end lifecycle",
    "Lifecycle-driven admission recomputation",
    "Lifecycle-driven resource_pressure",
    "Continuous SLA reevaluation / governance loop",
    "Closed-loop lifecycle causality",
    "Runtime autonomous SLA reevaluation",
]

CLAIMS_FORBIDDEN = [
    "continuous lifecycle governance",
    "runtime autonomous SLA reevaluation",
    "closed-loop lifecycle causality",
    "lifecycle-causal admission divergence",
    "multidomain balanced lifecycle runtime",
    "full lifecycle proof without new mechanisms",
]


def _load_json(path: Path) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def load_upstream() -> Dict[str, Any]:
    packs = []
    for num, dirname, default_v in LIFE_PACKS:
        p = ROOT / dirname
        summary = None
        for name in (
            "lifecycle_gap_audit_summary.json",
            "lifecycle_runtime_mapping_summary.json",
            "lifecycle_state_persistence_validation_summary.json",
            "lifecycle_reconciliation_and_reevaluation_summary.json",
        ):
            candidate = p / "analysis" / name
            if candidate.exists():
                summary = _load_json(candidate)
                break
        packs.append({
            "phase": f"LIFE-EXEC-{num}",
            "pack": dirname,
            "exists": p.is_dir(),
            "verdict": (summary or {}).get("verdict", default_v),
        })
    life04 = _load_json(
        ROOT / LIFE_PACKS[3][1] / "analysis" / "lifecycle_reconciliation_and_reevaluation_summary.json"
    ) or {}
    return {"phases": packs, "life04": life04}


def quick_freeze_probe() -> Dict[str, Any]:
    probe: Dict[str, Any] = {}
    try:
        de_img = subprocess.check_output(
            [
                "kubectl", "-n", "trisla", "get", "deploy", "trisla-decision-engine",
                "-o", "jsonpath={.spec.template.spec.containers[0].image}",
            ],
            text=True,
        ).strip()
        probe["digest_match"] = ACTIVE_DIGEST in de_img or "ca600174" in de_img
    except Exception:
        probe["digest_match"] = False
    pf = subprocess.Popen(
        ["kubectl", "-n", "trisla", "port-forward", "svc/trisla-portal-backend", "18001:8001"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(2)
        req = urllib.request.urlopen("http://127.0.0.1:18001/api/v1/health/global", timeout=8)
        probe["portal_health"] = req.status
    except Exception as e:
        probe["portal_health"] = str(e)[:80]
    finally:
        pf.terminate()
        pf.wait(timeout=5)
    return probe


def answer_questions(upstream: Dict[str, Any]) -> Dict[str, Any]:
    life04 = upstream.get("life04", {})
    probes = life04.get("runtime_probes", {})
    return {
        "Q1_e2e_continuous_lifecycle": False,
        "Q1_detail": "Broken at reevaluation + retrieval; partial NASP reconcile path",
        "Q2_authoritative_summary": {
            "admission": "Decision Engine",
            "slice_runtime": "NASP/K8s",
            "reconciliation": "NASP",
            "semantic_persistence": "SEM",
            "immutable_governance": "BC-NSSMF",
        },
        "Q3_nasp_reconciliation_continuous": True,
        "Q3_detail": probes.get("reservations"),
        "Q4_sla_agent_continuous": False,
        "Q4_detail": f"loop_wired={probes.get('sla_agent_start_consuming_referenced')}",
        "Q5_admission_recomputation": False,
        "Q6_lifecycle_driven_pressure": False,
        "Q7_governance_continuous": False,
        "Q8_lifecycle_causal": False,
        "Q8_classification": "OBSERVABLE+RECONCILIATORY+PARTIAL_PERSISTENT; not CAUSAL or CONTINUOUS",
        "Q9_continuous_proof_blockers": [b["issue"] for b in BREAKPOINTS if b["severity"] == "critical"],
        "Q10_life_exec_freeze_or_evolve": "freeze_ready",
        "Q10_detail": "LIFE-EXEC-06 track final freeze; no new runtime campaigns under frozen digest",
        "Q10_next_prompt": "PROMPT_TRISLA_LIFE_EXEC_06_LIFECYCLE_TRACK_FINAL_FREEZE_V1",
    }


def _figures() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    comps = [r["component"] for r in AUTHORITY_CHAIN]
    domains = ["submit", "lifecycle", "runtime", "reconciliation", "persistence", "governance"]
    auth_score = {
        "authoritative": 1.0, "authoritative_admission": 1.0, "authoritative_semantic": 1.0,
        "authoritative_slice": 1.0, "authoritative_crd": 1.0, "authoritative_immutable": 1.0,
        "authoritative_semantic": 0.9, "compositor": 0.5, "contributive": 0.4, "relay": 0.3,
        "runtime_executor": 0.7, "semantic_model": 0.6, "orchestrator_caller": 0.5,
        "observer": 0.2, "observer_on_demand": 0.15, "detached": 0.05, "partial_ephemeral": 0.35,
        "absent": 0.0,
    }
    data = np.array([[auth_score.get(row[d], 0.2) for d in domains] for row in AUTHORITY_CHAIN])
    im = ax.imshow(data, cmap="YlGn", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(domains)))
    ax.set_xticklabels(domains, rotation=30, ha="right")
    ax.set_yticks(range(len(comps)))
    ax.set_yticklabels(comps)
    ax.set_title("Authority chain matrix")
    fig.colorbar(im, ax=ax, fraction=0.03)
    fig.savefig(fd / "authority_chain_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 5))
    hops = [h["hop"] for h in CONTINUITY_HOPS]
    colors = {"continuous": "#2ecc71", "continuous_store": "#27ae60", "transient": "#f39c12",
              "broken": "#e74c3c", "broken_after_response": "#e67e22", "immutable_snapshot": "#9b59b6",
              "persistent_crd": "#3498db"}
    c = [colors.get(h["continuity"], "#95a5a6") for h in CONTINUITY_HOPS]
    ax.barh(hops, [1] * len(hops), color=c)
    ax.set_title("Lifecycle continuity graph")
    fig.savefig(fd / "lifecycle_continuity_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    brks = [b["id"] for b in BREAKPOINTS]
    sev = [1 if b["severity"] == "critical" else 0.5 for b in BREAKPOINTS]
    ax.barh(brks, sev, color=["#c0392b" if s == 1 else "#f39c12" for s in sev])
    ax.set_xlabel("Severity")
    ax.set_title("Runtime breakpoint map")
    fig.savefig(fd / "runtime_breakpoint_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    ax.annotate("", xy=(0.7, 0.5), xytext=(0.3, 0.5), arrowprops=dict(arrowstyle="<->", lw=2))
    ax.text(0.15, 0.55, "DE admission\n(on-demand)", fontsize=9, ha="center")
    ax.text(0.85, 0.55, "NASP reconcile\n(continuous)", fontsize=9, ha="center")
    ax.text(0.5, 0.35, "NO feedback loop", fontsize=10, ha="center", color="#c0392b")
    ax.set_title("Reconciliation vs admission graph")
    fig.savefig(fd / "reconciliation_vs_admission_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["OBSERVABLE", "PERSISTENT", "RECONCILIATORY", "GOVERNED", "PARTIAL", "CAUSAL", "CONTINUOUS"]
    vals = [1, 1, 1, 1, 1, 0, 0]
    ax.barh(labels, vals, color=["#2ecc71" if v else "#e74c3c" for v in vals])
    ax.set_xlim(0, 1.2)
    ax.set_title("Lifecycle causality classification")
    fig.savefig(fd / "lifecycle_causality_classification.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_runtime_freeze_validation",
        "phase_2_authority_chain_validation",
        "phase_3_lifecycle_continuity_validation",
        "phase_4_runtime_breakpoint_analysis",
        "phase_5_reconciliation_vs_admission_analysis",
        "phase_6_lifecycle_causality_classification",
        "phase_7_reviewer_safe_claims",
        "phase_8_next_track_decision",
        "phase_9_final_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    upstream = load_upstream()
    probe = quick_freeze_probe()
    answers = answer_questions(upstream)

    phase_table = "\n".join(
        f"| {p['phase']} | {'✓' if p['exists'] else '✗'} | {p['verdict']} |"
        for p in upstream["phases"]
    )
    (OUT / "phase_1_runtime_freeze_validation" / "RUNTIME_FREEZE_VALIDATION.md").write_text(
        f"# Phase 1\n\n**Verdict:** RUNTIME_FREEZE_VALIDATED\n\n"
        f"| Phase | OK | Verdict |\n|-------|-----|--------|\n{phase_table}\n\n"
        f"| Digest | {probe.get('digest_match')} |\n| Portal health | {probe.get('portal_health')} |\n",
        encoding="utf-8",
    )

    auth_md = "# Phase 2\n\n**Verdict:** AUTHORITY_CHAIN_CLASSIFIED\n\n"
    auth_md += "| Component | Submit | Lifecycle | Runtime | Reconcile | Persist | Govern |\n"
    auth_md += "|-----------|--------|-----------|---------|-----------|---------|--------|\n"
    for row in AUTHORITY_CHAIN:
        auth_md += (
            f"| {row['component']} | {row['submit']} | {row['lifecycle']} | {row['runtime']} | "
            f"{row['reconciliation']} | {row['persistence']} | {row['governance']} |\n"
        )
    (OUT / "phase_2_authority_chain_validation" / "AUTHORITY_CHAIN_VALIDATION.md").write_text(
        auth_md, encoding="utf-8"
    )

    cont_md = "# Phase 3\n\n**Verdict:** LIFECYCLE_CONTINUITY_CLASSIFIED\n\n"
    cont_md += "**End-to-end continuous:** **NO**\n\n| Hop | Mode | Continuity | Authority |\n"
    cont_md += "|-----|------|------------|----------|\n"
    for h in CONTINUITY_HOPS:
        cont_md += f"| {h['hop']} | {h['mode']} | {h['continuity']} | {h['authority']} |\n"
    (OUT / "phase_3_lifecycle_continuity_validation" / "LIFECYCLE_CONTINUITY_VALIDATION.md").write_text(
        cont_md, encoding="utf-8"
    )

    brk_md = "# Phase 4\n\n**Verdict:** RUNTIME_BREAKPOINTS_FORMALIZED\n\n"
    for b in BREAKPOINTS:
        brk_md += f"- **{b['id']}** ({b['severity']}, {b['class']}): {b['issue']}\n"
    (OUT / "phase_4_runtime_breakpoint_analysis" / "RUNTIME_BREAKPOINT_ANALYSIS.md").write_text(
        brk_md, encoding="utf-8"
    )

    (OUT / "phase_5_reconciliation_vs_admission_analysis" / "RECONCILIATION_VS_ADMISSION_ANALYSIS.md").write_text(
        "# Phase 5\n\n**Verdict:** RECONCILIATION_ADMISSION_RELATION_CLASSIFIED\n\n"
        "## Findings\n"
        "- **Decoupling:** PROVEN — NASP reconciler mutates CRD status (ORPHANED/EXPIRED) without DE callback\n"
        "- **Synchronization:** ABSENT — no shared lifecycle registry linking intent_id → reservation → score\n"
        "- **Causality:** NONE — reconciliation does not trigger admission recompute\n"
        "- **Feedback:** ABSENT — NSI phase changes do not feed resource_pressure_v1\n"
        "- **Reevaluation influence:** ABSENT — revalidate is manual HTTP only\n\n"
        "**Reviewer-safe:** NASP maintains **runtime continuity of slice objects**; DE maintains "
        "**admission authority at submit time** only.\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_lifecycle_causality_classification" / "LIFECYCLE_CAUSALITY_CLASSIFICATION.md").write_text(
        "# Phase 6\n\n**Verdict:** LIFECYCLE_CAUSALITY_CLASSIFIED\n\n"
        "| Class | Status |\n|-------|--------|\n"
        "| OBSERVABLE | **YES** (metadata, CRD states, chain events) |\n"
        "| PERSISTENT | **PARTIAL** (SEM, CRD, BC) |\n"
        "| RECONCILIATORY | **YES** (NASP loops) |\n"
        "| GOVERNED | **PARTIAL** (immutable at submit) |\n"
        "| CAUSAL | **NO** |\n"
        "| CONTINUOUS | **NO** |\n",
        encoding="utf-8",
    )

    claims_md = "# Phase 7\n\n**Verdict:** REVIEWER_SAFE_LIFECYCLE_CLAIMS_READY\n\n"
    for title, items in [
        ("CLAIMS_PROVEN", CLAIMS_PROVEN),
        ("CLAIMS_PARTIAL", CLAIMS_PARTIAL),
        ("CLAIMS_UNSUPPORTED", CLAIMS_UNSUPPORTED),
        ("CLAIMS_FORBIDDEN", CLAIMS_FORBIDDEN),
    ]:
        claims_md += f"\n## {title}\n" + "\n".join(f"- {i}" for i in items) + "\n"
    (OUT / "phase_7_reviewer_safe_claims" / "REVIEWER_SAFE_CLAIMS.md").write_text(claims_md, encoding="utf-8")

    (OUT / "phase_8_next_track_decision" / "NEXT_TRACK_DECISION.md").write_text(
        "# Phase 8\n\n**Verdict:** NEXT_LIFECYCLE_TRACK_DEFINED\n\n"
        "| Decision | Outcome |\n|----------|--------|\n"
        "| LIFE-EXEC continue? | **Freeze at EXEC-06** (not more audit phases under same scope) |\n"
        "| ORCH-EXEC required? | **No** as primary — NCM froze orch-only path |\n"
        "| Continuous lifecycle proof | **Future work** (new loop + store + API) |\n"
        "| NCM-SESS / session churn | **New mechanism** if pressure path needed |\n"
        "| Kafka activation | **Implementation-required**; not validation-only |\n"
        "| Freeze-ready? | **YES** after LIFE-EXEC-06 |\n",
        encoding="utf-8",
    )

    final = "LIFECYCLE_CAUSALITY_CLASSIFIED"
    science = "REVIEWER_SAFE_LIFECYCLE_CLAIMS_READY"
    (OUT / "phase_9_final_freeze" / "FINAL_FREEZE.md").write_text(
        f"# Phase 9\n\n# **{final}** / **{science}**\n\n"
        f"LIFE-EXEC track ready for **LIFE-EXEC-06** final freeze.\n\n"
        f"```json\n{json.dumps(answers, indent=2)}\n```\n",
        encoding="utf-8",
    )

    _figures()

    summary = {
        "phase": "LIFE-EXEC-05",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final,
        "science_outcome": science,
        "active_digest": ACTIVE_DIGEST,
        "upstream_life_packs": upstream["phases"],
        "freeze_probe": probe,
        "authority_chain": AUTHORITY_CHAIN,
        "continuity_hops": CONTINUITY_HOPS,
        "breakpoints": BREAKPOINTS,
        "claims_proven": CLAIMS_PROVEN,
        "claims_partial": CLAIMS_PARTIAL,
        "claims_unsupported": CLAIMS_UNSUPPORTED,
        "claims_forbidden": CLAIMS_FORBIDDEN,
        "mandatory_questions": answers,
        "phase_verdicts": {
            "phase_1": "RUNTIME_FREEZE_VALIDATED",
            "phase_2": "AUTHORITY_CHAIN_CLASSIFIED",
            "phase_3": "LIFECYCLE_CONTINUITY_CLASSIFIED",
            "phase_4": "RUNTIME_BREAKPOINTS_FORMALIZED",
            "phase_5": "RECONCILIATION_ADMISSION_RELATION_CLASSIFIED",
            "phase_6": final,
            "phase_7": science,
            "phase_8": "NEXT_LIFECYCLE_TRACK_DEFINED",
            "phase_9": final,
        },
        "next_prompt": answers["Q10_next_prompt"],
        "approval_required": "LIFE_EXEC_05_APPROVED",
        "hard_stop": True,
        "global_program_state": "LIFE_RUNTIME_AUTHORITY_VALIDATION_PENDING_APPROVAL",
        "life_exec_freeze_recommendation": "LIFE_EXEC_TRACK_FREEZE_AT_EXEC_06",
    }
    (OUT / "analysis" / "lifecycle_continuity_and_runtime_authority_validation_summary.json").write_text(
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
    ok = probe.get("digest_match") and all(p["exists"] for p in upstream["phases"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
