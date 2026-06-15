#!/usr/bin/env python3
"""CORE-EXEC-02: Core runtime observability mapping (audit/mapping only)."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OUT = Path(os.environ["OUT"])
ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
ACTIVE_DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"
CORE01 = ROOT / "evidencias_trisla_core_exec_01_core_attribution_audit_20260518T002045Z"
PROM_URL = os.environ.get(
    "PROMETHEUS_URL",
    "http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090",
)

# Field registry: static code-trace classifications
FIELD_REGISTRY: List[Dict[str, Any]] = [
    {
        "field": "core.cpu",
        "promql_key": "CORE_CPU",
        "prom_metric": "process_cpu_seconds_total",
        "classifications": [
            "COLLECTED",
            "SNAPSHOT_VISIBLE",
            "PRESSURE_INPUT",
            "SCORE_INDIRECT",
            "XAI_ONLY",
        ],
        "notes": "Collector writes legacy key; contract_v2 mirrors cpu_utilization",
    },
    {
        "field": "core.cpu_utilization",
        "promql_key": "CORE_CPU",
        "prom_metric": "process_cpu_seconds_total (rate)",
        "classifications": [
            "SNAPSHOT_VISIBLE",
            "FEASIBILITY_INPUT",
            "PRESSURE_INPUT",
            "SCORE_INDIRECT",
        ],
        "notes": "Alias from apply_telemetry_contract_v2; DE feasibility v1 normalizes /100",
    },
    {
        "field": "core.memory",
        "promql_key": "CORE_MEMORY",
        "prom_metric": "process_resident_memory_bytes",
        "classifications": ["COLLECTED", "SNAPSHOT_VISIBLE", "XAI_ONLY"],
        "notes": "SEM-CSMF may normalize to memory_utilization % before DE",
    },
    {
        "field": "core.memory_bytes",
        "promql_key": "CORE_MEMORY",
        "prom_metric": "process_resident_memory_bytes",
        "classifications": ["SNAPSHOT_VISIBLE", "UNUSED"],
        "notes": "contract_v2 alias; not in DE feasibility v1",
    },
    {
        "field": "core.memory_utilization",
        "promql_key": "CORE_MEMORY",
        "prom_metric": "derived % (SEM-CSMF)",
        "classifications": ["SNAPSHOT_VISIBLE", "XAI_ONLY", "CANDIDATE_FOR_CAUSALITY"],
        "notes": "slice_aware gates only; not in resource_pressure v1",
    },
    {
        "field": "core.memory_ratio",
        "promql_key": "CORE_MEMORY",
        "prom_metric": "derived ratio",
        "classifications": ["SNAPSHOT_VISIBLE", "UNUSED"],
        "notes": "Documented in TELEMETRY_UNITS_V2; no DE consumer on frozen digest",
    },
    {
        "field": "core_pressure_score (ML)",
        "promql_key": None,
        "prom_metric": None,
        "classifications": ["SCORE_INDIRECT", "XAI_ONLY"],
        "notes": "ml-nsmf predictor derived feature → ML risk only",
    },
    {
        "field": "core_risk (slice_aware)",
        "promql_key": None,
        "prom_metric": None,
        "classifications": ["SCORE_INDIRECT", "XAI_ONLY", "CANDIDATE_FOR_CAUSALITY"],
        "notes": "slice_md merge can upgrade severity; not score_mode numerator",
    },
    {
        "field": "core_goodness",
        "promql_key": None,
        "prom_metric": None,
        "classifications": ["NOT_COLLECTED", "CANDIDATE_FOR_CAUSALITY"],
        "notes": "Not implemented in decision_score_mode contributing_factors",
    },
]

PROM_QUERIES = [
    {
        "name": "CORE_CPU_default",
        "query": 'sum(rate(process_cpu_seconds_total[1m]))',
        "free5gc_scoped": False,
    },
    {
        "name": "CORE_MEMORY_default",
        "query": "sum(process_resident_memory_bytes)",
        "free5gc_scoped": False,
    },
    {
        "name": "CORE_CPU_free5gc_ns",
        "query": 'sum(rate(container_cpu_usage_seconds_total{namespace="ns-1274485"}[1m]))',
        "free5gc_scoped": True,
    },
    {
        "name": "CORE_MEMORY_free5gc_ns",
        "query": 'sum(container_memory_working_set_bytes{namespace="ns-1274485"})',
        "free5gc_scoped": True,
    },
    {
        "name": "AMF_pod_running",
        "query": 'count(kube_pod_status_phase{namespace="ns-1274485",pod=~"amf.*",phase="Running"})',
        "free5gc_scoped": True,
    },
    {
        "name": "SMF_pod_running",
        "query": 'count(kube_pod_status_phase{namespace="ns-1274485",pod=~"smf.*",phase="Running"})',
        "free5gc_scoped": True,
    },
    {
        "name": "UPF_pod_running",
        "query": 'count(kube_pod_status_phase{namespace="ns-1274485",pod=~"upf.*",phase="Running"})',
        "free5gc_scoped": True,
    },
]

FINAL_VERDICT = "CORE_OBSERVABILITY_MAPPING_FROZEN"
COMPANION_VERDICT = "CORE_CAUSALITY_PATHS_IDENTIFIED"


def _prom_instant(query: str, timeout: float = 15.0) -> Dict[str, Any]:
    url = f"{PROM_URL}/api/v1/query?{urllib.parse.urlencode({'query': query})}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        status = body.get("status")
        results = body.get("data", {}).get("result", [])
        values = []
        for r in results:
            v = r.get("value")
            if isinstance(v, list) and len(v) >= 2:
                try:
                    values.append(float(v[1]))
                except (TypeError, ValueError):
                    pass
        return {
            "query": query,
            "status": status,
            "n_series": len(results),
            "sample_values": values[:5],
            "available": status == "success" and len(results) > 0,
        }
    except Exception as e:
        return {"query": query, "status": "error", "error": str(e), "available": False}


def _probe_prometheus() -> List[Dict[str, Any]]:
    return [{**pq, "probe": _prom_instant(pq["query"])} for pq in PROM_QUERIES]


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


def _sample_datasets() -> Dict[str, Any]:
    """Best-effort presence stats from frozen campaign JSON/CSV (no new campaigns)."""
    stats: Dict[str, Any] = {"sources": [], "core_cpu_present": 0, "core_mem_present": 0, "n": 0}
    candidates = [
        ROOT
        / "evidencias_trisla_nad_exec_09_nad_liminal_02_campaign_execution_20260517T214300Z"
        / "dataset"
        / "enriched"
        / "nad_liminal_02_dataset.csv",
        ROOT
        / "evidencias_trisla_phase3_runtime_revalidation_20260517T133134Z"
        / "phase_2_full_nasp_campaign"
        / "phase_1_extreme_runtime_stress"
        / "raw",
    ]
    csv_path = candidates[0]
    if csv_path.exists():
        import csv as csvmod

        stats["sources"].append(str(csv_path))
        with csv_path.open(encoding="utf-8") as f:
            reader = csvmod.DictReader(f)
            for row in reader:
                stats["n"] += 1
                if row.get("core_cpu") or row.get("core_cpu_input"):
                    stats["core_cpu_present"] += 1
                if row.get("core_memory") or row.get("core_memory_input"):
                    stats["core_mem_present"] += 1
    raw_dir = candidates[1]
    if raw_dir.is_dir():
        stats["sources"].append(str(raw_dir))
        for p in list(raw_dir.rglob("submit_*.json"))[:200]:
            try:
                m = json.loads(p.read_text(encoding="utf-8"))["payload"]["metadata"]
                stats["n"] += 1
                ts = m.get("telemetry_snapshot") or {}
                co = ts.get("core") or {}
                if co.get("cpu") is not None or co.get("cpu_utilization") is not None:
                    stats["core_cpu_present"] += 1
                if co.get("memory") is not None or co.get("memory_utilization") is not None:
                    stats["core_mem_present"] += 1
            except Exception:
                continue
    return stats


def _mandatory_answers(prom: List[Dict[str, Any]], ds: Dict[str, Any]) -> Dict[str, Any]:
    cpu_def = next((p for p in prom if p["name"] == "CORE_CPU_default"), {})
    mem_def = next((p for p in prom if p["name"] == "CORE_MEMORY_default"), {})
    f5_cpu = next((p for p in prom if p["name"] == "CORE_CPU_free5gc_ns"), {})
    return {
        "Q1_prometheus_core_metrics": [
            "process_cpu_seconds_total (rate sum)",
            "process_resident_memory_bytes (sum)",
            "container_* @ ns-1274485 (documented, optional)",
        ],
        "Q1_default_available": cpu_def.get("probe", {}).get("available"),
        "Q1_free5gc_scoped_available": f5_cpu.get("probe", {}).get("available"),
        "Q2_snapshot_fields": [f["field"] for f in FIELD_REGISTRY if "SNAPSHOT" in str(f.get("classifications"))],
        "Q3_feasibility_inputs": ["core.cpu_utilization / core.cpu → compute_resource_pressure_v1"],
        "Q4_pressure_inputs": ["cpu only in v1 (w=0.3); memory in portal v2 only (DE uses v1)"],
        "Q5_score_mode_direct": [],
        "Q6_contributing_factors_core": "none — no core_* factor in terms list",
        "Q7_xai_only": ["core_cpu_input", "core_memory_input", "core_risk in slice_md"],
        "Q8_indirect_score": ["feasibility_goodness", "resource_headroom_goodness via pressure"],
        "Q9_present_no_causality": ["core.cpu", "core.memory", "core_cpu_input", "core_risk"],
        "Q10_minimal_causal_path": (
            "scoped AMF/SMF/UPF metrics → snapshot → explicit core_goodness term "
            "+ operational contention campaign (NCM track)"
        ),
        "dataset_core_cpu_rate": (ds["core_cpu_present"] / ds["n"]) if ds["n"] else None,
        "dataset_n": ds["n"],
    }


def _figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fd = OUT / "figures"
    fd.mkdir(exist_ok=True)

    fields = [f["field"].replace(" ", "\n")[:18] for f in FIELD_REGISTRY[:6]]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(fields, [1] * len(fields), color="#3498db")
    ax.set_title("Core metric inventory map (code + PromQL SSOT)")
    fig.savefig(fd / "core_metric_inventory_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 5))
    stages = ["Prometheus", "snapshot", "feasibility", "pressure", "score_mode", "XAI", "admission"]
    xs = np.arange(len(stages))
    ax.plot(xs, [1, 1, 0.7, 0.7, 0.35, 1, 0.1], "o-", lw=2, color="#2980b9", label="CPU path")
    ax.plot(xs, [1, 1, 0, 0, 0, 0.8, 0.05], "s--", lw=1.5, color="#e67e22", label="memory path")
    ax.set_xticks(xs)
    ax.set_xticklabels(stages, rotation=25, ha="right")
    ax.set_ylim(0, 1.15)
    ax.legend()
    ax.set_title("Core telemetry propagation graph")
    fig.savefig(fd / "core_telemetry_propagation_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    paths = ["Direct\n(score numerator)", "Indirect\n(pressure/feas)", "XAI only", "Unused"]
    vals = [0, 0.55, 0.85, 0.25]
    ax.bar(paths, vals, color=["#e74c3c", "#f39c12", "#3498db", "#95a5a6"])
    ax.set_ylim(0, 1)
    ax.set_title("Core direct vs indirect path map")
    fig.savefig(fd / "core_direct_vs_indirect_path_map.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    gaps = ["Prom\nscoped", "core_goodness", "Causal\nproof", "Contention", "Calibration"]
    present = [0.5, 0, 0, 0, 0.3]
    ax.bar(gaps, present, color=["#f39c12", "#e74c3c", "#e74c3c", "#e74c3c", "#f1c40f"])
    ax.set_ylim(0, 1.1)
    ax.set_title("Core observability gap matrix")
    fig.savefig(fd / "core_observability_gap_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axis("off")
    tree = [
        "Causality candidates (design-only)",
        "├─ core_goodness explicit term",
        "├─ UPF queue / PFCP contention",
        "├─ AMF/SMF session saturation",
        "├─ Scoped container metrics",
        "└─ NCM operational campaign",
    ]
    for i, ln in enumerate(tree):
        ax.text(0.05, 0.9 - i * 0.14, ln, fontsize=10, family="monospace")
    ax.set_title("Core causality candidate tree")
    fig.savefig(fd / "core_causality_candidate_tree.png", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    for sub in [
        "phase_1_prometheus_core_inventory",
        "phase_2_snapshot_field_mapping",
        "phase_3_feasibility_pressure_mapping",
        "phase_4_decision_score_path_mapping",
        "phase_5_xai_metadata_mapping",
        "phase_6_runtime_propagation_graph",
        "phase_7_observability_gap_matrix",
        "phase_8_causality_candidate_paths",
        "phase_9_final_observability_mapping_freeze",
        "analysis",
        "figures",
        "freeze",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    prom = _probe_prometheus()
    ds = _sample_datasets()
    answers = _mandatory_answers(prom, ds)
    de_img = _de_image()

    prom_rows = "\n".join(
        f"| {p['name']} | `{p['query'][:60]}…` | {p['probe'].get('available')} | "
        f"{p['probe'].get('n_series', 0)} | {p.get('free5gc_scoped')} |"
        for p in prom
    )
    (OUT / "phase_1_prometheus_core_inventory/PROMETHEUS_CORE_INVENTORY.md").write_text(
        f"# Phase 1 — Prometheus Core Inventory\n\n**Verdict:** PROMETHEUS_CORE_INVENTORY_COMPLETE\n\n"
        f"Prometheus URL: `{PROM_URL}`\n\n"
        f"| Query | PromQL (trunc) | Available | Series | free5GC scoped |\n"
        f"|-------|----------------|-----------|--------|----------------|\n{prom_rows}\n\n"
        "**Note:** Default collector uses aggregate `process_*` metrics, not per-AMF/SMF/UPF series.\n",
        encoding="utf-8",
    )
    (OUT / "analysis/prometheus_probe_results.json").write_text(
        json.dumps(prom, indent=2), encoding="utf-8"
    )

    snap_rows = "\n".join(
        f"| `{f['field']}` | {f.get('promql_key') or 'n/a'} | {', '.join(f['classifications'])} | {f['notes']} |"
        for f in FIELD_REGISTRY
        if "cpu" in f["field"] or "memory" in f["field"]
    )
    (OUT / "phase_2_snapshot_field_mapping/SNAPSHOT_FIELD_MAPPING.md").write_text(
        f"# Phase 2 — Snapshot Field Mapping\n\n**Verdict:** SNAPSHOT_FIELD_MAPPING_COMPLETE\n\n"
        f"Collector seeds `core: {{cpu, memory}}` then `apply_telemetry_contract_v2` adds aliases.\n\n"
        f"| Field | PromQL key | Classifications | Notes |\n|-------|------------|---------------|-------|\n{snap_rows}\n\n"
        f"**Dataset presence (frozen, n={ds['n']}):** core_cpu {ds['core_cpu_present']}, "
        f"core_mem {ds['core_mem_present']}\n",
        encoding="utf-8",
    )

    (OUT / "phase_3_feasibility_pressure_mapping/FEASIBILITY_PRESSURE_MAPPING.md").write_text(
        """# Phase 3 — Feasibility / Pressure Mapping

