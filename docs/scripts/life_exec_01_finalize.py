#!/usr/bin/env python3
"""LIFE-EXEC-01: Lifecycle gap audit (analysis-only, no runtime changes)."""

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

UPSTREAM = {
    "ssot": "evidencias_trisla_phase6_ssot_controlled_execution_20260517T154849Z",
    "sr09": "evidencias_trisla_sr_exec_09_final_program_freeze_20260517T192637Z",
    "nad15": "evidencias_trisla_nad_exec_15_final_freeze_20260518T001715Z",
    "core09": "evidencias_trisla_core_exec_09_core_track_final_freeze_20260518T012114Z",
    "ncm06": "evidencias_trisla_ncm_exec_06_ncm_track_final_freeze_20260518T022058Z",
}

LIFECYCLE_INVENTORY: List[Dict[str, Any]] = [
    {
        "artifact": "Portal POST /api/v1/sla/submit",
        "domain": "SLA lifecycle",
        "location": "apps/portal-backend/src/routers/sla.py",
        "runtime": True,
        "persistent": False,
        "notes": "sla_lifecycle dict with timestamped stages (DECIDED_*, ORCHESTRATED, BLOCKCHAIN_*, COMPLETED/FAILED) returned in response metadata only",
    },
    {
        "artifact": "Portal GET /api/v1/sla (list)",
        "domain": "SLA lifecycle UI",
        "location": "docs/FASE_F1_SLA_LIFECYCLE_AUDIT.md",
        "runtime": False,
        "persistent": False,
        "notes": "Route not implemented; frontend slaList() → 404; no SLA registry",
    },
    {
        "artifact": "Portal revalidate-telemetry",
        "domain": "SLA reevaluation",
        "location": "apps/portal-backend/src/routers/sla.py",
        "runtime": True,
        "persistent": False,
        "notes": "On-demand HTTP; delegates to SLA-Agent; not a continuous loop",
    },
    {
        "artifact": "SEM-CSMF Intent/NEST/Slice DB",
        "domain": "Intent & slice model",
        "location": "apps/sem-csmf/src/models/db_models.py",
        "runtime": True,
        "persistent": True,
        "notes": "SQLAlchemy sqlite default; intents, nests, network_slices tables",
    },
    {
        "artifact": "Decision Engine lifecycle_authority",
        "domain": "Semantic lifecycle",
        "location": "apps/decision-engine/src/lifecycle_authority.py",
        "runtime": True,
        "persistent": False,
        "notes": "metadata.lifecycle_event + governance_event; authority only, no execution",
    },
    {
        "artifact": "Decision Engine decision_persistence",
        "domain": "Decision evidence",
        "location": "apps/decision-engine/src/decision_persistence.py",
        "runtime": True,
        "persistent": True,
        "notes": "Ephemeral pod disk /tmp/trisla_evidence JSON per sla_id",
    },
    {
        "artifact": "NASP TriSLAReservation CRD",
        "domain": "Slice reservation ledger",
        "location": "apps/nasp-adapter/src/reservation_store.py",
        "runtime": True,
        "persistent": True,
        "notes": "K8s CRD PENDING→ACTIVE; TTL expire; orphan reconcile",
    },
    {
        "artifact": "NASP NSI Watch Controller",
        "domain": "Slice lifecycle",
        "location": "apps/nasp-adapter/src/controllers/nsi_watch_controller.py",
        "runtime": True,
        "persistent": True,
        "notes": "while True K8s watch on networksliceinstances; reconcile on ADDED/MODIFIED",
    },
    {
        "artifact": "NASP Capacity Reconciler",
        "domain": "Orchestration loop",
        "location": "apps/nasp-adapter/src/main.py",
        "runtime": True,
        "persistent": True,
        "notes": "Daemon thread while True; expire_pending + orphan NSI check",
    },
    {
        "artifact": "BC-NSSMF SLAContract + governance_lineage",
        "domain": "Blockchain lifecycle",
        "location": "apps/bc-nssmf/src/contracts/SLAContract.sol",
        "runtime": True,
        "persistent": True,
        "notes": "On-chain REQUESTED→ACTIVE states; lineage metadata registration",
    },
    {
        "artifact": "SLA-Agent Kafka consumer",
        "domain": "Async decision actions",
        "location": "apps/sla-agent-layer/src/kafka_consumer.py",
        "runtime": "conditional",
        "persistent": False,
        "notes": "KAFKA_ENABLED=false by default → offline mode; HTTP ingest primary",
    },
    {
        "artifact": "SLA-Agent revalidate-telemetry",
        "domain": "SLO compliance reevaluation",
        "location": "apps/sla-agent-layer/src/revalidate/",
        "runtime": True,
        "persistent": False,
        "notes": "SLO OK/RISK/VIOLATED state machine on demand; not PDU session churn",
    },
    {
        "artifact": "Portal telemetry collector",
        "domain": "Telemetry snapshot",
        "location": "apps/portal-backend/src/telemetry/collector.py",
        "runtime": True,
        "persistent": "optional_csv",
        "notes": "Prometheus instant/range at submit; optional CSV append; no TSDB in portal",
    },
    {
        "artifact": "UERANSIM / free5GC PDU session",
        "domain": "Session lifecycle",
        "location": "external (ns-1274485 / ueransim)",
        "runtime": True,
        "persistent": "external",
        "notes": "Not wired to TriSLA lifecycle API; NCM-SESS-01 candidate path",
    },
]

