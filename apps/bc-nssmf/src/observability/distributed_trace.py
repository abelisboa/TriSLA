"""Distributed trace context (Sprint M3 — W3C-compatible, no OTEL dependency)."""
from __future__ import annotations

import secrets
from typing import Any, Dict, List, Optional

TRACE_KEYS = ("trace_id", "span_id", "parent_span_id")


def new_root_trace(service: str = "portal-backend") -> Dict[str, Any]:
    return {
        "trace_id": secrets.token_hex(16),
        "span_id": secrets.token_hex(8),
        "parent_span_id": None,
        "service": service,
    }


def child_trace(parent: Optional[Dict[str, Any]], service: str) -> Dict[str, Any]:
    parent = parent or {}
    trace_id = parent.get("trace_id")
    if not trace_id:
        return new_root_trace(service)
    return {
        "trace_id": str(trace_id),
        "span_id": secrets.token_hex(8),
        "parent_span_id": parent.get("span_id"),
        "service": service,
    }


def build_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def parse_traceparent(value: str) -> Optional[Dict[str, str]]:
    if not value or not isinstance(value, str):
        return None
    parts = value.strip().split("-")
    if len(parts) != 4 or parts[0] != "00":
        return None
    trace_id, span_id = parts[1], parts[2]
    if len(trace_id) != 32 or len(span_id) != 16:
        return None
    return {"trace_id": trace_id, "span_id": span_id, "parent_span_id": None}


def trace_from_carrier(carrier: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not carrier:
        return None
    tp = carrier.get("traceparent") or carrier.get("Traceparent")
    if isinstance(tp, str):
        parsed = parse_traceparent(tp)
        if parsed:
            return parsed
    trace_id = carrier.get("trace_id")
    span_id = carrier.get("span_id")
    if trace_id and span_id:
        return {
            "trace_id": str(trace_id),
            "span_id": str(span_id),
            "parent_span_id": carrier.get("parent_span_id"),
        }
    return None


def trace_from_metadata(metadata: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(metadata, dict):
        return None
    trace_id = metadata.get("trace_id")
    span_id = metadata.get("span_id")
    if not trace_id or not span_id:
        block = metadata.get("distributed_traceability")
        if isinstance(block, dict):
            trace_id = block.get("trace_id")
            span_id = block.get("span_id")
    if trace_id and span_id:
        return {
            "trace_id": str(trace_id),
            "span_id": str(span_id),
            "parent_span_id": metadata.get("parent_span_id")
            or (metadata.get("distributed_traceability") or {}).get("parent_span_id"),
            "service": metadata.get("trace_service"),
        }
    return None


def merge_trace_into_metadata(metadata: Optional[Dict[str, Any]], trace: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(metadata or {})
    out["trace_id"] = trace.get("trace_id")
    out["span_id"] = trace.get("span_id")
    if trace.get("parent_span_id") is not None:
        out["parent_span_id"] = trace.get("parent_span_id")
    if trace.get("service"):
        out["trace_service"] = trace.get("service")
    return out


def inject_http_headers(headers: Optional[Dict[str, str]], trace: Dict[str, Any]) -> Dict[str, str]:
    out = dict(headers or {})
    trace_id = trace.get("trace_id")
    span_id = trace.get("span_id")
    if trace_id and span_id:
        out["traceparent"] = build_traceparent(str(trace_id), str(span_id))
        out["X-Trace-Id"] = str(trace_id)
        out["X-Span-Id"] = str(span_id)
        if trace.get("parent_span_id"):
            out["X-Parent-Span-Id"] = str(trace.get("parent_span_id"))
    return out


def build_correlation_chain(hops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    chain: List[Dict[str, Any]] = []
    for hop in hops:
        if not hop.get("trace_id"):
            continue
        chain.append(
            {
                "service": hop.get("service"),
                "trace_id": hop.get("trace_id"),
                "span_id": hop.get("span_id"),
                "parent_span_id": hop.get("parent_span_id"),
            }
        )
    return chain


def build_distributed_traceability(
    root: Dict[str, Any],
    hops: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    all_hops = list(hops or [])
    if root.get("trace_id") and not any(h.get("trace_id") == root.get("trace_id") for h in all_hops):
        all_hops.insert(0, root)
    chain = build_correlation_chain(all_hops)
    unique_trace_ids = {h["trace_id"] for h in chain if h.get("trace_id")}
    return {
        "trace_id": root.get("trace_id"),
        "span_id": root.get("span_id"),
        "parent_span_id": root.get("parent_span_id"),
        "correlation_chain": chain,
        "hop_count": len(chain),
        "end_to_end": len(unique_trace_ids) <= 1 and bool(root.get("trace_id")),
    }
