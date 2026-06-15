#!/usr/bin/env python3
"""NCM-ORCH-01 campaign orchestrator (dry-run + live)."""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT))

from core_contention_runtime_controls import (  # noqa: E402
    ControlVerdict,
    SLICE_ORDER,
    pre_triplet_core_validation,
)
from nad_liminal_campaign import (  # noqa: E402
    _sla_metrics_from_result,
    query_proxy_prb,
)
from ncm_operational_contention_controls import (  # noqa: E402
    ACTIVE_DIGEST,
    EquivalentStateCoordinator,
    EvidenceCollector,
    NCMTenantCoordinator,
    NCMControlVerdict,
    NCMGuardSet,
    TelemetrySnapshotValidator,
    TripletSubmitter,
    UPFMultiFlowCompanion,
    extract_row_from_result,
    validate_equivalent_state_triplet,
)

NCM_WARMUP_S = float(os.getenv("NCM_WARMUP_S", "60"))


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _pack_root(output_dir: Path) -> Path:
    p = Path(output_dir).resolve()
    if p.name == "raw" and p.parent.name == "dataset":
        return p.parent.parent
    if p.name == "dataset":
        return p.parent
    return p


def planned_submits(*, epochs: int, reps: int, triplet: bool = True, background_probe: bool = True) -> int:
    per_rep = (3 if triplet else 1) + (1 if background_probe else 0)
    return epochs * reps * per_rep


def run_ncm_orch_campaign(
    output_dir: Path,
    *,
    epochs: int = 3,
    reps: int = 12,
    tenants: int = 4,
    stagger_s: float = 2.0,
    dry_run: bool = True,
    upf_companion: bool = False,
    warmup_s: float = NCM_WARMUP_S,
) -> Dict[str, Any]:
    if dry_run:
        return _run_dry(output_dir, epochs=epochs, reps=reps, tenants=tenants, stagger_s=stagger_s)
    return _run_live(
        output_dir,
        epochs=epochs,
        reps=reps,
        tenants=tenants,
        stagger_s=stagger_s,
        upf_companion=upf_companion,
        warmup_s=warmup_s,
    )


def _run_dry(
    output_dir: Path,
    *,
    epochs: int,
    reps: int,
    tenants: int,
    stagger_s: float,
) -> Dict[str, Any]:
    pack = _pack_root(output_dir)
    run_tag = _utc_stamp()
    es_coord = EquivalentStateCoordinator(run_tag)
    guards = NCMGuardSet()
    snap_val = TelemetrySnapshotValidator()
    evidence = EvidenceCollector(pack)
    n_plan = planned_submits(epochs=epochs, reps=reps)

    for epoch in range(epochs):
        epoch_fail = 0
        epoch_attempt = 0
        for rep in range(reps):
            slot = rep % tenants
            evidence.add_row(
                {
                    "run_tag": run_tag,
                    "campaign_id": "NCM-ORCH-01",
                    "epoch": epoch,
                    "rep_index": rep,
                    "equivalent_state_id": es_coord.equivalent_state_id(epoch, rep),
                    "slice": "eMBB",
                    "contention_source": "orch_probe",
                    "concurrent_slot": slot,
                    "decision_mode": "decision_score",
                    "resource_pressure": 0.31,
                    "feasibility_score": 0.54,
                    "dry_run": True,
                }
            )
            guards.record_submit(http_ok=True)
            epoch_attempt += 1

            state = es_coord.run_triplet(
                epoch,
                rep,
                lambda sl, es_id, idx: {"slice": sl, "dry_run": True},
                dry_run=True,
            )
            coherent, reason = validate_equivalent_state_triplet(state)
            for i, row in enumerate(state.rows):
                full = {
                    "run_tag": run_tag,
                    "campaign_id": "NCM-ORCH-01",
                    "epoch": epoch,
                    "rep_index": rep,
                    "equivalent_state_id": state.equivalent_state_id,
                    "slice": row["slice"],
                    "contention_source": "orch",
                    "concurrent_slot": i % tenants,
                    "decision_mode": "decision_score",
                    "resource_pressure": 0.32,
                    "feasibility_score": 0.52,
                    "triplet_coherent": coherent,
                    "triplet_discard_reason": "" if coherent else reason,
                    "dry_run": True,
                }
                snap_val.validate_row(full)
                evidence.add_row(full)
                guards.record_submit(http_ok=True)
                epoch_attempt += 1

        if guards.check_epoch_http_failures(epoch_fail, epoch_attempt).verdict == NCMControlVerdict.ABORT:
            break

    stats = {
        "campaign_id": "NCM-ORCH-01",
        "run_tag": run_tag,
        "digest": ACTIVE_DIGEST,
        "dry_run": True,
        "planned_submits": n_plan,
        "rows_written": len(evidence.rows),
        "n_plan_matches": len(evidence.rows) == n_plan,
        "triplets_completed": epochs * reps,
    }
    paths = evidence.write_all(run_tag, stats)
    stats["output_paths"] = paths
    return {"stats": stats, "rows": evidence.rows, "run_tag": run_tag}


