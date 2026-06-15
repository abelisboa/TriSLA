"""Registry hooks for offline replay foundation (Phase 34)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_shadow_validation_registry(registry_path: str) -> Dict[str, Any]:
    path = Path(registry_path)
    if not path.is_file():
        raise FileNotFoundError(f"registry not found: {registry_path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_replay_registry_hook(
    registry_path: str,
    *,
    phase: str = "34",
    replay_enabled: bool = False,
) -> Dict[str, Any]:
    """Read-only registry integration metadata for offline replay foundation."""
    registry = load_shadow_validation_registry(registry_path)
    golden = registry.get("golden_set") or {}
    replay_corpus = registry.get("replay_corpus") or {}
    active = registry.get("active_runtime") or {}
    candidates = registry.get("candidate_queue") or []

    primary_candidate = candidates[0] if candidates else {}

    return {
        "hook_type": "offline_replay_foundation",
        "registry_id": registry.get("registry_id"),
        "execution_status": registry.get("execution_status"),
        "replay_execution": False,
        "inference_execution": False,
        "golden_set": {
            "artifact_id": "golden_vectors_v1",
            "status": golden.get("status"),
            "checksum_sha256": golden.get("checksum_sha256"),
            "vector_count": golden.get("vector_count"),
            "manifest": golden.get("manifest"),
        },
        "replay_corpus": {
            "freeze_ref": replay_corpus.get("freeze_ref"),
            "dataset_sha256": replay_corpus.get("dataset_sha256"),
            "pack": replay_corpus.get("pack"),
        },
        "active_runtime_bundle": active.get("bundle_id"),
        "primary_candidate_bundle": primary_candidate.get("bundle_id"),
        "phase": phase,
        "replay_enabled": replay_enabled,
        "shadow_runs_count": len(registry.get("shadow_runs") or []),
    }
