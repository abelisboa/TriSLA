"""Model bundle loader abstraction (Phase 32)."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from dual_load_config import DualLoadConfig

logger = logging.getLogger(__name__)


@dataclass
class BundleSpec:
    bundle_id: str
    role: str
    model_path: str
    scaler_path: str
    classifier_path: Optional[str] = None
    metadata_path: Optional[str] = None
    registry_entries: List[str] = field(default_factory=list)
    load_classifier: bool = False


@dataclass
class BundleValidationResult:
    bundle_id: str
    role: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _read_manifest(bundle_dir: Path) -> Dict[str, Any]:
    manifest_path = bundle_dir / "bundle_manifest.json"
    if not manifest_path.is_file():
        return {}
    with manifest_path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_active_bundle(config: DualLoadConfig) -> BundleSpec:
    return BundleSpec(
        bundle_id="BUNDLE-OP-001",
        role="active",
        model_path=config.active_model_path,
        scaler_path=config.active_scaler_path,
        classifier_path=None,
        metadata_path=None,
        registry_entries=["MR-001", "MR-002"],
        load_classifier=False,
    )


def resolve_candidate_bundle(config: DualLoadConfig) -> BundleSpec:
    bundle_dir = Path(config.candidate_root) / config.candidate_bundle_id
    manifest = _read_manifest(bundle_dir)

    model_rel = manifest.get("model_path", "viability_model.pkl")
    scaler_rel = manifest.get("scaler_path", "scaler.pkl")
    clf_rel = manifest.get("classifier_path", "decision_classifier.pkl")
    meta_rel = manifest.get("metadata_path", "model_metadata.json")

    def _resolve(rel: str) -> str:
        p = bundle_dir / rel
        if p.is_file():
            return str(p)
        # Fallback: sibling models dir (dev tree)
        alt = bundle_dir.parent.parent / rel
        if alt.is_file():
            return str(alt)
        return str(p)

    entries = manifest.get("entries") or ["MR-003", "MR-004"]
    return BundleSpec(
        bundle_id=config.candidate_bundle_id,
        role="candidate",
        model_path=_resolve(model_rel),
        scaler_path=_resolve(scaler_rel),
        classifier_path=_resolve(clf_rel) if clf_rel else None,
        metadata_path=_resolve(meta_rel) if meta_rel else None,
        registry_entries=entries,
        load_classifier=True,
    )


def validate_bundle(spec: BundleSpec) -> BundleValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    if not os.path.isfile(spec.model_path):
        errors.append(f"model missing: {spec.model_path}")
    if not os.path.isfile(spec.scaler_path):
        errors.append(f"scaler missing: {spec.scaler_path}")

    if spec.load_classifier:
        if not spec.classifier_path or not os.path.isfile(spec.classifier_path):
            errors.append(f"classifier missing: {spec.classifier_path}")
    elif spec.classifier_path and os.path.isfile(spec.classifier_path):
        warnings.append("classifier present but not loaded for active role")

    if spec.metadata_path and not os.path.isfile(spec.metadata_path):
        warnings.append(f"metadata missing: {spec.metadata_path}")

    return BundleValidationResult(
        bundle_id=spec.bundle_id,
        role=spec.role,
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def load_golden_vectors(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        raise FileNotFoundError("golden vectors path not configured")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"golden vectors not found: {path}")
    with p.open(encoding="utf-8") as f:
        return json.load(f)
