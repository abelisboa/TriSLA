"""ONOS intent DELETE client for ACT-TN-002 LIVE rollback."""
from __future__ import annotations

from typing import Any, Optional, Tuple

from actuation.onos_rest import onos_request


def delete_intent(intent_key: str) -> Tuple[bool, Optional[str], dict]:
    """
    DELETE /onos/v1/intents/{key}
    Returns (deleted_ok, error_code, audit).
    """
    path = f"/onos/v1/intents/{intent_key}"
    data, err, audit = onos_request("DELETE", path)
    audit["operation"] = "delete_intent"
    audit["onos_intent_key"] = intent_key
    if err:
        return False, err, audit
    audit["deleted"] = True
    return True, None, audit


def delete_intent_if_present(intent_key: str) -> Tuple[bool, Optional[str], dict]:
    """Idempotent delete — GET first, DELETE only if exists."""
    from actuation.onos_post import get_intent

    _, get_err, get_audit = get_intent(intent_key)
    audit = {"get": get_audit, "operation": "delete_intent_if_present"}
    if get_err == "ONOS_HTTP_404":
        audit["skipped"] = "not_found"
        return True, None, audit
    if get_err:
        return False, get_err, audit
    ok, del_err, del_audit = delete_intent(intent_key)
    audit["delete"] = del_audit
    return ok, del_err, audit
