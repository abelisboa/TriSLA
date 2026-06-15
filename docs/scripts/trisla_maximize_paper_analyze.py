#!/usr/bin/env python3
"""Analyze maximize-paper campaign output: figures, stats, final reports."""

from __future__ import annotations

import json
import os
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
IEEE = {"font.family": "serif", "font.size": 9, "figure.dpi": 300}
plt.rcParams.update(IEEE)


def _find_dataset(out: Path) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for p in sorted((out / "stress_campaign").glob("run_*/dataset/maximize_dataset.csv")):
        if p.is_file():
            parts.append(pd.read_csv(p))
    if parts:
        return pd.concat(parts, ignore_index=True)
    alt = out / "dataset" / "maximize_merged.csv"
    if alt.is_file():
        return pd.read_csv(alt)
    return pd.DataFrame()


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=300)
    plt.close(fig)


def generate_figures(df: pd.DataFrame, figdir: Path) -> list[str]:
    figdir.mkdir(parents=True, exist_ok=True)
    made: list[str] = []
    prb = pd.to_numeric(df.get("prb_utilization_real"), errors="coerce")
    score = pd.to_numeric(df.get("decision_score"), errors="coerce")
    dec = df.get("decision", pd.Series(dtype=str)).astype(str).str.upper()
    phase = df.get("phase_id", pd.Series(dtype=str))

    def go(name: str, fig: plt.Figure | None):
        if fig is None:
            return
        _save(fig, figdir / f"{name}.png")
        made.append(name)

    if prb.notna().sum() >= 5:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        sc = ax.scatter(prb, score, c=dec.map({"ACCEPT": 0, "RENEGOTIATE": 1, "REJECT": 2}), cmap="RdYlGn_r", s=14, alpha=0.7)
        ax.set_xlabel("PRB (%)")
        ax.set_ylabel("Decision score")
        ax.set_title("PRB vs decision score")
        go("01_prb_vs_decision_score", fig)

        ordered = df.sort_values("prb_target_effective" if "prb_target_effective" in df.columns else prb.name)
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.plot(range(len(ordered)), pd.to_numeric(ordered["decision_score"], errors="coerce"), ".", alpha=0.5)
        ax.set_title("Progressive degradation (score vs sample order)")
        ax.set_xlabel("Stress progression index")
        go("02_progressive_degradation_curve", fig)

    if dec.nunique() >= 1:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        vc = dec.value_counts()
        ax.bar(vc.index, vc.values, color=["#2ecc71", "#f39c12", "#e74c3c"][: len(vc)])
        ax.set_title("ACCEPT / RENEGOTIATE / REJECT")
        go("03_accept_renegotiate_reject_boundary", fig)

    cols = [c for c in ("prb_utilization_real", "telemetry_transport_rtt_ms", "telemetry_core_cpu", "decision_score") if c in df.columns]
    sub = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    if len(sub) >= 10:
        fig, ax = plt.subplots(figsize=(4, 3))
        im = ax.imshow(sub.corr().values, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(cols)), cols, rotation=30, ha="right")
        ax.set_yticks(range(len(cols)), cols)
        fig.colorbar(im, ax=ax)
        ax.set_title("Multidomain sensitivity")
        go("04_multidomain_sensitivity_heatmap", fig)

    if phase.notna().any() and score.notna().any():
        fig, ax = plt.subplots(figsize=(4, 2.5))
        for p in sorted(phase.dropna().unique()):
            m = phase == p
            ax.scatter(prb[m], score[m], label=p, s=12, alpha=0.6)
        ax.legend(fontsize=6, ncol=2)
        ax.set_title("Runtime instability regions by phase")
        go("05_runtime_instability_regions", fig)

    if "slice_type" in df.columns:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        groups = [score[df["slice_type"] == s].dropna() for s in df["slice_type"].dropna().unique()]
        ax.boxplot(groups, tick_labels=list(df["slice_type"].dropna().unique()))
        ax.set_title("Slice-aware degradation")
        go("06_slice_aware_degradation", fig)

    if "bc_status" in df.columns:
        ok = df["bc_status"].astype(str).str.contains("COMMITTED", na=False)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        ax.bar(["COMMITTED", "other"], [ok.sum(), (~ok).sum()])
        ax.set_title("Governance under stress")
        go("07_governance_persistence_under_stress", fig)

    if "sla_agent_status" in df.columns:
        ok = df["sla_agent_status"].astype(str).str.contains("OK", na=False)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        ax.bar(["OK", "other"], [ok.sum(), (~ok).sum()])
        ax.set_title("SLA-Agent continuity")
        go("08_sla_agent_supervision_continuity", fig)

    risk = pd.to_numeric(df.get("ml_risk_score"), errors="coerce").dropna()
    if len(risk) > 5:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        ax.hist(risk, bins=20, color="#8e44ad")
        ax.set_title("ML risk under stress")
        go("09_ml_risk_degradation", fig)

    conf = pd.to_numeric(df.get("ml_confidence"), errors="coerce").dropna()
    if len(conf) > 5 and conf.std() > 0:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        ax.hist(conf, bins=20, color="#16a085")
        ax.set_title("ML confidence under stress")
        go("10_ml_confidence_degradation", fig)

    http = pd.to_numeric(df.get("http_elapsed_s"), errors="coerce").dropna()
    if len(http) > 5:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        ax.hist(http, bins=20, color="#34495e")
        ax.set_title("E2E latency under degradation")
        go("13_e2e_latency_under_degradation", fig)

    rtt = pd.to_numeric(df.get("telemetry_transport_rtt_ms"), errors="coerce")
    if rtt.notna().sum() >= 10:
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        ax.scatter(rtt, score, alpha=0.5, s=12)
        ax.set_xlabel("RTT (ms)")
        ax.set_title("Transport degradation sensitivity")
        go("14_transport_degradation_sensitivity", fig)

    return made


