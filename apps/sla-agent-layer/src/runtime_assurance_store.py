"""In-memory assurance state per intent (transition detection only)."""
from __future__ import annotations

from typing import Dict, Optional

_store: Dict[str, str] = {}


def get_previous_state(intent_id: Optional[str]) -> Optional[str]:
    if not intent_id:
        return None
    return _store.get(str(intent_id))


def set_state(intent_id: Optional[str], state: str) -> None:
    if intent_id and state:
        _store[str(intent_id)] = state


def clear_state(intent_id: Optional[str]) -> None:
    if intent_id:
        _store.pop(str(intent_id), None)
