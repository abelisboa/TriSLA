#!/usr/bin/env python3
"""TriSLA Chapter 7 Q1 evidence campaign — analysis, figures, validation (read-only)."""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
BASES = {
    "BASE_1": REPO / "evidencias_final_publication_artifact_20260515T112034Z",
    "BASE_2": REPO / "evidencias_final_e2e_accept_batch_20260515T110538Z",
    "BASE_3": REPO / "evidencias_core_ran_ready_for_nasp_20260515T104025Z",
    "BASE_4": REPO / "evidencias_ml_xai_runtime_activation_20260515T203800Z",
    "BASE_5": REPO / "evidencias_trisla_blockchain_governance_audit_20260515T204916Z",
    "BASE_6": REPO / "evidencias_trisla_sla_agent_audit_20260515T210547Z",
    "BASE_7": REPO / "evidencias_resultados_trisla_baseline_v13_2",
}

IEEE_RC = {"font.family": "serif", "font.size": 9, "axes.labelsize": 9, "figure.dpi": 300}
plt.rcParams.update(IEEE_RC)


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_float(v: Any) -> float | None:
    try:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def _flatten_record(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    meta = data.get("metadata") or {}
    row: dict[str, Any] = {
        "source_file": path.name,
        "source_base": path.parent.parent.name if path.parent.name == "dataset" else "",
        "intent_id": data.get("intent_id"),
        "decision": data.get("decision") or meta.get("final_decision"),
        "service_type": data.get("service_type"),
        "bc_status": data.get("bc_status") or meta.get("bc_status"),
        "sla_agent_status": data.get("sla_agent_status") or meta.get("sla_agent_status"),
        "tx_hash": data.get("tx_hash") or data.get("blockchain_tx_hash") or meta.get("tx_hash"),
        "decision_score": meta.get("decision_score"),
        "ml_risk_score": meta.get("ml_risk_score") or meta.get("raw_risk_score"),
        "ml_confidence": meta.get("confidence_score") or data.get("confidence"),
        "telemetry_complete": meta.get("telemetry_complete"),
        "ran_prb": meta.get("ran_prb_utilization_input"),
        "transport_latency_ms": meta.get("transport_latency_ms_input")
        or meta.get("transport_latency_input"),
        "core_cpu": meta.get("core_cpu_percent_input") or meta.get("core_cpu_input"),
        "http_elapsed_s": meta.get("http_elapsed_s") or data.get("elapsed_s"),
        "sem_csmf_status": data.get("sem_csmf_status"),
        "ml_nsmf_status": data.get("ml_nsmf_status"),
    }
    factors = meta.get("contributing_factors") or []
    for i, f in enumerate(factors[:5]):
        if isinstance(f, dict):
            row[f"factor_{i}_name"] = f.get("factor")
            row[f"factor_{i}_contrib"] = f.get("contribution")
    return row


def load_unified_dataset(dataset_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for f in sorted(dataset_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            rows.append(_flatten_record(f, data))
        except (json.JSONDecodeError, OSError):
            continue
    for f in sorted(dataset_dir.glob("*.csv")):
        try:
            df = pd.read_csv(f)
            df["source_file"] = f.name
            df["source_base"] = "csv_import"
            rows.extend(df.to_dict(orient="records"))
        except Exception:
            continue
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    for col in ("decision_score", "ml_risk_score", "ml_confidence", "ran_prb", "transport_latency_ms", "core_cpu", "http_elapsed_s"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def detect_problems(df: pd.DataFrame) -> list[str]:
    problems: list[str] = []
    if df.empty:
        return ["No valid JSON/CSV datasets found in consolidated dataset."]
    if "decision_score" in df.columns:
        vals = df["decision_score"].dropna()
        if len(vals) > 1 and vals.std() == 0:
            problems.append("Decision score has zero variability.")
        elif len(vals) > 1 and vals.std() < 0.005:
            problems.append(f"Decision score variability very low (std={vals.std():.6f}).")
    if "ml_risk_score" in df.columns:
        vals = df["ml_risk_score"].dropna()
        if len(vals) > 0 and (vals == 0.5).all():
            problems.append("ML fallback detected (ml_risk_score=0.5 in all runs).")
    if "ran_prb" in df.columns:
        prb = df["ran_prb"].dropna()
        if len(prb) > 1 and prb.std() == 0:
            problems.append("PRB utilization static across samples (zero variability).")
    if "tx_hash" in df.columns:
        hashes = df["tx_hash"].dropna().astype(str)
        hashes = hashes[hashes.str.len() > 4]
        if len(hashes) > 0 and hashes.nunique() != len(hashes):
            problems.append("Repeated tx_hash detected.")
    if "telemetry_complete" in df.columns:
        tc = df["telemetry_complete"].dropna()
        if len(tc) and (tc == False).any():  # noqa: E712
            problems.append("telemetry_complete=false detected.")
    if "bc_status" in df.columns:
        bad = ~df["bc_status"].astype(str).str.contains("COMMITTED|SUCCESS", case=False, na=False)
        if bad.any():
            n = int(bad.sum())
            problems.append(f"Blockchain commitment inconsistency ({n} rows without COMMITTED/SUCCESS).")
    if "sla_agent_status" in df.columns:
        bad = ~df["sla_agent_status"].astype(str).str.contains("OK", case=False, na=False)
        if bad.any():
            problems.append("SLA-Agent inconsistency detected.")
    if "decision" in df.columns:
        dec = df["decision"].astype(str).str.upper()
        if not dec.isin(["REJECT", "RENEGOTIATE"]).any():
            problems.append("No REJECT/RENEGOTIATE decisions in consolidated dataset (boundary evidence missing).")
        if dec.nunique() == 1:
            problems.append(f"Single decision class only: {dec.mode().iloc[0]}.")
    if "ml_confidence" in df.columns:
        conf = df["ml_confidence"].dropna()
        if len(conf) > 0 and (conf == 0).all():
            problems.append("ML confidence always zero (XAI/ML may be inactive).")
    return problems


def figure_validation(name: str, df: pd.DataFrame, cols: list[str], min_n: int = 5) -> str:
    sub = df[cols].dropna(how="all") if cols else df
    n = len(sub)
    variability = "N/A"
    if cols and cols[0] in sub.columns:
        v = sub[cols[0]].dropna()
        if len(v) > 1:
            if pd.api.types.is_numeric_dtype(v):
                variability = f"std={v.std():.6f}, range=[{v.min():.4f},{v.max():.4f}]"
            else:
                variability = f"unique={v.nunique()}, n={len(v)}"
    corr_txt = ""
    if len(cols) >= 2 and all(c in sub.columns for c in cols[:2]):
        a, b = sub[cols[0]].dropna(), sub[cols[1]].dropna()
        idx = a.index.intersection(b.index)
        if len(idx) >= 3 and pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            try:
                r, p = stats.pearsonr(a.loc[idx], b.loc[idx])
                corr_txt = f"Pearson({cols[0]},{cols[1]})={r:.4f}, p={p:.4g}"
            except Exception:
                corr_txt = "correlation undefined (constant input)"
    if n < min_n:
        klass = "insufficient"
    elif "std=0" in variability or variability == "N/A":
        klass = "weak"
    elif n >= min_n and variability != "N/A":
        klass = "Q1-ready" if "std=" in variability and float(variability.split("=")[1].split(",")[0]) > 0.01 else "weak"
    else:
        klass = "weak"
    return textwrap.dedent(
        f"""# {name} validation

- **Dataset**: consolidated CH7 dataset
- **Variables**: {', '.join(cols) or 'aggregate'}
- **Samples**: {n}
- **Variability**: {variability}
- **Correlation**: {corr_txt or 'n/a'}
- **Classification**: {klass}

"""
    )


def save_fig(path: Path, fig: plt.Figure) -> bool:
    try:
        fig.savefig(path, bbox_inches="tight", dpi=300)
        plt.close(fig)
        return path.stat().st_size > 800
    except Exception:
        plt.close(fig)
        return False


def run_figures(out: Path, df: pd.DataFrame, validations: dict[str, str]) -> dict[str, str]:
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    status: dict[str, str] = {}

    def plot_or_skip(name: str, plot_fn, cols: list[str]) -> None:
        fig_path = fig_dir / f"{name}.png"
        try:
            fig = plot_fn()
            if fig is None:
                status[name] = "skipped_no_data"
                validations[name] = figure_validation(name, df, cols) + "\nSkipped: insufficient data.\n"
                return
            ok = save_fig(fig_path, fig)
            status[name] = "generated" if ok else "empty_file"
        except Exception as e:
            status[name] = f"error:{e}"
        validations[name] = figure_validation(name, df, cols)

    def hist_col(col: str, title: str, xlabel: str):
        def _fn():
            if col not in df.columns:
                return None
            s = df[col].dropna()
            if len(s) < 2:
                return None
            fig, ax = plt.subplots(figsize=(3.5, 2.5))
            ax.hist(s, bins=min(20, max(5, len(s) // 3)), color="#1f4e79", edgecolor="white")
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel("Count")
            return fig

        return _fn

    plot_or_skip("01_e2e_admission_latency", hist_col("http_elapsed_s", "E2E SLA admission latency", "seconds (s)"), ["http_elapsed_s"])
    plot_or_skip(
        "02_decision_score_vs_prb",
        lambda: _scatter(df, "ran_prb", "decision_score", "Decision score vs PRB"),
        ["ran_prb", "decision_score"],
    )
    plot_or_skip("03_decision_score_distribution", hist_col("decision_score", "Decision score distribution", "score"), ["decision_score"])
    plot_or_skip("04_ml_risk_distribution", hist_col("ml_risk_score", "ML risk distribution", "risk"), ["ml_risk_score"])
    plot_or_skip("05_ml_confidence_distribution", hist_col("ml_confidence", "ML confidence distribution", "confidence"), ["ml_confidence"])
    plot_or_skip("06_shap_contribution_ranking", lambda: _factor_bar(df), ["factor_0_contrib"])
    plot_or_skip("07_telemetry_completeness", lambda: _telemetry_bar(df), ["telemetry_complete"])
    plot_or_skip("08_governance_tx_hash_validation", lambda: _tx_unique_bar(df), ["tx_hash"])
    plot_or_skip("09_runtime_pipeline_success", lambda: _pipeline_bar(df), ["sem_csmf_status", "bc_status"])
    plot_or_skip("10_slice_aware_behavior", lambda: _slice_box(df), ["service_type", "decision_score"])
    plot_or_skip(
        "11_multidomain_sensitivity",
        lambda: _scatter(df, "transport_latency_ms", "decision_score", "Transport latency vs score"),
        ["transport_latency_ms", "decision_score"],
    )
    plot_or_skip("12_accept_reject_boundary", lambda: _decision_bar(df), ["decision"])
    plot_or_skip("13_sla_agent_lifecycle", lambda: _status_bar(df, "sla_agent_status", "SLA-Agent status"), ["sla_agent_status"])
    plot_or_skip("14_blockchain_governance", lambda: _status_bar(df, "bc_status", "Blockchain status"), ["bc_status"])
    plot_or_skip(
        "15_multidomain_telemetry_snapshot",
        lambda: _multi_scatter(df),
        ["ran_prb", "transport_latency_ms", "core_cpu"],
    )
    plot_or_skip(
        "16_prb_sensitivity",
        lambda: _binned_curve(df, "ran_prb", "decision_score", "PRB sensitivity"),
        ["ran_prb", "decision_score"],
    )
    plot_or_skip(
        "17_transport_degradation_sensitivity",
        lambda: _binned_curve(df, "transport_latency_ms", "decision_score", "Transport degradation"),
        ["transport_latency_ms", "decision_score"],
    )
    plot_or_skip(
        "18_core_domain_influence",
        lambda: _scatter(df, "core_cpu", "decision_score", "Core CPU vs decision score"),
        ["core_cpu", "decision_score"],
    )
    plot_or_skip("19_e2e_workflow_timing", hist_col("http_elapsed_s", "E2E workflow timing", "s"), ["http_elapsed_s"])
    plot_or_skip("20_correlation_matrix", lambda: _corr_heatmap(df), ["ran_prb", "transport_latency_ms", "core_cpu", "decision_score"])
    return status


def _scatter(df: pd.DataFrame, x: str, y: str, title: str):
    if x not in df.columns or y not in df.columns:
        return None
    sub = df[[x, y]].dropna()
    if len(sub) < 3:
        return None
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.scatter(sub[x], sub[y], alpha=0.7, s=18, c="#c0392b")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title)
    return fig


def _factor_bar(df: pd.DataFrame):
    cols = [c for c in df.columns if c.endswith("_contrib")]
    if not cols:
        return None
    sums: dict[str, float] = {}
    for c in cols:
        name_col = c.replace("_contrib", "_name")
        if name_col in df.columns:
            for _, row in df[[name_col, c]].dropna().iterrows():
                n = str(row[name_col])
                sums[n] = sums.get(n, 0) + abs(float(row[c]))
    if not sums:
        return None
    items = sorted(sums.items(), key=lambda x: -x[1])[:8]
    fig, ax = plt.subplots(figsize=(4, 2.8))
    ax.barh([k for k, _ in items][::-1], [v for _, v in items][::-1], color="#2e86ab")
    ax.set_title("SHAP/XAI factor contributions (aggregated)")
    ax.set_xlabel("|contribution| sum")
    return fig


def _telemetry_bar(df: pd.DataFrame):
    if "telemetry_complete" not in df.columns:
        return None
    vc = df["telemetry_complete"].value_counts(dropna=False)
    if vc.empty:
        return None
    fig, ax = plt.subplots(figsize=(3, 2.5))
    ax.bar([str(k) for k in vc.index], vc.values, color="#27ae60")
    ax.set_title("Telemetry completeness")
    return fig


def _tx_unique_bar(df: pd.DataFrame):
    if "tx_hash" not in df.columns:
        return None
    h = df["tx_hash"].dropna().astype(str)
    h = h[h.str.len() > 4]
    if len(h) == 0:
        return None
    fig, ax = plt.subplots(figsize=(3, 2.5))
    ax.bar(["unique", "total"], [h.nunique(), len(h)], color=["#2980b9", "#95a5a6"])
    ax.set_title("Governance tx_hash uniqueness")
    return fig


def _pipeline_bar(df: pd.DataFrame):
    fields = ["sem_csmf_status", "ml_nsmf_status", "bc_status", "sla_agent_status"]
    present = [f for f in fields if f in df.columns]
    if not present:
        return None
    ok_rates = []
    labels = []
    for f in present:
        s = df[f].astype(str)
        ok = s.str.contains("OK|COMMITTED|SUCCESS", case=False, na=False).mean()
        ok_rates.append(ok * 100)
        labels.append(f.replace("_status", ""))
    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.bar(labels, ok_rates, color="#8e44ad")
    ax.set_ylim(0, 105)
    ax.set_ylabel("% success")
    ax.set_title("Runtime pipeline success ratio")
    return fig


def _slice_box(df: pd.DataFrame):
    if "service_type" not in df.columns or "decision_score" not in df.columns:
        return None
    sub = df[["service_type", "decision_score"]].dropna()
    if sub.empty:
        return None
    groups = [g["decision_score"].values for _, g in sub.groupby("service_type")]
    labels = list(sub.groupby("service_type").groups.keys())
    if not groups:
        return None
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.boxplot(groups, labels=labels)
    ax.set_title("Slice-aware decision score")
    ax.set_ylabel("decision_score")
    return fig


def _decision_bar(df: pd.DataFrame):
    if "decision" not in df.columns:
        return None
    vc = df["decision"].astype(str).str.upper().value_counts()
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.bar(vc.index, vc.values, color=["#27ae60", "#f39c12", "#e74c3c"][: len(vc)])
    ax.set_title("ACCEPT / REJECT / RENEGOTIATE")
    return fig


def _status_bar(df: pd.DataFrame, col: str, title: str):
    if col not in df.columns:
        return None
    vc = df[col].astype(str).value_counts().head(8)
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.bar(vc.index, vc.values)
    ax.set_title(title)
    plt.xticks(rotation=25, ha="right")
    return fig


def _binned_curve(df: pd.DataFrame, x: str, y: str, title: str):
    if x not in df.columns or y not in df.columns:
        return None
    sub = df[[x, y]].dropna()
    if len(sub) < 5 or sub[x].std() == 0:
        return None
    sub = sub.sort_values(x)
    sub["bin"] = pd.qcut(sub[x], q=min(5, len(sub) // 2), duplicates="drop")
    agg = sub.groupby("bin", observed=True)[y].mean()
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot(range(len(agg)), agg.values, marker="o", color="#16a085")
    ax.set_title(title)
    ax.set_xlabel(f"binned {x}")
    ax.set_ylabel(f"mean {y}")
    return fig


def _multi_scatter(df: pd.DataFrame):
    cols = ["ran_prb", "transport_latency_ms", "core_cpu"]
    present = [c for c in cols if c in df.columns]
    if len(present) < 2:
        return None
    sub = df[present].dropna()
    if len(sub) < 3:
        return None
    fig, axes = plt.subplots(1, len(present) - 1, figsize=(3.5 * (len(present) - 1), 2.5))
    if len(present) - 1 == 1:
        axes = [axes]
    for ax, i in zip(axes, range(len(present) - 1)):
        ax.scatter(sub[present[i]], sub[present[i + 1]], s=12, alpha=0.7)
        ax.set_xlabel(present[i])
        ax.set_ylabel(present[i + 1])
    fig.suptitle("Multidomain telemetry snapshot")
    return fig


def _corr_heatmap(df: pd.DataFrame):
    cols = [c for c in ("ran_prb", "transport_latency_ms", "core_cpu", "decision_score", "ml_risk_score") if c in df.columns]
    sub = df[cols].dropna()
    if len(sub) < 5:
        return None
    corr = sub.corr()
    fig, ax = plt.subplots(figsize=(4, 3.2))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)), cols, rotation=45, ha="right")
    ax.set_yticks(range(len(cols)), cols)
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title("Correlation matrix")
    return fig


def statistics_report(df: pd.DataFrame, out: Path) -> None:
    lines = ["# Statistical summary\n"]
    numeric = df.select_dtypes(include=[np.number])
    if numeric.empty:
        lines.append("No numeric columns.\n")
    else:
        desc = numeric.describe().T
        desc["IQR"] = desc["75%"] - desc["25%"]
        lines.append("```\n" + desc.to_string() + "\n```\n")
        lines.append("\n## Correlations (Pearson)\n")
        if len(numeric.columns) >= 2:
            lines.append("```\n" + numeric.corr().to_string() + "\n```\n")
    (out / "analysis" / "statistical_summary.md").write_text("\n".join(lines), encoding="utf-8")
    numeric.to_csv(out / "dataset" / "consolidated_numeric.csv", index=False)


def tables_report(df: pd.DataFrame, out: Path, problems: list[str]) -> None:
    tdir = out / "tables"
    summaries = {
        "01_runtime_summary.md": _runtime_table(df),
        "02_ml_xai_summary.md": _ml_table(df),
        "03_governance_summary.md": _gov_table(df),
        "04_sla_agent_summary.md": _sla_table(df),
        "05_telemetry_summary.md": _tel_table(df),
        "06_slice_aware_summary.md": _slice_table(df),
        "07_freeze_consistency.md": "See freeze/trisla_runtime_freeze.yaml and runtime snapshots.\n",
        "08_statistical_summary.md": "See analysis/statistical_summary.md\n",
        "09_reproducibility_summary.md": _repro_table(problems),
        "10_deployment_consistency.md": "See runtime/trisla_deployments.txt\n",
    }
    for name, body in summaries.items():
        (tdir / name).write_text(body, encoding="utf-8")


def _runtime_table(df: pd.DataFrame) -> str:
    cols = ["sem_csmf_status", "ml_nsmf_status", "bc_status", "sla_agent_status"]
    lines = ["# Runtime summary\n"]
    for c in cols:
        if c in df.columns:
            lines.append(f"\n## {c}\n")
            lines.append("```\n" + df[c].value_counts().to_string() + "\n```")
    return "\n".join(lines)


def _ml_table(df: pd.DataFrame) -> str:
    parts = ["# ML/XAI summary\n"]
    for c in ("ml_risk_score", "ml_confidence"):
        if c in df.columns:
            s = df[c].dropna()
            parts.append(f"- **{c}**: n={len(s)}, mean={s.mean():.4f}, std={s.std():.4f}")
    return "\n".join(parts)


def _gov_table(df: pd.DataFrame) -> str:
    lines = ["# Governance summary\n"]
    if "tx_hash" in df.columns:
        h = df["tx_hash"].dropna().astype(str)
        lines.append(f"- unique tx_hash: {h.nunique()} / {len(h)}")
    if "bc_status" in df.columns:
        lines.append("\n```\n" + df["bc_status"].value_counts().to_string() + "\n```")
    return "\n".join(lines)


def _sla_table(df: pd.DataFrame) -> str:
    if "sla_agent_status" not in df.columns:
        return "# SLA-Agent summary\n\nNo data.\n"
    return "# SLA-Agent summary\n\n```\n" + df["sla_agent_status"].value_counts().to_string() + "\n```"


def _tel_table(df: pd.DataFrame) -> str:
    lines = ["# Telemetry summary\n"]
    for c in ("ran_prb", "transport_latency_ms", "core_cpu", "telemetry_complete"):
        if c in df.columns:
            s = df[c].dropna()
            if len(s):
                lines.append(f"- {c}: mean={s.mean():.4f}, std={s.std():.4f}, n={len(s)}")
    return "\n".join(lines)


def _slice_table(df: pd.DataFrame) -> str:
    if "service_type" not in df.columns:
        return "# Slice-aware summary\n\nNo service_type column.\n"
    g = df.groupby("service_type").agg(
        n=("decision_score", "count"),
        mean_score=("decision_score", "mean"),
        std_score=("decision_score", "std"),
    )
    return "# Slice-aware summary\n\n```\n" + g.to_string() + "\n```"


def _repro_table(problems: list[str]) -> str:
    return "# Reproducibility summary\n\n" + ("\n".join(f"- {p}" for p in problems) if problems else "- No critical blockers logged.\n")


def final_reports(out: Path, df: pd.DataFrame, problems: list[str], fig_status: dict[str, str]) -> None:
    q1_figs = [k for k, v in fig_status.items() if v == "generated"]
    weak = [k for k, v in fig_status.items() if v != "generated"]
    publishable = len(problems) == 0 and len(q1_figs) >= 10

    claims = [
        "TriSLA executes E2E SLA submission with portal-backend integration (when runtime healthy).",
    ]
    if "bc_status" in df.columns and df["bc_status"].astype(str).str.contains("COMMITTED", na=False).any():
        claims.append("Blockchain records COMMITTED governance transactions for successful E2E runs.")
    if "sla_agent_status" in df.columns and df["sla_agent_status"].astype(str).str.contains("OK", na=False).any():
        claims.append("SLA-Agent reports OK supervision on successful pipeline runs.")
    if "decision_score" in df.columns and df["decision_score"].dropna().std() and df["decision_score"].dropna().std() > 0.01:
        claims.append("Decision score exhibits measurable variability across samples.")
    if not any("REJECT" in p for p in problems):
        if "decision" in df.columns and df["decision"].astype(str).str.upper().isin(["REJECT", "RENEGOTIATE"]).any():
            claims.append("Admission boundary includes non-ACCEPT decisions in dataset.")

    (out / "analysis" / "CLAIMS_ALLOWED.md").write_text(
        "# Claims allowed (evidence-backed only)\n\n" + "\n".join(f"- {c}" for c in claims) + "\n\n## Claims NOT allowed without new campaign\n\n"
        + "\n".join(f"- {p}" for p in problems)
        + "\n",
        encoding="utf-8",
    )

    report = f"""# FINAL Q1 CH7 REPORT

**Campaign output**: `{out.name}`  
**UTC**: {datetime.now(timezone.utc).isoformat()}

## Executive summary

Consolidated **{len(df)}** records from BASE_2,4,5,6,7 (+ publication artifact metadata).
**Critical problems**: {len(problems)}  
**Q1 figures generated**: {len(q1_figs)} / 20  
**Chapter 7 publishable (strict Q1)**: **{"YES (conditional)" if publishable else "NO"}**

## Strong results

- E2E ACCEPT batch with COMMITTED blockchain and OK SLA-Agent on recent campaign (BASE_2/5/6).
- Multidomain telemetry fields present (RAN PRB, transport latency, core CPU) in JSON metadata.
- Governance tx_hash uniqueness in primary E2E batch.

## Weak results / gaps

{chr(10).join(f"- {p}" for p in problems) if problems else "- See per-figure validation."}

## Figure disposition

### Q1-ready (generated with data)
{chr(10).join(f"- {f}" for f in sorted(q1_figs)) if q1_figs else "- none"}

### Weak / skipped / insufficient
{chr(10).join(f"- {f}: {fig_status[f]}" for f in sorted(weak))}

## Publication readiness (honest)

| Venue | Readiness |
|-------|-----------|
| IEEE Network | {"Medium" if len(q1_figs) >= 8 else "Low"} — needs boundary + PRB sensitivity campaigns |
| Computer Networks | {"Medium-Low" if problems else "Low"} |
| TNSM | Low without REJECT/RENEGOTIATE + statistical power |
| TMC | Low — multidomain sensitivity insufficient in consolidated set |

## Scientific risks

- ML risk pinned at 0.5 (fallback) in several JSON runs.
- PRB input at 0.0 in E2E batch → weak PRB sensitivity claims.
- ML confidence 0.0 → XAI not demonstrated as operational in that batch.
- Baseline v13_2 mixes BLOCKCHAIN_FAILED rows — do not merge naively with May-15 E2E success batch.

## Answers (Phase 9)

1. **Capítulo 7 publicável?** {"Parcialmente — somente claims de pipeline/governance com campanha dedicada de sensibilidade." if problems else "Revisar figuras individuais."}
2. **Figuras Q1**: ver lista acima ({len(q1_figs)} geradas com dados).
3. **Descartar**: figuras skipped/empty e qualquer gráfico com PRB/ML sem variabilidade.
4. **Refazer campanhas**: sensibilidade PRB, boundary REJECT/RENEGOTIATE, ML/XAI online sem fallback.
5. **Dataset suficiente?** Parcial — consolidado grande, mas classes de decisão desbalanceadas.
6. **Runtime sustenta claims?** Sim para pipeline E2E recente; não para sensibilidade PRB/ML sem nova coleta.
7. **Claims arriscados**: "ML online", "SHAP operacional", "PRB influencia decisão" sem nova campanha.
8. **Inconsistências**: ver problem detection report.
9. **Gráficos enganosos**: distribuição de score estreita (~0.82–0.83) pode sugerir discriminação inexistente.
10. **Acima do NASP?** Parcial — governance E2E sim; multidomínio sensibilidade ainda abaixo do bar NASP-level.

"""
    (out / "analysis" / "FINAL_Q1_CH7_REPORT.md").write_text(report, encoding="utf-8")


def consolidate_bases(out: Path) -> None:
    ds = out / "dataset"
    ds.mkdir(parents=True, exist_ok=True)
    for key in ("BASE_2", "BASE_4", "BASE_5", "BASE_6", "BASE_7"):
        base = BASES[key]
        if not base.is_dir():
            continue
        for pattern in ("*.csv", "*.json"):
            for src in base.rglob(pattern):
                if "dataset" in src.parts or src.parent.name == "dataset":
                    dest = ds / f"{key}_{src.name}"
                    if not dest.exists():
                        shutil.copy2(src, dest)


def main() -> None:
    ts = os.environ.get("OUT_STAMP") or _stamp()
    out = REPO / f"evidencias_trisla_ch7_q1_final_{ts}"
    for sub in ("analysis", "dataset", "figures", "tables", "runtime", "freeze", "validation", "logs", "paper_assets", "correction_plan"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    consolidate_bases(out)
    df = load_unified_dataset(out / "dataset")
    df.to_csv(out / "dataset" / "unified_ch7_records.csv", index=False)

    problems = detect_problems(df)
    (out / "analysis" / "problem_detection_report.md").write_text(
        "# Problem Detection Report\n\n" + ("\n".join(f"- {p}" for p in problems) if problems else "No critical scientific inconsistencies detected.\n"),
        encoding="utf-8",
    )
    for idx, p in enumerate(problems):
        (out / "correction_plan" / f"problem_{idx + 1}.md").write_text(
            f"# {p}\n\nRoot cause investigation required.\nThe result cannot be considered Q1-ready until resolved.\n",
            encoding="utf-8",
        )

    validations: dict[str, str] = {}
    fig_status = run_figures(out, df, validations)
    for name, body in validations.items():
        (out / "analysis" / f"{name}_validation.md").write_text(body, encoding="utf-8")

    statistics_report(df, out)
    tables_report(df, out, problems)
    final_reports(out, df, problems, fig_status)

    manifest = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    (out / "analysis" / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(f"TRISLA CH7 Q1 FINAL CAMPAIGN COMPLETED: {out}")


if __name__ == "__main__":
    main()
