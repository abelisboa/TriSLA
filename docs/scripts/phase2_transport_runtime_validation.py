#!/usr/bin/env python3
"""Phase 2 — post-deploy validation: transport_rtt_goodness in score_mode."""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))
from scientific_multidomain_ieee_campaign import (  # noqa: E402
    _extract_row,
    _submit,
    _utc_stamp,
)

OUT_PARENT = Path("/home/porvir5g/gtp5g/trisla")


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = min(len(xs), len(ys))
    if n < 3:
        return None
    mx, my = statistics.mean(xs[:n]), statistics.mean(ys[:n])
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = sum((xs[i] - mx) ** 2 for i in range(n)) ** 0.5
    dy = sum((ys[i] - my) ** 2 for i in range(n)) ** 0.5
    return num / (dx * dy) if dx and dy else None


def main() -> None:
    ts = _utc_stamp()
    out = OUT_PARENT / f"evidencias_trisla_phase2_de_runtime_integration_{ts}"
    val = out / "phase_4_runtime_validation"
    val.mkdir(parents=True, exist_ok=True)
    raw = val / "raw"
    raw.mkdir(exist_ok=True)

    rows = []
    for i in range(3):
        doc = _submit("default", f"phase2_transport_val_{i}")
        (raw / f"submit_{i}.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
        row = _extract_row(doc)
        row["submit_idx"] = i
        rows.append(row)
        time.sleep(2)

    score_rows = [r for r in rows if r.get("decision_source") == "decision_score_mode"]
    transport_hits = 0
    recon_err = []
    for r in score_rows:
        meta = r.get("metadata") or {}
        factors = meta.get("contributing_factors") or []
        tr = [f for f in factors if f.get("factor") == "transport_rtt_goodness"]
        if tr:
            transport_hits += 1
        score = r.get("decision_score")
        if score is not None and factors:
            calc = sum(f.get("contribution", 0) for f in factors) / sum(f.get("weight", 0) for f in factors)
            recon_err.append(abs(float(score) - calc))

    prb = [float(r["ran_prb_input"]) for r in score_rows if r.get("ran_prb_input") is not None]
    scores = [float(r["decision_score"]) for r in score_rows if r.get("decision_score") is not None]

    verdict = (
        "RUNTIME_VALIDATION_SUCCESS"
        if transport_hits >= 1 and (not recon_err or max(recon_err) < 1e-4)
        else "RUNTIME_VALIDATION_FAILED"
    )

    md = f"""# Phase 4 — Runtime Validation (smoke)

**UTC:** {datetime.now(timezone.utc).isoformat()}  
**Submits:** n={len(rows)}  
**score_mode:** n={len(score_rows)}  
**transport_rtt_goodness present:** {transport_hits}/{len(score_rows)}  
**Verdict:** `{verdict}`

## Checks

| Check | Result |
|-------|--------|
| transport_rtt_goodness in contributing_factors | {transport_hits >= 1} |
| Score reconstruction | max err={max(recon_err) if recon_err else 'n/a'} |
| r(PRB,score) score_mode | {_pearson(prb, scores)} |

## Sample factors

"""
    if score_rows:
        meta = score_rows[0].get("metadata") or {}
        md += "```json\n" + json.dumps(meta.get("contributing_factors"), indent=2)[:2000] + "\n```\n"

    (val / "RUNTIME_VALIDATION.md").write_text(md, encoding="utf-8")
    (val / "validation_stats.json").write_text(
        json.dumps(
            {
                "verdict": verdict,
                "transport_hits": transport_hits,
                "n_score_mode": len(score_rows),
                "recon_err": recon_err,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"{verdict} -> {val}")
    return 0 if verdict.endswith("SUCCESS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
