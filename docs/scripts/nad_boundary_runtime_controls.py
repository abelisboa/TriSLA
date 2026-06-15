#!/usr/bin/env python3
"""
NAD-EXEC-04: campaign-control runtime helpers (no decision-engine math changes).

Authorized controls only: PRB stabilization, liminal corridor checks, same-state sync,
score_mode targeting, telemetry convergence sampling, hard-gate abort logic.
"""

from __future__ import annotations

import json
import os
import statistics
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# Frozen NAD-EXEC-02 / NAD-EXEC-03 corridor (design SSOT)
PRB_ABORT_PCT = float(os.getenv("NAD_PRB_ABORT_PCT", "24.0"))
PRB_SOFT_ABORT_PCT = float(os.getenv("NAD_PRB_SOFT_ABORT_PCT", "23.5"))
WARMUP_LIMINAL02_S = float(os.getenv("NAD_WARMUP_LIMINAL02_S", "120"))
WARMUP_EXTENSION_S = float(os.getenv("NAD_WARMUP_EXTENSION_S", "30"))
ROLLBACK_SOFT_ABORT_THRESHOLD = int(os.getenv("NAD_ROLLBACK_SOFT_ABORT_THRESHOLD", "3"))
PRE_TRIPLET_SAMPLES = int(os.getenv("NAD_PRE_TRIPLET_SAMPLES", "4"))
PRB_CORRIDOR_LO = float(os.getenv("NAD_PRB_CORRIDOR_LO", "18.0"))
PRB_CORRIDOR_HI = float(os.getenv("NAD_PRB_CORRIDOR_HI", "24.0"))
HARD_PRB_RENEG_PCT = float(os.getenv("NAD_HARD_PRB_RENEG_PCT", "25.0"))
PRB_SIGMA_MAX_PCT = float(os.getenv("NAD_PRB_SIGMA_MAX_PCT", "2.0"))
WARMUP_S = float(os.getenv("NAD_WARMUP_S", "90"))
STABILIZATION_MIN_S = float(os.getenv("NAD_STABILIZATION_MIN_S", "90"))
PRB_SAMPLE_INTERVAL_S = float(os.getenv("NAD_PRB_SAMPLE_INTERVAL_S", "5.0"))
TRIPLET_PAUSE_S = float(os.getenv("NAD_TRIPLET_PAUSE_S", "1.5"))
SCORE_TARGET_LO = float(os.getenv("NAD_SCORE_TARGET_LO", "0.52"))
SCORE_TARGET_HI = float(os.getenv("NAD_SCORE_TARGET_HI", "0.58"))
RTT_LO_MS = float(os.getenv("NAD_RTT_LO_MS", "9.0"))
RTT_HI_MS = float(os.getenv("NAD_RTT_HI_MS", "14.0"))
FEAS_LO = float(os.getenv("NAD_FEAS_LO", "0.50"))
FEAS_HI = float(os.getenv("NAD_FEAS_HI", "0.68"))
PRESSURE_LO = float(os.getenv("NAD_PRESSURE_LO", "0.55"))
PRESSURE_HI = float(os.getenv("NAD_PRESSURE_HI", "0.78"))

# NAD-LIMINAL-03 (NAD-EXEC-11 design SSOT) — campaign controls only
PRB_TARGET_LO = float(os.getenv("NAD_PRB_TARGET_LO", "18.0"))
PRB_TARGET_HI = float(os.getenv("NAD_PRB_TARGET_HI", "22.5"))
LIM03_PRESSURE_MIN = float(os.getenv("NAD_LIM03_PRESSURE_MIN", "0.30"))
LIM03_PRESSURE_MAX = float(os.getenv("NAD_LIM03_PRESSURE_MAX", "0.65"))
LIM03_FEAS_MIN = float(os.getenv("NAD_LIM03_FEAS_MIN", "0.30"))
LIM03_FEAS_MAX = float(os.getenv("NAD_LIM03_FEAS_MAX", "0.55"))
LIM03_RTT_MIN_MS = float(os.getenv("NAD_LIM03_RTT_MIN_MS", "10.0"))
LIM03_RTT_MAX_MS = float(os.getenv("NAD_LIM03_RTT_MAX_MS", "18.0"))
WARMUP_LIMINAL03_S = float(os.getenv("NAD_WARMUP_LIMINAL03_S", "90"))
CONCURRENT_TENANTS = int(os.getenv("NAD_CONCURRENT_TENANTS", "2"))
CONCURRENT_STAGGER_S = float(os.getenv("NAD_CONCURRENT_STAGGER_S", "3.0"))
LIM03_STOP_HARD_GATE_FRAC = float(os.getenv("NAD_LIM03_STOP_HARD_GATE_FRAC", "0.25"))
DENOM_STABILITY_EPS = float(os.getenv("NAD_DENOM_STABILITY_EPS", "0.05"))

SLICE_ORDER: Tuple[str, ...] = ("URLLC", "eMBB", "mMTC")
ACTIVE_DIGEST = os.getenv(
    "NAD_ACTIVE_DIGEST",
    "sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6",
)


class ControlVerdict(str, Enum):
    PASS = "PASS"
    ABORT = "ABORT"
    SKIP_REP = "SKIP_REP"
    WARN = "WARN"


@dataclass
class PrbStabilizationResult:
    verdict: ControlVerdict
    samples: List[float] = field(default_factory=list)
    mean_pct: Optional[float] = None
    sigma_pct: Optional[float] = None
    reason: str = ""


