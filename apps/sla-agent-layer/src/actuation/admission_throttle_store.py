"""Persistent admission throttle state (external gate — does not modify Decision Engine)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

_lock = Lock()

ACT_ORCH_005 = "ACT-ORCH-005"
ACTION_DOMAIN_ORCHESTRATION = "ORCHESTRATION"


class ThrottleState(str, Enum):
    NORMAL = "NORMAL"
    THROTTLED = "THROTTLED"
    RESTORED = "RESTORED"


class AdmissionThrottleRecord(BaseModel):
    state: ThrottleState = ThrottleState.NORMAL
    reason: Optional[str] = None
    actor: Optional[str] = None
    authorization_state: Optional[str] = None
    request_id: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    throttled_at: Optional[datetime] = None
    restored_at: Optional[datetime] = None
    history: list[Dict[str, Any]] = Field(default_factory=list)


def store_path() -> Path:
    raw = os.getenv("ADMISSION_THROTTLE_STORE_PATH", "/tmp/trisla_admission_throttle")
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path / "throttle_state.json"


def load_throttle() -> AdmissionThrottleRecord:
    path = store_path()
    if not path.exists():
        return AdmissionThrottleRecord()
    with _lock:
        data = json.loads(path.read_text(encoding="utf-8"))
    return AdmissionThrottleRecord.model_validate(data)


def save_throttle(record: AdmissionThrottleRecord) -> None:
    record.updated_at = datetime.now(timezone.utc)
    with _lock:
        store_path().write_text(
            json.dumps(record.model_dump(mode="json"), indent=2, default=str),
            encoding="utf-8",
        )


def admission_allowed() -> bool:
    return load_throttle().state != ThrottleState.THROTTLED


def gate_status() -> Dict[str, Any]:
    rec = load_throttle()
    return {
        "action": ACT_ORCH_005,
        "throttle_state": rec.state.value,
        "admission_allowed": rec.state != ThrottleState.THROTTLED,
        "reason": rec.reason,
        "actor": rec.actor,
        "request_id": rec.request_id,
        "updated_at": rec.updated_at.isoformat(),
        "external_gate": True,
        "decision_engine_unmodified": True,
    }


def apply_throttled(
    *,
    reason: str,
    actor: str,
    authorization_state: str,
    request_id: str,
) -> AdmissionThrottleRecord:
    rec = load_throttle()
    rec.state = ThrottleState.THROTTLED
    rec.reason = reason
    rec.actor = actor
    rec.authorization_state = authorization_state
    rec.request_id = request_id
    rec.throttled_at = datetime.now(timezone.utc)
    rec.history.append(
        {
            "event": "THROTTLED",
            "request_id": request_id,
            "actor": actor,
            "reason": reason,
            "at": rec.throttled_at.isoformat(),
        }
    )
    save_throttle(rec)
    return rec


def apply_restored(*, actor: str, reason: str, request_id: str) -> AdmissionThrottleRecord:
    rec = load_throttle()
    rec.state = ThrottleState.RESTORED
    rec.actor = actor
    rec.reason = reason
    rec.request_id = request_id
    rec.restored_at = datetime.now(timezone.utc)
    rec.history.append(
        {
            "event": "RESTORED",
            "request_id": request_id,
            "actor": actor,
            "reason": reason,
            "at": rec.restored_at.isoformat(),
        }
    )
    save_throttle(rec)
    # Gate open: transition RESTORED → NORMAL for admission
    rec.state = ThrottleState.NORMAL
    save_throttle(rec)
    return rec
