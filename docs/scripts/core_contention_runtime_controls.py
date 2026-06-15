#!/usr/bin/env python3
"""
CORE-EXEC-06: UPF-first operational contention campaign controls (scripts only).

Does NOT modify decision-engine, portal-backend, formulas, gates, or Helm.
"""

from __future__ import annotations

import json
import os
import statistics
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# CORE-EXEC-05 design SSOT
PRB_CORRIDOR_LO = float(os.getenv("CORE_PRB_CORRIDOR_LO", "18.0"))
PRB_CORRIDOR_HI = float(os.getenv("CORE_PRB_CORRIDOR_HI", "24.0"))
PRB_ABORT_PCT = float(os.getenv("CORE_PRB_ABORT_PCT", "24.0"))
PRB_SOFT_ABORT_PCT = float(os.getenv("CORE_PRB_SOFT_ABORT_PCT", "23.5"))
HARD_GATE_STOP_FRAC = float(os.getenv("CORE_HARD_GATE_STOP_FRAC", "0.25"))
CORE_PRESSURE_MIN = float(os.getenv("CORE_PRESSURE_MIN", "0.30"))
CORE_FEASIBILITY_MAX = float(os.getenv("CORE_FEASIBILITY_MAX", "0.55"))
WARMUP_S = float(os.getenv("CORE_WARMUP_S", "120"))
CONCURRENT_TENANTS = int(os.getenv("CORE_CONCURRENT_TENANTS", "2"))
CONCURRENT_STAGGER_S = float(os.getenv("CORE_CONCURRENT_STAGGER_S", "3.0"))
PRB_SIGMA_MAX_PCT = float(os.getenv("CORE_PRB_SIGMA_MAX_PCT", "2.0"))
TRIPLET_PAUSE_S = float(os.getenv("CORE_TRIPLET_PAUSE_S", "1.5"))
PRE_PROBE_SAMPLES = int(os.getenv("CORE_PRE_PROBE_SAMPLES", "4"))
ACTIVE_DIGEST = os.getenv(
    "CORE_ACTIVE_DIGEST",
    "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6",
)

DEFAULT_LADDER_CORE = [
    {"label": "20Mbps", "bitrate": "20M", "role": "calibration_low"},
    {"label": "24Mbps", "bitrate": "24M", "role": "calibration_mid"},
    {"label": "28Mbps", "bitrate": "28M", "role": "primary_target"},
    {"label": "32Mbps", "bitrate": "32M", "role": "primary_upper"},
]

SLICE_ORDER: Tuple[str, ...] = ("URLLC", "eMBB", "mMTC")


class ControlVerdict(str, Enum):
    PASS = "PASS"
    ABORT = "ABORT"
    SKIP_REP = "SKIP_REP"
    WARN = "WARN"


def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


@dataclass
class GuardResult:
    verdict: ControlVerdict
    checks: Dict[str, bool] = field(default_factory=dict)
    monitored: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class TripletSyncState:
    network_state_id: str
    regime_label: str
    rep_index: int
    rows: List[dict] = field(default_factory=list)
    prb_drift_pct: Optional[float] = None
    score_range: Optional[float] = None
    admission_drift: bool = False


def prb_corridor_guard(
    prb_pct: Optional[float],
    *,
    lo: float = PRB_CORRIDOR_LO,
    hi: float = PRB_CORRIDOR_HI,
    abort_pct: float = PRB_ABORT_PCT,
) -> GuardResult:
    """PRB 18–24% corridor; hard abort >=24%."""
    checks: Dict[str, bool] = {}
    if prb_pct is None:
        return GuardResult(ControlVerdict.WARN, reason="PRB missing")
    if prb_pct >= abort_pct:
        return GuardResult(
            ControlVerdict.ABORT,
            checks={"prb_below_abort": False},
            monitored={"prb_pct": prb_pct},
            reason=f"PRB>={abort_pct}%",
        )
    if prb_pct >= PRB_SOFT_ABORT_PCT:
        return GuardResult(
            ControlVerdict.SKIP_REP,
            checks={"prb_soft": False},
            monitored={"prb_pct": prb_pct},
            reason=f"PRB>={PRB_SOFT_ABORT_PCT}% soft abort",
        )
    checks["prb_in_corridor"] = lo <= prb_pct <= hi
    checks["prb_below_hard_abort"] = prb_pct < abort_pct
    ok = all(checks.values())
    return GuardResult(
        ControlVerdict.PASS if ok else ControlVerdict.SKIP_REP,
        checks=checks,
        monitored={"prb_pct": prb_pct},
        reason="PRB corridor OK" if ok else "PRB outside 18–24%",
    )


