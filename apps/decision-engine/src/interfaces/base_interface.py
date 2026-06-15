import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from interfaces.config.interface_flags import should_emit_interface_signals

logger = logging.getLogger("trisla.interfaces")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _safe_payload_summary(payload: Any) -> dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, dict):
        summary: dict[str, Any] = {}
        for key in [
            "tenant_id",
            "request_id",
            "decision",
            "decision_score",
            "bc_status",
            "sla_agent_status",
            "nasp_orchestration_status",
            "telemetry_complete",
            "phase",
            "mode",
            "intent_id",
            "active",
            "ml_prediction_present",
            "action",
            "domains",
        ]:
            if key in payload:
                summary[key] = payload.get(key)
        return summary
    return {"type": type(payload).__name__}


def log_interface(
    interface_id: str, payload: Any = None, phase: str | None = None, mode: str | None = None
) -> None:
    if not should_emit_interface_signals():
        return
    event = {
        "event": "trisla_interface_invoked",
        "interface_id": interface_id,
        "phase": phase,
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload_summary": _safe_payload_summary(payload),
    }
    logger.info("[INTERFACE] %s", json.dumps(event, sort_keys=True, default=str))
