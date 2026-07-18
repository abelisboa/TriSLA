"""Active ML model configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class DualLoadConfig:
    """Environment-driven active-model settings."""

    active_model_path: str
    active_scaler_path: str

    @classmethod
    def from_env(cls) -> "DualLoadConfig":
        return cls(
            active_model_path=os.getenv(
                "ML_ACTIVE_MODEL_PATH", "/app/models/viability_model.pkl"
            ),
            active_scaler_path=os.getenv(
                "ML_ACTIVE_SCALER_PATH", "/app/models/scaler.pkl"
            ),
        )

    def dev_paths_if_missing(self) -> "DualLoadConfig":
        """Map container defaults to repository model paths for local validation."""
        models = _repo_root() / "apps" / "ml-nsmf" / "models"
        active_model = self.active_model_path
        active_scaler = self.active_scaler_path
        if not Path(active_model).is_file() and (models / "viability_model.pkl").is_file():
            active_model = str(models / "viability_model.pkl")
        if not Path(active_scaler).is_file() and (models / "scaler.pkl").is_file():
            active_scaler = str(models / "scaler.pkl")
        return DualLoadConfig(
            active_model_path=active_model,
            active_scaler_path=active_scaler,
        )
