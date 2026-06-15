"""Shadow logger foundation (Phase 33 — metadata only, no candidate inference)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from shadow_event_schema import build_foundation_event, validate_shadow_event
from shadow_logger_config import ShadowLoggerConfig
from shadow_registry_hooks import (
    build_logger_registry_hook,
    golden_vector_reference_for_vector,
    load_golden_vector_by_id,
    load_shadow_validation_registry,
)
from shadow_sinks import FileShadowLogSink, create_sink

logger = logging.getLogger(__name__)


class ShadowLogger:
    """
    Foundation shadow logger — records metadata events only.
    Does NOT execute candidate inference or emit scores/confidence.
    """

    def __init__(self, config: Optional[ShadowLoggerConfig] = None):
        self.config = config or ShadowLoggerConfig.from_env()
        self._sink = create_sink(
            self.config.log_sink,
            self.config.log_path,
            self.config.run_id,
            self.config.otlp_enabled,
            enabled=self.config.logger_enabled,
        )
        self._registry_hook: Optional[Dict[str, Any]] = None
        self._events_emitted = 0
        self._initialized = False

    @property
    def enabled(self) -> bool:
        return self.config.logger_enabled

    def initialize(self) -> Dict[str, Any]:
        """Emit logger_initialized foundation event when enabled."""
        hook = build_logger_registry_hook(
            self.config.registry_path,
            phase="33",
            logger_enabled=self.config.logger_enabled,
            sink=self.config.log_sink,
        )
        self._registry_hook = hook

        event = build_foundation_event(
            request_id=f"shadow-logger-init-{self.config.run_id}",
            model_id="MR-001",
            bundle_id=hook.get("active_runtime_bundle") or "BUNDLE-OP-001",
            run_id=self.config.run_id,
            execution_context={
                "environment": self.config.environment,
                "phase": "33",
                "event_kind": "logger_initialized",
                "shadow_execution": False,
                "candidate_inference": False,
                "sink": self.config.log_sink,
                "logger_enabled": self.config.logger_enabled,
            },
        )

        if self.config.logger_enabled:
            self._emit(event)
        self._initialized = True
        return {"initialized": True, "registry_hook": hook, "event": event}

    def register_context(
        self,
        *,
        request_id: str,
        model_id: str,
        bundle_id: str,
        event_kind: str = "context_registered",
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register execution context without candidate data."""
        ctx = {
            "environment": self.config.environment,
            "phase": "33",
            "event_kind": event_kind,
            "shadow_execution": False,
            "candidate_inference": False,
        }
        if extra_context:
            ctx.update(extra_context)

        event = build_foundation_event(
            request_id=request_id,
            model_id=model_id,
            bundle_id=bundle_id,
            run_id=self.config.run_id,
            execution_context=ctx,
        )
        if self.config.logger_enabled:
            self._emit(event)
        return event

    def register_golden_vector_reference(
        self,
        *,
        request_id: str,
        vector_id: str,
        model_id: str = "MR-001",
        bundle_id: str = "BUNDLE-OP-001",
    ) -> Dict[str, Any]:
        """Attach golden vector reference metadata — no inference."""
        registry = load_shadow_validation_registry(self.config.registry_path)
        gvr = golden_vector_reference_for_vector(registry, vector_id)
        vec = load_golden_vector_by_id(self.config.golden_vectors_path, vector_id)
        if vec:
            gvr["slice_type"] = vec.get("slice_type")
            gvr["intent_id"] = (vec.get("metrics") or {}).get("intent_id")

        event = build_foundation_event(
            request_id=request_id,
            model_id=model_id,
            bundle_id=bundle_id,
            run_id=self.config.run_id,
            golden_vector_reference=gvr,
            execution_context={
                "environment": self.config.environment,
                "phase": "33",
                "event_kind": "golden_vector_reference",
                "shadow_execution": False,
                "candidate_inference": False,
            },
        )
        if self.config.logger_enabled:
            self._emit(event)
        return event

    def _emit(self, event: Dict[str, Any]) -> None:
        validate_shadow_event(event)
        try:
            self._sink.write(event)
            self._events_emitted += 1
            logger.info("[SHADOW] foundation event emitted request_id=%s", event.get("request_id"))
        except Exception as exc:
            logger.warning("[SHADOW] emit failed (fail-silent): %s", exc)

    def write_manifest(self) -> None:
        if not self.config.logger_enabled or not isinstance(self._sink, FileShadowLogSink):
            return
        manifest = {
            "run_id": self.config.run_id,
            "record_type": "shadow_foundation_manifest",
            "schema_version": "1.0.0",
            "events_emitted": self._events_emitted,
            "shadow_execution": False,
            "registry_hook": self._registry_hook,
        }
        self._sink.write_manifest(manifest)

    def get_status(self) -> Dict[str, Any]:
        return {
            "logger_enabled": self.config.logger_enabled,
            "initialized": self._initialized,
            "shadow_execution": False,
            "candidate_inference": False,
            "sink": self.config.log_sink,
            "run_id": self.config.run_id,
            "events_emitted": self._events_emitted,
            "otlp_enabled": self.config.otlp_enabled,
            "registry_hook_loaded": self._registry_hook is not None,
        }

    def close(self) -> None:
        self.write_manifest()
        self._sink.close()
