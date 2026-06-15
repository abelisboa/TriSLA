"""Shadow logger configuration (Phase 33)."""

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
class ShadowLoggerConfig:
    """Foundation logger settings — disabled by default."""

    logger_enabled: bool
    log_sink: str
    log_path: str
    run_id: str
    environment: str
    otlp_enabled: bool
    golden_vectors_path: str
    golden_manifest_path: str
    registry_path: str

    @classmethod
    def from_env(cls) -> "ShadowLoggerConfig":
        root = _repo_root()
        default_log = os.getenv("SHADOW_LOG_PATH", "/var/log/trisla/shadow")
        run_id = os.getenv("SHADOW_RUN_ID") or f"shadow-foundation-{uuid.uuid4().hex[:12]}"
        sink = os.getenv("SHADOW_LOG_SINK", "file").strip().lower()
        otlp = _env_bool("SHADOW_LOG_OTLP_ENABLED", False)

        return cls(
            logger_enabled=_env_bool("SHADOW_LOGGER_ENABLED", False),
            log_sink=sink,
            log_path=default_log,
            run_id=run_id,
            environment=os.getenv("SHADOW_ENVIRONMENT", "offline"),
            otlp_enabled=otlp and sink == "otlp",
            golden_vectors_path=str(
                root / "model-registry" / "shadow-validation" / "golden_vectors_v1.json"
            ),
            golden_manifest_path=str(
                root / "model-registry" / "shadow-validation" / "golden_vectors_manifest_v1.json"
            ),
            registry_path=str(
                root / "model-registry" / "shadow-validation" / "SHADOW_VALIDATION_REGISTRY.json"
            ),
        )