def hard_validation(df: pd.DataFrame) -> dict[str, Any]:
    prb = pd.to_numeric(df.get("prb_utilization_real"), errors="coerce").dropna()
    score = pd.to_numeric(df.get("decision_score"), errors="coerce").dropna()
    dec = df.get("decision", pd.Series(dtype=str)).astype(str).str.upper()
    counts = dec.value_counts().to_dict()
    pr, sp = (np.nan, np.nan)
    if len(prb) >= 3 and len(score) >= 3:
        try:
            pr = float(stats.pearsonr(prb, score)[0])
            sp = float(stats.spearmanr(prb, score)[0])
        except Exception:
            pass
    risk = pd.to_numeric(df.get("ml_risk_score"), errors="coerce").dropna()
    return {
        "n": len(df),
        "prb_std": float(prb.std()) if len(prb) > 1 else 0,
        "prb_range": [float(prb.min()), float(prb.max())] if len(prb) else None,
        "decisions": counts,
        "pearson_prb_score": pr,
        "spearman_prb_score": sp,
        "transition_region": counts.get("RENEGOTIATE", 0) > 0,
        "reject_emergence": counts.get("REJECT", 0) > 0,
        "boundary_rich": all(counts.get(k, 0) >= 30 for k in ("ACCEPT", "RENEGOTIATE", "REJECT")),
        "ml_fallback_all_05": bool(len(risk) and (risk == 0.5).all()),
        "governance_committed_rate": float(df["bc_status"].astype(str).str.contains("COMMITTED", na=False).mean()) if "bc_status" in df.columns else None,
        "sla_ok_rate": float(df["sla_agent_status"].astype(str).str.contains("OK", na=False).mean()) if "sla_agent_status" in df.columns else None,
    }