def pressure_guard(
    *,
    resource_pressure: Optional[float],
    prb_pct: Optional[float] = None,
    sigma_prb_pct: Optional[float] = None,
    pressure_min: float = CORE_PRESSURE_MIN,
) -> GuardResult:
    """Require real pressure >= pressure_min; no synthetic inflation."""
    checks: Dict[str, bool] = {}
    if resource_pressure is not None:
        checks["pressure_ge_min"] = resource_pressure >= pressure_min
    if prb_pct is not None:
        checks["prb_lt_abort"] = prb_pct < PRB_ABORT_PCT
    if sigma_prb_pct is not None:
        checks["sigma_ok"] = sigma_prb_pct < PRB_SIGMA_MAX_PCT
    if not checks:
        return GuardResult(ControlVerdict.WARN, reason="missing pressure telemetry")
    if prb_pct is not None and prb_pct >= PRB_ABORT_PCT:
        return GuardResult(ControlVerdict.ABORT, reason=f"PRB>={PRB_ABORT_PCT}%")
    if resource_pressure is not None and resource_pressure < pressure_min:
        return GuardResult(
            ControlVerdict.SKIP_REP,
            checks=checks,
            monitored={"resource_pressure": resource_pressure},
            reason=f"pressure<{pressure_min}",
        )
    ok = all(checks.values())
    return GuardResult(
        ControlVerdict.PASS if ok else ControlVerdict.SKIP_REP,
        checks=checks,
        monitored={"resource_pressure": resource_pressure},
        reason="pressure guard pass" if ok else "pressure guard partial fail",
    )


def feasibility_guard(
    *,
    feasibility: Optional[float],
    feasibility_max: float = CORE_FEASIBILITY_MAX,
) -> GuardResult:
    """Require feasibility <= max (liminal low-feasibility envelope)."""
    if feasibility is None:
        return GuardResult(ControlVerdict.WARN, reason="feasibility missing")
    checks = {"feas_le_max": feasibility <= feasibility_max}
    if feasibility > feasibility_max:
        return GuardResult(
            ControlVerdict.SKIP_REP,
            checks=checks,
            monitored={"feasibility": feasibility},
            reason=f"feasibility>{feasibility_max}",
        )
    return GuardResult(
        ControlVerdict.PASS,
        checks=checks,
        monitored={"feasibility": feasibility},
        reason="feasibility guard pass",
    )


def contention_abort_guard(
    *,
    hard_gate_count: int,
    total_submits: int,
    stop_frac: float = HARD_GATE_STOP_FRAC,
) -> GuardResult:
    """Stop regime when hard_gate rate exceeds threshold."""
    if total_submits <= 0:
        return GuardResult(ControlVerdict.PASS, reason="no submits yet")
    rate = hard_gate_count / total_submits
    if rate > stop_frac:
        return GuardResult(
            ControlVerdict.ABORT,
            monitored={"hard_gate_rate": rate, "threshold": stop_frac},
            reason=f"hard_gate rate {rate:.2%} > {stop_frac:.0%}",
        )
    return GuardResult(
        ControlVerdict.PASS,
        monitored={"hard_gate_rate": rate},
        reason="hard_gate rate OK",
    )