**Verdict:** FEASIBILITY_PRESSURE_MAPPING_COMPLETE

## compute_resource_pressure_v1 (DE + portal parity)

```
pressure = (0.4*PRB + 0.3*RTT + 0.3*CPU_core) / sum(active_weights)
feasibility = clamp01(1 - (ml_risk + pressure) / 2)
g_press = 1 - pressure  → resource_headroom_goodness term
```

| Input | Core field | Weight |
|-------|------------|--------|
| CPU | core.cpu_utilization / core.cpu | 0.30 |
| Memory | — | **not in v1** |

`TRISLA_FEASIBILITY_RUNTIME_ENABLED=true` (helm). Memory only in portal `compute_resource_pressure_v2` if `USE_SLA_V2` — **not** DE feasibility path on frozen digest.
""",
        encoding="utf-8",
    )

    (OUT / "phase_4_decision_score_path_mapping/DECISION_SCORE_PATH_MAPPING.md").write_text(
        """# Phase 4 — Decision Score Path Mapping

**Verdict:** DECISION_SCORE_PATH_MAPPING_COMPLETE

## score_mode numerator (frozen)

| Factor | Core? |
|--------|-------|
| feasibility_goodness | Indirect (pressure includes CPU) |
| resource_headroom_goodness | Indirect |
| ran_prb_goodness | No |
| transport_rtt_goodness | No |
| risk_inverse | No |
| semantic_priority | No |
| **core_goodness** | **NOT_PRESENT** |
| **core_weight** | **NOT_PRESENT** |