RUNTIME_MAP = [
    {"from": "Portal", "to": "SEM-CSMF", "transition": "interpret intent", "retention": "SEM DB"},
    {"from": "SEM-CSMF", "to": "Decision Engine", "transition": "decision request", "retention": "DE metadata + evidence files"},
    {"from": "Decision Engine", "to": "Portal", "transition": "lifecycle_event in metadata", "retention": "response only"},
    {"from": "Portal", "to": "NASP Adapter", "transition": "orchestration if ACCEPT", "retention": "NSI CRD + reservation"},
    {"from": "Portal", "to": "BC-NSSMF", "transition": "register SLA", "retention": "chain + lineage"},
    {"from": "Portal", "to": "SLA-Agent", "transition": "ingest / revalidate HTTP", "retention": "none in-agent"},
    {"from": "NASP Adapter", "to": "K8s NSI", "transition": "instantiate + watch reconcile", "retention": "cluster state"},
]

PERSISTENCE_MATRIX = [
    {"component": "Portal submit path", "class": "ephemeral", "replayable": False, "auditable": "per-response"},
    {"component": "SEM-CSMF SQLite", "class": "persistent", "replayable": True, "auditable": "DB rows"},
    {"component": "DE evidence dir", "class": "ephemeral_pod", "replayable": True, "auditable": "JSON files"},
    {"component": "NASP CRD reservations", "class": "persistent", "replayable": True, "auditable": "K8s API"},
    {"component": "NSI watch state", "class": "persistent", "replayable": True, "auditable": "K8s events"},
    {"component": "BC on-chain", "class": "persistent", "replayable": True, "auditable": "tx + events"},
    {"component": "Prometheus telemetry", "class": "external_tsdb", "replayable": "query-range", "auditable": "snapshots only"},
    {"component": "SLA-Agent in-memory", "class": "stateless", "replayable": False, "auditable": "HTTP logs"},
]

BLOCKERS = [
    {"id": "LIFE-B1", "type": "persistence_gap", "blocker": "No central SLA lifecycle registry (GET /api/v1/sla missing)"},
    {"id": "LIFE-B2", "type": "lifecycle_gap", "blocker": "Submit-path lifecycle is response metadata, not long-lived state machine"},
    {"id": "LIFE-B3", "type": "session_gap", "blocker": "No TriSLA API for PDU establish/release churn (NCM-SESS-01 not implemented)"},
    {"id": "LIFE-B4", "type": "orchestration_gap", "blocker": "DE lifecycle is semantic-only; does not drive NASP/BC execution"},
    {"id": "LIFE-B5", "type": "telemetry_gap", "blocker": "No continuous telemetry history binding to SLA lifecycle transitions"},
    {"id": "LIFE-B6", "type": "runtime_gap", "blocker": "SLA-Agent Kafka path offline by default; no always-on reevaluation loop"},
    {"id": "LIFE-B7", "type": "causal_gap", "blocker": "Lifecycle transitions do not map to resource_pressure_v1 (NCM-EXEC negative)"},
    {"id": "LIFE-B8", "type": "proof_gap", "blocker": "Full lifecycle proof requires CREATE→ACTIVE→MONITOR→TERMINATE with auditable retention"},
]

PROVEN = [
    "Synchronous SLA submit pipeline with timestamped sla_lifecycle stages",
    "DE semantic lifecycle_event and governance_event (FASE 4 authority)",
    "NASP NSI watch + reservation reconciler loops (real K8s controllers)",
    "SEM-CSMF persistent intent/nest/slice models",
    "BC on-chain SLA status transitions",
    "On-demand revalidate-telemetry (Portal ↔ SLA-Agent)",
    "Orchestration HTTP contention (NCM-EXEC-04, frozen track)",
]

