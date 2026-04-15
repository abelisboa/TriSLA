"""
Parsing defensivo de respostas Prometheus HTTP API (e estruturas compatíveis).
Evita iteração sobre `data.result` quando não é lista (ex.: bool em JSON malformado).
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


def safe_extract_result(payload: Any) -> Optional[List[Any]]:
    """
    Extrai `data.result` de uma resposta Prometheus API v1 (`/api/v1/query` ou `query_range`).

    Retorna lista de séries ou None se `result` não for lista (incl. bool, dict solto, etc.).
    """
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


def safe_first_vector_value(
    payload: Any,
) -> Optional[Any]:
    """
    Primeiro valor escalar de uma resposta instantânea (vector): result[0].value[1].
    """
    series_list = safe_extract_result(payload)
    if not series_list:
        return None
    first = series_list[0]
    if not isinstance(first, dict):
        return None
    val = first.get("value")
    if not isinstance(val, (list, tuple)) or len(val) < 2:
        return None
    return val[1]