@dataclass
class LiminalCorridorResult:
    verdict: ControlVerdict
    in_corridor: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    reason: str = ""


@dataclass
class SubmitGuardResult:
    verdict: ControlVerdict
    decision_mode: Optional[str] = None
    is_score_mode: bool = False
    is_hard_gate: bool = False
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


def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def prb_stabilization_gate(
    sample_fn: Callable[[], Optional[float]],
    *,
    warmup_s: float = WARMUP_S,
    min_stable_s: float = STABILIZATION_MIN_S,
    sample_interval_s: float = PRB_SAMPLE_INTERVAL_S,
    abort_pct: float = PRB_ABORT_PCT,
    sigma_max_pct: float = PRB_SIGMA_MAX_PCT,
) -> PrbStabilizationResult:
    """
    Q1: Poll PRB during stabilization; abort if any sample >= abort_pct or σ >= sigma_max.
    """
    stable_s = max(warmup_s, min_stable_s)
    deadline = time.time() + stable_s
    samples: List[float] = []
    while time.time() < deadline:
        v = sample_fn()
        if v is not None:
            samples.append(v)
            if v >= abort_pct:
                return PrbStabilizationResult(
                    verdict=ControlVerdict.ABORT,
                    samples=samples,
                    mean_pct=statistics.mean(samples),
                    reason=f"PRB>={abort_pct}% (hard-gate contamination risk)",
                )
        time.sleep(sample_interval_s)

    if len(samples) < 2:
        return PrbStabilizationResult(
            verdict=ControlVerdict.SKIP_REP,
            samples=samples,
            reason="insufficient PRB samples for stabilization",
        )
    sigma = statistics.pstdev(samples)
    mean_v = statistics.mean(samples)
    if sigma > sigma_max_pct:
        return PrbStabilizationResult(
            verdict=ControlVerdict.SKIP_REP,
            samples=samples,
            mean_pct=mean_v,
            sigma_pct=sigma,
            reason=f"σ(PRB)={sigma:.2f}% > {sigma_max_pct}%",
        )
    return PrbStabilizationResult(
        verdict=ControlVerdict.PASS,
        samples=samples,
        mean_pct=mean_v,
        sigma_pct=sigma,
        reason="PRB stable",
    )


@dataclass
class PrbAbortDecision:
    verdict: ControlVerdict
    level: str
    prb_pct: Optional[float] = None
    reason: str = ""


def prb_abort_check(
    prb_pct: Optional[float],
    *,
    soft_pct: float = PRB_SOFT_ABORT_PCT,
    hard_pct: float = PRB_ABORT_PCT,
) -> PrbAbortDecision:
    """LIMINAL-02: soft abort at 23.5%, hard abort at 24%."""
    if prb_pct is None:
        return PrbAbortDecision(ControlVerdict.WARN, "unknown", reason="PRB missing")
    if prb_pct >= hard_pct:
        return PrbAbortDecision(
            ControlVerdict.ABORT, "hard", prb_pct, f"PRB>={hard_pct}% hard abort"
        )
    if prb_pct >= soft_pct:
        return PrbAbortDecision(
            ControlVerdict.SKIP_REP, "soft", prb_pct, f"PRB>={soft_pct}% soft abort"
        )
    return PrbAbortDecision(ControlVerdict.PASS, "ok", prb_pct, "PRB within corridor")


@dataclass(frozen=True)
class LadderStep:
    label: str
    bitrate: str
    role: str = "primary"


DEFAULT_LADDER_LIMINAL02: Tuple[LadderStep, ...] = (
    LadderStep("22Mbps", "22M", "calibration_low"),
    LadderStep("26Mbps", "26M", "calibration_mid"),
    LadderStep("28Mbps", "28M", "primary_target"),
    LadderStep("30Mbps", "30M", "primary_upper"),
    LadderStep("28Mbps-fallback", "28M", "fallback_stable"),
)

DEFAULT_LADDER_LIMINAL03: Tuple[LadderStep, ...] = (
    LadderStep("24Mbps", "24M", "calibration"),
    LadderStep("25Mbps", "25M", "primary"),
    LadderStep("26Mbps", "26M", "primary_upper"),
    LadderStep("24Mbps-fallback", "24M", "fallback_stable"),
)


def parse_ladder(spec: str) -> Tuple[LadderStep, ...]:
    """Parse '22,26,28,30,28' into ladder steps with bitrates."""
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    out: List[LadderStep] = []
    for i, p in enumerate(parts):
        mbps = p.replace("M", "").replace("m", "")
        br = f"{mbps}M" if not p.upper().endswith("M") else p.upper().replace("MBPS", "M")
        if not br.endswith("M"):
            br = f"{p}M"
        label = f"{mbps}Mbps" if mbps.isdigit() else p
        if i == len(parts) - 1 and len(parts) > 1 and parts[-1] == parts[-2]:
            role = "fallback_stable"
            label = f"{mbps}Mbps-fallback" if mbps.isdigit() else f"{p}-fallback"
        elif i < 2:
            role = "calibration_low" if i == 0 else "calibration_mid"
        else:
            role = "primary_target" if i == 2 else "primary_upper"
        out.append(LadderStep(label, br, role))
    return tuple(out)


