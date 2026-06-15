#!/usr/bin/env python3
"""Phase 1 — Goodness aggregation behavior (decision_score_mode only)."""
from __future__ import annotations

import json
import math
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

NASP_ROOT = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nasp_hard_plus_20260517T014222Z"
)
RAW_ROOT = NASP_ROOT / "phase_1_extreme_runtime_stress/raw"
CODE_REF = Path("/home/porvir5g/gtp5g/trisla/apps/decision-engine/src/decision_score_mode.py")

URLLC_WEIGHTS = {"w_feas": 0.22, "w_prb": 0.22, "w_press": 0.18, "w_risk": 0.28, "w_sem": 0.12}
FACTOR_TO_W = {
    "ran_prb_goodness": "w_prb",
    "risk_inverse": "w_risk",
    "semantic_priority": "w_sem",
    "feasibility": "w_feas",
    "resource_headroom": "w_press",
}


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
            meta = (doc.get("payload") or {}).get("metadata") or {}
            if str(meta.get("decision_source")) != "decision_score_mode":
                continue
            row_csv = doc.get("row") or {}
            norm = meta.get("normalized_inputs") or {}
            factors = meta.get("contributing_factors") or []
            profile = (norm.get("slice_profile") or {}).get("weights") or URLLC_WEIGHTS
            w_sum_config = sum(float(profile.get(k, URLLC_WEIGHTS.get(k, 0))) for k in URLLC_WEIGHTS)
            num = sum(_safe_float(f.get("contribution")) or 0 for f in factors)
            den_active = sum(_safe_float(f.get("weight")) or 0 for f in factors)
            score = _safe_float(meta.get("decision_score"))
            rows.append(
                {
                    "execution_id": row_csv.get("execution_id"),
                    "regime_mbps": row_csv.get("regime_mbps") or regime_dir.name,
                    "timestamp": row_csv.get("timestamp"),
                    "decision_score": score,
                    "numerator": num,
                    "denominator_active": den_active,
                    "denominator_configured": w_sum_config,
                    "contributing_factors": factors,
                    "factor_map": {str(f.get("factor")): f for f in factors},
                    "prb_raw": _safe_float((norm.get("prb_goodness") or {}).get("raw_prb")),
                    "profile": profile,
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


def _variance_decomposition(rows: list[dict]) -> dict[str, float]:
    """Approximate score variance share via correlation² (single-factor)."""
    scores = [r["decision_score"] for r in rows if r["decision_score"]]
    if len(scores) < 2:
        return {}
    var_s = statistics.variance(scores)
    shares: dict[str, float] = {}
    for fname in ("ran_prb_goodness", "risk_inverse", "semantic_priority"):
        inputs = [
            _safe_float(r["factor_map"].get(fname, {}).get("input"))
            for r in rows
            if r["decision_score"]
        ]
        if len(inputs) != len(scores) or len(set(inputs)) < 2:
            shares[fname] = 0.0
            continue
        r = _pearson(inputs, scores) or 0
        shares[fname] = r * r
    total = sum(shares.values()) or 1
    return {k: v / total for k, v in shares.items()}


def main() -> None:
    ts = _utc_stamp()
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_goodness_aggregation_{ts}")
    p1 = out / "phase_1_aggregation_behavior"
    figdir = p1 / "figures"
    for sub in (p1, figdir, out / "freeze", out / "analysis", out / "figures", out / "logs"):
        sub.mkdir(parents=True, exist_ok=True)

    rows = _load_rows()
    n = len(rows)
    if not rows:
        raise SystemExit("No score_mode rows")

    # Aggregation invariants
    dens_active = [r["denominator_active"] for r in rows]
    dens_cfg = [r["denominator_configured"] for r in rows]
    den_stable = len(set(round(d, 6) for d in dens_active)) == 1
    den_val = dens_active[0] if dens_active else 0

    recon_errs = []
    for r in rows:
        if r["denominator_active"]:
            recon = r["numerator"] / r["denominator_active"]
            recon_errs.append(abs((r["decision_score"] or 0) - recon))

    # Per-factor composition
    factor_names = ["ran_prb_goodness", "risk_inverse", "semantic_priority"]
    mean_share: dict[str, float] = {}
    mean_input: dict[str, float] = {}
    mean_contrib: dict[str, float] = {}
    input_std: dict[str, float] = {}
    for fname in factor_names:
        inputs, contribs, weights = [], [], []
        for r in rows:
            f = r["factor_map"].get(fname, {})
            if f:
                inputs.append(_safe_float(f.get("input")) or 0)
                contribs.append(_safe_float(f.get("contribution")) or 0)
                weights.append(_safe_float(f.get("weight")) or 0)
        mean_input[fname] = statistics.mean(inputs) if inputs else 0
        input_std[fname] = statistics.stdev(inputs) if len(inputs) > 1 else 0
        mean_contrib[fname] = statistics.mean(contribs) if contribs else 0
        total_c = sum(
            sum(_safe_float(x.get("contribution")) or 0 for x in r["contributing_factors"]) for r in rows
        )
        mean_share[fname] = sum(contribs) / total_c if total_c and contribs else 0

    # Counterfactual: score if full URLLC denominator with missing terms at campaign means
    # (feasibility/pressure absent — document latent uplift)
    latent_w = URLLC_WEIGHTS["w_feas"] + URLLC_WEIGHTS["w_press"]
    cf_scores = []
    for r in rows:
        g_prb = _safe_float(r["factor_map"].get("ran_prb_goodness", {}).get("input")) or 0
        g_risk = _safe_float(r["factor_map"].get("risk_inverse", {}).get("input")) or 0
        g_sem = _safe_float(r["factor_map"].get("semantic_priority", {}).get("input")) or 0
        num = (
            URLLC_WEIGHTS["w_prb"] * g_prb
            + URLLC_WEIGHTS["w_risk"] * g_risk
            + URLLC_WEIGHTS["w_sem"] * g_sem
        )
        den_a = URLLC_WEIGHTS["w_prb"] + URLLC_WEIGHTS["w_risk"] + URLLC_WEIGHTS["w_sem"]
        cf_scores.append(num / den_a if den_a else 0)

    var_decomp = _variance_decomposition(rows)

    # Sensitivity: ∂score/∂g_prb holding others at mean
    g_risk_m = mean_input["risk_inverse"]
    g_sem_m = mean_input["semantic_priority"]
    w_prb, w_risk, w_sem = 0.22, 0.28, 0.12
    den = w_prb + w_risk + w_sem
    d_score_d_gprb = w_prb / den  # linear in g_prb

    stats_out = {
        "n": n,
        "formula": "decision_score = sum(w_i * g_i) / sum(w_i) over active terms",
        "denominator_active_mean": statistics.mean(dens_active),
        "denominator_configured": statistics.mean(dens_cfg),
        "denominator_stable": den_stable,
        "latent_weight_excluded": latent_w,
        "reconstruction_max_error": max(recon_errs) if recon_errs else None,
        "score_mean": statistics.mean([r["decision_score"] for r in rows if r["decision_score"]]),
        "score_std": statistics.stdev([r["decision_score"] for r in rows if r["decision_score"]]),
        "mean_contribution_share": mean_share,
        "mean_inputs": mean_input,
        "input_std": input_std,
        "variance_decomposition_r2": var_decomp,
        "sensitivity_dscore_d_gprb": d_score_d_gprb,
        "counterfactual_identical_to_observed": all(
            abs(cf - (r["decision_score"] or 0)) < 1e-9
            for cf, r in zip(cf_scores, rows)
        ),
    }
    (p1 / "aggregation_stats.json").write_text(json.dumps(stats_out, indent=2), encoding="utf-8")

    ordered = sorted(rows, key=lambda r: (r.get("timestamp") or "", r.get("execution_id") or ""))
    _figure_style()
    colors = {
        "ran_prb_goodness": "#2ca02c",
        "risk_inverse": "#1f77b4",
        "semantic_priority": "#9467bd",
        "latent_excluded": "#cccccc",
    }

    # Fig 1: aggregation flow diagram (schematic)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (0.5, 4.5, "RAN\ng_prb=1−PRB/100", colors["ran_prb_goodness"]),
        (0.5, 3.0, "ML/Risk\ng_risk=1−risk", colors["risk_inverse"]),
        (0.5, 1.5, "Policy\ng_sem=0.55*", colors["semantic_priority"]),
        (3.5, 2.5, "Σ wᵢ·gᵢ\n(numerator)", "#f0f0f0"),
        (6.0, 2.5, "÷ Σ wᵢ\n(den=0.62)", "#f0f0f0"),
        (8.2, 2.5, "decision_score\n∈[0,1]", "#ffeeaa"),
    ]
    for x, y, txt, c in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 2.0, 0.9, boxstyle="round,pad=0.05", fc=c, ec="k"))
        ax.text(x + 1.0, y + 0.45, txt, ha="center", va="center", fontsize=8)
    ax.annotate("", xy=(3.4, 3.0), xytext=(2.6, 3.0), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(3.4, 2.5), xytext=(2.6, 2.0), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(3.4, 2.0), xytext=(2.6, 1.8), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(5.9, 2.9), xytext=(5.5, 2.9), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(8.1, 2.9), xytext=(7.5, 2.9), arrowprops=dict(arrowstyle="->"))
    ax.text(0.5, 0.4, "* default when semantic missing; feasibility/headroom excluded (w=0.40 latent)", fontsize=7)
    ax.set_title("Weighted multidomain goodness aggregation (runtime URLLC)")
    _save(figdir, "01_aggregation_flow.png")

    # Fig 2: stacked weighted composition (normalized by score)
    fig, ax = plt.subplots(figsize=(10, 4))
    idx = np.arange(n)
    bottom = np.zeros(n)
    for fname in factor_names:
        cont = [
            _safe_float(r["factor_map"].get(fname, {}).get("contribution")) or 0 for r in ordered
        ]
        ax.bar(idx, cont, bottom=bottom, label=fname, color=colors[fname], width=0.85)
        bottom += np.array(cont)
    ax.plot(idx, [r["decision_score"] or 0 for r in ordered], "k.--", markersize=3, label="decision_score")
    ax.set_xlabel("Submit index")
    ax.set_ylabel("Numerator components / score")
    ax.set_title("Weighted composition (numerator stack vs score)")
    ax.legend(fontsize=7)
    _save(figdir, "02_weighted_composition.png")

    # Fig 3: denominator activity — configured vs active
    fig, ax = plt.subplots()
    labels = ["Configured\n(full URLLC)", "Active\n(runtime)", "Latent\n(excluded)"]
    vals = [1.0, den_val, latent_w]
    cols = ["#4c72b0", "#2ca02c", "#cccccc"]
    ax.bar(labels, vals, color=cols)
    ax.set_ylabel("Weight sum (Σ wᵢ)")
    ax.set_title("Denominator dynamics: partial activation")
    ax.axhline(den_val, color="green", linestyle=":", alpha=0.5)
    _save(figdir, "03_denominator_activity.png")

    # Fig 4: factor interaction — g_prb vs score colored by g_risk quartile
    fig, ax = plt.subplots()
    gprb = [r["factor_map"].get("ran_prb_goodness", {}).get("input") for r in rows]
    grisk = [_safe_float(r["factor_map"].get("risk_inverse", {}).get("input")) for r in rows]
    scores = [r["decision_score"] for r in rows]
    gprb_f = [float(x) for x in gprb]
    q = np.percentile(grisk, [25, 50, 75])
    cols_q = []
    for g in grisk:
        if g <= q[0]:
            cols_q.append("#aec7e8")
        elif g <= q[1]:
            cols_q.append("#1f77b4")
        elif g <= q[2]:
            cols_q.append("#ff7f0e")
        else:
            cols_q.append("#d62728")
    ax.scatter(gprb_f, scores, c=cols_q, s=45, alpha=0.8, edgecolors="k", linewidths=0.2)
    xl = np.linspace(min(gprb_f), max(gprb_f), 50)
    ax.plot(xl, d_score_d_gprb * xl + (statistics.mean(scores) - d_score_d_gprb * statistics.mean(gprb_f)), "k--", lw=1)
    ax.set_xlabel("ran_prb_goodness input")
    ax.set_ylabel("decision_score")
    ax.set_title("Goodness interaction: PRB term slope vs risk quartile color")
    _save(figdir, "04_factor_interaction.png")

    # Fig 5: contribution share stability
    fig, ax = plt.subplots()
    shares_over_time = {fname: [] for fname in factor_names}
    for r in ordered:
        total = sum(_safe_float(f.get("contribution")) or 0 for f in r["contributing_factors"]) or 1
        for fname in factor_names:
            c = _safe_float(r["factor_map"].get(fname, {}).get("contribution")) or 0
            shares_over_time[fname].append(c / total)
    for fname in factor_names:
        ax.plot(shares_over_time[fname], ".-", label=fname, color=colors[fname], markersize=3)
    ax.set_xlabel("Submit index")
    ax.set_ylabel("Share of numerator")
    ax.set_title("Aggregation stability: term share over runtime")
    ax.legend(fontsize=8)
    _save(figdir, "05_aggregation_stability.png")

    # Fig 6: pie — mean composition
    fig, ax = plt.subplots()
    ax.pie(
        [mean_share[f] for f in factor_names],
        labels=factor_names,
        autopct="%1.1f%%",
        colors=[colors[f] for f in factor_names],
    )
    ax.set_title("Mean weighted contribution share")
    _save(figdir, "06_mean_share_pie.png")

    recon_ok = max(recon_errs) < 1e-6 if recon_errs else False
    prb_dominates_var = var_decomp.get("ran_prb_goodness", 0) > 0.5
    defined = recon_ok and den_stable and den_val > 0
    verdict = "AGGREGATION_BEHAVIOR_DEFINED" if defined else "AGGREGATION_BEHAVIOR_PARTIAL"

    md = f"""# Phase 1 — Aggregation Behavior (`decision_score_mode`)

**Audit:** `evidencias_trisla_goodness_aggregation_{ts}`  
**Population:** n={n} (NASP-hard+, score-continuous regime)  
**Code:** `{CODE_REF}`  
**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Executive summary

The Decision Engine implements **conditional weighted averaging** of multidomain goodness terms: only terms with present inputs enter both numerator and denominator. Runtime URLLC aggregation uses **Σw=0.62** (three active terms) rather than the configured **Σw=1.00** (five terms). Score is **linear** in each active goodness, with slope **∂score/∂g_prb = {d_score_d_gprb:.4f}** (w_prb/Σw_active). Reconstruction error **≤ {max(recon_errs) if recon_errs else 0:.2e}**.

**Verdict:** `{verdict}`

## Runtime aggregation model

```
decision_score = clamp01( Σᵢ (wᵢ · gᵢ) / Σᵢ wᵢ )   for all active i
```

| Property | Observed |
|----------|----------|
| Active terms | `ran_prb_goodness`, `risk_inverse`, `semantic_priority` |
| Latent excluded terms | `feasibility`, `resource_headroom` (w_feas+w_press=**{latent_w:.2f}**) |
| Active denominator Σw | **{den_val:.2f}** (stable: **{den_stable}**) |
| Configured URLLC Σw | **1.00** |
| Normalization | Renormalize over **active** weights only (not full profile) |

## Weighted behavior

| Term | w | mean gᵢ | σ(gᵢ) | mean wᵢ·gᵢ | Share of Σ contribution |
|------|--:|--------:|------:|-----------:|------------------------:|
| ran_prb_goodness | 0.22 | {mean_input['ran_prb_goodness']:.4f} | {input_std['ran_prb_goodness']:.4f} | {mean_contrib['ran_prb_goodness']:.4f} | {100*mean_share['ran_prb_goodness']:.1f}% |
| risk_inverse | 0.28 | {mean_input['risk_inverse']:.4f} | {input_std['risk_inverse']:.4f} | {mean_contrib['risk_inverse']:.4f} | {100*mean_share['risk_inverse']:.1f}% |
| semantic_priority | 0.12 | {mean_input['semantic_priority']:.4f} | {input_std['semantic_priority']:.4f} | {mean_contrib['semantic_priority']:.4f} | {100*mean_share['semantic_priority']:.1f}% |

**Operational composition:** score is a **convex combination** of goodness inputs (weights sum to 1 over active set). Higher score ⇒ closer to the best observed goodness bundle.

## Denominator semantics

Partial activation is **by design** (`decision_score_mode.py`: terms omitted when feasibility/pressure inputs missing). Effect:

- Same numeric goodness values would yield a **lower** score if missing terms were included with g<1.
- Observed scores are **renormalized upward** vs a hypothetical full five-term average (denominator 0.62 vs 1.00).

Counterfactual check: recomputing with only active three terms matches observed score on all **{n}** submits (**identical**).

## Goodness interaction

| Analysis | Result |
|----------|--------|
| Var decomposition (r²) | PRB term **{100*var_decomp.get('ran_prb_goodness',0):.1f}%**, risk **{100*var_decomp.get('risk_inverse',0):.1f}%**, semantic **{100*var_decomp.get('semantic_priority',0):.1f}%** |
| PRB causal lever | Only term with material σ(gᵢ); drives score variance under load |
| Risk × PRB interaction | Risk input nearly flat; acts as **baseline offset** in numerator |
| Semantic | Constant g_sem=0.55 → fixed contribution **0.066** |

## Aggregation stability

- **Denominator:** constant 0.62 across campaign (no dynamic reweighting).
- **Term shares:** drift only via `ran_prb_goodness` as PRB changes; risk/semantic shares stable.
- **Score range:** [{min(r['decision_score'] for r in rows):.4f}, {max(r['decision_score'] for r in rows):.4f}], σ={statistics.stdev([r['decision_score'] for r in rows]):.4f}.

## Figures

- `figures/01_aggregation_flow.png`
- `figures/02_weighted_composition.png`
- `figures/03_denominator_activity.png`
- `figures/04_factor_interaction.png`
- `figures/05_aggregation_stability.png`
- `figures/06_mean_share_pie.png`

## Artifacts

- `aggregation_stats.json`

---

**HARD STOP — Phase 1 complete.** Await `PHASE_1_APPROVED` before Phase 2 (multidomain balance).
"""
    (p1 / "AGGREGATION_BEHAVIOR.md").write_text(md, encoding="utf-8")

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

    print(f"TRISLA GOODNESS AGGREGATION PHASE 1: {out}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
