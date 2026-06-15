#!/usr/bin/env python3
"""CORE-CONTENTION-01 campaign (live + dry-run) using core_contention_runtime_controls."""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))

from core_contention_runtime_controls import (  # noqa: E402
    ACTIVE_DIGEST,
    CONCURRENT_STAGGER_S,
    CONCURRENT_TENANTS,
    ControlVerdict,
    ContentionEvidenceCollector,
    DEFAULT_LADDER_CORE,
    HARD_GATE_STOP_FRAC,
    MultiTenantCoordinator,
    PRB_ABORT_PCT,
    PRB_SIGMA_MAX_PCT,
    PRB_SOFT_ABORT_PCT,
    TripletSyncState,
    UPFContentionSynchronizer,
    pre_triplet_core_validation,
    same_state_triplet_validation,
)
from nad_boundary_runtime_controls import (  # noqa: E402
    ControlVerdict as NadControlVerdict,
    LadderRollbackController,
    LadderStep,
    prb_abort_check,
    prb_stabilization_extended,
    score_mode_guard,
)
from nad_liminal_campaign import (  # noqa: E402
    IPERF_DURATION,
    LiminalRegime,
    SLICE_ORDER,
    _safe_float,
    _sla_metrics_from_result,
    _start_iperf,
    _stop_iperf,
    _submit_slice,
    extract_row,
    query_proxy_prb,
)

WARMUP_S = float(os.getenv("CORE_WARMUP_S", "120"))


def _pack_root(output_dir: Path) -> Path:
    p = Path(output_dir).resolve()
    if p.name == "raw" and p.parent.name == "dataset":
        return p.parent.parent
    if p.name == "dataset":
        return p.parent
    return p


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_core_ladder(spec: str) -> Tuple[LadderStep, ...]:
    """Parse '20,24,28,32' → ladder steps with M suffix."""
    out: List[LadderStep] = []
    for i, part in enumerate(spec.split(",")):
        part = part.strip().upper().replace("MBPS", "").replace("M", "")
        if not part:
            continue
        br = f"{part}M"
        role = "calibration_low" if i == 0 else ("primary_target" if i == len(spec.split(",")) - 2 else "mid")
        out.append(LadderStep(f"{part}Mbps", br, role))
    return tuple(out) if out else tuple(
        LadderStep(s["label"], s["bitrate"], s.get("role", "mid")) for s in DEFAULT_LADDER_CORE
    )


def _write_enriched_csv(pack: Path, rows: List[dict]) -> Path:
    path = pack / "dataset" / "enriched" / "core_contention_dataset.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    with path.open("w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return path


def run_core_contention_campaign(
    output_dir: Path,
    *,
    n_reps: int = 15,
    dry_run: bool = True,
    ladder: Optional[Sequence[LadderStep]] = None,
    warmup_s: float = WARMUP_S,
    soft_abort_pct: float = PRB_SOFT_ABORT_PCT,
    hard_abort_pct: float = PRB_ABORT_PCT,
    slice_order: Tuple[str, ...] = SLICE_ORDER,
) -> Dict[str, Any]:
    if dry_run:
        return _run_dry(output_dir, n_reps=n_reps, slice_order=slice_order)
    return _run_live(
        output_dir,
        n_reps=n_reps,
        ladder=ladder or tuple(
            LadderStep(s["label"], s["bitrate"], s.get("role", "mid")) for s in DEFAULT_LADDER_CORE
        ),
        warmup_s=warmup_s,
        soft_abort_pct=soft_abort_pct,
        hard_abort_pct=hard_abort_pct,
        slice_order=slice_order,
    )