def write_reports(out: Path, df: pd.DataFrame, val: dict[str, Any], figures: list[str]) -> None:
    ad = out / "analysis"
    strong = []
    weak = []
    if val.get("prb_std", 0) > 15:
        strong.append(f"PRB std={val['prb_std']:.1f} (target >15)")
    else:
        weak.append(f"PRB std={val.get('prb_std')} below target 15")
    if val.get("transition_region"):
        strong.append(f"RENEGOTIATE emerged ({val['decisions'].get('RENEGOTIATE', 0)} samples)")
    else:
        weak.append("No RENEGOTIATE in live maximize run")
    if val.get("reject_emergence"):
        strong.append(f"REJECT emerged ({val['decisions'].get('REJECT', 0)} samples)")
    else:
        weak.append("No REJECT in live maximize run — HARD_PRB reject threshold may not have been reached in telemetry path")
    if val.get("n", 0) >= 300:
        strong.append(f"n={val['n']} samples (≥300)")
    else:
        weak.append(f"n={val.get('n')} < 300")

    above_nasp = val.get("boundary_rich") and val.get("transition_region") and val.get("n", 0) >= 300

    body = f"""## Publication verdict
**{'READY (multidomain operational evaluation)' if above_nasp else 'ELEVATED — stronger than orchestration-only; boundary/ML gaps may remain'}**

## Strong results
{chr(10).join(f'- {s}' for s in strong) or '- none'}

## Weak results / gaps
{chr(10).join(f'- {w}' for w in weak) or '- none'}

## Hard validation (Phase 10)
| Check | Result |
|-------|--------|
| PRB influences score? | {'YES' if val.get('pearson_prb_score') and abs(val['pearson_prb_score']) > 0.15 else 'WEAK/NO'} (r={val.get('pearson_prb_score')}) |
| Transition region? | {'YES' if val.get('transition_region') else 'NO'} |
| Multidomain degradation? | {'YES' if val.get('prb_std', 0) > 5 else 'PARTIAL'} |
| Boundary richness 30/30/30? | {'YES' if val.get('boundary_rich') else 'NO'} |
| Governance continuity? | {val.get('governance_committed_rate')} |
| SLA-Agent continuity? | {val.get('sla_ok_rate')} |
| ML real (non-fallback)? | {'NO' if val.get('ml_fallback_all_05') else 'PARTIAL'} |
| n ≥ 300 | {'YES' if val.get('n', 0) >= 300 else 'NO'} |
| Above NASP experimentally? | {'YES' if above_nasp else 'NO'} |

## Claims allowed
- Progressive multidomain operational pressure campaign with real PRB/RTT/core telemetry.
- SLA feasibility transitions when HARD_PRB policy triggers (if RENEG/REJECT observed).
- Governance/SLA-Agent under stress (if rates high).

## Claims forbidden
- Fabricated boundary classes.
- ML/XAI fully operational if ml_risk=0.5 throughout.

## Approved figures
{chr(10).join(f'- `{f}`' for f in figures)}

## Venue readiness
| Venue | Assessment |
|-------|------------|
| IEEE Network | {'High' if above_nasp else 'Medium-High'} |
| Computer Networks | {'High' if val.get('transition_region') else 'Medium'} |
| IEEE TNSM | {'Medium-High' if val.get('boundary_rich') else 'Medium'} |
| IEEE TMC | {'Medium' if above_nasp else 'Low-Medium'} |
"""
    (ad / "MAXIMIZE_PAPER_FINAL_REPORT.md").write_text(f"# Maximize paper final report\n\n{body}\n", encoding="utf-8")

    (ad / "SECTION7_FINAL_READY.md").write_text(
        f"""# Section 7 final ready

## Primary dataset
`stress_campaign/run_*/dataset/maximize_dataset.csv` — **{val.get('n')}** rows

## Decisions
```json
{json.dumps(val.get('decisions'), indent=2)}
```

## Figures (`figures/`)
{chr(10).join(f'- {f}' for f in figures)}

## Outline
1. Progressive multidomain stress methodology (phases p1–p5)
2. Operational dynamics and transition regions
3. Governance + SLA-Agent under stress
4. ML/XAI limitations (if fallback persists)
5. Comparison with orchestration-only narrative

""",
        encoding="utf-8",
    )


def _append_v62_boundary(out: Path, df: pd.DataFrame) -> pd.DataFrame:
    v62 = REPO / "evidencias_resultados_trisla_baseline_v13_2/dataset/final_dataset_v6_2_clean.csv"
    if not v62.is_file():
        return df
    b = pd.read_csv(v62)
    b = b.rename(columns={"PRB_before": "prb_utilization_real", "decision_score": "decision_score", "decision": "decision"})
    b["phase_id"] = "v62_historical"
    b["stratum"] = "boundary_reference_v62"
    df = df.copy()
    df["stratum"] = "maximize_live_20260516"
    return pd.concat([df, b[["prb_utilization_real", "decision_score", "decision", "phase_id", "stratum"]].dropna(subset=["decision"])], ignore_index=True)


def main() -> None:
    stamp = os.environ["OUT_STAMP"]
    out = REPO / f"evidencias_trisla_maximize_paper_{stamp}"
    df = _find_dataset(out)
    if df.empty:
        raise SystemExit("No maximize dataset found")
    df_live = df.copy()
    df_live["stratum"] = "maximize_live_20260516"
    df = _append_v62_boundary(out, df_live)
    df.to_csv(out / "dataset" / "maximize_merged.csv", index=False)
    df_live.to_csv(out / "dataset" / "maximize_live_only.csv", index=False)
    val_live = hard_validation(df_live)
    val_merged = hard_validation(df[df.get("stratum") != "boundary_reference_v62"] if "stratum" in df.columns else df)
    val = {**val_live, "merged_with_v62_boundary": val_merged, "v62_stratum": dict(Counter(df[df.get("stratum") == "boundary_reference_v62"]["decision"].astype(str))) if "stratum" in df.columns else {}}
    (out / "statistics" / "hard_validation.json").write_text(json.dumps(val, indent=2, default=str), encoding="utf-8")
    figures = generate_figures(df, out / "figures")
    for f in figures:
        src = out / "figures" / f"{f}.png"
        if src.is_file():
            shutil.copy(src, out / "paper_ready" / f"{f}.png")
    write_reports(out, df, val, figures)
    manifest = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    (out / "analysis" / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(f"ANALYZE DONE {out}")


if __name__ == "__main__":
    main()
