"""Replay snapshot builder for offline execution (Phase 35)."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional


REPLAY_SNAPSHOT_WINDOW = {
    "policy": "[t-1s,t]",
    "start_offset_seconds": -1,
    "end_offset_seconds": 0,
    "step": "1s",
}

SNAPSHOT_MAX_AGE_SECONDS = 35


def canonical_snapshot_payload(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Fields included in snapshot_checksum (metrics excluded from gate identity)."""
    return {
        "snapshot_id": snapshot.get("snapshot_id"),
        "snapshot_timestamp": snapshot.get("snapshot_timestamp"),
        "snapshot_window": snapshot.get("snapshot_window"),
        "snapshot_source": snapshot.get("snapshot_source"),
        "vector_id": snapshot.get("vector_id"),
        "golden_artifact_id": snapshot.get("golden_artifact_id"),
    }


def snapshot_checksum(snapshot: Dict[str, Any]) -> str:
    payload = canonical_snapshot_payload(snapshot)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_replay_snapshot(
    *,
    vector_id: str,
    metrics: Dict[str, Any],
    run_id: str,
    golden_artifact_id: str = "golden_vectors_v1",
    snapshot_source: str = "RESULTS_FREEZE_MAIN",
    snapshot_timestamp: Optional[str] = None,
    origin: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a logical replay snapshot — same object for ACTIVE and CANDIDATE."""
    ts = snapshot_timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    snapshot: Dict[str, Any] = {
        "snapshot_id": f"{vector_id}@{run_id}",
        "snapshot_timestamp": ts,
        "snapshot_window": dict(REPLAY_SNAPSHOT_WINDOW),
        "snapshot_source": snapshot_source,
        "snapshot_max_age_seconds": SNAPSHOT_MAX_AGE_SECONDS,
        "vector_id": vector_id,
        "golden_artifact_id": golden_artifact_id,
        "metrics": deepcopy(metrics),
        "origin": dict(origin or {}),
    }
    snapshot["snapshot_checksum"] = snapshot_checksum(snapshot)
    return snapshot


def metrics_from_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Shared metrics view — both models MUST use this."""
    return snapshot["metrics"]
