#!/usr/bin/env python3
"""NASP-hard+ Phase 1: extreme legitimate UE→N6 stress with correct iperf path."""

from __future__ import annotations

import json
import os
import statistics
import subprocess
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
    PRB_PROXY_PROMQL,
    _extract_row,
    _http_json,
    _submit,
    _utc_stamp,
)

REPS = int(os.getenv("NASP_HARD_REPS", "30"))
PAUSE = float(os.getenv("NASP_HARD_PAUSE_S", "1.2"))
WARMUP = float(os.getenv("NASP_HARD_WARMUP_S", "75"))
IPERF_DURATION = int(os.getenv("NASP_HARD_IPERF_S", "450"))
IPERF_TARGET = os.getenv("TRISLA_IPERF_TARGET", "192.168.100.51")


@dataclass(frozen=True)
class Regime:
    label: str
    bitrate: str


REGIMES = [
    Regime("15Mbps", "15M"),
    Regime("40Mbps", "40M"),
    Regime("70Mbps", "70M"),
    Regime("100Mbps", "100M"),
    Regime("130Mbps", "130M"),
]


def _query_proxy_prb() -> Optional[float]:
    from scientific_multidomain_ieee_campaign import _query_proxy_prb as q

    return q()


def _start_iperf(bitrate: str, duration_s: int) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [
            "kubectl",
            "-n",
            "ueransim",
            "exec",
            "deploy/ueransim-singlepod",
            "-c",
            "ue",
            "--",
            "iperf3",
            "-c",
            IPERF_TARGET,
            "-u",
            "-b",
            bitrate,
            "-t",
            str(duration_s),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _stop(proc: Optional[subprocess.Popen[bytes]]) -> None:
    if proc is None:
        return
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_regime(out: Path, reg: Regime) -> list[dict[str, Any]]:
    raw = out / "raw" / reg.label
    raw.mkdir(parents=True, exist_ok=True)
    proc = _start_iperf(reg.bitrate, IPERF_DURATION)
    time.sleep(WARMUP)
    rows: list[dict[str, Any]] = []
    run_tag = _utc_stamp()
    for i in range(REPS):
        tenant = f"nasp-{run_tag}-{reg.label}-{i:03d}"
        result = _submit(tenant, f"nasp_{reg.label}_{i}")
        payload = result["payload"]
        meta = payload.get("metadata") or {}
        snap = meta.get("telemetry_snapshot") or {}
        ran = snap.get("ran") or {}
        proxy_prb = _query_proxy_prb()
        row = _extract_row(
            run_tag,
            reg.label,
            reg.label,
            {
                "regime_mbps": reg.label,
                "iperf_bitrate": reg.bitrate,
                "proxy_prb_at_submit": proxy_prb,
            },
            result,
        )
        row["ran_prb_input"] = meta.get("ran_prb_utilization_input")
        row["snapshot_prb"] = ran.get("prb_utilization")
        row["ml_risk_score"] = meta.get("ml_risk_score")
        row["ml_confidence"] = meta.get("confidence_score")
        row["tx_hash"] = payload.get("tx_hash")
        row["bc_status"] = payload.get("bc_status")
        row["sla_agent_status"] = payload.get("sla_agent_status")
        rows.append(row)
        (raw / f"submit_{i:03d}.json").write_text(
            json.dumps({"row": row, "payload": payload}, indent=2), encoding="utf-8"
        )
        with (raw / "submit_rows.jsonl").open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")
        time.sleep(PAUSE)
    _stop(proc)
    return rows


def _stats(vals: list[float]) -> dict[str, float]:
    if not vals:
        return {}
    return {
        "min": min(vals),
        "max": max(vals),
        "mean": statistics.mean(vals),
        "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
    }


def write_report(out: Path, all_rows: list[dict[str, Any]]) -> None:
    by_reg: dict[str, list[dict[str, Any]]] = {}
    for r in all_rows:
        by_reg.setdefault(str(r.get("regime_mbps")), []).append(r)

    lines = [
        "# Phase 1 — Extreme Runtime Stress",
        "",
        f"**Backend:** {BACKEND_URL}  ",
        f"**PRB PromQL:** `{PRB_PROXY_PROMQL}`  ",
        f"**iperf:** UE → `{IPERF_TARGET}` (no erroneous `-B 10.1.0.1`)  ",
        f"**Reps/regime:** {REPS}  ",
        "",
        "## Per-regime summary",
        "",
        "| Regime | PRB input (mean±std) | Score (mean±std) | Decisions |",
        "|--------|----------------------|------------------|-----------|",
    ]
    prb_all: list[float] = []
    score_all: list[float] = []
    for label in [r.label for r in REGIMES]:
        rows = by_reg.get(label, [])
        prb = [float(x["ran_prb_input"]) for x in rows if x.get("ran_prb_input") is not None]
        sc = [float(x["decision_score"]) for x in rows if x.get("decision_score") is not None]
        prb_all.extend(prb)
        score_all.extend(sc)
        dec = Counter(str(x.get("decision")) for x in rows)
        ps = _stats(prb)
        ss = _stats(sc)
        lines.append(
            f"| {label} | {ps.get('mean', 0):.2f}±{ps.get('std', 0):.2f} "
            f"[{ps.get('min', 0):.1f},{ps.get('max', 0):.1f}] | "
            f"{ss.get('mean', 0):.3f}±{ss.get('std', 0):.3f} | {dict(dec)} |"
        )

    if prb_all and score_all:
        n = min(len(prb_all), len(score_all))
        mx = sum(prb_all[i] * score_all[i] for i in range(n)) / n
        mp = sum(prb_all) / n
        ms = sum(score_all) / n
        sp = (sum((prb_all[i] - mp) ** 2 for i in range(n)) / max(n - 1, 1)) ** 0.5
        ss = (sum((score_all[i] - ms) ** 2 for i in range(n)) / max(n - 1, 1)) ** 0.5
        corr = (mx - mp * ms) / (sp * ss) if sp > 0 and ss > 0 else 0.0
        lines.extend(["", f"**Overall corr(PRB, score):** {corr:.3f}", ""])

    sat = max(prb_all) if prb_all else 0
    lines.extend(
        [
            f"**PRB saturation (max):** {sat:.2f}% (cap proxy 100 Mbps → theoretical max ~100%)",
            "",
            "## Note on prior maximize campaign",
            "",
            "`evidencias_trisla_maximize_paper_runtime_final_*` used broken iperf `-B 10.1.0.1`; "
            "PRB≈0 there — **not** used for NASP-hard+.",
            "",
        ]
    )
    ok = sat > 5 and len(prb_all) >= REPS
    lines.append(f"## Verdict\n\n# **{'EXTREME_STRESS_SUCCESS' if ok else 'EXTREME_STRESS_FAILED'}**")
    (out / "EXTREME_STRESS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    out = Path(os.environ["NASP_HARD_OUT"]) / "phase_1_extreme_runtime_stress"
    out.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, Any]] = []
    for reg in REGIMES:
        print(f"=== {reg.label} ===", flush=True)
        all_rows.extend(run_regime(out, reg))
    # CSV without pandas
    import csv

    csv_path = out / "extreme_stress_dataset.csv"
    if all_rows:
        keys = list(all_rows[0].keys())
        with csv_path.open("w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_rows)
    write_report(out, all_rows)
    print(json.dumps({"n": len(all_rows), "csv": str(csv_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
