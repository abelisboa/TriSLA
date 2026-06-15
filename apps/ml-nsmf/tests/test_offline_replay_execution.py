"""Phase 35 — offline replay execution tests."""

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
from offline_replay_executor import execute_offline_replay  # noqa: E402
from replay_parity import aggregate_parity_results, compute_vector_parity, jaccard  # noqa: E402
from replay_snapshot import REPLAY_SNAPSHOT_WINDOW, build_replay_snapshot  # noqa: E402
from replay_telemetry_gate import run_telemetry_consistency_gate, validate_replay_snapshot  # noqa: E402

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
        run_id="test-phase35-exec",
        environment="test",
        golden_vectors_path=str(GOLDEN_PATH),
        golden_manifest_path=str(MANIFEST_PATH),
        registry_path=str(REGISTRY_PATH),
        validate_checksums=True,
        max_vectors=max_vectors,
        snapshot_window_policy="[t-1s,t]",
        execute_offline=True,
    )


class TestReplaySnapshot:
    def test_snapshot_window_compliance(self):
        snap = build_replay_snapshot(
            vector_id="GV-URLLC-001",
            metrics=deepcopy(SAMPLE_METRICS),
            run_id="run-1",
        )
        assert snap["snapshot_window"]["policy"] == REPLAY_SNAPSHOT_WINDOW["policy"]
        assert snap["snapshot_window"]["step"] == "1s"
        assert validate_replay_snapshot(snap) == []

    def test_shared_snapshot_identity(self):
        snap = build_replay_snapshot(
            vector_id="GV-URLLC-001",
            metrics=deepcopy(SAMPLE_METRICS),
            run_id="run-1",
        )
        gate = run_telemetry_consistency_gate(snap, snap)
        assert gate.passed is True


class TestTelemetryGate:
    def test_gate_fails_on_different_snapshot(self):
        a = build_replay_snapshot(
            vector_id="GV-URLLC-001",
            metrics=deepcopy(SAMPLE_METRICS),
            run_id="run-a",
        )
        b = build_replay_snapshot(
            vector_id="GV-URLLC-001",
            metrics=deepcopy(SAMPLE_METRICS),
            run_id="run-b",
        )
        gate = run_telemetry_consistency_gate(a, b)
        assert gate.passed is False


class TestParity:
    def test_jaccard(self):
        assert jaccard(["a", "b"], ["b", "c"]) == pytest.approx(1 / 3)

    def test_aggregate_empty(self):
        assert aggregate_parity_results([])["vector_count"] == 0


class TestOfflineReplayExecution:
    @pytest.fixture(scope="module")
    def exec_result(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors missing")
        return execute_offline_replay(_exec_config(max_vectors=3), _dual_config())

    def test_active_and_candidate_executed(self, exec_result):
        m = exec_result["execution_manifest"]
        assert m["vector_count_executed"] == 3
        assert m["active_bundle_id"] == "BUNDLE-OP-001"
        assert m["candidate_bundle_id"] == "BUNDLE-SCI-001"

    def test_telemetry_gate_pass(self, exec_result):
        gate = exec_result["execution_manifest"]["telemetry_consistency_gate"]
        assert gate["passed"] is True
        assert gate["pass_count"] == 3

    def test_snapshot_window_in_manifest(self, exec_result):
        m = exec_result["execution_manifest"]
        assert m["snapshot_window_policy"] == "[t-1s,t]"
        assert m["snapshot_window_step"] == "1s"

    def test_parity_fields_present(self, exec_result):
        row = exec_result["vector_results"][0]
        p = row["parity"]
        assert "prediction_parity" in p
        assert "confidence_parity" in p
        assert "top3_factor_parity" in p
        assert "dominant_domain_parity" in p


class TestBackwardCompatibility:
    @pytest.fixture(scope="module")
    def legacy_service(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        cfg = DualLoadConfig(
            dual_load_enabled=False,
            active_model_path=str(MODELS_DIR / "viability_model.pkl"),
            active_scaler_path=str(MODELS_DIR / "scaler.pkl"),
            candidate_bundle_id="BUNDLE-SCI-001",
            candidate_root=str(MODELS_DIR / "candidate"),
            golden_vectors_path=str(GOLDEN_PATH),
            shadow_validation_enabled=False,
        )
        return DualLoadService(cfg)

    def test_predict_unchanged(self, legacy_service):
        r = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        assert "prediction" in r
        assert "shadow" not in r

    def test_offline_replay_not_executed_on_startup(self, legacy_service):
        status = legacy_service.offline_replay.get_status()
        assert status["replay_execution"] is False