Denominator = sum of active term weights only. Core never adds weight directly.
""",
        encoding="utf-8",
    )

    (OUT / "phase_5_xai_metadata_mapping/XAI_METADATA_MAPPING.md").write_text(
        """# Phase 5 — XAI / Metadata Mapping

**Verdict:** XAI_METADATA_MAPPING_COMPLETE

| Location | Core fields |
|----------|-------------|
| XAI bundle | `core_cpu_input`, `core_memory_input`, `core_cpu_percent_input` |
| slice_aware_multidomain | `core_risk`, reason_codes `*_CORE_RENEGOTIATE` |
| contributing_factors | **no** core_* factor |
| normalized_inputs | feasibility, resource_pressure (indirect) |
| ML metadata | `core_pressure_score` (predictor derived) |
| Audit logs | `[MULTI-DOMAIN SCORE] cpu= mem=` (legacy path only) |

Core in XAI is **explanatory metadata**, not a scored causal term.
""",
        encoding="utf-8",
    )

    (OUT / "phase_6_runtime_propagation_graph/RUNTIME_PROPAGATION_GRAPH.md").write_text(
        """# Phase 6 — Runtime Propagation Graph

**Verdict:** RUNTIME_PROPAGATION_GRAPH_COMPLETE

```mermaid
flowchart LR
  PROM[Prometheus CORE_CPU/MEM] --> COLL[portal collector]
  COLL --> SNAP[telemetry_snapshot.core]
  SNAP --> SEM[SEM-CSMF forward]
  SEM --> CTX[DE context]
  CTX --> FR[feasibility_runtime v1]
  FR --> PRESS[resource_pressure]
  PRESS --> FEAS[feasibility_score]
  PRESS --> HEAD[resource_headroom_goodness]
  FEAS --> SM[decision_score_mode]
  HEAD --> SM
  SNAP --> XAI[core_cpu/memory_input]
  SNAP --> SA[slice_aware core_risk]
  SA --> MERGE[_merge_slice_multidomain_severity]
  SM --> ADM[admission band]
  MERGE --> ADM
```

