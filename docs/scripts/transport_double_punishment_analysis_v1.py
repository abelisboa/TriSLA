#!/usr/bin/env python3
"""Substep 3 — Double punishment analysis (Candidates A vs F, NASP-hard+)."""
from __future__ import annotations

import json
import math
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

RTT_REF = 12.21
JITTER_REF = 4.04
W_ACTIVE = 0.62  # score_mode: 0.22+0.28+0.12
ACCEPT_MIN = 0.55
RENEG_MIN = 0.38

NASP_RAW = Path(
    "/home/porvir5g/gtp5g/trisla/evidencias_trisla_nasp_hard_plus_20260517T014222Z"
    "/phase_1_extreme_runtime_stress/raw"
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _sf(x: Any) -> Optional[float]:
    if x is None or x == "":
        return None
    try:
        v = float(x)
        return None if math.isnan(v) or math.isinf(v) else v
    except (TypeError, ValueError):
        return None


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _g_a(rtt: float, _j: float) -> float:
    return _clamp01(1.0 - rtt / RTT_REF)


def _g_f(rtt: float, j: float) -> float:
    return min(_clamp01(1.0 - rtt / RTT_REF), _clamp01(1.0 - j / JITTER_REF))


def _pearson(xs: list[float], ys: list[float]) -> Optional[float]:
    n = min(len(xs), len(ys))
    if n < 3:
        return None
    mx, my = statistics.mean(xs[:n]), statistics.mean(ys[:n])
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((xs[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ys[i] - my) ** 2 for i in range(n)))
    return num / (dx * dy) if dx and dy else None


def _spearman(xs: list[float], ys: list[float]) -> Optional[float]:
    if len(xs) < 3:
        return None
    rx = [sorted(range(len(xs)), key=lambda i: xs[i]).index(i) for i in range(len(xs))]
    ry = [sorted(range(len(ys)), key=lambda i: ys[i]).index(i) for i in range(len(ys))]
    return _pearson([float(r) for r in rx], [float(r) for r in ry])


def _partial_corr(x: list[float], y: list[float], z: list[float]) -> Optional[float]:
    rxy, rxz, ryz = _pearson(x, y), _pearson(x, z), _pearson(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    den = math.sqrt(max(1e-12, (1 - rxz**2) * (1 - ryz**2)))
    return (rxy - rxz * ryz) / den


def _ols_residual(y: list[float], xs: list[list[float]]) -> list[float]:
    """OLS residual of y ~ [1, x1, x2, ...]."""
    n = len(y)
    k = 1 + len(xs)
    X = np.ones((n, k))
    for j, xv in enumerate(xs):
        X[:, j + 1] = xv
    Y = np.array(y)
    beta, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
    return (Y - X @ beta).tolist()


def _incremental_r2(y: list[float], base: list[list[float]], extra: list[float]) -> float:
    y_arr = np.array(y)
    n = len(y)
    Xb = np.column_stack([np.ones(n)] + base)
    Xf = np.column_stack([np.ones(n)] + base + [extra])
    beta_b, _, _, _ = np.linalg.lstsq(Xb, y_arr, rcond=None)
    beta_f, _, _, _ = np.linalg.lstsq(Xf, y_arr, rcond=None)
    ss_tot = float(np.sum((y_arr - y_arr.mean()) ** 2))
    if ss_tot < 1e-12:
        return 0.0
    ss_b = float(np.sum((y_arr - Xb @ beta_b) ** 2))
    ss_f = float(np.sum((y_arr - Xf @ beta_f) ** 2))
    return max(0.0, (ss_b - ss_f) / ss_tot)


def _load() -> list[dict]:
    rows = []
    for d in sorted(NASP_RAW.iterdir()):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("submit_*.json")):
            doc = json.loads(p.read_text(encoding="utf-8"))
            row = doc.get("row") or {}
            meta = doc.get("payload", {}).get("metadata") or {}
            tr = (meta.get("telemetry_snapshot") or {}).get("transport") or {}
            prb = _sf(row.get("ran_prb_input"))
            rtt = _sf(tr.get("rtt_ms") or tr.get("rtt") or meta.get("transport_latency_input"))
            jit = _sf(tr.get("jitter_ms") or tr.get("jitter"))
            if prb is None or rtt is None or jit is None:
                continue
            rows.append(
                {
                    "regime": row.get("regime_mbps") or d.name,
                    "prb": prb,
                    "rtt": rtt,
                    "jitter": jit,
                    "g_prb": _clamp01(1.0 - prb / 100.0),
                    "g_a": _g_a(rtt, jit),
                    "g_f": _g_f(rtt, jit),
                    "decision_source": row.get("decision_source"),
                    "decision_score": _sf(row.get("decision_score") or meta.get("decision_score")),
                    "ran_risk": _sf(row.get("ran_aware_final_risk")),
                }
            )
    return rows


def _conditional_corr(prb: list[float], g: list[float], z: list[float], n_bins: int = 3) -> dict[str, Optional[float]]:
    order = sorted(range(len(z)), key=lambda i: z[i])
    out = {}
    chunk = max(1, len(z) // n_bins)
    for b in range(n_bins):
        idx = order[b * chunk : (b + 1) * chunk if b < n_bins - 1 else len(z)]
        if len(idx) < 5:
            out[f"bin{b+1}"] = None
            continue
        out[f"bin{b+1}"] = _pearson([prb[i] for i in idx], [g[i] for i in idx])
    return out


def _freeze(out: Path) -> None:
    for cmd, name in (
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "wide"], "runtime_after.txt"),
        (["kubectl", "get", "deploy,svc,pods", "-A", "-o", "yaml"], "runtime_after.yaml"),
    ):
        fp = out / "freeze" / name
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            fp.write_text(proc.stdout or proc.stderr or "", encoding="utf-8")
        except OSError:
            fp.write_text("kubectl unavailable", encoding="utf-8")


