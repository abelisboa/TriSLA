"""Registry hooks for shadow logger foundation (Phase 33)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_shadow_validation_registry(registry_path: str) -> Dict[str, Any]:
    path = Path(registry_path)
    if not path.is_file():
        raise FileNotFoundError(f"registry not found: {registry_path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def golden_vector_reference_from_registry(registry: Dict[str, Any]) -> Dict[str, Any]:
    golden = registry.get("golden_set") or {}
    return {
        "artifact_id": "golden_vectors_v1",
        "checksum_sha256": golden.get("checksum_sha256"),
        "vector_count": golden.get("vector_count"),
        "status": golden.get("status"),
        "manifest": golden.get("manifest"),
    }


def golden_vector_reference_for_vector(
    registry: Dict[str, Any],
    vector_id: str,
) -> Dict[str, Any]:
    ref = golden_vector_reference_from_registry(registry)
    ref["vector_id"] = vector_id
    return ref


def build_logger_registry_hook(
    registry_path: str,
    *,
    phase: str = "33",
    logger_enabled: bool = False,
    sink: str = "file",
) -> Dict[str, Any]:
    """Read-only registry integration metadata for shadow logger foundation."""
    registry = load_shadow_validation_registry(registry_path)
    return {
        "hook_type": "shadow_logger_foundation",
        "registry_id": registry.get("registry_id"),
        "execution_status": registry.get("execution_status"),
        "shadow_execution": False,
        "golden_set": golden_vector_reference_from_registry(registry),
        "active_runtime_bundle": (registry.get("active_runtime") or {}).get("bundle_id"),
        "replay_corpus_sha256": (registry.get("replay_corpus") or {}).get("dataset_sha256"),
        "phase": phase,
        "logger_enabled": logger_enabled,
        "sink": sink,
        "shadow_runs_count": len(registry.get("shadow_runs") or []),
    }


def load_golden_vector_by_id(
    golden_vectors_path: str,
    vector_id: str,
) -> Optional[Dict[str, Any]]:
    path = Path(golden_vectors_path)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        doc = json.load(f)
    for vec in doc.get("vectors") or []:
        if vec.get("vector_id") == vector_id:
            return vec
    return None
