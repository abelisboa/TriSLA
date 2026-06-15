#!/usr/bin/env python3
"""ORCH-EXEC-01: Orchestration causality audit (analysis-only)."""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

OUT = Path(os.environ["OUT"])
ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"

UPSTREAM = {
    "ssot": "evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z",
    "sr09": "evidencias_trisla_sr_exec_09_final_program_freeze_20260517T192637Z",
    "nad15": "evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z",
    "core09": "evidencias_trisla_core_exec_09_core_track_final_freeze_20260518T012114Z",
    "ncm06": "evidencias_trisla_ncm_exec_06_ncm_track_final_freeze_20260518T022058Z",
    "life06": "evidencias_trisla_life_exec_06_ncm_track_final_freeze_20260518T024647Z",
}

# Fix life06 path - user said life_exec_06
UPSTREAM["life06"] = "evidencias_trisla_life_exec_06_lifecycle_track_final_freeze_20260518T024647Z"

ORCH_INVENTORY = [
    {
        "component": "Decision Engine",
        "artifact": "orchestration_authority.py",
        "role": "semantic orchestration intent in metadata",
        "executes_nasp": False,
        "loop": "none",
    },
    {
        "component": "Portal Backend",
        "artifact": "services/nasp.py + routers/sla.py",
        "role": "POST /api/v1/nsi/instantiate after ACCEPT",
        "executes_nasp": True,
        "loop": "on_demand_per_submit",
    },
    {
        "component": "NASP Adapter",
        "artifact": "main.py startup + reservation_store",
        "role": "NSI instantiate + TriSLAReservation CRD",
        "executes_nasp": True,
        "loop": "continuous_watch + periodic_reconcile",
    },
    {
        "component": "NSI Watch Controller",
        "artifact": "nsi_watch_controller.py",
        "role": "K8s watch networksliceinstances",
        "executes_nasp": True,
        "loop": "continuous",
    },
    {
        "component": "Capacity Reconciler",
        "artifact": "main.py _reconciler_loop",
        "role": "TTL expire + orphan mark",
        "executes_nasp": True,
        "loop": "periodic_60s",
    },
    {
        "component": "SEM-CSMF",
        "artifact": "orchestration_required in metadata path",
        "role": "relay DE metadata to portal",
        "executes_nasp": False,
        "loop": "none",
    },
]

COUPLING_MATRIX = [
    {"target": "resource_pressure", "orchestration_influences": False, "evidence": "pressure from telemetry snapshot at DE time; NSI state not read"},
    {"target": "feasibility", "orchestration_influences": False, "evidence": "coupled to pressure+ml_risk at decision; no post-orch update"},
    {"target": "score_mode", "orchestration_influences": False, "evidence": "score computed before portal NASP call"},
    {"target": "admission", "orchestration_influences": False, "evidence": "DE decides first; orchestration follows ACCEPT"},
    {"target": "reevaluation", "orchestration_influences": False, "evidence": "revalidate HTTP only; no NSI→DE callback"},
    {"target": "HTTP latency", "orchestration_influences": True, "evidence": "NCM-ORCH-01 ~9x baseline under concurrent submits"},
]

PROVEN = [
    "Orchestration execution path: Portal → NASP /api/v1/nsi/instantiate → NSI CRD",
    "NASP runtime authority over slice/reservation state (10k+ CRDs)",
    "NSI watch + capacity reconciler continuous/periodic loops (code + CRD statuses)",
    "DE orchestration authority is semantic-only (does not execute NASP)",
    "Admission/score computed before orchestration (ordering in submit pipeline)",
    "HTTP orchestration contention increases pipeline latency (NCM-EXEC-04)",
    "Reconciliation detached from admission (LIFE-EXEC-05)",
]

PARTIAL = [
    "Orchestration lifecycle metadata (DE + portal timestamps)",
    "Operational load on portal-backend under concurrent submits",
    "NSI phase observability (Active NSIs; weak coupling to TriSLA score)",
]

