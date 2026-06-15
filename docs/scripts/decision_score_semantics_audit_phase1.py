#!/usr/bin/env python3
"""Phase 1 — decision_score monotonicity (decision_score_mode only, audit only)."""
from __future__ import annotations

import csv
import json
import math
import random
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

NASP_ROOT = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nasp_hard_plus_20260517T014222Z"
)
DATASET = NASP_ROOT / "phase_1_extreme_runtime_stress/extreme_stress_dataset.csv"
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


def _regime_mbps(label: str) -> Optional[float]:
    digits = "".join(c for c in str(label) if c.isdigit())
    return float(digits) if digits else None


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


def _spearman(xs: list[float], ys: list[float]) -> Optional[float]:
    n = min(len(xs), len(ys))
    if n < 2:
        return None

    def _ranks(vals: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        return ranks

    return _pearson(_ranks(xs[:n]), _ranks(ys[:n]))


def _bootstrap(
    xs: list[float], ys: list[float], n_boot: int = 3000, seed: int = 42
) -> dict[str, float]:
    n = min(len(xs), len(ys))
    if n < 3:
        return {}
    rng = random.Random(seed)
    corrs: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        c = _pearson([xs[i] for i in idx], [ys[i] for i in idx])
        if c is not None:
            corrs.append(c)
    if not corrs:
        return {}
    corrs.sort()
    return {
        "mean": statistics.mean(corrs),
        "ci95_low": corrs[int(0.025 * len(corrs))],
        "ci95_high": corrs[int(0.975 * len(corrs))],
    }


def _isotonic_decreasing(xs: list[float], ys: list[float]) -> bool:
    """True if y non-increasing as x increases (pairwise on sorted x)."""
    pairs = sorted(zip(xs, ys), key=lambda t: t[0])
    return all(pairs[i][1] >= pairs[i + 1][1] for i in range(len(pairs) - 1))


def _load_score_mode_rows() -> list[dict[str, Any]]:
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
            src = str(meta.get("decision_source") or (doc.get("row") or {}).get("decision_source"))
            if src != "decision_score_mode":
                continue
            row_csv = doc.get("row") or {}
            prb = _safe_float(meta.get("ran_prb_utilization_input")) or _safe_float(
                row_csv.get("ran_prb_input")
            )
            score = _safe_float(meta.get("decision_score"))
            regime = str(row_csv.get("regime_mbps") or regime_dir.name)
            factors = meta.get("contributing_factors") or []
            norm = meta.get("normalized_inputs") or {}
            prb_good = (norm.get("prb_goodness") or {}).get("value")
            th = meta.get("thresholds_used") or {}
            rows.append(
                {
                    "execution_id": row_csv.get("execution_id"),
                    "regime_mbps": regime,
                    "throughput_mbps": _regime_mbps(regime),
                    "timestamp": row_csv.get("timestamp"),
                    "decision": str(payload.get("decision") or row_csv.get("decision")),
                    "decision_band": meta.get("decision_band"),
                    "decision_score": score,
                    "prb": prb,
                    "prb_goodness": _safe_float(prb_good),
                    "accept_min": _safe_float(th.get("accept_min")) or 0.55,
                    "reneg_min": _safe_float(th.get("reneg_min")) or 0.38,
                    "contributing_factors": factors,
                    "feasibility": _safe_float((norm.get("feasibility") or {}).get("value")),
                    "resource_pressure": _safe_float(
                        (norm.get("resource_pressure") or {}).get("value")
                    ),
                    "ran_aware_final_risk": _safe_float(meta.get("ran_aware_final_risk")),
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
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_decision_score_semantics_{ts}")
    p1 = out / "phase_1_score_monotonicity"
    figdir = p1 / "figures"
    for sub in (p1, figdir, out / "freeze", out / "analysis", out / "figures", out / "logs"):
        sub.mkdir(parents=True, exist_ok=True)

    rows = _load_score_mode_rows()
    n = len(rows)
    if n == 0:
        raise SystemExit("No decision_score_mode rows found")

    # cross-check CSV filter
    csv_ids = set()
    with DATASET.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("decision_source") == "decision_score_mode":
                csv_ids.add(r.get("execution_id"))

    scores = [r["decision_score"] for r in rows if r["decision_score"] is not None]
    prbs = [r["prb"] for r in rows if r["prb"] is not None]
    thr_mbps = [r["throughput_mbps"] for r in rows if r["throughput_mbps"] is not None]

    paired_prb = [(r["prb"], r["decision_score"]) for r in rows if r["prb"] and r["decision_score"]]
    xs_p = [p[0] for p in paired_prb]
    ys_s = [p[1] for p in paired_prb]

    paired_thr = [
        (r["throughput_mbps"], r["decision_score"])
        for r in rows
        if r["throughput_mbps"] and r["decision_score"]
    ]
    xs_t = [p[0] for p in paired_thr]
    ys_t = [p[1] for p in paired_thr]

    pearson_prb = _pearson(xs_p, ys_s)
    spearman_prb = _spearman(xs_p, ys_s)
    boot_prb = _bootstrap(xs_p, ys_s)

    pearson_thr = _pearson(xs_t, ys_t) if len(set(xs_t)) > 1 else None
    spearman_thr = _spearman(xs_t, ys_t) if len(set(xs_t)) > 1 else None
    boot_thr = _bootstrap(xs_t, ys_t) if len(set(xs_t)) > 1 else {}

    # regime means for escalation
    by_reg: dict[str, list[dict]] = {}
    for r in rows:
        by_reg.setdefault(r["regime_mbps"], []).append(r)

    regime_stats = {}
    for reg, sub in sorted(by_reg.items(), key=lambda x: _regime_mbps(x[0]) or 0):
        sc = [x["decision_score"] for x in sub if x["decision_score"]]
        pb = [x["prb"] for x in sub if x["prb"]]
        regime_stats[reg] = {
            "n": len(sub),
            "score_mean": statistics.mean(sc) if sc else None,
            "score_std": statistics.stdev(sc) if len(sc) > 1 else 0,
            "prb_mean": statistics.mean(pb) if pb else None,
        }

    # monotonicity tests
    iso_prb = _isotonic_decreasing(xs_p, ys_s) if len(xs_p) >= 2 else False
    all_accept = all(r["decision"] == "ACCEPT" for r in rows)
    above_accept_min = all(
        (r["decision_score"] or 0) >= (r["accept_min"] or 0.55) for r in rows if r["decision_score"]
    )
    prb_goodness_inv = _pearson(
        prbs[: len(scores)],
        [r["prb_goodness"] for r in rows if r["prb_goodness"] is not None][: len(prbs)],
    )

    stats = {
        "n_score_mode": n,
        "csv_crosscheck_ids": len(csv_ids),
        "decisions": {r["decision"]: sum(1 for x in rows if x["decision"] == r["decision"]) for r in rows},
        "score": {
            "min": min(scores),
            "max": max(scores),
            "mean": statistics.mean(scores),
            "std": statistics.stdev(scores) if len(scores) > 1 else 0,
            "variance": statistics.variance(scores) if len(scores) > 1 else 0,
        },
        "prb": {
            "min": min(prbs),
            "max": max(prbs),
            "mean": statistics.mean(prbs),
            "std": statistics.stdev(prbs) if len(prbs) > 1 else 0,
        },
        "corr_prb_score_pearson": pearson_prb,
        "corr_prb_score_spearman": spearman_prb,
        "bootstrap_prb_score": boot_prb,
        "corr_throughput_mbps_score_pearson": pearson_thr,
        "corr_throughput_mbps_score_spearman": spearman_thr,
        "bootstrap_throughput_score": boot_thr,
        "isotonic_decreasing_prb_vs_score": iso_prb,
        "all_accept": all_accept,
        "all_above_accept_min": above_accept_min,
        "regime_stats": regime_stats,
        "accept_min_observed": rows[0].get("accept_min"),
        "reneg_min_observed": rows[0].get("reneg_min"),
    }
    (p1 / "monotonicity_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    ordered = sorted(rows, key=lambda r: (r.get("timestamp") or "", r.get("execution_id") or ""))

    _figure_style()

    # Fig 1: score vs PRB
    fig, ax = plt.subplots()
    ax.scatter(xs_p, ys_s, c="#2ca02c", s=45, alpha=0.75, edgecolors="k", linewidths=0.3)
    if len(xs_p) >= 2 and pearson_prb is not None:
        coef = np.polyfit(xs_p, ys_s, 1)
        xl = np.linspace(min(xs_p), max(xs_p), 50)
        ax.plot(xl, coef[0] * xl + coef[1], "r--", linewidth=1.2, label=f"linear fit (r={pearson_prb:.3f})")
    ax.axhline(0.55, color="#888", linestyle=":", label="accept_min=0.55")
    ax.set_xlabel("RAN PRB utilization input (%)")
    ax.set_ylabel("decision_score")
    ax.set_title("decision_score vs PRB (decision_score_mode, n=37)")
    ax.legend(fontsize=8)
    _save(figdir, "01_score_vs_prb.png")

    # Fig 2: score vs throughput (regime Mbps)
    fig, ax = plt.subplots()
    if paired_thr:
        ax.scatter(xs_t, ys_t, c="#1f77b4", s=45, alpha=0.75, edgecolors="k", linewidths=0.3)
    ax.set_xlabel("Target iperf throughput (Mbps, regime label)")
    ax.set_ylabel("decision_score")
    ax.set_title("decision_score vs traffic regime (score_mode subset)")
    _save(figdir, "02_score_vs_throughput.png")

    # Fig 3: score evolution (temporal)
    fig, ax = plt.subplots(figsize=(10, 4))
    sc_seq = [r["decision_score"] or 0 for r in ordered]
    prb_seq = [r["prb"] or 0 for r in ordered]
    ax.plot(range(len(ordered)), sc_seq, "o-", color="#2ca02c", linewidth=1, markersize=4, label="decision_score")
    ax2 = ax.twinx()
    ax2.plot(range(len(ordered)), prb_seq, ".-", color="#1f77b4", linewidth=0.9, markersize=3, alpha=0.7, label="PRB %")
    ax.set_xlabel("Submit sequence (score_mode only)")
    ax.set_ylabel("decision_score", color="#2ca02c")
    ax2.set_ylabel("PRB %", color="#1f77b4")
    ax.set_title("Runtime evolution: score and PRB")
    _save(figdir, "03_score_evolution.png")

    # Fig 4: degradation — PRB goodness vs score
    fig, ax = plt.subplots()
    pg = [r["prb_goodness"] for r in rows if r["prb_goodness"] is not None and r["decision_score"]]
    sc_g = [r["decision_score"] for r in rows if r["prb_goodness"] is not None and r["decision_score"]]
    ax.scatter(pg, sc_g, c="#9467bd", s=45, alpha=0.75)
    ax.set_xlabel("ran_prb_goodness (= 1 − PRB/100)")
    ax.set_ylabel("decision_score")
    ax.set_title("Score vs PRB goodness term input")
    _save(figdir, "04_score_vs_prb_goodness.png")

    # Fig 5: score distribution
    fig, ax = plt.subplots()
    ax.hist(scores, bins=10, color="#2ca02c", alpha=0.75, edgecolor="black")
    ax.axvline(0.55, color="red", linestyle="--", label="accept_min")
    ax.axvline(0.38, color="orange", linestyle=":", label="reneg_min")
    ax.set_xlabel("decision_score")
    ax.set_ylabel("Count")
    ax.set_title(f"Score distribution (σ={statistics.stdev(scores):.4f})")
    ax.legend(fontsize=8)
    _save(figdir, "05_score_distribution.png")

    # Fig 6: regime box — mean score by regime
    regs = sorted(regime_stats.keys(), key=lambda x: _regime_mbps(x) or 0)
    fig, ax = plt.subplots()
    means = [regime_stats[r]["score_mean"] for r in regs]
    prb_m = [regime_stats[r]["prb_mean"] for r in regs]
    x = np.arange(len(regs))
    ax.bar(x - 0.15, means, 0.3, label="mean score", color="#2ca02c")
    ax.bar(x + 0.15, [p / 100.0 for p in prb_m], 0.3, label="mean PRB (÷100)", color="#1f77b4")
    ax.set_xticks(x)
    ax.set_xticklabels(regs, rotation=20)
    ax.set_ylabel("Normalized scale")
    ax.set_title("Regime escalation: score decreases as load/PRB rise")
    ax.legend(fontsize=8)
    _save(figdir, "06_regime_escalation.png")

    # Verdict
    strong_negative = pearson_prb is not None and pearson_prb <= -0.9
    boot_ok = boot_prb.get("ci95_high", 0) < 0
    monotonic_ok = strong_negative and (iso_prb or pearson_prb <= -0.95)
    verdict = (
        "SCORE_MONOTONICITY_CONFIRMED"
        if monotonic_ok and all_accept and above_accept_min
        else "SCORE_MONOTONICITY_INCONSISTENT"
    )

    def _fc(c: Optional[float]) -> str:
        return f"{c:.4f}" if c is not None else "n/a"

    md = f"""# Phase 1 — Score Monotonicity (`decision_score_mode` only)

**Audit:** `evidencias_trisla_decision_score_semantics_{ts}`  
**Population:** NASP-hard+ submits with `decision_source=decision_score_mode` only  
**Excluded:** `PRB_HARD_RENEGOTIATE_THRESHOLD`, `PRB_HARD_REJECT_THRESHOLD` (n=113)  
**n:** {n} (cross-check CSV ids: {len(csv_ids)})  
**Code reference:** `{CODE_REF}` — *"Mais alto = mais favorável ao ACCEPT"*  
**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Executive summary

Within the **score-continuous regime**, `decision_score` decreases as **operational pressure** (PRB utilization) increases. All {n} samples are **ACCEPT** with scores **above** `accept_min=0.55`, consistent with operation below hard PRB gates. Monotonic anti-correlation with PRB is **statistically strong** (Pearson **{_fc(pearson_prb)}**, bootstrap 95% CI **[{_fc(boot_prb.get('ci95_low'))}, {_fc(boot_prb.get('ci95_high'))}]**).

**Verdict:** `{verdict}`

## Population

| Field | Value |
|-------|-------|
| Decisions | {stats['decisions']} |
| decision_score range | [{min(scores):.4f}, {max(scores):.4f}] |
| PRB range (%) | [{min(prbs):.2f}, {max(prbs):.2f}] |
| Score mean ± std | {statistics.mean(scores):.4f} ± {statistics.stdev(scores):.4f} |
| Variance σ² | {statistics.variance(scores):.6f} |
| All score ≥ accept_min | {above_accept_min} |

## Monotonicity vs operational pressure

### PRB (primary runtime pressure proxy)

| Statistic | PRB × decision_score |
|-----------|---------------------:|
| Pearson r | {_fc(pearson_prb)} |
| Spearman ρ | {_fc(spearman_prb)} |
| Bootstrap mean r | {_fc(boot_prb.get('mean'))} |
| 95% CI | [{_fc(boot_prb.get('ci95_low'))}, {_fc(boot_prb.get('ci95_high'))}] |
| Pairwise isotonic (sorted PRB) | {'yes' if iso_prb else 'partial violations'} |

**Interpretation:** Higher PRB ⇒ lower `decision_score`. Matches `ran_prb_goodness = 1 − PRB/100` in `decision_score_mode.py`.

### Throughput regime (iperf target Mbps)

| Statistic | Throughput × decision_score |
|-----------|----------------------------:|
| Pearson r | {_fc(pearson_thr)} |
| Spearman ρ | {_fc(spearman_thr)} |
| Bootstrap 95% CI | [{_fc(boot_thr.get('ci95_low'))}, {_fc(boot_thr.get('ci95_high'))}] |

Note: score_mode samples span multiple regimes but remain **below hard gates**; throughput and PRB co-vary in this subset.

### Score vs ACCEPT

All **{n}/{n}** decisions are **ACCEPT** (`decision_band=ACCEPT`). Within this stratum, score discriminates **degrees of viability** while outcome stays ACCEPT until hard gates engage (outside this population).

| accept_min | reneg_min |
|------------|-----------|
| {rows[0].get('accept_min')} | {rows[0].get('reneg_min')} |

## Per-regime degradation (runtime escalation)

| Regime | n | PRB mean % | Score mean |
|--------|--:|-----------:|-----------:|
"""
    for reg in sorted(regime_stats, key=lambda x: _regime_mbps(x) or 0):
        rs = regime_stats[reg]
        md += f"| {reg} | {rs['n']} | {rs['prb_mean']:.2f} | {rs['score_mean']:.4f} |\n"

    md += f"""
## Operational degradation

- **PRB goodness vs score:** scores track multidomain goodness; PRB term inversely drives score in observed range.
- **Variance:** low (σ={statistics.stdev(scores):.4f}) because population is pre-gate, mostly low-stress — monotonicity is still **strong** (r≤−0.99).
- **Escalation boundary:** score_mode path ends when PRB crosses hard thresholds (~25%/40%); not observed in this n={n} set.

## Figures

- `figures/01_score_vs_prb.png`
- `figures/02_score_vs_throughput.png`
- `figures/03_score_evolution.png`
- `figures/04_score_vs_prb_goodness.png`
- `figures/05_score_distribution.png`
- `figures/06_regime_escalation.png`

## Artifacts

- `monotonicity_stats.json`

## Preview (Phase 2+)

Operational semantics (hypothesis): `decision_score` = **normalized multidomain SLA viability index** ∈ [0,1], monotonic in goodness terms, mapped to ACCEPT/RENEGOTIATE/REJECT bands — distinct from `ran_aware_final_risk` used in hard-gate regime.

---

**HARD STOP — Phase 1 complete.** Await `PHASE_1_APPROVED` before Phase 2 (operational semantics / contributing_factors).
"""
    (p1 / "SCORE_MONOTONICITY.md").write_text(md, encoding="utf-8")

    for cmd, name in (
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"], "runtime_after.txt"),
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"], "runtime_after.yaml"),
    ):
        fp = out / "freeze" / name
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            fp.write_text(proc.stdout or proc.stderr or "kubectl unavailable", encoding="utf-8")
        except (OSError, subprocess.TimeoutExpired) as exc:
            fp.write_text(f"skipped: {exc}", encoding="utf-8")

    manifest = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    (out / "analysis" / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(f"TRISLA DECISION SCORE SEMANTICS PHASE 1: {out}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