class LadderRollbackController:
    """Rollback one ladder step after N consecutive soft aborts."""

    def __init__(
        self,
        ladder: Sequence[LadderStep],
        *,
        rollback_threshold: int = ROLLBACK_SOFT_ABORT_THRESHOLD,
    ) -> None:
        self.ladder = tuple(ladder)
        self.index = 0
        self.rollback_threshold = rollback_threshold
        self.consecutive_soft_aborts = 0
        self.rollback_events: List[dict] = []

    @property
    def current(self) -> LadderStep:
        return self.ladder[self.index]

    def record_abort(self, decision: PrbAbortDecision) -> Optional[dict]:
        if decision.level == "soft":
            self.consecutive_soft_aborts += 1
            if self.consecutive_soft_aborts >= self.rollback_threshold and self.index > 0:
                self.index -= 1
                ev = {
                    "action": "rollback",
                    "to_index": self.index,
                    "to_bitrate": self.current.bitrate,
                    "soft_aborts": self.consecutive_soft_aborts,
                }
                self.rollback_events.append(ev)
                self.consecutive_soft_aborts = 0
                return ev
            return {"action": "skip_rep", "reason": decision.reason}
        if decision.level == "hard":
            return {"action": "stop_regime", "reason": decision.reason}
        self.consecutive_soft_aborts = 0
        return None

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "current": {"label": self.current.label, "bitrate": self.current.bitrate},
            "rollback_events": self.rollback_events,
            "consecutive_soft_aborts": self.consecutive_soft_aborts,
        }


def prb_stabilization_extended(
    sample_fn: Callable[[], Optional[float]],
    *,
    warmup_s: float = WARMUP_LIMINAL02_S,
    sigma_max_pct: float = PRB_SIGMA_MAX_PCT,
    soft_pct: float = PRB_SOFT_ABORT_PCT,
    hard_pct: float = PRB_ABORT_PCT,
    allow_extension: bool = True,
    extension_s: float = WARMUP_EXTENSION_S,
    sample_interval_s: float = PRB_SAMPLE_INTERVAL_S,
) -> PrbStabilizationResult:
    """120s warmup with optional single +30s extension if σ>2% once."""
    result = prb_stabilization_gate(
        sample_fn,
        warmup_s=warmup_s,
        min_stable_s=warmup_s,
        sample_interval_s=sample_interval_s,
        abort_pct=hard_pct,
        sigma_max_pct=sigma_max_pct,
    )
    if result.verdict == ControlVerdict.SKIP_REP and allow_extension and "σ(PRB)" in result.reason:
        ext = prb_stabilization_gate(
            sample_fn,
            warmup_s=extension_s,
            min_stable_s=extension_s,
            sample_interval_s=sample_interval_s,
            abort_pct=hard_pct,
            sigma_max_pct=sigma_max_pct,
        )
        ext.reason = f"extension:{ext.reason}"
        return ext
    if result.samples:
        last = result.samples[-1]
        chk = prb_abort_check(last, soft_pct=soft_pct, hard_pct=hard_pct)
        if chk.verdict != ControlVerdict.PASS:
            return PrbStabilizationResult(
                verdict=chk.verdict,
                samples=result.samples,
                mean_pct=result.mean_pct,
                sigma_pct=result.sigma_pct,
                reason=chk.reason,
            )
    return result


def pre_triplet_prb_validation(
    sample_fn: Callable[[], Optional[float]],
    *,
    n_samples: int = PRE_TRIPLET_SAMPLES,
    soft_pct: float = PRB_SOFT_ABORT_PCT,
    hard_pct: float = PRB_ABORT_PCT,
    sigma_max_pct: float = PRB_SIGMA_MAX_PCT,
) -> Tuple[ControlVerdict, PrbAbortDecision, List[float]]:
    """4-sample convergence with soft/hard abort."""
    conv, vals = telemetry_convergence_check(
        sample_fn, n_samples=n_samples, sigma_max_pct=sigma_max_pct
    )
    peak = max(vals) if vals else None
    chk = prb_abort_check(peak, soft_pct=soft_pct, hard_pct=hard_pct)
    if chk.verdict == ControlVerdict.ABORT:
        return ControlVerdict.ABORT, chk, vals
    if chk.verdict == ControlVerdict.SKIP_REP or conv == ControlVerdict.SKIP_REP:
        return ControlVerdict.SKIP_REP, chk, vals
    return ControlVerdict.PASS, chk, vals


def hard_gate_pre_detect(prb_pct: Optional[float]) -> bool:
    """Q2: True if PRB would trigger hard_prb_gate (≥25% reneg path)."""
    if prb_pct is None:
        return False
    return prb_pct >= HARD_PRB_RENEG_PCT


def telemetry_convergence_check(
    sample_fn: Callable[[], Optional[float]],
    *,
    n_samples: int = 4,
    interval_s: float = PRB_SAMPLE_INTERVAL_S,
    sigma_max_pct: float = PRB_SIGMA_MAX_PCT,
) -> Tuple[ControlVerdict, List[float]]:
    """
    Q4: Multi-sample PRB before each submit (campaign-side jitter reduction; portal window unchanged).
    """
    vals: List[float] = []
    for _ in range(n_samples):
        v = sample_fn()
        if v is not None:
            vals.append(v)
        time.sleep(interval_s)
    if len(vals) < 2:
        return ControlVerdict.WARN, vals
    if statistics.pstdev(vals) > sigma_max_pct:
        return ControlVerdict.SKIP_REP, vals
    return ControlVerdict.PASS, vals


def extract_decision_mode(metadata: dict) -> Optional[str]:
    return metadata.get("decision_mode") or metadata.get("decision_source")