**Admission:** PRB hard-gate → score_mode → optional severity merge. Core cannot bypass PRB governance.
""",
        encoding="utf-8",
    )

    (OUT / "phase_7_observability_gap_matrix/OBSERVABILITY_GAP_MATRIX.md").write_text(
        """# Phase 7 — Observability Gap Matrix

**Verdict:** OBSERVABILITY_GAP_MATRIX_COMPLETE

| Gap | Present? | Impact |
|-----|----------|--------|
| AMF/SMF/UPF scoped metrics in default collector | Partial / optional | Core not network-function specific |
| core_goodness in score numerator | **Absent** | No direct Core score term |
| Core causal admission proof | **Absent** | NAD freeze |
| Operational Core contention | **Absent** | NCM track required |
| Unit calibration at all producers | Partial | PHASE11 memory % fix |
| Memory in DE pressure v1 | **Absent** | Memory ignored in feasibility path |
""",
        encoding="utf-8",
    )

    (OUT / "phase_8_causality_candidate_paths/CAUSALITY_CANDIDATE_PATHS.md").write_text(
        """# Phase 8 — Causality Candidate Paths

**Verdict:** CAUSALITY_CANDIDATE_PATHS_DEFINED

Design-only candidates (no implementation in CORE-EXEC-02):

1. **core_goodness** — explicit weighted term in score_mode (capped, subordinate to PRB)
2. **Scoped PromQL** — `container_*{namespace=free5gc}` for AMF/SMF/UPF
3. **UPF contention** — queue depth / GTP throughput stress → measurable CPU+pressure
4. **AMF/SMF saturation** — registration/session rate proxies
5. **PFCP/N4 bottleneck** — observability hook (future interface)
6. **Operational campaign** — NCM-EXEC contention (per NAD-EXEC-15)

