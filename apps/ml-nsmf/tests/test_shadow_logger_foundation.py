"""Phase 33 — shadow logger foundation tests."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from copy import deepcopy
from io import StringIO
from pathlib import Path

import pytest

ML_SRC = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ML_SRC))

from dual_load_config import DualLoadConfig  # noqa: E402
from dual_load_service import DualLoadService  # noqa: E402
from shadow_event_schema import (  # noqa: E402
    ShadowEventSchemaError,
    build_foundation_event,
    validate_shadow_event,
)
from shadow_logger import ShadowLogger  # noqa: E402
from shadow_logger_config import ShadowLoggerConfig  # noqa: E402
from shadow_registry_hooks import (  # noqa: E402
    build_logger_registry_hook,
    golden_vector_reference_for_vector,
    load_golden_vector_by_id,
    load_shadow_validation_registry,
)
from shadow_sinks import (  # noqa: E402
    FileShadowLogSink,
    OtlpShadowLogSink,
    StdoutShadowLogSink,
    create_sink,
)

MODELS_DIR = REPO_ROOT / "apps" / "ml-nsmf" / "models"
GOLDEN_PATH = REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_v1.json"
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


def _disabled_logger_config(tmp_path: Path) -> ShadowLoggerConfig:
    return ShadowLoggerConfig(
        logger_enabled=False,
        log_sink="file",
        log_path=str(tmp_path),
        run_id="test-run-disabled",
        environment="test",
        otlp_enabled=False,
        golden_vectors_path=str(GOLDEN_PATH),
        golden_manifest_path=str(
            REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_manifest_v1.json"
        ),
        registry_path=str(REGISTRY_PATH),
    )


def _enabled_file_logger_config(tmp_path: Path) -> ShadowLoggerConfig:
    return ShadowLoggerConfig(
        logger_enabled=True,
        log_sink="file",
        log_path=str(tmp_path),
        run_id="test-run-file",
        environment="test",
        otlp_enabled=False,
        golden_vectors_path=str(GOLDEN_PATH),
        golden_manifest_path=str(
            REPO_ROOT / "model-registry" / "shadow-validation" / "golden_vectors_manifest_v1.json"
        ),
        registry_path=str(REGISTRY_PATH),
    )


class TestLoggerInitialization:
    def test_shadow_logger_disabled_by_default(self):
        cfg = ShadowLoggerConfig.from_env()
        assert cfg.logger_enabled is False

    def test_initialize_when_disabled(self, tmp_path):
        logger = ShadowLogger(_disabled_logger_config(tmp_path))
        result = logger.initialize()
        assert result["initialized"] is True
        assert logger.get_status()["initialized"] is True
        assert logger.get_status()["events_emitted"] == 0
        assert logger.get_status()["shadow_execution"] is False
        assert logger.get_status()["candidate_inference"] is False

    def test_initialize_when_enabled_writes_file(self, tmp_path):
        logger = ShadowLogger(_enabled_file_logger_config(tmp_path))
        logger.initialize()
        sink = logger._sink
        assert isinstance(sink, FileShadowLogSink)
        assert sink.events_path.is_file()
        lines = sink.events_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["execution_context"]["event_kind"] == "logger_initialized"
        logger.close()

    def test_stdout_sink(self):
        buf = StringIO()
        sink = StdoutShadowLogSink(stream=buf)
        event = build_foundation_event(
            request_id="req-1",
            model_id="MR-001",
            bundle_id="BUNDLE-OP-001",
            execution_context={"shadow_execution": False, "candidate_inference": False},
        )
        sink.write(event)
        assert "shadow_foundation_event" in buf.getvalue()

    def test_otlp_sink_disabled_by_default(self):
        sink = OtlpShadowLogSink(enabled=False)
        event = build_foundation_event(
            request_id="req-otlp",
            model_id="MR-001",
            bundle_id="BUNDLE-OP-001",
            execution_context={"shadow_execution": False, "candidate_inference": False},
        )
        sink.write(event)
        assert len(sink.buffer) == 1


class TestSchemaValidation:
    def test_valid_foundation_event(self):
        event = build_foundation_event(
            request_id="req-schema",
            model_id="MR-001",
            bundle_id="BUNDLE-OP-001",
            execution_context={
                "phase": "33",
                "event_kind": "context_registered",
                "shadow_execution": False,
                "candidate_inference": False,
            },
        )
        validate_shadow_event(event)

    def test_rejects_candidate_score_fields(self):
        event = build_foundation_event(
            request_id="req-bad",
            model_id="MR-001",
            bundle_id="BUNDLE-OP-001",
            execution_context={"shadow_execution": False, "candidate_inference": False},
        )
        event["risk_score"] = 0.5
        with pytest.raises(ShadowEventSchemaError):
            validate_shadow_event(event)

    def test_rejects_shadow_execution_true(self):
        with pytest.raises(ShadowEventSchemaError):
            build_foundation_event(
                request_id="req-exec",
                model_id="MR-001",
                bundle_id="BUNDLE-OP-001",
                execution_context={"shadow_execution": True, "candidate_inference": False},
            )

    def test_golden_vector_reference_requires_vector_id(self):
        event = {
            "record_type": "shadow_foundation_event",
            "schema_version": "1.0.0",
            "request_id": "req-gvr",
            "model_id": "MR-001",
            "bundle_id": "BUNDLE-OP-001",
            "timestamp_utc": "2026-06-12T00:00:00.000Z",
            "execution_context": {"shadow_execution": False, "candidate_inference": False},
            "golden_vector_reference": {"artifact_id": "golden_vectors_v1"},
        }
        with pytest.raises(ShadowEventSchemaError):
            validate_shadow_event(event)


class TestRegistryIntegration:
    def test_load_shadow_validation_registry(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        registry = load_shadow_validation_registry(str(REGISTRY_PATH))
        assert registry["registry_id"] == "shadow_validation_registry"
        assert registry["golden_set"]["status"] == "FROZEN"

    def test_build_logger_registry_hook(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        hook = build_logger_registry_hook(str(REGISTRY_PATH), phase="33", logger_enabled=False)
        assert hook["hook_type"] == "shadow_logger_foundation"
        assert hook["shadow_execution"] is False
        assert hook["golden_set"]["artifact_id"] == "golden_vectors_v1"
        assert hook["active_runtime_bundle"] == "BUNDLE-OP-001"

    def test_registry_flags_shadow_logger_ready(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        registry = load_shadow_validation_registry(str(REGISTRY_PATH))
        flags = registry.get("flags") or {}
        assert flags.get("SHADOW_LOGGER_IMPLEMENTED") is True
        assert flags.get("SHADOW_LOGGER_READY") is True
        shadow_logger = registry.get("shadow_logger") or {}
        assert shadow_logger.get("execution_wired") is False
        assert shadow_logger.get("candidate_inference_wired") is False


class TestGoldenVectorReference:
    def test_golden_vector_reference_for_vector(self):
        if not REGISTRY_PATH.is_file():
            pytest.skip("registry not present")
        registry = load_shadow_validation_registry(str(REGISTRY_PATH))
        ref = golden_vector_reference_for_vector(registry, "GV-URLLC-001")
        assert ref["vector_id"] == "GV-URLLC-001"
        assert ref["artifact_id"] == "golden_vectors_v1"
        assert ref["checksum_sha256"]

    def test_load_golden_vector_by_id(self):
        if not GOLDEN_PATH.is_file():
            pytest.skip("golden vectors not present")
        vec = load_golden_vector_by_id(str(GOLDEN_PATH), "GV-URLLC-001")
        assert vec is not None
        assert vec["slice_type"] == "URLLC"

    def test_register_golden_vector_reference(self, tmp_path):
        if not GOLDEN_PATH.is_file() or not REGISTRY_PATH.is_file():
            pytest.skip("artifacts not present")
        logger = ShadowLogger(_disabled_logger_config(tmp_path))
        logger.initialize()
        event = logger.register_golden_vector_reference(
            request_id="req-gv",
            vector_id="GV-URLLC-001",
        )
        assert event["golden_vector_reference"]["vector_id"] == "GV-URLLC-001"
        assert event["execution_context"]["event_kind"] == "golden_vector_reference"
        assert "risk_score" not in event
        assert "confidence" not in event


class TestBackwardCompatibility:
    @pytest.fixture(scope="module")
    def legacy_service(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        return DualLoadService(_legacy_config())

    def test_predict_response_unchanged(self, legacy_service):
        response = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        assert "latency_ms" in response
        assert "prediction" in response
        assert "explanation" in response
        for forbidden in ("shadow", "candidate_prediction", "candidate_output"):
            assert forbidden not in response

    def test_health_includes_shadow_logger_status(self, legacy_service):
        status = legacy_service.get_status()
        assert "shadow_logger" in status
        sl = status["shadow_logger"]
        assert sl["shadow_execution"] is False
        assert sl["candidate_inference"] is False
        assert sl["logger_enabled"] is False

    def test_predict_does_not_emit_shadow_events(self, legacy_service, tmp_path):
        cfg = _enabled_file_logger_config(tmp_path)
        enabled_logger = ShadowLogger(cfg)
        enabled_logger.initialize()
        legacy_service.shadow_logger = enabled_logger
        before = enabled_logger.get_status()["events_emitted"]
        legacy_service.predict(deepcopy(SAMPLE_METRICS))
        after = enabled_logger.get_status()["events_emitted"]
        assert after == before
        enabled_logger.close()


class TestRegression:
    @pytest.fixture(scope="module")
    def legacy_service(self):
        if not (MODELS_DIR / "viability_model.pkl").is_file():
            pytest.skip("model artifacts missing")
        return DualLoadService(_legacy_config())

    def test_dual_load_status_still_valid(self, legacy_service):
        status = legacy_service.get_status()
        assert status["dual_load_enabled"] is False
        assert status["shadow_execution"] is False
        assert status["active"]["authority"] is True

    def test_predict_scores_stable(self, legacy_service):
        r1 = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        r2 = legacy_service.predict(deepcopy(SAMPLE_METRICS))
        assert r1["prediction"]["risk_score"] == r2["prediction"]["risk_score"]
        assert r1["prediction"]["confidence"] == pytest.approx(
            r2["prediction"]["confidence"], rel=1e-9
        )
