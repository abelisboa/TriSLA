"""Dual-load service — ACTIVE authority + CANDIDATE load/validate only (Phase 32)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from dual_load_config import DualLoadConfig
from model_loader import (
    BundleSpec,
    BundleValidationResult,
    load_golden_vectors,
    resolve_active_bundle,
    resolve_candidate_bundle,
    validate_bundle,
)
from prediction_pipeline import build_active_prediction, format_predict_response
from predictor import RiskPredictor
from offline_replay_engine import OfflineReplayEngine
from shadow_logger import ShadowLogger

logger = logging.getLogger(__name__)

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
    """
    Manages ACTIVE (decision authority) and CANDIDATE (load/validate only) predictors.
    CANDIDATE never participates in predict() response (Phase 32).
    """

    def __init__(self, config: Optional[DualLoadConfig] = None):
        self.config = (config or DualLoadConfig.from_env()).dev_paths_if_missing()
        self.active_spec = resolve_active_bundle(self.config)
        self.candidate_spec: Optional[BundleSpec] = None
        self.active_validation = validate_bundle(self.active_spec)
        if not self.active_validation.valid:
            raise RuntimeError(
                f"ACTIVE bundle invalid: {self.active_validation.errors}"
            )

        if self.config.dual_load_enabled:
            self._active = RiskPredictor(
                model_path=self.active_spec.model_path,
                scaler_path=self.active_spec.scaler_path,
                pin_paths=True,
                role="active",
                load_classifier=False,
            )
        else:
            cfg = self.config.dev_paths_if_missing()
            active = resolve_active_bundle(cfg)
            if Path(active.model_path).is_file() and Path(active.scaler_path).is_file():
                self._active = RiskPredictor(
                    model_path=active.model_path,
                    scaler_path=active.scaler_path,
                    pin_paths=True,
                    role="default",
                )
            else:
                self._active = RiskPredictor()

        self._candidate: Optional[RiskPredictor] = None
        self.candidate_validation: Optional[BundleValidationResult] = None
        self._candidate_lifecycle_state = "NOT_LOADED"

        if self.config.dual_load_enabled:
            self._initialize_candidate()

        self.shadow_logger = ShadowLogger()
        self.shadow_logger.initialize()

        self.offline_replay = OfflineReplayEngine(dual_load_config=self.config)
        self.offline_replay.initialize()

    def close(self) -> None:
        self.shadow_logger.close()
        self.offline_replay.close()

    def _initialize_candidate(self) -> None:
        self.candidate_spec = resolve_candidate_bundle(self.config)
        self.candidate_validation = validate_bundle(self.candidate_spec)
        if not self.candidate_validation.valid:
            logger.warning(
                "[DUAL_LOAD] CANDIDATE bundle validation failed: %s",
                self.candidate_validation.errors,
            )
            self._candidate_lifecycle_state = "VALIDATION_FAILED"
            return

        try:
            self._candidate = RiskPredictor(
                model_path=self.candidate_spec.model_path,
                scaler_path=self.candidate_spec.scaler_path,
                pin_paths=True,
                role="candidate",
                load_classifier=True,
                classifier_path=self.candidate_spec.classifier_path,
            )
            self._candidate_lifecycle_state = "LOADED"
            logger.info(
                "[DUAL_LOAD] CANDIDATE bundle %s loaded (not wired to decision)",
                self.candidate_spec.bundle_id,
            )
        except Exception as exc:
            logger.exception("[DUAL_LOAD] CANDIDATE load failed: %s", exc)
            self._candidate = None
            self._candidate_lifecycle_state = "LOAD_FAILED"

    @property
    def active_predictor(self) -> RiskPredictor:
        return self._active

    @property
    def candidate_predictor(self) -> Optional[RiskPredictor]:
        return self._candidate

    def predict(self, metrics: dict) -> Dict[str, Any]:
        """Production predict — ACTIVE model only; response schema unchanged."""
        prediction, explanation, _ = build_active_prediction(self._active, metrics)
        response = format_predict_response(prediction, explanation)
        self._assert_no_candidate_leak(response)
        return response

    @staticmethod
    def _assert_no_candidate_leak(response: Dict[str, Any]) -> None:
        for key in FORBIDDEN_RESPONSE_KEYS:
            if key in response:
                raise RuntimeError(f"Forbidden candidate/shadow key in response: {key}")
        pred = response.get("prediction") or {}
        for key in FORBIDDEN_RESPONSE_KEYS:
            if key in pred:
                raise RuntimeError(f"Forbidden candidate/shadow key in prediction: {key}")

    def validate_candidate_with_golden_sample(self, max_vectors: int = 3) -> Dict[str, Any]:
        """Lifecycle hook: verify candidate can normalize sample golden vectors (no DE impact)."""
        if not self._candidate:
            return {"validated": False, "reason": self._candidate_lifecycle_state}

        try:
            golden = load_golden_vectors(self.config.golden_vectors_path)
        except OSError as exc:
            return {"validated": False, "reason": str(exc)}

        vectors = golden.get("vectors") or []
        tested = 0
        errors: List[str] = []
        for vec in vectors[:max_vectors]:
            metrics = vec.get("metrics") or {}
            try:
                self._candidate.normalize(metrics)
                tested += 1
            except Exception as exc:
                errors.append(f"{vec.get('vector_id')}: {exc}")

        return {
            "validated": tested > 0 and not errors,
            "vectors_tested": tested,
            "errors": errors,
            "golden_set_version": golden.get("artifact_id"),
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "dual_load_enabled": self.config.dual_load_enabled,
            "shadow_validation_enabled": self.config.shadow_validation_enabled,
            "shadow_execution": False,
            "active": {
                "bundle_id": self.active_spec.bundle_id,
                "role": "ACTIVE_RUNTIME",
                "model_path": self.active_spec.model_path,
                "scaler_path": self.active_spec.scaler_path,
                "valid": self.active_validation.valid,
                "authority": True,
            },
            "candidate": {
                "bundle_id": self.candidate_spec.bundle_id if self.candidate_spec else None,
                "role": "CANDIDATE",
                "lifecycle_state": self._candidate_lifecycle_state,
                "loaded": self._candidate is not None,
                "participates_in_decision": False,
                "valid": (
                    self.candidate_validation.valid
                    if self.candidate_validation
                    else False
                ),
            },
            "shadow_logger": self.shadow_logger.get_status(),
            "offline_replay": self.offline_replay.get_status(),
        }
