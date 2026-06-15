#!/usr/bin/env python3
"""NCM-EXEC-03: Orchestration contention campaign controls (scripts only)."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from core_contention_runtime_controls import (  # noqa: E402
    ACTIVE_DIGEST,
    ControlVerdict,
    ContentionEvidenceCollector,
    HARD_GATE_STOP_FRAC,
    PRB_ABORT_PCT,
    PRB_CORRIDOR_HI,
    PRB_CORRIDOR_LO,
    PRB_SOFT_ABORT_PCT,
    SLICE_ORDER,
    contention_abort_guard,
    feasibility_guard,
    pressure_guard,
    prb_corridor_guard,
    same_state_triplet_validation,
)
from nad_boundary_runtime_controls import score_mode_guard  # noqa: E402

# NCM-EXEC-02 blueprint SSOT
NCM_PRESSURE_MIN = float(os.getenv("NCM_PRESSURE_MIN", "0.30"))
NCM_FEASIBILITY_MAX = float(os.getenv("NCM_FEASIBILITY_MAX", "0.55"))
NCM_TENANTS = int(os.getenv("NCM_TENANTS", "4"))
NCM_CONCURRENCY = int(os.getenv("NCM_CONCURRENCY_IN_FLIGHT", "4"))
NCM_STAGGER_S = float(os.getenv("NCM_STAGGER_S", "2.0"))
NCM_TRIPLET_PAUSE_S = float(os.getenv("NCM_TRIPLET_PAUSE_S", "1.5"))
NCM_HTTP_FAIL_STOP_FRAC = float(os.getenv("NCM_HTTP_FAIL_STOP_FRAC", "0.50"))
NCM_UPF_MF_BITRATE = os.getenv("NCM_UPF_MF_BITRATE", "24M")
NCM_UPF_MF_FLOWS = int(os.getenv("NCM_UPF_MF_FLOWS", "2"))
NCM_WARMUP_S = float(os.getenv("NCM_WARMUP_S", "60"))
IPERF_DURATION = int(os.getenv("NCM_IPERF_DURATION_S", "600"))


class NCMControlVerdict(str, Enum):
    PASS = "PASS"
    ABORT = "ABORT"
    SKIP = "SKIP"
    WARN = "WARN"


@dataclass
class GuardResult:
    verdict: NCMControlVerdict
    reason: str = ""
    monitored: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquivalentStateState:
    equivalent_state_id: str
    epoch: int
    rep_index: int
    rows: List[dict] = field(default_factory=list)


def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v) if v not in ("", None) else None
    except (TypeError, ValueError):
        return None


class NCMTenantCoordinator:
    """4 tenants, max 4 in-flight, stagger 2s between slot starts."""

    def __init__(
        self,
        *,
        n_tenants: int = NCM_TENANTS,
        max_in_flight: int = NCM_CONCURRENCY,
        stagger_s: float = NCM_STAGGER_S,
    ) -> None:
        self.n_tenants = n_tenants
        self.max_in_flight = max_in_flight
        self.stagger_s = stagger_s
        self._semaphore = threading.Semaphore(max_in_flight)
        self._last_slot_start: Dict[int, float] = {}
        self._in_flight = 0
        self._lock = threading.Lock()

    def tenant_id(self, run_tag: str, epoch: int, rep: int, slot: int, slice_key: str = "") -> str:
        base = f"ncm-{run_tag}-ep{epoch:02d}-r{rep:03d}-t{slot}"
        return f"{base}-{slice_key}" if slice_key else base

    def acquire_slot(self, slot: int) -> None:
        now = time.time()
        last = self._last_slot_start.get(slot, 0.0)
        wait = self.stagger_s - (now - last)
        if wait > 0:
            time.sleep(wait)
        self._last_slot_start[slot] = time.time()
        self._semaphore.acquire()
        with self._lock:
            self._in_flight += 1

    def release_slot(self) -> None:
        with self._lock:
            self._in_flight = max(0, self._in_flight - 1)
        self._semaphore.release()

    @property
    def concurrent_in_flight(self) -> int:
        with self._lock:
            return self._in_flight

    def to_dict(self) -> dict:
        return {
            "n_tenants": self.n_tenants,
            "max_in_flight": self.max_in_flight,
            "stagger_s": self.stagger_s,
            "in_flight": self.concurrent_in_flight,
        }


class EquivalentStateCoordinator:
    """Grouping by ncm-{run_tag}-ep{epoch}-rep{rep}; triplet URLLC→eMBB→mMTC."""

    def __init__(
        self,
        run_tag: str,
        *,
        slice_order: Sequence[str] = SLICE_ORDER,
        pause_s: float = NCM_TRIPLET_PAUSE_S,
    ) -> None:
        self.run_tag = run_tag
        self.slice_order = tuple(slice_order)
        self.pause_s = pause_s

    def equivalent_state_id(self, epoch: int, rep: int) -> str:
        return f"ncm-{self.run_tag}-ep{epoch:02d}-rep{rep:03d}"

    def run_triplet(
        self,
        epoch: int,
        rep: int,
        submit_fn: Callable[[str, str, int], dict],
        *,
        dry_run: bool = False,
    ) -> EquivalentStateState:
        es_id = self.equivalent_state_id(epoch, rep)
        state = EquivalentStateState(es_id, epoch, rep)
        for i, sl in enumerate(self.slice_order):
            if dry_run:
                row = {
                    "slice": sl,
                    "decision": "RENEGOTIATE",
                    "decision_mode": "decision_score",
                    "decision_score": 0.68,
                    "resource_pressure": 0.32,
                    "feasibility_score": 0.52,
                    "dry_run": True,
                }
            else:
                row = submit_fn(sl, es_id, i)
            row["equivalent_state_id"] = es_id
            row["epoch"] = epoch
            row["rep_index"] = rep
            row["slice"] = sl
            if not dry_run:
                time.sleep(self.pause_s)
            state.rows.append(row)
        return state


class TripletSubmitter:
    """POST /api/v1/sla/submit with URLLC/eMBB/mMTC templates."""

    def __init__(
        self,
        *,
        backend_url: Optional[str] = None,
        timeout_s: float = 180.0,
        campaign_id: str = "NCM-ORCH-01",
    ) -> None:
        from nad_liminal_campaign import BACKEND_URL, SLICES, _submit_slice  # noqa: WPS433

        self.backend_url = (backend_url or BACKEND_URL).rstrip("/")
        self.timeout_s = timeout_s
        self.campaign_id = campaign_id
        self._submit_slice = _submit_slice
        self.slices = SLICES

    def submit(
        self,
        tenant_id: str,
        slice_key: str,
        scenario: str,
        *,
        coordinator: Optional[NCMTenantCoordinator] = None,
        slot: int = 0,
    ) -> dict:
        if coordinator:
            coordinator.acquire_slot(slot)
        try:
            t0 = time.perf_counter()
            result = self._submit_slice(tenant_id, scenario, slice_key)
            elapsed = time.perf_counter() - t0
            result["http_elapsed_s"] = elapsed
            return result
        finally:
            if coordinator:
                coordinator.release_slot()


class TelemetrySnapshotValidator:
    """Require telemetry_snapshot and key SLA fields when present."""

    def validate(self, result: dict) -> GuardResult:
        payload = result.get("payload") or {}
        meta = payload.get("metadata") or {}
        snap = meta.get("telemetry_snapshot")
        if not isinstance(snap, dict):
            return GuardResult(NCMControlVerdict.SKIP, reason="missing telemetry_snapshot")
        ran = snap.get("ran") or {}
        transport = snap.get("transport") or {}
        core = snap.get("core") or {}
        sla = meta.get("sla_metrics") or {}
        checks = {
            "has_snapshot": True,
            "has_ran": bool(ran),
            "has_transport": bool(transport),
            "has_core": bool(core),
        }
        press = _safe_float(sla.get("resource_pressure"))
        feas = _safe_float(sla.get("feasibility_score"))
        if press is not None:
            checks["has_pressure"] = True
        if feas is not None:
            checks["has_feasibility"] = True
        if not all(checks.values()):
            return GuardResult(
                NCMControlVerdict.WARN,
                reason="partial snapshot fields",
                monitored=checks,
            )
        return GuardResult(NCMControlVerdict.PASS, reason="snapshot OK", monitored=checks)

    def validate_row(self, row: dict) -> GuardResult:
        if row.get("dry_run"):
            return GuardResult(NCMControlVerdict.PASS, reason="dry-run row")
        if not row.get("telemetry_snapshot_present"):
            return GuardResult(NCMControlVerdict.SKIP, reason="snapshot flag false")
        return GuardResult(NCMControlVerdict.PASS, reason="row snapshot OK")


class NCMGuardSet:
    """pressure, feasibility, PRB, hard_gate rate, HTTP failure per epoch."""

    def __init__(
        self,
        *,
        pressure_min: float = NCM_PRESSURE_MIN,
        feasibility_max: float = NCM_FEASIBILITY_MAX,
        hard_gate_stop: float = HARD_GATE_STOP_FRAC,
        http_fail_stop: float = NCM_HTTP_FAIL_STOP_FRAC,
    ) -> None:
        self.pressure_min = pressure_min
        self.feasibility_max = feasibility_max
        self.hard_gate_stop = hard_gate_stop
        self.http_fail_stop = http_fail_stop
        self.hard_gate_count = 0
        self.total_submits = 0
        self.http_fail_count = 0

    def check_pressure(self, pressure: Optional[float], prb: Optional[float] = None) -> GuardResult:
        g = pressure_guard(resource_pressure=pressure, prb_pct=prb, pressure_min=self.pressure_min)
        v = NCMControlVerdict.PASS if g.verdict == ControlVerdict.PASS else (
            NCMControlVerdict.ABORT if g.verdict == ControlVerdict.ABORT else NCMControlVerdict.SKIP
        )
        return GuardResult(v, reason=g.reason, monitored=dict(g.monitored))

    def check_feasibility(self, feasibility: Optional[float]) -> GuardResult:
        g = feasibility_guard(feasibility=feasibility, feasibility_max=self.feasibility_max)
        v = NCMControlVerdict.PASS if g.verdict == ControlVerdict.PASS else NCMControlVerdict.SKIP
        return GuardResult(v, reason=g.reason, monitored=dict(g.monitored))

    def check_prb(self, prb_pct: Optional[float]) -> GuardResult:
        g = prb_corridor_guard(prb_pct)
        if g.verdict == ControlVerdict.ABORT:
            return GuardResult(NCMControlVerdict.ABORT, reason=g.reason, monitored=dict(g.monitored))
        if g.verdict != ControlVerdict.PASS:
            return GuardResult(NCMControlVerdict.SKIP, reason=g.reason, monitored=dict(g.monitored))
        return GuardResult(NCMControlVerdict.PASS, reason=g.reason, monitored=dict(g.monitored))

    def record_submit(self, *, http_ok: bool = True, is_hard_gate: bool = False) -> None:
        self.total_submits += 1
        if not http_ok:
            self.http_fail_count += 1
        if is_hard_gate:
            self.hard_gate_count += 1

    def check_hard_gate_stop(self) -> GuardResult:
        g = contention_abort_guard(
            hard_gate_count=self.hard_gate_count,
            total_submits=self.total_submits,
            stop_frac=self.hard_gate_stop,
        )
        v = NCMControlVerdict.ABORT if g.verdict == ControlVerdict.ABORT else NCMControlVerdict.PASS
        return GuardResult(v, reason=g.reason, monitored=dict(g.monitored))

    def check_epoch_http_failures(self, epoch_failures: int, epoch_attempts: int) -> GuardResult:
        if epoch_attempts <= 0:
            return GuardResult(NCMControlVerdict.PASS, reason="no epoch attempts")
        rate = epoch_failures / epoch_attempts
        if rate > self.http_fail_stop:
            return GuardResult(
                NCMControlVerdict.ABORT,
                reason=f"HTTP fail rate {rate:.2%} > {self.http_fail_stop:.0%}",
                monitored={"http_fail_rate": rate},
            )
        return GuardResult(NCMControlVerdict.PASS, monitored={"http_fail_rate": rate})

    def to_dict(self) -> dict:
        return {
            "pressure_min": self.pressure_min,
            "feasibility_max": self.feasibility_max,
            "hard_gate_stop": self.hard_gate_stop,
            "http_fail_stop": self.http_fail_stop,
            "hard_gate_count": self.hard_gate_count,
            "total_submits": self.total_submits,
            "http_fail_count": self.http_fail_count,
        }


class UPFMultiFlowCompanion:
    """Optional 2-flow UDP @ 24M fixed; ladder forbidden."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        flows: int = NCM_UPF_MF_FLOWS,
        bitrate: str = NCM_UPF_MF_BITRATE,
        ladder_forbidden: bool = True,
    ) -> None:
        self.enabled = enabled
        self.flows = flows
        self.bitrate = bitrate
        self.ladder_forbidden = ladder_forbidden
        self._procs: List[subprocess.Popen[bytes]] = []

    def validate_config(self, *, ladder_mode: bool = False) -> GuardResult:
        if ladder_mode and self.ladder_forbidden:
            return GuardResult(NCMControlVerdict.ABORT, reason="ladder-only forbidden for NCM-UPF-MF-01")
        if self.enabled and self.flows < 1:
            return GuardResult(NCMControlVerdict.SKIP, reason="flows < 1")
        return GuardResult(NCMControlVerdict.PASS, reason="UPF-MF config OK")

    def start(self, duration_s: int = IPERF_DURATION) -> GuardResult:
        if not self.enabled:
            return GuardResult(NCMControlVerdict.PASS, reason="companion disabled")
        from nad_liminal_campaign import IPERF_TARGET, _start_iperf  # noqa: WPS433

        self.stop()
        for _ in range(self.flows):
            self._procs.append(_start_iperf(self.bitrate, duration_s))
        return GuardResult(NCMControlVerdict.PASS, reason=f"started {self.flows} flows @ {self.bitrate}")

    def stop(self) -> None:
        from nad_liminal_campaign import _stop_iperf  # noqa: WPS433

        for p in self._procs:
            _stop_iperf(p)
        self._procs = []

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "flows": self.flows,
            "bitrate": self.bitrate,
            "ladder_forbidden": self.ladder_forbidden,
            "active_procs": len(self._procs),
        }


