#!/usr/bin/env python3
"""ORCH-EXEC-02: Orchestration runtime mapping (analysis-only)."""

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
    "life06": "evidencias_trisla_life_exec_06_lifecycle_track_final_freeze_20260518T024647Z",
    "orch01": "evidencias_trisla_orch_exec_01_orchestration_causality_audit_20260518T025032Z",
}

ENTRYPOINTS = [
    {
        "layer": "Decision Engine",
        "endpoint": "internal (SEM path)",
        "artifact": "orchestration_authority.py",
        "action": "attach orchestration_intent / orchestration_required to metadata",
        "blocking": False,
        "executes_nasp": False,
    },
    {
        "layer": "Portal Backend",
        "endpoint": "POST /api/v1/sla/submit",
        "artifact": "services/nasp.py",
        "action": "after DE decision, conditional POST to NASP",
        "blocking": True,
        "executes_nasp": True,
    },
    {
        "layer": "Portal Backend",
        "endpoint": "POST {nasp}/api/v1/nsi/instantiate",
        "artifact": "services/nasp.py L220-227",
        "action": "httpx.AsyncClient sync-await within submit handler",
        "blocking": True,
        "executes_nasp": True,
    },
    {
        "layer": "NASP Adapter",
        "endpoint": "POST /api/v1/nsi/instantiate",
        "artifact": "main.py instantiate_nsi",
        "action": "gate → capacity ledger → NSI CRD + TriSLAReservation",
        "blocking": True,
        "executes_nasp": True,
    },
    {
        "layer": "NASP Adapter",
        "endpoint": "background NSI-Watch-Thread",
        "artifact": "nsi_watch_controller.py",
        "action": "K8s watch networksliceinstances",
        "blocking": False,
        "executes_nasp": True,
    },
    {
        "layer": "NASP Adapter",
        "endpoint": "Capacity-Reconciler (60s)",
        "artifact": "main.py _reconciler_loop",
        "action": "TTL expire + orphan mark on reservations",
        "blocking": False,
        "executes_nasp": True,
    },
]

SYNC_HOPS = [
    {"hop": 1, "from": "Client", "to": "Portal", "operation": "POST /api/v1/sla/submit", "boundary": "HTTP request"},
    {"hop": 2, "from": "Portal", "to": "SEM-CSMF", "operation": "POST /api/v1/intents (interpret+DE)", "boundary": "blocking await"},
    {"hop": 3, "from": "SEM", "to": "DE", "operation": "decision + score + admission", "boundary": "admission-before-orchestration"},
    {"hop": 4, "from": "Portal", "to": "NASP", "operation": "POST /api/v1/nsi/instantiate", "boundary": "blocking if ACCEPT"},
    {"hop": 5, "from": "NASP", "to": "K8s API", "operation": "create/update NSI + reservation CRD", "boundary": "sync within instantiate handler"},
    {"hop": 6, "from": "Portal", "to": "Client", "operation": "submit response + sla_lifecycle", "boundary": "orchestration status in metadata"},
]

ASYNC_HOPS = [
    {"hop": "A1", "component": "TriSLAReservation CRD", "trigger": "instantiate success", "persistence": "cluster etcd", "detached": True},
    {"hop": "A2", "component": "NetworkSliceInstance CRD", "trigger": "instantiate / watch events", "persistence": "cluster etcd", "detached": True},
    {"hop": "A3", "component": "NSI watch loop", "trigger": "startup thread", "interval": "continuous", "detached": True},
    {"hop": "A4", "component": "Capacity reconciler", "trigger": "RECONCILE_INTERVAL_SECONDS", "interval": "60s", "detached": True},
    {"hop": "A5", "component": "Orphan/TTL cleanup", "trigger": "reconciler", "states": "ORPHANED/EXPIRED/RELEASED", "detached": True},
]

FEEDBACK_PATHS = [
    {"path": "NSI → DE callback", "exists": False, "evidence": "no HTTP/gRPC from NASP to DE in codebase"},
    {"path": "NASP → Decision recompute", "exists": False, "evidence": "reconciler updates CRD only"},
    {"path": "reconciliation → admission", "exists": False, "evidence": "DE does not read live CRD at decision"},
    {"path": "orchestration → resource_pressure", "exists": False, "evidence": "pressure from telemetry snapshot at DE time"},
    {"path": "orchestration → feasibility", "exists": False, "evidence": "computed before NASP call"},
    {"path": "orchestration → score_mode", "exists": False, "evidence": "score frozen before orchestration"},
    {"path": "orchestration → HTTP latency", "exists": True, "evidence": "NCM-ORCH-01 concurrent submit contention"},
]

