"""GET-only ONOS REST client for W2B dry-run validation (no POST/PUT/DELETE)."""
from __future__ import annotations

import base64
import json
import os
from typing import Any, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ALLOWED_METHOD = "GET"


def onos_rest_url() -> str:
    return os.getenv(
        "ONOS_REST_URL",
        "http://onos.nasp-transport.svc.cluster.local:8181",
    ).rstrip("/")


def onos_rest_auth() -> Tuple[str, str]:
    raw = os.getenv("ONOS_REST_AUTH", "onos:rocks")
    if ":" in raw:
        user, pwd = raw.split(":", 1)
        return user, pwd
    return "onos", raw


def onos_get(path: str, timeout: float = 10.0) -> Tuple[Optional[Any], Optional[str]]:
    """GET-only. Returns (json_body, error_code). Never mutates ONOS."""
    url = f"{onos_rest_url()}{path}"
    user, pwd = onos_rest_auth()
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    req = Request(
        url,
        method=ALLOWED_METHOD,
        headers={"Authorization": f"Basic {token}", "Accept": "application/json"},
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if not body.strip():
                return {}, None
            return json.loads(body), None
    except HTTPError as exc:
        if exc.code in (401, 403):
            return None, "ONOS_AUTH_FAILED"
        return None, f"ONOS_HTTP_{exc.code}"
    except URLError:
        return None, "ONOS_REST_UNREACHABLE"
    except Exception:
        return None, "ONOS_REST_ERROR"


def onos_topology_snapshot() -> dict:
    """Read-only topology context for dry-run validation."""
    snapshot: dict = {"onos_mutation": False, "method": ALLOWED_METHOD}
    for ep, key in (
        ("/onos/v1/devices", "devices"),
        ("/onos/v1/links", "links"),
        ("/onos/v1/intents", "intents"),
    ):
        data, err = onos_get(ep)
        if err:
            snapshot[key] = {"error": err, "count": 0}
        elif isinstance(data, dict):
            items = data.get(key) or data.get("devices") or data.get("links") or data.get("intents")
            snapshot[key] = {"count": len(items) if isinstance(items, list) else 0}
        elif isinstance(data, list):
            snapshot[key] = {"count": len(data)}
        else:
            snapshot[key] = {"count": 0}
    return snapshot
