"""REPLAY_TELEMETRY_CONSISTENCY_GATE (Phase 35)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from replay_snapshot import REPLAY_SNAPSHOT_WINDOW, canonical_snapshot_payload, snapshot_checksum


GATE_REQUIRED_FIELDS = (
    "snapshot_id",
    "snapshot_timestamp",
    "snapshot_checksum",
    "snapshot_window",
    "snapshot_source",
)


@dataclass
class TelemetryGateResult:
    passed: bool
    gate_name: str = "REPLAY_TELEMETRY_CONSISTENCY_GATE"
    mismatches: List[str] = field(default_factory=list)
    active_snapshot_ref: Dict[str, Any] = field(default_factory=dict)
    candidate_snapshot_ref: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate": self.gate_name,
            "passed": self.passed,
            "mismatches": self.mismatches,
            "active_snapshot_ref": self.active_snapshot_ref,
            "candidate_snapshot_ref": self.candidate_snapshot_ref,
        }


def _gate_identity(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **canonical_snapshot_payload(snapshot),
        "snapshot_checksum": snapshot.get("snapshot_checksum"),
    }


def validate_replay_snapshot(snapshot: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for key in GATE_REQUIRED_FIELDS:
        if key not in snapshot:
            errors.append(f"missing {key}")
    expected_cs = snapshot_checksum(snapshot)
    if snapshot.get("snapshot_checksum") != expected_cs:
        errors.append("snapshot_checksum mismatch")
    window = snapshot.get("snapshot_window") or {}
    if window.get("policy") != REPLAY_SNAPSHOT_WINDOW["policy"]:
        errors.append("snapshot_window policy not [t-1s,t]")
    if window.get("step") != REPLAY_SNAPSHOT_WINDOW["step"]:
        errors.append("snapshot_window step not 1s")
    return errors


def run_telemetry_consistency_gate(
    active_snapshot: Dict[str, Any],
    candidate_snapshot: Dict[str, Any],
) -> TelemetryGateResult:
    """
    ACTIVE and CANDIDATE must receive exactly the same logical snapshot identity.
    """
    mismatches: List[str] = []

    for label, snap in (("active", active_snapshot), ("candidate", candidate_snapshot)):
        mismatches.extend(f"{label}: {e}" for e in validate_replay_snapshot(snap))

    active_id = _gate_identity(active_snapshot)
    candidate_id = _gate_identity(candidate_snapshot)

    for key in GATE_REQUIRED_FIELDS:
        if active_snapshot.get(key) != candidate_snapshot.get(key):
            mismatches.append(f"field mismatch: {key}")

    if active_id != candidate_id:
        mismatches.append("gate identity mismatch")

    if active_snapshot.get("metrics") is not candidate_snapshot.get("metrics"):
        if active_snapshot.get("metrics") != candidate_snapshot.get("metrics"):
            mismatches.append("metrics object identity/value mismatch")

    return TelemetryGateResult(
        passed=len(mismatches) == 0,
        mismatches=mismatches,
        active_snapshot_ref=active_id,
        candidate_snapshot_ref=candidate_id,
    )
