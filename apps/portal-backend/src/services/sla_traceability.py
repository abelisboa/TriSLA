"""Extract distributed traceability for status API (Sprint M3)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.observability.distributed_trace import build_distributed_traceability, trace_from_metadata


def build_traceability_summary(sem_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    metadata = sem_result.get("metadata") if isinstance(sem_result.get("metadata"), dict) else {}
    root = trace_from_metadata(metadata)
    if not root:
        return None
    block = metadata.get("distributed_traceability")
    if isinstance(block, dict) and block.get("correlation_chain"):
        return block
    hops = metadata.get("distributed_trace_hops")
    if isinstance(hops, list):
        return build_distributed_traceability(root, hops)
    return build_distributed_traceability(root, [root])
