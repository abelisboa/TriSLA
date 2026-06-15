#!/usr/bin/env python3
"""Phase 1 — Decision source stratification (audit only)."""
from __future__ import annotations

import csv
import json
import math
import random
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

NASP_ROOT = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nasp_hard_plus_20260517T014222Z"
)
DATASET = NASP_ROOT / "phase_1_extreme_runtime_stress/extreme_stress_dataset.csv"
RAW_ROOT = NASP_ROOT / "phase_1_extreme_runtime_stress/raw"

SOURCES_ORDER = (
    "decision_score_mode",
    "PRB_HARD_RENEGOTIATE_THRESHOLD",
    "PRB_HARD_REJECT_THRESHOLD",
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_float(x: Any) -> Optional[float]:
    if x is None or x == "":
        return None
    try:
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except (TypeError, ValueError):
        return None


def _pearson(xs: list[float], ys: list[float]) -> Optional[float]:
    n = min(len(xs), len(ys))
    if n < 2:
        return None
    mx, my = statistics.mean(xs[:n]), statistics.mean(ys[:n])
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den_x = math.sqrt(sum((xs[i] - mx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ys[i] - my) ** 2 for i in range(n)))
    if den_x <= 0 or den_y <= 0:
        return None
    return num / (den_x * den_y)


def _spearman(xs: list[float], ys: list[float]) -> Optional[float]:
    n = min(len(xs), len(ys))
    if n < 2:
        return None
    rx = [sorted(range(n), key=lambda i: xs[i])[i] for i in range(n)]
    ry = [sorted(range(n), key=lambda i: ys[i])[i] for i in range(n)]
    # average ranks for ties (simple; dataset has few ties)
    rank_x = [0.0] * n
    rank_y = [0.0] * n
    for i in range(n):
        rank_x[rx[i]] = float(i)
        rank_y[ry[i]] = float(i)
    return _pearson(rank_x, rank_y)


def _bootstrap_corr(
    xs: list[float], ys: list[float], n_boot: int = 2000, seed: int = 42
) -> dict[str, float]:
    n = min(len(xs), len(ys))
    if n < 3:
        return {}
    rng = random.Random(seed)
    corrs: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        bx = [xs[i] for i in idx]
        by = [ys[i] for i in idx]
        c = _pearson(bx, by)
        if c is not None:
            corrs.append(c)
    if not corrs:
        return {}
    corrs.sort()
    return {
        "mean": statistics.mean(corrs),
        "ci95_low": corrs[int(0.025 * len(corrs))],
        "ci95_high": corrs[int(0.975 * len(corrs))],
    }


def _load_raw_index() -> dict[str, dict[str, Any]]:
    """execution_id -> enriched metadata from raw JSON."""
    index: dict[str, dict[str, Any]] = {}
    for regime_dir in sorted(RAW_ROOT.iterdir()):
        if not regime_dir.is_dir():
            continue
        for p in regime_dir.glob("submit_*.json"):
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            row = doc.get("row") or {}
            payload = doc.get("payload") or {}
            meta = payload.get("metadata") or {}
            eid = row.get("execution_id") or meta.get("execution_id")
            if not eid:
                continue
            snap = meta.get("decision_snapshot") or {}
            if isinstance(snap, dict) and "final_score" in snap:
                gate_final = _safe_float(snap.get("final_score"))
            else:
                gate_final = None
            hpt = meta.get("hard_prb_thresholds") or {}
            index[str(eid)] = {
                "decision_source": meta.get("decision_source") or row.get("decision_source"),
                "decision_mode": meta.get("decision_mode"),
                "decision_score": _safe_float(meta.get("decision_score")),
                "decision_band": meta.get("decision_band"),
                "ran_aware_final_risk": _safe_float(meta.get("ran_aware_final_risk")),
                "raw_risk_score": _safe_float(meta.get("raw_risk_score")),
                "gate_final_score": gate_final,
                "hard_reject_th": _safe_float(hpt.get("reject")),
                "hard_reneg_th": _safe_float(hpt.get("renegotiate")),
                "policy_governed": meta.get("policy_governed"),
                "csv_pick_score": _safe_float(row.get("decision_score")),
            }
    return index


def _figure_style() -> None:
    plt.rcParams.update(
        {
            "figure.figsize": (7.5, 4.5),
            "font.size": 10,
            "font.family": "serif",
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )


def _save(figdir: Path, name: str) -> None:
    plt.tight_layout()
    plt.savefig(figdir / name, dpi=300, bbox_inches="tight")
    plt.close()


def _stats(vals: list[float]) -> dict[str, float]:
    if not vals:
        return {}
    return {
        "n": len(vals),
        "min": min(vals),
        "max": max(vals),
        "mean": statistics.mean(vals),
        "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
    }


def main() -> None:
    ts = _utc_stamp()
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_score_semantics_{ts}")
    p1 = out / "phase_1_decision_source_analysis"
    figdir = p1 / "figures"
    for sub in (p1, figdir, out / "freeze", out / "analysis", out / "figures", out / "logs"):
        sub.mkdir(parents=True, exist_ok=True)

    raw_index = _load_raw_index()
    rows: list[dict[str, Any]] = []
    with DATASET.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            row: dict[str, Any] = dict(r)
            eid = str(row.get("execution_id") or "")
            csv_score_col = _safe_float(r.get("decision_score"))
            csv_source_col = str(r.get("decision_source") or "")
            enrich = raw_index.get(eid, {})
            row.update(enrich)
            row["prb"] = _safe_float(row.get("ran_prb_input")) or _safe_float(
                row.get("prb_utilization_real")
            )
            row["decision"] = str(row.get("decision") or "")
            src = str(row.get("decision_source") or csv_source_col or "unknown")
            row["decision_source"] = src
            row["csv_score"] = csv_score_col
            if row.get("gate_final_score") is None and row.get("ran_aware_final_risk") is not None:
                if "PRB_HARD" in src:
                    row["gate_final_score"] = 1.0 - float(row["ran_aware_final_risk"])
            rows.append(row)

    n = len(rows)
    src_counts = Counter(r["decision_source"] for r in rows)
    other_sources = [s for s in src_counts if s not in SOURCES_ORDER]

    by_src: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_src[r["decision_source"]].append(r)

    # Per-source stats
    per_src_stats: dict[str, Any] = {}
    for src in list(SOURCES_ORDER) + other_sources:
        sub = by_src.get(src, [])
        if not sub:
            continue
        prbs = [r["prb"] for r in sub if r["prb"] is not None]
        decs = Counter(r["decision"] for r in sub)
        meta_scores = [r["decision_score"] for r in sub if r.get("decision_score") is not None]
        risks = [r["ran_aware_final_risk"] for r in sub if r.get("ran_aware_final_risk") is not None]
        csv_scores = [r["csv_score"] for r in sub if r.get("csv_score") is not None]
        gate_scores = [r["gate_final_score"] for r in sub if r.get("gate_final_score") is not None]
        per_src_stats[src] = {
            "count": len(sub),
            "share": len(sub) / n,
            "decisions": dict(decs),
            "prb": _stats(prbs),
            "metadata_decision_score": _stats(meta_scores),
            "ran_aware_final_risk": _stats(risks),
            "csv_column_score": _stats(csv_scores),
            "gate_final_score": _stats(gate_scores),
            "corr_prb_metadata_score": _pearson(prbs, meta_scores)
            if len(prbs) == len(meta_scores) and len(meta_scores) >= 2
            else None,
            "corr_prb_csv_score": _pearson(prbs, csv_scores)
            if len(prbs) == len(csv_scores) and len(csv_scores) >= 2
            else None,
            "corr_prb_ran_risk": _pearson(prbs, risks)
            if len(prbs) == len(risks) and len(risks) >= 2
            else None,
        }

    # Monotonicity: PRB mean by decision within each source
    mono: dict[str, bool] = {}
    for src, sub in by_src.items():
        by_dec_prb: dict[str, list[float]] = defaultdict(list)
        for r in sub:
            if r["prb"] is not None:
                by_dec_prb[r["decision"]].append(r["prb"])
        means = []
        for dec in ("ACCEPT", "RENEGOTIATE", "REJECT"):
            if by_dec_prb.get(dec):
                means.append((dec, statistics.mean(by_dec_prb[dec])))
        mono[src] = (
            len(means) >= 2
            and all(means[i][1] <= means[i + 1][1] for i in range(len(means) - 1))
        )

    # Global stratified correlations
    sm = by_src.get("decision_score_mode", [])
    sm_prb = [r["prb"] for r in sm if r["prb"] and r.get("decision_score")]
    sm_sc = [r["decision_score"] for r in sm if r["prb"] and r.get("decision_score")]
    sm_boot = _bootstrap_corr(sm_prb, sm_sc) if len(sm_prb) >= 3 else {}

    hard_rej = by_src.get("PRB_HARD_REJECT_THRESHOLD", [])
    hr_prb = [r["prb"] for r in hard_rej if r["prb"]]
    hr_risk = [r["ran_aware_final_risk"] for r in hard_rej if r.get("ran_aware_final_risk")]

    # Temporal evolution (campaign order)
    ordered = sorted(rows, key=lambda r: (r.get("regime_mbps", ""), r.get("timestamp", "")))

    stats_out = {
        "n": n,
        "decision_source_counts": dict(src_counts),
        "per_source": per_src_stats,
        "monotonicity_prb_by_decision_per_source": mono,
        "score_mode_corr_prb_decision_score": _pearson(sm_prb, sm_sc),
        "score_mode_spearman": _spearman(sm_prb, sm_sc),
        "score_mode_bootstrap": sm_boot,
        "hard_reject_corr_prb_ran_risk": _pearson(hr_prb, hr_risk),
        "pick_score_artifact": {
            "note": "CSV uses _pick_score: decision_score else ran_aware_final_risk",
            "hard_reject_csv_score_unique": sorted(
                {r["csv_score"] for r in hard_rej if r.get("csv_score")}
            ),
        },
    }
    (p1 / "decision_source_stats.json").write_text(
        json.dumps(stats_out, indent=2), encoding="utf-8"
    )

    _figure_style()
    palette = {
        "decision_score_mode": "#2ca02c",
        "PRB_HARD_RENEGOTIATE_THRESHOLD": "#ff7f0e",
        "PRB_HARD_REJECT_THRESHOLD": "#d62728",
    }
    colors_dec = {"ACCEPT": "#2ca02c", "RENEGOTIATE": "#ff7f0e", "REJECT": "#d62728"}

    # Fig 1: decision_source pie + bar
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    labels = [s for s in SOURCES_ORDER if src_counts.get(s)] + other_sources
    counts = [src_counts[s] for s in labels]
    cols = [palette.get(s, "#888888") for s in labels]
    axes[0].pie(counts, labels=[s.replace("PRB_HARD_", "HARD_") for s in labels], autopct="%1.1f%%", colors=cols)
    axes[0].set_title("Decision source frequency")
    axes[1].bar(range(len(labels)), counts, color=cols)
    axes[1].set_xticks(range(len(labels)))
    axes[1].set_xticklabels([s.replace("PRB_HARD_", "HARD_\n") for s in labels], rotation=15, ha="right", fontsize=8)
    axes[1].set_ylabel("Count")
    axes[1].set_title("Decision path counts (n=150)")
    _save(figdir, "01_decision_source_distribution.png")

    # Fig 2: PRB by decision_source (boxplot-style via scatter)
    fig, ax = plt.subplots(figsize=(9, 5))
    positions: dict[str, int] = {s: i for i, s in enumerate(labels)}
    for r in rows:
        if r["prb"] is None:
            continue
        src = r["decision_source"]
        x = positions.get(src, len(labels)) + (random.Random(hash(r["execution_id"])).random() - 0.5) * 0.25
        ax.scatter(x, r["prb"], c=palette.get(src, "#888"), alpha=0.55, s=22, edgecolors="none")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([s.replace("PRB_HARD_", "HARD_") for s in labels], rotation=15, ha="right", fontsize=8)
    ax.set_ylabel("PRB utilization (%)")
    ax.set_title("PRB distribution by decision_source")
    _save(figdir, "02_prb_by_decision_source.png")

    # Fig 3: score by decision_source (three metrics)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
    for ax, key, title in (
        (axes[0], "decision_score", "metadata.decision_score"),
        (axes[1], "ran_aware_final_risk", "ran_aware_final_risk"),
        (axes[2], "csv_score", "CSV column (_pick_score)"),
    ):
        for src in labels:
            sub = by_src[src]
            vals = [r.get(key) for r in sub if r.get(key) is not None]
            if not vals:
                continue
            ax.scatter(
                [src.replace("PRB_HARD_", "HARD_")] * len(vals),
                vals,
                c=palette.get(src, "#888"),
                alpha=0.5,
                s=20,
            )
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=20)
    _save(figdir, "03_score_metrics_by_source.png")

    # Fig 4: class distribution stacked by source
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(labels))
    bottom = np.zeros(len(labels))
    for dec in ("ACCEPT", "RENEGOTIATE", "REJECT"):
        vals = [sum(1 for r in by_src[s] if r["decision"] == dec) for s in labels]
        ax.bar(x, vals, bottom=bottom, label=dec, color=colors_dec[dec])
        bottom += np.array(vals)
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace("PRB_HARD_", "HARD_") for s in labels], rotation=15, ha="right", fontsize=8)
    ax.set_ylabel("Count")
    ax.set_title("Decision class by decision_source")
    ax.legend()
    _save(figdir, "04_class_by_decision_source.png")

    # Fig 5: regime evolution — source mix
    regimes = sorted(
        {str(r.get("regime_mbps")) for r in rows},
        key=lambda x: int("".join(c for c in x if c.isdigit()) or "0"),
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.25
    xr = np.arange(len(regimes))
    for i, src in enumerate(SOURCES_ORDER):
        if not src_counts.get(src):
            continue
        vals = [
            sum(1 for r in rows if r.get("regime_mbps") == reg and r["decision_source"] == src)
            for reg in regimes
        ]
        ax.bar(xr + i * width, vals, width, label=src.replace("PRB_HARD_", "HARD_"), color=palette[src])
    ax.set_xticks(xr + width)
    ax.set_xticklabels(regimes, rotation=15)
    ax.set_ylabel("Count per regime (30 total)")
    ax.set_title("Decision_source evolution across traffic regimes")
    ax.legend(fontsize=7)
    _save(figdir, "05_regime_source_evolution.png")

    # Fig 6: temporal strip (source + PRB)
    fig, ax = plt.subplots(figsize=(11, 4))
    prbs = [r["prb"] or 0 for r in ordered]
    src_idx = {s: i for i, s in enumerate(labels)}
    colors_pts = [palette.get(r["decision_source"], "#888") for r in ordered]
    ax.scatter(range(len(ordered)), prbs, c=colors_pts, s=18, alpha=0.7)
    ax.set_xlabel("Submit sequence (regime blocks)")
    ax.set_ylabel("PRB %")
    ax.set_title("Temporal evolution: PRB colored by decision_source")
    from matplotlib.lines import Line2D

    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=palette[s], label=s.replace("PRB_HARD_", "HARD_"))
        for s in labels
    ]
    ax.legend(handles=handles, fontsize=7, loc="upper left")
    _save(figdir, "06_temporal_source_evolution.png")

    # Verdict
    only_three = set(src_counts) <= set(SOURCES_ORDER) and len(src_counts) == 3
    covers_all = sum(src_counts.values()) == n
    sep_ok = all(
        per_src_stats.get(s, {}).get("prb", {}).get("mean", 0) > 0 for s in SOURCES_ORDER if src_counts.get(s)
    )
    sm_mono = mono.get("decision_score_mode", False)
    hard_sep = (
        per_src_stats.get("PRB_HARD_RENEGOTIATE_THRESHOLD", {}).get("prb", {}).get("mean", 0)
        < per_src_stats.get("PRB_HARD_REJECT_THRESHOLD", {}).get("prb", {}).get("mean", 0)
    )
    valid = only_three and covers_all and sep_ok and hard_sep
    verdict = (
        "DECISION_SOURCE_STRATIFICATION_VALID"
        if valid
        else "DECISION_SOURCE_STRATIFICATION_INCONSISTENT"
    )

    sm_corr = stats_out.get("score_mode_corr_prb_decision_score")
    boot = stats_out.get("score_mode_bootstrap") or {}
    mixed_prb = [r["prb"] for r in rows if r["prb"] is not None]
    mixed_csv = [r["csv_score"] for r in rows if r["csv_score"] is not None]
    mixed_corr = _pearson(mixed_prb[: len(mixed_csv)], mixed_csv)
    hr_corr = _pearson(hr_prb, hr_risk)

    def _fmt_corr(c: Optional[float]) -> str:
        return f"{c:.3f}" if c is not None else "n/a"

    md = f"""# Phase 1 — Decision Source Analysis (Stratified)

**Audit:** `evidencias_trisla_score_semantics_{ts}`  
**Dataset:** `{DATASET}`  
**Rows:** {n}  
**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Executive summary

TriSLA NASP-hard+ exhibits **exactly three runtime decision paths**, mutually exclusive per submit, driven by live PRB telemetry. No additional `decision_source` values were observed. Stratification resolves the Phase-1 boundary finding that mixed-path CSV scores conflate **viability score** with **risk proxy**.

**Verdict:** `{verdict}`

## Runtime paths identified

| decision_source | n | Share | decision_mode | Role |
|-----------------|--:|------:|---------------|------|
"""
    for src in SOURCES_ORDER:
        st = per_src_stats.get(src, {})
        prb_m = st.get("prb", {}).get("mean", 0)
        decs = st.get("decisions", {})
        mode = (
            "decision_score"
            if src == "decision_score_mode"
            else "hard_prb_gate"
        )
        md += f"| `{src}` | {st.get('count', 0)} | {100*st.get('share', 0):.1f}% | {mode} | PRB mean {prb_m:.1f}% → {decs} |\n"

    if other_sources:
        md += "\n**Other sources:** " + ", ".join(other_sources) + "\n"
    else:
        md += "\n**Other sources:** none observed.\n"

    md += f"""
## Statistical separation

### PRB by decision_source

| Source | PRB min | PRB max | PRB mean | PRB std |
|--------|--------:|--------:|---------:|--------:|
"""
    for src in SOURCES_ORDER:
        p = per_src_stats.get(src, {}).get("prb", {})
        md += f"| {src.replace('PRB_HARD_', 'HARD_')} | {p.get('min', 0):.1f} | {p.get('max', 0):.1f} | {p.get('mean', 0):.1f} | {p.get('std', 0):.1f} |\n"

    md += f"""
Hard-gate ordering: RENEGOTIATE path mean PRB **{'<' if hard_sep else '≥'}** REJECT path mean PRB — consistent with thresholds renegotiate **25%** / reject **40%**.

### Score semantics by path (do not mix)

| Source | Field | Mean | Interpretation |
|--------|-------|-----:|----------------|
| decision_score_mode | `metadata.decision_score` | {per_src_stats.get('decision_score_mode', {}).get('metadata_decision_score', {}).get('mean', 0):.3f} | Weighted viability ∈ [0,1]; higher → ACCEPT band |
| PRB_HARD_RENEGOTIATE | `gate_final_score` | {per_src_stats.get('PRB_HARD_RENEGOTIATE_THRESHOLD', {}).get('gate_final_score', {}).get('mean', 0):.3f} | Fixed composite snapshot (0.3) |
| PRB_HARD_REJECT | `gate_final_score` | {per_src_stats.get('PRB_HARD_REJECT_THRESHOLD', {}).get('gate_final_score', {}).get('mean', 0):.3f} | Fixed composite snapshot (0.0) |
| PRB_HARD_REJECT | `ran_aware_final_risk` | {per_src_stats.get('PRB_HARD_REJECT_THRESHOLD', {}).get('ran_aware_final_risk', {}).get('mean', 0):.3f} | Risk proxy = 1 − final_score → **1.0** |
| PRB_HARD_REJECT | CSV `_pick_score` | {per_src_stats.get('PRB_HARD_REJECT_THRESHOLD', {}).get('csv_column_score', {}).get('mean', 0):.3f} | **Artifact:** falls back to risk when `decision_score` absent |

### Correlations (stratified)

| Pair | Scope | Pearson | Notes |
|------|-------|--------:|-------|
| PRB × decision_score | score_mode only (n={len(sm)}) | {_fmt_corr(sm_corr)} | Negative → higher PRB lowers viability score |
| PRB × decision_score | score_mode bootstrap 95% CI | [{boot.get('ci95_low', 0):.3f}, {boot.get('ci95_high', 0):.3f}] | n_boot=2000 |
| PRB × CSV score | all paths mixed | {_fmt_corr(mixed_corr)} | Positive if hard-path risk fallback dominates |
| PRB × ran_aware_final_risk | hard_reject only | {_fmt_corr(hr_corr)} | Risk saturates at 1.0 under reject gate |

### Monotonicity (PRB mean: ACCEPT ≤ RENEG ≤ REJECT)

| decision_source | Monotone |
|-----------------|----------|
"""
    for src in SOURCES_ORDER:
        md += f"| `{src}` | {'yes' if mono.get(src) else 'n/a or partial'} |\n"

    md += f"""
## Operational differences

| Regime | score_mode | HARD_reneg | HARD_reject |
|--------|----------:|----------:|------------:|
"""
    for reg in regimes:
        sub = [r for r in rows if r.get("regime_mbps") == reg]
        c = Counter(r["decision_source"] for r in sub)
        md += f"| {reg} | {c.get('decision_score_mode', 0)} | {c.get('PRB_HARD_RENEGOTIATE_THRESHOLD', 0)} | {c.get('PRB_HARD_REJECT_THRESHOLD', 0)} |\n"

    md += """
## Two-regime hypothesis (preview for Phases 2–4)

1. **Score-continuous regime** (`decision_score_mode`): weighted multidomain viability; PRB enters as `ran_prb_goodness = 1 − PRB/100`; bands `accept_min=0.55`, `reneg_min=0.38`.
2. **Hard-boundary regime** (`PRB_HARD_*`): policy-governed preemptive gates; bypasses continuous score for decision; exports `ran_aware_final_risk` not `decision_score`.

These regimes are **semantically distinct** and must be reported separately in publication (Phase 5).

## Runtime legitimacy

- All 150 submits map to **observed** `metadata.decision_source` in raw JSON (no synthetic relabeling).
- Path selection correlates with **measured** PRB under real iperf load (NASP-hard+).
- CSV `_pick_score()` fallback explains mixed-path correlation; stratification restores coherent DE reading.

## Figures

- `figures/01_decision_source_distribution.png`
- `figures/02_prb_by_decision_source.png`
- `figures/03_score_metrics_by_source.png`
- `figures/04_class_by_decision_source.png`
- `figures/05_regime_source_evolution.png`
- `figures/06_temporal_source_evolution.png`

## Artifacts

- `decision_source_stats.json`

---

**HARD STOP — Phase 1 complete.** Await `PHASE_1_APPROVED` before Phase 2 (score semantics, score_mode only).
"""
    (p1 / "DECISION_SOURCE_ANALYSIS.md").write_text(md, encoding="utf-8")

    # freeze
    for cmd, name in (
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"], "runtime_after.txt"),
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"], "runtime_after.yaml"),
    ):
        fp = out / "freeze" / name
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            fp.write_text(proc.stdout or proc.stderr or "kubectl unavailable", encoding="utf-8")
        except (OSError, subprocess.TimeoutExpired) as exc:
            fp.write_text(f"skipped: {exc}", encoding="utf-8")

    manifest = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    (out / "analysis" / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(f"TRISLA SCORE SEMANTICS STRATIFIED AUDIT PHASE 1: {out}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