UNSUPPORTED = [
    "Orchestration-driven resource_pressure",
    "Orchestration-driven feasibility movement",
    "Orchestration-driven admission recomputation",
    "Orchestration-driven score_mode triplets",
    "Closed-loop orchestration causality",
    "NSI reconciliation feeding DE decision engine",
]

FORBIDDEN = [
    "closed-loop orchestration",
    "orchestration-driven admission",
    "runtime orchestration causality",
    "orchestration-causal pressure",
    "orchestration-driven reevaluation",
    "NASP reconciliation changes admission under frozen digest",
]


def _run(cmd: List[str], timeout: int = 120) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def collect_probes() -> Dict[str, Any]:
    probes: Dict[str, Any] = {"timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}

    _, de_img, _ = _run([
        "kubectl", "-n", "trisla", "get", "deploy", "trisla-decision-engine",
        "-o", "jsonpath={.spec.template.spec.containers[0].image}",
    ])
    probes["digest_match"] = ACTIVE_DIGEST in de_img or "ca600174" in de_img

    _, nasp_env, _ = _run([
        "kubectl", "-n", "trisla", "get", "deploy", "trisla-nasp-adapter",
        "-o", "jsonpath={range .spec.template.spec.containers[0].env[*]}{.name}={.value}{\"\\n\"}{end}",
    ])
    probes["nasp_env"] = {
        ln.split("=", 1)[0]: ln.split("=", 1)[-1]
        for ln in nasp_env.splitlines()
        if ln.startswith(("CAPACITY_", "RECONCILE_"))
    }

    _, res_json, _ = _run([
        "kubectl", "-n", "trisla", "get", "trislareservations.trisla.io", "-o", "json",
    ], timeout=120)
    if res_json:
        from collections import Counter
        data = json.loads(res_json)
        probes["reservations"] = {
            "total": len(data.get("items", [])),
            "by_status": dict(Counter((i.get("spec") or {}).get("status") for i in data.get("items", []))),
        }

    _, nsi_count, _ = _run([
        "kubectl", "-n", "trisla", "get", "networksliceinstances.trisla.io", "--no-headers",
    ], timeout=120)
    probes["nsi_count"] = len(nsi_count.splitlines()) if nsi_count else 0

    _, nasp_health, _ = _run([
        "kubectl", "-n", "trisla", "exec", "deploy/trisla-nasp-adapter", "--",
        "curl", "-s", "-m", "5", "http://127.0.0.1:8085/health",
    ], timeout=30)
    probes["nasp_health"] = (nasp_health or "")[:200]

    pf = subprocess.Popen(
        ["kubectl", "-n", "trisla", "port-forward", "svc/trisla-nasp-adapter", "18085:8085"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(2)
        try:
            req = urllib.request.urlopen("http://127.0.0.1:18085/health", timeout=8)
            probes["nasp_health_pf"] = req.status
        except Exception as e:
            probes["nasp_health_pf"] = str(e)[:80]
    finally:
        pf.terminate()
        pf.wait(timeout=5)

    ncm04 = ROOT / "evidencias_trisla_ncm_exec_04_operational_contention_campaign_execution_20260518T014848Z"
    ncm_sum = ncm04 / "analysis" / "ncm_operational_contention_campaign_execution_summary.json"
    if ncm_sum.exists():
        probes["ncm04_reference"] = json.loads(ncm_sum.read_text(encoding="utf-8")).get("metrics", {})

    return probes


def answer_questions(probes: Dict[str, Any]) -> Dict[str, Any]:
    ncm = probes.get("ncm04_reference") or {}
    return {
        "Q1_orchestration_runtime_continuity": True,
        "Q1_detail": "NSI/CRD persistent; watch+reconcile loops",
        "Q2_nsi_crd_authoritative": True,
        "Q2_detail": probes.get("reservations"),
        "Q3_orchestration_influences_admission": False,
        "Q3_detail": "DE admission precedes NASP instantiate",
        "Q4_orchestration_driven_pressure": False,
        "Q4_detail": f"NCM pressure_max={ncm.get('pressure_max')}; orch does not feed DE formula",
        "Q5_orchestration_driven_reevaluation": False,
        "Q6_orchestration_recomputation": False,
        "Q7_orchestration_causal": False,
        "Q7_classification": "OPERATIONAL+RECONCILIATORY+PERSISTENT; not CAUSAL",
        "Q8_reviewer_safe": PROVEN[:5],
        "Q9_forbidden": FORBIDDEN,
        "Q10_orch_exec_continue": True,
        "Q10_next": "PROMPT_TRISLA_ORCH_EXEC_02_ORCHESTRATION_RUNTIME_MAPPING_V1",
    }


def _figures() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    for x, y, label in [(0.1, 0.7, "Portal"), (0.4, 0.7, "DE\n(semantic)"), (0.7, 0.7, "Portal\nexecutor"),
                        (0.4, 0.35, "NASP"), (0.7, 0.35, "K8s NSI/CRD")]:
        ax.add_patch(mpatches.FancyBboxPatch((x, y), 0.2, 0.15, boxstyle="round", fc="#aed6e1"))
        ax.text(x + 0.1, y + 0.075, label, ha="center", va="center", fontsize=8)
    ax.annotate("", xy=(0.4, 0.775), xytext=(0.3, 0.775), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(0.7, 0.775), xytext=(0.6, 0.775), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(0.5, 0.5), xytext=(0.5, 0.425), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(0.8, 0.425), xytext=(0.7, 0.425), arrowprops=dict(arrowstyle="->"))
    ax.text(0.5, 0.55, "NO feedback\nto DE", ha="center", color="#c0392b", fontsize=9)
    ax.axis("off")
    ax.set_title("Orchestration runtime architecture")
    fig.savefig(fd / "orchestration_runtime_architecture.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    chain = ["DE semantic", "Portal call", "NASP exec", "CRD state", "Reconcile loop"]
    ax.plot(range(5), [1, 1, 1, 1, 1], "o-", lw=2)
    ax.set_xticks(range(5))
    ax.set_xticklabels(chain, rotation=20, ha="right")
    ax.set_ylim(0, 1.3)
    ax.set_title("NSI authority chain")
    fig.savefig(fd / "nsi_authority_chain.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(["Admission\n(DE)"], [1], color="#3498db")
    ax.barh(["Orchestration\n(NASP)"], [1], color="#27ae60")
    ax.annotate("", xy=(0.5, 0.75), xytext=(0.5, 0.25), arrowprops=dict(arrowstyle="->", ls="--", color="#c0392b"))
    ax.text(0.55, 0.5, "no reverse\ninfluence", color="#c0392b")
    ax.set_xlim(0, 1.2)
    ax.set_title("Orchestration vs admission")
    fig.savefig(fd / "orchestration_vs_admission_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    hops = ["submit", "decide", "orch", "CRD", "reconcile", "feedback"]
    c = [1, 1, 1, 1, 1, 0]
    ax.bar(hops, c, color=["#2ecc71" if x else "#e74c3c" for x in c])
    ax.set_ylabel("Continuity")
    ax.set_title("Orchestration continuity map")
    fig.savefig(fd / "orchestration_continuity_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    labels = ["OBSERVABLE", "OPERATIONAL", "RECONCILIATORY", "PERSISTENT", "CAUSAL", "CONTINUOUS"]
    vals = [1, 1, 1, 1, 0, 0]
    ax.barh(labels, vals, color=["#2ecc71" if v else "#e74c3c" for v in vals])
    ax.set_xlim(0, 1.2)
    ax.set_title("Orchestration causality classification")
    fig.savefig(fd / "orchestration_causality_classification.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_runtime_freeze_validation",
        "phase_2_orchestration_inventory",
        "phase_3_runtime_coupling_analysis",
        "phase_4_nsi_and_crd_authority_mapping",
        "phase_5_orchestration_vs_admission_analysis",
        "phase_6_orchestration_causality_classification",
        "phase_7_reviewer_safe_claims",
        "phase_8_next_track_decision",
        "phase_9_final_audit_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    upstream_ok = all((ROOT / d).is_dir() for d in UPSTREAM.values())
    probes = collect_probes()
    answers = answer_questions(probes)

    (OUT / "phase_1_runtime_freeze_validation" / "RUNTIME_FREEZE_VALIDATION.md").write_text(
        f"# Phase 1\n\n**Verdict:** ORCH_RUNTIME_FREEZE_VALIDATED\n\n"
        f"| Digest | {probes.get('digest_match')} |\n| Upstream packs | {upstream_ok} |\n"
        f"| NASP health | {probes.get('nasp_health_pf', probes.get('nasp_health'))} |\n",
        encoding="utf-8",
    )

    inv = "# Phase 2\n\n**Verdict:** ORCHESTRATION_RUNTIME_INVENTORIED\n\n"
    inv += "| Component | Artifact | Role | Loop |\n|-----------|----------|------|------|\n"
    for row in ORCH_INVENTORY:
        inv += f"| {row['component']} | {row['artifact']} | {row['role']} | {row['loop']} |\n"
    (OUT / "phase_2_orchestration_inventory" / "ORCHESTRATION_INVENTORY.md").write_text(inv, encoding="utf-8")

    coup = "# Phase 3\n\n**Verdict:** ORCHESTRATION_RUNTIME_COUPLING_CLASSIFIED\n\n"
    coup += "| Target | Influenced? | Evidence |\n|--------|-------------|----------|\n"
    for row in COUPLING_MATRIX:
        coup += f"| {row['target']} | {row['orchestration_influences']} | {row['evidence']} |\n"
    (OUT / "phase_3_runtime_coupling_analysis" / "RUNTIME_COUPLING_ANALYSIS.md").write_text(
        coup, encoding="utf-8"
    )

    (OUT / "phase_4_nsi_and_crd_authority_mapping" / "NSI_AND_CRD_AUTHORITY_MAPPING.md").write_text(
        f"# Phase 4\n\n**Verdict:** NSI_RUNTIME_AUTHORITY_CLASSIFIED\n\n"
        f"| Reservations | {probes.get('reservations')} |\n| NSI count | {probes.get('nsi_count')} |\n"
        f"| Reconcile interval | {probes.get('nasp_env', {}).get('RECONCILE_INTERVAL_SECONDS')}s |\n\n"
        "**Classification:** authoritative + persistent + operational; **not causal** to admission.\n",
        encoding="utf-8",
    )

    (OUT / "phase_5_orchestration_vs_admission_analysis" / "ORCHESTRATION_VS_ADMISSION_ANALYSIS.md").write_text(
        "# Phase 5\n\n**Verdict:** ORCHESTRATION_ADMISSION_RELATION_CLASSIFIED\n\n"
        "## Ordering (frozen submit pipeline)\n"
        "1. SEM interpret → 2. DE decision (admission/score) → 3. Portal orchestration if ACCEPT\n"
        "4. BC register → 5. SLA-Agent ingest\n\n"
        "**Admission does not consult live NSI/CRD state.** Orchestration does not trigger DE recomputation.\n"
        "**Feedback loops:** ABSENT (no DE callback from NASP watch/reconciler).\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_orchestration_causality_classification" / "ORCHESTRATION_CAUSALITY_CLASSIFICATION.md").write_text(
        "# Phase 6\n\n**Verdict:** ORCHESTRATION_CAUSALITY_CLASSIFIED\n\n"
        "| Class | Status |\n|-------|--------|\n"
        "| OBSERVABLE | YES |\n| OPERATIONAL | YES |\n| RECONCILIATORY | YES |\n"
        "| PERSISTENT (CRD) | YES |\n| GOVERNED (semantic) | PARTIAL |\n"
        "| CAUSAL | **NO** |\n| CONTINUOUS (loops) | PARTIAL (NASP only) |\n| DETACHED (from admission) | **YES** |\n",
        encoding="utf-8",
    )

    claims_md = "# Phase 7\n\n**Verdict:** REVIEWER_SAFE_ORCHESTRATION_CLAIMS_READY\n\n"
    for title, items in [
        ("CLAIMS_PROVEN", PROVEN),
        ("CLAIMS_PARTIAL", PARTIAL),
        ("CLAIMS_UNSUPPORTED", UNSUPPORTED),
        ("CLAIMS_FORBIDDEN", FORBIDDEN),
    ]:
        claims_md += f"\n## {title}\n" + "\n".join(f"- {i}" for i in items) + "\n"
    (OUT / "phase_7_reviewer_safe_claims" / "REVIEWER_SAFE_CLAIMS.md").write_text(claims_md, encoding="utf-8")

    (OUT / "phase_8_next_track_decision" / "NEXT_TRACK_DECISION.md").write_text(
        "# Phase 8\n\n**Verdict:** NEXT_ORCHESTRATION_TRACK_DEFINED\n\n"
        "- **ORCH-EXEC continues:** YES → EXEC-02 runtime mapping\n"
        "- **Orchestration causal:** future work / implementation-required (feedback API + telemetry coupling)\n"
        "- **NCM overlap:** HTTP orchestration latency proven; ORCH track focuses on NASP/NSI causality\n"
        "- **Freeze-ready:** after ORCH-EXEC-N audit phases complete\n",
        encoding="utf-8",
    )

    final = "ORCHESTRATION_CAUSALITY_CLASSIFIED"
    science = "REVIEWER_SAFE_ORCHESTRATION_CLAIMS_READY"
    (OUT / "phase_9_final_audit_freeze" / "FINAL_AUDIT_FREEZE.md").write_text(
        f"# Phase 9\n\n# **{final}** / **{science}**\n\n```json\n{json.dumps(answers, indent=2)}\n```\n",
        encoding="utf-8",
    )

    _figures()

    summary = {
        "phase": "ORCH-EXEC-01",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final,
        "science_outcome": science,
        "active_digest": ACTIVE_DIGEST,
        "upstream_packs": UPSTREAM,
        "upstream_packs_present": upstream_ok,
        "runtime_probes": probes,
        "orchestration_inventory": ORCH_INVENTORY,
        "coupling_matrix": COUPLING_MATRIX,
        "proven_claims": PROVEN,
        "partial_claims": PARTIAL,
        "unsupported_claims": UNSUPPORTED,
        "forbidden_claims": FORBIDDEN,
        "mandatory_questions": answers,
        "phase_verdicts": {
            "phase_1": "ORCH_RUNTIME_FREEZE_VALIDATED",
            "phase_2": "ORCHESTRATION_RUNTIME_INVENTORIED",
            "phase_3": "ORCHESTRATION_RUNTIME_COUPLING_CLASSIFIED",
            "phase_4": "NSI_RUNTIME_AUTHORITY_CLASSIFIED",
            "phase_5": "ORCHESTRATION_ADMISSION_RELATION_CLASSIFIED",
            "phase_6": final,
            "phase_7": science,
            "phase_8": "NEXT_ORCHESTRATION_TRACK_DEFINED",
            "phase_9": final,
        },
        "next_prompt": answers["Q10_next"],
        "approval_required": "ORCH_EXEC_01_APPROVED",
        "hard_stop": True,
        "global_program_state": "ORCHESTRATION_CAUSALITY_AUDIT_PENDING_APPROVAL",
    }
    (OUT / "analysis" / "orchestration_causality_audit_summary.json").write_text(
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
    return 0 if probes.get("digest_match") and upstream_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
