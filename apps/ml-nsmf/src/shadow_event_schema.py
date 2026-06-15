"""Shadow foundation event schema (Phase 33 — metadata only, no candidate scores)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

SCHEMA_VERSION = "1.0.0"
RECORD_TYPE = "shadow_foundation_event"

REQUIRED_FIELDS = frozenset(
    {
        "record_type",
        "schema_version",
        "request_id",
        "model_id",
        "bundle_id",
        "timestamp_utc",
        "execution_context",
    }
)

OPTIONAL_FIELDS = frozenset({"golden_vector_reference", "run_id"})

ALLOWED_TOP_LEVEL = REQUIRED_FIELDS | OPTIONAL_FIELDS

FORBIDDEN_FIELDS: Set[str] = frozenset(
    {
        "candidate_output",
        "active_output",
        "comparison",
        "risk_score",
        "raw_risk_score",
        "slice_adjusted_risk_score",
        "confidence",
        "confidence_score",
        "classifier_confidence",
        "predicted_decision_class",
        "class_probabilities",
        "candidate_prediction",
        "candidate_score",
        "parity",
        "risk_abs_delta",
        "decision_class_match",
    }
)

FORBIDDEN_SUBSTRINGS = ("candidate_score", "candidate_confidence", "candidate_decision")


class ShadowEventSchemaError(ValueError):
    """Raised when a shadow event violates foundation schema rules."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _find_forbidden_keys(obj: Any, prefix: str = "") -> List[str]:
    found: List[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in FORBIDDEN_FIELDS:
                found.append(path)
            key_lower = str(key).lower()
            for sub in FORBIDDEN_SUBSTRINGS:
                if sub in key_lower:
                    found.append(path)
            found.extend(_find_forbidden_keys(value, path))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            found.extend(_find_forbidden_keys(item, f"{prefix}[{idx}]"))
    return found


def validate_shadow_event(event: Dict[str, Any]) -> None:
    """Validate foundation-only shadow event. Raises ShadowEventSchemaError on violation."""
    if not isinstance(event, dict):
        raise ShadowEventSchemaError("event must be a dict")

    extra = set(event.keys()) - ALLOWED_TOP_LEVEL
    if extra:
        raise ShadowEventSchemaError(f"unexpected fields: {sorted(extra)}")

    missing = REQUIRED_FIELDS - set(event.keys())
    if missing:
        raise ShadowEventSchemaError(f"missing required fields: {sorted(missing)}")

    if event.get("record_type") != RECORD_TYPE:
        raise ShadowEventSchemaError(f"record_type must be {RECORD_TYPE}")

    if event.get("schema_version") != SCHEMA_VERSION:
        raise ShadowEventSchemaError(f"schema_version must be {SCHEMA_VERSION}")

    forbidden = _find_forbidden_keys(event)
    if forbidden:
        raise ShadowEventSchemaError(f"forbidden candidate/score fields: {forbidden}")

    ctx = event.get("execution_context")
    if not isinstance(ctx, dict):
        raise ShadowEventSchemaError("execution_context must be a dict")
    if ctx.get("shadow_execution") is True:
        raise ShadowEventSchemaError("shadow_execution must be false in foundation phase")

    gvr = event.get("golden_vector_reference")
    if gvr is not None:
        if not isinstance(gvr, dict):
            raise ShadowEventSchemaError("golden_vector_reference must be a dict or omitted")
        for key in ("vector_id", "artifact_id"):
            if key not in gvr:
                raise ShadowEventSchemaError(f"golden_vector_reference missing {key}")


def build_foundation_event(
    *,
    request_id: str,
    model_id: str,
    bundle_id: str,
    execution_context: Dict[str, Any],
    golden_vector_reference: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
    timestamp_utc: Optional[str] = None,
) -> Dict[str, Any]:
    """Build and validate a foundation shadow event."""
    ctx = dict(execution_context)
    ctx.setdefault("shadow_execution", False)
    ctx.setdefault("candidate_inference", False)

    event: Dict[str, Any] = {
        "record_type": RECORD_TYPE,
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "model_id": model_id,
        "bundle_id": bundle_id,
        "timestamp_utc": timestamp_utc or utc_now_iso(),
        "execution_context": ctx,
    }
    if run_id:
        event["run_id"] = run_id
    if golden_vector_reference:
        event["golden_vector_reference"] = golden_vector_reference

    validate_shadow_event(event)
    return event
