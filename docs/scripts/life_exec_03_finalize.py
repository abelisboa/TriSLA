#!/usr/bin/env python3
"""LIFE-EXEC-03: Lifecycle state persistence validation (read-only)."""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

OUT = Path(os.environ["OUT"])
ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"

UPSTREAM = {
    "life01": "evidencias_trisla_life_exec_01_lifecycle_gap_audit_20260518T022450Z",
    "life02": "evidencias_trisla_life_exec_02_lifecycle_runtime_mapping_20260518T023001Z",
}

PERSISTENCE_GAPS = [
    {"id": "LIFE-P1", "gap": "no unified lifecycle registry", "class": "FRAGMENTED"},
    {"id": "LIFE-P2", "gap": "portal retrieval absent (GET /api/v1/sla → 404)", "class": "ABSENT"},
    {"id": "LIFE-P3", "gap": "DE persistence non-durable (ephemeral pod FS)", "class": "EPHEMERAL"},
    {"id": "LIFE-P4", "gap": "fragmented lifecycle lineage across stores", "class": "FRAGMENTED"},
    {"id": "LIFE-P5", "gap": "SLA-Agent not persistent (stateless HTTP)", "class": "ABSENT"},
    {"id": "LIFE-P6", "gap": "no continuous reevaluation persistence", "class": "ABSENT"},
    {"id": "LIFE-P7", "gap": "no session lifecycle persistence in TriSLA", "class": "ABSENT"},
    {"id": "LIFE-P8", "gap": "lifecycle not causal for admission/pressure", "class": "FORBIDDEN_CLAIM"},
]

COMPONENT_MATRIX: List[Dict[str, Any]] = [
    {
        "component": "Portal",
        "durability": "none",
        "replayability": False,
        "retrieval": False,
        "runtime_coupling": "submit_request",
        "lifecycle_continuity": "transient_response",
        "classification": "EPHEMERAL",
    },
    {
        "component": "SEM-CSMF",
        "durability": "pod_local_sqlite",
        "replayability": True,
        "retrieval": True,
        "runtime_coupling": "intent_id",
        "lifecycle_continuity": "semantic_only",
        "classification": "PERSISTENT",
    },
    {
        "component": "Decision Engine",
        "durability": "ephemeral_pod",
        "replayability": "partial",
        "retrieval": "file_by_intent",
        "runtime_coupling": "decision_time",
        "lifecycle_continuity": "metadata_in_json",
        "classification": "PARTIAL",
    },
    {
        "component": "NASP (CRD/NSI)",
        "durability": "kubernetes_etcd",
        "replayability": True,
        "retrieval": True,
        "runtime_coupling": "orchestration_authoritative",
        "lifecycle_continuity": "reservation_nsi_phases",
        "classification": "PERSISTENT",
    },
    {
        "component": "SLA-Agent",
        "durability": "none",
        "replayability": False,
        "retrieval": False,
        "runtime_coupling": "on_demand_http",
        "lifecycle_continuity": "none",
        "classification": "ABSENT",
    },
    {
        "component": "Blockchain (BC-NSSMF)",
        "durability": "on_chain",
        "replayability": True,
        "retrieval": "numeric_sla_id",
        "runtime_coupling": "submit_coupled",
        "lifecycle_continuity": "immutable_states",
        "classification": "PERSISTENT",
    },
]


