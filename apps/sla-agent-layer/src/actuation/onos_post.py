"""ONOS intent POST/GET client for ACT-TN-002 LIVE."""
from __future__ import annotations

from typing import Any, Optional, Tuple

from actuation.onos_rest import onos_request


def post_intent(intent_body: dict) -> Tuple[Optional[str], Optional[Any], Optional[str], dict]:
    """
    POST /onos/v1/intents
    Returns (onos_intent_key, response_json, error_code, audit).
    """
    data, err, audit = onos_request("POST", "/onos/v1/intents", body=intent_body)
    audit["operation"] = "post_intent"
    if err:
        return None, data, err, audit
    intent_key = _extract_intent_key(data)
    audit["onos_intent_key"] = intent_key
    return intent_key, data, None, audit


def get_intent(intent_key: str) -> Tuple[Optional[Any], Optional[str], dict]:
    """GET /onos/v1/intents/{key}"""
    path = f"/onos/v1/intents/{intent_key}"
    data, err, audit = onos_request("GET", path)
    audit["operation"] = "get_intent"
    audit["onos_intent_key"] = intent_key
    return data, err, audit


def list_intents() -> Tuple[Optional[Any], Optional[str], dict]:
    """GET /onos/v1/intents"""
    data, err, audit = onos_request("GET", "/onos/v1/intents")
    audit["operation"] = "list_intents"
    return data, err, audit


def _extract_intent_key(data: Any) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    intent = data.get("intent") if "intent" in data else data
    if isinstance(intent, dict):
        for key in ("id", "intentId", "key"):
            if intent.get(key) is not None:
                return str(intent[key])
    if data.get("id") is not None:
        return str(data["id"])
    return None
