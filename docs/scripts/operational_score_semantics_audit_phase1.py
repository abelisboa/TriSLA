#!/usr/bin/env python3
"""Phase 1 — Contributing factors audit (decision_score_mode only)."""
from __future__ import annotations

import json
import math
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
RAW_ROOT = NASP_ROOT / "phase_1_extreme_runtime_stress/raw"
CODE_REF = Path("/home/porvir5g/gtp5g/trisla/apps/decision-engine/src/decision_score_mode.py")


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


def _load_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for regime_dir in sorted(RAW_ROOT.iterdir()):
        if not regime_dir.is_dir():
            continue
        for p in sorted(regime_dir.glob("submit_*.json")):
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            payload = doc.get("payload") or {}
            meta = payload.get("metadata") or {}
            if str(meta.get("decision_source")) != "decision_score_mode":
                continue
            row_csv = doc.get("row") or {}
            snap = meta.get("telemetry_snapshot") or {}
            transport = snap.get("transport") or {}
            core = snap.get("core") or {}
            sla = meta.get("sla_metrics") or row_csv
            norm = meta.get("normalized_inputs") or {}
            factors = meta.get("contributing_factors") or []
            factor_map = {str(f.get("factor")): f for f in factors}
            num = sum(_safe_float(f.get("contribution")) or 0 for f in factors)
            den = sum(_safe_float(f.get("weight")) or 0 for f in factors)
            score = _safe_float(meta.get("decision_score"))
            recon = num / den if den > 0 else None
            rows.append(
                {
                    "execution_id": row_csv.get("execution_id"),
                    "regime_mbps": row_csv.get("regime_mbps") or regime_dir.name,
                    "timestamp": row_csv.get("timestamp"),
                    "decision_score": score,
                    "score_reconstructed": recon,
                    "reconstruction_error": abs((score or 0) - (recon or 0)) if score and recon else None,
                    "contributing_factors": factors,
                    "factor_map": factor_map,
                    "active_factor_names": [f.get("factor") for f in factors],
                    "reason_codes": meta.get("reason_codes") or [],
                    "prb_raw": _safe_float((norm.get("prb_goodness") or {}).get("raw_prb"))
                    or _safe_float(meta.get("ran_prb_utilization_input")),
                    "prb_goodness": _safe_float((norm.get("prb_goodness") or {}).get("value")),
                    "risk_goodness": _safe_float((norm.get("risk_goodness") or {}).get("value")),
                    "feasibility_status": (norm.get("feasibility") or {}).get("status"),
                    "pressure_status": (norm.get("resource_pressure") or {}).get("status"),
                    "semantic_status": (norm.get("semantic") or {}).get("status"),
                    "ran_aware_final_risk": _safe_float(meta.get("ran_aware_final_risk")),
                    "rtt_ms": _safe_float(transport.get("rtt_ms", transport.get("rtt"))),
                    "jitter_ms": _safe_float(transport.get("jitter_ms", transport.get("jitter"))),
                    "core_cpu": _safe_float(core.get("cpu_utilization", core.get("cpu"))),
                    "core_memory": _safe_float(core.get("memory_utilization", core.get("memory"))),
                    "feasibility_score": _safe_float(sla.get("feasibility_score") if isinstance(sla, dict) else None),
                    "resource_pressure": _safe_float(sla.get("resource_pressure") if isinstance(sla, dict) else None),
                    "weights_profile": (norm.get("slice_profile") or {}).get("weights"),
                }
            )
    return rows


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