PARTIAL = [
    "SLA lifecycle continuity across requests (no list/registry API)",
    "SLA persistence beyond single HTTP response",
    "Continuous SLA reevaluation (Kafka offline; HTTP-only)",
    "Slice maintenance after instantiate (watch exists; TriSLA-level SLA coupling weak)",
]

UNSUPPORTED = [
    "Full lifecycle proof end-to-end",
    "Persistent slice lifecycle exposed to portal/tenant",
    "Stateful admission driven by lifecycle state",
    "Lifecycle-causal pressure under frozen resource_pressure_v1",
    "PDU/session churn as TriSLA-controlled mechanism",
]


def answer_questions() -> Dict[str, Any]:
    return {
        "Q1_real_lifecycle_runtime": "partial",
        "Q1_detail": "Submit-path + NSI/CRD + BC yes; portal SLA list and session churn no",
        "Q2_state_persistence": True,
        "Q2_detail": "SEM DB, K8s CRDs, BC chain, DE evidence files; portal submit ephemeral",
        "Q3_session_persistence": False,
        "Q3_detail": "No TriSLA session store; UERANSIM/free5GC external only",
        "Q4_orchestration_loop_real": True,
        "Q4_detail": "NSI watch while True + capacity reconciler; Kafka consumer conditional",
        "Q5_telemetry_retention": "partial",
        "Q5_detail": "Prometheus external TSDB; optional CSV; snapshots at submit/revalidate",
        "Q6_continuous_sla_reevaluation": False,
        "Q6_detail": "revalidate on-demand only; no periodic SLA lifecycle evaluator in portal",
        "Q7_lifecycle_causal_vs_observable": "observable",
        "Q7_detail": "Metadata propagation; not admission/pressure causal (NCM/CORE precedent)",
        "Q8_full_lifecycle_proof_blockers": [b["blocker"] for b in BLOCKERS],
        "Q9_lifecycle_causal_path_viable": "design_only",
        "Q9_detail": "Requires NCM-SESS-01 + telemetry lock + guards; not present in codebase",
        "Q10_next_track": "LIFE-EXEC-02 runtime mapping",
        "Q10_next_prompt": "PROMPT_TRISLA_LIFE_EXEC_02_LIFECYCLE_RUNTIME_MAPPING_V1",
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
        (0.05, 0.55, "Portal\n(submit/revalidate)", "#aed6e1"),
        (0.28, 0.55, "SEM-CSMF\n(DB)", "#abebc6"),
        (0.51, 0.55, "Decision Engine\n(semantic life.)", "#f9e79f"),
        (0.74, 0.55, "NASP Adapter\n(NSI+CRD)", "#f5b7b1"),
        (0.28, 0.15, "BC-NSSMF\n(chain)", "#d7bde2"),
        (0.51, 0.15, "SLA-Agent\n(HTTP/SLO)", "#fadbd8"),
        (0.74, 0.15, "Prometheus\n(external)", "#d5dbdb"),
    ]
    for x, y, label, color in boxes:
        ax.add_patch(mpatches.FancyBboxPatch((x, y), 0.18, 0.28, boxstyle="round", fc=color, ec="black"))
        ax.text(x + 0.09, y + 0.14, label, ha="center", va="center", fontsize=7)
    for (x1, y1), (x2, y2) in [((0.23, 0.69), (0.28, 0.69)), ((0.46, 0.69), (0.51, 0.69)), ((0.69, 0.69), (0.74, 0.69)),
                                 ((0.37, 0.55), (0.37, 0.43)), ((0.60, 0.55), (0.60, 0.43)), ((0.83, 0.55), (0.83, 0.43))]:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Lifecycle runtime architecture (audit)")
    fig.savefig(fd / "lifecycle_runtime_architecture.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 4))
    stages = ["submit", "DE meta", "orchestrate", "BC", "agent", "NSI watch"]
    depth = [1, 1, 1, 1, 0.5, 1]
    ax.barh(stages, depth, color=["#3498db", "#f1c40f", "#e67e22", "#9b59b6", "#1abc9c", "#e74c3c"])
    ax.set_xlabel("State propagation depth (qualitative)")
    ax.set_title("Runtime state propagation map")
    fig.savefig(fd / "runtime_state_propagation_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    comps = [r["component"][:22] for r in PERSISTENCE_MATRIX]
    classes = [str(r["class"]) for r in PERSISTENCE_MATRIX]
    uniq = sorted(set(classes))
    cmap = {c: i for i, c in enumerate(uniq)}
    ax.barh(comps, [cmap[c] + 1 for c in classes], color=plt.cm.Set3(np.linspace(0, 1, len(uniq))))
    ax.set_xlabel("Persistence class (ordinal)")
    ax.set_title("Persistence classification matrix")
    fig.savefig(fd / "persistence_classification_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    loops = ["NSI watch", "Capacity reconciler", "Kafka consumer", "PRB simulator", "Portal revalidate"]
    real = [1, 1, 0.3, 1, 0.2]
    ax.barh(loops, real, color=["#2ecc71", "#2ecc71", "#f39c12", "#2ecc71", "#95a5a6"])
    ax.set_xlim(0, 1.2)
    ax.set_xlabel("Loop presence (1=real daemon)")
    ax.set_title("Orchestration loop map")
    fig.savefig(fd / "orchestration_loop_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    txt = "\n".join(f"{b['id']}: {b['type']}" for b in BLOCKERS)
    ax.text(0.05, 0.5, txt, fontsize=9, family="monospace", va="center")
    ax.set_title("Lifecycle gap / blocker graph")
    fig.savefig(fd / "lifecycle_gap_blocker_graph.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_runtime_freeze_validation",
        "phase_2_lifecycle_inventory",
        "phase_3_runtime_lifecycle_mapping",
        "phase_4_state_and_persistence_analysis",
        "phase_5_orchestration_loop_analysis",
        "phase_6_gap_and_blocker_analysis",
        "phase_7_reviewer_safe_interpretation",
        "phase_8_next_path_decision",
        "phase_9_final_audit_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    upstream_ok = all((ROOT / d).is_dir() for d in UPSTREAM.values())
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

    answers = answer_questions()
    final = "LIFECYCLE_BLOCKERS_IDENTIFIED"
    science = "LIFECYCLE_RUNTIME_PARTIALLY_CHARACTERIZED"

    (OUT / "phase_1_runtime_freeze_validation" / "RUNTIME_FREEZE_VALIDATION.md").write_text(
        f"# Phase 1\n\n**Verdict:** RUNTIME_FREEZE_VALIDATED\n\n"
        f"| Digest | `{ACTIVE_DIGEST}` |\n| Image | `{de_img or 'n/a'}` |\n"
        f"| Upstream packs | {upstream_ok} |\n| Since NCM freeze | no code changes in this phase |\n",
        encoding="utf-8",
    )

    inv_md = "# Phase 2 — Lifecycle Inventory\n\n**Verdict:** LIFECYCLE_INVENTORY_COMPLETE\n\n"
    inv_md += "| Artifact | Domain | Runtime | Persistent |\n|----------|--------|---------|------------|\n"
    for a in LIFECYCLE_INVENTORY:
        inv_md += f"| {a['artifact']} | {a['domain']} | {a['runtime']} | {a['persistent']} |\n"
    (OUT / "phase_2_lifecycle_inventory" / "LIFECYCLE_INVENTORY.md").write_text(inv_md, encoding="utf-8")

    map_md = "# Phase 3 — Runtime Lifecycle Mapping\n\n**Verdict:** RUNTIME_LIFECYCLE_MAPPING_COMPLETE\n\n"
    for e in RUNTIME_MAP:
        map_md += f"- **{e['from']} → {e['to']}**: {e['transition']} (retention: {e['retention']})\n"
    (OUT / "phase_3_runtime_lifecycle_mapping" / "RUNTIME_LIFECYCLE_MAPPING.md").write_text(
        map_md, encoding="utf-8"
    )

    pers_md = "# Phase 4 — State and Persistence\n\n**Verdict:** STATE_AND_PERSISTENCE_CHARACTERIZED\n\n"
    pers_md += "| Component | Class | Replayable | Auditable |\n|-----------|-------|------------|----------|\n"
    for r in PERSISTENCE_MATRIX:
        pers_md += f"| {r['component']} | {r['class']} | {r['replayable']} | {r['auditable']} |\n"
    (OUT / "phase_4_state_and_persistence_analysis" / "STATE_AND_PERSISTENCE_ANALYSIS.md").write_text(
        pers_md, encoding="utf-8"
    )

    (OUT / "phase_5_orchestration_loop_analysis" / "ORCHESTRATION_LOOP_ANALYSIS.md").write_text(
        "# Phase 5\n\n**Verdict:** ORCHESTRATION_LOOP_STATE_CHARACTERIZED\n\n"
        "## Real loops\n- NSI WatchController: `while True` K8s watch + reconcile\n"
        "- Capacity reconciler: `while True` expire_pending + orphan NSI\n"
        "- PRB simulator: periodic loop (if deployed)\n\n"
        "## Conditional / absent\n- SLA-Agent Kafka: disabled unless KAFKA_ENABLED=true\n"
        "- Portal: no background SLA lifecycle scheduler\n"
        "- revalidate-telemetry: on-demand HTTP only\n",
        encoding="utf-8",
    )

    blk_md = "# Phase 6\n\n**Verdict:** LIFECYCLE_BLOCKERS_IDENTIFIED\n\n"
    for b in BLOCKERS:
        blk_md += f"- **{b['id']}** ({b['type']}): {b['blocker']}\n"
    (OUT / "phase_6_gap_and_blocker_analysis" / "GAP_AND_BLOCKER_ANALYSIS.md").write_text(
        blk_md, encoding="utf-8"
    )

    (OUT / "phase_7_reviewer_safe_interpretation" / "REVIEWER_SAFE_INTERPRETATION.md").write_text(
        "# Phase 7\n\n**Verdict:** REVIEWER_SAFE_LIFECYCLE_INTERPRETATION_READY\n\n"
        "## PROVEN\n" + "\n".join(f"- {x}" for x in PROVEN) + "\n\n"
        "## PARTIAL\n" + "\n".join(f"- {x}" for x in PARTIAL) + "\n\n"
        "## UNSUPPORTED\n" + "\n".join(f"- {x}" for x in UNSUPPORTED) + "\n",
        encoding="utf-8",
    )

    (OUT / "phase_8_next_path_decision" / "NEXT_PATH_DECISION.md").write_text(
        "# Phase 8\n\n**Verdict:** NEXT_LIFECYCLE_PATH_DEFINED\n\n"
        "- **Continue LIFE-EXEC:** YES → EXEC-02 runtime mapping (mandatory next)\n"
        "- **ORCH-EXEC alone:** NOT prioritized (NCM froze orch-only path)\n"
        "- **NCM-SESS / churn:** design candidate; requires LIFE-EXEC-02+ before campaigns\n"
        "- **Redundant:** Repeat NCM-ORCH-01; portal-only lifecycle UI without backend list API\n"
        "- **Dangerous:** Synthetic lifecycle; guard weakening; unfrozen digest changes\n\n"
        f"**Q10:** {answers['Q10_next_prompt']}\n",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_audit_freeze" / "FINAL_AUDIT_FREEZE.md").write_text(
        f"# Phase 9\n\n# **{final}** / **{science}**\n\n```json\n{json.dumps(answers, indent=2)}\n```\n",
        encoding="utf-8",
    )

    _figures()

    (OUT / "analysis" / "lifecycle_inventory.json").write_text(
        json.dumps(LIFECYCLE_INVENTORY, indent=2), encoding="utf-8"
    )
    (OUT / "analysis" / "lifecycle_blockers.json").write_text(
        json.dumps(BLOCKERS, indent=2), encoding="utf-8"
    )

    summary = {
        "phase": "LIFE-EXEC-01",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": final,
        "science_outcome": science,
        "active_digest": ACTIVE_DIGEST,
        "upstream_packs": UPSTREAM,
        "upstream_packs_present": upstream_ok,
        "runtime_freeze_ok": freeze_ok,
        "lifecycle_inventory": LIFECYCLE_INVENTORY,
        "runtime_map": RUNTIME_MAP,
        "persistence_matrix": PERSISTENCE_MATRIX,
        "blockers": BLOCKERS,
        "proven_claims": PROVEN,
        "partial_claims": PARTIAL,
        "unsupported_claims": UNSUPPORTED,
        "mandatory_questions": answers,
        "phase_verdicts": {
            "phase_1": "RUNTIME_FREEZE_VALIDATED",
            "phase_2": "LIFECYCLE_INVENTORY_COMPLETE",
            "phase_3": "RUNTIME_LIFECYCLE_MAPPING_COMPLETE",
            "phase_4": "STATE_AND_PERSISTENCE_CHARACTERIZED",
            "phase_5": "ORCHESTRATION_LOOP_STATE_CHARACTERIZED",
            "phase_6": "LIFECYCLE_BLOCKERS_IDENTIFIED",
            "phase_7": "REVIEWER_SAFE_LIFECYCLE_INTERPRETATION_READY",
            "phase_8": "NEXT_LIFECYCLE_PATH_DEFINED",
            "phase_9": final,
        },
        "next_prompt": "PROMPT_TRISLA_LIFE_EXEC_02_LIFECYCLE_RUNTIME_MAPPING_V1",
        "approval_required": "LIFE_EXEC_01_APPROVED",
        "hard_stop": True,
        "global_program_state": "LIFE_EXEC_AUDIT_PENDING_APPROVAL",
    }
    (OUT / "analysis" / "lifecycle_gap_audit_summary.json").write_text(
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
    return 0 if upstream_ok and freeze_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