class EvidenceCollector:
    """all_rows.json, orchestration_evidence.json, CSV, SHA256."""

    def __init__(self, pack_root: Path) -> None:
        self.pack_root = Path(pack_root)
        self.rows: List[dict] = []
        self.orch = ContentionEvidenceCollector()

    def add_row(self, row: dict) -> None:
        self.rows.append(row)

    def write_all(self, run_tag: str, stats: dict) -> Dict[str, str]:
        raw = self.pack_root / "dataset" / "raw"
        enr = self.pack_root / "dataset" / "enriched"
        raw.mkdir(parents=True, exist_ok=True)
        enr.mkdir(parents=True, exist_ok=True)
        (raw / "all_rows.json").write_text(json.dumps(self.rows, indent=2), encoding="utf-8")
        csv_path = enr / "ncm_orch_01_dataset.csv"
        if self.rows:
            with csv_path.open("w", newline="", encoding="utf-8") as fp:
                w = csv.DictWriter(fp, fieldnames=list(self.rows[0].keys()), extrasaction="ignore")
                w.writeheader()
                w.writerows(self.rows)
        else:
            csv_path.write_text("", encoding="utf-8")
        orch_path = self.pack_root / "orchestration_evidence.json"
        self.orch.write_json(str(orch_path))
        stats_path = self.pack_root / "campaign_execution_stats.json"
        stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        digest = hashlib.sha256(csv_path.read_bytes()).hexdigest() if csv_path.stat().st_size else hashlib.sha256(b"").hexdigest()
        sha_path = self.pack_root / "analysis" / "dataset_sha256.txt"
        sha_path.parent.mkdir(parents=True, exist_ok=True)
        sha_path.write_text(f"{digest}  {csv_path.name}\n", encoding="utf-8")
        return {
            "all_rows": str(raw / "all_rows.json"),
            "csv": str(csv_path),
            "orchestration_evidence": str(orch_path),
            "stats": str(stats_path),
            "sha256": digest,
        }


