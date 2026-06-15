#!/usr/bin/env python3
"""TriSLA maximize-paper: progressive multidomain stress via real UE traffic (proxy-only PRB)."""

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
    IPERF_WARMUP_S,
    SUBMIT_PAUSE_S,
    _apply_real_traffic_stress,
    _extract_row,
    _query_proxy_prb,
    _stop_iperf,
    _utc_stamp,
)

REPO = _SCRIPT_DIR.parents[1]
REPS = int(os.getenv("TRISLA_MAX_REPS", "25"))
PAUSE = float(os.getenv("TRISLA_MAX_SUBMIT_PAUSE_S", "1.0"))
SCRAPE_WAIT = float(os.getenv("TRISLA_MAX_PRB_WAIT_S", "30"))


@dataclass(frozen=True)
class StressPhase:
    phase_id: str
    iperf_bitrate: Optional[str]
    template_id: str
    service_type: str
    form_values: dict[str, Any]


PHASES: list[StressPhase] = [
    StressPhase("p1_low", None, "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "5ms", "reliability": 0.999, "throughput": "50Mbps"}),
    StressPhase("p1_low", "10M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "5ms", "reliability": 0.999, "throughput": "50Mbps"}),
    StressPhase("p2_moderate", "25M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "2ms", "reliability": 0.99999, "throughput": "100Mbps"}),
    StressPhase("p2_moderate", "40M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "2ms", "reliability": 0.99999, "throughput": "200Mbps"}),
    StressPhase("p3_transition", "60M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "500Mbps"}),
    StressPhase("p3_transition", "75M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "500Mbps"}),
    StressPhase("p3_transition", "85M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "800Mbps"}),
    StressPhase("p4_congestion", "95M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "900Mbps"}),
    StressPhase("p4_congestion", "100M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "900Mbps"}),
    StressPhase("p4_congestion", "110M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "900Mbps"}),
    StressPhase("p5_instability", "120M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "900Mbps"}),
    StressPhase("p5_instability", "130M", "urllc-template-001", "URLLC", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "900Mbps"}),
]


def _build_payload(phase: StressPhase, tenant: str) -> dict[str, Any]:
    return {
        "template_id": phase.template_id,
        "tenant_id": tenant,
        "form_values": {
            **phase.form_values,
            "service_name": f"maximize {phase.phase_id}",
            "scenario": f"maximize_{phase.phase_id}",
        },
    }


def _submit_phase(phase: StressPhase, tenant: str) -> dict[str, Any]:
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen

    body = _build_payload(phase, tenant)
    t0 = time.time()
    data = json.dumps(body).encode("utf-8")
    req = Request(
        f"{BACKEND_URL}/api/v1/sla/submit",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=180.0) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw else {}
    except HTTPError as exc:
        payload = {"decision": "ERROR", "error": str(exc), "metadata": {}}
    return {"http_elapsed_s": time.time() - t0, "payload": payload}


def _enrich_row(row: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("metadata") or {}
    row["slice_type"] = payload.get("service_type")
    row["ml_risk_score"] = meta.get("ml_risk_score") or meta.get("raw_risk_score")
    row["ml_confidence"] = meta.get("confidence_score") or payload.get("confidence")
    row["telemetry_complete"] = meta.get("telemetry_complete")
    row["tx_hash"] = payload.get("tx_hash") or payload.get("blockchain_tx_hash")
    row["bc_status"] = payload.get("bc_status")
    row["sla_agent_status"] = payload.get("sla_agent_status")
    row["contributing_factors"] = json.dumps(meta.get("contributing_factors") or [])
    row["decision_source"] = meta.get("decision_source")
    row["ran_prb_input"] = meta.get("ran_prb_utilization_input")
    return row


def collect(out: Path) -> Path:
    run_tag = _utc_stamp()
    stress_dir = out / "stress_campaign" / f"run_{run_tag}"
    rawdir = stress_dir / "raw"
    procdir = stress_dir / "dataset"
    rawdir.mkdir(parents=True, exist_ok=True)
    procdir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_tag": run_tag,
        "backend": BACKEND_URL,
        "traffic_strategy": "real_ue_iperf_proxy_ssot",
        "reps_per_phase": REPS,
        "phases": len(PHASES),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    (stress_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    rows: list[dict[str, Any]] = []
    from_phase = os.environ.get("TRISLA_MAX_FROM_PHASE", "")
    phase_list = PHASES
    if from_phase:
        idx = next((i for i, p in enumerate(PHASES) if p.phase_id == from_phase), 0)
        phase_list = PHASES[idx:]
    for phase in phase_list:
        stress_meta, proc = _apply_real_traffic_stress(phase.iperf_bitrate)
        time.sleep(SCRAPE_WAIT)
        for rep in range(REPS):
            tenant = f"max-{run_tag}-{phase.phase_id}-{phase.iperf_bitrate or 'idle'}-{rep}"
            result = _submit_phase(phase, tenant)
            payload = result["payload"]
            row = _extract_row(
                run_tag,
                f"maximize_{phase.phase_id}",
                phase.phase_id,
                {
                    "phase_id": phase.phase_id,
                    "iperf_bitrate": phase.iperf_bitrate or "none",
                    "slice_type": phase.service_type,
                    "proxy_prb_at_submit": _query_proxy_prb(),
                    **stress_meta,
                },
                result,
            )
            row = _enrich_row(row, payload)
            rows.append(row)
            with (rawdir / "submit_rows.jsonl").open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(row, ensure_ascii=False) + "\n")
            time.sleep(PAUSE)
        _stop_iperf(proc)

    import pandas as pd

    df = pd.DataFrame(rows)
    csv_path = procdir / "maximize_dataset.csv"
    df.to_csv(csv_path, index=False)
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["n"] = len(df)
    manifest["decisions"] = dict(Counter(df["decision"].dropna().astype(str)))
    (stress_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return csv_path


def main() -> int:
    ts = os.environ.get("OUT_STAMP") or _utc_stamp()
    out = REPO / f"evidencias_trisla_maximize_paper_{ts}"
    for sub in (
        "runtime",
        "stress_campaign",
        "boundary_campaign",
        "multidomain_campaign",
        "dataset",
        "figures",
        "statistics",
        "analysis",
        "validation",
        "freeze",
        "paper_ready",
        "correction_plan",
    ):
        (out / sub).mkdir(parents=True, exist_ok=True)

    mode = os.environ.get("TRISLA_MAX_MODE", "collect")
    if mode == "collect":
        path = collect(out)
        print(path)
        return 0
    print("Use TRISLA_MAX_MODE=analyze with OUT_STAMP after collect", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