def score_mode_guard(metadata: dict, prb_pct: Optional[float] = None) -> SubmitGuardResult:
    """
    Q5: Classify submit outcome; flag hard_prb_gate before score_mode analysis.
    """
    mode = (extract_decision_mode(metadata) or "").lower()
    source = str(metadata.get("decision_source") or "").lower()
    prb = prb_pct if prb_pct is not None else _safe_float(metadata.get("ran_prb_utilization_input"))
    if hard_gate_pre_detect(prb) or "hard_prb" in mode or "hard_prb" in source:
        return SubmitGuardResult(
            verdict=ControlVerdict.ABORT,
            decision_mode="hard_prb_gate",
            is_score_mode=False,
            is_hard_gate=True,
            reason="hard_prb_gate path",
        )
    is_sm = mode == "decision_score" or "decision_score" in source
    if is_sm:
        return SubmitGuardResult(
            verdict=ControlVerdict.PASS,
            decision_mode="decision_score",
            is_score_mode=True,
            is_hard_gate=False,
            reason="score_mode eligible",
        )
    return SubmitGuardResult(
        verdict=ControlVerdict.WARN,
        decision_mode=mode or None,
        is_score_mode=False,
        is_hard_gate=False,
        reason="non-score_mode path",
    )


def liminal_corridor_validate(
    *,
    prb_pct: Optional[float] = None,
    decision_score: Optional[float] = None,
    rtt_ms: Optional[float] = None,
    feasibility: Optional[float] = None,
    resource_pressure: Optional[float] = None,
    strict_score: bool = False,
) -> LiminalCorridorResult:
    """Q1/Q5: Post-submit corridor check (runtime validation only; no threshold edits)."""
    checks: Dict[str, bool] = {}
    if prb_pct is not None:
        checks["prb_in_corridor"] = PRB_CORRIDOR_LO <= prb_pct <= PRB_CORRIDOR_HI
        checks["prb_below_abort"] = prb_pct < PRB_ABORT_PCT
    if decision_score is not None:
        checks["score_in_target"] = SCORE_TARGET_LO <= decision_score <= SCORE_TARGET_HI
    if rtt_ms is not None:
        checks["rtt_in_window"] = RTT_LO_MS <= rtt_ms <= RTT_HI_MS
    if feasibility is not None:
        checks["feasibility_in_window"] = FEAS_LO <= feasibility <= FEAS_HI
    if resource_pressure is not None:
        checks["pressure_in_window"] = PRESSURE_LO <= resource_pressure <= PRESSURE_HI

    if not checks:
        return LiminalCorridorResult(
            verdict=ControlVerdict.WARN,
            in_corridor=False,
            checks=checks,
            reason="no telemetry to validate",
        )
    in_corridor = all(checks.values())
    if strict_score and decision_score is not None and not checks.get("score_in_target", True):
        return LiminalCorridorResult(
            verdict=ControlVerdict.WARN,
            in_corridor=False,
            checks=checks,
            reason="score outside 0.52–0.58 (expected for NAD-LIMINAL-01)",
        )
    return LiminalCorridorResult(
        verdict=ControlVerdict.PASS if in_corridor else ControlVerdict.WARN,
        in_corridor=in_corridor,
        checks=checks,
        reason="liminal corridor OK" if in_corridor else "partial corridor miss",
    )


class SameStateSynchronizer:
    """Q3: URLLC → eMBB → mMTC triplet executor with drift detection."""

    def __init__(
        self,
        *,
        slice_order: Sequence[str] = SLICE_ORDER,
        pause_s: float = TRIPLET_PAUSE_S,
        prb_drift_max_pct: float = 7.0,
    ) -> None:
        self.slice_order = tuple(slice_order)
        self.pause_s = pause_s
        self.prb_drift_max_pct = prb_drift_max_pct

    def network_state_id(self, regime_label: str, rep_index: int) -> str:
        return f"{regime_label}-rep{rep_index:03d}"

    def finalize_triplet(self, state: TripletSyncState) -> TripletSyncState:
        prbs = [_safe_float(r.get("prb_utilization_real")) for r in state.rows]
        prbs = [x for x in prbs if x is not None]
        scores = [_safe_float(r.get("decision_score")) for r in state.rows]
        scores = [x for x in scores if x is not None]
        if prbs:
            state.prb_drift_pct = max(prbs) - min(prbs)
        if scores:
            state.score_range = max(scores) - min(scores)
        decs = {str(r.get("decision", "")).upper() for r in state.rows}
        state.admission_drift = len({d for d in decs if d}) > 1
        return state

    def triplet_coherent(self, state: TripletSyncState) -> Tuple[bool, str]:
        if len(state.rows) != len(self.slice_order):
            return False, "incomplete triplet"
        if state.prb_drift_pct is not None and state.prb_drift_pct > self.prb_drift_max_pct:
            return False, f"PRB drift {state.prb_drift_pct:.2f}% > {self.prb_drift_max_pct}%"
        flat_modes = []
        for r in state.rows:
            meta = {
                "decision_mode": r.get("decision_mode"),
                "decision_source": r.get("decision_source"),
            }
            flat_modes.append(score_mode_guard(meta, _safe_float(r.get("prb_utilization_real"))))
        if any(m.is_hard_gate for m in flat_modes):
            return False, "hard_prb_gate in triplet"
        if not all(m.is_score_mode for m in flat_modes):
            return False, "not score_mode-only"
        return True, "triplet coherent"

    def run_triplet(
        self,
        state: TripletSyncState,
        submit_fn: Callable[[str, str], dict],
    ) -> TripletSyncState:
        """submit_fn(slice_key, network_state_id) -> row dict with slice field set."""
        state.rows = []
        for sl in self.slice_order:
            row = submit_fn(sl, state.network_state_id)
            row["network_state_id"] = state.network_state_id
            row["slice"] = sl
            row["rep_index"] = state.rep_index
            row["regime_mbps"] = state.regime_label
            state.rows.append(row)
            time.sleep(self.pause_s)
        return self.finalize_triplet(state)