def validate_equivalent_state_triplet(state: EquivalentStateState) -> Tuple[bool, str]:
    """Reuse core same-state validation on row dicts."""
    from core_contention_runtime_controls import TripletSyncState

    ts = TripletSyncState(state.equivalent_state_id, f"ep{state.epoch}", state.rep_index)
    ts.rows = state.rows
    return same_state_triplet_validation(ts)


def extract_row_from_result(
    run_tag: str,
    result: dict,
    *,
    epoch: int,
    rep: int,
    slice_key: str,
    equivalent_state_id: str,
    slot: int,
    contention_source: str = "orch",
) -> dict:
    from nad_liminal_campaign import _safe_float as sf  # noqa: WPS433

    payload = result.get("payload") or {}
    meta = payload.get("metadata") or {}
    snap = meta.get("telemetry_snapshot") or {}
    ran = snap.get("ran") or {}
    transport = snap.get("transport") or {}
    core = snap.get("core") or {}
    sla = meta.get("sla_metrics") or {}
    prb = sf(ran.get("prb_utilization")) or sf(meta.get("ran_prb_utilization_input"))
    guard = score_mode_guard(meta, prb)
    return {
        "run_tag": run_tag,
        "campaign_id": "NCM-ORCH-01",
        "epoch": epoch,
        "rep_index": rep,
        "equivalent_state_id": equivalent_state_id,
        "slice": slice_key,
        "tenant_id": payload.get("intent_id") or "",
        "contention_source": contention_source,
        "concurrent_slot": slot,
        "decision": payload.get("decision"),
        "decision_mode": meta.get("decision_mode"),
        "decision_score": sf(meta.get("decision_score")),
        "resource_pressure": sf(sla.get("resource_pressure")),
        "feasibility_score": sf(sla.get("feasibility_score")),
        "prb_utilization_real": prb,
        "telemetry_core_cpu": sf(core.get("cpu_utilization", core.get("cpu"))),
        "telemetry_transport_rtt_ms": sf(transport.get("rtt_ms", transport.get("rtt"))),
        "http_elapsed_s": result.get("http_elapsed_s"),
        "telemetry_snapshot_present": bool(snap),
        "is_hard_gate": guard.is_hard_gate,
        "dry_run": result.get("dry_run", False),
    }