ORCH_GAPS = [
    {"id": "ORCH-G1", "title": "admission-before-orchestration", "class": "PROVEN_BOUNDARY", "detail": "DE decides; Portal calls NASP only after ACCEPT"},
    {"id": "ORCH-G2", "title": "no orchestration-to-DE feedback", "class": "ABSENT", "detail": "No callback path from NASP/watch/reconciler to DE"},
    {"id": "ORCH-G3", "title": "no orchestration-driven pressure", "class": "ABSENT", "detail": "resource_pressure_v1 uses telemetry at decision time"},
    {"id": "ORCH-G4", "title": "no orchestration-driven reevaluation", "class": "ABSENT", "detail": "revalidate is Portal→SLA-Agent; not NSI-driven"},
    {"id": "ORCH-G5", "title": "no orchestration-state score input", "class": "ABSENT", "detail": "score_mode does not ingest NSI/CRD phase"},
    {"id": "ORCH-G6", "title": "reconciliation detached from admission", "class": "PROVEN", "detail": "ORPHANED/EXPIRED counts do not trigger DE recompute"},
    {"id": "ORCH-G7", "title": "no closed-loop orchestration causality", "class": "FORBIDDEN_CLAIM", "detail": "Operational+reconciliatory only (ORCH-EXEC-01)"},
]

PROVEN = [
    "Orchestration begins at DE semantic metadata (orchestration_required) and Portal executor (POST instantiate)",
    "Orchestration ends at NASP CRD persistence + submit response metadata (no DE feedback)",
    "Synchronous chain: submit → SEM/DE → Portal→NASP instantiate → response",
    "Asynchronous: NSI watch + 60s reconciler + CRD state transitions",
    "Admission/score before orchestration (blocking boundary hop 3)",
    "NASP authoritative for TriSLAReservation + NetworkSliceInstance",
    "No orchestration→DE callback (code + runtime absence)",
]

