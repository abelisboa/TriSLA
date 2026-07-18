"""Active-model service preserving the public ML prediction contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from dual_load_config import DualLoadConfig
from model_loader import resolve_active_bundle, validate_bundle
from prediction_pipeline import build_active_prediction, format_predict_response
from predictor import RiskPredictor

FORBIDDEN_RESPONSE_KEYS = frozenset(
    {
        "shadow",
        "candidate_prediction",
        "candidate_output",
        "shadow_compare",
        "dual_load_compare",
    }
)


class DualLoadService:
    """Serve predictions from the single approved active model bundle."""

    def __init__(self, config: Optional[DualLoadConfig] = None):
        self.config = (config or DualLoadConfig.from_env()).dev_paths_if_missing()
        self.active_spec = resolve_active_bundle(self.config)
        self.active_validation = validate_bundle(self.active_spec)
        if not self.active_validation.valid:
            raise RuntimeError(
                f"ACTIVE bundle invalid: {self.active_validation.errors}"
            )

        if Path(self.active_spec.model_path).is_file() and Path(
            self.active_spec.scaler_path
        ).is_file():
            self._active = RiskPredictor(
                model_path=self.active_spec.model_path,
                scaler_path=self.active_spec.scaler_path,
                pin_paths=True,
                role="active",
                load_classifier=False,
            )
        else:
            self._active = RiskPredictor()

    def close(self) -> None:
        """No external experimental resources are opened by the public service."""

    @property
    def active_predictor(self) -> RiskPredictor:
        return self._active

    def predict(self, metrics: dict) -> Dict[str, Any]:
        prediction, explanation, _ = build_active_prediction(self._active, metrics)
        response = format_predict_response(prediction, explanation)
        self._assert_public_response(response)
        return response

    @staticmethod
    def _assert_public_response(response: Dict[str, Any]) -> None:
        prediction = response.get("prediction") or {}
        for key in FORBIDDEN_RESPONSE_KEYS:
            if key in response or key in prediction:
                raise RuntimeError(f"Forbidden experimental response key: {key}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": "active-only",
            "active": {
                "bundle_id": self.active_spec.bundle_id,
                "role": "ACTIVE_RUNTIME",
                "model_path": self.active_spec.model_path,
                "scaler_path": self.active_spec.scaler_path,
                "valid": self.active_validation.valid,
                "authority": True,
            },
        }
