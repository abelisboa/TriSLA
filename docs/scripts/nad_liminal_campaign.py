#!/usr/bin/env python3
"""NAD-LIMINAL-01 campaign execution (uses nad_boundary_runtime_controls only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))
from nad_boundary_runtime_controls import (  # noqa: E402
    ACTIVE_DIGEST,
    CONCURRENT_TENANTS,
    ControlVerdict,
    DEFAULT_LADDER_LIMINAL02,
    DEFAULT_LADDER_LIMINAL03,
    LIM03_STOP_HARD_GATE_FRAC,
    LadderRollbackController,
    LadderStep,
    PRB_ABORT_PCT,
    PRB_SIGMA_MAX_PCT,
    PRB_SOFT_ABORT_PCT,
    SLICE_ORDER,
    CONCURRENT_STAGGER_S,
    ConcurrentTenantCoordinator,
    PrbAbortDecision,
    TripletBarrierSynchronizer,
    TripletSyncState,
    WARMUP_LIMINAL02_S,
    WARMUP_LIMINAL03_S,
    WARMUP_S,
    hard_gate_pre_detect,
    liminal03_corridor_enforce,
    liminal_corridor_validate,
    parse_ladder,
    pre_triplet_liminal03_validation,
    pre_triplet_prb_validation,
    prb_abort_check,
    prb_stabilization_extended,
    prb_stabilization_gate,
    score_mode_guard,
    telemetry_convergence_check,
)

BACKEND_URL = os.getenv("TRISLA_BACKEND_URL", "http://192.168.10.15:32002").rstrip("/")
PRB_PROXY_PROMQL = os.getenv(
    "TRISLA_PRB_PROXY_PROMQL",
    'avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})',
)
IPERF_TARGET = os.getenv("TRISLA_IPERF_TARGET", "192.168.100.51")
IPERF_DURATION = int(os.getenv("NAD_IPERF_DURATION_S", "450"))
HARD_GATE_STOP_FRAC = float(os.getenv("NAD_HARD_GATE_STOP_FRAC", "0.30"))

SLICES: Dict[str, Tuple[str, dict]] = {
    "URLLC": (
        "urllc-template-001",
        {"type": "URLLC", "service_name": "URLLC", "latency": "1ms", "reliability": 0.99999, "throughput": "100Mbps"},
    ),
    "eMBB": (
        "embb-template-001",
        {"type": "eMBB", "service_name": "eMBB", "latency": "20ms", "reliability": 0.99, "throughput": "500Mbps"},
    ),
    "mMTC": (
        "mmtc-template-001",
        {"type": "mMTC", "service_name": "mMTC", "latency": "100ms", "reliability": 0.95, "throughput": "1Mbps"},
    ),
}


@dataclass(frozen=True)
class LiminalRegime:
    label: str
    bitrate: str = "15M"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _http_json(method: str, url: str, body: Optional[dict] = None, timeout: float = 180.0) -> Any:
    data = None
    headers: dict[str, str] = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def query_proxy_prb() -> Optional[float]:
    url = f"{BACKEND_URL}/api/v1/prometheus/query?" + urlencode({"query": PRB_PROXY_PROMQL})
    try:
        data = _http_json("GET", url, timeout=30.0)
    except Exception:
        return None
    for item in (((data or {}).get("data") or {}).get("result") or []):
        metric = item.get("metric") or {}
        if str(metric.get("job") or "") == "trisla-ran-ue-upf-proxy":
            return _safe_float((item.get("value") or [None, None])[1])
    return None


def _term(meta: dict, factor: str, key: str) -> Optional[float]:
    for t in meta.get("contributing_factors") or []:
        if isinstance(t, dict) and t.get("factor") == factor:
            return _safe_float(t.get(key))
    return None


def extract_row(
    run_tag: str,
    regime: LiminalRegime,
    rep_idx: int,
    slice_key: str,
    network_state_id: str,
    proxy_prb: Optional[float],
    result: dict[str, Any],
    *,
    control_meta: Optional[dict] = None,
    campaign_id: str = "NAD-LIMINAL-01",
) -> dict[str, Any]:
    payload = result["payload"]
    meta = payload.get("metadata") or {}
    snap = meta.get("telemetry_snapshot") or {}
    ran = snap.get("ran") or {}
    transport = snap.get("transport") or {}
    core = snap.get("core") or {}
    sla = meta.get("sla_metrics") or {}
    ni = meta.get("normalized_inputs") or {}
    sp = ni.get("slice_profile") or {}
    weights = sp.get("weights") or {}
    decision = str(payload.get("decision") or "")
    dmap = {"ACCEPT": 1.0, "AC": 1.0, "RENEGOTIATE": 0.5, "RENEG": 0.5, "REJECT": 0.0, "REJ": 0.0}
    prb = _safe_float(ran.get("prb_utilization")) or _safe_float(meta.get("ran_prb_utilization_input"))
    den = sum(_safe_float(t.get("weight")) or 0.0 for t in (meta.get("contributing_factors") or []) if isinstance(t, dict))
    guard = score_mode_guard(meta, prb)
    row = {
        "run_tag": run_tag,
        "campaign_id": campaign_id,
        "regime_mbps": regime.label,
        "iperf_bitrate": regime.bitrate,
        "rep_index": rep_idx,
        "network_state_id": network_state_id,
        "slice": slice_key,
        "template_id": SLICES[slice_key][0],
        "timestamp": snap.get("timestamp") or payload.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "execution_id": meta.get("execution_id"),
        "tenant_id": payload.get("intent_id") or "",
        "decision": decision,
        "decision_num": dmap.get(decision.upper()),
        "decision_score": _safe_float(meta.get("decision_score")),
        "decision_band": meta.get("decision_band") or meta.get("final_decision"),
        "decision_mode": meta.get("decision_mode"),
        "decision_source": meta.get("decision_source"),
        "prb_utilization_real": prb,
        "telemetry_transport_rtt_ms": _safe_float(transport.get("rtt_ms", transport.get("rtt"))),
        "telemetry_core_cpu": _safe_float(core.get("cpu_utilization", core.get("cpu"))),
        "feasibility_score": _safe_float(sla.get("feasibility_score")) or _safe_float((ni.get("feasibility") or {}).get("value")),
        "resource_pressure": _safe_float(sla.get("resource_pressure")) or _safe_float((ni.get("resource_pressure") or {}).get("value")),
        "w_transport": _safe_float(weights.get("w_transport")) or _term(meta, "transport_rtt_goodness", "weight"),
        "score_denominator_weights": den,
        "proxy_prb_at_submit": proxy_prb,
        "http_elapsed_s": result["http_elapsed_s"],
        "control_guard": guard.reason,
        "triplet_coherent": control_meta.get("triplet_coherent") if control_meta else None,
    }
    if control_meta:
        row["liminal_checks"] = json.dumps(control_meta.get("liminal_checks") or {})
    return row


def _start_iperf(bitrate: str, duration_s: int) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [
            "kubectl", "-n", "ueransim", "exec", "deploy/ueransim-singlepod", "-c", "ue", "--",
            "iperf3", "-c", IPERF_TARGET, "-u", "-b", bitrate, "-t", str(duration_s),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _stop_iperf(proc: Optional[subprocess.Popen[bytes]]) -> None:
    if proc is None:
        return
    try:
        proc.wait(timeout=90)
    except subprocess.TimeoutExpired:
        proc.kill()


def _submit_slice(tenant_id: str, scenario: str, slice_key: str) -> dict[str, Any]:
    tid, fv = SLICES[slice_key]
    body = {"template_id": tid, "tenant_id": tenant_id, "form_values": dict(fv)}
    body["form_values"]["scenario"] = scenario
    t0 = time.time()
    payload = _http_json("POST", f"{BACKEND_URL}/api/v1/sla/submit", body, timeout=180.0)
    return {"http_elapsed_s": time.time() - t0, "payload": payload, "slice": slice_key}


def run_campaign(
    output_dir: Path,
    *,
    campaign_id: str = "NAD-LIMINAL-01",
    n_regimes: int = 5,
    n_reps: int = 20,
    require_scoremode_only: bool = True,
    abort_prb_pct: float = PRB_ABORT_PCT,
    prb_sigma_max: float = PRB_SIGMA_MAX_PCT,
    warmup_s: float = WARMUP_S,
    slice_order: Tuple[str, ...] = SLICE_ORDER,
) -> dict[str, Any]:
    raw_root = output_dir / "dataset" / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    run_tag = _utc_stamp()
    regimes = [LiminalRegime(f"liminal-{i:02d}") for i in range(n_regimes)]
    sync = SameStateSynchronizer(slice_order=slice_order)
    all_rows: List[dict] = []
    stats = {
        "campaign_id": campaign_id,
        "run_tag": run_tag,
        "digest": ACTIVE_DIGEST,
        "triplets_attempted": 0,
        "triplets_kept": 0,
        "triplets_discarded": 0,
        "reps_skipped": 0,
        "hard_gate_submits": 0,
        "abort_regime": [],
    }

    for reg in regimes:
        reg_dir = raw_root / reg.label
        reg_dir.mkdir(parents=True, exist_ok=True)
        proc = _start_iperf(reg.bitrate, IPERF_DURATION)
        stab = prb_stabilization_gate(query_proxy_prb, warmup_s=warmup_s, abort_pct=abort_prb_pct, sigma_max_pct=prb_sigma_max)
        (reg_dir / "prb_stabilization.json").write_text(json.dumps(stab.__dict__, default=str, indent=2), encoding="utf-8")
        if stab.verdict == ControlVerdict.ABORT:
            stats["abort_regime"].append({"regime": reg.label, "reason": stab.reason})
            _stop_iperf(proc)
            continue

        regime_hard = [0]
        regime_attempts = 0
        for rep in range(n_reps):
            conv, pre_prb = telemetry_convergence_check(query_proxy_prb)
            if conv == ControlVerdict.SKIP_REP or hard_gate_pre_detect(pre_prb[-1] if pre_prb else None):
                stats["reps_skipped"] += 1
                continue
            if pre_prb and max(pre_prb) >= abort_prb_pct:
                stats["reps_skipped"] += 1
                continue

            ns_id = sync.network_state_id(reg.label, rep)
            state = TripletSyncState(network_state_id=ns_id, regime_label=reg.label, rep_index=rep)
            stats["triplets_attempted"] += 1
            regime_attempts += 1

            def submit_fn(sl: str, _ns: str) -> dict:
                tenant = f"nad-{run_tag}-{reg.label}-{rep:03d}-{sl}"
                proxy = query_proxy_prb()
                res = _submit_slice(tenant, f"nad_{reg.label}_{rep}_{sl}", sl)
                payload = res["payload"]
                meta = payload.get("metadata") or {}
                snap = meta.get("telemetry_snapshot") or {}
                ran = snap.get("ran") or {}
                prb = _safe_float(ran.get("prb_utilization")) or _safe_float(meta.get("ran_prb_utilization_input"))
                guard = score_mode_guard(meta, prb)
                if guard.is_hard_gate:
                    regime_hard[0] += 1
                    stats["hard_gate_submits"] += 1
                lim = liminal_corridor_validate(
                    prb_pct=prb,
                    decision_score=_safe_float(meta.get("decision_score")),
                    rtt_ms=_safe_float((snap.get("transport") or {}).get("rtt_ms")),
                    feasibility=_safe_float((meta.get("sla_metrics") or {}).get("feasibility_score")),
                    resource_pressure=_safe_float((meta.get("sla_metrics") or {}).get("resource_pressure")),
                )
                return extract_row(run_tag, reg, rep, sl, _ns, proxy, res, control_meta={"liminal_checks": lim.checks})

            state = sync.run_triplet(state, submit_fn)
            coherent, reason = sync.triplet_coherent(state)
            for row in state.rows:
                row["triplet_coherent"] = coherent
                row["triplet_discard_reason"] = "" if coherent else reason
                all_rows.append(row)
                stem = f"{reg.label}_rep{rep:03d}_{row['slice']}"
                (reg_dir / f"{stem}.json").write_text(
                    json.dumps({"row": row, "coherent": coherent}, indent=2),
                    encoding="utf-8",
                )
            if coherent:
                stats["triplets_kept"] += 1
            else:
                stats["triplets_discarded"] += 1

            if regime_attempts >= 5 and regime_hard[0] / max(regime_attempts * 3, 1) > HARD_GATE_STOP_FRAC:
                (reg_dir / "STOP_HARD_GATE.txt").write_text(
                    f"hard_gate rate exceeded {HARD_GATE_STOP_FRAC}\n", encoding="utf-8"
                )
                break

        _stop_iperf(proc)

    raw_root.mkdir(parents=True, exist_ok=True)
    (output_dir / "dataset" / "raw" / "all_rows.json").write_text(
        json.dumps(all_rows, indent=2), encoding="utf-8"
    )
    stats["n_rows"] = len(all_rows)
    stats["n_submits_expected"] = n_regimes * n_reps * len(slice_order)
    (output_dir / "campaign_execution_stats.json").write_text(
        json.dumps(stats, indent=2), encoding="utf-8"
    )
    return {"rows": all_rows, "stats": stats, "run_tag": run_tag}


def _pack_root(output_dir: Path) -> Path:
    """Accept evidence pack root or legacy .../dataset/raw path."""
    p = output_dir.resolve()
    if p.name == "raw" and p.parent.name == "dataset":
        return p.parent.parent
    return p


def run_liminal02_campaign(
    output_dir: Path,
    *,
    ladder: Tuple[LadderStep, ...] = DEFAULT_LADDER_LIMINAL02,
    n_reps: int = 20,
    require_scoremode_only: bool = True,
    soft_abort_pct: float = PRB_SOFT_ABORT_PCT,
    hard_abort_pct: float = PRB_ABORT_PCT,
    prb_sigma_max: float = PRB_SIGMA_MAX_PCT,
    warmup_s: float = WARMUP_LIMINAL02_S,
    slice_order: Tuple[str, ...] = SLICE_ORDER,
    dry_run: bool = False,
) -> dict[str, Any]:
    """NAD-LIMINAL-02: higher-stress ladder with soft/hard abort and rollback."""
    pack = _pack_root(output_dir)
    raw_root = pack / "dataset" / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    run_tag = _utc_stamp()
    sync = SameStateSynchronizer(slice_order=slice_order)
    ladder_ctl = LadderRollbackController(ladder)
    all_rows: List[dict] = []
    stats: Dict[str, Any] = {
        "campaign_id": "NAD-LIMINAL-02",
        "run_tag": run_tag,
        "digest": ACTIVE_DIGEST,
        "dry_run": dry_run,
        "ladder": [{"label": s.label, "bitrate": s.bitrate, "role": s.role} for s in ladder],
        "soft_abort_pct": soft_abort_pct,
        "hard_abort_pct": hard_abort_pct,
        "warmup_s": warmup_s,
        "triplets_attempted": 0,
        "triplets_kept": 0,
        "triplets_discarded": 0,
        "reps_skipped": 0,
        "soft_aborts": 0,
        "hard_aborts": 0,
        "rollbacks": 0,
        "hard_gate_submits": 0,
        "abort_regime": [],
    }

    if dry_run:
        stats["dry_run_plan"] = {
            "regimes": len(ladder),
            "reps": n_reps,
            "expected_submits": len(ladder) * n_reps * len(slice_order),
        }
        (pack / "campaign_execution_stats.json").write_text(
            json.dumps(stats, indent=2), encoding="utf-8"
        )
        return {"rows": [], "stats": stats, "run_tag": run_tag}

    for step in ladder:
        reg = LiminalRegime(step.label, step.bitrate)
        reg_dir = raw_root / reg.label.replace("/", "_")
        reg_dir.mkdir(parents=True, exist_ok=True)
        proc = _start_iperf(reg.bitrate, IPERF_DURATION)
        cal_warmup = 90.0 if "calibration" in step.role else warmup_s
        stab = prb_stabilization_extended(
            query_proxy_prb,
            warmup_s=cal_warmup,
            soft_pct=soft_abort_pct,
            hard_pct=hard_abort_pct,
            sigma_max_pct=prb_sigma_max,
        )
        (reg_dir / "prb_stabilization.json").write_text(
            json.dumps({**stab.__dict__, "ladder_index": ladder_ctl.index}, default=str, indent=2),
            encoding="utf-8",
        )
        if stab.verdict == ControlVerdict.ABORT:
            stats["abort_regime"].append({"regime": reg.label, "reason": stab.reason})
            _stop_iperf(proc)
            continue

        regime_hard = [0]
        regime_attempts = 0
        for rep in range(n_reps):
            conv, chk, pre_vals = pre_triplet_prb_validation(
                query_proxy_prb,
                soft_pct=soft_abort_pct,
                hard_pct=hard_abort_pct,
                sigma_max_pct=prb_sigma_max,
            )
            if conv == ControlVerdict.ABORT:
                stats["hard_aborts"] += 1
                ev = ladder_ctl.record_abort(chk)
                if ev and ev.get("action") == "stop_regime":
                    break
                continue
            if conv == ControlVerdict.SKIP_REP:
                stats["soft_aborts"] += 1
                stats["reps_skipped"] += 1
                ev = ladder_ctl.record_abort(chk)
                if ev and ev.get("action") == "rollback":
                    stats["rollbacks"] += 1
                continue

            ns_id = sync.network_state_id(reg.label, rep)
            state = TripletSyncState(network_state_id=ns_id, regime_label=reg.label, rep_index=rep)
            stats["triplets_attempted"] += 1
            regime_attempts += 1

            def submit_fn(sl: str, _ns: str) -> dict:
                tenant = f"nad02-{run_tag}-{reg.label}-{rep:03d}-{sl}"
                proxy = query_proxy_prb()
                res = _submit_slice(tenant, f"nad02_{reg.label}_{rep}_{sl}", sl)
                payload = res["payload"]
                meta = payload.get("metadata") or {}
                snap = meta.get("telemetry_snapshot") or {}
                ran = snap.get("ran") or {}
                prb = _safe_float(ran.get("prb_utilization")) or _safe_float(meta.get("ran_prb_utilization_input"))
                guard = score_mode_guard(meta, prb)
                if guard.is_hard_gate:
                    regime_hard[0] += 1
                    stats["hard_gate_submits"] += 1
                lim = liminal_corridor_validate(
                    prb_pct=prb,
                    decision_score=_safe_float(meta.get("decision_score")),
                    rtt_ms=_safe_float((snap.get("transport") or {}).get("rtt_ms")),
                    feasibility=_safe_float((meta.get("sla_metrics") or {}).get("feasibility_score")),
                    resource_pressure=_safe_float((meta.get("sla_metrics") or {}).get("resource_pressure")),
                )
                return extract_row(
                    run_tag,
                    reg,
                    rep,
                    sl,
                    _ns,
                    proxy,
                    res,
                    control_meta={
                        "liminal_checks": lim.checks,
                        "ladder_role": step.role,
                    },
                    campaign_id="NAD-LIMINAL-02",
                )

            state = sync.run_triplet(state, submit_fn)
            coherent, reason = sync.triplet_coherent(state)
            for row in state.rows:
                row["triplet_coherent"] = coherent
                row["triplet_discard_reason"] = "" if coherent else reason
                row["ladder_role"] = step.role
                all_rows.append(row)
            if coherent:
                stats["triplets_kept"] += 1
            else:
                stats["triplets_discarded"] += 1

            if regime_attempts >= 5 and regime_hard[0] / max(regime_attempts * 3, 1) > HARD_GATE_STOP_FRAC:
                (reg_dir / "STOP_HARD_GATE.txt").write_text(
                    f"hard_gate rate exceeded {HARD_GATE_STOP_FRAC}\n", encoding="utf-8"
                )
                break

        _stop_iperf(proc)
        (reg_dir / "ladder_controller.json").write_text(
            json.dumps(ladder_ctl.to_dict(), indent=2), encoding="utf-8"
        )

    (pack / "dataset" / "raw" / "all_rows.json").write_text(
        json.dumps(all_rows, indent=2), encoding="utf-8"
    )
    stats["n_rows"] = len(all_rows)
    stats["n_submits_expected"] = len(ladder) * n_reps * len(slice_order)
    stats["ladder_final"] = ladder_ctl.to_dict()
    (pack / "campaign_execution_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return {"rows": all_rows, "stats": stats, "run_tag": run_tag}


def _sla_metrics_from_result(result: dict[str, Any]) -> dict[str, Optional[float]]:
    meta = (result.get("payload") or {}).get("metadata") or {}
    snap = meta.get("telemetry_snapshot") or {}
    ran = snap.get("ran") or {}
    transport = snap.get("transport") or {}
    sla = meta.get("sla_metrics") or {}
    ni = meta.get("normalized_inputs") or {}
    den = sum(
        _safe_float(t.get("weight")) or 0.0
        for t in (meta.get("contributing_factors") or [])
        if isinstance(t, dict)
    )
    return {
        "prb": _safe_float(ran.get("prb_utilization")) or _safe_float(meta.get("ran_prb_utilization_input")),
        "pressure": _safe_float(sla.get("resource_pressure"))
        or _safe_float((ni.get("resource_pressure") or {}).get("value")),
        "feasibility": _safe_float(sla.get("feasibility_score"))
        or _safe_float((ni.get("feasibility") or {}).get("value")),
        "rtt_ms": _safe_float(transport.get("rtt_ms", transport.get("rtt"))),
        "denominator": den if den > 0 else None,
    }


def run_liminal03_campaign(
    output_dir: Path,
    *,
    ladder: Tuple[LadderStep, ...] = DEFAULT_LADDER_LIMINAL03,
    n_reps: int = 15,
    require_scoremode_only: bool = True,
    soft_abort_pct: float = PRB_SOFT_ABORT_PCT,
    hard_abort_pct: float = PRB_ABORT_PCT,
    warmup_s: float = 120.0,
    prb_sigma_max: float = PRB_SIGMA_MAX_PCT,
    slice_order: Tuple[str, ...] = SLICE_ORDER,
    dry_run: bool = False,
) -> dict[str, Any]:
    """NAD-LIMINAL-03: pressure/feasibility corridor + concurrent tenants (EXEC-12 controls)."""
    pack = _pack_root(output_dir)
    raw_root = pack / "dataset" / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    run_tag = _utc_stamp()
    sync = TripletBarrierSynchronizer(slice_order=slice_order)
    coord = ConcurrentTenantCoordinator()
    ladder_ctl = LadderRollbackController(ladder)
    all_rows: List[dict] = []
    stats: Dict[str, Any] = {
        "campaign_id": "NAD-LIMINAL-03",
        "run_tag": run_tag,
        "digest": ACTIVE_DIGEST,
        "dry_run": dry_run,
        "ladder": [{"label": s.label, "bitrate": s.bitrate, "role": s.role} for s in ladder],
        "soft_abort_pct": soft_abort_pct,
        "hard_abort_pct": hard_abort_pct,
        "warmup_s": warmup_s,
        "concurrent_tenants": CONCURRENT_TENANTS,
        "stop_hard_gate_frac": LIM03_STOP_HARD_GATE_FRAC,
        "controls": [
            "pressure_guard",
            "feasibility_guard",
            "pre_triplet_liminal03_validation",
            "liminal03_corridor_enforce",
            "ConcurrentTenantCoordinator",
            "TripletBarrierSynchronizer",
        ],
        "triplets_attempted": 0,
        "triplets_kept": 0,
        "triplets_discarded": 0,
        "reps_skipped": 0,
        "pressure_skips": 0,
        "feasibility_skips": 0,
        "soft_aborts": 0,
        "hard_aborts": 0,
        "rollbacks": 0,
        "hard_gate_submits": 0,
        "concurrent_background_submits": 0,
        "abort_regime": [],
    }
    if dry_run:
        stats["dry_run_plan"] = {
            "regimes": len(ladder),
            "reps": n_reps,
            "expected_submits": len(ladder) * n_reps * len(slice_order),
            "concurrent_slots": CONCURRENT_TENANTS,
        }
        (pack / "campaign_execution_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
        return {"rows": [], "stats": stats, "run_tag": run_tag}

    for step in ladder:
        reg = LiminalRegime(step.label, step.bitrate)
        reg_dir = raw_root / reg.label.replace("/", "_")
        reg_dir.mkdir(parents=True, exist_ok=True)
        proc = _start_iperf(reg.bitrate, IPERF_DURATION)
        stab = prb_stabilization_extended(
            query_proxy_prb,
            warmup_s=warmup_s,
            soft_pct=soft_abort_pct,
            hard_pct=hard_abort_pct,
            sigma_max_pct=prb_sigma_max,
        )
        (reg_dir / "prb_stabilization.json").write_text(
            json.dumps({**stab.__dict__, "ladder_index": ladder_ctl.index}, default=str, indent=2),
            encoding="utf-8",
        )
        if stab.verdict == ControlVerdict.ABORT:
            stats["abort_regime"].append({"regime": reg.label, "reason": stab.reason})
            _stop_iperf(proc)
            continue

        regime_hard = [0]
        regime_attempts = 0
        for rep in range(n_reps):
            coord.acquire_slot(1)
            bg_tenant = coord.tenant_id(run_tag, reg.label, rep, 1)
            bg_res = _submit_slice(bg_tenant, f"nad03_bg_{reg.label}_{rep}", "eMBB")
            stats["concurrent_background_submits"] += 1
            bg_m = _sla_metrics_from_result(bg_res)
            time.sleep(CONCURRENT_STAGGER_S)

            conv, pg, fg, pre_vals = pre_triplet_liminal03_validation(
                query_proxy_prb,
                resource_pressure=bg_m["pressure"],
                feasibility=bg_m["feasibility"],
                score_denominator=bg_m["denominator"],
            )
            if conv == ControlVerdict.ABORT:
                stats["hard_aborts"] += 1
                chk = prb_abort_check(max(pre_vals) if pre_vals else bg_m["prb"], soft_pct=soft_abort_pct, hard_pct=hard_abort_pct)
                ev = ladder_ctl.record_abort(chk)
                if ev and ev.get("action") == "stop_regime":
                    break
                stats["reps_skipped"] += 1
                continue
            if conv == ControlVerdict.SKIP_REP:
                stats["reps_skipped"] += 1
                if pg.verdict != ControlVerdict.PASS:
                    stats["pressure_skips"] += 1
                if fg.verdict != ControlVerdict.PASS:
                    stats["feasibility_skips"] += 1
                if pg.verdict == ControlVerdict.SKIP_REP and "soft" in (pg.reason or ""):
                    stats["soft_aborts"] += 1
                    ev = ladder_ctl.record_abort(
                        PrbAbortDecision(ControlVerdict.SKIP_REP, "soft", pg.prb_pct, pg.reason)
                    )
                    if ev and ev.get("action") == "rollback":
                        stats["rollbacks"] += 1
                continue

            ns_id = sync.network_state_id(reg.label, rep)
            state = TripletSyncState(network_state_id=ns_id, regime_label=reg.label, rep_index=rep)
            stats["triplets_attempted"] += 1
            regime_attempts += 1
            coord.acquire_slot(0)

            def submit_fn(sl: str, _ns: str) -> dict:
                tenant = coord.tenant_id(run_tag, reg.label, rep, 0) + f"-{sl}"
                proxy = query_proxy_prb()
                res = _submit_slice(tenant, f"nad03_{reg.label}_{rep}_{sl}", sl)
                payload = res["payload"]
                meta = payload.get("metadata") or {}
                snap = meta.get("telemetry_snapshot") or {}
                ran = snap.get("ran") or {}
                transport = snap.get("transport") or {}
                sla = meta.get("sla_metrics") or {}
                prb = _safe_float(ran.get("prb_utilization")) or _safe_float(meta.get("ran_prb_utilization_input"))
                press = _safe_float(sla.get("resource_pressure"))
                feas = _safe_float(sla.get("feasibility_score"))
                rtt = _safe_float(transport.get("rtt_ms", transport.get("rtt")))
                guard = score_mode_guard(meta, prb)
                if guard.is_hard_gate:
                    regime_hard[0] += 1
                    stats["hard_gate_submits"] += 1
                lim = liminal03_corridor_enforce(
                    prb_pct=prb,
                    resource_pressure=press,
                    feasibility=feas,
                    rtt_ms=rtt,
                    decision_score=_safe_float(meta.get("decision_score")),
                    decision_mode=meta.get("decision_mode"),
                )
                row = extract_row(
                    run_tag,
                    reg,
                    rep,
                    sl,
                    _ns,
                    proxy,
                    res,
                    control_meta={
                        "liminal_checks": {**lim.checks, **lim.monitored},
                        "ladder_role": step.role,
                        "pressure_guard": pg.verdict.value,
                        "feasibility_guard": fg.verdict.value,
                    },
                    campaign_id="NAD-LIMINAL-03",
                )
                row["concurrent_slot"] = 0
                row["background_pressure"] = bg_m["pressure"]
                return row

            state = sync.run_triplet_barrier(state, submit_fn)
            coherent, reason = sync.triplet_coherent(state)
            for row in state.rows:
                row["triplet_coherent"] = coherent
                row["triplet_discard_reason"] = "" if coherent else reason
                row["ladder_role"] = step.role
                all_rows.append(row)
            if coherent:
                stats["triplets_kept"] += 1
            else:
                stats["triplets_discarded"] += 1

            if regime_attempts >= 5 and regime_hard[0] / max(regime_attempts * 3, 1) > LIM03_STOP_HARD_GATE_FRAC:
                (reg_dir / "STOP_HARD_GATE.txt").write_text(
                    f"hard_gate rate exceeded {LIM03_STOP_HARD_GATE_FRAC}\n", encoding="utf-8"
                )
                break

        _stop_iperf(proc)
        (reg_dir / "ladder_controller.json").write_text(
            json.dumps(ladder_ctl.to_dict(), indent=2), encoding="utf-8"
        )

    (pack / "dataset" / "raw" / "all_rows.json").write_text(
        json.dumps(all_rows, indent=2), encoding="utf-8"
    )
    stats["n_rows"] = len(all_rows)
    stats["n_submits_expected"] = len(ladder) * n_reps * len(slice_order)
    stats["ladder_final"] = ladder_ctl.to_dict()
    stats["coordinator"] = coord.to_dict()
    (pack / "campaign_execution_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return {"rows": all_rows, "stats": stats, "run_tag": run_tag}


def _cli() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="NAD liminal campaign runner")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--campaign", type=str, default="NAD-LIMINAL-02")
    ap.add_argument("--ladder", type=str, default="22,26,28,30,28")
    ap.add_argument("--soft-abort", type=float, default=PRB_SOFT_ABORT_PCT)
    ap.add_argument("--hard-abort", type=float, default=PRB_ABORT_PCT)
    ap.add_argument("--warmup", type=float, default=WARMUP_LIMINAL02_S)
    ap.add_argument("--sigma-max", type=float, default=PRB_SIGMA_MAX_PCT)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--output-dir", type=str, default=None)
    ap.add_argument("--triplet-order", type=str, default="urllc,embb,mmtc")
    args = ap.parse_args()

    if args.self_test:
        from nad_boundary_runtime_controls import self_test

        r = self_test()
        print(json.dumps(r, indent=2))
        return 0 if all(r.values()) else 1

    out = Path(args.output_dir or os.environ.get("NAD_CAMPAIGN_OUT", "."))
    if args.campaign == "NAD-LIMINAL-03":
        ladder = parse_ladder(args.ladder) if args.ladder else tuple(DEFAULT_LADDER_LIMINAL03)
        result = run_liminal03_campaign(
            out,
            ladder=ladder,
            n_reps=args.reps,
            soft_abort_pct=args.soft_abort,
            hard_abort_pct=args.hard_abort,
            warmup_s=args.warmup,
            prb_sigma_max=args.sigma_max,
            dry_run=args.dry_run,
        )
    else:
        ladder = parse_ladder(args.ladder)
        result = run_liminal02_campaign(
            out,
            ladder=ladder,
            n_reps=args.reps,
            soft_abort_pct=args.soft_abort,
            hard_abort_pct=args.hard_abort,
            warmup_s=args.warmup,
            prb_sigma_max=args.sigma_max,
            dry_run=args.dry_run,
        )
    print(json.dumps(result["stats"], indent=2))
    return 0 if args.dry_run or result["stats"].get("n_rows", 0) > 0 else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
