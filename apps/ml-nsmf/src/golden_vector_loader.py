"""Golden vector loader for offline replay (Phase 34)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class GoldenVectorLoadError(ValueError):
    """Raised when golden vector loading or validation fails."""


REQUIRED_VECTOR_FIELDS = frozenset({"vector_id", "slice_type", "metrics"})

FORBIDDEN_VECTOR_FIELDS = frozenset(
    {
        "risk_score",
        "confidence",
        "candidate_prediction",
        "active_prediction",
        "parity",
    }
)


@dataclass
class GoldenVectorRef:
    vector_id: str
    slice_type: str
    origin_source: Optional[str]
    intent_id: Optional[str]
    tags: List[str] = field(default_factory=list)


@dataclass
class GoldenVectorLoadResult:
    artifact_id: str
    vector_count: int
    slice_distribution: Dict[str, int]
    vectors: List[GoldenVectorRef]
    replay_corpus_sha256: Optional[str] = None


def _validate_vector_entry(vec: Dict[str, Any]) -> None:
    missing = REQUIRED_VECTOR_FIELDS - set(vec.keys())
    if missing:
        raise GoldenVectorLoadError(
            f"vector {vec.get('vector_id', '?')} missing fields: {sorted(missing)}"
        )
    for key in FORBIDDEN_VECTOR_FIELDS:
        if key in vec:
            raise GoldenVectorLoadError(
                f"vector {vec.get('vector_id')} contains forbidden field: {key}"
            )
    metrics = vec.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        raise GoldenVectorLoadError(
            f"vector {vec.get('vector_id')} metrics must be a non-empty dict"
        )


def load_golden_vector_refs(
    golden_vectors_path: str,
    *,
    max_vectors: int = 0,
    slice_filter: Optional[str] = None,
) -> GoldenVectorLoadResult:
    """
    Load golden vector metadata references — metrics loaded but never scored.
    """
    path = Path(golden_vectors_path)
    if not path.is_file():
        raise FileNotFoundError(f"golden vectors not found: {golden_vectors_path}")

    with path.open(encoding="utf-8") as f:
        doc = json.load(f)

    artifact_id = doc.get("artifact_id")
    if not artifact_id:
        raise GoldenVectorLoadError("golden vectors missing artifact_id")

    raw_vectors = doc.get("vectors") or []
    if not raw_vectors:
        raise GoldenVectorLoadError("golden vectors list is empty")

    refs: List[GoldenVectorRef] = []
    for vec in raw_vectors:
        _validate_vector_entry(vec)
        if slice_filter and vec.get("slice_type") != slice_filter:
            continue
        origin = vec.get("origin") or {}
        metrics = vec.get("metrics") or {}
        refs.append(
            GoldenVectorRef(
                vector_id=vec["vector_id"],
                slice_type=vec["slice_type"],
                origin_source=origin.get("source"),
                intent_id=metrics.get("intent_id") or origin.get("intent_id"),
                tags=list(vec.get("tags") or []),
            )
        )
        if max_vectors > 0 and len(refs) >= max_vectors:
            break

    return GoldenVectorLoadResult(
        artifact_id=artifact_id,
        vector_count=doc.get("vector_count", len(raw_vectors)),
        slice_distribution=dict(doc.get("slice_distribution") or {}),
        vectors=refs,
        replay_corpus_sha256=doc.get("replay_corpus_sha256"),
    )


def load_golden_vector_metrics(
    golden_vectors_path: str,
    vector_id: str,
) -> Optional[Dict[str, Any]]:
    """Load metrics for a single vector — for future replay, not inference."""
    path = Path(golden_vectors_path)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        doc = json.load(f)
    for vec in doc.get("vectors") or []:
        if vec.get("vector_id") == vector_id:
            return dict(vec.get("metrics") or {})
    return None
