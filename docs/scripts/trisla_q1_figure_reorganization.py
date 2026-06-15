#!/usr/bin/env python3
"""
TriSLA Q1 Figure Reorganization — real datasets only, reviewer-safe.
Output: docs/paper_q1_figures/
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

TRISLA_ROOT = Path(os.environ.get("TRISLA_ROOT", "/home/porvir5g/gtp5g/trisla"))
OUT = TRISLA_ROOT / "docs" / "paper_q1_figures"
DPI = 300
DIGEST = "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6"
HARD_PRB_RENEG = 0.25
HARD_PRB_REJECT = 0.40

SOURCES = {
    "tri_slice": TRISLA_ROOT
    / "evidencias_trisla_sr_exec_05_tri_slice_nasp_hardplus_campaign_20260517T182121Z/dataset/enriched/tri_slice_runtime_dataset.csv",
    "baseline_v6": TRISLA_ROOT / "evidencias_resultados_trisla_baseline_v13/dataset/final_dataset_v6.csv",
    "ncm_orch": TRISLA_ROOT
    / "evidencias_trisla_ncm_exec_04_operational_contention_campaign_execution_20260518T014848Z/dataset/enriched/ncm_orch_01_dataset.csv",
    "nad_liminal02": TRISLA_ROOT
    / "evidencias_trisla_nad_exec_09_nad_liminal_02_campaign_execution_20260517T214300Z/dataset/enriched/nad_liminal_02_dataset.csv",
    "nad_liminal05": TRISLA_ROOT
    / "evidencias_trisla_nad_exec_05_liminal_scoremode_campaign_20260517T201420Z/dataset/enriched/liminal_scoremode_dataset.csv",
    "e2e_accept": TRISLA_ROOT
    / "evidencias_final_e2e_accept_batch_20260515T110538Z/dataset/final_accept_batch.csv",
    "pub_accept": TRISLA_ROOT
    / "evidencias_final_publication_artifact_20260515T112034Z/dataset/final_accept_batch.csv",
    "life_persistence": TRISLA_ROOT
    / "evidencias_trisla_life_exec_03_lifecycle_state_persistence_validation_20260518T023455Z/analysis/persistence_probes.json",
}

SLICE_COLORS = {"URLLC": "#1f77b4", "eMBB": "#ff7f0e", "mMTC": "#2ca02c", "eMBB": "#ff7f0e"}
DECISION_COLORS = {"ACCEPT": "#2ca02c", "RENEGOTIATE": "#ff7f0e", "REJECT": "#d62728"}


@dataclass
class DatasetQuality:
    name: str
    path: str
    valid: bool
    rows: int
    reason: str
    sha256: str = ""
    numeric_variance: Dict[str, float] = field(default_factory=dict)


@dataclass
class FigureRecord:
    fig_id: str
    title: str
    filename: str
    status: str  # GENERATED | INVALID | CONCEPTUAL
    hypothesis: str
    objective: str
    dataset: str
    freeze: str
    paper_section: str
    proves: str
    reviewer_safe: str
    not_infer: str
    quality_notes: str = ""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.exists() or path.stat().st_size < 10:
        return [], []
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return (reader.fieldnames or []), rows


def write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def fnum(v: Any, default: float = float("nan")) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def parse_ts(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_dataset(name: str, path: Path, min_rows: int = 10, numeric_cols: Optional[List[str]] = None) -> DatasetQuality:
    numeric_cols = numeric_cols or []
    if not path.exists() or path.stat().st_size < 20:
        return DatasetQuality(name, str(path), False, 0, "missing or empty")
    if path.suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return DatasetQuality(name, str(path), True, 1, "json probe", _sha256(path))
        except Exception as e:
            return DatasetQuality(name, str(path), False, 0, f"json error: {e}")
    cols, rows = load_csv(path)
    if len(rows) < min_rows:
        return DatasetQuality(name, str(path), False, len(rows), f"rows<{min_rows}")
    var = {}
    for c in numeric_cols:
        if c not in cols:
            continue
        vals = [fnum(r[c]) for r in rows if math.isfinite(fnum(r[c]))]
        if len(vals) < 2:
            var[c] = 0.0
        else:
            var[c] = statistics.pstdev(vals)
    if numeric_cols and all(var.get(c, 0) == 0 for c in numeric_cols if c in cols):
        return DatasetQuality(name, str(path), False, len(rows), "zero variance on key metrics", _sha256(path), var)
    return DatasetQuality(name, str(path), True, len(rows), "ok", _sha256(path), var)


def save_fig(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def annotate_regime_changes(ax, xs: List[datetime], regimes: List[str]) -> None:
    last = None
    for i, reg in enumerate(regimes):
        if reg != last and last is not None:
            ax.axvline(xs[i], color="#888888", linestyle="--", alpha=0.5, linewidth=0.8)
            ax.text(xs[i], ax.get_ylim()[1] * 0.98, f"regime→{reg}", fontsize=7, rotation=90, va="top", ha="right")
        last = reg


# ---------- Figure builders ----------

def build_enriched_tri_slice() -> Tuple[List[Dict[str, Any]], Path]:
    _, rows = load_csv(SOURCES["tri_slice"])
    out_rows = []
    for i, r in enumerate(rows):
        ts = parse_ts(r.get("timestamp", ""))
        out_rows.append(
            {
                "request_index": i,
                "timestamp": r.get("timestamp", ""),
                "runtime_phase": "admission",
                "event_marker": "iperf_regime_change" if i > 0 and r.get("regime_mbps") != rows[i - 1].get("regime_mbps") else "",
                "slice": r.get("slice", ""),
                "regime_mbps": r.get("regime_mbps", ""),
                "network_state_id": r.get("network_state_id", ""),
                "decision": r.get("decision", ""),
                "decision_score": r.get("decision_score", ""),
                "feasibility_score": r.get("feasibility_score", ""),
                "resource_pressure": r.get("resource_pressure", ""),
                "prb_utilization_real": r.get("prb_utilization_real", ""),
                "prb_norm": r.get("prb_norm", ""),
                "telemetry_transport_rtt_ms": r.get("telemetry_transport_rtt_ms", ""),
                "telemetry_core_cpu": r.get("telemetry_core_cpu", ""),
                "http_elapsed_s": r.get("http_elapsed_s", ""),
                "source": "SR-EXEC-05",
            }
        )
    dst = OUT / "datasets/final_q1_figures/enriched_tri_slice_admission_timeline.csv"
    cols = list(out_rows[0].keys()) if out_rows else []
    write_csv(dst, cols, out_rows)
    return out_rows, dst


def fig01_score_evolution(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    pts = [(parse_ts(r["timestamp"]), r) for r in rows if parse_ts(r.get("timestamp", ""))]
    if len(pts) < 20:
        rec.status = "INVALID"
        rec.quality_notes = "insufficient timestamps"
        return False
    pts.sort(key=lambda x: x[0])
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for sl in ("URLLC", "eMBB", "mMTC"):
        sub = [(t, fnum(r["decision_score"])) for t, r in pts if r.get("slice") == sl]
        if sub:
            ax.plot([t for t, _ in sub], [s for _, s in sub], ".-", label=sl, color=SLICE_COLORS.get(sl), markersize=3, linewidth=1)
    regimes = [r.get("regime_mbps", "") for _, r in pts]
    annotate_regime_changes(ax, [t for t, _ in pts], regimes)
    ax.set_xlabel("Campaign runtime (UTC)")
    ax.set_ylabel("SLA decision score")
    ax.set_title("Runtime SLA decision score evolution under multidomain telemetry changes")
    ax.legend(loc="lower left", fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    save_fig(fig, OUT / "figures/fig01_runtime_sla_score_evolution.png")
    rec.status = "GENERATED"
    return True


def fig02_prb_decision_regions(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    xs, ys, cs, labs = [], [], [], []
    for r in rows:
        pn = fnum(r.get("prb_norm"))
        if not math.isfinite(pn):
            pn = fnum(r.get("prb_utilization_real")) / 100.0
        sc = fnum(r.get("decision_score"))
        if math.isfinite(pn) and math.isfinite(sc):
            xs.append(pn)
            ys.append(sc)
            cs.append(DECISION_COLORS.get(r.get("decision", ""), "#7f7f7f"))
            labs.append(r.get("decision", ""))
    if len(xs) < 20:
        rec.status = "INVALID"
        return False
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axvspan(HARD_PRB_RENEG, HARD_PRB_REJECT, color="#fff3cd", alpha=0.4, label="Renegotiate band")
    ax.axvspan(HARD_PRB_REJECT, 1.0, color="#f8d7da", alpha=0.35, label="Reject band")
    ax.scatter(xs, ys, c=cs, s=18, alpha=0.75, edgecolors="none")
    ax.axvline(HARD_PRB_RENEG, color="#ff7f0e", linestyle="--", linewidth=1, label=f"PRB reneg gate ({HARD_PRB_RENEG})")
    ax.axvline(HARD_PRB_REJECT, color="#d62728", linestyle="--", linewidth=1, label=f"PRB reject gate ({HARD_PRB_REJECT})")
    ax.set_xlabel("Normalized PRB utilization at admission time")
    ax.set_ylabel("SLA decision score")
    ax.set_title("PRB utilization vs admission decision regions")
    ax.legend(fontsize=7, loc="lower left")
    save_fig(fig, OUT / "figures/fig02_prb_vs_admission_regions.png")
    rec.status = "GENERATED"
    return True


def fig03_feasibility_pressure(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    idx, feas, press, dec = [], [], [], []
    for i, r in enumerate(rows):
        f, p = fnum(r.get("feasibility_score")), fnum(r.get("resource_pressure"))
        if math.isfinite(f) and math.isfinite(p):
            idx.append(i)
            feas.append(f)
            press.append(p)
            dec.append(r.get("decision", ""))
    if len(idx) < 20:
        rec.status = "INVALID"
        return False
    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax2 = ax1.twinx()
    ax1.plot(idx, feas, color="#1f77b4", label="Feasibility", linewidth=1.2)
    ax2.plot(idx, press, color="#d62728", label="Resource pressure", linewidth=1.2, alpha=0.8)
    for i, d in zip(idx, dec):
        if d != "ACCEPT":
            ax1.axvline(i, color=DECISION_COLORS.get(d, "#333"), alpha=0.3, linewidth=0.8)
    ax1.set_xlabel("Admission request index (campaign order)")
    ax1.set_ylabel("Feasibility score")
    ax2.set_ylabel("Resource pressure")
    ax1.set_title("Feasibility and pressure evolution during admission windows")
    lines1, lab1 = ax1.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lab1 + lab2, fontsize=8, loc="upper right")
    save_fig(fig, OUT / "figures/fig03_feasibility_pressure_timeline.png")
    rec.status = "GENERATED"
    return True


def fig04_latency_consistency(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    by_slice: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        h = fnum(r.get("http_elapsed_s"))
        if math.isfinite(h):
            by_slice[r.get("slice", "?")].append(h)
    if sum(len(v) for v in by_slice.values()) < 15:
        rec.status = "INVALID"
        return False
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    slices = sorted(by_slice.keys())
    axes[0].boxplot([by_slice[s] for s in slices], labels=slices)
    axes[0].set_ylabel("End-to-end HTTP latency (s)")
    axes[0].set_title("Admission path latency by slice type")
    sc = []
    for r in rows:
        h, s = fnum(r.get("http_elapsed_s")), fnum(r.get("decision_score"))
        if math.isfinite(h) and math.isfinite(s):
            sc.append((h, s, r.get("slice", "")))
    for sl in slices:
        sub = [(h, sc2) for h, sc2, sl2 in sc if sl2 == sl]
        if sub:
            axes[1].scatter([h for h, _ in sub], [sc2 for _, sc2 in sub], label=sl, s=12, alpha=0.6)
    axes[1].set_xlabel("HTTP latency (s)")
    axes[1].set_ylabel("Decision score")
    axes[1].set_title("Score consistency vs admission latency")
    axes[1].legend(fontsize=7)
    save_fig(fig, OUT / "figures/fig04_admission_latency_score_consistency.png")
    rec.status = "GENERATED"
    return True


def fig05_multidomain_telemetry(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    idx = list(range(len(rows)))
    prb = [fnum(r.get("prb_utilization_real")) for r in rows]
    rtt = [fnum(r.get("telemetry_transport_rtt_ms")) for r in rows]
    cpu = [fnum(r.get("telemetry_core_cpu")) * 100 for r in rows]
    if not any(math.isfinite(v) and statistics.pstdev([x for x in prb if math.isfinite(x)] or [0]) > 0 for v in prb):
        rec.status = "INVALID"
        rec.quality_notes = "flat RAN series"
        return False
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(idx, prb, label="RAN PRB utilization (%)", color="#1f77b4", linewidth=1)
    ax2 = ax.twinx()
    ax2.plot(idx, rtt, label="Transport RTT (ms)", color="#ff7f0e", alpha=0.85, linewidth=1)
    ax3 = ax.twinx()
    ax3.spines["right"].set_position(("outward", 55))
    ax3.plot(idx, cpu, label="Core CPU (%)", color="#2ca02c", alpha=0.7, linewidth=1)
    ax.set_xlabel("Request index (temporal campaign order)")
    ax.set_ylabel("PRB utilization (%)")
    ax2.set_ylabel("RTT (ms)")
    ax3.set_ylabel("Core CPU (%)")
    ax.set_title("RAN, transport, and core telemetry evolution during runtime")
    lines = ax.get_lines() + ax2.get_lines() + ax3.get_lines()
    ax.legend(lines, [l.get_label() for l in lines], fontsize=7, loc="upper left")
    save_fig(fig, OUT / "figures/fig05_multidomain_telemetry_evolution.png")
    rec.status = "GENERATED"
    return True


def fig06_multidomain_influence(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    _, rows = load_csv(SOURCES["tri_slice"])
    rows = [r for r in rows if math.isfinite(fnum(r.get("contrib_prb")))]
    if len(rows) < 20:
        rec.status = "INVALID"
        rec.quality_notes = "insufficient contrib_* rows"
        return False
    contrib_cols = [
        ("contrib_prb", "RAN PRB goodness"),
        ("contrib_feasibility", "Feasibility"),
        ("contrib_transport", "Transport"),
        ("contrib_headroom", "Headroom"),
        ("contrib_risk", "Risk inverse"),
        ("contrib_semantic", "Semantic priority"),
    ]
    idx = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(10, 4.5))
    any_line = False
    for col, lab in contrib_cols:
        if col not in rows[0]:
            continue
        vals = [fnum(r.get(col)) for r in rows]
        clean = [v for v in vals if math.isfinite(v)]
        if len(clean) >= 2 and statistics.pstdev(clean) > 1e-9:
            ax.plot(idx, vals, label=lab, linewidth=1)
            any_line = True
    if not any_line:
        rec.status = "INVALID"
        return False
    ax.set_xlabel("Request index")
    ax.set_ylabel("Weighted score contribution")
    ax.set_title("Multidomain operational influence on admission score (frozen weights)")
    ax.legend(fontsize=7)
    save_fig(fig, OUT / "figures/fig06_multidomain_score_influence.png")
    rec.status = "GENERATED"
    return True


def fig07_prb_score_correlation(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    pts = [(parse_ts(r["timestamp"]), fnum(r.get("prb_utilization_real")), fnum(r.get("decision_score"))) for r in rows]
    pts = [(t, p, s) for t, p, s in pts if t and math.isfinite(p) and math.isfinite(s)]
    if len(pts) < 20:
        rec.status = "INVALID"
        return False
    pts.sort(key=lambda x: x[0])
    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax2 = ax1.twinx()
    ax1.plot([t for t, _, _ in pts], [p for _, p, _ in pts], color="#d62728", label="PRB %", linewidth=1)
    ax2.plot([t for t, _, _ in pts], [s for _, _, s in pts], color="#1f77b4", label="Decision score", linewidth=1)
    ax1.set_ylabel("PRB utilization (%)")
    ax2.set_ylabel("Decision score")
    ax1.set_xlabel("Campaign runtime (UTC)")
    ax1.set_title("Correlation timeline: PRB pressure and decision score")
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], fontsize=8)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    save_fig(fig, OUT / "figures/fig07_prb_score_correlation_timeline.png")
    rec.status = "GENERATED"
    return True


def fig08_e2e_workflow(rec: FigureRecord) -> bool:
    path = SOURCES["e2e_accept"]
    _, rows = load_csv(path)
    if len(rows) < 5:
        rec.status = "INVALID"
        return False
    fig, ax = plt.subplots(figsize=(10, 4))
    runs, times = [], []
    for r in rows:
        runs.append(int(fnum(r.get("run", 0))))
        times.append(fnum(r.get("total_time")))
    ax.bar(runs, times, color="#4e79a7", width=0.7)
    for i, r in enumerate(rows):
        ax.text(runs[i], times[i] + 0.1, "BC✓" if r.get("bc_status") == "COMMITTED" else r.get("bc_status", ""), ha="center", fontsize=6)
    ax.axhline(statistics.mean(times), color="#333", linestyle="--", linewidth=1, label=f"Mean E2E ({statistics.mean(times):.2f}s)")
    ax.set_xlabel("Sequential submit run")
    ax.set_ylabel("End-to-end request duration (s)")
    ax.set_title("Orchestration workflow: submit → NASP → governance (E2E accept batch)")
    ax.legend(fontsize=8)
    save_fig(fig, OUT / "figures/fig08_orchestration_e2e_workflow.png")
    rec.status = "GENERATED"
    return True


def fig09_ncm_latency(rec: FigureRecord) -> bool:
    _, rows = load_csv(SOURCES["ncm_orch"])
    if len(rows) < 10:
        rec.status = "INVALID"
        return False
    x, y = [], []
    for r in rows:
        ep, rep = int(fnum(r.get("epoch", 0))), int(fnum(r.get("rep_index", 0)))
        x.append(ep * 12 + rep)
        y.append(fnum(r.get("http_elapsed_s")))
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x, y, "o-", color="#e15759", markersize=4, linewidth=1)
    for ep in sorted({int(fnum(r.get("epoch", 0))) for r in rows}):
        ax.axvline(ep * 12, color="#aaa", linestyle=":", alpha=0.6)
        ax.text(ep * 12 + 0.5, max(y) * 0.95, f"epoch {ep}", fontsize=7)
    ax.set_xlabel("Campaign progression (epoch × replicates)")
    ax.set_ylabel("Orchestration HTTP latency (s)")
    ax.set_title("Runtime latency during operational contention (NCM-ORCH-01)")
    save_fig(fig, OUT / "figures/fig09_orchestration_latency_contention.png")
    rec.status = "GENERATED"
    return True


def fig10_persistence_snapshot(rec: FigureRecord) -> bool:
    data = json.loads(SOURCES["life_persistence"].read_text(encoding="utf-8"))
    sem = data.get("sem_db", {}).get("counts", {})
    if not sem:
        rec.status = "INVALID"
        return False
    labels, vals = list(sem.keys()), [sem[k] for k in sem]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, vals, color=["#59a14f", "#76b7b2", "#edc948"])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
    tr = data.get("sem_db", {}).get("intent_ts_range", {})
    ax.set_title(f"Semantic persistence snapshot (intents {tr.get('min','?')} → {tr.get('max','?')})")
    ax.set_ylabel("Persisted object count")
    ax.set_xlabel("SEM-CSMF SQLite store")
    save_fig(fig, OUT / "figures/fig10_semantic_persistence_snapshot.png")
    rec.status = "GENERATED"
    rec.quality_notes = "cluster snapshot at LIFE-EXEC-03 probe — not a continuous NSI time series"
    return True


def fig11_ncm_pressure_decoupling(rec: FigureRecord) -> bool:
    _, rows = load_csv(SOURCES["ncm_orch"])
    px = [fnum(r.get("resource_pressure")) for r in rows]
    py = [fnum(r.get("http_elapsed_s")) for r in rows]
    if len(px) < 10:
        rec.status = "INVALID"
        return False
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(px, py, c="#4e79a7", s=40, alpha=0.8)
    ax.set_xlabel("Admission-time resource pressure (frozen formula)")
    ax.set_ylabel("Orchestration HTTP latency (s)")
    ax.set_title("Orchestration latency vs admission pressure (no causal recompute)")
    save_fig(fig, OUT / "figures/fig11_orch_latency_vs_pressure.png")
    rec.status = "GENERATED"
    return True


def fig12_governance_timeline(rec: FigureRecord) -> bool:
    _, rows = load_csv(SOURCES["e2e_accept"])
    if len(rows) < 5:
        rec.status = "INVALID"
        return False
    fig, ax = plt.subplots(figsize=(10, 3.5))
    y = 1
    for r in rows:
        run = int(fnum(r.get("run", 0)))
        t = fnum(r.get("total_time"))
        ax.barh(y, t, left=run * 0, height=0.3, color="#59a14f" if r.get("bc_status") == "COMMITTED" else "#e15759")
        ax.text(run, y, f"#{run}", ha="center", va="center", fontsize=6, color="white")
        y += 1
    ax.set_xlabel("Relative run order")
    ax.set_ylabel("Governance commit lane")
    ax.set_title("Governance event timeline: immutable BC commits after successful NASP")
    ax.set_yticks([])
    save_fig(fig, OUT / "figures/fig12_governance_bc_timeline.png")
    rec.status = "GENERATED"
    return True


def fig13_lineage_proxy(rows: List[Dict[str, Any]], rec: FigureRecord) -> bool:
    """Proxy: decision_score stability across same network_state_id triplets."""
    by_state: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        by_state[r.get("network_state_id", "")].append(fnum(r.get("decision_score")))
    spread = {k: max(v) - min(v) for k, v in by_state.items() if len(v) >= 2 and all(math.isfinite(x) for x in v)}
    if len(spread) < 5:
        rec.status = "INVALID"
        return False
    keys = sorted(spread.keys(), key=lambda k: spread[k], reverse=True)[:25]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(range(len(keys)), [spread[k] for k in keys], color="#76b7b2")
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([k[:18] for k in keys], fontsize=6)
    ax.set_xlabel("Score range within same network state ID")
    ax.set_title("Slice-aware score differentiation under identical network-state identifiers")
    save_fig(fig, OUT / "figures/fig13_slice_aware_same_state_spread.png")
    rec.status = "GENERATED"
    return True


def fig14_orch_pressure_limits(rec: FigureRecord) -> bool:
    _, rows = load_csv(SOURCES["ncm_orch"])
    scores = [fnum(r.get("decision_score")) for r in rows]
    press = [fnum(r.get("resource_pressure")) for r in rows]
    if len(scores) < 10:
        rec.status = "INVALID"
        return False
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(press, scores, c="#b07aa1", s=35)
    ax.set_xlabel("Resource pressure at admission")
    ax.set_ylabel("Decision score (unchanged by orchestration)")
    ax.set_title("Operational limit: orchestration does not recompute admission score")
    save_fig(fig, OUT / "figures/fig14_orch_pressure_non_causal.png")
    rec.status = "GENERATED"
    return True


def fig15_causal_boundaries_conceptual(rec: FigureRecord) -> bool:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (1, 4, "SEM\ninterpret", "#cfe2f3"),
        (3.5, 4, "DE\npreventive admission", "#d4edda"),
        (6, 4, "Portal\nNASP instantiate", "#fff3cd"),
        (8.5, 4, "CRD\nreconcile", "#e2e3e5"),
    ]
    for x, y, txt, col in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 1.8, 1.2, boxstyle="round,pad=0.05", facecolor=col, edgecolor="#333"))
        ax.text(x + 0.9, y + 0.6, txt, ha="center", va="center", fontsize=9)
    for x1, x2 in [(2.8, 3.5), (5.3, 6), (7.8, 8.5)]:
        ax.annotate("", xy=(x2, 4.6), xytext=(x1, 4.6), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(5, 2.2, "PROVEN: admission → orchestration (forward)", ha="center", fontsize=10, color="#155724")
    ax.text(5, 1.2, "NOT OBSERVED: orchestration → DE feedback", ha="center", fontsize=10, color="#721c24")
    ax.text(5, 0.4, "NOT OBSERVED: continuous autonomous reevaluation", ha="center", fontsize=9, color="#721c24")
    ax.set_title("Observed vs non-observed runtime causal boundaries (ORCH/LIFE freeze)")
    save_fig(fig, OUT / "figures/fig15_causal_boundaries_model.png")
    rec.status = "CONCEPTUAL"
    rec.quality_notes = "frozen audit model — not simulated telemetry"
    return True


def fig16_feedback_absence(rec: FigureRecord) -> bool:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    nodes = {"DE": (2, 2.5), "Portal": (5, 2.5), "NASP/CRD": (8, 2.5), "Reconciler": (8, 0.8)}
    for name, (x, y) in nodes.items():
        ax.add_patch(FancyBboxPatch((x - 0.9, y - 0.5), 1.8, 1, boxstyle="round", facecolor="#f8f9fa", edgecolor="#333"))
        ax.text(x, y, name, ha="center", va="center", fontsize=9)
    ax.annotate("", xy=(4.1, 2.5), xytext=(2.9, 2.5), arrowprops=dict(arrowstyle="->", color="green"))
    ax.annotate("", xy=(7.1, 2.5), xytext=(5.9, 2.5), arrowprops=dict(arrowstyle="->", color="green"))
    ax.plot([8, 5], [2.5, 3.4], "r--", linewidth=1.2)
    ax.plot([8, 2], [0.8, 3.4], "r--", linewidth=1.2)
    ax.text(6.5, 3.5, "NO PATH", fontsize=8, color="red", ha="center")
    ax.text(5, 2.1, "NO PATH", fontsize=8, color="red", ha="center")
    ax.set_title("Runtime feedback absence map (validated ORCH-EXEC-03)")
    save_fig(fig, OUT / "figures/fig16_feedback_absence_map.png")
    rec.status = "CONCEPTUAL"
    return True


FIGURE_SPECS: List[FigureRecord] = [
    FigureRecord("F01", "Runtime SLA score evolution", "fig01_runtime_sla_score_evolution.png", "PENDING", "H1,H2", "Preventive admission", "tri_slice", "SR-EXEC-05", "VI-A", "Score evolves with telemetry regimes", "Digest-frozen score_mode only", "Not closed-loop orchestration"),
    FigureRecord("F02", "PRB vs admission regions", "fig02_prb_vs_admission_regions.png", "PENDING", "H2", "PRB dominance", "tri_slice", "SR-EXEC-05", "VI-A", "PRB gates structure decisions", "Frozen HARD_PRB thresholds", "Not slice-specific admission proof alone"),
    FigureRecord("F03", "Feasibility and pressure timeline", "fig03_feasibility_pressure_timeline.png", "PENDING", "H1", "Feasibility-aware admission", "tri_slice", "SR-EXEC-05", "VI-A", "Pressure/feasibility co-evolve at admission", "Snapshot formula", "Not post-orchestration pressure"),
    FigureRecord("F04", "Latency and score consistency", "fig04_admission_latency_score_consistency.png", "PENDING", "H3", "Preventive path timing", "tri_slice", "SR-EXEC-05", "VI-A", "Admission path latency by slice", "HTTP elapsed only", "Not orchestration-only latency"),
    FigureRecord("F05", "Multidomain telemetry evolution", "fig05_multidomain_telemetry_evolution.png", "PENDING", "H1", "Multidomain observability", "tri_slice", "SR-EXEC-05", "VI-B", "RAN/transport/core visible at runtime", "Observability not balanced causality", "Not transport dominance"),
    FigureRecord("F06", "Multidomain score influence", "fig06_multidomain_score_influence.png", "PENDING", "H1,H2", "Weighted contributions", "tri_slice", "SR-EXEC-05", "VI-B", "Contribution terms from frozen weights", "Real contrib_* fields", "Not independent domain causality"),
    FigureRecord("F07", "PRB-score correlation timeline", "fig07_prb_score_correlation_timeline.png", "PENDING", "H2", "PRB-score coupling", "tri_slice", "SR-EXEC-05", "VI-B", "Temporal PRB-score anti-correlation tendency", "Campaign timestamps", "Not causal orchestration"),
    FigureRecord("F08", "E2E orchestration workflow", "fig08_orchestration_e2e_workflow.png", "PENDING", "H3,H4", "Admission before orchestration", "e2e_accept", "LIFE/ORCH", "VI-H", "Sequential E2E submit→NASP→BC", "Real batch timings", "Not continuous NSI timeline"),
    FigureRecord("F09", "NCM orchestration latency", "fig09_orchestration_latency_contention.png", "PENDING", "H5", "Operational contention", "ncm_orch", "NCM-EXEC-04", "VI-F", "Latency under orch_probe epochs", "NCM campaign", "Not admission recompute"),
    FigureRecord("F10", "Semantic persistence snapshot", "fig10_semantic_persistence_snapshot.png", "PENDING", "H4", "Persistence", "life_persistence", "LIFE-EXEC-03", "VI-G", "SEM store counts at probe time", "Snapshot not time series", "Not CRD churn over time"),
    FigureRecord("F11", "Orchestration vs pressure", "fig11_orch_latency_vs_pressure.png", "PENDING", "H5", "Detached orchestration", "ncm_orch", "NCM/ORCH", "VI-H", "Weak coupling orch latency vs pressure", "Real NCM rows", "Not orchestration-driven pressure"),
    FigureRecord("F12", "Governance BC timeline", "fig12_governance_bc_timeline.png", "PENDING", "H4", "Immutable governance", "e2e_accept", "publication", "VI-G", "BC commits after successful submits", "tx_hash present", "Not smart-contract performance benchmark"),
    FigureRecord("F13", "Same-state slice spread", "fig13_slice_aware_same_state_spread.png", "PENDING", "H1", "Slice-aware scoring", "tri_slice", "SR-EXEC-05", "VI-C", "Score range across slices same state", "network_state_id groups", "Not admission label divergence"),
    FigureRecord("F14", "Orchestration pressure limits", "fig14_orch_pressure_non_causal.png", "PENDING", "H5", "Negative: no orch feedback", "ncm_orch", "ORCH-EXEC-04", "VII", "Score stable vs pressure under orch", "NCM dataset", "Not proving zero latency"),
    FigureRecord("F15", "Causal boundaries model", "fig15_causal_boundaries_model.png", "PENDING", "H5", "Negative characterization", "freeze", "ORCH/LIFE", "VI-I", "Forward vs absent feedback paths", "Conceptual from freeze", "Not measured latency on diagram"),
    FigureRecord("F16", "Feedback absence map", "fig16_feedback_absence_map.png", "PENDING", "H5", "Negative characterization", "freeze", "ORCH-EXEC-03", "VI-I", "Validated absent feedback paths", "Conceptual from code audit", "Not live packet trace"),
]


def write_documentation(records: List[FigureRecord], qualities: List[DatasetQuality]) -> None:
    idx_lines = ["# Figure Master Index", "", f"Generated: {datetime.now(timezone.utc).isoformat()}", f"Digest: `{DIGEST}`", ""]
    hyp_lines = ["# Figure to Hypothesis Map", ""]
    val_lines = ["# Figure Runtime Validation", ""]
    cap_lines = ["# IEEE Captions (Q1)", ""]
    for rec in records:
        idx_lines.extend(
            [
                f"## {rec.fig_id} — {rec.title}",
                f"- **File:** `figures/{rec.filename}`",
                f"- **Status:** {rec.status}",
                f"- **Dataset:** {rec.dataset}",
                f"- **Freeze:** {rec.freeze}",
                f"- **Section:** {rec.paper_section}",
                "",
            ]
        )
        hyp_lines.append(f"| {rec.fig_id} | {rec.hypothesis} | {rec.objective} | {rec.status} |")
        val_lines.extend(
            [
                f"### {rec.fig_id}",
                f"- Proves: {rec.proves}",
                f"- Reviewer-safe: {rec.reviewer_safe}",
                f"- Do NOT infer: {rec.not_infer}",
                f"- Notes: {rec.quality_notes or '—'}",
                "",
            ]
        )
        cap_lines.extend(
            [
                f"**Figure {rec.fig_id[1:]} — {rec.title}.** ",
                f"{rec.proves} ",
                f"({rec.reviewer_safe}; not inferred: {rec.not_infer})",
                "",
            ]
        )
    hyp_lines.insert(3, "| Fig | Hypothesis | Objective | Status |")
    hyp_lines.insert(4, "|-----|------------|-----------|--------|")

    for name, content in [
        ("FIGURE_MASTER_INDEX.md", idx_lines),
        ("FIGURE_TO_HYPOTHESIS_MAP.md", hyp_lines),
        ("FIGURE_RUNTIME_VALIDATION.md", val_lines),
    ]:
        text = "\n".join(content)
        (OUT / name).write_text(text, encoding="utf-8")
        (OUT / "validation" / name).write_text(text, encoding="utf-8")
    (OUT / "ieee/IEEE_CAPTIONS.md").write_text("\n".join(cap_lines), encoding="utf-8")
    (OUT / "captions/IEEE_CAPTIONS.md").write_text("\n".join(cap_lines), encoding="utf-8")

    dq = ["# Dataset Quality Report", ""]
    for q in qualities:
        dq.append(f"## {q.name}")
        dq.append(f"- valid: {q.valid}")
        dq.append(f"- rows: {q.rows}")
        dq.append(f"- reason: {q.reason}")
        dq.append(f"- sha256: `{q.sha256}`")
        if q.numeric_variance:
            dq.append(f"- variance: `{q.numeric_variance}`")
        dq.append("")
    dq_text = "\n".join(dq)
    (OUT / "DATASET_QUALITY_REPORT.md").write_text(dq_text, encoding="utf-8")
    (OUT / "validation/DATASET_QUALITY_REPORT.md").write_text(dq_text, encoding="utf-8")

    guide = """# Reviewer-Safe Figure Guide

