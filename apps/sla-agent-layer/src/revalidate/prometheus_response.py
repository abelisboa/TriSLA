"""
Parsing defensivo de respostas Prometheus HTTP API (sla-agent revalidate path).

Cópia 1:1 de apps/portal-backend/src/utils/prometheus_response.py.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


def safe_extract_result(payload: Any) -> Optional[List[Any]]:
    if not isinstance(payload, dict):
        logger.debug(
            "[PROMETHEUS PARSE] result_type=%s (expected dict root)",
            type(payload).__name__,
        )
        return None
    data = payload.get("data")
    if not isinstance(data, dict):
        logger.debug(
            "[PROMETHEUS PARSE] result_type=%s (expected data dict)",
            type(data).__name__,
        )
        return None
    result = data.get("result")
    if not isinstance(result, list):
        logger.debug(
            "[PROMETHEUS PARSE] result_type=%s (expected list in data.result)",
            type(result).__name__,
        )
        return None
    return result
