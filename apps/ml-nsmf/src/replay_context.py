"""Replay context generation (Phase 34 — preparation only, no inference)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


FORBIDDEN_CONTEXT_KEYS = frozenset(
    {
        "risk_score",
        "confidence",
        "candidate_prediction",
        "active_prediction",
        "parity",
        "inference_results",
        "scores",
    }
)


class ReplayContextError(ValueError):
    """Raised when replay context violates foundation rules."""


@dataclass
class BundleContext:
    bundle_id: str
    role: str
    model_path: str
    scaler_path: str
    valid: bool
    classifier_path: Optional[str] = None


@dataclass
class ReplayContext:
    run_id: str
    phase: str
    status: str
    inference_execution: bool
    replay_execution: bool
    environment: str
    golden_artifact_id: str
    vector_count_planned: int
    vector_ids: List[str]
    slice_distribution: Dict[str, int]
    active_bundle: BundleContext
    candidate_bundle: Optional[BundleContext]
    registry_hook: Dict[str, Any]
    manifest_validation: Dict[str, Any]
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        _assert_no_forbidden_keys(data)
        return data


def _assert_no_forbidden_keys(obj: Any, prefix: str = "") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in FORBIDDEN_CONTEXT_KEYS:
                raise ReplayContextError(f"forbidden key in replay context: {path}")
            _assert_no_forbidden_keys(value, path)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            _assert_no_forbidden_keys(item, f"{prefix}[{idx}]")


def build_replay_context(
    *,
    run_id: str,
    environment: str,
    golden_artifact_id: str,
    vector_ids: List[str],
    slice_distribution: Dict[str, int],
    active_bundle: BundleContext,
    candidate_bundle: Optional[BundleContext],
    registry_hook: Dict[str, Any],
    manifest_validation: Dict[str, Any],
    errors: Optional[List[str]] = None,
) -> ReplayContext:
    ctx = ReplayContext(
        run_id=run_id,
        phase="34",
        status="PREPARED" if not errors else "PREPARE_FAILED",
        inference_execution=False,
        replay_execution=False,
        environment=environment,
        golden_artifact_id=golden_artifact_id,
        vector_count_planned=len(vector_ids),
        vector_ids=vector_ids,
        slice_distribution=slice_distribution,
        active_bundle=active_bundle,
        candidate_bundle=candidate_bundle,
        registry_hook=registry_hook,
        manifest_validation=manifest_validation,
        errors=list(errors or []),
    )
    ctx.to_dict()
    return ctx