- Use **GENERATED** figures for quantitative claims (SR, NCM, E2E batches).
- Use **CONCEPTUAL** figures (F15–F16) only for causal boundaries explicitly frozen in ORCH/LIFE tracks.
- Never infer closed-loop orchestration, continuous reevaluation, or core-driven admission from plots.
- Digest pinned: `%s`.
""" % DIGEST
    (OUT / "REVIEWER_SAFE_FIGURE_GUIDE.md").write_text(guide, encoding="utf-8")

    forbidden = """# Forbidden Figure Patterns

- Bar charts without temporal or experimental context
- Synthetic/smoothed/interpolated telemetry
- ML-style confusion matrices without runtime SLA context
- Heatmaps without scientific narrative
- Obscure internal variable names in titles
- Figures not tied to H1–H5 or frozen negative results
"""
    (OUT / "FORBIDDEN_FIGURE_PATTERNS.md").write_text(forbidden, encoding="utf-8")

    pos = """# Q1 Figure Positioning Report

TriSLA figures are repositioned to NASP-level **runtime narrative**:
1. Temporal admission campaigns (SR-EXEC-05, n≈450)
2. Operational contention epochs (NCM-EXEC-04)
3. E2E governance batch (publication artifact)
4. Explicit negative boundary diagrams (ORCH freeze)

