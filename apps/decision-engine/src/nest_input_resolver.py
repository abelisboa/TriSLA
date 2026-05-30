"""
M1 — Resolve NestSubset for /evaluate when SEM sends nest_id without nest dict.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from models import NestSubset, SLAEvaluateInput


def _intent_id_from_evaluate_input(sla_input: SLAEvaluateInput) -> str:
    intent_id = (sla_input.intent_id or "").strip()
    if intent_id:
        return intent_id
    intent_raw = sla_input.intent
    if isinstance(intent_raw, dict):
        candidate = intent_raw.get("intent_id")
        if candidate is not None and str(candidate).strip():
            return str(candidate).strip()
    return ""


def _nest_from_dict(raw: Dict[str, Any]) -> Optional[NestSubset]:
    nest_id = raw.get("nest_id")
    if not nest_id or not str(nest_id).strip():
        return None
    payload = dict(raw)
    payload.setdefault("network_slices", [])
    payload.setdefault("resources", {})
    payload.setdefault("status", "generated")
    if not payload.get("intent_id"):
        payload["intent_id"] = str(nest_id).replace("nest-", "", 1)
    return NestSubset(**payload)


def resolve_nest_for_evaluate(sla_input: SLAEvaluateInput) -> Optional[NestSubset]:
    """
    Map SLAEvaluateInput to NestSubset for DecisionInput.

    Priority:
    1. Explicit ``nest`` dict when present (unchanged legacy path).
    2. Top-level ``nest_id`` from SEM (PNL path — M1 fix).
    """
    nest_raw = sla_input.nest
    if isinstance(nest_raw, dict) and nest_raw:
        resolved = _nest_from_dict(nest_raw)
        if resolved is not None:
            return resolved

    nest_id = (sla_input.nest_id or "").strip()
    if not nest_id:
        return None

    intent_id = _intent_id_from_evaluate_input(sla_input)
    if not intent_id:
        intent_id = nest_id.replace("nest-", "", 1)

    return NestSubset(
        nest_id=nest_id,
        intent_id=intent_id,
        network_slices=[],
        resources={},
        status="generated",
    )
