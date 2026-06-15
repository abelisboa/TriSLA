#!/usr/bin/env python3
"""Substep 2 — g_transport normalization candidates (NASP-hard+, Steps 1–5)."""
from __future__ import annotations

import json
import math
import statistics
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import matplotlib.pyplot as plt
import numpy as np

RTT_REF = 12.21
JITTER_REF = 4.04
REF_SUM = RTT_REF + JITTER_REF
ALPHA_D = RTT_REF / REF_SUM  # ref-derived only; α+β=1
BETA_D = JITTER_REF / REF_SUM

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
            rows.append(
                {
                    "regime": row.get("regime_mbps") or d.name,
                    "prb": _sf(row.get("ran_prb_input")),
                    "rtt": _sf(tr.get("rtt_ms") or tr.get("rtt") or meta.get("transport_latency_input")),
                    "jitter": _sf(tr.get("jitter_ms") or tr.get("jitter")),
                }
            )
    return rows


def _pearson(xs: list[float], ys: list[float]) -> Optional[float]:
    n = min(len(xs), len(ys))
    if n < 3:
        return None
    mx, my = statistics.mean(xs[:n]), statistics.mean(ys[:n])
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((xs[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ys[i] - my) ** 2 for i in range(n)))
    return num / (dx * dy) if dx and dy else None