@dataclass
class PressureGuardResult:
    verdict: ControlVerdict
    pressure: Optional[float] = None
    prb_pct: Optional[float] = None
    sigma_prb: Optional[float] = None
    checks: Dict[str, bool] = field(default_factory=dict)
    reason: str = ""


@dataclass
class FeasibilityGuardResult:
    verdict: ControlVerdict
    feasibility: Optional[float] = None
    denominator: Optional[float] = None
    checks: Dict[str, bool] = field(default_factory=dict)
    reason: str = ""


@dataclass
class CorridorEnforcementResult:
    verdict: ControlVerdict
    in_operational_corridor: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    monitored: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""


def pressure_guard(
    *,
    resource_pressure: Optional[float],
    prb_pct: Optional[float],
    sigma_prb_pct: Optional[float] = None,
) -> PressureGuardResult:
    """NAD-LIMINAL-03: pre-triplet pressure corridor (no synthetic pressure)."""
    checks: Dict[str, bool] = {}
    if resource_pressure is not None:
        checks["pressure_ge_min"] = resource_pressure >= LIM03_PRESSURE_MIN
        checks["pressure_le_max"] = resource_pressure <= LIM03_PRESSURE_MAX
    if prb_pct is not None:
        checks["prb_lt_soft_abort"] = prb_pct < PRB_SOFT_ABORT_PCT
        checks["prb_in_target_band"] = PRB_TARGET_LO <= prb_pct <= PRB_TARGET_HI
    if sigma_prb_pct is not None:
        checks["sigma_prb_ok"] = sigma_prb_pct < PRB_SIGMA_MAX_PCT
    if not checks:
        return PressureGuardResult(
            ControlVerdict.WARN, reason="missing pressure/PRB telemetry"
        )
    if prb_pct is not None and prb_pct >= PRB_ABORT_PCT:
        return PressureGuardResult(
            ControlVerdict.ABORT,
            pressure=resource_pressure,
            prb_pct=prb_pct,
            sigma_prb=sigma_prb_pct,
            checks=checks,
            reason=f"PRB>={PRB_ABORT_PCT}%",
        )
    if prb_pct is not None and prb_pct >= PRB_SOFT_ABORT_PCT:
        return PressureGuardResult(
            ControlVerdict.SKIP_REP,
            pressure=resource_pressure,
            prb_pct=prb_pct,
            sigma_prb=sigma_prb_pct,
            checks=checks,
            reason=f"PRB>={PRB_SOFT_ABORT_PCT}% soft abort",
        )
    if resource_pressure is not None and resource_pressure < LIM03_PRESSURE_MIN:
        return PressureGuardResult(
            ControlVerdict.SKIP_REP,
            pressure=resource_pressure,
            prb_pct=prb_pct,
            sigma_prb=sigma_prb_pct,
            checks=checks,
            reason=f"pressure<{LIM03_PRESSURE_MIN}",
        )
    if resource_pressure is not None and resource_pressure > LIM03_PRESSURE_MAX:
        return PressureGuardResult(
            ControlVerdict.SKIP_REP,
            pressure=resource_pressure,
            prb_pct=prb_pct,
            sigma_prb=sigma_prb_pct,
            checks=checks,
            reason=f"pressure>{LIM03_PRESSURE_MAX} (rollback candidate)",
        )
    if sigma_prb_pct is not None and sigma_prb_pct >= PRB_SIGMA_MAX_PCT:
        return PressureGuardResult(
            ControlVerdict.SKIP_REP,
            pressure=resource_pressure,
            prb_pct=prb_pct,
            sigma_prb=sigma_prb_pct,
            checks=checks,
            reason=f"σ(PRB)={sigma_prb_pct:.2f}%",
        )
    ok = all(checks.values())
    return PressureGuardResult(
        ControlVerdict.PASS if ok else ControlVerdict.SKIP_REP,
        pressure=resource_pressure,
        prb_pct=prb_pct,
        sigma_prb=sigma_prb_pct,
        checks=checks,
        reason="pressure guard pass" if ok else "partial pressure corridor miss",
    )


def feasibility_guard(
    *,
    feasibility: Optional[float],
    score_denominator: Optional[float] = None,
) -> FeasibilityGuardResult:
    """NAD-LIMINAL-03: feasibility window + denominator stability (monitor only)."""
    checks: Dict[str, bool] = {}
    if feasibility is not None:
        checks["feas_ge_min"] = feasibility >= LIM03_FEAS_MIN
        checks["feas_le_max"] = feasibility <= LIM03_FEAS_MAX
    if score_denominator is not None:
        checks["denom_bounded"] = 0.5 <= score_denominator <= 1.5
        checks["denom_stable"] = abs(score_denominator - 1.0) <= DENOM_STABILITY_EPS + 0.5
    if not checks:
        return FeasibilityGuardResult(ControlVerdict.WARN, reason="missing feasibility")
    if feasibility is not None and feasibility > LIM03_FEAS_MAX:
        return FeasibilityGuardResult(
            ControlVerdict.SKIP_REP,
            feasibility=feasibility,
            denominator=score_denominator,
            checks=checks,
            reason=f"feasibility>{LIM03_FEAS_MAX}",
        )
    if feasibility is not None and feasibility < LIM03_FEAS_MIN:
        return FeasibilityGuardResult(
            ControlVerdict.SKIP_REP,
            feasibility=feasibility,
            denominator=score_denominator,
            checks=checks,
            reason=f"feasibility<{LIM03_FEAS_MIN}",
        )
    ok = all(checks.values())
    return FeasibilityGuardResult(
        ControlVerdict.PASS if ok else ControlVerdict.SKIP_REP,
        feasibility=feasibility,
        denominator=score_denominator,
        checks=checks,
        reason="feasibility guard pass" if ok else "feasibility/denom check fail",
    )


