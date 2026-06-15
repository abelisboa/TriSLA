"""Offline replay configuration (Phase 34)."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class OfflineReplayConfig:
    """Foundation offline replay settings — disabled by default."""

    replay_enabled: bool
    run_id: str
    environment: str
    golden_vectors_path: str
    golden_manifest_path: str
    registry_path: str
    validate_checksums: bool
    max_vectors: int
    snapshot_window_policy: str
    execute_offline: bool

    @classmethod
    def from_env(cls) -> "OfflineReplayConfig":
        root = _repo_root()
        shadow_dir = root / "model-registry" / "shadow-validation"
        run_id = os.getenv("OFFLINE_REPLAY_RUN_ID") or f"offline-replay-{uuid.uuid4().hex[:12]}"
        max_raw = os.getenv("OFFLINE_REPLAY_MAX_VECTORS", "0").strip()
        max_vectors = int(max_raw) if max_raw.isdigit() else 0

        return cls(
            replay_enabled=_env_bool("OFFLINE_REPLAY_ENABLED", False),
            run_id=run_id,
            environment=os.getenv("OFFLINE_REPLAY_ENVIRONMENT", "offline"),
            golden_vectors_path=str(shadow_dir / "golden_vectors_v1.json"),
            golden_manifest_path=str(shadow_dir / "golden_vectors_manifest_v1.json"),
            registry_path=str(shadow_dir / "SHADOW_VALIDATION_REGISTRY.json"),
            validate_checksums=_env_bool("OFFLINE_REPLAY_VALIDATE_CHECKSUMS", True),
            max_vectors=max_vectors,
            snapshot_window_policy=os.getenv("OFFLINE_REPLAY_SNAPSHOT_WINDOW", "[t-1s,t]"),
            execute_offline=_env_bool("OFFLINE_REPLAY_EXECUTE", False),
        )