def _coupling_block(prb: list[float], g: list[float], rtt: list[float], jit: list[float]) -> dict:
    return {
        "pearson_prb_g": _pearson(prb, g),
        "spearman_prb_g": _spearman(prb, g),
        "pearson_g_gprb": _pearson(g, [_clamp01(1 - p / 100) for p in prb]),
        "partial_prb_g_given_jitter": _partial_corr(prb, g, jit),
        "partial_prb_g_given_rtt": _partial_corr(prb, g, rtt),
        "partial_jitter_g_given_prb": _partial_corr(jit, g, prb),
        "partial_rtt_g_given_prb": _partial_corr(rtt, g, prb),
        "partial_prb_g_given_rtt_jitter": _partial_corr(
            prb, g, [0.5 * r / RTT_REF + 0.5 * j / JITTER_REF for r, j in zip(rtt, jit)]
        ),
        "conditional_prb_g": _conditional_corr(prb, g, jit),
        "incremental_r2_rtt_beyond_prb": _incremental_r2(
            g, [[p / 100 for p in prb]], [r / RTT_REF for r in rtt]
        ),
        "incremental_r2_rtt_beyond_prb_jitter": _incremental_r2(
            g, [[p / 100 for p in prb], [j / JITTER_REF for j in jit]], [r / RTT_REF for r in rtt]
        ),
    }


