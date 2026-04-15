#!/usr/bin/env python3
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception as exc:
    raise SystemExit(f"matplotlib unavailable: {exc}")


RUN_DIR = Path("/home/porvir5g/gtp5g/trisla/evidencias_resultados_article_trisla_v2/run_20260320_220653")
RAW_DATASET = RUN_DIR / "raw" / "raw_dataset_v2.csv"
ML_DATASET = RUN_DIR / "raw" / "ml_dataset_v2.csv"
METRICS_SCENARIO = RUN_DIR / "processed" / "metrics_by_scenario_v2.csv"
FIG_DIR = RUN_DIR / "figures_v3"


COLORS = {
    "latency_blue": "#1f77b4",
    "accept_green": "#2ca02c",
    "reneg_orange": "#ff7f0e",
    "neutral_gray": "#7f7f7f",
}


def read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None


def cdf(vals):
    x = np.sort(np.array(vals))
    y = np.arange(1, len(x) + 1) / len(x)
    return x, y


def save_figure(fig, preferred_name: str):
    """Never overwrite existing files; create suffixed version if needed."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    target = FIG_DIR / preferred_name
    if target.exists():
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        target = FIG_DIR / preferred_name.replace(".png", f"_{ts}.png")
    fig.savefig(target, dpi=350, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return target.name


def kde_curve(values, points=200):
    """Simple Gaussian KDE with Silverman bandwidth, no scipy dependency."""
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n < 2:
        return None, None
    std = np.std(arr, ddof=1)
    if std == 0:
        return None, None
    bw = 1.06 * std * (n ** (-1 / 5))
    if bw <= 0:
        return None, None
    xmin, xmax = arr.min(), arr.max()
    pad = (xmax - xmin) * 0.1 if xmax > xmin else 1e-6
    xs = np.linspace(xmin - pad, xmax + pad, points)
    density = np.zeros_like(xs)
    norm = 1 / (math.sqrt(2 * math.pi) * bw * n)
    for v in arr:
        u = (xs - v) / bw
        density += np.exp(-0.5 * u * u)
    ys = norm * density
    return xs, ys


def hist_kwargs(values, bins_hint=10):
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return {"bins": 1}
    lo = float(arr.min())
    hi = float(arr.max())
    if abs(hi - lo) < 1e-12:
        eps = max(1e-6, abs(lo) * 1e-6)
        return {"bins": [lo - eps, hi + eps]}
    eps = max(1e-9, (hi - lo) * 1e-6)
    bins = min(20, max(4, int(math.sqrt(arr.size)), bins_hint // 2))
    return {"bins": bins, "range": (lo - eps, hi + eps)}


def apply_style():
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": False,
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 9,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


def main():
    apply_style()
    raw_rows = read_csv(RAW_DATASET)
    ml_rows = read_csv(ML_DATASET)
    scenario_rows = read_csv(METRICS_SCENARIO)

    generated = []
    validation_notes = []
    points_used = {}

    # Use only real valid rows for latency-based figures.
    valid_latency = []
    for r in raw_rows:
        lat = fnum(r.get("e2e_latency_ms"))
        scenario = (r.get("scenario") or "").strip()
        if scenario and lat is not None and lat > 0:
            valid_latency.append((scenario, lat, r))

    # Figure 14: CDF latency by scenario
    fig, ax = plt.subplots(figsize=(8, 4.8))
    scenario_order = ["scenario_1", "scenario_10", "scenario_50"]
    scenario_points = 0
    for sc, color in zip(scenario_order, [COLORS["latency_blue"], "#4c9ed9", "#9bc8ea"]):
        vals = [lat for s, lat, _ in valid_latency if s == sc]
        if vals:
            xs, ys = cdf(vals)
            ax.plot(xs, ys, linewidth=2.0, label=sc, color=color)
            scenario_points += len(vals)
        else:
            validation_notes.append(f"No valid latency points for {sc} in CDF.")
    ax.set_title("Figure 14 - Latency CDF by Scenario")
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("CDF")
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False)
    generated.append(save_figure(fig, "figura_14_cdf_latency.png"))
    points_used["figura_14_cdf_latency"] = scenario_points

    # Figure 15: Boxplot latency by scenario
    fig, ax = plt.subplots(figsize=(8, 4.8))
    data = [[lat for s, lat, _ in valid_latency if s == sc] for sc in scenario_order]
    non_empty = [d for d in data if len(d) > 0]
    if non_empty:
        ax.boxplot(
            data,
            tick_labels=scenario_order,
            patch_artist=True,
            boxprops={"facecolor": "#d7e9f7", "edgecolor": COLORS["latency_blue"]},
            medianprops={"color": "#003b6f", "linewidth": 2},
            whiskerprops={"color": COLORS["latency_blue"]},
            capprops={"color": COLORS["latency_blue"]},
            flierprops={"marker": "o", "markersize": 3, "markerfacecolor": "#666666", "markeredgecolor": "#666666"},
        )
    else:
        validation_notes.append("No valid latency points for boxplot.")
    ax.set_title("Figure 15 - Latency Distribution (Boxplot)")
    ax.set_xlabel("Scenario")
    ax.set_ylabel("Latency (ms)")
    generated.append(save_figure(fig, "figura_15_boxplot_latency.png"))
    points_used["figura_15_boxplot_latency"] = sum(len(d) for d in data)

    # Figure 16: ML distribution (hist + KDE) by observed scientific decisions
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ml_valid = []
    for r in ml_rows:
        dec = (r.get("decision") or "").strip().upper()
        score = fnum(r.get("ml_risk_score"))
        if dec in {"ACCEPT", "RENEGOTIATE", "REJECT"} and score is not None:
            ml_valid.append((dec, score))
    palette = {
        "ACCEPT": COLORS["accept_green"],
        "RENEGOTIATE": COLORS["reneg_orange"],
        "REJECT": COLORS.get("reject_red", "#d62728"),
    }
    for dec in [d for d in ["ACCEPT", "RENEGOTIATE", "REJECT"] if any(x[0] == d for x in ml_valid)]:
        color = palette[dec]
        vals = [v for d, v in ml_valid if d == dec]
        if vals:
            bins = min(20, max(5, int(math.sqrt(len(vals)))))
            ax.hist(
                vals,
                density=True,
                alpha=0.28,
                color=color,
                label=f"{dec} hist",
                edgecolor=color,
                linewidth=0.7,
                **hist_kwargs(vals, bins),
            )
            xs, ys = kde_curve(vals)
            if xs is not None:
                ax.plot(xs, ys, color=color, linewidth=2.0, label=f"{dec} kde")
            else:
                validation_notes.append(f"KDE unavailable for {dec} due to low variance.")
        else:
            validation_notes.append(f"No ML points for decision={dec}.")
    ax.set_title("Figure 16 - ML Risk Distribution by Decision")
    ax.set_xlabel("ML Risk Score")
    ax.set_ylabel("Density")
    ax.legend(frameon=False, ncol=2)
    generated.append(save_figure(fig, "figura_16_ml_distribution.png"))
    points_used["figura_16_ml_distribution"] = len(ml_valid)

    # Figure 17: ML vs decision scatter with jitter
    fig, ax = plt.subplots(figsize=(8, 4.8))
    dec_map = {"REJECT": 0, "RENEGOTIATE": 1, "ACCEPT": 2}
    xs, ys = [], []
    for r in ml_rows:
        dec = (r.get("decision") or "").strip().upper()
        score = fnum(r.get("ml_risk_score"))
        if dec in dec_map and score is not None:
            xs.append(score)
            jitter = np.random.uniform(-0.08, 0.08)
            ys.append(dec_map[dec] + jitter)
    if xs:
        ax.scatter(xs, ys, s=18, alpha=0.7, c=COLORS["latency_blue"], edgecolors="none")
    else:
        validation_notes.append("No points for ML vs decision scatter.")
    ax.set_title("Figure 17 - ML Risk vs Decision (All Points)")
    ax.set_xlabel("ML Risk Score")
    ax.set_ylabel("Decision Code")
    ax.set_yticks([0, 1, 2], ["REJECT", "RENEGOTIATE", "ACCEPT"])
    generated.append(save_figure(fig, "figura_17_ml_vs_decision_scatter.png"))
    points_used["figura_17_ml_vs_decision_scatter"] = len(xs)

    # Figure 18: Throughput vs latency (scenario load vs mean latency)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    loads, mean_latency = [], []
    for r in scenario_rows:
        sc = r.get("scenario", "")
        load = 1 if sc == "scenario_1" else 10 if sc == "scenario_10" else 50 if sc == "scenario_50" else None
        mlat = fnum(r.get("mean_latency"))
        if load is not None and mlat is not None:
            loads.append(load)
            mean_latency.append(mlat)
    if loads:
        pairs = sorted(zip(loads, mean_latency), key=lambda x: x[0])
        loads, mean_latency = zip(*pairs)
        ax.plot(loads, mean_latency, marker="o", linewidth=2, color=COLORS["latency_blue"])
    else:
        validation_notes.append("No valid points in metrics_by_scenario_v2.csv for Figure 18.")
    ax.set_title("Figure 18 - Load vs Mean Latency")
    ax.set_xlabel("Load (Number of SLA Requests)")
    ax.set_ylabel("Mean Latency (ms)")
    generated.append(save_figure(fig, "figura_18_throughput_latency.png"))
    points_used["figura_18_throughput_latency"] = len(loads)

    # Figure 19: Module latency distribution
    fig, ax = plt.subplots(figsize=(8, 4.8))
    sem = [fnum(r.get("semantic_latency_ms")) for _, _, r in valid_latency if fnum(r.get("semantic_latency_ms")) is not None]
    dec = [fnum(r.get("decision_latency_ms")) for _, _, r in valid_latency if fnum(r.get("decision_latency_ms")) is not None]
    ml = [fnum(r.get("ml_prediction_latency_ms")) for _, _, r in valid_latency if fnum(r.get("ml_prediction_latency_ms")) is not None]
    labels, data = [], []
    if sem:
        labels.append("semantic_latency_ms")
        data.append(sem)
    else:
        validation_notes.append("Field semantic_latency_ms missing/empty for Figure 19.")
    if ml:
        labels.append("ml_latency_ms")
        data.append(ml)
    else:
        validation_notes.append("Field ml_latency_ms missing; used alias ml_prediction_latency_ms if available.")
    if dec:
        labels.append("decision_latency_ms")
        data.append(dec)
    else:
        validation_notes.append("Field decision_latency_ms missing/empty for Figure 19.")
    if data:
        ax.boxplot(
            data,
            tick_labels=labels,
            patch_artist=True,
            boxprops={"facecolor": "#eaf3fb", "edgecolor": COLORS["latency_blue"]},
            medianprops={"color": "#003b6f", "linewidth": 2},
            whiskerprops={"color": COLORS["latency_blue"]},
            capprops={"color": COLORS["latency_blue"]},
            flierprops={"marker": "o", "markersize": 3, "markerfacecolor": "#666666", "markeredgecolor": "#666666"},
        )
    ax.set_title("Figure 19 - Module Latency Distribution")
    ax.set_ylabel("Latency (ms)")
    generated.append(save_figure(fig, "figura_19_module_latency_distribution.png"))
    points_used["figura_19_module_latency_distribution"] = sum(len(d) for d in data)

    report = {
        "run_dir": str(RUN_DIR),
        "output_dir": str(FIG_DIR),
        "generated_figures": generated,
        "real_data_sources": [
            str(RAW_DATASET),
            str(ML_DATASET),
            str(METRICS_SCENARIO),
        ],
        "points_used_by_figure": points_used,
        "notes": validation_notes,
        "status": "VALID",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (FIG_DIR / "figures_validation_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(FIG_DIR))


if __name__ == "__main__":
    main()
