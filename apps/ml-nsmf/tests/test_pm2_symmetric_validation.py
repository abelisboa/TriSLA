"""Phase 39 — PM-2 symmetric classifier validation tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ML_SRC = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ML_SRC))

from dual_load_config import DualLoadConfig  # noqa: E402
from offline_replay_config import OfflineReplayConfig  # noqa: E402
from pm2_symmetric_executor import (  # noqa: E402
    build_symmetric_predictors,
    execute_pm2_validation,
)

MODELS_DIR = REPO_ROOT / "apps" / "ml-nsmf" / "models"
GOLDEN_PATH = REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_v1.json"
MANIFEST_PATH = REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_manifest_v1.json"


def _dual_config() -> DualLoadConfig:
    return DualLoadConfig(
        dual_load_enabled=True,
        active_model_path=str(MODELS_DIR / "viability_model.pkl"),
        active_scaler_path=str(MODELS_DIR / "scaler.pkl"),
        candidate_bundle_id="BUNDLE-SCI-001",
        candidate_root=str(MODELS_DIR / "candidate"),
        golden_vectors_path=str(GOLDEN_PATH),
        shadow_validation_enabled=False,
    )


def _exec_config(max_vectors: int = 3) -> OfflineReplayConfig:
    return OfflineReplayConfig(
        replay_enabled=True,
        run_id="test-phase39-pm2",
        environment="test",
        golden_vectors_path=str(GOLDEN_PATH),
        golden_manifest_path=str(MANIFEST_PATH),
        registry_path=str(
            REPO_ROOT / "model-registry" / "shadow-validation" / "SHADOW_VALIDATION_REGISTRY.json"
        ),
        validate_checksums=True,
        max_vectors=max_vectors,
        snapshot_window_policy="[t-1s,t]",
        execute_offline=True,
    )


class TestPM2Symmetric:
    @pytest.fixture(scope="module")
    def pm2_result(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors missing")
        return execute_pm2_validation(_exec_config(max_vectors=3), _dual_config())

    def test_symmetric_classifier_built(self):
        active, candidate, clf_path = build_symmetric_predictors(_dual_config())
        assert active.classifier_bundle is not None
        assert candidate.classifier_bundle is not None
        assert Path(clf_path).is_file()

    def test_pm2_executed(self, pm2_result):
        m = pm2_result["execution_manifest"]
        assert m["parity_method"] == "PM-2"
        assert m["symmetric_classifier_loaded"] is True
        assert m["vector_count_executed"] == 3

    def test_pm2_perfect_parity_sample(self, pm2_result):
        summary = pm2_result["parity_summary"]
        assert summary["prediction_parity"]["parity_rate"] == pytest.approx(1.0)
        assert summary["pm2"]["decision_class_agreement_rate"] == pytest.approx(1.0)
        assert summary["pm2"]["symmetric_classifier_loaded"] is True

    def test_pm2_gates_pass_sample(self, pm2_result):
        gates = pm2_result["parity_summary"]["pm2"]["gates"]
        assert all(gates.values())
