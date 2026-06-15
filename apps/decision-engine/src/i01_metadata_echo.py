"""
Wave 1 G3-A — inbound metadata echo at DE /evaluate ingress.

Echo-only: metadata is retained for traceability and returned under
``DecisionResult.metadata.inbound_metadata``. It MUST NOT be wired into
``DecisionInput`` or decision rules.
"""

from typing import Any, Dict, Optional

from models import DecisionResult


def echo_inbound_metadata(
    result: DecisionResult,
    inbound: Optional[Dict[str, Any]],
) -> None:
    """Attach SEM inbound metadata bag to the decision response (echo only)."""
    if not inbound:
        return
    result.metadata = result.metadata or {}
    result.metadata["inbound_metadata"] = inbound
