"""Phase 34 — offline replay foundation tests."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ML_SRC = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ML_SRC))

from dual_load_config import DualLoadConfig  # noqa: E402
from dual_load_service import DualLoadService  # noqa: E402
from golden_vector_loader import (  # noqa: E402
    GoldenVectorLoadError,
    load_golden_vector_metrics,
    load_golden_vector_refs,
)
from offline_replay_config import OfflineReplayConfig  # noqa: E402
from offline_replay_engine import OfflineReplayEngine  # noqa: E402
from replay_context import build_replay_context  # noqa: E402
from replay_manifest import (  # noqa: E402
    ReplayManifestError,
    load_manifest,
    validate_golden_manifest,
)
from replay_registry_hooks import (  # noqa: E402
    build_replay_registry_hook,
    load_shadow_validation_registry,
)

MODELS_DIR = REPO_ROOT / "apps" / "ml-nsmf" / "models"
GOLDEN_PATH = REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_v1.json"
MANIFEST_PATH = REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_manifest_v1.json"
REGISTRY_PATH = REPO_ROOT / "model-registry" / "shadow-validation" / "SHADOW_VALIDATION_REGISTRY.json"

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


def _replay_config() -> OfflineReplayConfig:
    return OfflineReplayConfig(
        replay_enabled=False,
        run_id="test-replay-run",
        environment="test",
        golden_vectors_path=str(GOLDEN_PATH),
        golden_manifest_path=str(MANIFEST_PATH),
        registry_path=str(REGISTRY_PATH),
        validate_checksums=True,
        max_vectors=5,
        snapshot_window_policy="[t-1s,t]",
        execute_offline=False,
    )


class TestGoldenVectorLoading:
    def test_load_golden_vector_refs(self):
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors not present")
        result = load_golden_vector_refs(str(GOLDEN_PATH), max_vectors=10)
        assert result.artifact_id == "golden_vectors_v1"
        assert len(result.vectors) == 10
        assert all(v.vector_id.startswith("GV-") for v in result.vectors)

    def test_slice_filter(self):
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors not present")
        result = load_golden_vector_refs(
            str(GOLDEN_PATH), max_vectors=25, slice_filter="URLLC"
        )
        assert all(v.slice_type == "URLLC" for v in result.vectors)

    def test_load_golden_vector_metrics(self):
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors not present")
        metrics = load_golden_vector_metrics(str(GOLDEN_PATH), "GV-URLLC-001")
        assert metrics is not None
        assert "intent_id" in metrics
        assert "risk_score" not in metrics

    def test_rejects_empty_vectors_file(self, tmp_path):
        bad = tmp_path / "empty.json"
        bad.write_text(json.dumps({"artifact_id": "x", "vectors": []}), encoding="utf-8")
        with pytest.raises(GoldenVectorLoadError):
            load_golden_vector_refs(str(bad))


class TestManifestValidation:
    def test_validate_golden_manifest(self):
        if not MANIFEST_PATH.is_file() or not GOLDEN_PATH.is_file():
            pytest.skip("manifest/golden not present")
        manifest = load_manifest(str(MANIFEST_PATH))
        result = validate_golden_manifest(
            manifest,
            golden_vectors_path=str(GOLDEN_PATH),
            validate_checksum=True,
        )
        assert result["valid"] is True
        assert result["checksum_verified"] is True
        assert result["vector_count"] == 60

    def test_rejects_bad_checksum(self):
        if not MANIFEST_PATH.is_file() or not GOLDEN_PATH.is_file():
            pytest.skip("manifest/golden not present")
        manifest = load_manifest(str(MANIFEST_PATH))
        bad = dict(manifest)
        bad["checksum_sha256"] = "0" * 64
        with pytest.raises(ReplayManifestError):
            validate_golden_manifest(
                bad,
                golden_vectors_path=str(GOLDEN_PATH),
                validate_checksum=True,
            )

    def test_rejects_forbidden_fields(self):
        with pytest.raises(ReplayManifestError):
            validate_golden_manifest(
                {
                    "artifact_id": "golden_vectors_v1",
                    "version": "1.0.0",
                    "file": "x.json",
                    "checksum_sha256": "a" * 64,
                    "vector_count": 60,
                    "risk_score": 0.5,
                },
                validate_checksum=False,
            )


class TestRegistryIntegration:
    def test_load_registry(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        registry = load_shadow_validation_registry(str(REGISTRY_PATH))
        assert registry["registry_id"] == "shadow_validation_registry"

    def test_build_replay_registry_hook(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        hook = build_replay_registry_hook(str(REGISTRY_PATH), phase="34")
        assert hook["hook_type"] == "offline_replay_foundation"
        assert hook["replay_execution"] is False
        assert hook["inference_execution"] is False
        assert hook["golden_set"]["artifact_id"] == "golden_vectors_v1"

    def test_registry_offline_replay_flags(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        registry = load_shadow_validation_registry(str(REGISTRY_PATH))
        flags = registry.get("flags") or {}
        assert flags.get("OFFLINE_REPLAY_ENGINE_IMPLEMENTED") is True
        assert flags.get("OFFLINE_REPLAY_READY") is True
        offline = registry.get("offline_replay") or {}
        assert offline.get("execution_wired") is False
        assert offline.get("inference_wired") is False


class TestReplayContextGeneration:
    def test_engine_prepare_context(self):
        if not GOLDEN_PATH.is_file() or not MANIFEST_PATH.is_file():
            pytest.skip("artifacts not present")
        engine = OfflineReplayEngine(
            config=_replay_config(),
            dual_load_config=_legacy_config(),
        )
        ctx = engine.prepare_context()
        assert ctx.inference_execution is False
        assert ctx.replay_execution is False
        assert ctx.vector_count_planned == 5
        assert ctx.active_bundle.valid is True
        assert ctx.candidate_bundle is not None
        assert ctx.candidate_bundle.valid is True
        data = ctx.to_dict()
        assert "risk_score" not in json.dumps(data)
        manifest = engine.get_prepared_manifest()
        assert manifest is not None
        assert manifest["inference_execution"] is False
        assert manifest["replay_execution"] is False

    def test_prepared_manifest_has_no_inference_fields(self):
        if not GOLDEN_PATH.is_file() or not MANIFEST_PATH.is_file():
            pytest.skip("artifacts not present")
        engine = OfflineReplayEngine(
            config=_replay_config(),
            dual_load_config=_legacy_config(),
        )
        engine.prepare_context()
        manifest = engine.get_prepared_manifest()
        assert manifest is not None
        for forbidden in ("risk_score", "confidence", "parity", "inference_results"):
            assert forbidden not in manifest


class TestBackwardCompatibility:
    @pytest.fixture(scope="module")
    def legacy_service(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        return DualLoadService(_legacy_config())

    def test_predict_response_unchanged(self, legacy_service):
        response = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        assert "prediction" in response
        assert "shadow" not in response
        assert "offline_replay" not in response

    def test_health_includes_offline_replay_status(self, legacy_service):
        status = legacy_service.get_status()
        assert "offline_replay" in status
        replay = status["offline_replay"]
        assert replay["inference_execution"] is False
        assert replay["replay_execution"] is False
        assert replay["replay_enabled"] is False

    def test_predict_does_not_prepare_replay(self, legacy_service):
        before = legacy_service.offline_replay.get_status()["context_prepared"]
        legacy_service.predict(deepcopy(SAMPLE_METRICS))
        after = legacy_service.offline_replay.get_status()["context_prepared"]
        assert before == after


class TestRegression:
    @pytest.fixture(scope="module")
    def legacy_service(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        return DualLoadService(_legacy_config())

    def test_offline_replay_disabled_by_default(self):
        cfg = OfflineReplayConfig.from_env()
        assert cfg.replay_enabled is False

    def test_dual_load_status_unchanged(self, legacy_service):
        status = legacy_service.get_status()
        assert status["shadow_execution"] is False
        assert status["active"]["authority"] is True

    def test_predict_scores_stable(self, legacy_service):
        r1 = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        r2 = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        assert r1["prediction"]["risk_score"] == r2["prediction"]["risk_score"]

    def test_engine_initialize_idempotent(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        engine = OfflineReplayEngine(config=_replay_config())
        r1 = engine.initialize()
        r2 = engine.initialize()
        assert r1["initialized"] is True
        assert r2["initialized"] is True
