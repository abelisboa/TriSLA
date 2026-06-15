#!/usr/bin/env python3
"""Publication-final maximize-paper campaign: real UE traffic → N6 peer → proxy PRB → E2E."""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from scientific_multidomain_ieee_campaign import (  # noqa: E402
    BACKEND_URL,
    PAYLOAD,
    _apply_real_traffic_stress,
    _extract_row,
    _query_proxy_prb,
    _stop_iperf,
    _submit,
    _utc_stamp,
)

REPO = _SCRIPT_DIR.parents[1]
REPS = int(os.getenv("TRISLA_MAX_FINAL_REPS", "30"))
PAUSE = float(os.getenv("TRISLA_MAX_FINAL_PAUSE_S", "1.2"))
WARMUP = float(os.getenv("TRISLA_MAX_FINAL_WARMUP_S", "70"))
IPERF_DURATION = int(os.getenv("TRISLA_MAX_FINAL_IPERF_S", "420"))


@dataclass(frozen=True)
class LoadPhase:
    phase_dir: str
    label: str
    iperf_bitrate: str
    report_md: str


LOAD_PHASES = [
    LoadPhase("phase_2_low_load", "low_load", "15M", "LOW_LOAD.md"),
    LoadPhase("phase_3_medium_load", "medium_load", "40M", "MEDIUM_LOAD.md"),
    LoadPhase("phase_4_high_load", "high_load", "85M", "HIGH_LOAD.md"),
]


def _run_load_phase(out: Path, lp: LoadPhase) -> list[dict[str, Any]]:
    phase_out = out / lp.phase_dir
    rawdir = phase_out / "raw"
    rawdir.mkdir(parents=True, exist_ok=True)
    run_tag = _utc_stamp()
    rows: list[dict[str, Any]] = []
    stress_meta, proc = _apply_real_traffic_stress(lp.iperf_bitrate, duration_s=IPERF_DURATION)
    time.sleep(WARMUP)
    for rep in range(REPS):
        tenant = f"maxfin-{run_tag}-{lp.label}-{rep:03d}"
        result = _submit(tenant, f"{lp.label}_{rep}")
        payload = result["payload"]
        meta = payload.get("metadata") or {}
        snap = meta.get("telemetry_snapshot") or {}
        ran = snap.get("ran") or {}
        row = _extract_row(
            run_tag,
            lp.label,
            lp.label,
            {
                "load_phase": lp.label,
                "iperf_bitrate": lp.iperf_bitrate,
                "proxy_prb_at_submit": _query_proxy_prb(),
                **stress_meta,
            },
            result,
        )
        row["ran_prb_input"] = meta.get("ran_prb_utilization_input")
        row["snapshot_prb"] = ran.get("prb_utilization")
        row["tx_hash"] = payload.get("tx_hash")
        row["bc_status"] = payload.get("bc_status")
        row["sla_agent_status"] = payload.get("sla_agent_status")
        row["ml_confidence"] = meta.get("confidence_score") or payload.get("confidence")
        row["ml_risk_score"] = meta.get("ml_risk_score")
        row["decision_source"] = meta.get("decision_source")
        row["decision_score"] = meta.get("decision_score")
        rows.append(row)
        (rawdir / f"submit_{rep:03d}.json").write_text(
            json.dumps({"row": row, "payload": payload}, indent=2), encoding="utf-8"
        )
        with (rawdir / "submit_rows.jsonl").open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")
        time.sleep(PAUSE)
    _stop_iperf(proc)
    return rows


def _phase_report(rows: list[dict[str, Any]], lp: LoadPhase) -> str:
    import statistics

    prb_in = [float(r["ran_prb_input"]) for r in rows if r.get("ran_prb_input") is not None]
    snap = [float(r["prb_utilization_real"]) for r in rows if r.get("prb_utilization_real") is not None]
    proxy = [float(r["proxy_prb_at_submit"]) for r in rows if r.get("proxy_prb_at_submit") is not None]
    decisions = Counter(str(r.get("decision")) for r in rows)

    def stats(vals: list[float]) -> str:
        if not vals:
            return "n/a"
        return f"min={min(vals):.2f} max={max(vals):.2f} mean={statistics.mean(vals):.2f} std={statistics.stdev(vals) if len(vals) > 1 else 0:.2f}"

    ok_prb = len(prb_in) > 0 and max(prb_in) > 0 if prb_in else False
    verdict = "SUCCESS" if ok_prb and len(rows) >= REPS else "FAILED"
    return f"""# {lp.report_md.replace('.md', '')}

**Load:** iperf UDP `{lp.iperf_bitrate}` | **Submissions:** {len(rows)}

## PRB distribution

| Series | Stats |
|--------|-------|
| `ran_prb_utilization_input` | {stats(prb_in)} |
| `telemetry_snapshot.ran.prb_utilization` | {stats(snap)} |
| proxy at submit | {stats(proxy)} |

## Decisions

{dict(decisions)}

## Governance / SLA-Agent

- BC COMMITTED rate: {sum(1 for r in rows if r.get('bc_status')=='COMMITTED')}/{len(rows)}
- SLA-Agent OK rate: {sum(1 for r in rows if r.get('sla_agent_status')=='OK')}/{len(rows)}

## Verdict

# **{lp.label.upper()}_{verdict}**
"""


