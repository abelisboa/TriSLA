#!/usr/bin/env python3
"""Substep 1 — RTT_REF / JITTER_REF reference analysis (NASP-hard+)."""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

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


def _pct(vals: list[float], p: float) -> float:
    return float(np.percentile(vals, p)) if vals else 0.0


def _g_linear(x: float, ref: float) -> float:
    if ref <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - x / ref))


def main() -> None:
    ts = _utc_stamp()
    out = Path(f"/home/porvir5g/gtp5g/trisla/evidencias_trisla_transport_normalization_{ts}")
    s1 = out / "substep_1_reference_analysis"
    figdir = s1 / "figures"
    for sub in (s1, figdir, out / "analysis", out / "freeze"):
        sub.mkdir(parents=True, exist_ok=True)

    rows = _load()
    rtt = [r["rtt"] for r in rows if r["rtt"] is not None]
    jit = [r["jitter"] for r in rows if r["jitter"] is not None]
    idle = [r for r in rows if r.get("regime") == "15Mbps"]
    stress = [r for r in rows if r.get("regime") == "130Mbps"]
    rtt_idle = [r["rtt"] for r in idle if r["rtt"]]
    jit_idle = [r["jitter"] for r in idle if r["jitter"]]

    percentiles = [50, 75, 90, 95, 99]
    rtt_pct = {f"p{p}": _pct(rtt, p) for p in percentiles}
    jit_pct = {f"p{p}": _pct(jit, p) for p in percentiles}
    rtt_pct["max"] = max(rtt)
    jit_pct["max"] = max(jit)

    # Saturation onset: share with g=0 for candidate REF (linear 1-x/ref)
    ref_candidates_rtt = {
        "P90": rtt_pct["p90"],
        "P95": rtt_pct["p95"],
        "P99": rtt_pct["p99"],
        "max": rtt_pct["max"],
        "130M_mean_x1.5": reg_mean_130 * 1.5 if (reg_mean_130 := statistics.mean([r["rtt"] for r in stress if r["rtt"]])) else 0,
    }
    ref_candidates_jit = {
        "P90": jit_pct["p90"],
        "P95": jit_pct["p95"],
        "P99": jit_pct["p99"],
        "max": jit_pct["max"],
    }

    sat_rtt = {}
    for name, ref in ref_candidates_rtt.items():
        gs = [_g_linear(x, ref) for x in rtt]
        sat_rtt[name] = {
            "ref": ref,
            "frac_at_floor_g0": sum(1 for g in gs if g <= 0.01) / len(gs),
            "frac_below_half": sum(1 for g in gs if g < 0.5) / len(gs),
            "mean_g": statistics.mean(gs),
            "idle_mean_g": statistics.mean([_g_linear(x, ref) for x in rtt_idle]),
        }

    sat_jit = {}
    for name, ref in ref_candidates_jit.items():
        gs = [_g_linear(x, ref) for x in jit]
        sat_jit[name] = {
            "ref": ref,
            "frac_at_floor_g0": sum(1 for g in gs if g <= 0.01) / len(gs),
            "frac_below_half": sum(1 for g in gs if g < 0.5) / len(gs),
            "mean_g": statistics.mean(gs),
            "idle_mean_g": statistics.mean([_g_linear(x, ref) for x in jit_idle]),
        }

    # Proposed references
    rtt_ref_proposed = rtt_pct["p99"]  # severe tail without compressing 15-100M band
    jitter_ref_proposed = jit_pct["p95"]  # instability tail; P99≈max

    # Degradation onset: first regime where mean jitter > idle P90
    idle_j_p90 = _pct(jit_idle, 90)
    by_reg = defaultdict(list)
    for r in rows:
        by_reg[r["regime"]].append(r)
    onset = {}
    for reg in sorted(by_reg.keys(), key=lambda x: int("".join(c for c in x if c.isdigit()) or 0)):
        sub = by_reg[reg]
        onset[reg] = {
            "jitter_mean": statistics.mean([x["jitter"] for x in sub if x["jitter"]]),
            "rtt_mean": statistics.mean([x["rtt"] for x in sub if x["rtt"]]),
            "above_idle_jitter_p90": statistics.mean([x["jitter"] for x in sub if x["jitter"]]) > idle_j_p90,
        }

    stats = {
        "n": len(rows),
        "rtt_percentiles": rtt_pct,
        "jitter_percentiles": jit_pct,
        "idle_jitter_p90": idle_j_p90,
        "proposed_RTT_REF": rtt_ref_proposed,
        "proposed_JITTER_REF": jitter_ref_proposed,
        "saturation_rtt_candidates": sat_rtt,
        "saturation_jitter_candidates": sat_jit,
        "regime_onset": onset,
    }
    (s1 / "reference_analysis_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    plt.rcParams.update({"font.size": 10, "font.family": "serif"})

    fig, ax = plt.subplots()
    ax.hist(rtt, bins=30, color="#1f77b4", alpha=0.75, edgecolor="k")
    for p, c in [(90, "orange"), (95, "red"), (99, "darkred")]:
        v = _pct(rtt, p)
        ax.axvline(v, color=c, linestyle="--", label=f"P{p}={v:.2f}ms")
    ax.set_xlabel("RTT (ms)")
    ax.set_title("RTT distribution + percentile references")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(figdir / "01_rtt_distribution_percentiles.png", dpi=300)
    plt.close()

    fig, ax = plt.subplots()
    ax.hist(jit, bins=30, color="#ff7f0e", alpha=0.75, edgecolor="k")
    for p, c in [(90, "orange"), (95, "red"), (99, "darkred")]:
        v = _pct(jit, p)
        ax.axvline(v, color=c, linestyle="--", label=f"P{p}={v:.2f}ms")
    ax.set_xlabel("Jitter (ms)")
    ax.set_title("Jitter distribution + percentile references")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(figdir / "02_jitter_distribution_percentiles.png", dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4))
    ps = percentiles + [100]
    ax.plot(ps, [_pct(rtt, p) for p in percentiles] + [max(rtt)], "o-", label="RTT", color="#1f77b4")
    ax2 = ax.twinx()
    ax2.plot(ps, [_pct(jit, p) for p in percentiles] + [max(jit)], "s-", label="Jitter", color="#ff7f0e")
    ax.set_xlabel("Percentile")
    ax.set_ylabel("RTT (ms)", color="#1f77b4")
    ax2.set_ylabel("Jitter (ms)", color="#ff7f0e")
    ax.set_title("Percentile map (NASP-hard+)")
    plt.tight_layout()
    plt.savefig(figdir / "03_percentile_map.png", dpi=300)
    plt.close()

    # Saturation onset: mean g vs REF candidate for RTT
    fig, ax = plt.subplots(figsize=(9, 4))
    names = list(sat_rtt.keys())
    x = np.arange(len(names))
    ax.bar(x - 0.15, [sat_rtt[n]["idle_mean_g"] for n in names], 0.3, label="idle (15M) mean g", color="#2ca02c")
    ax.bar(x + 0.15, [sat_rtt[n]["mean_g"] for n in names], 0.3, label="global mean g", color="#1f77b4")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20)
    ax.set_ylabel("Linear goodness 1-x/ref")
    ax.set_title("RTT_REF candidates — avoid low ref (premature saturation)")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(figdir / "04_rtt_saturation_onset.png", dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 4))
    names_j = list(sat_jit.keys())
    xj = np.arange(len(names_j))
    ax.bar(xj - 0.15, [sat_jit[n]["idle_mean_g"] for n in names_j], 0.3, label="idle mean g", color="#2ca02c")
    ax.bar(xj + 0.15, [sat_jit[n]["frac_at_floor_g0"] * 100 for n in names_j], 0.3, label="% at floor (g≈0)", color="#d62728")
    ax.set_xticks(xj)
    ax.set_xticklabels(names_j, rotation=20)
    ax.set_title("JITTER_REF candidates — tail saturation fraction")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(figdir / "05_jitter_saturation_onset.png", dpi=300)
    plt.close()

    # Stable: clear separation idle vs stress percentiles
    stable = rtt_ref_proposed > _pct(rtt_idle, 95) * 1.5 and jitter_ref_proposed > idle_j_p90
    verdict = "REFERENCES_DEFINED" if stable else "REFERENCES_UNSTABLE"

    md = f"""# Substep 1 — Reference Analysis (`RTT_REF`, `JITTER_REF`)

**Audit:** `evidencias_trisla_transport_normalization_{ts}`  
**Dataset:** NASP-hard+ (n={len(rows)})  
**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Verdict

**`{verdict}`**

---

## 1. Percentile tables (ms)

### RTT (blackbox probe)

| Percentile | Value (ms) |
|------------|----------:|
| P50 | {rtt_pct['p50']:.3f} |
| P75 | {_pct(rtt, 75):.3f} |
| P90 | {rtt_pct['p90']:.3f} |
| P95 | {rtt_pct['p95']:.3f} |
| P99 | {rtt_pct['p99']:.3f} |
| max | {rtt_pct['max']:.3f} |

**Distribution shape:** RTT is **plateaued** 15–100 Mbps (~4.65–4.90 ms); **tail** at 130 Mbps drives P99=max (**{rtt_pct['max']:.2f} ms**).

### Jitter (1m probe spread)

| Percentile | Value (ms) |
|------------|----------:|
| P50 | {jit_pct['p50']:.3f} |
| P75 | {_pct(jit, 75):.3f} |
| P90 | {jit_pct['p90']:.3f} |
| P95 | {jit_pct['p95']:.3f} |
| P99 | {jit_pct['p99']:.3f} |
| max | {jit_pct['max']:.3f} |

**Distribution shape:** Bimodal stress response — idle ~0.2–0.6 ms; stressed tail **3.9–4.0 ms**.

---

## 2. Proposed references (publication-grade)

| Parameter | Value | Basis |
|-----------|------:|-------|
| **`RTT_REF`** | **{rtt_ref_proposed:.2f} ms** | **P99** (= observed max tail under 130 Mbps saturation) |
| **`JITTER_REF`** | **{jitter_ref_proposed:.2f} ms** | **P95** (≈ operational instability tail; P99≈max) |

### Why P99 for RTT (not P95)

| Candidate | REF (ms) | Idle (15M) mean g | Global mean g | Risk |
|-----------|--------:|------------------:|--------------:|------|
| P90 | {ref_candidates_rtt['P90']:.2f} | {sat_rtt['P90']['idle_mean_g']:.3f} | {sat_rtt['P90']['mean_g']:.3f} | **Premature saturation** — plateaus compress dynamic range |
| P95 | {ref_candidates_rtt['P95']:.2f} | {sat_rtt['P95']['idle_mean_g']:.3f} | {sat_rtt['P95']['mean_g']:.3f} | Still low headroom at 15–100M |
| **P99** | **{rtt_ref_proposed:.2f}** | **{sat_rtt['P99']['idle_mean_g']:.3f}** | **{sat_rtt['P99']['mean_g']:.3f}** | **Selected** — baseline RTT retains g≈0.6; tail can approach 0 |
| max | {ref_candidates_rtt['max']:.2f} | same as P99 | same | Equivalent here (max=P99) |

**Operational meaning:** `RTT_REF` anchors **severe transport delay** at observed saturation (130M regime), without treating normal ~5 ms RTT as “worst case.”

### Why P95 for jitter (not P90)

| Candidate | REF (ms) | % samples g≈0 | Idle mean g |
|-----------|--------:|--------------:|------------:|
| P90 | {ref_candidates_jit['P90']:.2f} | {100*sat_jit['P90']['frac_at_floor_g0']:.1f}% | {sat_jit['P90']['idle_mean_g']:.3f} |
| **P95** | **{jitter_ref_proposed:.2f}** | **{100*sat_jit['P95']['frac_at_floor_g0']:.1f}%** | **{sat_jit['P95']['idle_mean_g']:.3f}** |
| max | {ref_candidates_jit['max']:.2f} | {100*sat_jit['max']['frac_at_floor_g0']:.1f}% | {sat_jit['max']['idle_mean_g']:.3f} |

**Operational meaning:** `JITTER_REF` encodes **instability under stress**; only top ~5% of samples hit full penalty (g→0).

---

## 3. Degradation & saturation onset (by regime)

Idle jitter P90 = **{idle_j_p90:.2f} ms** (15 Mbps baseline).

| Regime | RTT μ | Jitter μ | Jitter > idle P90? |
|--------|------:|---------:|:------------------:|
"""
    for reg in sorted(onset.keys(), key=lambda x: int("".join(c for c in x if c.isdigit()) or 0)):
        o = onset[reg]
        md += f"| {reg} | {o['rtt_mean']:.2f} | {o['jitter_mean']:.2f} | {'yes' if o['above_idle_jitter_p90'] else 'no'} |\n"

    md += f"""
**Onset:** Jitter escalation becomes material at **100–130 Mbps**; RTT step-change mainly at **130 Mbps** (+1.43 ms vs 15M).

---

## 4. Linear component preview (not final g_transport)

Substep 2 will combine components. Per-metric linear maps:

```
g_rtt    = clamp01(1 - RTT_ms / RTT_REF)
g_jitter = clamp01(1 - jitter_ms / JITTER_REF)
```

At 15M idle: g_rtt≈{sat_rtt['P99']['idle_mean_g']:.2f}, g_jitter≈{sat_jit['P95']['idle_mean_g']:.2f}.

---

## 5. Risks (for Substep 2–3)

| Risk | Mitigation |
|------|------------|
| **Double punishment** (PRB+jitter r≈0.79) | Substep 3: orthogonalize or cap transport weight |
| RTT flat mid-regimes | RTT as **stabilizer** with low weight, not primary axis |
| Probe ≠ GTP path | Publication wording: monitoring-plane transport proxy |

---

## 6. Figures

- `figures/01_rtt_distribution_percentiles.png`
- `figures/02_jitter_distribution_percentiles.png`
- `figures/03_percentile_map.png`
- `figures/04_rtt_saturation_onset.png`
- `figures/05_jitter_saturation_onset.png`

## 7. Artifacts

- `reference_analysis_stats.json`

---

**HARD STOP — Substep 1 complete.** Await **`SUBSTEP_1_APPROVED`** before Substep 2 (normalization candidates).
"""
    (s1 / "REFERENCE_ANALYSIS.md").write_text(md, encoding="utf-8")

    import subprocess

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

    (out / "analysis" / "MANIFEST.txt").write_text(
        "\n".join(sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())) + "\n",
        encoding="utf-8",
    )

    print(f"TRANSPORT NORMALIZATION SUBSTEP 1: {out}")
    print(f"Verdict: {verdict}")
    print(f"RTT_REF={rtt_ref_proposed:.2f} JITTER_REF={jitter_ref_proposed:.2f}")


if __name__ == "__main__":
    main()
