#!/usr/bin/env python3
"""Figuras científicas (estilo IEEE/dissertação) a partir do dataset Fase 2 validado — PROMPT_229."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for cand in (p.parents[1], p.parents[2]):
        if (cand / "evidencias_resultados_trisla_baseline_v8").is_dir():
            return cand
    return p.parents[1]


ROOT = _repo_root()
SSOT = ROOT / "evidencias_resultados_trisla_baseline_v8"
DATASET = SSOT / "dataset" / "fase2" / "dataset_fase2_enriched.csv"
ANALYSIS = SSOT / "analysis" / "fase2"
FIGDIR = SSOT / "figures" / "fase2_ieee"


def _ieee_rc() -> None:
    plt.rcParams.update(
        {
            "figure.figsize": (7.0, 4.0),
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "legend.fontsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "font.family": "serif",
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )


def pick(df: pd.DataFrame, cols: list[str]) -> str | None:
    for c in cols:
        if c in df.columns:
            return c
    return None


def _boxplot_groups(data: list[pd.Series], labels: list[str]) -> None:
    clean = [d.dropna().values for d in data]
    try:
        plt.boxplot(clean, tick_labels=labels, patch_artist=True)
    except TypeError:
        plt.boxplot(clean, labels=labels, patch_artist=True)


def savefig(name: str) -> None:
    out = FIGDIR / name
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


def main() -> int:
    _ieee_rc()
    if not DATASET.is_file():
        print(f"[FAIL] Dataset em falta: {DATASET}", file=sys.stderr)
        return 1

    df = pd.read_csv(DATASET)
    FIGDIR.mkdir(parents=True, exist_ok=True)

    decision_col = pick(df, ["decision_trisla", "decision", "final_decision"])
    prb_col = pick(df, ["prb_utilization_real", "ran_prb_utilization", "prb_utilization"])
    lat_col = pick(
        df,
        [
            "e2e_latency_ms",
            "latency_ms",
            "total_latency_ms",
            "telemetry_transport_rtt_ms",
        ],
    )
    lat_ylabel = (
        "Latência E2E (ms)"
        if lat_col and lat_col in ("e2e_latency_ms", "latency_ms", "total_latency_ms")
        else "RTT transporte (ms)"
    )
    jitter_col = pick(df, ["transport_jitter_ms", "jitter_ms"])
    loss_col = pick(
        df,
        [
            "transport_packet_loss",
            "transport_packet_loss_pct",
            "packet_loss_pct",
            "packet_loss",
        ],
    )
    core_cpu_col = pick(df, ["core_cpu", "core_cpu_utilization", "core_cpu_pct", "cpu_utilization_core"])
    risk_col = pick(df, ["score_trisla", "decision_score", "risk_score", "ml_risk_score"])

    if decision_col is None:
        print("[FAIL] Coluna de decisão não encontrada no dataset.", file=sys.stderr)
        return 1

    # Figura 1 — distribuição de decisões
    plt.figure(figsize=(7, 4))
    df[decision_col].value_counts(dropna=False).sort_values(ascending=False).plot(
        kind="bar", color="steelblue", edgecolor="black"
    )
    plt.xlabel("Decisão")
    plt.ylabel("Contagem")
    plt.title("Distribuição das decisões do TriSLA (Fase 2)")
    plt.xticks(rotation=0)
    savefig("fig01_decision_distribution.png")

    # Figura 2 — PRB por decisão
    if prb_col:
        plt.figure(figsize=(7, 4))
        order = sorted(df[decision_col].dropna().astype(str).unique())
        data = [df.loc[df[decision_col].astype(str) == d, prb_col] for d in order]
        _boxplot_groups(data, order)
        plt.xlabel("Decisão")
        plt.ylabel("PRB utilization (proxy / normalizado)")
        plt.title("PRB observado por decisão")
        savefig("fig02_prb_by_decision.png")

    # Figura 3 — jitter por decisão
    if jitter_col:
        plt.figure(figsize=(7, 4))
        order = sorted(df[decision_col].dropna().astype(str).unique())
        data = [df.loc[df[decision_col].astype(str) == d, jitter_col] for d in order]
        _boxplot_groups(data, order)
        plt.xlabel("Decisão")
        plt.ylabel("Jitter (ms)")
        plt.title("Jitter de transporte por decisão")
        savefig("fig03_jitter_by_decision.png")

    # Figura 4 — perda por decisão
    if loss_col:
        plt.figure(figsize=(7, 4))
        order = sorted(df[decision_col].dropna().astype(str).unique())
        data = [df.loc[df[decision_col].astype(str) == d, loss_col] for d in order]
        _boxplot_groups(data, order)
        plt.xlabel("Decisão")
        ylab = "Packet loss" + (" (%)" if "pct" in loss_col.lower() else "")
        plt.ylabel(ylab)
        plt.title("Perda de pacotes (transporte) por decisão")
        savefig("fig04_loss_by_decision.png")

    # Figura 5 — core cpu por decisão
    if core_cpu_col:
        plt.figure(figsize=(7, 4))
        order = sorted(df[decision_col].dropna().astype(str).unique())
        data = [df.loc[df[decision_col].astype(str) == d, core_cpu_col] for d in order]
        _boxplot_groups(data, order)
        plt.xlabel("Decisão")
        plt.ylabel("Core CPU (fração / utilização)")
        plt.title("Utilização de CPU (core) por decisão")
        savefig("fig05_core_cpu_by_decision.png")

    # Figura 6 — CDF de latência / RTT
    if lat_col:
        vals = np.sort(pd.to_numeric(df[lat_col], errors="coerce").dropna().values)
        if len(vals) > 0:
            y = np.arange(1, len(vals) + 1) / len(vals)
            plt.figure(figsize=(7, 4))
            plt.plot(vals, y, color="darkgreen", linewidth=1.5)
            plt.xlabel(lat_ylabel)
            plt.ylabel("CDF")
            plt.title("CDF — " + ("latência E2E" if "E2E" in lat_ylabel else "RTT transporte"))
            plt.ylim(0, 1.05)
            savefig("fig06_cdf_e2e_latency.png")

    # Figura 7 — scatter PRB vs latência, por decisão
    if prb_col and lat_col:
        plt.figure(figsize=(7, 4))
        for dec in sorted(df[decision_col].dropna().astype(str).unique()):
            sub = df[df[decision_col].astype(str) == dec]
            x = pd.to_numeric(sub[prb_col], errors="coerce")
            yv = pd.to_numeric(sub[lat_col], errors="coerce")
            m = x.notna() & yv.notna()
            plt.scatter(x[m], yv[m], label=str(dec), alpha=0.65, s=22)
        plt.xlabel("PRB utilization")
        plt.ylabel(lat_ylabel)
        plt.title("PRB vs " + ("latência" if "E2E" in lat_ylabel else "RTT") + " por decisão")
        plt.legend(title="Decisão", fontsize=8)
        savefig("fig07_prb_vs_latency_by_decision.png")

    # Figura 8 — score por decisão
    if risk_col:
        plt.figure(figsize=(7, 4))
        order = sorted(df[decision_col].dropna().astype(str).unique())
        data = [df.loc[df[decision_col].astype(str) == d, risk_col] for d in order]
        _boxplot_groups(data, order)
        plt.xlabel("Decisão")
        plt.ylabel(risk_col.replace("_", " "))
        plt.title("Score de decisão por classe decisória")
        savefig("fig08_score_by_decision.png")

    # Figura 9 — correlação numérica (subset interpretável)
    key_num = [
        c
        for c in [
            "prb_utilization_real",
            "score_trisla",
            "telemetry_ran_prb",
            "telemetry_transport_rtt_ms",
            "telemetry_core_cpu",
            "transport_jitter_ms",
            "transport_packet_loss",
            "ran_prb",
            "core_cpu",
            "target_bps",
        ]
        if c in df.columns
    ]
    num_df = df[key_num].apply(pd.to_numeric, errors="coerce") if key_num else df.select_dtypes(include=[np.number])
    if num_df.shape[1] >= 2:
        corr = num_df.corr(numeric_only=True, min_periods=2)
        plt.figure(figsize=(9, 7))
        im = plt.imshow(corr.values, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
        plt.xticks(range(len(corr.columns)), corr.columns, rotation=85, ha="right")
        plt.yticks(range(len(corr.columns)), corr.columns)
        plt.colorbar(im, fraction=0.046, pad=0.04)
        plt.title("Correlação — métricas numéricas chave (Fase 2)")
        savefig("fig09_numeric_correlation_matrix.png")

    # Figura 10 — multislice (dados reais do relatório JSON)
    ms_file = ANALYSIS / "multislice_scale_report.json"
    if ms_file.is_file():
        ms = json.loads(ms_file.read_text(encoding="utf-8"))
        outcomes = ms.get("outcomes") or {}
        if isinstance(outcomes, dict) and outcomes:
            plt.figure(figsize=(7, 4))
            keys = list(outcomes.keys())
            vals = [float(outcomes[k]) for k in keys]
            plt.bar(keys, vals, color="coral", edgecolor="black")
            plt.ylabel("Pedidos")
            plt.xlabel("Resultado")
            tr = ms.get("total_requests")
            el = ms.get("elapsed_s")
            plt.title(
                "Teste de escala multislice — outcomes"
                + (f" (N={tr}, {el}s)" if tr is not None and el is not None else "")
            )
            plt.xticks(rotation=25, ha="right")
            savefig("fig10_multislice_summary.png")

    # Figura 11 — cenário Fase 2 vs decisão (quando existir)
    scen_col = pick(df, ["fase2_scenario", "scenario"])
    if scen_col:
        ct = pd.crosstab(df[scen_col].astype(str), df[decision_col].astype(str))
        plt.figure(figsize=(8, 4.5))
        ct.plot(kind="bar", ax=plt.gca(), width=0.85, edgecolor="black", linewidth=0.3)
        plt.xlabel("Cenário Fase 2")
        plt.ylabel("Contagem")
        plt.title("Decisão por cenário experimental")
        plt.legend(title="Decisão", bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.xticks(rotation=20, ha="right")
        savefig("fig11_scenario_vs_decision.png")

    n_png = len(list(FIGDIR.glob("*.png")))
    if n_png < 8:
        print(f"[WARN] Apenas {n_png} figuras em {FIGDIR} (mínimo sugerido: 8).", file=sys.stderr)
    print(f"[OK] Figuras IEEE Fase 2 geradas ({n_png} PNG) em {FIGDIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