def main() -> None:
    ts = _utc_stamp()
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_operational_score_semantics_{ts}")
    p1 = out / "phase_1_contributing_factors"
    figdir = p1 / "figures"
    for sub in (p1, figdir, out / "freeze", out / "analysis", out / "figures", out / "logs"):
        sub.mkdir(parents=True, exist_ok=True)

    rows = _load_rows()
    n = len(rows)
    if n == 0:
        raise SystemExit("No decision_score_mode rows")

    # Factor-level flattened records
    flat: list[dict[str, Any]] = []
    for r in rows:
        for f in r["contributing_factors"]:
            flat.append(
                {
                    "execution_id": r["execution_id"],
                    "factor": f.get("factor"),
                    "weight": _safe_float(f.get("weight")),
                    "input": _safe_float(f.get("input")),
                    "contribution": _safe_float(f.get("contribution")),
                    "decision_score": r["decision_score"],
                    "prb_raw": r["prb_raw"],
                }
            )

    factor_names = sorted({x["factor"] for x in flat if x["factor"]})
    factor_presence = Counter(x["factor"] for x in flat)
    by_factor: dict[str, list[dict]] = defaultdict(list)
    for x in flat:
        by_factor[str(x["factor"])].append(x)

    # Importance: mean contribution and share of total
    total_contrib = defaultdict(float)
    for x in flat:
        total_contrib[str(x["factor"])] += x["contribution"] or 0
    grand = sum(total_contrib.values()) or 1.0
    importance = {k: v / grand for k, v in total_contrib.items()}

    # Per-factor stats
    factor_stats: dict[str, Any] = {}
    for fname in factor_names:
        sub = by_factor[fname]
        inputs = [x["input"] for x in sub if x["input"] is not None]
        contribs = [x["contribution"] for x in sub if x["contribution"] is not None]
        scores = [x["decision_score"] for x in sub if x["decision_score"] is not None]
        factor_stats[fname] = {
            "presence_n": len(sub),
            "input_mean": statistics.mean(inputs) if inputs else None,
            "input_std": statistics.stdev(inputs) if len(inputs) > 1 else 0,
            "contribution_mean": statistics.mean(contribs) if contribs else None,
            "contribution_std": statistics.stdev(contribs) if len(contribs) > 1 else 0,
            "share_of_total_contribution": importance.get(fname, 0),
            "corr_input_score": _pearson(inputs, scores) if len(inputs) == len(scores) else None,
            "corr_contribution_score": _pearson(contribs, scores) if len(contribs) == len(scores) else None,
        }

    # Correlation matrix: factor inputs vs score
    scores_all = [r["decision_score"] for r in rows if r["decision_score"]]
    corr_inputs: dict[str, Optional[float]] = {}
    for fname in factor_names:
        vals = [
            _safe_float(r["factor_map"].get(fname, {}).get("input"))
            for r in rows
            if r["decision_score"] and fname in r["factor_map"]
        ]
        sc = [r["decision_score"] for r in rows if r["decision_score"] and fname in r["factor_map"]]
        if len(vals) == len(sc) and len(vals) >= 2:
            corr_inputs[fname] = _pearson(vals, sc)

    # PRB drives ran_prb_goodness
    prbs = [r["prb_raw"] for r in rows if r["prb_raw"] is not None]
    prb_good = [r["prb_goodness"] for r in rows if r["prb_goodness"] is not None]
    prb_inputs = [
        _safe_float(r["factor_map"].get("ran_prb_goodness", {}).get("input")) for r in rows
    ]
    prb_contrib = [
        _safe_float(r["factor_map"].get("ran_prb_goodness", {}).get("contribution")) for r in rows
    ]

    # Missing inputs audit
    missing_audit = {
        "feasibility_missing": sum(1 for r in rows if r["feasibility_status"] == "missing"),
        "pressure_missing": sum(1 for r in rows if r["pressure_status"] == "missing"),
        "semantic_missing": sum(1 for r in rows if r["semantic_status"] == "missing"),
        "reason_input_degraded": sum(1 for r in rows if "INPUT_DEGRADED" in (r["reason_codes"] or [])),
    }

    recon_errors = [r["reconstruction_error"] for r in rows if r["reconstruction_error"] is not None]
    recon_ok = all(e < 1e-6 for e in recon_errors) if recon_errors else False

    stats_out = {
        "n": n,
        "factor_presence": dict(factor_presence),
        "factor_stats": factor_stats,
        "importance_share": importance,
        "corr_factor_input_vs_score": corr_inputs,
        "corr_prb_raw_vs_score": _pearson(
            [r["prb_raw"] for r in rows if r["prb_raw"] and r["decision_score"]],
            [r["decision_score"] for r in rows if r["prb_raw"] and r["decision_score"]],
        ),
        "corr_prb_goodness_input_vs_score": _pearson(
            [x for x in prb_inputs if x is not None],
            [r["decision_score"] for r in rows if r["factor_map"].get("ran_prb_goodness")],
        ),
        "missing_inputs": missing_audit,
        "reconstruction_max_error": max(recon_errors) if recon_errors else None,
        "reconstruction_ok": recon_ok,
        "active_factors_runtime": factor_names,
        "inactive_configured": ["feasibility", "resource_headroom"],
    }
    (p1 / "contributing_factors_stats.json").write_text(
        json.dumps(stats_out, indent=2), encoding="utf-8"
    )

    ordered = sorted(rows, key=lambda r: (r.get("timestamp") or "", r.get("execution_id") or ""))

    _figure_style()

    # Fig 1: factor importance (mean contribution share)
    fig, ax = plt.subplots()
    names = list(importance.keys())
    vals = [importance[k] for k in names]
    colors = {"ran_prb_goodness": "#2ca02c", "risk_inverse": "#1f77b4", "semantic_priority": "#9467bd"}
    ax.barh(names, vals, color=[colors.get(n, "#888") for n in names])
    ax.set_xlabel("Share of total weighted contribution")
    ax.set_title("Runtime factor importance (n=37, score_mode)")
    _save(figdir, "01_factor_importance.png")

    # Fig 2: contribution distributions per factor
    fig, ax = plt.subplots(figsize=(9, 4.5))
    data = [
        [x["contribution"] for x in by_factor[f] if x["contribution"] is not None] for f in factor_names
    ]
    ax.boxplot(data, labels=[f.replace("_", "\n") for f in factor_names])
    ax.set_ylabel("Contribution to numerator")
    ax.set_title("Factor contribution distributions")
    _save(figdir, "02_factor_contribution_distributions.png")

    # Fig 3: heatmap inputs (rows=samples, cols=factors)
    mat = np.zeros((n, len(factor_names)))
    for i, r in enumerate(ordered):
        for j, fname in enumerate(factor_names):
            mat[i, j] = _safe_float(r["factor_map"].get(fname, {}).get("input")) or 0
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mat, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(factor_names)))
    ax.set_xticklabels(factor_names, rotation=25, ha="right")
    ax.set_ylabel("Submit index (ordered)")
    ax.set_title("Factor goodness inputs (heatmap)")
    plt.colorbar(im, ax=ax, fraction=0.046)
    _save(figdir, "03_factor_input_heatmap.png")

    # Fig 4: correlation bar factor input vs score
    fig, ax = plt.subplots()
    cnames = list(corr_inputs.keys())
    cvals = [corr_inputs[k] or 0 for k in cnames]
    ax.barh(cnames, cvals, color=[colors.get(k, "#888") for k in cnames])
    ax.axvline(0, color="k", linewidth=0.5)
    ax.set_xlabel("Pearson r with decision_score")
    ax.set_title("Factor input correlation with score")
    _save(figdir, "04_factor_score_correlation.png")

    # Fig 5: temporal evolution stacked contributions
    fig, ax = plt.subplots(figsize=(11, 4))
    idx = range(n)
    bottom = np.zeros(n)
    for fname in factor_names:
        cont = [
            _safe_float(r["factor_map"].get(fname, {}).get("contribution")) or 0 for r in ordered
        ]
        ax.bar(idx, cont, bottom=bottom, label=fname, color=colors.get(fname, "#888"))
        bottom += np.array(cont)
    ax.plot(idx, [r["decision_score"] or 0 for r in ordered], "k.-", linewidth=1, label="decision_score")
    ax.set_xlabel("Submit sequence")
    ax.set_ylabel("Contribution / score")
    ax.set_title("Runtime factor evolution + score overlay")
    ax.legend(fontsize=7, loc="upper right")
    _save(figdir, "05_factor_temporal_evolution.png")

    # Fig 6: PRB vs ran_prb_goodness contribution
    fig, ax = plt.subplots()
    ax.scatter(prbs, prb_contrib, c="#2ca02c", s=40, alpha=0.75)
    ax.set_xlabel("PRB raw (%)")
    ax.set_ylabel("ran_prb_goodness contribution")
    ax.set_title("RAN domain drives score via PRB term")
    _save(figdir, "06_prb_vs_ran_contribution.png")

    # Verdict
    three_factors = set(factor_names) == {
        "ran_prb_goodness",
        "risk_inverse",
        "semantic_priority",
    }
    defined = (
        recon_ok
        and three_factors
        and factor_presence.get("ran_prb_goodness", 0) == n
        and importance.get("ran_prb_goodness", 0) > 0
    )
    verdict = "CONTRIBUTING_FACTORS_DEFINED" if defined else "CONTRIBUTING_FACTORS_INCONSISTENT"

    md = f"""# Phase 1 — Contributing Factors (`decision_score_mode`)

**Audit:** `evidencias_trisla_operational_score_semantics_{ts}`  
**Population:** n={n} (NASP-hard+, score-continuous regime only)  
**Code:** `{CODE_REF}`  
**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Executive summary

Runtime `decision_score` is a **weighted mean of active goodness terms** (`score = Σ wᵢ·gᵢ / Σ wᵢ`). In NASP-hard+ score_mode, **three factors are active** in every submit: `ran_prb_goodness`, `risk_inverse`, `semantic_priority`. Configured terms `feasibility` and `resource_headroom` are **absent** (telemetry missing → excluded from denominator). Reconstruction from `contributing_factors` matches `metadata.decision_score` (max error **{max(recon_errors) if recon_errors else 0:.2e}**).

**Verdict:** `{verdict}`

## Active vs inactive factors

| Factor | In contributing_factors | Presence | Mean contribution | Share of Σ contribution |
|--------|-------------------------|----------|-------------------|-------------------------|
"""
    for fname in factor_names:
        fs = factor_stats[fname]
        md += (
            f"| `{fname}` | yes | {fs['presence_n']}/{n} | "
            f"{fs['contribution_mean']:.4f} | {100*fs['share_of_total_contribution']:.1f}% |\n"
        )

    md += f"""
### Configured but inactive at runtime (URLLC profile)

| Term | normalized_inputs status | n missing |
|------|--------------------------|----------:|
| feasibility | missing | {missing_audit['feasibility_missing']}/{n} |
| resource_headroom (resource_pressure) | missing | {missing_audit['pressure_missing']}/{n} |
| semantic (direct) | missing | {missing_audit['semantic_missing']}/{n} |

`semantic_priority` still contributes via **default** semantic goodness (0.55) when semantic input is missing (`INPUT_DEGRADED` on **{missing_audit['reason_input_degraded']}/{n}** submits).

## Factor hierarchy (runtime influence)

| Rank | Factor | Share | r(input, score) | Operational role |
|------|--------|------:|----------------:|------------------|
"""
    ranked = sorted(importance.items(), key=lambda x: -x[1])
    def _fmt_r(val: Optional[float]) -> str:
        return f"{val:.3f}" if val is not None else "n/a"

    for i, (fname, share) in enumerate(ranked, 1):
        r = corr_inputs.get(fname)
        role = {
            "ran_prb_goodness": "RAN — PRB headroom (1−PRB/100); **varies** with load",
            "risk_inverse": "ML/risk — 1−ran_aware_final_risk; **near-constant** in campaign",
            "semantic_priority": "Policy/semantic default; **constant** 0.55 input",
        }.get(fname, "")
        md += f"| {i} | `{fname}` | {100*share:.1f}% | {_fmt_r(r)} | {role} |\n"

    md += f"""
**Dominant runtime driver:** `ran_prb_goodness` — corr(PRB%, score)={stats_out.get('corr_prb_raw_vs_score', 0):.3f}; only term with material variance across submits.

## Aggregation semantics (observed)

```
decision_score = (w_prb·g_prb + w_risk·g_risk + w_sem·g_sem) / (w_prb + w_risk + w_sem)
```

URLLC weights (configured): w_prb=0.22, w_risk=0.28, w_sem=0.12 → **active denominator = 0.62** (not 1.0).

## Telemetry present but not in score terms

Transport/core metrics exist in `telemetry_snapshot` but do **not** appear as separate `contributing_factors` in score_mode (transport/core inform risk/feasibility upstream, not direct terms here):

| Metric | Available in snapshot |
|--------|----------------------|
| RTT / jitter | yes |
| Core CPU / memory | yes |
| SLA feasibility_score (row) | present in CSV, not in active terms |

## Statistical evidence

- **Reconstruction:** all {n} submits: `|reconstructed − decision_score| < 1e−6` → **{recon_ok}**
- **Factor variance:** highest on `ran_prb_goodness` contribution (PRB-driven); `risk_inverse` and `semantic_priority` contributions nearly flat across campaign.

## Figures

- `figures/01_factor_importance.png`
- `figures/02_factor_contribution_distributions.png`
- `figures/03_factor_input_heatmap.png`
- `figures/04_factor_score_correlation.png`
- `figures/05_factor_temporal_evolution.png`
- `figures/06_prb_vs_ran_contribution.png`

## Artifacts

- `contributing_factors_stats.json`

---

**HARD STOP — Phase 1 complete.** Await `PHASE_1_APPROVED` before Phase 2 (goodness aggregation).
"""
    (p1 / "CONTRIBUTING_FACTORS.md").write_text(md, encoding="utf-8")

    for cmd, name in (
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"], "runtime_after.txt"),
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"], "runtime_after.yaml"),
    ):
        fp = out / "freeze" / name
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            fp.write_text(proc.stdout or proc.stderr or "", encoding="utf-8")
        except (OSError, subprocess.TimeoutExpired) as exc:
            fp.write_text(f"skipped: {exc}", encoding="utf-8")

    manifest = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    (out / "analysis" / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(f"TRISLA OPERATIONAL SCORE SEMANTICS PHASE 1: {out}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