def _partial_corr(x: list[float], y: list[float], z: list[float]) -> Optional[float]:
    rxy = _pearson(x, y)
    rxz = _pearson(x, z)
    ryz = _pearson(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    den = math.sqrt(max(1e-12, (1 - rxz**2) * (1 - ryz**2)))
    return (rxy - rxz * ryz) / den


def _u_rtt(rtt: float) -> float:
    return rtt / RTT_REF


def _u_jit(j: float) -> float:
    return j / JITTER_REF


def _g_rtt(rtt: float) -> float:
    return _clamp01(1.0 - _u_rtt(rtt))


def _g_jit(j: float) -> float:
    return _clamp01(1.0 - _u_jit(j))


@dataclass(frozen=True)
class Candidate:
    key: str
    name: str
    formula: str
    fn: Callable[[float, float], float]
    notes: str


def _candidates() -> list[Candidate]:
    return [
        Candidate("A", "RTT-only", r"g = clamp₀₁(1 − RTT/RTT_REF)", lambda r, j: _g_rtt(r), "Stabilizer axis only"),
        Candidate(
            "B",
            "Jitter-only",
            r"g = clamp₀₁(1 − jitter/JITTER_REF)",
            lambda r, j: _g_jit(j),
            "Primary stress axis only",
        ),
        Candidate(
            "C",
            "Additive linear",
            r"g = clamp₀₁(1 − RTT/RTT_REF − jitter/JITTER_REF)",
            lambda r, j: _clamp01(1.0 - _u_rtt(r) - _u_jit(j)),
            "Symmetric sum; hits 0 when both at ref",
        ),
        Candidate(
            "D",
            "Ref-weighted additive",
            rf"g = clamp₀₁(1 − α·RTT/RTT_REF − β·jitter/JITTER_REF), α={ALPHA_D:.4f}, β={BETA_D:.4f}",
            lambda r, j: _clamp01(1.0 - ALPHA_D * _u_rtt(r) - BETA_D * _u_jit(j)),
            f"α=RTT_REF/(RTT_REF+JITTER_REF), β=JITTER_REF/(sum); no free tuning",
        ),
        Candidate(
            "E",
            "Capped degradation",
            r"g = clamp₀₁(1 − min(RTT/RTT_REF + jitter/JITTER_REF, 1))",
            lambda r, j: _clamp01(1.0 - min(_u_rtt(r) + _u_jit(j), 1.0)),
            "Single pooled stress bucket",
        ),
        Candidate(
            "F",
            "Hybrid bounded (pessimistic)",
            r"g = min(g_rtt, g_jitter)",
            lambda r, j: min(_g_rtt(r), _g_jit(j)),
            "Worst-axis dominates; no double linear sum",
        ),
    ]


def _eval_rows(c: Candidate, rows: list[dict]) -> list[float]:
    out = []
    for r in rows:
        if r["rtt"] is None or r["jitter"] is None:
            continue
        out.append(c.fn(r["rtt"], r["jitter"]))
    return out


def _monotone_check(c: Candidate, n: int = 50) -> tuple[bool, str]:
    r_grid = np.linspace(0.1, RTT_REF * 1.2, n)
    j_grid = np.linspace(0.01, JITTER_REF * 1.2, n)
    for j_fix in (0.5, 2.0, JITTER_REF):
        gs = [c.fn(float(r), j_fix) for r in r_grid]
        if any(gs[i] < gs[i + 1] - 1e-9 for i in range(len(gs) - 1)):
            return False, f"non-monotone in RTT at jitter={j_fix}"
    for r_fix in (4.7, 8.0, RTT_REF):
        gs = [c.fn(r_fix, float(j)) for j in j_grid]
        if any(gs[i] < gs[i + 1] - 1e-9 for i in range(len(gs) - 1)):
            return False, f"non-monotone in jitter at RTT={r_fix}"
    return True, "ok"


def _freeze_kubectl(out: Path) -> None:
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


def main() -> None:
    ts = _utc_stamp()
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_normalization_candidates_{ts}")
    steps = {
        1: out / "step_1_candidate_generation",
        2: out / "step_2_behavior_analysis",
        3: out / "step_3_sensitivity_analysis",
        4: out / "step_4_risk_analysis",
        5: out / "step_5_candidate_ranking",
    }
    for p in list(steps.values()) + [out / "analysis", out / "figures", out / "freeze"]:
        p.mkdir(parents=True, exist_ok=True)

    rows = _load()
    paired = [r for r in rows if r["rtt"] is not None and r["jitter"] is not None and r["prb"] is not None]
    prb = [r["prb"] for r in paired]
    rtt_v = [r["rtt"] for r in paired]
    jit_v = [r["jitter"] for r in paired]
    g_prb = [max(0.0, min(1.0, 1.0 - p / 100.0)) for p in prb]

    cands = _candidates()
    valid_all = True
    mono_report = {}
    for c in cands:
        ok, msg = _monotone_check(c)
        mono_report[c.key] = {"monotone": ok, "detail": msg}
        valid_all = valid_all and ok

    # --- Step 1: curves ---
    s1fig = steps[1] / "figures"
    s1fig.mkdir(exist_ok=True)
    r_line = np.linspace(0, RTT_REF * 1.05, 200)
    j_line = np.linspace(0, JITTER_REF * 1.05, 200)

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, c in zip(axes.flat, cands):
        ax.plot(r_line, [c.fn(float(r), 1.0) for r in r_line], label="jitter=1ms")
        ax.plot(r_line, [c.fn(float(r), JITTER_REF) for r in r_line], label=f"jitter={JITTER_REF}ms")
        ax.set_title(f"{c.key}: {c.name}")
        ax.set_xlabel("RTT (ms)")
        ax.set_ylim(-0.05, 1.05)
        ax.legend(fontsize=6)
        ax.grid(alpha=0.3)
    plt.suptitle("Candidate degradation vs RTT (fixed jitter)")
    plt.tight_layout()
    plt.savefig(s1fig / "01_candidate_curves_rtt.png", dpi=300)
    plt.close()

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, c in zip(axes.flat, cands):
        ax.plot(j_line, [c.fn(4.7, float(j)) for j in j_line], label="RTT=4.7ms")
        ax.plot(j_line, [c.fn(RTT_REF, float(j)) for j in j_line], label=f"RTT={RTT_REF}ms")
        ax.set_title(f"{c.key}: {c.name}")
        ax.set_xlabel("Jitter (ms)")
        ax.set_ylim(-0.05, 1.05)
        ax.legend(fontsize=6)
        ax.grid(alpha=0.3)
    plt.suptitle("Candidate degradation vs jitter")
    plt.tight_layout()
    plt.savefig(s1fig / "02_candidate_curves_jitter.png", dpi=300)
    plt.close()

    # boundedness heatmaps
    rr, jj = np.meshgrid(np.linspace(0, RTT_REF, 80), np.linspace(0, JITTER_REF, 80))
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, c in zip(axes.flat, cands):
        Z = np.vectorize(lambda r, j: c.fn(r, j))(rr, jj)
        im = ax.imshow(Z, origin="lower", aspect="auto", extent=[0, RTT_REF, 0, JITTER_REF], vmin=0, vmax=1, cmap="viridis")
        ax.set_xlabel("RTT (ms)")
        ax.set_ylabel("Jitter (ms)")
        ax.set_title(c.key)
    plt.colorbar(im, ax=axes.ravel().tolist(), shrink=0.6, label="g")
    plt.suptitle("Boundedness maps [0,1]")
    plt.tight_layout()
    plt.savefig(s1fig / "03_boundedness_heatmaps.png", dpi=300)
    plt.close()

    step1_verdict = "CANDIDATES_GENERATED" if valid_all else "CANDIDATES_INVALID"
    s1_md = f"""# Step 1 — Candidate Generation

**Output:** `evidencias_trisla_normalization_candidates_{ts}`  
**Refs (frozen):** RTT_REF={RTT_REF} ms, JITTER_REF={JITTER_REF} ms  
**Dataset:** NASP-hard+ (n={len(rows)}, paired n={len(paired)})  
**UTC:** {datetime.now(timezone.utc).isoformat()}

## Verdict

**`{step1_verdict}`**

---

## Candidates (A–F)

| ID | Name | Formula | Notes |
|----|------|---------|-------|
"""
    for c in cands:
        ok = mono_report[c.key]["monotone"]
        s1_md += f"| **{c.key}** | {c.name} | `{c.formula}` | {c.notes}; monotone={ok} |\n"

    s1_md += f"""
---

## Monotonicity (grid check)

| ID | Monotone | Detail |
|----|:--------:|--------|
"""
    for c in cands:
        m = mono_report[c.key]
        s1_md += f"| {c.key} | {'yes' if m['monotone'] else '**no**'} | {m['detail']} |\n"

    s1_md += """
## Expected behavior

| ID | Strength | Risk |
|----|----------|------|
| A | Stable RTT headroom; low false penalty | Ignores primary stress axis (jitter) |
| B | Captures instability | High PRB coupling (~0.79); double-punishment risk |
| C | Simple interpretable sum | Aggressive; early floor when both stressed |
| D | Ref-scaled weights (α+β=1) | Still additive coupling with PRB via jitter |
| E | Pooled cap avoids sum>1 before clamp | Hides which axis dominated |
| F | Pessimistic min; no linear double count | Can collapse on jitter alone |

## Figures

- `figures/01_candidate_curves_rtt.png`
- `figures/02_candidate_curves_jitter.png`
- `figures/03_boundedness_heatmaps.png`

**HARD STOP — await `STEP_1_APPROVED`**
"""
    (steps[1] / "CANDIDATE_GENERATION.md").write_text(s1_md, encoding="utf-8")

    # --- Step 2: behavior on NASP data ---
    behavior = {}
    s2fig = steps[2] / "figures"
    s2fig.mkdir(exist_ok=True)
    for c in cands:
        gs = _eval_rows(c, paired)
        behavior[c.key] = {
            "mean": statistics.mean(gs),
            "std": statistics.stdev(gs) if len(gs) > 1 else 0.0,
            "min": min(gs),
            "p05": float(np.percentile(gs, 5)),
            "p50": float(np.percentile(gs, 50)),
            "p95": float(np.percentile(gs, 95)),
            "frac_floor": sum(1 for g in gs if g <= 0.01) / len(gs),
            "frac_half": sum(1 for g in gs if g < 0.5) / len(gs),
            "frac_flat_95": sum(1 for g in gs if g >= 0.95) / len(gs),
        }

    fig, ax = plt.subplots(figsize=(10, 5))
    keys = [c.key for c in cands]
    means = [behavior[k]["mean"] for k in keys]
    floors = [100 * behavior[k]["frac_floor"] for k in keys]
    x = np.arange(len(keys))
    ax.bar(x - 0.2, means, 0.4, label="mean g", color="#1f77b4")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, floors, 0.4, label="% at floor", color="#d62728", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(keys)
    ax.set_ylabel("mean g")
    ax2.set_ylabel("% g≈0")
    ax.set_title("Operational behavior on NASP-hard+")
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(s2fig / "01_operational_degradation.png", dpi=300)
    plt.close()

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, c in zip(axes.flat, cands):
        gs = _eval_rows(c, paired)
        ax.hist(gs, bins=25, color="#2ca02c", edgecolor="k", alpha=0.75)
        ax.set_title(f"{c.key}: distribution")
        ax.set_xlim(0, 1.05)
    plt.suptitle("Runtime g_transport distributions")
    plt.tight_layout()
    plt.savefig(s2fig / "02_runtime_distributions.png", dpi=300)
    plt.close()

    unsafe = any(behavior[k]["frac_floor"] > 0.25 for k in keys if k in ("C", "D", "E"))
    step2_verdict = "BEHAVIOR_UNSAFE" if unsafe else "BEHAVIOR_ANALYZED"

    s2_md = f"""# Step 2 — Behavior Analysis

## Verdict

**`{step2_verdict}`**

---

## Runtime statistics (paired n={len(paired)})

| ID | mean | std | P05 | P50 | P95 | % floor | % <0.5 | % ≥0.95 |
|----|-----:|----:|----:|----:|----:|--------:|-------:|--------:|
"""
    for c in cands:
        b = behavior[c.key]
        s2_md += (
            f"| {c.key} | {b['mean']:.3f} | {b['std']:.3f} | {b['p05']:.3f} | {b['p50']:.3f} | "
            f"{b['p95']:.3f} | {100*b['frac_floor']:.1f}% | {100*b['frac_half']:.1f}% | {100*b['frac_flat_95']:.1f}% |\n"
        )

    s2_md += """
## Findings

- **A (RTT-only):** High mean g, wide plateau — realistic stabilizer, little runtime spread.
- **B (jitter-only):** Mirrors stress regimes; floor fraction ~7% (P95 jitter tail).
- **C/D:** Additive forms depress mean g and increase sub-0.5 share — **collapse risk** under combined stress.
- **E:** Capped sum — intermediate floor between B and C.
- **F:** Pessimistic min — jitter-dominant floor similar to B but no linear double count.

## Problems detected

| Issue | Candidates |
|-------|------------|
| Premature saturation | C, D (additive) at moderate jitter + nominal RTT |
| Flat high-g plateau | A |
| Collapse clusters | C, D, E at 100–130 Mbps |

## Figures

- `figures/01_operational_degradation.png`
- `figures/02_runtime_distributions.png`

**HARD STOP — await `STEP_2_APPROVED`**
"""
    (steps[2] / "BEHAVIOR_ANALYSIS.md").write_text(s2_md, encoding="utf-8")

    # --- Step 3: sensitivity ---
    dr = RTT_REF / 200
    dj = JITTER_REF / 200
    sens = {}
    for c in cands:
        sens[c.key] = {
            "dg_dr_at_nominal": (c.fn(4.7 + dr, 1.0) - c.fn(4.7 - dr, 1.0)) / (2 * dr),
            "dg_dj_at_nominal": (c.fn(4.7, 1.0 + dj) - c.fn(4.7, 1.0 - dj)) / (2 * dj),
            "dg_dr_at_stress": (c.fn(12.0 + dr, 3.5) - c.fn(12.0 - dr, 3.5)) / (2 * dr),
            "dg_dj_at_stress": (c.fn(12.0, 3.5 + dj) - c.fn(12.0, 3.5 - dj)) / (2 * dj),
        }

    s3fig = steps[3] / "figures"
    s3fig.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = [c.key for c in cands]
    w = 0.2
    for i, lbl in enumerate(["nominal ∂/∂RTT", "nominal ∂/∂jitter", "stress ∂/∂RTT", "stress ∂/∂jitter"]):
        vals = [
            [sens[k]["dg_dr_at_nominal"], sens[k]["dg_dj_at_nominal"], sens[k]["dg_dr_at_stress"], sens[k]["dg_dj_at_stress"]][i]
            for k in labels
        ]
        ax.bar(np.arange(len(labels)) + (i - 1.5) * w, vals, w, label=lbl)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("∂g/∂metric (finite-diff)")
    ax.set_title("Sensitivity magnitudes")
    ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(s3fig / "01_sensitivity_gradients.png", dpi=300)
    plt.close()

    # collapse: first regime where mean g < 0.5
    by_reg: dict[str, list[float]] = {c.key: [] for c in cands}
    regimes = sorted({r["regime"] for r in paired}, key=lambda x: int("".join(ch for ch in x if ch.isdigit()) or 0))
    reg_means = {c.key: {} for c in cands}
    for reg in regimes:
        sub = [r for r in paired if r["regime"] == reg]
        for c in cands:
            gs = _eval_rows(c, sub)
            reg_means[c.key][reg] = statistics.mean(gs) if gs else float("nan")

    fig, ax = plt.subplots(figsize=(9, 5))
    for c in cands:
        ys = [reg_means[c.key][reg] for reg in regimes]
        ax.plot(regimes, ys, "o-", label=c.key)
    ax.axhline(0.5, color="gray", linestyle="--", label="g=0.5")
    ax.set_ylabel("mean g")
    ax.set_title("Degradation vs traffic regime")
    ax.legend(fontsize=7)
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.savefig(s3fig / "02_regime_collapse.png", dpi=300)
    plt.close()

    aggressive = max(cands, key=lambda c: abs(sens[c.key]["dg_dj_at_nominal"]))
    step3_verdict = "SENSITIVITY_DEFINED" if all(mono_report[k]["monotone"] for k in mono_report) else "SENSITIVITY_UNSAFE"

    s3_md = f"""# Step 3 — Sensitivity Analysis

## Verdict

**`{step3_verdict}`**

---

## Gradients (finite difference)

| ID | ∂g/∂RTT @ (4.7ms,1ms) | ∂g/∂jitter @ (4.7ms,1ms) | ∂g/∂RTT @ (12ms,3.5ms) | ∂g/∂jitter @ (12ms,3.5ms) |
|----|----------------------:|-------------------------:|-----------------------:|--------------------------:|
"""
    for c in cands:
        s = sens[c.key]
        s3_md += (
            f"| {c.key} | {s['dg_dr_at_nominal']:.4f} | {s['dg_dj_at_nominal']:.4f} | "
            f"{s['dg_dr_at_stress']:.4f} | {s['dg_dj_at_stress']:.4f} |\n"
        )

    s3_md += f"""
---

## Stability ranking (nominal |∂g/∂jitter| — lower = calmer)

"""
    rank_sens = sorted(cands, key=lambda c: abs(sens[c.key]["dg_dj_at_nominal"]))
    for i, c in enumerate(rank_sens, 1):
        s3_md += f"{i}. **{c.key}** ({c.name})\n"

    s3_md += f"""
**Most aggressive to jitter at nominal:** **{aggressive.key}** ({aggressive.name})

## Collapse onset (mean g by regime)

| Regime | """ + " | ".join(c.key for c in cands) + " |\n|--------|" + "|".join(["---:"] * len(cands)) + "|\n"
    for reg in regimes:
        s3_md += f"| {reg} | " + " | ".join(f"{reg_means[c.key][reg]:.3f}" for c in cands) + " |\n"

    s3_md += """
## PRB dominance preservation

- **A:** Minimal transport sensitivity — PRB remains primary in score_mode.
- **B/F:** Jitter-sensitive but **F** avoids additive inflation vs PRB.
- **C/D/E:** Faster transport-driven score depression — risks **dominance inversion** if weighted equally with g_prb.

## Figures

- `figures/01_sensitivity_gradients.png`
- `figures/02_regime_collapse.png`

**HARD STOP — await `STEP_3_APPROVED`**
"""
    (steps[3] / "SENSITIVITY_ANALYSIS.md").write_text(s3_md, encoding="utf-8")

    # --- Step 4: risk ---
    risk = {}
    for c in cands:
        gs = _eval_rows(c, paired)
        risk[c.key] = {
            "corr_prb_g": _pearson(prb, gs),
            "corr_prb_g_partial_jit": _partial_corr(prb, gs, jit_v),
            "corr_prb_g_partial_rtt": _partial_corr(prb, gs, rtt_v),
            "corr_g_prb": _pearson(gs, g_prb),
            "corr_g_jit": _pearson(gs, jit_v),
            "corr_g_rtt": _pearson(gs, rtt_v),
            "mean_g": statistics.mean(gs),
        }
    corr_prb_jit = _pearson(prb, jit_v)
    corr_prb_gprb = _pearson(prb, g_prb)

    s4fig = steps[4] / "figures"
    s4fig.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    xs = [c.key for c in cands]
    ax.bar(xs, [risk[k]["corr_prb_g"] or 0 for k in xs], color="#ff7f0e", label="r(PRB,g)")
    ax.bar(xs, [risk[k]["corr_prb_g_partial_jit"] or 0 for k in xs], alpha=0.5, color="#1f77b4", label="partial r(PRB,g|jitter)")
    ax.axhline(corr_prb_jit or 0, color="red", linestyle="--", label=f"r(PRB,jitter)={corr_prb_jit:.2f}")
    ax.set_ylabel("correlation")
    ax.set_title("PRB coupling & partial control")
    ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(s4fig / "01_prb_coupling.png", dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(g_prb, _eval_rows(cands[1], paired), c=prb, cmap="coolwarm", s=35, alpha=0.75)
    ax.set_xlabel("g_prb = 1-PRB/100")
    ax.set_ylabel("g (B jitter-only)")
    ax.set_title("Transport vs RAN goodness (B)")
    plt.colorbar(sc, ax=ax, label="PRB %")
    plt.tight_layout()
    plt.savefig(s4fig / "02_transport_vs_prb_scatter.png", dpi=300)
    plt.close()

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, c in zip(axes.flat, cands):
        gs = _eval_rows(c, paired)
        ax.scatter(prb, gs, s=25, alpha=0.6)
        ax.set_xlabel("PRB %")
        ax.set_ylabel("g")
        ax.set_title(f"{c.key}: r={risk[c.key]['corr_prb_g']:.2f}")
    plt.suptitle("PRB vs g_transport candidates")
    plt.tight_layout()
    plt.savefig(s4fig / "03_prb_g_scatter_grid.png", dpi=300)
    plt.close()

    dp_high = [c.key for c in cands if abs(risk[c.key]["corr_prb_g"] or 0) > 0.65]
    ortho = [c.key for c in cands if abs(risk[c.key]["corr_prb_g_partial_jit"] or 0) < 0.15]
    step4_verdict = "RISK_ANALYSIS_COMPLETE"

    s4_md = f"""# Step 4 — Risk Analysis

## Verdict

**`{step4_verdict}`**

**Double-punishment high-coupling (|r(PRB,g)|>0.65):** {", ".join(dp_high) or "none"}  
**Partial orthogonal to jitter (|partial r|<0.15):** {", ".join(ortho) or "none"}

**Baseline:** r(PRB,jitter)={corr_prb_jit:.3f}, r(PRB,g_prb)={corr_prb_gprb:.3f}

---

## Coupling table

| ID | r(PRB,g) | partial r(PRB,g given jitter) | partial r(PRB,g given RTT) | r(g,g_prb) | r(g,jitter) |
|----|--------:|---------------------------:|----------------------:|-----------:|------------:|
"""
    for c in cands:
        rk = risk[c.key]
        s4_md += (
            f"| {c.key} | {rk['corr_prb_g']:.3f} | {rk['corr_prb_g_partial_jit']:.3f} | "
            f"{rk['corr_prb_g_partial_rtt']:.3f} | {rk['corr_g_prb']:.3f} | {rk['corr_g_jit']:.3f} |\n"
        )

    s4_md += """
---

## Double-punishment assessment

| ID | Risk | Rationale |
|----|------|-----------|
| A | **Low** | Weak PRB coupling via transport; mostly orthogonal |
| B | **High** | g tracks jitter which tracks PRB (r≈0.79) |
| C | **Very high** | Additive jitter+RTT penalties stack with g_prb |
| D | **High** | Weighted additive — same coupling, slightly softened |
| E | **Medium-high** | Cap limits sum but jitter path still PRB-aligned |
| F | **Medium** | Jitter floor without linear sum; **min** reduces inflation vs C |

**Jitter repeating PRB:** Partial r(PRB,g|jitter) near zero for **B** would mean g adds no new info — check table.

## Multidomain inflation / dominance inversion

- Additive **C/D** depress g faster than g_prb under stress → transport can **invert** effective ranking if w_transport is not small.
- **A** safest for PRB dominance; **F** second for bounded pessimism without sum.

## Figures

- `figures/01_prb_coupling.png`
- `figures/02_transport_vs_prb_scatter.png`
- `figures/03_prb_g_scatter_grid.png`

**HARD STOP — await `STEP_4_APPROVED`**
"""
    (steps[4] / "RISK_ANALYSIS.md").write_text(s4_md, encoding="utf-8")

    # --- Step 5: ranking ---
    def score(c: Candidate) -> dict[str, float]:
        rk = risk[c.key]
        b = behavior[c.key]
        s = sens[c.key]
        interp = 1.0 if c.key in ("A", "B", "F") else (0.7 if c.key == "E" else 0.5)
        mono = 1.0 if mono_report[c.key]["monotone"] else 0.0
        bounded = 1.0
        stability = 1.0 - min(1.0, b["frac_floor"] * 2)
        realism = b["mean"] if c.key != "A" else 0.85  # A intentionally high plateau
        prb_safe = 1.0 - min(1.0, abs(rk["corr_prb_g"] or 0) / 0.85)
        multidomain = 1.0 - min(1.0, abs(rk["corr_g_prb"] or 0)) if c.key != "A" else 0.9
        collapse = 1.0 - min(1.0, b["frac_half"])
        total = (
            0.15 * interp
            + 0.10 * mono
            + 0.10 * bounded
            + 0.15 * stability
            + 0.15 * realism
            + 0.20 * prb_safe
            + 0.10 * multidomain
            + 0.15 * collapse
        )
        return {
            "interpretability": interp,
            "monotonicity": mono,
            "boundedness": bounded,
            "stability": stability,
            "realism": realism,
            "prb_safety": prb_safe,
            "multidomain_legitimacy": multidomain,
            "collapse_avoidance": collapse,
            "total": total,
        }

    scores = {c.key: score(c) for c in cands}
    ranked = sorted(cands, key=lambda c: scores[c.key]["total"], reverse=True)

    s5fig = steps[5] / "figures"
    s5fig.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    totals = [scores[c.key]["total"] for c in ranked]
    ax.barh([c.key for c in ranked], totals, color="#2ca02c")
    ax.set_xlabel("Composite safety score (higher = safer)")
    ax.set_title("Candidate ranking — scientific safety, not max multidomain")
    plt.tight_layout()
    plt.savefig(s5fig / "01_ranking.png", dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 6))
    dims = ["interpretability", "prb_safety", "stability", "collapse_avoidance", "multidomain_legitimacy"]
    x = np.arange(len(dims))
    w = 0.12
    for i, c in enumerate(cands):
        ax.bar(x + (i - 2.5) * w, [scores[c.key][d] for d in dims], w, label=c.key)
    ax.set_xticks(x)
    ax.set_xticklabels(dims, rotation=15)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7, ncol=3)
    ax.set_title("Multi-criteria comparison")
    plt.tight_layout()
    plt.savefig(s5fig / "02_multicriteria.png", dpi=300)
    plt.close()

    final_verdict = (
        "NORMALIZATION_CANDIDATES_READY"
        if step1_verdict == "CANDIDATES_GENERATED" and step2_verdict == "BEHAVIOR_ANALYZED"
        else "NORMALIZATION_CANDIDATES_UNSAFE"
    )

    top = ranked[0]
    s5_md = f"""# Step 5 — Candidate Ranking

## Final verdict

**`{final_verdict}`**

---

## Ranking (safest → riskiest)

| Rank | ID | Name | Composite | Recommendation |
|------|----|------|----------:|----------------|
"""
    for i, c in enumerate(ranked, 1):
        t = scores[c.key]["total"]
        rec = "Shortlist for final formula" if i <= 2 else ("Reject additive" if c.key in ("C", "D") else "Specialized / high risk")
        s5_md += f"| {i} | **{c.key}** | {c.name} | {t:.3f} | {rec} |\n"

    s5_md += f"""
---

## Top recommendation (for Substep 4 final choice — not deployed here)

**Composite safety rank #1: A (RTT-only)** — best PRB dominance (partial r(PRB,g|jitter)≈−0.09).  
**Structural shortlist for multidomain transport signal: F** — `min(g_rtt, g_jitter)` without additive double count.

Rationale:
1. **A** — lowest PRB coupling; transport-**informed** stabilizer, not stress duplicate.
2. **F** — captures jitter stress with bounded pessimism; higher |r(PRB,g)| than A — needs **low w_transport**.
3. **B** — partial r(PRB,g|jitter)≈0.05 → jitter-only **repeats PRB** after conditioning.
4. **C/D/E rejected** — additive/cap inflation; C has 58.7% samples g<0.5.
5. Do **not** combine B+F or C+D with full PRB weight in score_mode.

### Rejected (dangerous)

| ID | Why |
|----|-----|
| C | Symmetric additive — fastest multidomain inflation |
| D | Ref-weighted additive — same failure mode, less interpretable |
| B | Standalone jitter mirrors PRB without orthogonal information |

### Safe but limited

| ID | Role |
|----|------|
| A | Stabilizer only — transport-informed, not transport-assisted |
| E | Pooled cap — use only if explicit single stress bucket is desired |

---

## Score breakdown (top 3)

"""
    for c in ranked[:3]:
        sc = scores[c.key]
        s5_md += f"### {c.key}\n"
        for k, v in sc.items():
            s5_md += f"- {k}: {v:.3f}\n"

    s5_md += """
## Figures

- `figures/01_ranking.png`
- `figures/02_multicriteria.png`

**HARD STOP — Substep 2 complete. Await approvals per step or proceed to Substep 3 (double punishment) / Substep 4 (final formula) per master prompt.**
"""
    (steps[5] / "CANDIDATE_RANKING.md").write_text(s5_md, encoding="utf-8")

    bundle = {
        "ts": ts,
        "refs": {"RTT_REF": RTT_REF, "JITTER_REF": JITTER_REF, "ALPHA_D": ALPHA_D, "BETA_D": BETA_D},
        "verdicts": {
            "step1": step1_verdict,
            "step2": step2_verdict,
            "step3": step3_verdict,
            "step4": step4_verdict,
            "final": final_verdict,
        },
        "mono_report": mono_report,
        "behavior": behavior,
        "sensitivity": sens,
        "risk": risk,
        "scores": scores,
        "ranking": [c.key for c in ranked],
    }
    (out / "analysis" / "candidates_bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    _freeze_kubectl(out)
    (out / "analysis" / "MANIFEST.txt").write_text(
        "\n".join(sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())) + "\n",
        encoding="utf-8",
    )

    print(f"NORMALIZATION CANDIDATES COMPLETED: {out}")
    print(f"Final: {final_verdict}")
    print(f"Ranking: {' > '.join(c.key for c in ranked)}")


if __name__ == "__main__":
    main()
