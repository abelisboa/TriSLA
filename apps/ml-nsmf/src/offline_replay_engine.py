"""Offline replay engine foundation (Phase 34 — prepare only, no inference)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from dual_load_config import DualLoadConfig
from golden_vector_loader import GoldenVectorLoadError, load_golden_vector_refs
from model_loader import resolve_active_bundle, resolve_candidate_bundle, validate_bundle
from offline_replay_config import OfflineReplayConfig
from replay_context import BundleContext, ReplayContext, build_replay_context
from replay_manifest import (
    ReplayManifestError,
    build_prepared_replay_manifest,
    load_manifest,
    validate_golden_manifest,
)
from offline_replay_executor import execute_offline_replay
from replay_registry_hooks import build_replay_registry_hook

logger = logging.getLogger(__name__)


class OfflineReplayEngine:
    """
    Foundation offline replay engine — loads vectors and bundle specs,
    validates context, prepares future execution. Does NOT run inference.
    """

    def __init__(
        self,
        config: Optional[OfflineReplayConfig] = None,
        dual_load_config: Optional[DualLoadConfig] = None,
    ):
        self.config = config or OfflineReplayConfig.from_env()
        self._dual_config = (dual_load_config or DualLoadConfig.from_env()).dev_paths_if_missing()
        self._registry_hook: Optional[Dict[str, Any]] = None
        self._manifest_validation: Optional[Dict[str, Any]] = None
        self._replay_context: Optional[ReplayContext] = None
        self._prepared_manifest: Optional[Dict[str, Any]] = None
        self._initialized = False

    @property
    def enabled(self) -> bool:
        return self.config.replay_enabled

    def initialize(self) -> Dict[str, Any]:
        """Load registry hook and validate golden manifest."""
        hook = build_replay_registry_hook(
            self.config.registry_path,
            phase="34",
            replay_enabled=self.config.replay_enabled,
        )
        self._registry_hook = hook

        manifest_doc = load_manifest(self.config.golden_manifest_path)
        self._manifest_validation = validate_golden_manifest(
            manifest_doc,
            golden_vectors_path=self.config.golden_vectors_path,
            validate_checksum=self.config.validate_checksums,
        )
        self._initialized = True
        logger.info(
            "[OFFLINE_REPLAY] initialized run_id=%s enabled=%s",
            self.config.run_id,
            self.config.replay_enabled,
        )
        return {
            "initialized": True,
            "registry_hook": hook,
            "manifest_validation": self._manifest_validation,
        }

    def prepare_context(self) -> ReplayContext:
        """
        Load golden vectors, validate bundle specs, build replay context.
        Does NOT execute inference or scoring.
        """
        if not self._initialized:
            self.initialize()

        errors: list[str] = []
        try:
            golden = load_golden_vector_refs(
                self.config.golden_vectors_path,
                max_vectors=self.config.max_vectors,
            )
        except (OSError, GoldenVectorLoadError) as exc:
            errors.append(str(exc))
            golden = None

        active_spec = resolve_active_bundle(self._dual_config)
        active_val = validate_bundle(active_spec)
        active_ctx = BundleContext(
            bundle_id=active_spec.bundle_id,
            role=active_spec.role,
            model_path=active_spec.model_path,
            scaler_path=active_spec.scaler_path,
            valid=active_val.valid,
        )
        if not active_val.valid:
            errors.extend(active_val.errors)

        candidate_ctx: Optional[BundleContext] = None
        try:
            cand_spec = resolve_candidate_bundle(self._dual_config)
            cand_val = validate_bundle(cand_spec)
            candidate_ctx = BundleContext(
                bundle_id=cand_spec.bundle_id,
                role=cand_spec.role,
                model_path=cand_spec.model_path,
                scaler_path=cand_spec.scaler_path,
                valid=cand_val.valid,
                classifier_path=cand_spec.classifier_path,
            )
            if not cand_val.valid:
                errors.extend(cand_val.errors)
        except Exception as exc:
            errors.append(f"candidate bundle resolution: {exc}")

        vector_ids: list[str] = []
        slice_dist: Dict[str, int] = {}
        artifact_id = "golden_vectors_v1"
        if golden:
            vector_ids = [v.vector_id for v in golden.vectors]
            slice_dist = golden.slice_distribution
            artifact_id = golden.artifact_id

        assert self._registry_hook is not None
        assert self._manifest_validation is not None

        ctx = build_replay_context(
            run_id=self.config.run_id,
            environment=self.config.environment,
            golden_artifact_id=artifact_id,
            vector_ids=vector_ids,
            slice_distribution=slice_dist,
            active_bundle=active_ctx,
            candidate_bundle=candidate_ctx,
            registry_hook=self._registry_hook,
            manifest_validation=self._manifest_validation,
            errors=errors,
        )
        self._replay_context = ctx

        if ctx.status == "PREPARED":
            self._prepared_manifest = build_prepared_replay_manifest(
                run_id=self.config.run_id,
                golden_manifest=load_manifest(self.config.golden_manifest_path),
                registry_hook=self._registry_hook,
                vector_ids=vector_ids,
                active_bundle_id=active_ctx.bundle_id,
                candidate_bundle_id=(
                    candidate_ctx.bundle_id if candidate_ctx else None
                ),
            )

        return ctx

    def execute_replay(self) -> Dict[str, Any]:
        """Execute offline replay (Phase 35) — not wired to production predict path."""
        if not self._initialized:
            self.initialize()
        result = execute_offline_replay(self.config, self._dual_config)
        self._execution_result = result
        return result

    def get_execution_result(self) -> Optional[Dict[str, Any]]:
        return getattr(self, "_execution_result", None)

    def get_status(self) -> Dict[str, Any]:
        exec_result = self.get_execution_result()
        ctx_status = None
        if exec_result:
            ctx_status = {
                "status": "EXECUTED",
                "vector_count_executed": exec_result["execution_manifest"]["vector_count_executed"],
                "inference_execution": True,
                "replay_execution": True,
            }
        elif self._replay_context:
            ctx_status = {
                "status": self._replay_context.status,
                "vector_count_planned": self._replay_context.vector_count_planned,
                "inference_execution": self._replay_context.inference_execution,
                "replay_execution": self._replay_context.replay_execution,
            }
        return {
            "replay_enabled": self.config.replay_enabled,
            "initialized": self._initialized,
            "inference_execution": exec_result is not None,
            "replay_execution": exec_result is not None,
            "run_id": self.config.run_id,
            "registry_hook_loaded": self._registry_hook is not None,
            "manifest_validated": self._manifest_validation is not None,
            "context_prepared": self._replay_context is not None,
            "context": ctx_status,
        }

    def get_prepared_manifest(self) -> Optional[Dict[str, Any]]:
        return self._prepared_manifest

    def close(self) -> None:
        return