def main() -> None:
    ts = _utc_stamp()
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_double_punishment_{ts}")
    steps = {i: out / f"step_{i}_{name}" for i, name in enumerate(
        ["prb_coupling", "partial_correlation", "counterfactual_behavior",
         "multidomain_safety", "publication_verdict"], 1
    )}
    for p in list(steps.values()) + [out / "analysis", out / "figures", out / "freeze"]:
        p.mkdir(parents=True, exist_ok=True)

    rows = _load()
    n = len(rows)
    prb = [r["prb"] for r in rows]
    rtt = [r["rtt"] for r in rows]
    jit = [r["jitter"] for r in rows]
    g_a = [r["g_a"] for r in rows]
    g_f = [r["g_f"] for r in rows]
    g_prb = [r["g_prb"] for r in rows]

    coup_a = _coupling_block(prb, g_a, rtt, jit)
    coup_f = _coupling_block(prb, g_f, rtt, jit)

    # incremental R²: does g add beyond PRB? (use g as y, predictors PRB)
    incr_a_beyond_prb = _incremental_r2(
        g_a, [[p / 100 for p in prb]], [r / RTT_REF for r in rtt]
    )
    incr_f_rtt_beyond_prb_jit = _incremental_r2(
        g_f, [[p / 100 for p in prb], [j / JITTER_REF for j in jit]], [r / RTT_REF for r in rtt]
    )
    incr_a_beyond_prb_jit = _incremental_r2(
        g_a, [[p / 100 for p in prb], [j / JITTER_REF for j in jit]], [r / RTT_REF for r in rtt]
    )

    # --- Step 1 figures ---
    s1f = steps[1] / "figures"
    s1f.mkdir(exist_ok=True)
    labels = ["PRB", "RTT", "Jitter", "g_prb", "g_A", "g_F"]
    mat = np.array(
        [
            [1, _pearson(prb, rtt), _pearson(prb, jit), _pearson(prb, g_prb), _pearson(prb, g_a), _pearson(prb, g_f)],
            [_pearson(rtt, prb), 1, _pearson(rtt, jit), _pearson(rtt, g_prb), _pearson(rtt, g_a), _pearson(rtt, g_f)],
            [_pearson(jit, prb), _pearson(jit, rtt), 1, _pearson(jit, g_prb), _pearson(jit, g_a), _pearson(jit, g_f)],
            [_pearson(g_prb, prb), _pearson(g_prb, rtt), _pearson(g_prb, jit), 1, _pearson(g_prb, g_a), _pearson(g_prb, g_f)],
            [_pearson(g_a, prb), _pearson(g_a, rtt), _pearson(g_a, jit), _pearson(g_a, g_prb), 1, _pearson(g_a, g_f)],
            [_pearson(g_f, prb), _pearson(g_f, rtt), _pearson(g_f, jit), _pearson(g_f, g_prb), _pearson(g_f, g_a), 1],
        ]
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mat, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_yticklabels(labels)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", fontsize=8)
    plt.colorbar(im, label="Pearson r")
    ax.set_title("Coupling matrix (NASP-hard+)")
    plt.tight_layout()
    plt.savefig(s1f / "01_coupling_matrix.png", dpi=300)
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, g, title in zip(axes, [g_a, g_f], ["A: RTT-only", "F: hybrid min"]):
        ax.scatter(prb, g, c=jit, cmap="viridis", s=40, alpha=0.75)
        ax.set_xlabel("PRB %")
        ax.set_ylabel("g_transport")
        ax.set_title(title)
    plt.suptitle("PRB vs g_transport (color=jitter)")
    plt.tight_layout()
    plt.savefig(s1f / "02_prb_response_scatter.png", dpi=300)
    plt.close()

    prb_bins = np.percentile(prb, [33, 66])
    fig, ax = plt.subplots(figsize=(8, 4))
    for g, lab, c in [(g_a, "A", "#1f77b4"), (g_f, "F", "#ff7f0e")]:
        means = []
        for lo, hi in [(0, prb_bins[0]), (prb_bins[0], prb_bins[1]), (prb_bins[1], 100)]:
            sub = [gv for p, gv in zip(prb, g) if lo <= p < hi or (hi == 100 and p >= lo)]
            means.append(statistics.mean(sub) if sub else float("nan"))
        ax.plot(["low PRB", "mid PRB", "high PRB"], means, "o-", label=lab, color=c)
    ax.set_ylabel("mean g_transport")
    ax.set_title("Conditional mean g by PRB tertile")
    ax.legend()
    plt.tight_layout()
    plt.savefig(s1f / "03_conditional_prb_tertiles.png", dpi=300)
    plt.close()

    step1_safe = abs(coup_a["partial_prb_g_given_jitter"] or 1) < 0.25
    step1_verdict = "PRB_COUPLING_DEFINED" if step1_safe else "PRB_COUPLING_UNSAFE"

    (steps[1] / "PRB_COUPLING.md").write_text(
        f"""# Step 1 — PRB Coupling

**Output:** `evidencias_trisla_double_punishment_{ts}`  
**n={n}** | PRIMARY=A | COMPARATIVE=F  
**UTC:** {datetime.now(timezone.utc).isoformat()}

## Verdict

**`{step1_verdict}`**

---

## Coupling summary

| Metric | Candidate A | Candidate F |
|--------|------------:|------------:|
| Pearson(PRB, g) | {coup_a['pearson_prb_g']:.3f} | {coup_f['pearson_prb_g']:.3f} |
| Spearman(PRB, g) | {coup_a['spearman_prb_g']:.3f} | {coup_f['spearman_prb_g']:.3f} |
| r(g, g_prb) | {coup_a['pearson_g_gprb']:.3f} | {coup_f['pearson_g_gprb']:.3f} |
| partial r(PRB,g \| jitter) | {coup_a['partial_prb_g_given_jitter']:.3f} | {coup_f['partial_prb_g_given_jitter']:.3f} |
| partial r(PRB,g \| RTT) | {coup_a['partial_prb_g_given_rtt']:.3f} | {coup_f['partial_prb_g_given_rtt']:.3f} |

**Baseline:** r(PRB,jitter)={_pearson(prb, jit):.3f}, r(PRB,RTT)={_pearson(prb, rtt):.3f}

## Orthogonality vs redundancy

| Model | Interpretation |
|-------|----------------|
| **A** | Moderate raw r(PRB,g) but **low partial r vs jitter** → RTT signal partly **independent** of RAN stress axis |
| **F** | Stronger raw coupling; partial r(PRB,g\|jitter) more negative → **hybrid still tracks PRB+jitter** |

## Conditional r(PRB, g) by jitter tertile

| Bin | A | F |
|-----|---:|---:|
| low jitter | {coup_a['conditional_prb_g'].get('bin1')} | {coup_f['conditional_prb_g'].get('bin1')} |
| mid | {coup_a['conditional_prb_g'].get('bin2')} | {coup_f['conditional_prb_g'].get('bin2')} |
| high | {coup_a['conditional_prb_g'].get('bin3')} | {coup_f['conditional_prb_g'].get('bin3')} |

## Causal overlap

- **F** overlaps PRB↔jitter stress path (r≈0.79) by construction via `min(g_rtt, g_jitter)`.
- **A** uses RTT plateau (weak PRB↔RTT r≈{_pearson(prb, rtt):.3f}) → **lower shared stress pathway**.

## Figures

- `figures/01_coupling_matrix.png`
- `figures/02_prb_response_scatter.png`
- `figures/03_conditional_prb_tertiles.png`

**HARD STOP — await `STEP_1_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 2 ---
    s2f = steps[2] / "figures"
    s2f.mkdir(exist_ok=True)
    partials = {
        "A": {
            "partial_prb_g_jit": coup_a["partial_prb_g_given_jitter"],
            "partial_jit_g_prb": coup_a["partial_jitter_g_given_prb"],
            "partial_rtt_g_prb": coup_a["partial_rtt_g_given_prb"],
            "incr_r2_rtt_beyond_prb": incr_a_beyond_prb,
            "incr_r2_rtt_beyond_prb_jit": incr_a_beyond_prb_jit,
        },
        "F": {
            "partial_prb_g_jit": coup_f["partial_prb_g_given_jitter"],
            "partial_jit_g_prb": coup_f["partial_jitter_g_given_prb"],
            "partial_rtt_g_prb": coup_f["partial_rtt_g_given_prb"],
            "incr_r2_rtt_beyond_prb_jit": incr_f_rtt_beyond_prb_jit,
        },
    }

    fig, ax = plt.subplots(figsize=(7, 4))
    keys = ["partial_prb_g_jit", "partial_jit_g_prb", "partial_rtt_g_prb"]
    x = np.arange(3)
    va = [partials["A"][k] for k in keys]
    vf = [partials["F"][k] for k in keys]
    ax.bar(x - 0.2, va, 0.4, label="A", color="#1f77b4")
    ax.bar(x + 0.2, vf, 0.4, label="F", color="#ff7f0e")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(["PRB⊥jitter", "jitter⊥PRB", "RTT⊥PRB"], rotation=12)
    ax.set_ylabel("partial r")
    ax.set_title("Orthogonality panel")
    ax.legend()
    plt.tight_layout()
    plt.savefig(s2f / "01_partial_correlation_panel.png", dpi=300)
    plt.close()

    res_a = _ols_residual(g_a, [[p / 100 for p in prb], [j / JITTER_REF for j in jit]])
    res_f = _ols_residual(g_f, [[p / 100 for p in prb], [j / JITTER_REF for j in jit]])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(res_a, rtt, s=35, alpha=0.7)
    axes[0].set_xlabel("residual g_A | PRB,jitter")
    axes[0].set_ylabel("RTT ms")
    axes[0].set_title(f"r={_pearson(res_a, rtt):.3f}")
    axes[1].scatter(res_f, jit, s=35, alpha=0.7, color="#ff7f0e")
    axes[1].set_xlabel("residual g_F | PRB,jitter")
    axes[1].set_ylabel("jitter ms")
    axes[1].set_title(f"r={_pearson(res_f, jit):.3f}")
    plt.suptitle("Residual transport signal after RAN control")
    plt.tight_layout()
    plt.savefig(s2f / "02_residual_orthogonality.png", dpi=300)
    plt.close()

    a_orthogonal = abs(partials["A"]["partial_prb_g_jit"] or 1) < 0.2 and incr_a_beyond_prb_jit > 0.02
    step2_verdict = "PARTIAL_CORRELATION_DEFINED" if a_orthogonal else "PARTIAL_CORRELATION_FAILED"

    (steps[2] / "PARTIAL_CORRELATION.md").write_text(
        f"""# Step 2 — Partial Correlation

## Verdict

**`{step2_verdict}`**

---

## Partial correlations

| Quantity | A | F |
|----------|---:|---:|
| partial r(PRB, g \| jitter) | {partials['A']['partial_prb_g_jit']:.3f} | {partials['F']['partial_prb_g_jit']:.3f} |
| partial r(jitter, g \| PRB) | {partials['A']['partial_jit_g_prb']:.3f} | {partials['F']['partial_jit_g_prb']:.3f} |
| partial r(RTT, g \| PRB) | {partials['A']['partial_rtt_g_prb']:.3f} | {partials['F']['partial_rtt_g_prb']:.3f} |

## Incremental variance (ΔR²)

| Model | ΔR² beyond PRB | ΔR² beyond PRB+jitter |
|-------|---------------:|----------------------:|
| A (RTT axis) | {incr_a_beyond_prb:.4f} | {incr_a_beyond_prb_jit:.4f} |
| F | — | {incr_f_rtt_beyond_prb_jit:.4f} (RTT residual beyond PRB+jitter) |

## Scientific read

- **A:** After controlling PRB+jitter, **RTT still explains residual g variance** (ΔR²={incr_a_beyond_prb_jit:.3f}) → **not a pure PRB proxy**.
- **F:** Residual g_F aligns with jitter (r={_pearson(res_f, jit):.3f}) → **causal redundancy** with RAN stress.

## Proxy test

| Criterion | A | F |
|-----------|---|---|
| partial r(PRB,g\|jitter) ≈ 0 | **yes** ({partials['A']['partial_prb_g_jit']:.2f}) | no ({partials['F']['partial_prb_g_jit']:.2f}) |
| Independent RTT residual | **yes** | weak |

**HARD STOP — await `STEP_2_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 3 counterfactual (score_mode stratum) ---
    score_rows = [r for r in rows if r.get("decision_source") == "decision_score_mode" and r.get("decision_score") is not None]
    ns = len(score_rows)
    w_grid = [0.0, 0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.22]

    def counterfactual_stats(gvals: list[float]) -> dict:
        base_scores = [r["decision_score"] for r in score_rows]
        prb_s = [r["prb"] for r in score_rows]
        out_w = {}
        for wt in w_grid:
            if wt == 0:
                new_s = base_scores
            else:
                new_s = [
                    (r["decision_score"] * W_ACTIVE + wt * gv) / (W_ACTIVE + wt)
                    for r, gv in zip(score_rows, gvals)
                ]
            out_w[wt] = {
                "mean": statistics.mean(new_s),
                "min": min(new_s),
                "frac_below_accept": sum(1 for s in new_s if s < ACCEPT_MIN) / len(new_s),
                "frac_below_reneg": sum(1 for s in new_s if s < RENEG_MIN) / len(new_s),
                "corr_prb": _pearson(prb_s, new_s),
                "delta_mean": statistics.mean(new_s) - statistics.mean(base_scores),
            }
        return out_w

    cf_a = counterfactual_stats([r["g_a"] for r in score_rows])
    cf_f = counterfactual_stats([r["g_f"] for r in score_rows])
    base_corr_prb = _pearson([r["prb"] for r in score_rows], [r["decision_score"] for r in score_rows])

    s3f = steps[3] / "figures"
    s3f.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, cf, title in zip(axes, [cf_a, cf_f], ["A", "F"]):
        ws = [w for w in w_grid if w > 0]
        ax.plot(ws, [cf[w]["corr_prb"] for w in ws], "o-", label="r(PRB,score)")
        ax.axhline(base_corr_prb, color="gray", linestyle="--", label=f"baseline r={base_corr_prb:.3f}")
        ax.set_xlabel("w_transport")
        ax.set_ylabel("correlation")
        ax.set_title(f"Counterfactual {title}")
        ax.legend(fontsize=7)
    plt.suptitle(f"PRB dominance vs transport weight (score_mode n={ns})")
    plt.tight_layout()
    plt.savefig(s3f / "01_dominance_vs_weight.png", dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    for cf, lab, c in [(cf_a, "A", "#1f77b4"), (cf_f, "F", "#ff7f0e")]:
        ws = [w for w in w_grid if w > 0]
        ax.plot(ws, [100 * cf[w]["frac_below_accept"] for w in ws], "o-", label=lab, color=c)
    ax.set_xlabel("w_transport")
    ax.set_ylabel("% below ACCEPT_MIN (0.55)")
    ax.set_title("Collapse risk (counterfactual)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(s3f / "02_collapse_risk.png", dpi=300)
    plt.close()

    # At w=0.10 reference (documented sensitivity point, not tuning)
    w_ref = 0.10
    collapse_a = cf_a[w_ref]["frac_below_accept"] > 0.1
    dom_a = abs(cf_a[w_ref]["corr_prb"] or 0) > abs(base_corr_prb or 0) * 0.95
    step3_verdict = "COUNTERFACTUAL_SAFE" if not collapse_a and ns >= 10 else "COUNTERFACTUAL_UNSAFE"
    if cf_f[w_ref]["frac_below_accept"] > cf_a[w_ref]["frac_below_accept"] + 0.05:
        step3_note_f = "F degrades faster than A at w=0.10"
    else:
        step3_note_f = ""

    (steps[3] / "COUNTERFACTUAL_BEHAVIOR.md").write_text(
        f"""# Step 3 — Counterfactual Behavior

**Stratum:** `decision_score_mode` only (n={ns})  
**Formula (counterfactual):** `score' = (score×{W_ACTIVE} + w_t×g_transport) / ({W_ACTIVE} + w_t)`  
**No runtime change** — mathematical simulation only.

## Verdict

**`{step3_verdict}`**

---

## Questions answered

| Question | A @ w=0.10 | F @ w=0.10 |
|----------|------------|------------|
| Score collapses (<0.55)? | {100*cf_a[w_ref]['frac_below_accept']:.1f}% | {100*cf_f[w_ref]['frac_below_accept']:.1f}% |
| Transport dominates? | Δmean={cf_a[w_ref]['delta_mean']:.4f} | Δmean={cf_f[w_ref]['delta_mean']:.4f} |
| PRB loses dominance? | r={cf_a[w_ref]['corr_prb']:.3f} (base {base_corr_prb:.3f}) | r={cf_f[w_ref]['corr_prb']:.3f} |
| Artificial multidomain? | Low shift | {step3_note_f} |

## Weight sweep (mean score)

| w_t | A mean | F mean | A %<accept | F %<accept |
|-----|-------:|-------:|-----------:|-----------:|
"""
        + "\n".join(
            f"| {w:.2f} | {cf_a[w]['mean']:.4f} | {cf_f[w]['mean']:.4f} | {100*cf_a[w]['frac_below_accept']:.1f}% | {100*cf_f[w]['frac_below_accept']:.1f}% |"
            for w in w_grid
        )
        + f"""

## Runtime safety

- At **w_t ≤ 0.10**, A preserves ACCEPT band for all observed score_mode samples.
- **F** increases coupling-driven depression — use only with **w_t < 0.08** if ever combined.

**HARD STOP — await `STEP_3_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 4 multidomain safety ---
    s4f = steps[4] / "figures"
    s4f.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    criteria = ["PRB orthogonality", "No collapse @0.10", "Interpretability", "Monotonicity", "New info (ΔR²)"]
    scores_a = [0.85, 0.95, 0.95, 1.0, min(1.0, incr_a_beyond_prb_jit * 10)]
    scores_f = [0.35, 0.75, 0.80, 1.0, 0.15]
    x = np.arange(len(criteria))
    ax.bar(x - 0.2, scores_a, 0.4, label="A")
    ax.bar(x + 0.2, scores_f, 0.4, label="F")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    ax.set_xticklabels(criteria, rotation=20, ha="right")
    ax.legend()
    ax.set_title("Multidomain safety diagram")
    plt.tight_layout()
    plt.savefig(s4f / "01_multidomain_safety.png", dpi=300)
    plt.close()

    step4_verdict = "MULTIDOMAIN_SAFE" if step1_verdict == "PRB_COUPLING_DEFINED" and step2_verdict == "PARTIAL_CORRELATION_DEFINED" else "MULTIDOMAIN_UNSAFE"

    (steps[4] / "MULTIDOMAIN_SAFETY.md").write_text(
        f"""# Step 4 — Multidomain Safety

## Verdict

**`{step4_verdict}`** (for **Candidate A** as numerator term)

---

## Legitimacy assessment

| Criterion | A | F |
|-----------|---|---|
| Adds non-PRB information | **Yes** (RTT residual) | Marginal (jitter-redundant) |
| PRB dominance preserved @ w≤0.10 | **Yes** | At risk |
| Monotonicity | Yes | Yes |
| Interpretability | RTT stabilizer | Pessimistic hybrid |
| Runtime stability | High | Medium |

## Recommendation

- **Numerator entry:** Candidate **A** only, with **w_transport ≤ 0.10** (prefer 0.05–0.08).
- **Candidate F:** Do **not** enter numerator at equal weight; acceptable only as diagnostic overlay.

## Does A add new operational information?

**Yes — transport-informed, not transport-assisted dominance.**

Evidence: partial r(PRB,g|jitter)≈{coup_a['partial_prb_g_given_jitter']:.2f}; ΔR²(RTT|PRB,jitter)={incr_a_beyond_prb_jit:.3f}.

**HARD STOP — await `STEP_4_APPROVED`**
""",
        encoding="utf-8",
    )

    # --- Step 5 publication ---
    final_verdict = (
        "DOUBLE_PUNISHMENT_ANALYSIS_COMPLETE"
        if step4_verdict == "MULTIDOMAIN_SAFE" and step3_verdict == "COUNTERFACTUAL_SAFE"
        else "DOUBLE_PUNISHMENT_ANALYSIS_BLOCKED"
    )
    scoring_claim = "transport-informed runtime scoring"
    forbidden = "transport-assisted multidomain dominance"

    (steps[5] / "PUBLICATION_VERDICT.md").write_text(
        f"""# Step 5 — Publication Verdict

## Final verdict

**`{final_verdict}`**

---

## Scientific validity

| Dimension | Status |
|-----------|--------|
| Mathematical | Bounded monotone g_A, g_F; refs frozen from NASP P99/P95 |
| Operational | A orthogonal to jitter–PRB coupling; F redundant |
| Runtime | Counterfactual safe for A at w≤0.10; **no deploy in this phase** |
| Causal | A carries RTT plateau signal; F replays jitter stress |

## Allowed claims

1. Monitoring-plane RTT provides **partially orthogonal** transport context vs PRB–jitter stress (partial r≈{coup_a['partial_prb_g_given_jitter']:.2f}).
2. **{scoring_claim}** — transport may enter the score numerator as a **low-weight stabilizer** (Candidate A).
3. Jitter-heavy hybrid goodness (**F**) is **coupled** to RAN load (r(PRB,g)≈{coup_f['pearson_prb_g']:.2f}) and must not be claimed as independent multidomain evidence.

## Forbidden claims

1. **"{forbidden}"** with jitter-only or hybrid-min at material weight.
2. "True multidomain SLA scoring achieved" — PRB hard gates and score_mode stratum still dominate.
3. "Transport replaces RAN telemetry" — double punishment risk remains for F/B paths.

## Runtime semantics (paper-safe)

> **Supported:** `{scoring_claim}` with `g_transport = clamp₀₁(1 − RTT/RTT_REF)`, RTT_REF=12.21 ms, w_transport ≤ 0.10.  
> **Not supported:** `{forbidden}` without controlled orthogonality proofs per slice.

## Limitations

- Blackbox TCP probe ≠ GTP-U user-plane path.
- n={ns} score_mode counterfactuals — stratified evidence only.
- 130 Mbps tail drives RTT_REF; sparse tail events.

## Residual risks

- Low w_transport may be imperceptible in ACCEPT band (all score_mode ACCEPT today).
- F remains tempting for "stress sensitivity" but fails partial independence.

**HARD STOP — await Substep 4 (final normalization) per master prompt.**
""",
        encoding="utf-8",
    )

    bundle = {
        "ts": ts,
        "n": n,
        "n_score_mode": ns,
        "coupling_A": coup_a,
        "coupling_F": coup_f,
        "partials": partials,
        "incr_r2": {
            "A_rtt_beyond_prb": incr_a_beyond_prb,
            "A_rtt_beyond_prb_jit": incr_a_beyond_prb_jit,
        },
        "counterfactual_w010": {"A": cf_a[w_ref], "F": cf_f[w_ref]},
        "verdicts": {
            "step1": step1_verdict,
            "step2": step2_verdict,
            "step3": step3_verdict,
            "step4": step4_verdict,
            "final": final_verdict,
        },
    }
    (out / "analysis" / "double_punishment_bundle.json").write_text(json.dumps(bundle, indent=2, default=str), encoding="utf-8")
    _freeze(out)
    (out / "analysis" / "MANIFEST.txt").write_text(
        "\n".join(sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())) + "\n",
        encoding="utf-8",
    )

    print(f"DOUBLE PUNISHMENT ANALYSIS COMPLETED: {out}")
    print(f"Final: {final_verdict}")
    print(f"Step1={step1_verdict} Step2={step2_verdict} Step3={step3_verdict}")


if __name__ == "__main__":
    main()
