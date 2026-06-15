"""Replay manifest validation (Phase 34)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReplayManifestError(ValueError):
    """Raised when a replay manifest fails validation."""


REQUIRED_MANIFEST_FIELDS = frozenset(
    {
        "artifact_id",
        "version",
        "file",
        "checksum_sha256",
        "vector_count",
    }
)

FORBIDDEN_MANIFEST_FIELDS = frozenset(
    {
        "risk_score",
        "confidence",
        "candidate_prediction",
        "parity",
        "inference_results",
    }
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(manifest_path: str) -> Dict[str, Any]:
    path = Path(manifest_path)
    if not path.is_file():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_golden_manifest(
    manifest: Dict[str, Any],
    *,
    golden_vectors_path: Optional[str] = None,
    validate_checksum: bool = True,
) -> Dict[str, Any]:
    """Validate golden_vectors_manifest_v1 structure and optional file checksum."""
    errors: List[str] = []

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"missing manifest field: {field}")

    for field in FORBIDDEN_MANIFEST_FIELDS:
        if field in manifest:
            errors.append(f"forbidden manifest field: {field}")

    artifact_id = manifest.get("artifact_id")
    if artifact_id != "golden_vectors_v1":
        errors.append(f"unexpected artifact_id: {artifact_id}")

    vector_count = manifest.get("vector_count")
    if not isinstance(vector_count, int) or vector_count < 50:
        errors.append(f"vector_count invalid: {vector_count}")

    checksum_match: Optional[bool] = None
    if validate_checksum and golden_vectors_path:
        gv_path = Path(golden_vectors_path)
        if not gv_path.is_file():
            errors.append(f"golden vectors file missing: {golden_vectors_path}")
        else:
            expected = manifest.get("checksum_sha256")
            actual = sha256_file(gv_path)
            checksum_match = actual == expected
            if not checksum_match:
                errors.append(
                    f"checksum mismatch: expected {expected}, got {actual}"
                )

    if errors:
        raise ReplayManifestError("; ".join(errors))

    return {
        "valid": True,
        "artifact_id": artifact_id,
        "vector_count": vector_count,
        "checksum_sha256": manifest.get("checksum_sha256"),
        "checksum_verified": checksum_match,
        "slice_distribution": manifest.get("slice_distribution"),
    }


def build_prepared_replay_manifest(
    *,
    run_id: str,
    golden_manifest: Dict[str, Any],
    registry_hook: Dict[str, Any],
    vector_ids: List[str],
    active_bundle_id: str,
    candidate_bundle_id: Optional[str],
) -> Dict[str, Any]:
    """Build a foundation replay manifest — preparation only, no inference."""
    manifest = {
        "record_type": "offline_replay_prepared_manifest",
        "schema_version": "1.0.0",
        "run_id": run_id,
        "phase": "34",
        "status": "PREPARED",
        "inference_execution": False,
        "replay_execution": False,
        "golden_artifact_id": golden_manifest.get("artifact_id"),
        "golden_checksum_sha256": golden_manifest.get("checksum_sha256"),
        "vector_count_planned": len(vector_ids),
        "vector_ids": vector_ids,
        "active_bundle_id": active_bundle_id,
        "candidate_bundle_id": candidate_bundle_id,
        "registry_id": registry_hook.get("registry_id"),
        "replay_corpus_sha256": registry_hook.get("replay_corpus_sha256"),
    }
    for field in FORBIDDEN_MANIFEST_FIELDS:
        if field in manifest:
            raise ReplayManifestError(f"forbidden field in prepared manifest: {field}")
    return manifest