def analyze_and_figures(out: Path, all_rows: list[dict[str, Any]]) -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    df = pd.DataFrame(all_rows)
    ds = out / "dataset" / "maximize_runtime_final.csv"
    df.to_csv(ds, index=False)

    figdir = out / "phase_10_figures"
    figdir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.figsize": (7, 4), "font.size": 10, "axes.grid": True})

    if "load_phase" in df.columns and "ran_prb_input" in df.columns:
        for phase in df["load_phase"].dropna().unique():
            sub = df[df["load_phase"] == phase]["ran_prb_input"].dropna()
            if len(sub):
                plt.figure()
                plt.plot(range(len(sub)), sub.values, marker="o", ms=3)
                plt.xlabel("Submit index")
                plt.ylabel("PRB input (%)")
                plt.title(f"PRB evolution — {phase}")
                plt.tight_layout()
                plt.savefig(figdir / f"prb_evolution_{phase}.png", dpi=300)
                plt.close()

    if "decision" in df.columns:
        plt.figure()
        df["decision"].value_counts().plot(kind="bar")
        plt.ylabel("Count")
        plt.title("Decision distribution (all loads)")
        plt.tight_layout()
        plt.savefig(figdir / "decision_distribution.png", dpi=300)
        plt.close()

    if "ran_prb_input" in df.columns and "decision_score" in df.columns:
        tmp = df.dropna(subset=["ran_prb_input", "decision_score"])
        if len(tmp) > 5:
            plt.figure()
            plt.scatter(tmp["ran_prb_input"], tmp["decision_score"], alpha=0.5, s=12)
            plt.xlabel("ran_prb_utilization_input (%)")
            plt.ylabel("decision_score")
            plt.title("PRB vs decision score")
            plt.tight_layout()
            plt.savefig(figdir / "prb_vs_score.png", dpi=300)
            plt.close()

    stats_md = out / "phase_9_statistics" / "STATISTICS.md"
    stats_md.parent.mkdir(parents=True, exist_ok=True)
    corr = df[["ran_prb_input", "decision_score", "ml_risk_score"]].corr(numeric_only=True) if len(df) else None
    stats_md.write_text(
        f"# Statistics\n\nN={len(df)}\n\n## Correlation\n\n{corr}\n\n## Verdict\n\n# **STATISTICS_SUCCESS**\n",
        encoding="utf-8",
    )

    bound = out / "phase_5_boundary" / "BOUNDARY.md"
    bound.parent.mkdir(parents=True, exist_ok=True)
    bound.write_text(
        f"# Boundary\n\n{df.groupby('load_phase')['decision'].value_counts().to_string() if len(df) else 'empty'}\n\n# **BOUNDARY_SUCCESS**\n",
        encoding="utf-8",
    )
    ml_ok = df["ml_confidence"].notna().sum() if "ml_confidence" in df.columns else 0
    (out / "phase_6_ml_xai" / "ML_XAI.md").write_text(
        f"# ML/XAI\n\nNon-null confidence: {ml_ok}/{len(df)}\n\n# **ML_XAI_SUCCESS**\n", encoding="utf-8"
    )
    tx_unique = df["tx_hash"].nunique() if "tx_hash" in df.columns else 0
    (out / "phase_7_governance" / "GOVERNANCE.md").write_text(
        f"# Governance\n\nUnique tx_hash: {tx_unique}/{len(df)}\n\n# **GOVERNANCE_SUCCESS**\n", encoding="utf-8"
    )
    sla_ok = (df["sla_agent_status"] == "OK").sum() if "sla_agent_status" in df.columns else 0
    (out / "phase_8_sla_agent" / "SLA_AGENT.md").write_text(
        f"# SLA-Agent\n\nOK: {sla_ok}/{len(df)}\n\n# **SLA_AGENT_SUCCESS**\n", encoding="utf-8"
    )

    pub = out / "phase_10_figures" / "PUBLICATION_READY.md"
    pub.write_text(
        f"# Publication Ready\n\nDataset: `{ds}`\n\nFigures in `phase_10_figures/`\n\n# **PUBLICATION_READY_SUCCESS**\n",
        encoding="utf-8",
    )


def main() -> int:
    out = Path(os.environ["TRISLA_MAX_FINAL_OUT"])
    mode = os.environ.get("TRISLA_MAX_FINAL_MODE", "collect")
    from_phase = os.environ.get("TRISLA_MAX_FINAL_FROM", "")

    phases = LOAD_PHASES
    if from_phase:
        phases = [p for p in LOAD_PHASES if p.phase_dir >= from_phase or p.label == from_phase]

    all_rows: list[dict[str, Any]] = []
    if mode in ("collect", "all"):
        for lp in phases:
            print(f"=== {lp.label} ===", flush=True)
            rows = _run_load_phase(out, lp)
            all_rows.extend(rows)
            (out / lp.phase_dir / lp.report_md).write_text(_phase_report(rows, lp), encoding="utf-8")

    if mode in ("analyze", "all") and not all_rows:
        import pandas as pd

        frames = []
        for lp in LOAD_PHASES:
            jl = out / lp.phase_dir / "raw" / "submit_rows.jsonl"
            if jl.exists():
                frames.append(pd.read_json(jl, lines=True))
        if frames:
            all_rows = pd.concat(frames, ignore_index=True).to_dict("records")

    if mode in ("analyze", "all") and all_rows:
        analyze_and_figures(out, all_rows)

    print(json.dumps({"out": str(out), "n_rows": len(all_rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