def inventory() -> Dict[str, Any]:
    return {
        "module": "docs/scripts/ncm_operational_contention_controls.py",
        "digest_required": ACTIVE_DIGEST,
        "components": [
            "NCMTenantCoordinator",
            "EquivalentStateCoordinator",
            "TripletSubmitter",
            "TelemetrySnapshotValidator",
            "NCMGuardSet",
            "UPFMultiFlowCompanion",
            "EvidenceCollector",
            "validate_equivalent_state_triplet",
        ],
        "policy": {
            "tenants": NCM_TENANTS,
            "concurrency_in_flight": NCM_CONCURRENCY,
            "stagger_s": NCM_STAGGER_S,
            "pressure_min": NCM_PRESSURE_MIN,
            "feasibility_max": NCM_FEASIBILITY_MAX,
            "prb_corridor": [PRB_CORRIDOR_LO, PRB_CORRIDOR_HI],
            "prb_abort_pct": PRB_ABORT_PCT,
            "hard_gate_stop_frac": HARD_GATE_STOP_FRAC,
            "http_fail_stop_frac": NCM_HTTP_FAIL_STOP_FRAC,
            "upf_mf_bitrate": NCM_UPF_MF_BITRATE,
            "upf_mf_flows": NCM_UPF_MF_FLOWS,
        },
        "forbidden": [
            "decision-engine edits",
            "portal formula/threshold changes",
            "synthetic telemetry",
            "ladder-only primary campaign",
            "PRB weakening",
        ],
    }


