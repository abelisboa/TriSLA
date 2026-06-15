"""Phase 32 — dual-load foundation tests."""

from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ML_SRC = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ML_SRC))

from dual_load_config import DualLoadConfig  # noqa: E402
from dual_load_service import DualLoadService  # noqa: E402
from model_loader import (  # noqa: E402
    load_golden_vectors,
    resolve_active_bundle,
    resolve_candidate_bundle,
    validate_bundle,
)
from prediction_pipeline import build_active_prediction, format_predict_response  # noqa: E402
from predictor import RiskPredictor  # noqa: E402


MODELS_DIR = REPO_ROOT / "apps" / "ml-nsmf" / "models"
GOLDEN_PATH = REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_v1.json"

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


def _legacy_config() -> DualLoadConfig:
    return DualLoadConfig(
        dual_load_enabled=False,
        active_model_path=str(MODELS_DIR / "viability_model.pkl"),
        active_scaler_path=str(MODELS_DIR / "scaler.pkl"),
        candidate_bundle_id="BUNDLE-SCI-001",
        candidate_root=str(MODELS_DIR / "candidate"),
        golden_vectors_path=str(GOLDEN_PATH),
        shadow_validation_enabled=False,
    )


def _dual_load_config() -> DualLoadConfig:
    return DualLoadConfig(
        dual_load_enabled=True,
        active_model_path=str(MODELS_DIR / "viability_model.pkl"),
        active_scaler_path=str(MODELS_DIR / "scaler.pkl"),
        candidate_bundle_id="BUNDLE-SCI-001",
        candidate_root=str(MODELS_DIR / "candidate"),
        golden_vectors_path=str(GOLDEN_PATH),
        shadow_validation_enabled=False,
    )


@pytest.fixture(scope="module")
def legacy_service():
    if not (MODELS_DIR / "viability_model.pkl").is_file():
        pytest.skip("model artifacts missing")
    return DualLoadService(_legacy_config())


@pytest.fixture(scope="module")
def dual_service():
    if not (MODELS_DIR / "viability_model.pkl").is_file():
        pytest.skip("model artifacts missing")
    return DualLoadService(_dual_load_config())


class TestModelLoading:
    def test_active_model_loads(self, legacy_service):
        assert legacy_service.active_predictor.model is not None
        assert legacy_service.active_predictor.scaler is not None

    def test_active_bundle_validation(self):
        cfg = _dual_load_config()
        spec = resolve_active_bundle(cfg)
        result = validate_bundle(spec)
        assert result.valid, result.errors

    def test_candidate_model_loads_when_dual_enabled(self, dual_service):
        assert dual_service.config.dual_load_enabled is True
        assert dual_service.candidate_predictor is not None
        assert dual_service.candidate_predictor.classifier_bundle is not None

    def test_active_skips_classifier(self, dual_service):
        assert dual_service.active_predictor.classifier_bundle is None


class TestRegistryLoading:
    def test_resolve_candidate_bundle_from_manifest(self):
        cfg = _dual_load_config()
        spec = resolve_candidate_bundle(cfg)
        assert spec.bundle_id == "BUNDLE-SCI-001"
        assert Path(spec.model_path).is_file()
        assert Path(spec.scaler_path).is_file()
        assert Path(spec.classifier_path).is_file()

    def test_candidate_validation_passes(self):
        cfg = _dual_load_config()
        spec = resolve_candidate_bundle(cfg)
        result = validate_bundle(spec)
        assert result.valid, result.errors


class TestGoldenVectorLoading:
    def test_golden_vectors_file_loads(self):
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors not present")
        data = load_golden_vectors(str(GOLDEN_PATH))
        assert data["vector_count"] == 60
        assert data["slice_distribution"]["URLLC"] == 20

    def test_active_predict_on_golden_vectors(self, legacy_service):
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors not present")
        golden = load_golden_vectors(str(GOLDEN_PATH))
        for vec in golden["vectors"][:5]:
            pred, expl, _ = build_active_prediction(
                legacy_service.active_predictor, vec["metrics"]
            )
            assert "risk_score" in pred
            assert expl.get("method")


class TestBackwardCompatibility:
    def test_legacy_predict_response_schema(self, legacy_service):
        response = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        assert "latency_ms" in response
        assert "prediction" in response
        assert "explanation" in response
        assert "shadow" not in response
        assert "candidate_prediction" not in response

    def test_dual_load_disabled_matches_legacy_paths(self):
        cfg = _legacy_config()
        svc = DualLoadService(cfg)
        assert svc.config.dual_load_enabled is False
        assert svc.candidate_predictor is None


class TestRegression:
    def test_dual_active_matches_pinned_active_predictor(self, dual_service):
        cfg = _dual_load_config()
        active_only = RiskPredictor(
            model_path=cfg.active_model_path,
            scaler_path=cfg.active_scaler_path,
            pin_paths=True,
            role="active",
            load_classifier=False,
        )
        r_dual = dual_service.predict(deepcopy(SAMPLE_METRICS))
        pred, expl, _ = build_active_prediction(active_only, deepcopy(SAMPLE_METRICS))
        r_active = format_predict_response(pred, expl)
        assert r_dual["prediction"]["risk_score"] == pytest.approx(
            r_active["prediction"]["risk_score"], rel=1e-6
        )
        assert r_dual["prediction"]["confidence"] == pytest.approx(
            r_active["prediction"]["confidence"], rel=1e-6
        )

    def test_legacy_predict_stable_across_calls(self, legacy_service):
        r1 = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        r2 = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        assert r1["prediction"]["risk_score"] == r2["prediction"]["risk_score"]
        assert r1["prediction"]["confidence"] == pytest.approx(
            r2["prediction"]["confidence"], rel=1e-9
        )

    def test_candidate_not_in_response(self, dual_service):
        response = dual_service.predict(deepcopy(SAMPLE_METRICS))
        for forbidden in ("shadow", "candidate_prediction", "candidate_output"):
            assert forbidden not in response
            assert forbidden not in (response.get("prediction") or {})

    def test_active_model_authority(self, dual_service):
        status = dual_service.get_status()
        assert status["active"]["authority"] is True
        assert status["candidate"]["participates_in_decision"] is False
        assert status["shadow_execution"] is False

    def test_candidate_golden_validation_hook(self, dual_service):
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors not present")
        result = dual_service.validate_candidate_with_golden_sample(max_vectors=3)
        assert result["validated"] is True
        assert result["vectors_tested"] == 3