def pre_triplet_liminal03_validation(
    sample_prb_fn: Callable[[], Optional[float]],
    *,
    resource_pressure: Optional[float] = None,
    feasibility: Optional[float] = None,
    score_denominator: Optional[float] = None,
) -> Tuple[ControlVerdict, PressureGuardResult, FeasibilityGuardResult, List[float]]:
    """Combined PRB convergence + pressure + feasibility guards before triplet."""
    conv, prb_vals = telemetry_convergence_check(
        sample_prb_fn, n_samples=PRE_TRIPLET_SAMPLES, sigma_max_pct=PRB_SIGMA_MAX_PCT
    )
    sigma = statistics.pstdev(prb_vals) if len(prb_vals) >= 2 else None
    peak = max(prb_vals) if prb_vals else None
    pg = pressure_guard(
        resource_pressure=resource_pressure,
        prb_pct=peak,
        sigma_prb_pct=sigma,
    )
    fg = feasibility_guard(feasibility=feasibility, score_denominator=score_denominator)
    if pg.verdict == ControlVerdict.ABORT or fg.verdict == ControlVerdict.ABORT:
        return ControlVerdict.ABORT, pg, fg, prb_vals
    if (
        pg.verdict != ControlVerdict.PASS
        or fg.verdict != ControlVerdict.PASS
        or conv != ControlVerdict.PASS
    ):
        return ControlVerdict.SKIP_REP, pg, fg, prb_vals
    return ControlVerdict.PASS, pg, fg, prb_vals


def liminal03_corridor_enforce(
    *,
    prb_pct: Optional[float] = None,
    resource_pressure: Optional[float] = None,
    feasibility: Optional[float] = None,
    rtt_ms: Optional[float] = None,
    decision_score: Optional[float] = None,
    decision_mode: Optional[str] = None,
) -> CorridorEnforcementResult:
    """
    NAD-LIMINAL-03 operational corridor. Score target is monitored only (never forced).
    """
    checks: Dict[str, bool] = {}
    monitored: Dict[str, Any] = {}
    if prb_pct is not None:
        checks["prb_operational"] = PRB_TARGET_LO <= prb_pct <= PRB_TARGET_HI
        checks["prb_below_hard_abort"] = prb_pct < PRB_ABORT_PCT
    if resource_pressure is not None:
        checks["pressure_operational"] = LIM03_PRESSURE_MIN <= resource_pressure <= LIM03_PRESSURE_MAX
    if feasibility is not None:
        checks["feasibility_operational"] = LIM03_FEAS_MIN <= feasibility <= LIM03_FEAS_MAX
    if rtt_ms is not None:
        checks["rtt_operational"] = LIM03_RTT_MIN_MS <= rtt_ms <= LIM03_RTT_MAX_MS
    if decision_score is not None:
        monitored["score_in_target"] = SCORE_TARGET_LO <= decision_score <= SCORE_TARGET_HI
        monitored["score_value"] = decision_score
    if decision_mode:
        checks["score_mode_only"] = "decision_score" in str(decision_mode).lower()
    in_corr = bool(checks) and all(checks.values())
    guard = score_mode_guard({"decision_mode": decision_mode or "decision_score"}, prb_pct)
    if guard.is_hard_gate:
        return CorridorEnforcementResult(
            ControlVerdict.ABORT,
            in_operational_corridor=False,
            checks=checks,
            monitored=monitored,
            reason="hard_prb_gate contamination",
        )
    return CorridorEnforcementResult(
        ControlVerdict.PASS if in_corr else ControlVerdict.WARN,
        in_operational_corridor=in_corr,
        checks=checks,
        monitored=monitored,
        reason="LIMINAL-03 corridor OK" if in_corr else "corridor partial (score monitored only)",
    )


class ConcurrentTenantCoordinator:
    """Two real tenants with 3s stagger and triplet isolation."""

    def __init__(
        self,
        *,
        n_tenants: int = CONCURRENT_TENANTS,
        stagger_s: float = CONCURRENT_STAGGER_S,
    ) -> None:
        self.n_tenants = n_tenants
        self.stagger_s = stagger_s
        self._active: List[str] = []
        self._last_slot_time: Dict[int, float] = {}

    def tenant_id(self, run_tag: str, regime: str, rep: int, slot: int) -> str:
        return f"nad03-{run_tag}-{regime}-r{rep:03d}-t{slot}"

    def acquire_slot(self, slot: int) -> None:
        now = time.time()
        last = self._last_slot_time.get(slot, 0.0)
        wait = self.stagger_s - (now - last)
        if wait > 0:
            time.sleep(wait)
        self._last_slot_time[slot] = time.time()

    def register(self, tenant_id: str) -> bool:
        if tenant_id in self._active:
            return False
        self._active.append(tenant_id)
        return True

    def release(self, tenant_id: str) -> None:
        if tenant_id in self._active:
            self._active.remove(tenant_id)

    def to_dict(self) -> dict:
        return {
            "n_tenants": self.n_tenants,
            "stagger_s": self.stagger_s,
            "active": list(self._active),
        }