class TelemetrySnapshotLock:
    """Per network_state_id lock ID for triplet consistency."""

    def __init__(self) -> None:
        self._locks: Dict[str, str] = {}

    def lock_id(self, network_state_id: str) -> str:
        if network_state_id not in self._locks:
            self._locks[network_state_id] = f"core-lock-{network_state_id}-{int(time.time() * 1000)}"
        return self._locks[network_state_id]

    def clear(self, network_state_id: Optional[str] = None) -> None:
        if network_state_id:
            self._locks.pop(network_state_id, None)
        else:
            self._locks.clear()


def telemetry_snapshot_lock(network_state_id: str, store: Optional[TelemetrySnapshotLock] = None) -> str:
    """Return lock token for snapshot alignment across triplet."""
    s = store or TelemetrySnapshotLock()
    return s.lock_id(network_state_id)


def same_state_triplet_validation(state: TripletSyncState) -> Tuple[bool, str]:
    """Validate URLLC→eMBB→mMTC coherence (no admission drift, no hard_gate)."""
    if len(state.rows) != len(SLICE_ORDER):
        return False, "incomplete triplet"
    prbs = [_safe_float(r.get("prb_utilization_real") or r.get("prb_utilization")) for r in state.rows]
    prbs = [x for x in prbs if x is not None]
    if prbs:
        state.prb_drift_pct = max(prbs) - min(prbs)
    scores = [_safe_float(r.get("decision_score")) for r in state.rows]
    scores = [x for x in scores if x is not None]
    if scores:
        state.score_range = max(scores) - min(scores)
    decs = {str(r.get("decision", "")).upper() for r in state.rows if r.get("decision")}
    state.admission_drift = len(decs) > 1
    if state.admission_drift:
        return False, "admission drift across slices"
    for r in state.rows:
        mode = str(r.get("decision_mode") or r.get("decision_source") or "").lower()
        if "hard_prb" in mode or "hard_gate" in mode:
            return False, "hard_gate in triplet"
    return True, "same-state triplet valid"


class MultiTenantCoordinator:
    """Multi-tenant UPF contention with staggered slot acquisition."""

    def __init__(
        self,
        *,
        n_tenants: int = CONCURRENT_TENANTS,
        stagger_s: float = CONCURRENT_STAGGER_S,
    ) -> None:
        self.n_tenants = n_tenants
        self.stagger_s = stagger_s
        self._active: List[str] = []
        self._last_slot: Dict[int, float] = {}

    def tenant_id(self, run_tag: str, regime: str, rep: int, slot: int) -> str:
        return f"core-{run_tag}-{regime}-r{rep:03d}-t{slot}"

    def acquire_slot(self, slot: int) -> None:
        now = time.time()
        last = self._last_slot.get(slot, 0.0)
        wait = self.stagger_s - (now - last)
        if wait > 0:
            time.sleep(wait)
        self._last_slot[slot] = time.time()

    def register(self, tenant_id: str) -> bool:
        if tenant_id in self._active:
            return False
        self._active.append(tenant_id)
        return True

    def release(self, tenant_id: str) -> None:
        if tenant_id in self._active:
            self._active.remove(tenant_id)

    def to_dict(self) -> dict:
        return {"n_tenants": self.n_tenants, "stagger_s": self.stagger_s, "active": list(self._active)}


class UPFContentionSynchronizer:
    """Barrier sync for UPF load steps + triplet execution."""

    def __init__(
        self,
        *,
        slice_order: Sequence[str] = SLICE_ORDER,
        pause_s: float = TRIPLET_PAUSE_S,
        lock_store: Optional[TelemetrySnapshotLock] = None,
    ) -> None:
        self.slice_order = tuple(slice_order)
        self.pause_s = pause_s
        self.lock_store = lock_store or TelemetrySnapshotLock()

    def network_state_id(self, regime: str, rep: int) -> str:
        return f"{regime}-rep{rep:03d}"

    def run_triplet(
        self,
        state: TripletSyncState,
        submit_fn: Callable[[str, str], dict],
        *,
        dry_run: bool = False,
    ) -> TripletSyncState:
        lock = telemetry_snapshot_lock(state.network_state_id, self.lock_store)
        state.rows = []
        for sl in self.slice_order:
            if dry_run:
                row = {
                    "slice": sl,
                    "decision": "RENEGOTIATE",
                    "decision_mode": "decision_score",
                    "decision_score": 0.72,
                    "dry_run": True,
                }
            else:
                row = submit_fn(sl, state.network_state_id)
            row["network_state_id"] = state.network_state_id
            row["slice"] = sl
            row["rep_index"] = state.rep_index
            row["regime_mbps"] = state.regime_label
            row["telemetry_snapshot_lock"] = lock
            state.rows.append(row)
            time.sleep(self.pause_s if not dry_run else 0.0)
        return state


