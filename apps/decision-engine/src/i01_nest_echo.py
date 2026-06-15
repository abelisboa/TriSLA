"""
Wave 3A G3-C — inbound NEST echo at DE /evaluate ingress.

Echo-only: the inbound ``nest`` dict is retained for traceability and returned
under ``DecisionResult.metadata.inbound_nest``. It MUST NOT be wired into
``DecisionInput.nest`` or decision rules (see ``resolve_nest_for_evaluate``).
"""

from typing import Any, Dict, Optional

from models import DecisionResult


def echo_inbound_nest(
    result: DecisionResult,
    inbound: Optional[Dict[str, Any]],
) -> None:
    """Attach SEM inbound NEST body to the decision response (echo only)."""
    if not inbound:
        return
    result.metadata = result.metadata or {}
    result.metadata["inbound_nest"] = inbound
