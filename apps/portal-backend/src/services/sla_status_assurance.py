"""Resolve runtime_assurance for GET /sla/status (Sprint 5M4)."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional
from urllib.parse import urlparse, urlunparse

import httpx


def _assurance_evaluate_url() -> Optional[str]:
    explicit = os.getenv("SLA_AGENT_RUNTIME_ASSURANCE_URL", "").strip()
    if explicit:
        return explicit
    pipeline = os.getenv("SLA_AGENT_PIPELINE_INGEST_URL", "").strip()
    if not pipeline:
        return None
    parsed = urlparse(pipeline)
    path = "/api/v1/runtime-assurance/evaluate"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def resolve_status_runtime_assurance(
    sem_result: Dict[str, Any],
    *,
    telemetry_snapshot: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Prefer SEM-persisted runtime_assurance; optional live evaluate via SLA-Agent."""
    md = sem_result.get("metadata")
    if isinstance(md, dict):
        ra = md.get("runtime_assurance")
        if isinstance(ra, dict) and ra.get("state"):
            return ra

    url = _assurance_evaluate_url()
    snap = telemetry_snapshot
    if not url or not isinstance(snap, dict) or not snap:
        return None

    sla_req = sem_result.get("sla_requirements")
    if not isinstance(sla_req, dict) and isinstance(md, dict):
        sla_req = md.get("sla_requirements")
    payload = {
        "intent_id": sem_result.get("intent_id"),
        "nest_id": sem_result.get("nest_id"),
        "telemetry_snapshot": snap,
        "sla_requirements": sla_req if isinstance(sla_req, dict) else None,
        "slice_type": sem_result.get("service_type") or (sla_req or {}).get("slice_type"),
        "reference_telemetry_snapshot": (
            md.get("telemetry_snapshot") if isinstance(md, dict) else None
        ),
    }
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            body = resp.json()
        ra = body.get("runtime_assurance")
        return ra if isinstance(ra, dict) else None
    except Exception:
        return None