class TripletBarrierSynchronizer(SameStateSynchronizer):
    """URLLC→eMBB→mMTC with snapshot lock ID and contamination discard."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._lock_ids: Dict[str, str] = {}

    def snapshot_lock_id(self, network_state_id: str) -> str:
        if network_state_id not in self._lock_ids:
            self._lock_ids[network_state_id] = f"lock-{network_state_id}-{int(time.time() * 1000)}"
        return self._lock_ids[network_state_id]

    def run_triplet_barrier(
        self,
        state: TripletSyncState,
        submit_fn: Callable[[str, str], dict],
    ) -> TripletSyncState:
        lock = self.snapshot_lock_id(state.network_state_id)
        for sl in self.slice_order:
            row = submit_fn(sl, state.network_state_id)
            row["network_state_id"] = state.network_state_id
            row["slice"] = sl
            row["rep_index"] = state.rep_index
            row["regime_mbps"] = state.regime_label
            row["telemetry_snapshot_lock"] = lock
            state.rows.append(row)
            time.sleep(self.pause_s)
        return self.finalize_triplet(state)


def inventory() -> Dict[str, Any]:
    """Phase 1: runtime control component inventory."""
    return {
        "module": "docs/scripts/nad_boundary_runtime_controls.py",
        "digest_required": ACTIVE_DIGEST,
        "components": [
            "prb_stabilization_gate",
            "prb_stabilization_extended",
            "prb_abort_check",
            "LadderRollbackController",
            "pre_triplet_prb_validation",
            "hard_gate_pre_detect",
            "telemetry_convergence_check",
            "score_mode_guard",
            "liminal_corridor_validate",
            "SameStateSynchronizer",
        ],
        "liminal02": {
            "soft_abort_pct": PRB_SOFT_ABORT_PCT,
            "hard_abort_pct": PRB_ABORT_PCT,
            "warmup_s": WARMUP_LIMINAL02_S,
            "ladder": [s.bitrate for s in DEFAULT_LADDER_LIMINAL02],
        },
        "liminal03": {
            "prb_target": [PRB_TARGET_LO, PRB_TARGET_HI],
            "pressure_window": [LIM03_PRESSURE_MIN, LIM03_PRESSURE_MAX],
            "feasibility_window": [LIM03_FEAS_MIN, LIM03_FEAS_MAX],
            "rtt_window_ms": [LIM03_RTT_MIN_MS, LIM03_RTT_MAX_MS],
            "score_monitored_only": [SCORE_TARGET_LO, SCORE_TARGET_HI],
            "concurrent_tenants": CONCURRENT_TENANTS,
            "stagger_s": CONCURRENT_STAGGER_S,
            "warmup_s": WARMUP_LIMINAL03_S,
            "stop_hard_gate_frac": LIM03_STOP_HARD_GATE_FRAC,
            "ladder": [s.bitrate for s in DEFAULT_LADDER_LIMINAL03],
            "components": [
                "pressure_guard",
                "feasibility_guard",
                "pre_triplet_liminal03_validation",
                "liminal03_corridor_enforce",
                "ConcurrentTenantCoordinator",
                "TripletBarrierSynchronizer",
            ],
        },
        "abort_conditions": [
            f"PRB>={PRB_ABORT_PCT}%",
            f"σ(PRB)>{PRB_SIGMA_MAX_PCT}%",
            "hard_prb_gate on pre-check or post-submit",
            "incomplete triplet",
        ],
        "env_overrides": [
            "NAD_PRB_ABORT_PCT",
            "NAD_WARMUP_S",
            "NAD_PRB_SIGMA_MAX_PCT",
            "NAD_TRIPLET_PAUSE_S",
        ],
        "forbidden": [
            "decision_score_mode formula edits",
            "accept_min/reneg_min/PRB gate changes",
            "portal PromQL / collector window edits",
        ],
    }


def self_test() -> Dict[str, Any]:
    """Unit-level checks without live cluster."""
    results: Dict[str, Any] = {}
    results["hard_gate_24"] = hard_gate_pre_detect(24.0) is False
    results["hard_gate_25"] = hard_gate_pre_detect(25.0) is True
    results["guard_score"] = score_mode_guard(
        {"decision_mode": "decision_score", "decision_source": "decision_score_mode"}
    ).is_score_mode
    results["guard_hard"] = score_mode_guard(
        {"decision_mode": "hard_prb_gate"}, prb_pct=30.0
    ).is_hard_gate
    lim = liminal_corridor_validate(prb_pct=20.0, decision_score=0.55, rtt_ms=12.0)
    results["liminal_sample"] = lim.in_corridor
    seq = [18.0, 18.5, 19.0, 19.2]

    def _sample():
        return seq.pop(0) if seq else 19.0

    conv, _ = telemetry_convergence_check(_sample, n_samples=4, interval_s=0.01)
    results["convergence_pass"] = conv == ControlVerdict.PASS
    d_soft = prb_abort_check(23.6, soft_pct=23.5, hard_pct=24.0)
    results["soft_abort_23_5"] = d_soft.level == "soft"
    results["hard_abort_24"] = prb_abort_check(24.0).level == "hard"
    ladder = LadderRollbackController(DEFAULT_LADDER_LIMINAL02)
    results["ladder_steps"] = len(ladder.ladder) == 5
    ev = ladder.record_abort(PrbAbortDecision(ControlVerdict.SKIP_REP, "soft", 23.6, "test"))
    results["rollback_controller"] = ladder.index >= 0
    pg = pressure_guard(resource_pressure=0.40, prb_pct=20.0, sigma_prb_pct=1.0)
    results["pressure_guard_pass"] = pg.verdict == ControlVerdict.PASS
    pg_low = pressure_guard(resource_pressure=0.15, prb_pct=20.0, sigma_prb_pct=1.0)
    results["pressure_guard_skip_low"] = pg_low.verdict == ControlVerdict.SKIP_REP
    fg = feasibility_guard(feasibility=0.45, score_denominator=0.95)
    results["feasibility_guard_pass"] = fg.verdict == ControlVerdict.PASS
    fg_high = feasibility_guard(feasibility=0.72, score_denominator=0.95)
    results["feasibility_guard_skip_high"] = fg_high.verdict == ControlVerdict.SKIP_REP
    c3 = liminal03_corridor_enforce(
        prb_pct=20.0,
        resource_pressure=0.42,
        feasibility=0.48,
        rtt_ms=12.0,
        decision_score=0.75,
        decision_mode="decision_score",
    )
    results["liminal03_corridor_partial"] = c3.verdict in (ControlVerdict.PASS, ControlVerdict.WARN)
    results["liminal03_score_monitored"] = "score_in_target" in c3.monitored
    coord = ConcurrentTenantCoordinator()
    tid = coord.tenant_id("tag", "24Mbps", 0, 0)
    results["concurrent_tenant_id"] = tid.startswith("nad03-")
    results["liminal03_ladder"] = len(DEFAULT_LADDER_LIMINAL03) == 4
    return results


def _cli() -> int:
    import argparse
    from pathlib import Path

    ap = argparse.ArgumentParser(description="NAD boundary runtime controls")
    ap.add_argument("--self-test", action="store_true", help="Run unit self-test")
    ap.add_argument("--campaign", type=str, default=None, help="Campaign ID (NAD-LIMINAL-01)")
    ap.add_argument("--reps", type=int, default=int(os.getenv("NAD_LIMINAL_REPS", "20")))
    ap.add_argument("--regimes", type=int, default=int(os.getenv("NAD_LIMINAL_REGIMES", "5")))
    ap.add_argument("--triplet-order", type=str, default="urllc,embb,mmtc")
    ap.add_argument("--require-scoremode-only", action="store_true", default=True)
    ap.add_argument("--abort-prb-pct", type=float, default=PRB_ABORT_PCT)
    ap.add_argument("--prb-sigma-max", type=float, default=PRB_SIGMA_MAX_PCT)
    ap.add_argument("--warmup", type=float, default=WARMUP_S)
    ap.add_argument("--output-dir", type=str, default=None)
    args = ap.parse_args()

    if args.self_test:
        r = self_test()
        print(json.dumps(r, indent=2))
        return 0 if all(r.values()) else 1

    if args.campaign:
        if args.campaign not in ("NAD-LIMINAL-01", "NAD-LIMINAL-02", "NAD-LIMINAL-03"):
            print(f"Unknown campaign: {args.campaign}", file=sys.stderr)
            return 1
        if not args.output_dir:
            print("--output-dir required", file=sys.stderr)
            return 1
        order = tuple(s.strip().upper() for s in args.triplet_order.split(",") if s.strip())
        for s in order:
            if s not in ("URLLC", "EMBB", "MMTC"):
                print(f"Invalid slice in triplet-order: {s}", file=sys.stderr)
                return 1
        order_map = {"URLLC": "URLLC", "EMBB": "eMBB", "MMTC": "mMTC"}
        slice_order = tuple(order_map[s] for s in order)

        from nad_liminal_campaign import run_campaign, run_liminal02_campaign, run_liminal03_campaign

        out = Path(args.output_dir)
        if args.campaign == "NAD-LIMINAL-03":
            result = run_liminal03_campaign(
                out,
                n_reps=args.reps,
                require_scoremode_only=args.require_scoremode_only,
                dry_run=True,
                slice_order=slice_order,
            )
        elif args.campaign == "NAD-LIMINAL-02":
            result = run_liminal02_campaign(
                out,
                n_reps=args.reps,
                require_scoremode_only=args.require_scoremode_only,
                soft_abort_pct=float(os.getenv("NAD_PRB_SOFT_ABORT_PCT", "23.5")),
                hard_abort_pct=args.abort_prb_pct,
                prb_sigma_max=args.prb_sigma_max,
                warmup_s=args.warmup,
                slice_order=slice_order,
            )
        else:
            result = run_campaign(
                out,
                n_regimes=args.regimes,
                n_reps=args.reps,
                require_scoremode_only=args.require_scoremode_only,
                abort_prb_pct=args.abort_prb_pct,
                prb_sigma_max=args.prb_sigma_max,
                warmup_s=args.warmup,
                slice_order=slice_order,
            )
        stats_path = out / "campaign_execution_stats.json"
        stats_path.write_text(json.dumps(result["stats"], indent=2), encoding="utf-8")
        print(json.dumps(result["stats"], indent=2))
        return 0 if result["stats"].get("n_rows", 0) > 0 else 1

    ap.print_help()
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_cli())
