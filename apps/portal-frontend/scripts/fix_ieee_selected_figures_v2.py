#!/usr/bin/env python3
import csv
import json
from pathlib import Path

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception as exc:
    raise SystemExit(f"matplotlib unavailable: {exc}")


RUN_DIR = Path("/home/porvir5g/gtp5g/trisla/evidencias_resultados_article_trisla_v2/run_20260320_220653")
RAW_PATH = RUN_DIR / "raw" / "raw_dataset_v2.csv"
ML_PATH = RUN_DIR / "raw" / "ml_dataset_v2.csv"
OUT_DIR = RUN_DIR / "figures_ieee_v2"

COLORS = {
    "semantic": "#4C78A8",
    "ml": "#72B7B2",
    "decision": "#F58518",
    "ACCEPT": "#54A24B",
    "REJECT": "#E45756",
    "RENEGOTIATE": "#B279A2",
    "mean": "#4C78A8",
    "p95": "#F58518",
    "p99": "#B279A2",
}


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None


def style():
    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.linestyle": "--",
            "grid.alpha": 0.3,
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "legend.fontsize": 10,
        }
    )


def tune(ax):
    for spine in ax.spines.values():
        spine.set_alpha(0.3)


def save(fig, filename):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=400, facecolor="white")
    plt.close(fig)
    return path


def load_data():
    raw = read_csv(RAW_PATH)
    ml = read_csv(ML_PATH)
    valid = []
    for r in raw:
        s = (r.get("scenario") or "").strip()
        e2e = fnum(r.get("e2e_latency_ms"))
        if not s or e2e is None or e2e <= 0:
            continue
        valid.append(
            {
                "scenario": s,
                "decision": (r.get("decision") or "").strip().upper(),
                "ml_risk_score": fnum(r.get("ml_risk_score")),
            }
        )
    ml_valid = []
    for r in ml:
        d = (r.get("decision") or "").strip().upper()
        sc = fnum(r.get("ml_risk_score"))
        if d in {"ACCEPT", "REJECT", "RENEGOTIATE"} and sc is not None:
            ml_valid.append({"decision": d, "ml_risk_score": sc})
    return valid, ml_valid


def plot_03(valid):
    order = ["scenario_1", "scenario_10", "scenario_50"]
    acc, rej, ren = [], [], []
    for s in order:
        rows = [r for r in valid if r["scenario"] == s]
        t = len(rows)
        acc.append(sum(1 for r in rows if r["decision"] == "ACCEPT") / t if t else 0.0)
        rej.append(sum(1 for r in rows if r["decision"] == "REJECT") / t if t else 0.0)
        ren.append(sum(1 for r in rows if r["decision"] == "RENEGOTIATE") / t if t else 0.0)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    b1 = ax.bar(order, acc, color=COLORS["ACCEPT"], alpha=0.85, linewidth=2, label="ACCEPT")
    b2 = ax.bar(order, rej, bottom=acc, color=COLORS["REJECT"], alpha=0.85, linewidth=2, label="REJECT")
    b3 = ax.bar(order, ren, bottom=[a + r for a, r in zip(acc, rej)], color=COLORS["RENEGOTIATE"], alpha=0.85, linewidth=2, label="RENEGOTIATE")

    for bars, vals, bottom in [(b1, acc, [0, 0, 0]), (b2, rej, acc), (b3, ren, [a + r for a, r in zip(acc, rej)])]:
        for rect, v, b in zip(bars, vals, bottom):
            if v > 0:
                ax.text(rect.get_x() + rect.get_width() / 2, b + v / 2, f"{v*100:.1f}%", ha="center", va="center", fontsize=9, color="white")
    ax.set_title("Figure 3 - Decision Distribution by Scenario")
    ax.set_ylabel("Proportion")
    ax.legend()
    tune(ax)
    return save(fig, "figure_03_decision_distribution_by_scenario.png")


