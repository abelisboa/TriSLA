#!/usr/bin/env python3
"""
Geração final de figuras IEEE/Q1 a partir de dados reais TriSLA.

SSOT baseline: evidencias_resultados_trisla_v3/raw/raw_dataset_v3.csv
(Não usar evidencias_consolidated/raw/dataset_combined.csv — ver load_merged_rows.)

Opcional: TRISLA_IEEE_INCLUDE_REJECT_STRESS=1 para acrescentar reject_stress_*.csv (nunca dataset_combined).

Saída: evidencias_resultados_trisla_v3_ieee_final/{figures,figures_article_overleaf,manifest,logs}
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception as exc:
    raise SystemExit(f"matplotlib + numpy required: {exc}")

# --- Paths ---
REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_BASE = REPO_ROOT / "evidencias_resultados_trisla_v3_ieee_final"
FIG_DIR = OUT_BASE / "figures"
OVERLEAF_DIR = OUT_BASE / "figures_article_overleaf"
MANIFEST_DIR = OUT_BASE / "manifest"
LOG_PATH = OUT_BASE / "logs" / "generate_ieee_q1.log"

V3 = REPO_ROOT / "evidencias_resultados_trisla_v3" / "raw" / "raw_dataset_v3.csv"
REJECT_CONS = REPO_ROOT / "evidencias_reject_stress" / "raw" / "reject_stress_dataset_consolidated.csv"
REJECT_SINGLE = REPO_ROOT / "evidencias_reject_stress" / "raw" / "reject_stress_dataset.csv"

# --- Visual (prompt) ---
DPI = 300
# Aspect ratio ~ 1.86 (w/h)
FIG_W, FIG_H = 11.16, 6.0

C_ACCEPT = "#2E5AAC"
C_RENEGOTIATE = "#E67E22"
C_REJECT = "#C0392B"
C_ML_RISK = "#641E16"
C_FEAS = "#1E5631"
C_NASP = "#4A148C"
C_PRESSURE = "#2F4F4F"
C_GRID = "#B0BEC5"

DECISION_ORDER = ("ACCEPT", "RENEGOTIATE", "REJECT")
DECISION_COLOR = {
    "ACCEPT": C_ACCEPT,
    "RENEGOTIATE": C_RENEGOTIATE,
    "REJECT": C_REJECT,
}

MIN_N_TOTAL = 30
MIN_N_GROUP = 10


def fnum(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def row_ok(r: Dict[str, str]) -> bool:
    o = r.get("ok", "")
    if str(o) not in ("1", "1.0", "True", "true"):
        return False
    d = (r.get("decision") or "").strip().upper()
    if d not in {"ACCEPT", "RENEGOTIATE", "REJECT"}:
        return False
    return True


def normalize_campaign(c: str) -> str:
    c = (c or "").strip()
    if c in ("trisla_v3", "", "baseline", "v3"):
        return "baseline_v3"
    if c in ("reject_stress", "stress"):
        return "reject_stress"
    return c or "baseline_v3"


def extract_load_num(scenario: str) -> Optional[int]:
    s = scenario or ""
    m = re.search(r"_n(\d+)$", s)
    if m:
        return int(m.group(1))
    m2 = re.search(r"sat(\d+)_", s)
    if m2:
        return int(m2.group(1))
    return None


def apply_style():
    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.linestyle": "--",
            "grid.alpha": 0.35,
            "grid.color": C_GRID,
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
        }
    )


def tune_axes(ax):
    for spine in ax.spines.values():
        spine.set_alpha(0.4)


def save_both(fig, stem: Path):
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    fig.savefig(png, dpi=DPI, facecolor="white", bbox_inches="tight")
    fig.savefig(pdf, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    shutil.copy2(png, OVERLEAF_DIR / png.name)
    shutil.copy2(pdf, OVERLEAF_DIR / pdf.name)


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _boxplot_compat(ax, data, categories: List[str], **kwargs):
    """matplotlib < 3.9: labels= ; >=3.9: tick_labels=."""
    try:
        return ax.boxplot(data, tick_labels=categories, **kwargs)
    except TypeError:
        return ax.boxplot(data, labels=categories, **kwargs)


def load_merged_rows() -> Tuple[List[Dict[str, str]], List[str]]:
    """Carrega baseline a partir de raw_dataset_v3 apenas; não usa dataset_combined."""
    sources: List[str] = []
    rows: List[Dict[str, str]] = []

    v3 = read_csv(V3)
    if v3:
        sources.append(str(V3))
        for r in v3:
            rr = dict(r)
            rr["campaign"] = normalize_campaign(rr.get("campaign") or "baseline_v3")
            rows.append(rr)

    if os.environ.get("TRISLA_IEEE_INCLUDE_REJECT_STRESS", "0").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        for path, default_c in (
            (REJECT_CONS, "reject_stress"),
            (REJECT_SINGLE, "reject_stress"),
        ):
            chunk = read_csv(path)
            if not chunk:
                continue
            sources.append(str(path))
            for r in chunk:
                rr = dict(r)
                rr["campaign"] = normalize_campaign(rr.get("campaign") or default_c)
                rows.append(rr)

    return rows, sources


def enrich_row(r: Dict[str, str]) -> Dict[str, str]:
    out = dict(r)
    sem = fnum(out.get("semantic_latency_ms")) or 0.0
    ml = fnum(out.get("ml_latency_ms")) or 0.0
    dec = fnum(out.get("decision_latency_ms")) or 0.0
    nasp = fnum(out.get("nasp_latency_ms")) or 0.0
    bc = fnum(out.get("blockchain_latency_ms")) or 0.0
    out["_semantic"] = sem
    out["_ml"] = ml
    out["_decision"] = dec
    out["_nasp"] = nasp
    out["_bc"] = bc
    tot = sem + ml + dec + nasp + bc
    out["_total_latency_ms"] = tot
    out["_orchestration_ratio"] = (nasp / tot) if tot > 0 else None
    d = (out.get("decision") or "").strip().upper()
    out["_accept"] = 1 if d == "ACCEPT" else 0
    out["_reneg"] = 1 if d == "RENEGOTIATE" else 0
    out["_reject"] = 1 if d == "REJECT" else 0
    ln = extract_load_num(out.get("scenario") or "")
    out["_load_num"] = "" if ln is None else str(ln)
    na = out.get("nasp_latency_available", "")
    out["_nasp_ok"] = str(na) in ("1", "1.0", "True", "true")
    conf = fnum(out.get("confidence"))
    if conf is None:
        conf = fnum(out.get("admission_confidence"))
    out["_conf"] = conf
    return out


def std_vals(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    a = np.array(xs, dtype=float)
    return float(a.std(ddof=1))


def signal_check(
    n_total: int,
    group_counts: Optional[Sequence[int]] = None,
    values: Optional[List[float]] = None,
    *,
    strict_multi_group: bool = False,
) -> Tuple[bool, str]:
    # n_total >= 30 OU cada grupo relevante >= 10 (prompt)
    gc_nonzero = [g for g in (group_counts or []) if g > 0]
    ok_per_group = bool(gc_nonzero) and min(gc_nonzero) >= MIN_N_GROUP
    if n_total < MIN_N_TOTAL and not ok_per_group:
        return False, f"n_total={n_total} < {MIN_N_TOTAL} sem grupos n>={MIN_N_GROUP}"
    if values is not None and len(values) >= 2:
        if std_vals(values) <= 0:
            return False, "std==0 (valor único)"
    if strict_multi_group and group_counts:
        non_zero = [g for g in group_counts if g > 0]
        if len(non_zero) < 2:
            return False, "menos de 2 grupos com dados para comparação"
    return True, "ok"


def pearson_r(x: List[float], y: List[float]) -> Optional[float]:
    if len(x) < 3 or len(x) != len(y):
        return None
    a, b = np.array(x), np.array(y)
    if np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


# --- Figures ---


def fig_decision_stacked_by_campaign(
    valid: List[Dict[str, str]],
) -> Dict[str, Any]:
    fid = "fig01_decision_by_campaign"
    title = "Decision distribution by campaign (stacked)"
    by_c: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in valid:
        c = r.get("campaign") or "unknown"
        d = (r.get("decision") or "").upper()
        by_c[c][d] += 1
    campaigns = sorted(by_c.keys())
    n_tot = len(valid)
    counts_mat = [[by_c[c].get(d, 0) for d in DECISION_ORDER] for c in campaigns]
    flat = [v for row in counts_mat for v in row]
    ok_sig, reason = signal_check(
        n_tot,
        group_counts=[sum(row) for row in counts_mat],
        values=[float(x) for x in flat],
        strict_multi_group=False,
    )
    if not campaigns:
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], reason, "")

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    x = np.arange(len(campaigns))
    bottom = np.zeros(len(campaigns))
    for j, d in enumerate(DECISION_ORDER):
        vals = np.array([by_c[c].get(d, 0) for c in campaigns], dtype=float)
        ax.bar(x, vals, bottom=bottom, label=d, color=DECISION_COLOR[d], edgecolor="#333", linewidth=0.4)
        bottom += vals
    ax.set_xticks(x)
    ax.set_xticklabels(campaigns, rotation=15, ha="right")
    ax.set_ylabel("Count (requests)")
    ax.set_xlabel("Campaign")
    ax.legend(title="Decision")
    ax.set_title(title + f" (n={n_tot})")
    reject_n = sum(1 for r in valid if (r.get("decision") or "").upper() == "REJECT")
    note = f"REJECT count={reject_n} (explicit)." if reject_n == 0 else f"REJECT count={reject_n}."
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig else "EXCLUDED_LOW_SIGNAL"
    stem = FIG_DIR / fid
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, stem)
    else:
        plt.close(fig)
    return figure_manifest(
        fid,
        title,
        status,
        n_tot,
        campaigns,
        ["decision", "campaign"],
        note if ok_sig else reason,
        "Stacked bars SLA-aware; REJECT=0 não ocultado." if reject_n == 0 else "Multi-campaign decision mix.",
    )


def fig_decision_by_slice(valid: List[Dict[str, str]]) -> Dict[str, Any]:
    fid = "fig02_decision_by_slice"
    title = "Decision distribution by slice type"
    slices = sorted({(r.get("slice_type") or "UNK").upper() for r in valid})
    by_s: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in valid:
        s = (r.get("slice_type") or "UNK").upper()
        d = (r.get("decision") or "").upper()
        by_s[s][d] += 1
    n_tot = len(valid)
    group_sizes = [sum(by_s[s].values()) for s in slices]
    ok_sig, reason = signal_check(n_tot, group_counts=group_sizes, strict_multi_group=True)
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    x = np.arange(len(slices))
    width = 0.25
    for i, d in enumerate(DECISION_ORDER):
        offs = (i - 1) * width
        heights = [by_s[s].get(d, 0) for s in slices]
        ax.bar(x + offs, heights, width, label=d, color=DECISION_COLOR[d], edgecolor="#333", linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels(slices)
    ax.set_ylabel("Count")
    ax.set_xlabel("Slice type")
    ax.legend()
    ax.set_title(f"{title} (n={n_tot})")
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig and len(slices) >= 2 else "EXCLUDED_LOW_SIGNAL"
    if not slices:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], "no slices", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, slices, ["slice_type", "decision"], reason, "Slice differentiation.")


def fig_decision_by_scenario(valid: List[Dict[str, str]]) -> Dict[str, Any]:
    fid = "fig03_decision_by_scenario"
    title = "Decision distribution by scenario (load profiles)"
    scenarios = sorted({(r.get("scenario") or "").strip() for r in valid if (r.get("scenario") or "").strip()})
    if len(scenarios) > 24:
        scenarios = scenarios[:24]
    by: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in valid:
        sc = (r.get("scenario") or "").strip()
        if sc not in scenarios:
            continue
        d = (r.get("decision") or "").upper()
        by[sc][d] += 1
    n_tot = sum(sum(by[s].values()) for s in scenarios)
    ok_sig, reason = signal_check(
        n_tot,
        group_counts=[sum(by[s].values()) for s in scenarios],
        strict_multi_group=True,
    )
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    x = np.arange(len(scenarios))
    width = 0.25
    for i, d in enumerate(DECISION_ORDER):
        offs = (i - 1) * width
        ax.bar(x + offs, [by[s].get(d, 0) for s in scenarios], width, label=d, color=DECISION_COLOR[d], edgecolor="#333", linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("Count")
    ax.set_xlabel("Scenario")
    ax.legend()
    ax.set_title(f"{title} (n={n_tot})")
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig and len(scenarios) >= 2 else "EXCLUDED_LOW_SIGNAL"
    if not scenarios:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], "no scenarios", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, scenarios, ["scenario"], reason, "Load/scenario effect.")


def rates_vs_load(valid: List[Dict[str, str]], fid: str, title: str, rate_key: str) -> Dict[str, Any]:
    loads = [1, 3, 10, 50]
    subset = [r for r in valid if r.get("_load_num") in {str(x) for x in loads}]
    by_l: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for r in subset:
        by_l[r["_load_num"]].append(r)
    xs = []
    ys = []
    for L in loads:
        grp = by_l.get(str(L), [])
        if not grp:
            continue
        n = len(grp)
        if rate_key == "accept":
            ys.append(sum(1 for r in grp if r.get("decision", "").upper() == "ACCEPT") / n)
        elif rate_key == "reneg":
            ys.append(sum(1 for r in grp if r.get("decision", "").upper() == "RENEGOTIATE") / n)
        else:
            ys.append(sum(1 for r in grp if r.get("decision", "").upper() == "REJECT") / n)
        xs.append(L)
    n_tot = len(subset)
    vals = [float(y) for y in ys]
    ok_sig, reason = signal_check(
        n_tot,
        group_counts=[len(by_l[str(L)]) for L in loads if str(L) in by_l],
        values=vals,
        strict_multi_group=True,
    )
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    if xs:
        ax.plot(xs, ys, marker="o", linewidth=2, markersize=8, color=C_ACCEPT if rate_key == "accept" else C_RENEGOTIATE if rate_key == "reneg" else C_REJECT)
    ax.set_xticks(loads)
    ax.set_xlabel("Load (requests per scenario)")
    ax.set_ylabel("Rate")
    ax.set_ylim(0, 1.05)
    ax.set_title(f"{title} (n={n_tot})")
    tune_axes(ax)
    if rate_key == "reject" and sum(ys) == 0 and n_tot > 0:
        ok_sig = False
        reason = "REJECT rate zero — low scientific value for this curve"
    status = "INCLUDED_IN_PAPER" if ok_sig and len(xs) >= 2 else "EXCLUDED_LOW_SIGNAL"
    if not xs:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", n_tot, [], ["load"], "no load-tagged rows", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, [str(x) for x in xs], ["scenario", "decision"], reason, title)


def boxplot_by_decision(
    valid: List[Dict[str, str]],
    fid: str,
    title: str,
    value_fn: Callable[[Dict[str, str]], Optional[float]],
    ylabel: str,
    color_bar: str,
) -> Dict[str, Any]:
    by_d: Dict[str, List[float]] = defaultdict(list)
    for r in valid:
        d = (r.get("decision") or "").upper()
        v = value_fn(r)
        if v is not None:
            by_d[d].append(v)
    orders = [d for d in DECISION_ORDER if by_d.get(d)]
    data = [by_d[d] for d in orders]
    n_tot = sum(len(x) for x in data)
    group_counts = [len(x) for x in data]
    allv = [v for row in data for v in row]
    ok_sig, reason = signal_check(
        n_tot, group_counts=group_counts, values=allv, strict_multi_group=True
    )
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    if data:
        bp = _boxplot_compat(ax, data, orders, patch_artist=True)
        for patch in bp["boxes"]:
            patch.set_facecolor(color_bar)
            patch.set_alpha(0.55)
        rng = np.random.default_rng(42)
        for i, d in enumerate(orders):
            vals = by_d[d]
            jitter = rng.normal(0, 0.04, size=len(vals))
            ax.scatter(np.ones(len(vals)) * (i + 1) + jitter, vals, s=12, alpha=0.45, color="#222", zorder=3)
        ax.set_title(f"{title} (N={{{', '.join(f'{d}:{len(by_d[d])}' for d in orders)}}})")
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Decision")
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig and len(orders) >= 2 else "EXCLUDED_LOW_SIGNAL"
    if not orders:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], "no numeric values", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, orders, [ylabel, "decision"], reason, title)


def scatter_two(
    valid: List[Dict[str, str]],
    fid: str,
    title: str,
    xfn: Callable[[Dict[str, str]], Optional[float]],
    yfn: Callable[[Dict[str, str]], Optional[float]],
    xlab: str,
    ylab: str,
    annotate_r: bool = False,
) -> Dict[str, Any]:
    xs, ys, cs = [], [], []
    for r in valid:
        x = xfn(r)
        y = yfn(r)
        if x is None or y is None:
            continue
        xs.append(x)
        ys.append(y)
        cs.append(DECISION_COLOR.get((r.get("decision") or "").upper(), "#888"))
    n_tot = len(xs)
    ok_sig, reason = signal_check(n_tot, values=xs + ys, strict_multi_group=False)
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    ax.scatter(xs, ys, c=cs, s=28, alpha=0.65, edgecolors="k", linewidths=0.2)
    from matplotlib.lines import Line2D

    leg = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_ACCEPT, label="ACCEPT", markersize=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_RENEGOTIATE, label="RENEGOTIATE", markersize=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_REJECT, label="REJECT", markersize=8),
    ]
    if n_tot >= 3 and len(set(xs)) > 1:
        coef = np.polyfit(xs, ys, 1)
        xp = np.linspace(min(xs), max(xs), 50)
        (ln,) = ax.plot(xp, np.poly1d(coef)(xp), "--", color="#444", linewidth=1.2, label="Linear guide")
        leg.append(ln)
    sub = title
    if annotate_r:
        rpv = pearson_r(xs, ys)
        if rpv is not None:
            sub += f" (Pearson r={rpv:.3f})"
    ax.set_title(sub + f" n={n_tot}")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    tune_axes(ax)
    ax.legend(handles=leg, loc="best")
    status = "INCLUDED_IN_PAPER" if ok_sig else "EXCLUDED_LOW_SIGNAL"
    if n_tot == 0:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], "no pairs", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, [], [xlab, ylab], reason, title)


def fig_nasp_by_slice(valid: List[Dict[str, str]]) -> Dict[str, Any]:
    fid = "fig13_nasp_latency_by_slice"
    title = "NASP adapter latency by slice (nasp_latency_available=1)"
    sub = [r for r in valid if r.get("_nasp_ok") and fnum(r.get("nasp_latency_ms")) is not None]
    by_s: Dict[str, List[float]] = defaultdict(list)
    for r in sub:
        v = fnum(r.get("nasp_latency_ms"))
        if v is not None:
            by_s[(r.get("slice_type") or "UNK").upper()].append(v)
    orders = sorted(by_s.keys())
    data = [by_s[s] for s in orders]
    n_tot = len(sub)
    ok_sig, reason = signal_check(
        n_tot,
        group_counts=[len(x) for x in data],
        values=[v for row in data for v in row],
        strict_multi_group=True,
    )
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    if data:
        bp = _boxplot_compat(ax, data, orders, patch_artist=True)
        for patch in bp["boxes"]:
            patch.set_facecolor(C_NASP)
            patch.set_alpha(0.55)
    ax.set_ylabel("NASP latency (ms)")
    ax.set_xlabel("Slice")
    ax.set_title(f"{title} (n={n_tot})")
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig and n_tot >= MIN_N_GROUP else "EXCLUDED_NO_REAL_DATA"
    if n_tot == 0:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], ["nasp_latency_ms"], "no NASP rows", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, orders, ["nasp_latency_ms", "slice_type"], reason, "Real orchestration cost.")


def fig_orchestration_ratio(valid: List[Dict[str, str]]) -> Dict[str, Any]:
    fid = "fig15_orchestration_ratio"
    title = "Orchestration ratio (nasp / total latency)"
    vals = []
    for r in valid:
        rr = fnum(r.get("_orchestration_ratio"))
        if rr is not None and 0 <= rr <= 1:
            vals.append(rr)
    n_tot = len(vals)
    ok_sig, reason = signal_check(n_tot, values=vals, strict_multi_group=False)
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    if vals:
        _boxplot_compat(ax, [vals], ["all"], patch_artist=True)
    ax.set_ylabel("Ratio (dimensionless)")
    ax.set_title(f"{title} n={n_tot}")
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig else "EXCLUDED_LOW_SIGNAL"
    if n_tot == 0:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], ["orchestration_ratio"], "no ratio", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, ["all"], ["nasp_latency_ms", "total_latency"], reason, "E2E share.")


def fig_latency_stacked_campaign(valid: List[Dict[str, str]]) -> Dict[str, Any]:
    fid = "fig16_pipeline_latency_breakdown"
    title = "Mean pipeline latency breakdown by campaign"
    camps = sorted({r.get("campaign") or "x" for r in valid})
    comps = [
        ("_semantic", "semantic", C_ACCEPT),
        ("_ml", "ml", C_ML_RISK),
        ("_decision", "decision", C_RENEGOTIATE),
        ("_nasp", "nasp", C_NASP),
        ("_bc", "blockchain", C_PRESSURE),
    ]
    n_tot = len(valid)
    ok_sig, reason = signal_check(
        n_tot,
        group_counts=[len([r for r in valid if r.get("campaign") == c]) for c in camps],
        strict_multi_group=False,
    )
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    x = np.arange(len(camps))
    bottom = np.zeros(len(camps))
    for i, (key, lab, col) in enumerate(comps):
        heights = []
        for camp in camps:
            slice_g = [r for r in valid if r.get("campaign") == camp]
            vs = [float(r.get(key, 0) or 0) for r in slice_g]
            heights.append(float(np.mean(vs)) if vs else 0.0)
        ax.bar(x, heights, bottom=bottom, label=lab, color=col, edgecolor="#333", linewidth=0.3, alpha=0.85)
        bottom += np.array(heights)
    ax.set_xticks(x)
    ax.set_xticklabels(camps)
    ax.set_ylabel("Mean latency (ms)")
    ax.set_xlabel("Campaign")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"{title} (n={n_tot})")
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig and len(camps) >= 1 else "EXCLUDED_LOW_SIGNAL"
    if not camps:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], "no campaigns", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, camps, [c[1] for c in comps], reason, "Stacked pipeline.")


def fig_domain_by_slice(valid: List[Dict[str, str]]) -> Dict[str, Any]:
    fid = "fig17_domain_metrics_by_slice"
    title = "Domain metrics by slice (mean)"
    slices = sorted({(r.get("slice_type") or "UNK").upper() for r in valid})
    metrics = [
        ("ran_prb_utilization", "RAN PRB", C_ACCEPT),
        ("transport_rtt", "Transport RTT", C_RENEGOTIATE),
        ("core_cpu", "Core CPU", C_NASP),
    ]
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    x = np.arange(len(slices))
    w = 0.25
    n_tot = len(valid)
    for i, (field, lab, col) in enumerate(metrics):
        means = []
        for s in slices:
            grp = [r for r in valid if (r.get("slice_type") or "").upper() == s]
            vs = [fnum(r.get(field)) for r in grp]
            vs = [v for v in vs if v is not None]
            means.append(float(np.mean(vs)) if vs else 0.0)
        ax.bar(x + (i - 1) * w, means, w, label=lab, color=col, alpha=0.8, edgecolor="#333", linewidth=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(slices)
    ax.set_ylabel("Value (native units)")
    ax.legend()
    ax.set_title(f"{title} (n={n_tot})")
    tune_axes(ax)
    ok_sig, reason = signal_check(
        n_tot,
        group_counts=[len([r for r in valid if (r.get("slice_type") or "").upper() == s]) for s in slices],
        strict_multi_group=True,
    )
    status = "INCLUDED_IN_PAPER" if ok_sig and len(slices) >= 2 else "EXCLUDED_LOW_SIGNAL"
    if not slices:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], "no slice", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, slices, [m[0] for m in metrics], reason, "RAN/transport/core.")


def fig_mean_bar_with_se(
    valid: List[Dict[str, str]],
    fid: str,
    title: str,
    field: str,
    ylabel: str,
    color: str,
) -> Dict[str, Any]:
    slices = sorted({(r.get("slice_type") or "UNK").upper() for r in valid})
    means, ses = [], []
    for s in slices:
        grp = [r for r in valid if (r.get("slice_type") or "").upper() == s]
        vs = [fnum(r.get(field)) for r in grp]
        vs = [v for v in vs if v is not None]
        if vs:
            means.append(float(np.mean(vs)))
            ses.append(float(np.std(vs, ddof=1) / math.sqrt(len(vs))) if len(vs) > 1 else 0.0)
        else:
            means.append(0.0)
            ses.append(0.0)
    n_tot = len(valid)
    ok_sig, reason = signal_check(
        n_tot,
        group_counts=[len([r for r in valid if (r.get("slice_type") or "").upper() == s]) for s in slices],
        strict_multi_group=True,
    )
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    x = np.arange(len(slices))
    ax.bar(x, means, yerr=ses, capsize=4, color=color, edgecolor="#333", linewidth=0.4, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(slices)
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title} (n={n_tot})")
    tune_axes(ax)
    status = "INCLUDED_IN_PAPER" if ok_sig and len(slices) >= 2 else "EXCLUDED_LOW_SIGNAL"
    if not slices:
        plt.close(fig)
        return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", 0, [], [], "", "")
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(fid, title, status, n_tot, slices, [field], reason, title)


def fig_campaign_comparison(valid: List[Dict[str, str]]) -> Dict[str, Any]:
    fid = "fig20_campaign_comparison"
    title = "Campaign comparison: baseline vs reject stress"
    camps = sorted({r.get("campaign") or "" for r in valid})
    if len(camps) < 2:
        return figure_manifest(
            fid,
            title,
            "EXCLUDED_NO_REAL_DATA",
            len(valid),
            camps,
            ["campaign"],
            "Need >=2 campaigns in combined dataset",
            "",
        )
    metrics = [
        ("ml_risk_score", "mean ML risk", C_ML_RISK),
        ("resource_pressure", "mean resource pressure", C_PRESSURE),
        ("feasibility_score", "mean feasibility", C_FEAS),
    ]
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    x = np.arange(len(camps))
    w = 0.25
    for i, (field, lab, col) in enumerate(metrics):
        vals = []
        for c in camps:
            grp = [r for r in valid if r.get("campaign") == c]
            vs = [fnum(r.get(field)) for r in grp]
            vs = [v for v in vs if v is not None]
            vals.append(float(np.mean(vs)) if vs else float("nan"))
        ax.bar(x + (i - 1) * w, vals, w, label=lab, color=col, alpha=0.85, edgecolor="#333", linewidth=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(camps)
    ax.legend()
    ax.set_title(f"{title} (n={len(valid)})")
    tune_axes(ax)
    ok_sig, reason = signal_check(
        len(valid),
        group_counts=[len([r for r in valid if r.get("campaign") == c]) for c in camps],
        strict_multi_group=True,
    )
    status = "INCLUDED_IN_PAPER" if ok_sig else "EXCLUDED_LOW_SIGNAL"
    if status == "INCLUDED_IN_PAPER":
        save_both(fig, FIG_DIR / fid)
    else:
        plt.close(fig)
    return figure_manifest(
        fid,
        title,
        status,
        len(valid),
        camps,
        [m[0] for m in metrics],
        reason,
        "Stress vs baseline.",
    )


def figure_manifest(
    figure_id: str,
    title: str,
    status: str,
    n_total: int,
    groups: List[str],
    columns_used: List[str],
    scientific_note: str,
    why: str,
) -> Dict[str, Any]:
    return {
        "figure_id": figure_id,
        "title": title,
        "status": status,
        "n_total": n_total,
        "groups": groups,
        "columns_used": columns_used,
        "scientific_note": scientific_note,
        "why_included_or_excluded": why,
    }


def main() -> int:
    apply_style()
    OUT_BASE.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    OVERLEAF_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows, sources = load_merged_rows()
    enriched = [enrich_row(r) for r in rows]
    valid = [r for r in enriched if row_ok(r)]

    log_lines = [
        f"{datetime.now(timezone.utc).isoformat()} sources={sources}",
        f"rows_total={len(rows)} valid={len(valid)}",
    ]
    LOG_PATH.write_text("\n".join(log_lines), encoding="utf-8")

    figures: List[Dict[str, Any]] = []
    figures.append(fig_decision_stacked_by_campaign(valid))
    figures.append(fig_decision_by_slice(valid))
    figures.append(fig_decision_by_scenario(valid))
    figures.append(rates_vs_load(valid, "fig04_accept_rate_vs_load", "Accept rate vs load", "accept"))
    figures.append(rates_vs_load(valid, "fig05_renegotiate_rate_vs_load", "Renegotiate rate vs load", "reneg"))
    figures.append(rates_vs_load(valid, "fig06_reject_rate_vs_load", "Reject rate vs load", "reject"))
    figures.append(
        boxplot_by_decision(
            valid,
            "fig07_ml_risk_by_decision",
            "ML risk score by decision",
            lambda r: fnum(r.get("ml_risk_score")),
            "ML risk score",
            C_ML_RISK,
        )
    )
    figures.append(
        boxplot_by_decision(
            valid,
            "fig08_feasibility_by_decision",
            "Feasibility score by decision",
            lambda r: fnum(r.get("feasibility_score")),
            "Feasibility",
            C_FEAS,
        )
    )
    figures.append(
        boxplot_by_decision(
            valid,
            "fig09_resource_pressure_by_decision",
            "Resource pressure by decision",
            lambda r: fnum(r.get("resource_pressure")),
            "Resource pressure",
            C_PRESSURE,
        )
    )
    figures.append(
        scatter_two(
            valid,
            "fig10_ml_risk_vs_resource_pressure",
            "ML risk vs resource pressure",
            lambda r: fnum(r.get("resource_pressure")),
            lambda r: fnum(r.get("ml_risk_score")),
            "Resource pressure",
            "ML risk score",
            False,
        )
    )
    figures.append(
        scatter_two(
            valid,
            "fig11_feasibility_vs_resource_pressure",
            "Feasibility vs resource pressure",
            lambda r: fnum(r.get("resource_pressure")),
            lambda r: fnum(r.get("feasibility_score")),
            "Resource pressure",
            "Feasibility score",
            True,
        )
    )
    figures.append(
        boxplot_by_decision(
            valid,
            "fig12_confidence_by_decision",
            "Confidence / admission confidence by decision",
            lambda r: fnum(r.get("confidence")) or fnum(r.get("admission_confidence")),
            "Confidence",
            C_ACCEPT,
        )
    )
    figures.append(fig_nasp_by_slice(valid))
    # fig14 nasp by load — reuse rates structure with median nasp per load bucket
    def fig14():
        fid = "fig14_nasp_latency_by_load"
        title = "NASP latency by load (median)"
        loads = [1, 3, 10, 50]
        subset = [r for r in valid if r.get("_nasp_ok") and r.get("_load_num") in {str(x) for x in loads}]
        by_l: Dict[int, List[float]] = defaultdict(list)
        for r in subset:
            ln = int(r["_load_num"])
            v = fnum(r.get("nasp_latency_ms"))
            if v is not None:
                by_l[ln].append(v)
        xs, ys = [], []
        for L in loads:
            if by_l.get(L):
                xs.append(L)
                ys.append(float(np.median(by_l[L])))
        n_tot = len(subset)
        ok_sig, reason = signal_check(n_tot, values=ys, strict_multi_group=True)
        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        if xs:
            ax.plot(xs, ys, marker="s", color=C_NASP, linewidth=2, markersize=8)
        ax.set_xticks(loads)
        ax.set_xlabel("Load")
        ax.set_ylabel("Median NASP latency (ms)")
        ax.set_title(f"{title} n={n_tot}")
        tune_axes(ax)
        st = "INCLUDED_IN_PAPER" if ok_sig and len(xs) >= 2 else "EXCLUDED_LOW_SIGNAL"
        if not xs:
            plt.close(fig)
            return figure_manifest(fid, title, "EXCLUDED_NO_REAL_DATA", n_tot, [], ["nasp"], "no data", "")
        if st == "INCLUDED_IN_PAPER":
            save_both(fig, FIG_DIR / fid)
        else:
            plt.close(fig)
        return figure_manifest(fid, title, st, n_tot, [str(x) for x in xs], ["nasp_latency_ms", "load"], reason, title)

    figures.append(fig14())
    figures.append(fig_orchestration_ratio(valid))
    figures.append(fig_latency_stacked_campaign(valid))
    figures.append(fig_domain_by_slice(valid))
    figures.append(fig_mean_bar_with_se(valid, "fig18_mean_pressure_by_slice", "Mean resource pressure by slice", "resource_pressure", "Mean pressure", C_PRESSURE))
    figures.append(fig_mean_bar_with_se(valid, "fig19_mean_feasibility_by_slice", "Mean feasibility by slice", "feasibility_score", "Mean feasibility", C_FEAS))
    figures.append(fig_campaign_comparison(valid))

    included = sum(1 for f in figures if f["status"] == "INCLUDED_IN_PAPER")
    excluded_ls = sum(1 for f in figures if f["status"] == "EXCLUDED_LOW_SIGNAL")
    excluded_nd = sum(1 for f in figures if f["status"] == "EXCLUDED_NO_REAL_DATA")
    excluded_rd = sum(1 for f in figures if f["status"] == "EXCLUDED_REDUNDANT")

    dist: Dict[str, int] = defaultdict(int)
    for r in valid:
        dist[(r.get("decision") or "").upper()] += 1

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_sources": sources,
        "rows_ingested": len(rows),
        "rows_valid_scientific": len(valid),
        "generated_count": len(figures),
        "included_count": included,
        "excluded_low_signal": excluded_ls,
        "excluded_no_real_data": excluded_nd,
        "excluded_redundant": excluded_rd,
        "decision_distribution_global": dict(dist),
        "campaigns_present": sorted({r.get("campaign") for r in valid}),
        "scientific_status": "OK" if included >= 12 and len(figures) >= 15 else "INSUFFICIENT_SIGNAL_OR_DATA",
        "figures": figures,
        "criteria_note": "Target: >=15 generated, >=12 INCLUDED; requires real E2E datasets with ok=1.",
    }
    (MANIFEST_DIR / "MANIFESTO.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in manifest if k != "figures"}, indent=2))
    return 0 if manifest["scientific_status"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
