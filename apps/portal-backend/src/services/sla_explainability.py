"""Explainability contract passthrough — portal view only (RC-P20-04A)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def flatten_metric_explainability(
    domain_explainability: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Assemble metric_explainability[] from domain_explainability (no score recomputation)."""
    if not isinstance(domain_explainability, dict):
        return []
    flat: List[Dict[str, Any]] = []
    for domain in ("ran", "transport", "core"):
        rows = domain_explainability.get(domain)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            flat.append({**row, "domain": domain})
    return flat


def enrich_runtime_assurance_explainability(
    runtime_assurance: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Recover top-level metric_explainability from domain_explainability when absent.
    SLA-Agent generates nested metric_explainability per domain; portal status API
    historically exposed only domain_explainability (flattened view).
    """
    if not isinstance(runtime_assurance, dict):
        return runtime_assurance
    merged = dict(runtime_assurance)
    if merged.get("metric_explainability"):
        return merged
    de = merged.get("domain_explainability")
    flat = flatten_metric_explainability(de if isinstance(de, dict) else None)
    if flat:
        merged["metric_explainability"] = flat
    return merged