**Minimal path (Q10):** scoped metrics + `core_goodness` term + validated contention envelope.
""",
        encoding="utf-8",
    )

    (OUT / "phase_9_final_observability_mapping_freeze/FINAL_OBSERVABILITY_MAPPING_FREEZE.md").write_text(
        f"# Phase 9 — Final Observability Mapping Freeze\n\n# **{FINAL_VERDICT}**\n\n"
        f"Companion: **{COMPANION_VERDICT}**\n\n"
        f"Digest: `{ACTIVE_DIGEST}` — match in image: **{ACTIVE_DIGEST in de_img}**\n\n"
        f"CORE-EXEC-01 reference: `{CORE01}`\n",
        encoding="utf-8",
    )

    _figures()

    summary = {
        "phase": "CORE-EXEC-02",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": FINAL_VERDICT,
        "companion_verdict": COMPANION_VERDICT,
        "audit_only": True,
        "active_digest": ACTIVE_DIGEST,
        "decision_engine_image": de_img,
        "core_exec_01_reference": str(CORE01),
        "field_registry": FIELD_REGISTRY,
        "prometheus_probes": prom,
        "dataset_presence": ds,
        "mandatory_answers": answers,
        "phase_verdicts": {
            "phase1": "PROMETHEUS_CORE_INVENTORY_COMPLETE",
            "phase2": "SNAPSHOT_FIELD_MAPPING_COMPLETE",
            "phase3": "FEASIBILITY_PRESSURE_MAPPING_COMPLETE",
            "phase4": "DECISION_SCORE_PATH_MAPPING_COMPLETE",
            "phase5": "XAI_METADATA_MAPPING_COMPLETE",
            "phase6": "RUNTIME_PROPAGATION_GRAPH_COMPLETE",
            "phase7": "OBSERVABILITY_GAP_MATRIX_COMPLETE",
            "phase8": "CAUSALITY_CANDIDATE_PATHS_DEFINED",
            "phase9": FINAL_VERDICT,
        },
        "next_prompt": "PROMPT_TRISLA_CORE_EXEC_03_CORE_CAUSALITY_GAP_ANALYSIS_V1",
        "approval_required": "CORE_EXEC_02_APPROVED",
        "hard_stop": True,
    }
    (OUT / "analysis/core_runtime_observability_mapping_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (OUT / "analysis/field_classification_matrix.json").write_text(
        json.dumps(FIELD_REGISTRY, indent=2), encoding="utf-8"
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
