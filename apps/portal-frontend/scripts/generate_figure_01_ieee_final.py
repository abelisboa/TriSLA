#!/usr/bin/env python3
"""
FIGURA 01 — Module Latency Summary (IEEE final).
Loads raw/raw_dataset_v2.csv from TRISLA_RUN_PATH (default: run_20260320_220653).
Does not generate other figures.
"""
from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

RUN_DEFAULT = Path(__file__).resolve().parents[3] / "evidencias_resultados_article_trisla_v2" / "run_20260320_220653"

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception as exc:
    raise SystemExit(f"matplotlib required: {exc}")


def load_modules(raw_path: Path) -> dict[str, list[float]]:
    vals: dict[str, list[float]] = {
        "semantic": [],
        "ml": [],
        "decision": [],
        "nasp": [],
        "blockchain": [],
    }
    with raw_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mapping = {
                "semantic": row.get("semantic_latency_ms") or row.get("semantic_parsing_latency_ms"),
                "ml": row.get("ml_latency_ms") or row.get("ml_prediction_latency_ms"),
                "decision": row.get("decision_latency_ms") or row.get("decision_duration_ms"),
                "nasp": row.get("nasp_latency_ms"),
                "blockchain": row.get("blockchain_latency_ms") or row.get("blockchain_transaction_latency_ms"),
            }
            for key, value in mapping.items():
                try:
                    v = float(value)
                except (ValueError, TypeError):
                    continue
                if v > 0:
                    vals[key].append(v)
    return vals


def validate(modules: dict[str, list[float]]) -> None:
    included = [k for k, v in modules.items() if v]
    if not included:
        raise SystemExit("VALIDATION NOK: empty series")
    for name, vals in modules.items():
        if not vals:
            continue
        if any(math.isnan(x) or math.isinf(x) for x in vals):
            raise SystemExit(f"VALIDATION NOK: {name} has NaN/Inf")
        if any(x <= 0 for x in vals):
            raise SystemExit(f"VALIDATION NOK: {name} has non-positive")
        if len(vals) > 1 and statistics.variance(vals) <= 0:
            raise SystemExit(f"VALIDATION NOK: {name} variance not > 0")


def main() -> int:
    run_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(
        __import__("os").environ.get("TRISLA_RUN_PATH", str(RUN_DEFAULT))
    )
    raw_path = run_path / "raw" / "raw_dataset_v2.csv"
    if not raw_path.is_file():
        raise SystemExit(f"VALIDATION NOK: missing {raw_path}")

    with raw_path.open(encoding="utf-8") as f:
        header = next(csv.reader(f))
    modules = load_modules(raw_path)
    validate(modules)
    labels = [k for k in ["semantic", "ml", "decision", "nasp", "blockchain"] if modules[k]]
    means = [statistics.mean(modules[k]) for k in labels]

    out_dir = run_path / "figures_ieee_final"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "figure_01_module_latency_summary.png"

    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.linestyle": "--",
            "grid.alpha": 0.35,
            "font.family": "sans-serif",
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
        }
    )

    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    colors = ["#4C72B0", "#72B7B2", "#DD8452", "#937860", "#DA8BC3"][: len(labels)]
    bars = ax.bar(labels, means, color=colors, width=0.55, edgecolor="#333333", linewidth=0.6)
    ax.set_ylabel("Mean latency (ms)")
    ax.set_title("Module latency summary (mean)")
    apply_axes_tuning(ax)
    for b, m in zip(bars, means):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height(),
            f"{m:.1f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    fig.tight_layout()
    fig.savefig(out_png, dpi=400, facecolor="white")
    plt.close(fig)

    print(f"OK: {out_png}")
    missing = [k for k in ["semantic", "ml", "decision", "nasp", "blockchain"] if not modules[k]]
    print(f"included_modules={labels}")
    print(f"missing_modules={missing}")
    print(f"means_by_module_ms={dict(zip(labels, means))}")
    print(f"n_rows_used={max(len(modules[k]) for k in labels)}")
    return 0


def apply_axes_tuning(ax):
    for spine in ax.spines.values():
        spine.set_alpha(0.35)


if __name__ == "__main__":
    raise SystemExit(main())
