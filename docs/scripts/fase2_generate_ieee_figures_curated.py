#!/usr/bin/env python3
"""PROMPT_230 — figuras IEEE curadas (base + opcional contraste); sem fig08/10/11."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for cand in (p.parents[2], p.parents[1]):
        if (cand / "evidencias_resultados_trisla_baseline_v8").is_dir():
            return cand
    return p.parents[2]


ROOT = _repo_root()
SSOT = ROOT / "evidencias_resultados_trisla_baseline_v8"
BASE = SSOT / "dataset" / "fase2" / "dataset_fase2_enriched.csv"
CONTRAST = SSOT / "dataset" / "fase2_contrast" / "dataset_fase2_contrast_enriched.csv"
FIGDIR = SSOT / "figures" / "fase2_ieee"


def col(df: pd.DataFrame, cands: list[str]) -> str | None:
    for c in cands:
        if c in df.columns:
            return c
    return None


def _ieee_rc() -> None:
    plt.rcParams.update(
        {
            "figure.figsize": (7.0, 4.0),
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "font.family": "serif",
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )


def _boxplot(data: list[np.ndarray], labels: list[str]) -> None:
    try:
        plt.boxplot(data, tick_labels=labels, patch_artist=True)
    except TypeError:
        plt.boxplot(data, labels=labels, patch_artist=True)


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGDIR / name, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    _ieee_rc()
    if not BASE.is_file():
        print(f"[FAIL] Falta dataset base: {BASE}", file=sys.stderr)
        return 1

    df1 = pd.read_csv(BASE)
    df1["dataset_origin"] = "base"
    frames: list[pd.DataFrame] = [df1]
    if CONTRAST.is_file():
        df2 = pd.read_csv(CONTRAST)
        df2["dataset_origin"] = "contrast"
        frames.append(df2)
    df = pd.concat(frames, ignore_index=True)

    decision = col(df, ["decision_trisla", "decision", "final_decision"])
    prb = col(df, ["prb_utilization_real", "ran_prb_utilization", "prb_utilization"])
    rtt = col(df, ["telemetry_transport_rtt_ms", "transport_rtt_ms", "rtt_ms"])
    jitter = col(df, ["transport_jitter_ms", "jitter_ms"])
    loss = col(df, ["transport_packet_loss", "transport_packet_loss_pct", "packet_loss_pct", "packet_loss"])
    core = col(df, ["core_cpu", "core_cpu_utilization", "core_cpu_pct", "cpu_utilization_core"])

    if decision is None:
        print("[FAIL] Coluna de decisão ausente.", file=sys.stderr)
        return 1

    FIGDIR.mkdir(parents=True, exist_ok=True)

    for weak in (
        "fig08_score_by_decision.png",
        "fig10_multislice_summary.png",
        "fig11_scenario_vs_decision.png",
        "fig11_scenario_by_decision.png",
        "fig06_cdf_e2e_latency.png",
        "fig07_prb_vs_latency_by_decision.png",
    ):
        p = FIGDIR / weak
        if p.is_file():
            p.unlink()

    order = sorted(df[decision].dropna().astype(str).unique())

    plt.figure(figsize=(7, 4))
    df[decision].astype(str).value_counts().sort_values(ascending=False).plot(
        kind="bar", color="steelblue", edgecolor="black"
    )
    plt.xlabel("Decisão")
    plt.ylabel("Contagem")
    plt.title("Distribuição das decisões do TriSLA (base + contraste)")
    save("fig01_decision_distribution.png")

    if prb:
        plt.figure(figsize=(7, 4))
        data = [df.loc[df[decision].astype(str) == d, prb].dropna().astype(float).values for d in order]
        _boxplot(data, order)
        plt.xlabel("Decisão")
        plt.ylabel("PRB utilization")
        plt.title("PRB por decisão")
        save("fig02_prb_by_decision.png")

    if jitter:
        plt.figure(figsize=(7, 4))
        data = [df.loc[df[decision].astype(str) == d, jitter].dropna().astype(float).values for d in order]
        _boxplot(data, order)
        plt.xlabel("Decisão")
        plt.ylabel("Jitter (ms)")
        plt.title("Jitter de transporte por decisão")
        save("fig03_jitter_by_decision.png")

    if loss:
        plt.figure(figsize=(7, 4))
        data = [df.loc[df[decision].astype(str) == d, loss].dropna().astype(float).values for d in order]
        _boxplot(data, order)
        plt.xlabel("Decisão")
        ylab = "Packet loss" + (" (%)" if "pct" in loss.lower() else "")
        plt.ylabel(ylab)
        plt.title("Perda de pacotes por decisão")
        save("fig04_loss_by_decision.png")

    if core:
        plt.figure(figsize=(7, 4))
        data = [df.loc[df[decision].astype(str) == d, core].dropna().astype(float).values for d in order]
        _boxplot(data, order)
        plt.xlabel("Decisão")
        plt.ylabel("Core CPU")
        plt.title("CPU (core) por decisão")
        save("fig05_core_cpu_by_decision.png")

    if rtt:
        vals = np.sort(pd.to_numeric(df[rtt], errors="coerce").dropna().values)
        if len(vals) > 0:
            y = np.arange(1, len(vals) + 1) / len(vals)
            plt.figure(figsize=(7, 4))
            plt.plot(vals, y, color="darkgreen", linewidth=1.5)
            plt.xlabel("RTT transporte (ms)")
            plt.ylabel("CDF")
            plt.title("CDF do RTT de transporte")
            plt.ylim(0, 1.05)
            save("fig06_cdf_transport_rtt.png")

    if prb and rtt:
        plt.figure(figsize=(7, 4))
        for d in order:
            sub = df[df[decision].astype(str) == d]
            x = pd.to_numeric(sub[prb], errors="coerce")
            yv = pd.to_numeric(sub[rtt], errors="coerce")
            m = x.notna() & yv.notna()
            plt.scatter(x[m], yv[m], label=str(d), alpha=0.65, s=22)
        plt.xlabel("PRB utilization")
        plt.ylabel("RTT transporte (ms)")
        plt.title("PRB vs RTT por decisão")
        plt.legend(title="Decisão", fontsize=8)
        save("fig07_prb_vs_rtt_by_decision.png")

    key_num = [
        c
        for c in [
            prb,
            rtt,
            jitter,
            loss,
            core,
            "score_trisla",
            "telemetry_ran_prb",
            "telemetry_core_cpu",
        ]
        if c and c in df.columns
    ]
    if len(key_num) >= 2:
        subm = df[key_num].apply(pd.to_numeric, errors="coerce")
        corr = subm.corr(numeric_only=True, min_periods=2)
        plt.figure(figsize=(8, 6.5))
        im = plt.imshow(corr.values, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
        plt.xticks(range(len(corr.columns)), corr.columns, rotation=85, ha="right")
        plt.yticks(range(len(corr.columns)), corr.columns)
        plt.colorbar(im, fraction=0.046, pad=0.04)
        plt.title("Correlação entre métricas multi-domínio")
        save("fig09_numeric_correlation_matrix.png")

    print("[OK] Curadoria forte concluída.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