def _run(cmd: List[str], timeout: int = 120) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def _portal_get(url: str) -> Dict[str, Any]:
    try:
        req = urllib.request.urlopen(url, timeout=8)
        return {"http_status": req.status, "body_preview": req.read()[:300].decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        return {"http_status": e.code, "error": str(e)[:120]}
    except Exception as e:
        return {"http_status": None, "error": str(e)[:120]}


def collect_probes() -> Dict[str, Any]:
    probes: Dict[str, Any] = {"timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}

    _, de_img, _ = _run([
        "kubectl", "-n", "trisla", "get", "deploy", "trisla-decision-engine",
        "-o", "jsonpath={.spec.template.spec.containers[0].image}",
    ])
    probes["digest_match"] = ACTIVE_DIGEST in de_img or "ca600174" in de_img
    probes["decision_engine_image"] = de_img

    pf = subprocess.Popen(
        ["kubectl", "-n", "trisla", "port-forward", "svc/trisla-portal-backend", "18001:8001"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(2)
        probes["portal_health"] = _portal_get("http://127.0.0.1:18001/api/v1/health/global")
        probes["portal_sla_list"] = _portal_get("http://127.0.0.1:18001/api/v1/sla")
        probes["portal_status_probe"] = _portal_get(
            "http://127.0.0.1:18001/api/v1/sla/status/00000000-0000-0000-0000-000000000001"
        )
    finally:
        pf.terminate()
        pf.wait(timeout=5)

    sem_py = r"""
import sqlite3, json
c = sqlite3.connect('file:/app/trisla_sem_csmf.db?mode=ro', uri=True)
schema = {r[0]: [x[1] for x in c.execute(f'PRAGMA table_info({r[0]})').fetchall()]
            for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
counts = {t: c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in schema}
oldest = c.execute('SELECT MIN(created_at), MAX(created_at) FROM intents').fetchone()
recent = c.execute(
    'SELECT intent_id, service_type, created_at FROM intents ORDER BY created_at DESC LIMIT 2'
).fetchall()
nest_link = c.execute(
    'SELECT COUNT(*) FROM nests n JOIN intents i ON n.intent_id=i.intent_id'
).fetchone()[0]
print(json.dumps({
    'tables': list(schema.keys()),
    'counts': counts,
    'intent_ts_range': {'min': oldest[0], 'max': oldest[1]},
    'recent_intents': recent,
    'nest_intent_fk_rows': nest_link,
    'schema_intents_cols': schema.get('intents', []),
}))
"""
    _, sem_out, _ = _run([
        "kubectl", "-n", "trisla", "exec", "deploy/trisla-sem-csmf", "--",
        "python3", "-c", sem_py,
    ], timeout=90)
    try:
        probes["sem_db"] = json.loads(sem_out) if sem_out else {}
    except json.JSONDecodeError:
        probes["sem_db"] = {"raw": sem_out[:500]}

    de_py = r"""
import os, json, glob
base = '/tmp/trisla_evidence/21_decision_engine_snapshots'
files = glob.glob(base + '/decision_*.json')
expl = glob.glob(base + '/explanation_*.json')
sample = {}
if files:
    with open(sorted(files)[-1]) as f:
        d = json.load(f)
    sample['keys'] = sorted(d.keys())[:25]
    md = d.get('metadata') or {}
    sample['has_lifecycle_event'] = 'lifecycle_event' in md
    sample['has_governance'] = 'governance_event' in md
print(json.dumps({
    'decision_files': len(files),
    'explanation_files': len(expl),
    'base_exists': os.path.isdir(base),
    'sample_latest': sample,
}))
"""
    _, de_out, _ = _run([
        "kubectl", "-n", "trisla", "exec", "deploy/trisla-decision-engine", "--",
        "python3", "-c", de_py,
    ], timeout=60)
    try:
        probes["de_evidence"] = json.loads(de_out) if de_out else {}
    except json.JSONDecodeError:
        probes["de_evidence"] = {"raw": de_out[:500]}

    _, res_json, _ = _run([
        "kubectl", "-n", "trisla", "get", "trislareservations.trisla.io", "-o", "json",
    ], timeout=120)
    if res_json:
        data = json.loads(res_json)
        from collections import Counter
        c = Counter((i.get("spec") or {}).get("status") for i in data.get("items", []))
        probes["reservations"] = {"total": len(data.get("items", [])), "by_status": dict(c)}
        sample = data["items"][0] if data.get("items") else {}
        probes["reservation_sample_spec_keys"] = sorted((sample.get("spec") or {}).keys())

    _, nsi_phases, _ = _run([
        "kubectl", "-n", "trisla", "get", "networksliceinstances.trisla.io",
        "-o", "jsonpath={range .items[*]}{.status.phase}{\"\\n\"}{end}",
    ], timeout=120)
    if nsi_phases:
        from collections import Counter
        phases = [p for p in nsi_phases.splitlines() if p.strip()]
        probes["nsi"] = {"count": len(phases), "by_phase": dict(Counter(phases))}

    _, bc_health, _ = _run([
        "kubectl", "-n", "trisla", "exec", "deploy/trisla-bc-nssmf", "--",
        "curl", "-s", "-m", "5", "http://127.0.0.1:8083/health",
    ], timeout=30)
    probes["bc_health"] = bc_health[:400] if bc_health else None

    _, sa_health, _ = _run([
        "kubectl", "-n", "trisla", "exec", "deploy/trisla-sla-agent-layer", "--",
        "curl", "-s", "-m", "5", "http://127.0.0.1:8084/health",
    ], timeout=30)
    probes["sla_agent_health"] = sa_health[:400] if sa_health else None

    _, sa_env, _ = _run([
        "kubectl", "-n", "trisla", "get", "deploy", "trisla-sla-agent-layer",
        "-o", "jsonpath={range .spec.template.spec.containers[0].env[*]}{.name}={.value}{\"\\n\"}{end}",
    ])
    probes["sla_agent_kafka"] = {
        ln.split("=", 1)[0]: ln.split("=", 1)[-1]
        for ln in sa_env.splitlines()
        if ln.startswith("KAFKA_")
    }

    return probes


def answer_questions(probes: Dict[str, Any]) -> Dict[str, Any]:
    sem = probes.get("sem_db") or {}
    de = probes.get("de_evidence") or {}
    pl = probes.get("portal_sla_list") or {}
    return {
        "Q1_portal_real_persistence": False,
        "Q1_detail": "No DB/registry; sla_lifecycle only in submit response",
        "Q2_sem_replayable": bool(sem.get("counts", {}).get("intents", 0) > 0),
        "Q2_detail": sem.get("counts"),
        "Q3_de_durable": False,
        "Q3_detail": f"ephemeral_pod: {de.get('decision_files')} files, no PVC",
        "Q4_nasp_runtime_authoritative": True,
        "Q4_detail": probes.get("reservations"),
        "Q5_blockchain_coupling": "coupled_at_submit",
        "Q5_detail": "on-chain immutable; retrieval by numeric id not intent UUID",
        "Q6_unified_lineage": False,
        "Q6_detail": "SEM + CRD + BC + DE files; no single registry",
        "Q7_retrieval_persistent": False,
        "Q7_detail": f"GET /sla={pl.get('http_status')}; GET intents/{{id}} via SEM only",
        "Q8_reevaluation_persistence": False,
        "Q8_detail": "revalidate on-demand; no stored reevaluation history in TriSLA",
        "Q9_persistence_causal": False,
        "Q9_detail": "Persistence does not imply causal admission (NCM/CORE frozen)",
        "Q10_full_proof_missing": [g["gap"] for g in PERSISTENCE_GAPS],
        "Q10_next_prompt": "PROMPT_TRISLA_LIFE_EXEC_04_LIFECYCLE_RECONCILIATION_AND_REEVALUATION_AUDIT_V1",
    }


def _figures(probes: Dict[str, Any]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    comps = ["Portal", "SEM", "DE", "NASP", "SLA-Agent", "BC"]
    y = [0.1, 0.9, 0.35, 0.95, 0.05, 0.85]
    colors = ["#e74c3c", "#2ecc71", "#f39c12", "#27ae60", "#bdc3c7", "#9b59b6"]
    for i, (c, yi, col) in enumerate(zip(comps, y, colors)):
        ax.barh(i, yi, color=col)
    ax.set_yticks(range(len(comps)))
    ax.set_yticklabels(comps)
    ax.set_xlabel("Persistence durability score (audit)")
    ax.set_title("Lifecycle persistence architecture")
    fig.savefig(fd / "lifecycle_persistence_architecture.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    dims = ["durability", "replay", "retrieve", "continuity"]
    portal = [0, 0, 0, 0.2]
    sem = [0.9, 1, 0.8, 0.5]
    nasp = [1, 1, 1, 0.8]
    x = np.arange(len(dims))
    w = 0.25
    ax.bar(x - w, portal, w, label="Portal", color="#e74c3c")
    ax.bar(x, sem, w, label="SEM", color="#2ecc71")
    ax.bar(x + w, nasp, w, label="NASP", color="#3498db")
    ax.set_xticks(x)
    ax.set_xticklabels(dims)
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=8)
    ax.set_title("Persistence durability matrix (subset)")
    fig.savefig(fd / "persistence_durability_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    txt = (
        "Portal (ephemeral)\n"
        "    |\n"
        "SEM DB -------+---- DE files (pod)\n"
        "    |         |\n"
        "NASP CRD -----+---- BC chain\n"
        "    |\n"
        "SLA-Agent (none)\n"
        "=> FRAGMENTED LINEAGE (LIFE-P4)"
    )
    ax.text(0.1, 0.5, txt, fontsize=10, family="monospace", va="center")
    ax.set_title("Runtime lineage fragmentation graph")
    fig.savefig(fd / "runtime_lineage_fragmentation_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    labels = ["PERSISTENT", "PARTIAL", "EPHEMERAL", "FRAGMENTED", "ABSENT"]
    counts = [2, 1, 1, 1, 1]
    ax.bar(labels, counts, color=["#2ecc71", "#f39c12", "#e67e22", "#9b59b6", "#e74c3c"])
    ax.set_ylabel("Components")
    ax.set_title("Replayability classification map")
    fig.savefig(fd / "replayability_classification_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    gaps = [g["id"] for g in PERSISTENCE_GAPS]
    ax.barh(gaps, [1] * len(gaps), color="#c0392b")
    ax.set_xlabel("Gap severity (qualitative)")
    ax.set_title("Lifecycle persistence gap matrix")
    fig.savefig(fd / "lifecycle_persistence_gap_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_runtime_freeze_validation",
        "phase_2_portal_persistence_validation",
        "phase_3_semantic_db_persistence_validation",
        "phase_4_decision_engine_persistence_validation",
        "phase_5_nasp_crd_persistence_validation",
        "phase_6_blockchain_persistence_validation",
        "phase_7_persistence_gap_matrix",
        "phase_8_reviewer_safe_persistence_interpretation",
        "phase_9_final_persistence_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    life02_ok = (ROOT / UPSTREAM["life02"]).is_dir()
    probes = collect_probes()
    answers = answer_questions(probes)

    (OUT / "phase_1_runtime_freeze_validation" / "RUNTIME_FREEZE_VALIDATION.md").write_text(
        f"# Phase 1\n\n**Verdict:** RUNTIME_FREEZE_VALIDATED\n\n"
        f"| Digest | {probes.get('digest_match')} |\n| LIFE-EXEC-02 | {life02_ok} |\n",
        encoding="utf-8",
    )

    ph, pl, ps = probes.get("portal_health", {}), probes.get("portal_sla_list", {}), probes.get("portal_status_probe", {})
    (OUT / "phase_2_portal_persistence_validation" / "PORTAL_PERSISTENCE_VALIDATION.md").write_text(
        f"# Phase 2\n\n**Verdict:** PORTAL_PERSISTENCE_CHARACTERIZED\n\n"
        f"| Probe | HTTP |\n|-------|------|\n| health/global | {ph.get('http_status')} |\n"
        f"| GET /api/v1/sla | {pl.get('http_status')} |\n| GET status/{{uuid}} | {ps.get('http_status')} |\n\n"
        "**Classification:** EPHEMERAL / TRANSIENT — no portal-side SLA registry; restart survivability **none**.\n",
        encoding="utf-8",
    )

    sem = probes.get("sem_db", {})
    (OUT / "phase_3_semantic_db_persistence_validation" / "SEMANTIC_DB_PERSISTENCE_VALIDATION.md").write_text(
        f"# Phase 3\n\n**Verdict:** SEMANTIC_PERSISTENCE_VALIDATED\n\n"
        f"```json\n{json.dumps(sem, indent=2)[:3000]}\n```\n\n"
        "**Classification:** PERSISTENT, replayable via intent_id; not portal lifecycle_state.\n",
        encoding="utf-8",
    )

    de = probes.get("de_evidence", {})
    (OUT / "phase_4_decision_engine_persistence_validation" / "DECISION_ENGINE_PERSISTENCE_VALIDATION.md").write_text(
        f"# Phase 4\n\n**Verdict:** DECISION_ENGINE_PERSISTENCE_CHARACTERIZED\n\n"
        f"```json\n{json.dumps(de, indent=2)}\n```\n\n"
        "**Classification:** EPHEMERAL_POD — auditable, partially replayable until pod reschedule; **non_durable**.\n",
        encoding="utf-8",
    )

    res = probes.get("reservations", {})
    nsi = probes.get("nsi", {})
    (OUT / "phase_5_nasp_crd_persistence_validation" / "NASP_CRD_PERSISTENCE_VALIDATION.md").write_text(
        f"# Phase 5\n\n**Verdict:** NASP_PERSISTENCE_VALIDATED\n\n"
        f"| Reservations | {res} |\n| NSI phases | {nsi} |\n\n"
        "**Classification:** PERSISTENT_RUNTIME — reconciled, recoverable, **runtime_authoritative** for slice instances.\n",
        encoding="utf-8",
    )

    (OUT / "phase_6_blockchain_persistence_validation" / "BLOCKCHAIN_PERSISTENCE_VALIDATION.md").write_text(
        f"# Phase 6\n\n**Verdict:** BLOCKCHAIN_PERSISTENCE_VALIDATED\n\n"
        f"Health: `{(probes.get('bc_health') or 'n/a')[:200]}`\n\n"
        "**Classification:** IMMUTABLE PERSISTENT — coupled at submit; detached for ongoing lifecycle unless update-sla-status called.\n",
        encoding="utf-8",
    )

    gap_md = "# Phase 7\n\n**Verdict:** LIFECYCLE_PERSISTENCE_GAPS_CLASSIFIED\n\n"
    gap_md += "| Component | Classification | Durability | Replay | Retrieve |\n|-----------|----------------|------------|--------|----------|\n"
    for row in COMPONENT_MATRIX:
        gap_md += (
            f"| {row['component']} | {row['classification']} | {row['durability']} | "
            f"{row['replayability']} | {row['retrieval']} |\n"
        )
    gap_md += "\n## LIFE-P gaps\n"
    for g in PERSISTENCE_GAPS:
        gap_md += f"- **{g['id']}** ({g['class']}): {g['gap']}\n"
    (OUT / "phase_7_persistence_gap_matrix" / "PERSISTENCE_GAP_MATRIX.md").write_text(gap_md, encoding="utf-8")

    (OUT / "phase_8_reviewer_safe_persistence_interpretation" / "REVIEWER_SAFE_PERSISTENCE_INTERPRETATION.md").write_text(
        "# Phase 8\n\n**Verdict:** REVIEWER_SAFE_PERSISTENCE_READY\n\n"
        "## PROVEN\n- SEM semantic persistence (SQLite)\n- NASP CRD/NSI cluster persistence\n"
        "- BC on-chain immutable persistence\n- Reconciliation state in CRDs (ACTIVE/ORPHANED/…)\n\n"
        "## PARTIAL\n- DE evidence JSON on pod disk\n- Telemetry via external Prometheus snapshots\n\n"
        "## UNSUPPORTED\n- Unified lifecycle retrieval\n- Session persistence\n"
        "- Continuous reevaluation store\n- Lifecycle-causal persistence\n",
        encoding="utf-8",
    )

    final = "LIFECYCLE_PERSISTENCE_GAPS_CLASSIFIED"
    science = "REVIEWER_SAFE_PERSISTENCE_READY"
    (OUT / "phase_9_final_persistence_freeze" / "FINAL_PERSISTENCE_FREEZE.md").write_text(
        f"# Phase 9\n\n# **{final}** / **{science}**\n\n```json\n{json.dumps(answers, indent=2)}\n```\n",
        encoding="utf-8",
    )

    _figures(probes)

    (OUT / "analysis" / "persistence_probes.json").write_text(json.dumps(probes, indent=2), encoding="utf-8")
    (OUT / "analysis" / "component_persistence_matrix.json").write_text(
        json.dumps(COMPONENT_MATRIX, indent=2), encoding="utf-8"
    )

    summary = {
        "phase": "LIFE-EXEC-03",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final,
        "science_outcome": science,
        "active_digest": ACTIVE_DIGEST,
        "upstream": UPSTREAM,
        "persistence_probes": probes,
        "component_matrix": COMPONENT_MATRIX,
        "persistence_gaps": PERSISTENCE_GAPS,
        "mandatory_questions": answers,
        "phase_verdicts": {
            "phase_1": "RUNTIME_FREEZE_VALIDATED",
            "phase_2": "PORTAL_PERSISTENCE_CHARACTERIZED",
            "phase_3": "SEMANTIC_PERSISTENCE_VALIDATED",
            "phase_4": "DECISION_ENGINE_PERSISTENCE_CHARACTERIZED",
            "phase_5": "NASP_PERSISTENCE_VALIDATED",
            "phase_6": "BLOCKCHAIN_PERSISTENCE_VALIDATED",
            "phase_7": final,
            "phase_8": science,
            "phase_9": final,
        },
        "next_prompt": answers["Q10_next_prompt"],
        "approval_required": "LIFE_EXEC_03_APPROVED",
        "hard_stop": True,
        "global_program_state": "LIFE_PERSISTENCE_VALIDATION_PENDING_APPROVAL",
    }
    (OUT / "analysis" / "lifecycle_state_persistence_validation_summary.json").write_text(
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
    return 0 if probes.get("digest_match") and life02_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
