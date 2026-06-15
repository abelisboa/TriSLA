"""Audit and optional cleanup of FAILED ONOS intents (e.g. 0x288)."""
from __future__ import annotations

import os
from typing import Any, List, Tuple

from actuation.onos_delete import delete_intent_if_present
from actuation.onos_post import list_intents


def cleanup_enabled() -> bool:
    return os.getenv("TN002_FAILED_INTENT_CLEANUP_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def audit_failed_intents() -> Tuple[List[dict], dict]:
    """
    List FAILED intents from ONOS (GET-only audit).
    Returns (failed_intents, audit_envelope).
    """
    data, err, audit = list_intents()
    failed: List[dict] = []
    if err or not isinstance(data, dict):
        return failed, {"error": err, "audit": audit}
    intents = data.get("intents") or []
    for item in intents:
        if not isinstance(item, dict):
            continue
        state = (item.get("state") or item.get("status") or "").upper()
        if state == "FAILED" or item.get("failed"):
            failed.append(
                {
                    "id": item.get("id") or item.get("key"),
                    "state": state or "FAILED",
                    "app_id": item.get("appId"),
                    "priority": item.get("priority"),
                    "error": item.get("error") or item.get("failureReason"),
                }
            )
    audit["failed_count"] = len(failed)
    return failed, audit


def cleanup_failed_intent(intent_key: str) -> Tuple[bool, dict]:
    """
    DELETE a specific failed intent when cleanup flag enabled.
    Default OFF — no mutation unless explicitly enabled.
    """
    envelope: dict = {"intent_key": intent_key, "cleanup_enabled": cleanup_enabled()}
    if not cleanup_enabled():
        envelope["skipped"] = "TN002_FAILED_INTENT_CLEANUP_ENABLED=false"
        return False, envelope
    ok, err, audit = delete_intent_if_present(intent_key)
    envelope["delete_audit"] = audit
    envelope["ok"] = ok
    envelope["error"] = err
    return ok, envelope