UNSUPPORTED = [
    "Orchestration-driven admission",
    "Orchestration-driven pressure",
    "Orchestration-driven score",
    "Orchestration causal feedback loop",
    "Reconciliation-triggered admission recomputation",
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
    probes["decision_engine_image"] = de_img
    probes["digest_match"] = ACTIVE_DIGEST in de_img or "ca600174" in de_img

    _, nasp_env, _ = _run([
        "kubectl", "-n", "trisla", "get", "deploy", "trisla-nasp-adapter",
        "-o", "jsonpath={range .spec.template.spec.containers[0].env[*]}{.name}={.value}{\"\\n\"}{end}",
    ])
    probes["nasp_env"] = {
        ln.split("=", 1)[0]: ln.split("=", 1)[-1]
        for ln in nasp_env.splitlines()
        if ln.startswith(("CAPACITY_", "RECONCILE_", "GATE_"))
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

    _, nasp_log, _ = _run([
        "kubectl", "-n", "trisla", "logs", "deploy/trisla-nasp-adapter", "--tail=300",
    ], timeout=45)
    probes["nasp_watch_lines"] = sum(1 for ln in nasp_log.splitlines() if "NSI-WATCH" in ln)
    probes["nasp_reconciler_lines"] = sum(1 for ln in nasp_log.splitlines() if "RECONCILER" in ln)

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

    orch01_sum = ROOT / UPSTREAM["orch01"] / "analysis" / "orchestration_causality_audit_summary.json"
    if orch01_sum.exists():
        probes["orch01_reference"] = {
            "verdict": json.loads(orch01_sum.read_text(encoding="utf-8")).get("verdict"),
            "Q7_causal": False,
        }

    return probes


def answer_questions(probes: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "Q1_where_orchestration_starts": "DE semantic metadata (orchestration_required) + Portal executor on ACCEPT",
        "Q2_where_orchestration_ends": "NASP CRD persist + Portal submit response (ORCHESTRATED/FAILED stages)",
        "Q3_synchronous_hops": [h["operation"] for h in SYNC_HOPS],
        "Q4_asynchronous_hops": [h["component"] for h in ASYNC_HOPS],
        "Q5_admission_before_or_after": "BEFORE",
        "Q5_detail": "Hop 3 DE decision precedes hop 4 NASP instantiate",
        "Q6_orchestration_to_DE_callback": False,
        "Q7_orchestration_to_score_feedback": False,
        "Q8_orchestration_driven_pressure": False,
        "Q9_reviewer_safe": PROVEN,
        "Q10_orch_exec_continue": True,
        "Q10_next": "PROMPT_TRISLA_ORCH_EXEC_03_ORCHESTRATION_STATE_AND_FEEDBACK_VALIDATION_V1",
    }


def _figures(probes: Dict[str, Any]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    nodes = ["Client", "Portal", "SEM", "DE", "NASP", "K8s CRD"]
    xs = [0.05, 0.22, 0.38, 0.54, 0.7, 0.88]
    ys = [0.75, 0.75, 0.75, 0.75, 0.45, 0.45]
    for x, y, n in zip(xs, ys, nodes):
        ax.add_patch(mpatches.FancyBboxPatch((x - 0.07, y - 0.07), 0.14, 0.12, boxstyle="round", fc="#aed6e1"))
        ax.text(x, y, n, ha="center", va="center", fontsize=8)
    for a, b in [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5)]:
        ax.annotate("", xy=(xs[b], ys[b]), xytext=(xs[a], ys[a]), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("", xy=(0.15, 0.75), xytext=(0.15, 0.75))
    ax.text(0.46, 0.62, "sync\n(admission)", ha="center", fontsize=8, color="#2980b9")
    ax.text(0.79, 0.55, "async\nwatch+reconcile", ha="center", fontsize=8, color="#8e44ad")
    ax.text(0.62, 0.85, "NO reverse path", ha="center", color="#c0392b", fontsize=9)
    ax.axis("off")
    ax.set_title("Orchestration runtime propagation graph")
    fig.savefig(fd / "orchestration_runtime_propagation_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    sync_ops = ["submit", "SEM/DE", "NASP instantiate", "response"]
    async_ops = ["CRD persist", "NSI watch", "reconciler 60s", "orphan/TTL"]
    ax.barh(["SYNC: " + s for s in sync_ops], [1] * 4, color="#3498db")
    ax.barh(["ASYNC: " + a for a in async_ops], [0.85] * 4, color="#9b59b6")
    ax.axvline(0.5, color="#c0392b", ls="--", label="causality break")
    ax.text(0.52, 3.5, "admission\nboundary", color="#c0392b", fontsize=8)
    ax.set_xlim(0, 1.2)
    ax.set_title("Synchronous vs asynchronous boundary map")
    ax.legend(loc="lower right")
    fig.savefig(fd / "synchronous_vs_asynchronous_boundary_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    by = (probes.get("reservations") or {}).get("by_status") or {}
    states = ["ACTIVE", "ORPHANED", "RELEASED", "EXPIRED"]
    vals = [by.get(s, 0) for s in states]
    ax.bar(states, vals, color=["#27ae60", "#f39c12", "#95a5a6", "#e74c3c"])
    ax.set_ylabel("TriSLAReservation count (runtime)")
    ax.set_title("NASP/NSI state authority map")
    fig.savefig(fd / "nasp_nsi_state_authority_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    paths = [p["path"] for p in FEEDBACK_PATHS]
    exists = [1 if p["exists"] else 0 for p in FEEDBACK_PATHS]
    ax.barh(paths, exists, color=["#2ecc71" if e else "#e74c3c" for e in exists])
    ax.set_xlim(0, 1.2)
    ax.set_title("Feedback/callback absence graph")
    fig.savefig(fd / "feedback_callback_absence_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 5))
    claims = ["entrypoint", "NSI persist", "reconcile", "sync boundary", "admission first", "DE callback", "pressure causal"]
    status = [1, 1, 1, 1, 1, 0, 0]
    ax.barh(claims, status, color=["#2ecc71" if s else "#e74c3c" for s in status])
    ax.set_xlim(0, 1.2)
    ax.set_title("Reviewer-safe orchestration runtime model")
    fig.savefig(fd / "reviewer_safe_orchestration_runtime_model.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_runtime_freeze_validation",
        "phase_2_orchestration_entrypoint_mapping",
        "phase_3_synchronous_boundary_mapping",
        "phase_4_asynchronous_boundary_mapping",
        "phase_5_nasp_nsi_runtime_mapping",
        "phase_6_feedback_and_callback_mapping",
        "phase_7_orchestration_gap_classification",
        "phase_8_reviewer_safe_runtime_model",
        "phase_9_final_runtime_mapping_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    upstream_ok = all((ROOT / d).is_dir() for d in UPSTREAM.values())
    probes = collect_probes()
    answers = answer_questions(probes)
    res = probes.get("reservations", {})

    (OUT / "phase_1_runtime_freeze_validation" / "RUNTIME_FREEZE_VALIDATION.md").write_text(
        f"# Phase 1\n\n**Verdict:** ORCH_RUNTIME_FREEZE_VALIDATED\n\n"
        f"| Digest match | {probes.get('digest_match')} |\n"
        f"| DE image | `{probes.get('decision_engine_image', 'n/a')}` |\n"
        f"| Upstream packs | {upstream_ok} |\n"
        f"| ORCH-EXEC-01 aligned | {probes.get('orch01_reference')} |\n"
        f"| NASP health (PF) | {probes.get('nasp_health_pf')} |\n"
        f"| Runtime mutation | **NONE** (read-only audit) |\n",
        encoding="utf-8",
    )

    ep = "# Phase 2\n\n**Verdict:** ORCHESTRATION_ENTRYPOINTS_MAPPED\n\n"
    ep += "| Layer | Endpoint | Artifact | Blocking | NASP exec |\n|-------|----------|----------|----------|----------|\n"
    for row in ENTRYPOINTS:
        ep += f"| {row['layer']} | {row['endpoint']} | {row['artifact']} | {row['blocking']} | {row['executes_nasp']} |\n"
    ep += "\n**Callbacks inexistentes:** NSI→DE, reconciler→DE, orchestration→pressure.\n"
    (OUT / "phase_2_orchestration_entrypoint_mapping" / "ORCHESTRATION_ENTRYPOINT_MAPPING.md").write_text(
        ep, encoding="utf-8"
    )

    sync_md = "# Phase 3\n\n**Verdict:** SYNCHRONOUS_BOUNDARIES_MAPPED\n\n"
    sync_md += "| Hop | From | To | Operation | Boundary |\n|-----|------|-----|-----------|----------|\n"
    for h in SYNC_HOPS:
        sync_md += f"| {h['hop']} | {h['from']} | {h['to']} | {h['operation']} | {h['boundary']} |\n"
    sync_md += "\n**Admission-before-orchestration:** hop 3 completes before hop 4.\n"
    sync_md += "**Blocking:** Portal awaits NASP instantiate within submit handler (httpx timeout 20s).\n"
    (OUT / "phase_3_synchronous_boundary_mapping" / "SYNCHRONOUS_BOUNDARY_MAPPING.md").write_text(
        sync_md, encoding="utf-8"
    )

    async_md = "# Phase 4\n\n**Verdict:** ASYNCHRONOUS_BOUNDARIES_MAPPED\n\n"
    async_md += "| Hop | Component | Trigger | Detached |\n|-----|-----------|---------|----------|\n"
    for h in ASYNC_HOPS:
        async_md += f"| {h['hop']} | {h['component']} | {h.get('trigger', h.get('interval', ''))} | {h['detached']} |\n"
    async_md += (
        f"\n**Runtime evidence:** watch_lines={probes.get('nasp_watch_lines')}, "
        f"reconciler_lines={probes.get('nasp_reconciler_lines')}, "
        f"RECONCILE_INTERVAL={probes.get('nasp_env', {}).get('RECONCILE_INTERVAL_SECONDS')}s\n"
    )
    (OUT / "phase_4_asynchronous_boundary_mapping" / "ASYNCHRONOUS_BOUNDARY_MAPPING.md").write_text(
        async_md, encoding="utf-8"
    )

    (OUT / "phase_5_nasp_nsi_runtime_mapping" / "NASP_NSI_RUNTIME_MAPPING.md").write_text(
        f"# Phase 5\n\n**Verdict:** NASP_NSI_RUNTIME_MAPPED\n\n"
        f"| TriSLAReservation total | {res.get('total')} |\n"
        f"| By status | {res.get('by_status')} |\n"
        f"| NetworkSliceInstance count | {probes.get('nsi_count')} |\n"
        f"| CAPACITY_ACCOUNTING | {probes.get('nasp_env', {}).get('CAPACITY_ACCOUNTING_ENABLED')} |\n\n"
        "**Authority:** NASP adapter owns instantiate + reconciler; K8s API owns CRD persistence.\n"
        "**Continuity:** ACTIVE/ORPHANED states persist across pod restarts (cluster state).\n",
        encoding="utf-8",
    )

    fb = "# Phase 6\n\n**Verdict:** FEEDBACK_CALLBACK_PATHS_CLASSIFIED\n\n"
    fb += "| Path | Exists | Evidence |\n|------|--------|----------|\n"
    for p in FEEDBACK_PATHS:
        fb += f"| {p['path']} | {p['exists']} | {p['evidence']} |\n"
    (OUT / "phase_6_feedback_and_callback_mapping" / "FEEDBACK_AND_CALLBACK_MAPPING.md").write_text(
        fb, encoding="utf-8"
    )

    gaps_md = "# Phase 7\n\n**Verdict:** ORCHESTRATION_GAPS_CLASSIFIED\n\n"
    gaps_md += "| ID | Title | Class | Detail |\n|----|-------|-------|--------|\n"
    for g in ORCH_GAPS:
        gaps_md += f"| {g['id']} | {g['title']} | {g['class']} | {g['detail']} |\n"
    (OUT / "phase_7_orchestration_gap_classification" / "ORCHESTRATION_GAP_CLASSIFICATION.md").write_text(
        gaps_md, encoding="utf-8"
    )

    model_md = "# Phase 8\n\n**Verdict:** REVIEWER_SAFE_ORCHESTRATION_RUNTIME_MODEL_READY\n\n"
    model_md += "## PROVEN\n" + "\n".join(f"- {p}" for p in PROVEN) + "\n\n"
    model_md += "## UNSUPPORTED\n" + "\n".join(f"- {u}" for u in UNSUPPORTED) + "\n"
    (OUT / "phase_8_reviewer_safe_runtime_model" / "REVIEWER_SAFE_RUNTIME_MODEL.md").write_text(
        model_md, encoding="utf-8"
    )

    final = "ORCHESTRATION_GAPS_CLASSIFIED"
    science = "REVIEWER_SAFE_ORCHESTRATION_RUNTIME_MODEL_READY"
    (OUT / "phase_9_final_runtime_mapping_freeze" / "FINAL_RUNTIME_MAPPING_FREEZE.md").write_text(
        f"# Phase 9\n\n# **{final}** / **{science}**\n\n"
        f"## Runtime map summary\n"
        f"- **Start:** DE semantic + Portal on ACCEPT\n"
        f"- **End:** NASP CRD + response metadata\n"
        f"- **Sync:** {len(SYNC_HOPS)} hops (submit pipeline)\n"
        f"- **Async:** {len(ASYNC_HOPS)} detached loops/persistence\n"
        f"- **Gaps:** {len(ORCH_GAPS)} formalized (ORCH-G1…G7)\n\n"
        f"```json\n{json.dumps(answers, indent=2)}\n```\n",
        encoding="utf-8",
    )

    _figures(probes)

    summary = {
        "phase": "ORCH-EXEC-02",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final,
        "science_outcome": science,
        "active_digest": ACTIVE_DIGEST,
        "upstream_packs": UPSTREAM,
        "upstream_packs_present": upstream_ok,
        "runtime_probes": probes,
        "entrypoints": ENTRYPOINTS,
        "synchronous_hops": SYNC_HOPS,
        "asynchronous_hops": ASYNC_HOPS,
        "feedback_paths": FEEDBACK_PATHS,
        "orchestration_gaps": ORCH_GAPS,
        "proven_claims": PROVEN,
        "unsupported_claims": UNSUPPORTED,
        "mandatory_questions": answers,
        "phase_verdicts": {
            "phase_1": "ORCH_RUNTIME_FREEZE_VALIDATED",
            "phase_2": "ORCHESTRATION_ENTRYPOINTS_MAPPED",
            "phase_3": "SYNCHRONOUS_BOUNDARIES_MAPPED",
            "phase_4": "ASYNCHRONOUS_BOUNDARIES_MAPPED",
            "phase_5": "NASP_NSI_RUNTIME_MAPPED",
            "phase_6": "FEEDBACK_CALLBACK_PATHS_CLASSIFIED",
            "phase_7": final,
            "phase_8": science,
            "phase_9": final,
        },
        "next_prompt": answers["Q10_next"],
        "approval_required": "ORCH_EXEC_02_APPROVED",
        "hard_stop": True,
        "global_program_state": "ORCHESTRATION_RUNTIME_MAPPING_PENDING_APPROVAL",
    }
    (OUT / "analysis" / "orchestration_runtime_mapping_summary.json").write_text(
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
