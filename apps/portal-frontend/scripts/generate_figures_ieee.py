#!/usr/bin/env python3
import csv
import json
import math
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
MET_SCENARIO_PATH = RUN_DIR / "processed" / "metrics_by_scenario_v2.csv"
OUT_DIR = RUN_DIR / "figures_ieee"

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

FIGURE_FILES = [
    "figure_01_module_latency_summary.png",
    "figure_02_e2e_latency_by_scenario.png",
    "figure_03_decision_distribution_by_scenario.png",
    "figure_04_global_decision_distribution.png",
    "figure_05_ml_risk_distribution_by_decision.png",
    "figure_06_e2e_latency_by_slice.png",
    "figure_07_scalability_overview.png",
    "figure_08_sequential_pipeline_latency.png",
    "figure_09_ml_risk_vs_decision.png",
    "figure_10_admission_behavior_by_scenario.png",
    "figure_11_semantic_cost_by_slice.png",
    "figure_12_selectivity_under_stress.png",
    "figure_13_module_latency_distribution.png",
    "figure_14_latency_cdf_by_scenario.png",
    "figure_15_latency_dispersion_by_scenario.png",
]

USED_COLORS = set()


def apply_ieee_style():
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


def color(name):
    USED_COLORS.add(name)
    return COLORS[name]


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


def load_data():
    raw = read_csv(RAW_PATH)
    ml = read_csv(ML_PATH)
    metrics_scenario = read_csv(MET_SCENARIO_PATH)

    valid = []
    for r in raw:
        scenario = (r.get("scenario") or "").strip()
        e2e = fnum(r.get("e2e_latency_ms"))
        sem = fnum(r.get("semantic_latency_ms")) or fnum(r.get("semantic_parsing_latency_ms"))
        dec = fnum(r.get("decision_latency_ms")) or fnum(r.get("decision_duration_ms"))
        ml_lat = fnum(r.get("ml_prediction_latency_ms"))
        if scenario and e2e is not None and e2e > 0:
            valid.append(
                {
                    "scenario": scenario,
                    "slice_type": (r.get("slice_type") or "").strip(),
                    "decision": (r.get("decision") or "").strip().upper(),
                    "e2e": e2e,
                    "semantic": sem,
                    "decision_latency": dec,
                    "ml_latency": ml_lat,
                    "ml_risk_score": fnum(r.get("ml_risk_score")),
                    "nasp_latency_ms": fnum(r.get("nasp_latency_ms")),
                    "blockchain_latency_ms": fnum(r.get("blockchain_latency_ms")) or fnum(r.get("blockchain_transaction_latency_ms")),
                }
            )

    ml_valid = []
    for r in ml:
        decision = (r.get("decision") or "").strip().upper()
        score = fnum(r.get("ml_risk_score"))
        if decision in {"ACCEPT", "REJECT", "RENEGOTIATE"} and score is not None:
            ml_valid.append({"decision": decision, "ml_risk_score": score})

    return valid, ml_valid, metrics_scenario


def apply_axes_tuning(ax):
    for spine in ax.spines.values():
        spine.set_alpha(0.3)


def save_figure(fig, filename):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / filename
    fig.tight_layout()
    fig.savefig(out, dpi=400, facecolor="white")
    plt.close(fig)
    return out


def percentile(vals, p):
    arr = np.array(vals, dtype=float)
    return float(np.percentile(arr, p))


def kde(vals, points=200):
    arr = np.array(vals, dtype=float)
    if arr.size < 2:
        return None, None
    std = float(np.std(arr, ddof=1))
    if std <= 0:
        return None, None
    bw = 1.06 * std * (arr.size ** (-1 / 5))
    if bw <= 0:
        return None, None
    lo, hi = float(np.min(arr)), float(np.max(arr))
    pad = (hi - lo) * 0.1 if hi > lo else 1e-6
    xs = np.linspace(lo - pad, hi + pad, points)
    ys = np.zeros_like(xs)
    norm = 1 / (math.sqrt(2 * math.pi) * bw * arr.size)
    for v in arr:
        u = (xs - v) / bw
        ys += np.exp(-0.5 * u * u)
    ys = norm * ys
    return xs, ys