def _run_dry(
    output_dir: Path,
    *,
    n_reps: int,
    slice_order: Sequence[str],
) -> Dict[str, Any]:
    from core_contention_runtime_controls import TripletSyncState as TSS

    pack = _pack_root(output_dir)
    evidence = ContentionEvidenceCollector()
    monitor_stats: Dict[str, Any] = {}
    rows: List[dict] = []
    stats = {
        "campaign_id": "CORE-CONTENTION-01",
        "run_tag": _utc_stamp(),
        "digest": ACTIVE_DIGEST,
        "dry_run": True,
        "n_reps": n_reps,
        "n_rows": 0,
    }
    sync = UPFContentionSynchronizer(slice_order=slice_order)
    for step in DEFAULT_LADDER_CORE:
        for rep in range(n_reps):
            state = TSS(f"{step['label']}-rep{rep:03d}", step["label"], rep)
            state = sync.run_triplet(state, lambda sl, nid: {}, dry_run=True)
            rows.extend(state.rows)
    stats["n_rows"] = len(rows)
    (pack / "campaign_execution_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return {"stats": stats, "rows": rows}


def _run_live(
    output_dir: Path,
    *,
    n_reps: int,
    ladder: Sequence[LadderStep],
    warmup_s: float,
    soft_abort_pct: float,
    hard_abort_pct: float,
    slice_order: Tuple[str, ...],
) -> Dict[str, Any]:
    pack = _pack_root(output_dir)
    raw_root = pack / "dataset" / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    run_tag = _utc_stamp()
    sync = UPFContentionSynchronizer(slice_order=slice_order)
    coord = MultiTenantCoordinator()
    ladder_ctl = LadderRollbackController(ladder)
    evidence = ContentionEvidenceCollector()
    all_rows: List[dict] = []
    stats: Dict[str, Any] = {
        "campaign_id": "CORE-CONTENTION-01",
        "run_tag": run_tag,
        "digest": ACTIVE_DIGEST,
        "dry_run": False,
        "ladder": [{"label": s.label, "bitrate": s.bitrate, "role": s.role} for s in ladder],
        "warmup_s": warmup_s,
        "soft_abort_pct": soft_abort_pct,
        "hard_abort_pct": hard_abort_pct,
        "concurrent_tenants": CONCURRENT_TENANTS,
        "stop_hard_gate_frac": HARD_GATE_STOP_FRAC,
        "triplets_attempted": 0,
        "triplets_kept": 0,
        "triplets_discarded": 0,
        "reps_skipped": 0,
        "pressure_skips": 0,
        "feasibility_skips": 0,
        "prb_skips": 0,
        "soft_aborts": 0,
        "hard_aborts": 0,
        "hard_gate_submits": 0,
        "concurrent_background_submits": 0,
        "abort_regime": [],
    }

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
            sigma_max_pct=PRB_SIGMA_MAX_PCT,
        )
        (reg_dir / "prb_stabilization.json").write_text(
            json.dumps({**stab.__dict__, "ladder_index": ladder_ctl.index}, default=str, indent=2),
            encoding="utf-8",
        )
        if stab.verdict == NadControlVerdict.ABORT:
            stats["abort_regime"].append({"regime": reg.label, "reason": stab.reason})
            _stop_iperf(proc)
            continue

        regime_hard = [0]
        regime_attempts = 0
        for rep in range(n_reps):
            coord.acquire_slot(1)
            bg_tenant = coord.tenant_id(run_tag, reg.label, rep, 1)
            bg_res = _submit_slice(bg_tenant, f"core_bg_{reg.label}_{rep}", "eMBB")
            stats["concurrent_background_submits"] += 1
            bg_m = _sla_metrics_from_result(bg_res)
            time.sleep(CONCURRENT_STAGGER_S)

            conv, pg, fg, pc, pre_vals = pre_triplet_core_validation(
                query_proxy_prb,
                resource_pressure=bg_m["pressure"],
                feasibility=bg_m["feasibility"],
            )
            evidence.record(
                "pre_triplet",
                {
                    "regime": reg.label,
                    "rep": rep,
                    "verdict": conv.value,
                    "pressure": pg.monitored.get("resource_pressure"),
                    "feasibility": fg.monitored.get("feasibility"),
                    "prb_pct": pc.monitored.get("prb_pct"),
                },
            )
            if conv == ControlVerdict.ABORT:
                stats["hard_aborts"] += 1
                chk = prb_abort_check(
                    max(pre_vals) if pre_vals else bg_m["prb"],
                    soft_pct=soft_abort_pct,
                    hard_pct=hard_abort_pct,
                )
                ladder_ctl.record_abort(chk)
                stats["reps_skipped"] += 1
                continue
            if conv == ControlVerdict.SKIP_REP:
                stats["reps_skipped"] += 1
                if pg.verdict != ControlVerdict.PASS:
                    stats["pressure_skips"] += 1
                if fg.verdict != ControlVerdict.PASS:
                    stats["feasibility_skips"] += 1
                if pc.verdict != ControlVerdict.PASS:
                    stats["prb_skips"] += 1
                continue

            ns_id = sync.network_state_id(reg.label, rep)
            state = TripletSyncState(network_state_id=ns_id, regime_label=reg.label, rep_index=rep)
            stats["triplets_attempted"] += 1
            regime_attempts += 1
            coord.acquire_slot(0)

            def submit_fn(sl: str, _ns: str) -> dict:
                tenant = coord.tenant_id(run_tag, reg.label, rep, 0) + f"-{sl}"
                proxy = query_proxy_prb()
                res = _submit_slice(tenant, f"core_{reg.label}_{rep}_{sl}", sl)
                payload = res["payload"]
                meta = payload.get("metadata") or {}
                snap = meta.get("telemetry_snapshot") or {}
                ran = snap.get("ran") or {}
                core = snap.get("core") or {}
                transport = snap.get("transport") or {}
                sla = meta.get("sla_metrics") or {}
                prb = float(ran.get("prb_utilization") or meta.get("ran_prb_utilization_input") or 0)
                guard = score_mode_guard(meta, prb)
                if guard.is_hard_gate:
                    regime_hard[0] += 1
                    stats["hard_gate_submits"] += 1
                row = extract_row(
                    run_tag,
                    reg,
                    rep,
                    sl,
                    _ns,
                    proxy,
                    res,
                    control_meta={
                        "core_contention": True,
                        "ladder_role": step.role,
                        "pressure_guard": pg.verdict.value,
                        "feasibility_guard": fg.verdict.value,
                    },
                    campaign_id="CORE-CONTENTION-01",
                )
                row["telemetry_core_memory"] = _safe_float(
                    core.get("memory_utilization", core.get("memory"))
                )
                row["background_pressure"] = bg_m["pressure"]
                row["concurrent_slot"] = 0
                row["pre_probe_pressure"] = bg_m["pressure"]
                row["pre_probe_feasibility"] = bg_m["feasibility"]
                return row

            state = sync.run_triplet(state, submit_fn, dry_run=False)
            ok, reason = same_state_triplet_validation(state)
            for row in state.rows:
                row["triplet_coherent"] = ok
                row["triplet_discard_reason"] = "" if ok else reason
                row["ladder_role"] = step.role
                all_rows.append(row)
                stem = f"{reg.label}_rep{rep:03d}_{row['slice']}"
                (reg_dir / f"{stem}.json").write_text(
                    json.dumps({"row": row, "coherent": ok}, indent=2),
                    encoding="utf-8",
                )
            if ok:
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

    (raw_root / "all_rows.json").write_text(json.dumps(all_rows, indent=2), encoding="utf-8")
    stats["n_rows"] = len(all_rows)
    stats["n_submits_expected"] = len(ladder) * n_reps * len(slice_order)
    stats["coordinator"] = coord.to_dict()
    stats["ladder_final"] = ladder_ctl.to_dict()
    (pack / "campaign_execution_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    evidence.write_json(str(pack / "contention_evidence.json"))
    csv_path = _write_enriched_csv(pack, all_rows)
    stats["enriched_csv"] = str(csv_path)
    return {"rows": all_rows, "stats": stats, "run_tag": run_tag}


def _cli() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="CORE contention campaign")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--campaign", type=str, default="CORE-CONTENTION-01")
    ap.add_argument("--ladder", type=str, default="20,24,28,32")
    ap.add_argument("--reps", type=int, default=15)
    ap.add_argument("--warmup", type=float, default=WARMUP_S)
    ap.add_argument("--stagger", type=float, default=CONCURRENT_STAGGER_S)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.campaign != "CORE-CONTENTION-01":
        print(f"Unknown campaign: {args.campaign}", file=sys.stderr)
        return 1
    os.environ["CORE_CONCURRENT_STAGGER_S"] = str(args.stagger)
    os.environ["CORE_WARMUP_S"] = str(args.warmup)
    ladder = parse_core_ladder(args.ladder)
    result = run_core_contention_campaign(
        Path(args.output_dir),
        n_reps=args.reps,
        dry_run=args.dry_run and not args.live,
        ladder=ladder,
        warmup_s=args.warmup,
    )
    print(json.dumps(result["stats"], indent=2))
    return 0 if result["stats"].get("n_rows", 0) > 0 or args.dry_run else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