def _run_live(
    output_dir: Path,
    *,
    epochs: int,
    reps: int,
    tenants: int,
    stagger_s: float,
    upf_companion: bool,
    warmup_s: float,
) -> Dict[str, Any]:
    pack = _pack_root(output_dir)
    (pack / "dataset" / "raw").mkdir(parents=True, exist_ok=True)
    run_tag = _utc_stamp()
    coord = NCMTenantCoordinator(n_tenants=tenants, max_in_flight=4, stagger_s=stagger_s)
    es_coord = EquivalentStateCoordinator(run_tag)
    submitter = TripletSubmitter()
    guards = NCMGuardSet()
    snap_val = TelemetrySnapshotValidator()
    companion = UPFMultiFlowCompanion(enabled=upf_companion)
    evidence = EvidenceCollector(pack)

    stats: Dict[str, Any] = {
        "campaign_id": "NCM-ORCH-01",
        "run_tag": run_tag,
        "digest": ACTIVE_DIGEST,
        "dry_run": False,
        "epochs": epochs,
        "reps": reps,
        "tenants": tenants,
        "stagger_s": stagger_s,
        "warmup_s": warmup_s,
        "upf_companion": companion.to_dict(),
        "planned_submits": planned_submits(epochs=epochs, reps=reps),
        "orch_burst_submits": 0,
        "probe_submits": 0,
        "triplets_attempted": 0,
        "triplets_kept": 0,
        "triplets_skipped_guard": 0,
        "pressure_skips": 0,
        "feasibility_skips": 0,
        "prb_skips": 0,
        "hard_gate_submits": 0,
        "http_failures": 0,
        "regime_aborts": [],
    }

    cfg = companion.validate_config(ladder_mode=False)
    if cfg.verdict == NCMControlVerdict.ABORT:
        stats["abort_reason"] = cfg.reason
        evidence.write_all(run_tag, stats)
        return {"stats": stats, "rows": [], "run_tag": run_tag}

    if warmup_s > 0:
        time.sleep(warmup_s)

    if upf_companion:
        companion.start()
        stats["upf_companion_start"] = companion.to_dict()

    def _do_submit(tenant: str, scenario: str, sl: str, slot: int) -> dict:
        try:
            return submitter.submit(tenant, sl, scenario, coordinator=coord, slot=slot)
        except Exception as exc:
            return {"http_elapsed_s": None, "payload": {}, "error": str(exc), "slice": sl, "slice_key": sl}

    for epoch in range(epochs):
        epoch_http_fail = 0
        epoch_http_attempt = 0
        for rep in range(reps):
            es_id = es_coord.equivalent_state_id(epoch, rep)
            scenario_probe = f"ncm_probe_{epoch}_{rep}"

            # Orchestration burst: concurrent eMBB probes (slots 0..tenants-1)
            burst_results: List[dict] = []
            with ThreadPoolExecutor(max_workers=min(tenants, 4)) as pool:
                futs = []
                for slot in range(min(tenants, 4)):
                    tenant = coord.tenant_id(run_tag, epoch, rep, slot, "eMBB")
                    futs.append(
                        pool.submit(
                            _do_submit,
                            tenant,
                            f"{scenario_probe}_burst_{slot}",
                            "eMBB",
                            slot,
                        )
                    )
                for fut in as_completed(futs):
                    burst_results.append(fut.result())
                    stats["orch_burst_submits"] += 1

            probe_tenant = coord.tenant_id(run_tag, epoch, rep, 0, "eMBB")
            probe_res = _do_submit(probe_tenant, scenario_probe, "eMBB", 0)
            stats["probe_submits"] += 1
            epoch_http_attempt += 1

            http_ok = not probe_res.get("error") and bool(probe_res.get("payload"))
            if not http_ok:
                epoch_http_fail += 1
                stats["http_failures"] += 1
                guards.record_submit(http_ok=False)
                evidence.orch.record("probe_http_fail", {"epoch": epoch, "rep": rep})
                continue

            bg_m = _sla_metrics_from_result(probe_res)
            conv, pg, fg, pc, pre_vals = pre_triplet_core_validation(
                query_proxy_prb,
                resource_pressure=bg_m["pressure"],
                feasibility=bg_m["feasibility"],
            )
            evidence.orch.record(
                "pre_triplet",
                {
                    "epoch": epoch,
                    "rep": rep,
                    "verdict": conv.value,
                    "pressure": bg_m["pressure"],
                    "feasibility": bg_m["feasibility"],
                    "prb_peak": max(pre_vals) if pre_vals else None,
                    "orch_in_flight": coord.concurrent_in_flight,
                },
            )

            probe_row = extract_row_from_result(
                run_tag,
                probe_res,
                epoch=epoch,
                rep=rep,
                slice_key="eMBB",
                equivalent_state_id=es_id,
                slot=0,
                contention_source="orch_probe",
            )
            probe_row["orch_burst_n"] = len(burst_results)
            evidence.add_row(probe_row)
            guards.record_submit(http_ok=True, is_hard_gate=probe_row.get("is_hard_gate", False))
            if probe_row.get("is_hard_gate"):
                stats["hard_gate_submits"] += 1

            if conv == ControlVerdict.ABORT:
                stats["prb_skips"] += 1
                stats["regime_aborts"].append({"epoch": epoch, "rep": rep, "reason": "prb_abort"})
                continue
            if conv == ControlVerdict.SKIP_REP:
                stats["triplets_skipped_guard"] += 1
                if pg.verdict != ControlVerdict.PASS:
                    stats["pressure_skips"] += 1
                if fg.verdict != ControlVerdict.PASS:
                    stats["feasibility_skips"] += 1
                if pc.verdict != ControlVerdict.PASS:
                    stats["prb_skips"] += 1
                continue

            stats["triplets_attempted"] += 1

            def submit_fn(sl: str, _es: str, idx: int) -> dict:
                tenant = coord.tenant_id(run_tag, epoch, rep, idx % tenants, sl)
                return _do_submit(tenant, f"ncm_{epoch}_{rep}_{sl}", sl, idx % tenants)

            state = es_coord.run_triplet(epoch, rep, submit_fn, dry_run=False)
            triplet_rows: List[dict] = []
            for i, res in enumerate(state.rows):
                sl = res.get("slice", SLICE_ORDER[i] if i < 3 else "?")
                if res.get("error") or not res.get("payload"):
                    epoch_http_fail += 1
                    stats["http_failures"] += 1
                    guards.record_submit(http_ok=False)
                    continue
                full = extract_row_from_result(
                    run_tag,
                    res,
                    epoch=epoch,
                    rep=rep,
                    slice_key=sl,
                    equivalent_state_id=es_id,
                    slot=i % tenants,
                    contention_source="orch",
                )
                full["orch_concurrent_in_flight"] = coord.concurrent_in_flight
                snap_val.validate_row(full)
                triplet_rows.append(full)
                epoch_http_attempt += 1
                guards.record_submit(http_ok=True, is_hard_gate=full.get("is_hard_gate", False))
                if full.get("is_hard_gate"):
                    stats["hard_gate_submits"] += 1
            state.rows = triplet_rows
            coherent, reason = validate_equivalent_state_triplet(state)
            for full in triplet_rows:
                full["triplet_coherent"] = coherent
                full["triplet_discard_reason"] = "" if coherent else reason
                evidence.add_row(full)

            if coherent:
                stats["triplets_kept"] += 1
            else:
                stats["triplets_skipped_guard"] += 1

            hg = guards.check_hard_gate_stop()
            if hg.verdict == NCMControlVerdict.ABORT:
                stats["stop_hard_gate"] = True
                break

        ef = guards.check_epoch_http_failures(epoch_http_fail, epoch_http_attempt)
        if ef.verdict == NCMControlVerdict.ABORT:
            stats["epoch_http_abort"] = epoch
            break

    companion.stop()
    stats["rows_written"] = len(evidence.rows)
    stats["n_score_mode"] = sum(
        1 for r in evidence.rows if str(r.get("decision_mode")) == "decision_score"
    )
    stats["guards"] = guards.to_dict()
    stats["coordinator"] = coord.to_dict()
    paths = evidence.write_all(run_tag, stats)
    stats["output_paths"] = paths
    return {"stats": stats, "rows": evidence.rows, "run_tag": run_tag}


def _cli() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="NCM-ORCH-01 campaign")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--campaign", default="NCM-ORCH-01")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--reps", type=int, default=12)
    ap.add_argument("--tenants", type=int, default=4)
    ap.add_argument("--stagger", type=float, default=2.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--upf-companion", action="store_true")
    args = ap.parse_args()
    if args.campaign != "NCM-ORCH-01":
        print(f"Unknown campaign: {args.campaign}", file=sys.stderr)
        return 1
    dry = args.dry_run and not args.live
    result = run_ncm_orch_campaign(
        Path(args.output_dir),
        epochs=args.epochs,
        reps=args.reps,
        tenants=args.tenants,
        stagger_s=args.stagger,
        dry_run=dry,
        upf_companion=args.upf_companion and not dry,
    )
    print(json.dumps(result["stats"], indent=2))
    if dry:
        ok = result["stats"].get("n_plan_matches") and result["stats"].get("planned_submits") == 144
    else:
        ok = result["stats"].get("rows_written", 0) > 0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
