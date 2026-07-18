"""Active model bundle loader."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import List

from dual_load_config import DualLoadConfig

logger = logging.getLogger(__name__)


@dataclass
class BundleSpec:
    bundle_id: str
    role: str
    model_path: str
    scaler_path: str
    registry_entries: List[str] = field(default_factory=list)


@dataclass
class BundleValidationResult:
    bundle_id: str
    role: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def resolve_active_bundle(config: DualLoadConfig) -> BundleSpec:
    return BundleSpec(
        bundle_id="BUNDLE-OP-001",
        role="active",
        model_path=config.active_model_path,
        scaler_path=config.active_scaler_path,
        registry_entries=["MR-001", "MR-002"],
    )


def validate_bundle(spec: BundleSpec) -> BundleValidationResult:
    errors: List[str] = []
    if not os.path.isfile(spec.model_path):
        errors.append(f"model missing: {spec.model_path}")
    if not os.path.isfile(spec.scaler_path):
        errors.append(f"scaler missing: {spec.scaler_path}")
    return BundleValidationResult(
        bundle_id=spec.bundle_id,
        role=spec.role,
        valid=not errors,
        errors=errors,
    )
