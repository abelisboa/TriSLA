from __future__ import annotations

from typing import Any, Dict, Optional


def map_bc_nssmf_response(*, status_code: int, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    body = body or {}

    if 400 <= status_code < 500:
        detail = body.get("detail") or body.get("message") or body
        return {
            "success": False,
            "phase": "blockchain",
            "reason": "business_error",
            "detail": detail,
            "upstream_status": status_code,
        }

    if 500 <= status_code < 600:
        detail = body.get("detail") or body.get("message") or body
        return {
            "success": False,
            "phase": "blockchain",
            "reason": "nasp_degraded",
            "detail": detail or "BC-NSSMF indisponível (erro 5xx).",
            "upstream_status": status_code,
        }

    return {
        "success": False,
        "phase": "blockchain",
        "reason": "nasp_degraded",
        "detail": {"unexpected_status": status_code, "body": body},
        "upstream_status": status_code,
    }

