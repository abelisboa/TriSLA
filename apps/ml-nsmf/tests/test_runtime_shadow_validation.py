"""Phase 40 — runtime shadow validation tests."""

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
from offline_replay_config import OfflineReplayConfig  # noqa: E402
from runtime_shadow_decision import simulate_de_action, threshold_decision  # noqa: E402
from runtime_shadow_executor import execute_runtime_shadow  # noqa: E402

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
        shadow_validation_enabled=True,
    )


def _exec_config(max_vectors: int = 3) -> OfflineReplayConfig:
    return OfflineReplayConfig(
        replay_enabled=True,
        run_id="test-phase40-shadow",
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


class TestRuntimeShadowDecision:
    def test_threshold_decision(self):
        assert threshold_decision(0.1, "URLLC") == "ACCEPT"
        assert threshold_decision(0.9, "URLLC") == "REJECT"

    def test_active_authority_threshold_only(self):
        pred = {"risk_score": 0.4, "slice_adjusted_risk_score": 0.4, "classifier_loaded": False}
        out = simulate_de_action(pred, slice_type="URLLC", authority="active_production")
        assert out["decision_mode"] == "threshold"
        assert out["action"] == "ACCEPT"


class TestRuntimeShadowExecution:
    @pytest.fixture(scope="module")
    def shadow_result(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        return execute_runtime_shadow(_exec_config(max_vectors=3), _dual_config())

    def test_runtime_shadow_executed(self, shadow_result):
        m = shadow_result["execution_manifest"]
        assert m["runtime_shadow"] is True
        assert m["vector_count_executed"] == 3

    def test_active_authority_preserved(self, shadow_result):
        for row in shadow_result["vector_results"]:
            assert row["production_authority_preserved"] is True
            assert row["active"]["prediction"]["classifier_loaded"] is False
            assert row["production_response_hash"]["classifier_loaded"] is False

    def test_pm4_measured(self, shadow_result):
        assert "action_flip_rate" in shadow_result["summary"]["pm4"]
        assert shadow_result["summary"]["production_flip_count"] == 0

    def test_pm5_explainability(self, shadow_result):
        pm5 = shadow_result["summary"]["pm5"]
        assert pm5["dominant_domain_match_rate"] == 1.0

    def test_predict_response_no_shadow_leak(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        svc = DualLoadService(_dual_config())
        try:
            r = svc.predict(deepcopy({"slice_type": "URLLC", "latency": 1.0, "throughput": 100.0}))
            assert "shadow" not in r
            assert r["prediction"]["classifier_loaded"] is False
        finally:
            svc.close()