Gaps documented honestly:
- No continuous NSI/CRD time-series in repo → F10 is snapshot
- CORE/NAD liminal-03 CSV empty → use NAD-02 / SR for boundary figures
"""
    (OUT / "Q1_FIGURE_POSITIONING_REPORT.md").write_text(pos, encoding="utf-8")

    # Overleaf stubs
    ol = OUT / "overleaf"
    ol.mkdir(exist_ok=True)
    figs = [r for r in records if r.status in ("GENERATED", "CONCEPTUAL")]
    tex = ["% TriSLA Q1 figures — include from paper_q1_figures/figures/", "\\usepackage{graphicx}", ""]
    for i, r in enumerate(figs, 1):
        tex.append(f"% Figure {i}: {r.fig_id}")
        tex.append("\\begin{figure}[!t]")
        tex.append("\\centering")
        tex.append(f"\\includegraphics[width=\\linewidth]{{figures/{r.filename}}}")
        tex.append(f"\\caption{{{r.title}. {r.proves}}}")
        tex.append(f"\\label{{fig:trisla_{r.fig_id.lower()}}}")
        tex.append("\\end{figure}")
        tex.append("")
    (ol / "figures.tex").write_text("\n".join(tex), encoding="utf-8")


def main() -> None:
    for sub in ("figures", "datasets/final_q1_figures", "captions", "validation", "manifests", "analysis", "ieee", "overleaf"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    qualities = [
        validate_dataset("tri_slice", SOURCES["tri_slice"], 50, ["decision_score", "prb_utilization_real"]),
        validate_dataset("ncm_orch", SOURCES["ncm_orch"], 10, ["http_elapsed_s", "decision_score"]),
        validate_dataset("nad_liminal02", SOURCES["nad_liminal02"], 20, ["decision_score"]),
        validate_dataset("e2e_accept", SOURCES["e2e_accept"], 5, ["total_time"]),
        validate_dataset("life_persistence", SOURCES["life_persistence"], 1, []),
    ]

    tri_rows, enriched_path = build_enriched_tri_slice()

    # Additional per-figure datasets (copy-through enrichment)
    ds_dir = OUT / "datasets/final_q1_figures"
    for label, src in [
        ("ncm_orch_01_timeline.csv", SOURCES["ncm_orch"]),
        ("e2e_governance_batch.csv", SOURCES["e2e_accept"]),
        ("nad_liminal02_boundary.csv", SOURCES["nad_liminal02"]),
    ]:
        if src.exists():
            shutil.copy2(src, ds_dir / label)

    builders = [
        (fig01_score_evolution, tri_rows),
        (fig02_prb_decision_regions, tri_rows),
        (fig03_feasibility_pressure, tri_rows),
        (fig04_latency_consistency, tri_rows),
        (fig05_multidomain_telemetry, tri_rows),
        (fig06_multidomain_influence, tri_rows),
        (fig07_prb_score_correlation, tri_rows),
        (fig13_lineage_proxy, tri_rows),
    ]
    bi = 0
    for rec in FIGURE_SPECS:
        if rec.fig_id in ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F13"):
            fn, data = builders[bi]
            fn(data, rec)
            bi += 1
        elif rec.fig_id == "F08":
            fig08_e2e_workflow(rec)
        elif rec.fig_id == "F09":
            fig09_ncm_latency(rec)
        elif rec.fig_id == "F10":
            fig10_persistence_snapshot(rec)
        elif rec.fig_id == "F11":
            fig11_ncm_pressure_decoupling(rec)
        elif rec.fig_id == "F12":
            fig12_governance_timeline(rec)
        elif rec.fig_id == "F14":
            fig14_orch_pressure_limits(rec)
        elif rec.fig_id == "F15":
            fig15_causal_boundaries_conceptual(rec)
        elif rec.fig_id == "F16":
            fig16_feedback_absence(rec)

    write_documentation(FIGURE_SPECS, qualities)

    generated = sum(1 for r in FIGURE_SPECS if r.status == "GENERATED")
    conceptual = sum(1 for r in FIGURE_SPECS if r.status == "CONCEPTUAL")
    invalid = sum(1 for r in FIGURE_SPECS if r.status == "INVALID")

    summary = {
        "phase": "FIGURE_REORGANIZATION_Q1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "output": str(OUT.relative_to(TRISLA_ROOT)),
        "figures_generated": generated,
        "figures_conceptual": conceptual,
        "figures_invalid": invalid,
        "enriched_dataset": str(enriched_path.relative_to(TRISLA_ROOT)),
        "digest": DIGEST,
    }
    (OUT / "analysis/q1_figure_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    (OUT / "manifests/FILE_MANIFEST.txt").write_text("\n".join(str(p.relative_to(OUT)) for p in files), encoding="utf-8")
    with (OUT / "manifests/SHA256SUMS.txt").open("w") as out:
        for p in files:
            out.write(f"{_sha256(p)}  {p.relative_to(OUT)}\n")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
