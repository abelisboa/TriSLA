"""Dual-load configuration (Phase 32 — Wave 4C)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _repo_root() -> Path:
    # apps/ml-nsmf/src/dual_load_config.py -> repo root
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class DualLoadConfig:
    """Environment-driven dual-load settings."""

    dual_load_enabled: bool
    active_model_path: str
    active_scaler_path: str
    candidate_bundle_id: str
    candidate_root: str
    golden_vectors_path: Optional[str]
    shadow_validation_enabled: bool

    @classmethod
    def from_env(cls) -> "DualLoadConfig":
        root = _repo_root()
        models_dir = root / "apps" / "ml-nsmf" / "models"
        default_candidate_root = str(models_dir / "candidate")
        default_golden = str(root / "model-registry" / "shadow-validation" / "golden_vectors_v1.json")

        return cls(
            dual_load_enabled=_env_bool("ML_DUAL_LOAD_ENABLED", False),
            active_model_path=os.getenv("ML_ACTIVE_MODEL_PATH", "/app/models/viability_model.pkl"),
            active_scaler_path=os.getenv("ML_ACTIVE_SCALER_PATH", "/app/models/scaler.pkl"),
            candidate_bundle_id=os.getenv("SHADOW_CANDIDATE_BUNDLE_ID", "BUNDLE-SCI-001"),
            candidate_root=os.getenv("SHADOW_CANDIDATE_ROOT", default_candidate_root),
            golden_vectors_path=os.getenv("ML_GOLDEN_VECTORS_PATH", default_golden),
            shadow_validation_enabled=_env_bool("SHADOW_VALIDATION_ENABLED", False),
        )

    def dev_paths_if_missing(self) -> "DualLoadConfig":
        """Map container defaults to repo model paths for local/tests."""
        root = _repo_root()
        models = root / "apps" / "ml-nsmf" / "models"
        active_model = self.active_model_path
        active_scaler = self.active_scaler_path
        if not Path(active_model).is_file() and (models / "viability_model.pkl").is_file():
            active_model = str(models / "viability_model.pkl")
        if not Path(active_scaler).is_file() and (models / "scaler.pkl").is_file():
            active_scaler = str(models / "scaler.pkl")
        candidate_root = self.candidate_root
        if not Path(candidate_root).is_dir():
            candidate_root = str(models / "candidate")
        golden = self.golden_vectors_path
        if golden and not Path(golden).is_file():
            alt = root / "model-registry" / "shadow-validation" / "golden_vectors_v1.json"
            if alt.is_file():
                golden = str(alt)
        return DualLoadConfig(
            dual_load_enabled=self.dual_load_enabled,
            active_model_path=active_model,
            active_scaler_path=active_scaler,
            candidate_bundle_id=self.candidate_bundle_id,
            candidate_root=candidate_root,
            golden_vectors_path=golden,
            shadow_validation_enabled=self.shadow_validation_enabled,
        )
