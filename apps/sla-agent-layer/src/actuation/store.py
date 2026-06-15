"""JSON persistence for actuation audit records."""
from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import List, Optional

from actuation.models import ActuationRecord

_lock = Lock()


def store_path() -> Path:
    raw = os.getenv("ACTUATION_AUDIT_STORE_PATH", "/tmp/trisla_actuation_audit")
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _record_file(request_id: str) -> Path:
    return store_path() / f"{request_id}.json"


def _index_file() -> Path:
    return store_path() / "index.jsonl"


def save_record(record: ActuationRecord) -> None:
    with _lock:
        payload = record.model_dump(mode="json")
        _record_file(record.request.request_id).write_text(
            json.dumps(payload, indent=2, default=str), encoding="utf-8"
        )
        with _index_file().open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"request_id": record.request.request_id, "updated_at": str(record.updated_at)}) + "\n")


def load_record(request_id: str) -> Optional[ActuationRecord]:
    path = _record_file(request_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return ActuationRecord.model_validate(data)


def list_recent(limit: int = 50) -> List[ActuationRecord]:
    index = _index_file()
    if not index.exists():
        return []
    lines = index.read_text(encoding="utf-8").strip().splitlines()
    out: List[ActuationRecord] = []
    for line in reversed(lines[-limit:]):
        if not line.strip():
            continue
        rid = json.loads(line).get("request_id")
        rec = load_record(rid) if rid else None
        if rec:
            out.append(rec)
    return out


def count_pending() -> int:
    return sum(
        1
        for r in list_recent(500)
        if r.request.authorization_state.value == "AUTH_PENDING"
    )


def count_executing() -> int:
    return sum(
        1
        for r in list_recent(500)
        if r.request.execution_state.value == "EXECUTING"
    )