class RuntimeStabilityMonitor:
    """Track submits, hard gates, aborts for regime stop."""

    def __init__(self) -> None:
        self.total_submits = 0
        self.hard_gate_count = 0
        self.skip_count = 0
        self.abort_count = 0

    def record_submit(self, *, is_hard_gate: bool = False) -> None:
        self.total_submits += 1
        if is_hard_gate:
            self.hard_gate_count += 1

    def record_skip(self) -> None:
        self.skip_count += 1

    def record_abort(self) -> None:
        self.abort_count += 1

    def check_regime_stop(self) -> GuardResult:
        return contention_abort_guard(
            hard_gate_count=self.hard_gate_count,
            total_submits=self.total_submits,
        )

    def to_dict(self) -> dict:
        return {
            "total_submits": self.total_submits,
            "hard_gate_count": self.hard_gate_count,
            "skip_count": self.skip_count,
            "abort_count": self.abort_count,
        }


class ContentionEvidenceCollector:
    """Append-only guard evidence for reviewer-safe packs."""

    def __init__(self) -> None:
        self.events: List[dict] = []

    def record(self, event_type: str, payload: dict) -> None:
        self.events.append(
            {
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "type": event_type,
                **payload,
            }
        )

    def to_dict(self) -> dict:
        return {"n_events": len(self.events), "events": self.events}

    def write_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


def pre_triplet_core_validation(
    sample_prb_fn: Callable[[], Optional[float]],
    *,
    resource_pressure: Optional[float],
    feasibility: Optional[float],
) -> Tuple[ControlVerdict, GuardResult, GuardResult, GuardResult, List[float]]:
    """PRB samples + pressure + feasibility + corridor before triplet."""
    prb_vals: List[float] = []
    for _ in range(PRE_PROBE_SAMPLES):
        v = sample_prb_fn()
        if v is not None:
            prb_vals.append(v)
        time.sleep(0.01)
    peak = max(prb_vals) if prb_vals else None
    sigma = statistics.pstdev(prb_vals) if len(prb_vals) >= 2 else None
    pg = pressure_guard(resource_pressure=resource_pressure, prb_pct=peak, sigma_prb_pct=sigma)
    fg = feasibility_guard(feasibility=feasibility)
    pc = prb_corridor_guard(peak)
    if pg.verdict == ControlVerdict.ABORT or pc.verdict == ControlVerdict.ABORT:
        return ControlVerdict.ABORT, pg, fg, pc, prb_vals
    if pg.verdict != ControlVerdict.PASS or fg.verdict != ControlVerdict.PASS:
        return ControlVerdict.SKIP_REP, pg, fg, pc, prb_vals
    if pc.verdict != ControlVerdict.PASS:
        return ControlVerdict.SKIP_REP, pg, fg, pc, prb_vals
    return ControlVerdict.PASS, pg, fg, pc, prb_vals


