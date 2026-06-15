"""Shared ONOS REST transport — auth, retries, audit envelope."""
from __future__ import annotations

import base64
import json
import logging
import os
import time
from typing import Any, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = float(os.getenv("ONOS_REST_TIMEOUT_SECONDS", "10"))
DEFAULT_RETRIES = int(os.getenv("ONOS_REST_RETRIES", "2"))
RETRY_BACKOFF = float(os.getenv("ONOS_REST_RETRY_BACKOFF_SECONDS", "0.5"))


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


def _auth_header() -> str:
    user, pwd = onos_rest_auth()
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return f"Basic {token}"


def onos_request(
    method: str,
    path: str,
    body: Optional[dict] = None,
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> Tuple[Optional[Any], Optional[str], dict]:
    """
    ONOS REST call with retries and audit envelope.
    Returns (json_body, error_code, audit).
    """
    url = f"{onos_rest_url()}{path}"
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    audit: dict = {
        "method": method.upper(),
        "path": path,
        "url": url,
        "attempts": 0,
        "onos_mutation": method.upper() in ("POST", "PUT", "DELETE"),
    }
    last_err: Optional[str] = None

    for attempt in range(retries + 1):
        audit["attempts"] = attempt + 1
        req = Request(
            url,
            data=payload,
            method=method.upper(),
            headers={
                "Authorization": _auth_header(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                audit["http_status"] = resp.status
                if not raw.strip():
                    audit["ok"] = True
                    return {}, None, audit
                data = json.loads(raw)
                audit["ok"] = True
                return data, None, audit
        except HTTPError as exc:
            last_err = "ONOS_AUTH_FAILED" if exc.code in (401, 403) else f"ONOS_HTTP_{exc.code}"
            audit["http_status"] = exc.code
            try:
                audit["error_body"] = exc.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
        except URLError:
            last_err = "ONOS_REST_UNREACHABLE"
        except json.JSONDecodeError:
            last_err = "ONOS_JSON_ERROR"
        except Exception:
            last_err = "ONOS_REST_ERROR"

        audit["last_error"] = last_err
        if attempt < retries:
            time.sleep(RETRY_BACKOFF * (attempt + 1))

    audit["ok"] = False
    return None, last_err, audit