def self_test() -> Dict[str, bool]:
    r: Dict[str, bool] = {}
    coord = NCMTenantCoordinator(n_tenants=4, max_in_flight=4, stagger_s=0.0)
    tid = coord.tenant_id("rtag", 1, 5, 2, "eMBB")
    r["tenant_id_format"] = tid.startswith("ncm-rtag-ep01-r005-t2-eMBB")
    es = EquivalentStateCoordinator("20260518T000000Z")
    r["equivalent_state_id"] = es.equivalent_state_id(2, 7) == "ncm-20260518T000000Z-ep02-rep007"
    st = es.run_triplet(0, 0, lambda s, e, i: {"slice": s}, dry_run=True)
    r["triplet_rows"] = len(st.rows) == 3
    ok, _ = validate_equivalent_state_triplet(st)
    r["triplet_valid_dry"] = ok
    guards = NCMGuardSet()
    r["pressure_skip"] = guards.check_pressure(0.12).verdict == NCMControlVerdict.SKIP
    r["feas_skip"] = guards.check_feasibility(0.70).verdict == NCMControlVerdict.SKIP
    r["prb_abort"] = guards.check_prb(24.5).verdict == NCMControlVerdict.ABORT
    r["http_epoch_abort"] = guards.check_epoch_http_failures(6, 10).verdict == NCMControlVerdict.ABORT
    comp = UPFMultiFlowCompanion(enabled=True)
    r["upf_ladder_block"] = comp.validate_config(ladder_mode=True).verdict == NCMControlVerdict.ABORT
    r["upf_config_ok"] = comp.validate_config(ladder_mode=False).verdict == NCMControlVerdict.PASS
    val = TelemetrySnapshotValidator()
    r["snapshot_dry"] = val.validate_row({"dry_run": True}).verdict == NCMControlVerdict.PASS
    ev = EvidenceCollector(Path("/tmp/ncm_ev_test"))
    ev.add_row({"a": 1})
    paths = ev.write_all("t", {"n_rows": 1})
    r["evidence_write"] = Path(paths["all_rows"]).exists()
    r["digest_frozen"] = ACTIVE_DIGEST.startswith("sha256:ca600174")
    return r


if __name__ == "__main__":
    import sys

    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--inventory", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        res = self_test()
        print(json.dumps(res, indent=2))
        sys.exit(0 if all(res.values()) else 1)
    if args.inventory:
        print(json.dumps(inventory(), indent=2))
        sys.exit(0)
    ap.print_help()
    sys.exit(0)