def inventory() -> Dict[str, Any]:
    return {
        "module": "docs/scripts/core_contention_runtime_controls.py",
        "digest_required": ACTIVE_DIGEST,
        "components": [
            "MultiTenantCoordinator",
            "UPFContentionSynchronizer",
            "pressure_guard",
            "feasibility_guard",
            "prb_corridor_guard",
            "contention_abort_guard",
            "telemetry_snapshot_lock",
            "same_state_triplet_validation",
            "ContentionEvidenceCollector",
            "RuntimeStabilityMonitor",
            "pre_triplet_core_validation",
        ],
        "policy": {
            "prb_corridor": [PRB_CORRIDOR_LO, PRB_CORRIDOR_HI],
            "prb_abort_pct": PRB_ABORT_PCT,
            "pressure_min": CORE_PRESSURE_MIN,
            "feasibility_max": CORE_FEASIBILITY_MAX,
            "warmup_s": WARMUP_S,
            "stagger_s": CONCURRENT_STAGGER_S,
            "hard_gate_stop_frac": HARD_GATE_STOP_FRAC,
        },
        "ladder": DEFAULT_LADDER_CORE,
        "forbidden": [
            "decision-engine edits",
            "portal telemetry injection",
            "synthetic pressure/feasibility",
            "PRB gate weakening",
        ],
    }


def self_test() -> Dict[str, Any]:
    r: Dict[str, Any] = {}
    r["prb_corridor_pass"] = prb_corridor_guard(20.0).verdict == ControlVerdict.PASS
    r["prb_corridor_skip"] = prb_corridor_guard(17.0).verdict == ControlVerdict.SKIP_REP
    r["prb_abort"] = prb_corridor_guard(24.5).verdict == ControlVerdict.ABORT
    r["pressure_pass"] = pressure_guard(resource_pressure=0.35, prb_pct=20.0).verdict == ControlVerdict.PASS
    r["pressure_skip_low"] = pressure_guard(resource_pressure=0.12, prb_pct=20.0).verdict == ControlVerdict.SKIP_REP
    r["feas_pass"] = feasibility_guard(feasibility=0.50).verdict == ControlVerdict.PASS
    r["feas_skip_high"] = feasibility_guard(feasibility=0.70).verdict == ControlVerdict.SKIP_REP
    r["contention_abort"] = (
        contention_abort_guard(hard_gate_count=3, total_submits=10).verdict == ControlVerdict.ABORT
    )
    r["contention_ok"] = (
        contention_abort_guard(hard_gate_count=1, total_submits=10).verdict == ControlVerdict.PASS
    )
    lock = telemetry_snapshot_lock("test-ns")
    r["snapshot_lock"] = lock.startswith("core-lock-")
    state = TripletSyncState("ns1", "24M", 0)
    state.rows = [
        {"slice": "URLLC", "decision": "RENEGOTIATE", "decision_mode": "decision_score"},
        {"slice": "eMBB", "decision": "RENEGOTIATE", "decision_mode": "decision_score"},
        {"slice": "mMTC", "decision": "RENEGOTIATE", "decision_mode": "decision_score"},
    ]
    ok, _ = same_state_triplet_validation(state)
    r["triplet_valid"] = ok
    coord = MultiTenantCoordinator()
    r["tenant_id"] = coord.tenant_id("t", "28M", 1, 0).startswith("core-")
    sync = UPFContentionSynchronizer()
    st = TripletSyncState("28M-rep000", "28M", 0)
    sync.run_triplet(st, lambda s, n: {}, dry_run=True)
    r["dry_run_triplet"] = len(st.rows) == 3
    ev = ContentionEvidenceCollector()
    ev.record("test", {"ok": True})
    r["evidence"] = ev.to_dict()["n_events"] == 1
    mon = RuntimeStabilityMonitor()
    for _ in range(9):
        mon.record_submit()
    mon.record_submit(is_hard_gate=True)
    r["stability"] = mon.check_regime_stop().verdict == ControlVerdict.PASS
    pre_v, _, _, _, _ = pre_triplet_core_validation(
        lambda: 20.0, resource_pressure=0.35, feasibility=0.50
    )
    r["pre_triplet_pass"] = pre_v == ControlVerdict.PASS
    return r


def _cli() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Core contention runtime controls")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--inventory", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        results = self_test()
        print(json.dumps(results, indent=2))
        return 0 if all(results.values()) else 1
    if args.inventory:
        print(json.dumps(inventory(), indent=2))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_cli())