def plot_figure_01(valid):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    sem = [r["semantic"] for r in valid if isinstance(r["semantic"], (int, float))]
    ml = [r["ml_latency"] for r in valid if isinstance(r["ml_latency"], (int, float))]
    dec = [r["decision_latency"] for r in valid if isinstance(r["decision_latency"], (int, float))]
    nasp = [fnum(r.get("nasp_latency_ms")) for r in valid if fnum(r.get("nasp_latency_ms")) is not None]
    bc = [fnum(r.get("blockchain_latency_ms")) for r in valid if fnum(r.get("blockchain_latency_ms")) is not None]
    modules = [("semantic", sem), ("ml", ml), ("decision", dec), ("nasp", nasp), ("blockchain", bc)]
    labels = [m for m, vals in modules if vals]
    means = [np.mean(vals) for _, vals in modules if vals]
    stds = [np.std(vals) if len(vals) > 1 else 0 for _, vals in modules if vals]
    palette = {
        "semantic": color("semantic"),
        "ml": color("ml"),
        "decision": color("decision"),
        "nasp": "#937860",
        "blockchain": "#DA8BC3",
    }
    ax.bar(labels, means, yerr=stds, capsize=4, alpha=0.85, linewidth=2, color=[palette[l] for l in labels])
    ax.set_title("Figure 1 - Module Latency Summary")
    ax.set_ylabel("Latency (ms)")
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[0])


def plot_figure_02(valid):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    order = ["scenario_1", "scenario_10", "scenario_50"]
    loads = [1, 10, 50]
    mean, p95, p99 = [], [], []
    for s in order:
        vals = [r["e2e"] for r in valid if r["scenario"] == s]
        mean.append(float(np.mean(vals)))
        p95.append(percentile(vals, 95))
        p99.append(percentile(vals, 99))
    ax.plot(loads, mean, marker="o", linewidth=2, alpha=0.85, color=color("mean"), label="mean")
    ax.plot(loads, p95, marker="s", linewidth=2, alpha=0.85, color=color("p95"), label="p95")
    ax.plot(loads, p99, marker="^", linewidth=2, alpha=0.85, color=color("p99"), label="p99")
    ax.set_title("Figure 2 - E2E Latency by Scenario")
    ax.set_xlabel("Load (SLA requests)")
    ax.set_ylabel("Latency (ms)")
    ax.legend()
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[1])


def plot_figure_03(valid):
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    order = ["scenario_1", "scenario_10", "scenario_50"]
    acc, rej, ren = [], [], []
    for s in order:
        rows = [r for r in valid if r["scenario"] == s]
        t = len(rows)
        acc.append(sum(1 for r in rows if r["decision"] == "ACCEPT") / t)
        rej.append(sum(1 for r in rows if r["decision"] == "REJECT") / t)
        ren.append(sum(1 for r in rows if r["decision"] == "RENEGOTIATE") / t)
    ax.bar(order, acc, alpha=0.85, linewidth=2, color=color("ACCEPT"), label="ACCEPT")
    ax.bar(order, rej, bottom=acc, alpha=0.85, linewidth=2, color=color("REJECT"), label="REJECT")
    ax.bar(order, ren, bottom=[a + r for a, r in zip(acc, rej)], alpha=0.85, linewidth=2, color=color("RENEGOTIATE"), label="RENEGOTIATE")
    ax.set_title("Figure 3 - Decision Distribution by Scenario")
    ax.set_ylabel("Proportion")
    ax.legend()
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[2])


def plot_figure_04(valid):
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    total = len(valid)
    vals = [
        sum(1 for r in valid if r["decision"] == "ACCEPT") / total,
        sum(1 for r in valid if r["decision"] == "REJECT") / total,
        sum(1 for r in valid if r["decision"] == "RENEGOTIATE") / total,
    ]
    ax.pie(vals, labels=["ACCEPT", "REJECT", "RENEGOTIATE"],
           colors=[color("ACCEPT"), color("REJECT"), color("RENEGOTIATE")], autopct="%1.1f%%")
    ax.set_title("Figure 4 - Global Decision Distribution")
    return save_figure(fig, FIGURE_FILES[3])


