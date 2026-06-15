#!/usr/bin/env python3
"""NAD-EXEC-04 Phase 7: controlled smoke validation (no full campaign)."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))
from nad_boundary_runtime_controls import (  # noqa: E402
    ACTIVE_DIGEST,
    SameStateSynchronizer,
    hard_gate_pre_detect,
    liminal_corridor_validate,
    prb_stabilization_gate,
    score_mode_guard,
    self_test,
    telemetry_convergence_check,
)

BACKEND_URL = os.getenv("TRISLA_BACKEND_URL", "http://192.168.10.15:32002").rstrip("/")
PRB_PROXY_PROMQL = os.getenv(
    "TRISLA_PRB_PROXY_PROMQL",
    'avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})',
)
SMOKE_SUBMITS = int(os.getenv("NAD_SMOKE_SUBMITS", "0"))  # 0 = dry-run only


def _http_json(method: str, url: str, body: Optional[dict] = None, timeout: float = 120.0) -> Any:
    data = None
    headers: dict[str, str] = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _query_proxy_prb() -> Optional[float]:
    url = f"{BACKEND_URL}/api/v1/prometheus/query?" + urlencode({"query": PRB_PROXY_PROMQL})
    try:
        data = _http_json("GET", url, timeout=30.0)
    except Exception as exc:
        return None
    for item in (((data or {}).get("data") or {}).get("result") or []):
        metric = item.get("metric") or {}
        if str(metric.get("job") or "") == "trisla-ran-ue-upf-proxy":
            try:
                return float((item.get("value") or [None, None])[1])
            except (TypeError, ValueError):
                return None
    return None


def _health() -> bool:
    try:
        h = _http_json("GET", f"{BACKEND_URL}/health", timeout=10.0)
        return str(h.get("status", "")).lower() in ("healthy", "ok", "up")
    except Exception:
        return False


def _smoke_submit(slice_key: str) -> dict:
    templates = {
        "URLLC": ("urllc-template-001", {"type": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "100Mbps"}),
        "eMBB": ("embb-template-001", {"type": "eMBB", "latency": "20ms", "reliability": 0.99, "throughput": "500Mbps"}),
        "mMTC": ("mmtc-template-001", {"type": "mMTC", "latency": "100ms", "reliability": 0.95, "throughput": "1Mbps"}),
    }
    tid, fv = templates[slice_key]
    body = {"template_id": tid, "tenant_id": f"nad-smoke-{int(time.time())}", "form_values": dict(fv)}
    t0 = time.time()
    payload = _http_json("POST", f"{BACKEND_URL}/api/v1/sla/submit", body, timeout=180.0)
    meta = payload.get("metadata") or {}
    snap = meta.get("telemetry_snapshot") or {}
    ran = snap.get("ran") or {}
    transport = snap.get("transport") or {}
    sla = meta.get("sla_metrics") or {}
    prb = ran.get("prb_utilization")
    try:
        prb_f = float(prb) if prb is not None else None
    except (TypeError, ValueError):
        prb_f = None
    guard = score_mode_guard(meta, prb_f)
    lim = liminal_corridor_validate(
        prb_pct=prb_f,
        decision_score=float(meta.get("decision_score")) if meta.get("decision_score") is not None else None,
        rtt_ms=float(transport.get("rtt_ms") or transport.get("rtt") or 0) if transport else None,
        feasibility=float(sla.get("feasibility_score")) if sla.get("feasibility_score") is not None else None,
        resource_pressure=float(sla.get("resource_pressure")) if sla.get("resource_pressure") is not None else None,
    )
    return {
        "slice": slice_key,
        "http_elapsed_s": time.time() - t0,
        "decision": payload.get("decision"),
        "decision_mode": meta.get("decision_mode"),
        "decision_score": meta.get("decision_score"),
        "prb_utilization_real": prb_f,
        "guard": guard.__dict__,
        "liminal": lim.__dict__,
    }


def run_smoke(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    report: dict = {"self_test": self_test(), "backend_healthy": _health(), "digest": ACTIVE_DIGEST}
    prb = _query_proxy_prb()
    report["live_proxy_prb"] = prb
    report["hard_gate_pre_detect"] = hard_gate_pre_detect(prb)

    if os.getenv("NAD_SMOKE_QUICK_STABILIZATION", "1") == "1" and prb is not None:
        # Short stabilization demo (10s) for smoke — not full 90s campaign window
        def _s():
            return _query_proxy_prb()

        report["quick_convergence"] = telemetry_convergence_check(
            _s, n_samples=2, interval_s=2.0, sigma_max_pct=10.0
        )[0].value

    submits: List[dict] = []
    if SMOKE_SUBMITS > 0 and report["backend_healthy"]:
        sync = SameStateSynchronizer()
        ns = sync.network_state_id("smoke", 0)
        for sl in sync.slice_order[: min(SMOKE_SUBMITS, 3)]:
            submits.append(_smoke_submit(sl))
        report["smoke_submits"] = submits
    else:
        report["smoke_submits"] = []
        report["smoke_note"] = "dry-run (NAD_SMOKE_SUBMITS=0); set NAD_SMOKE_SUBMITS=3 for one triplet"

    (out / "smoke_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    if args.self_test:
        from nad_boundary_runtime_controls import self_test

        r = self_test()
        print(json.dumps(r, indent=2))
        raise SystemExit(0 if all(r.values()) else 1)
    out = Path(args.out or os.environ.get("NAD_SMOKE_OUT", "."))
    print(json.dumps(run_smoke(out), indent=2))