def plot_04(valid):
    total = len(valid)
    ratios = {
        "ACCEPT": sum(1 for r in valid if r["decision"] == "ACCEPT") / total if total else 0,
        "REJECT": sum(1 for r in valid if r["decision"] == "REJECT") / total if total else 0,
        "RENEGOTIATE": sum(1 for r in valid if r["decision"] == "RENEGOTIATE") / total if total else 0,
    }
    ordered = sorted(ratios.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in ordered]
    vals = [v for _, v in ordered]
    colors = [COLORS[k] for k in labels]
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    bars = ax.barh(labels, vals, color=colors, alpha=0.85, linewidth=2)
    for bar, v in zip(bars, vals):
        ax.text(v + 0.01, bar.get_y() + bar.get_height() / 2, f"{v*100:.1f}%", va="center", fontsize=10)
    ax.set_xlim(0, max(vals) * 1.25 if vals else 1)
    ax.set_title("Figure 4 - Global Decision Distribution")
    ax.set_xlabel("Proportion")
    tune(ax)
    return save(fig, "figure_04_global_decision_distribution.png")


def plot_05(ml_valid):
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    order = ["ACCEPT", "RENEGOTIATE", "REJECT"]
    data = [[r["ml_risk_score"] for r in ml_valid if r["decision"] == d] for d in order]
    labels = [d for d, vals in zip(order, data) if vals]
    data = [vals for vals in data if vals]
    if len(labels) < 2 or any(len(v) < 5 for v in data):
        raise RuntimeError("Figure 5 cannot be generated: insufficient decision class diversity (>=2 classes with n>=5).")

    # Boxplot + jitter strip; no KDE if N < 10.
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True)
    for patch, d in zip(bp["boxes"], labels):
        patch.set(facecolor=COLORS[d], alpha=0.35, edgecolor=COLORS[d], linewidth=2)

    for i, (d, vals) in enumerate(zip(labels, data), start=1):
        jitter = np.random.uniform(-0.08, 0.08, size=len(vals))
        ax.scatter(np.full(len(vals), i) + jitter, vals, s=16, alpha=0.75, color=COLORS[d], linewidths=0)
    ax.set_title("Figure 5 - ML Risk Distribution by Decision")
    ax.set_ylabel("ML Risk Score")
    ax.text(
        0.99,
        0.98,
        "N total=" + str(sum(len(v) for v in data)) + " | " + " | ".join(f"{l}={len(v)}" for l, v in zip(labels, data)),
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
    )
    tune(ax)
    return save(fig, "figure_05_ml_risk_distribution_by_decision.png")


def plot_09(ml_valid):
    # Rule: use boxplot or stripplot with jitter.
    order = ["REJECT", "RENEGOTIATE", "ACCEPT"]
    data = [[r["ml_risk_score"] for r in ml_valid if r["decision"] == d] for d in order]
    labels = [d for d, vals in zip(order, data) if vals]
    data = [vals for vals in data if vals]
    if len(data) < 2:
        return None

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True)
    for patch, d in zip(bp["boxes"], labels):
        patch.set(facecolor=COLORS[d], alpha=0.35, edgecolor=COLORS[d], linewidth=2)
    for i, (d, vals) in enumerate(zip(labels, data), start=1):
        jitter = np.random.uniform(-0.08, 0.08, size=len(vals))
        ax.scatter(np.full(len(vals), i) + jitter, vals, s=14, alpha=0.8, color=COLORS[d], linewidths=0)
    ax.set_title("Figure 9 - ML Risk vs Decision")
    ax.set_ylabel("ML Risk Score")
    tune(ax)
    return save(fig, "figure_09_ml_risk_vs_decision.png")


def validate(out_files):
    for p in out_files:
        if p is None:
            continue
        if not p.exists() or p.stat().st_size <= 0:
            raise RuntimeError(f"Invalid output file: {p}")


def main():
    style()
    valid, ml_valid = load_data()
    generated = []

    generated.append(plot_03(valid))
    generated.append(plot_04(valid))
    generated.append(plot_05(ml_valid))

    fig9 = plot_09(ml_valid)
    removed = []
    if fig9 is None:
        removed.append(9)
    else:
        generated.append(fig9)

    # Figure 10: option A (remove, recommended).
    removed.append(10)

    validate(generated)

    report = {
        "fixed_figures": [3, 4, 5, 9, 10],
        "removed_figures": sorted(set(removed)),
        "notes": "Visualization corrected for scientific validity",
    }
    (OUT_DIR / "fix_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(OUT_DIR))


if __name__ == "__main__":
    main()