def plot_figure_05(ml_valid):
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    classes = [d for d in ["ACCEPT", "RENEGOTIATE", "REJECT"] if any(r["decision"] == d for r in ml_valid)]
    qualified = [d for d in classes if len([r for r in ml_valid if r["decision"] == d]) >= 5]
    if len(qualified) < 2:
        raise RuntimeError("Figure 5 requires >=2 decision classes with n>=5 each.")
    for dec in qualified:
        vals = [r["ml_risk_score"] for r in ml_valid if r["decision"] == dec]
        if not vals:
            continue
        bins = min(20, max(4, int(np.sqrt(len(vals)))))
        lo, hi = min(vals), max(vals)
        if abs(hi - lo) < 1e-12:
            eps = max(1e-6, abs(lo) * 1e-6)
            ax.hist(vals, bins=[lo - eps, hi + eps], alpha=0.5, color=color(dec), density=True, label=f"{dec} hist", linewidth=2)
        else:
            ax.hist(vals, bins=bins, alpha=0.5, color=color(dec), density=True, label=f"{dec} hist", linewidth=2)
        if np.std(vals, ddof=0) > 0:
            xs, ys = kde(vals)
            if xs is not None:
                ax.plot(xs, ys, linewidth=2, alpha=0.85, color=color(dec), label=f"{dec} kde")
    ax.set_title("Figure 5 - ML Risk Distribution by Decision")
    ax.set_xlabel("ML Risk Score")
    ax.set_ylabel("Density")
    ax.legend()
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[4])


def plot_figure_06(valid):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    order = ["URLLC", "eMBB", "mMTC"]
    data = [[r["e2e"] for r in valid if r["slice_type"] == s] for s in order]
    bp = ax.boxplot(data, tick_labels=order, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set(facecolor=color("semantic"), alpha=0.25, edgecolor=color("semantic"), linewidth=2)
    ax.set_title("Figure 6 - E2E Latency by Slice")
    ax.set_ylabel("Latency (ms)")
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[5])


def plot_figure_07(metrics_scenario):
    fig, ax1 = plt.subplots(figsize=(8.4, 4.8))
    loads, lat, acc = [], [], []
    for r in metrics_scenario:
        s = r.get("scenario")
        load = 1 if s == "scenario_1" else 10 if s == "scenario_10" else 50 if s == "scenario_50" else None
        if load is None:
            continue
        ml = fnum(r.get("mean_latency"))
        ar = fnum(r.get("accept_ratio"))
        if ml is None or ar is None:
            continue
        loads.append(load)
        lat.append(ml)
        acc.append(ar)
    pairs = sorted(zip(loads, lat, acc), key=lambda x: x[0])
    loads = [p[0] for p in pairs]
    lat = [p[1] for p in pairs]
    eff = [(p[2] * 1000.0 / p[1]) if p[1] > 0 else 0 for p in pairs]
    ax1.plot(loads, lat, marker="o", linewidth=2, alpha=0.85, color=color("semantic"), label="latency")
    ax1.set_xlabel("Load (SLA requests)")
    ax1.set_ylabel("Mean Latency (ms)", color=color("semantic"))
    ax2 = ax1.twinx()
    ax2.plot(loads, eff, marker="s", linewidth=2, alpha=0.85, color=color("ACCEPT"), label="efficiency")
    ax2.set_ylabel("Decision Efficiency (accept/ms)", color=color("ACCEPT"))
    ax1.set_title("Figure 7 - Scalability Overview")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="best")
    apply_axes_tuning(ax1)
    apply_axes_tuning(ax2)
    return save_figure(fig, FIGURE_FILES[6])


def plot_figure_08(valid):
    fig, ax = plt.subplots(figsize=(8.6, 3.2))
    sem = [r["semantic"] for r in valid if isinstance(r["semantic"], (int, float))]
    ml = [r["ml_latency"] for r in valid if isinstance(r["ml_latency"], (int, float))]
    dec = [r["decision_latency"] for r in valid if isinstance(r["decision_latency"], (int, float))]
    sem_m = float(np.mean(sem)) if sem else 0.0
    ml_m = float(np.mean(ml)) if ml else 0.0
    dec_m = float(np.mean(dec)) if dec else 0.0
    decision_component = max(dec_m - ml_m, 0.0)
    left = 0.0
    for val, lbl, c in [
        (sem_m, "semantic", color("semantic")),
        (ml_m, "ml", color("ml")),
        (decision_component, "decision", color("decision")),
    ]:
        ax.barh(["pipeline"], [val], left=left, linewidth=2, alpha=0.85, color=c, label=lbl)
        left += val
    ax.set_title("Figure 8 - Sequential Pipeline Latency")
    ax.set_xlabel("Latency (ms)")
    ax.legend(ncol=3, loc="upper center")
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[7])


