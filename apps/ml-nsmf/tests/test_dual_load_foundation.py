"""Active-model loading and prediction contract tests."""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import pytest

ML_SRC = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ML_SRC))

from dual_load_config import DualLoadConfig  # noqa: E402
from dual_load_service import DualLoadService  # noqa: E402
from model_loader import resolve_active_bundle, validate_bundle  # noqa: E402
from prediction_pipeline import build_active_prediction, format_predict_response  # noqa: E402
from predictor import RiskPredictor  # noqa: E402

MODELS_DIR = REPO_ROOT / "apps" / "ml-nsmf" / "models"

SAMPLE_METRICS = {
    "intent_id": "test-intent-001",
    "service_type": "URLLC",
    "slice_type": "URLLC",
    "slice_type_encoded": 1,
    "latency": 1.0,
    "throughput": 100.0,
    "reliability": 0.99999,
    "jitter": 0.1,
    "packet_loss": 0.00001,
    "cpu_utilization": 0.1,
    "memory_utilization": 0.1,
    "network_bandwidth_available": 1000.0,
    "active_slices_count": 1,
}


def _active_config() -> DualLoadConfig:
    return DualLoadConfig(
        active_model_path=str(MODELS_DIR / "viability_model.pkl"),
        active_scaler_path=str(MODELS_DIR / "scaler.pkl"),
    )


@pytest.fixture(scope="module")
def active_service():
    if not (MODELS_DIR / "viability_model.pkl").is_file():
        pytest.skip("model artifacts missing")
    return DualLoadService(_active_config())


class TestModelLoading:
    def test_active_model_loads(self, active_service):
        assert active_service.active_predictor.model is not None
        assert active_service.active_predictor.scaler is not None

    def test_active_bundle_validation(self):
        result = validate_bundle(resolve_active_bundle(_active_config()))
        assert result.valid, result.errors

    def test_active_skips_classifier(self, active_service):
        assert active_service.active_predictor.classifier_bundle is None


class TestPublicPredictionContract:
    def test_predict_response_schema(self, active_service):
        response = active_service.predict(deepcopy(SAMPLE_METRICS))
        assert "latency_ms" in response
        assert "prediction" in response
        assert "explanation" in response
        for forbidden in ("shadow", "candidate_prediction", "candidate_output"):
            assert forbidden not in response
            assert forbidden not in (response.get("prediction") or {})

    def test_active_service_matches_pinned_predictor(self, active_service):
        config = _active_config()
        active_only = RiskPredictor(
            model_path=config.active_model_path,
            scaler_path=config.active_scaler_path,
            pin_paths=True,
            role="active",
            load_classifier=False,
        )
        service_response = active_service.predict(deepcopy(SAMPLE_METRICS))
        prediction, explanation, _ = build_active_prediction(
            active_only, deepcopy(SAMPLE_METRICS)
        )
        direct_response = format_predict_response(prediction, explanation)
        assert service_response["prediction"]["risk_score"] == pytest.approx(
            direct_response["prediction"]["risk_score"], rel=1e-6
        )
        assert service_response["prediction"]["confidence"] == pytest.approx(
            direct_response["prediction"]["confidence"], rel=1e-6
        )

    def test_predict_is_stable(self, active_service):
        first = active_service.predict(deepcopy(SAMPLE_METRICS))
        second = active_service.predict(deepcopy(SAMPLE_METRICS))
        assert first["prediction"]["risk_score"] == second["prediction"]["risk_score"]
        assert first["prediction"]["confidence"] == pytest.approx(
            second["prediction"]["confidence"], rel=1e-9
        )

    def test_status_has_single_authority(self, active_service):
        status = active_service.get_status()
        assert status["mode"] == "active-only"
        assert status["active"]["authority"] is True
        assert "candidate" not in status
        assert "offline_replay" not in status
        assert "shadow_logger" not in status