def plot_figure_09(ml_valid):
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    mapping = {"REJECT": 0, "RENEGOTIATE": 1, "ACCEPT": 2}
    xs, ys, cs = [], [], []
    for r in ml_valid:
        d = r["decision"]
        xs.append(r["ml_risk_score"])
        ys.append(mapping[d] + np.random.uniform(-0.08, 0.08))
        cs.append(color(d))
    if len(set(round(x, 8) for x in xs)) < 5:
        order = ["REJECT", "RENEGOTIATE", "ACCEPT"]
        data = [[r["ml_risk_score"] for r in ml_valid if r["decision"] == d] for d in order]
        labels = [d for d, vals in zip(order, data) if vals]
        data = [vals for vals in data if vals]
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True)
        for patch, d in zip(bp["boxes"], labels):
            patch.set(facecolor=color(d), alpha=0.35, edgecolor=color(d), linewidth=2)
        ax.set_ylabel("ML Risk Score")
    else:
        ax.scatter(xs, ys, c=cs, s=20, alpha=0.8, linewidths=0)
        ax.set_yticks([0, 1, 2], ["REJECT", "RENEGOTIATE", "ACCEPT"])
        ax.set_ylabel("Decision")
    ax.set_xlabel("ML Risk Score")
    ax.set_title("Figure 9 - ML Risk vs Decision")
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[8])


def plot_figure_10(valid):
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    order = ["scenario_1", "scenario_10", "scenario_50"]
    acc, rej, ren = [], [], []
    for s in order:
        rows = [r for r in valid if r["scenario"] == s]
        t = len(rows)
        acc.append(sum(1 for r in rows if r["decision"] == "ACCEPT") / t)
        rej.append(sum(1 for r in rows if r["decision"] == "REJECT") / t)
        ren.append(sum(1 for r in rows if r["decision"] == "RENEGOTIATE") / t)
    ax.bar(order, acc, alpha=0.85, linewidth=2, color=color("ACCEPT"), label="ACCEPT")
    ax.bar(order, ren, bottom=acc, alpha=0.85, linewidth=2, color=color("RENEGOTIATE"), label="RENEGOTIATE")
    ax.bar(order, rej, bottom=[a + n for a, n in zip(acc, ren)], alpha=0.85, linewidth=2, color=color("REJECT"), label="REJECT")
    ax.set_title("Figure 10 - Admission Behavior by Scenario")
    ax.set_ylabel("Proportion")
    ax.legend()
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[9])


def plot_figure_11(valid):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    order = ["URLLC", "eMBB", "mMTC"]
    means, stds = [], []
    for s in order:
        vals = [r["semantic"] for r in valid if r["slice_type"] == s and isinstance(r["semantic"], (int, float))]
        means.append(float(np.mean(vals)) if vals else 0.0)
        stds.append(float(np.std(vals)) if len(vals) > 1 else 0.0)
    ax.bar(order, means, yerr=stds, capsize=4, alpha=0.85, linewidth=2, color=color("semantic"))
    ax.set_title("Figure 11 - Semantic Cost by Slice")
    ax.set_ylabel("Semantic Latency (ms)")
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[10])


def plot_figure_12(valid):
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    order = ["scenario_1", "scenario_10", "scenario_50"]
    loads = [1, 10, 50]
    acc, rej, ren = [], [], []
    for s in order:
        rows = [r for r in valid if r["scenario"] == s]
        t = len(rows)
        acc.append(100 * sum(1 for r in rows if r["decision"] == "ACCEPT") / t)
        rej.append(100 * sum(1 for r in rows if r["decision"] == "REJECT") / t)
        ren.append(100 * sum(1 for r in rows if r["decision"] == "RENEGOTIATE") / t)
    ax.plot(loads, acc, marker="o", linewidth=2, alpha=0.85, color=color("ACCEPT"), label="ACCEPT")
    ax.plot(loads, rej, marker="^", linewidth=2, alpha=0.85, color=color("REJECT"), label="REJECT")
    ax.plot(loads, ren, marker="s", linewidth=2, alpha=0.85, color=color("RENEGOTIATE"), label="RENEGOTIATE")
    ax.set_title("Figure 12 - Selectivity Under Stress")
    ax.set_xlabel("Load (SLA requests)")
    ax.set_ylabel("Decision Rate (%)")
    ax.legend()
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[11])


def plot_figure_13(valid):
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    sem = [r["semantic"] for r in valid if isinstance(r["semantic"], (int, float))]
    ml = [r["ml_latency"] for r in valid if isinstance(r["ml_latency"], (int, float))]
    dec = [r["decision_latency"] for r in valid if isinstance(r["decision_latency"], (int, float))]
    bp = ax.boxplot([sem, ml, dec], tick_labels=["semantic", "ml", "decision"], patch_artist=True)
    for patch, cname in zip(bp["boxes"], ["semantic", "ml", "decision"]):
        patch.set(facecolor=color(cname), alpha=0.35, edgecolor=color(cname), linewidth=2)
    ax.set_title("Figure 13 - Module Latency Distribution")
    ax.set_ylabel("Latency (ms)")
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[12])


def plot_figure_14(valid):
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    order = ["scenario_1", "scenario_10", "scenario_50"]
    for s, c in zip(order, [color("mean"), color("p95"), color("p99")]):
        vals = sorted([r["e2e"] for r in valid if r["scenario"] == s])
        x = np.array(vals, dtype=float)
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(x, y, linewidth=2, alpha=0.85, color=c, label=s)
    ax.set_title("Figure 14 - Latency CDF by Scenario")
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("CDF")
    ax.set_ylim(0, 1.02)
    ax.legend()
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[13])


def plot_figure_15(valid):
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    s1 = [r["e2e"] for r in valid if r["scenario"] == "scenario_1"]
    s10 = [r["e2e"] for r in valid if r["scenario"] == "scenario_10"]
    s50 = [r["e2e"] for r in valid if r["scenario"] == "scenario_50"]
    if len(s1) == 1:
        ax.scatter([1], s1, s=40, alpha=0.85, color=color("mean"), label="scenario_1 (single point)")
        bp = ax.boxplot([s10, s50], positions=[2, 3], widths=0.5, patch_artist=True)
        for patch in bp["boxes"]:
            patch.set(facecolor=color("semantic"), alpha=0.25, edgecolor=color("semantic"), linewidth=2)
        ax.set_xticks([1, 2, 3], ["scenario_1", "scenario_10", "scenario_50"])
        ax.legend()
    else:
        bp = ax.boxplot([s1, s10, s50], tick_labels=["scenario_1", "scenario_10", "scenario_50"], patch_artist=True)
        for patch in bp["boxes"]:
            patch.set(facecolor=color("semantic"), alpha=0.25, edgecolor=color("semantic"), linewidth=2)
    ax.set_title("Figure 15 - Latency Dispersion by Scenario")
    ax.set_ylabel("Latency (ms)")
    apply_axes_tuning(ax)
    return save_figure(fig, FIGURE_FILES[14])


def validate_output():
    missing = [name for name in FIGURE_FILES if not (OUT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"Missing figures: {missing}")
    if len(list(OUT_DIR.glob("figure_*.png"))) != 15:
        raise RuntimeError("Output validation failed: number of figure files is not 15.")
    for name in FIGURE_FILES:
        p = OUT_DIR / name
        if p.stat().st_size <= 0:
            raise RuntimeError(f"Empty figure file: {p}")

    required_color_keys = {"semantic", "ml", "decision", "ACCEPT", "REJECT", "RENEGOTIATE", "mean", "p95", "p99"}
    if not required_color_keys.issubset(USED_COLORS):
        missing_keys = sorted(required_color_keys - USED_COLORS)
        raise RuntimeError(f"Palette validation failed. Missing color usages: {missing_keys}")

    report = {
        "status": "approved",
        "figures_generated": 15,
        "style": "ieee",
        "palette_validated": True,
        "notes": "All figures regenerated with scientific visualization standards",
    }
    (OUT_DIR / "ieee_figures_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    apply_ieee_style()
    valid, ml_valid, metrics_scenario = load_data()
    plot_figure_01(valid)
    plot_figure_02(valid)
    plot_figure_03(valid)
    plot_figure_04(valid)
    plot_figure_05(ml_valid)
    plot_figure_06(valid)
    plot_figure_07(metrics_scenario)
    plot_figure_08(valid)
    plot_figure_09(ml_valid)
    plot_figure_10(valid)
    plot_figure_11(valid)
    plot_figure_12(valid)
    plot_figure_13(valid)
    plot_figure_14(valid)
    plot_figure_15(valid)
    validate_output()
    print(str(OUT_DIR))


if __name__ == "__main__":
    main()
