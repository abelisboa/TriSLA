"""
Telemetry contract v2 (PR-01 / PROMPT_39).

Adds canonical field aliases alongside legacy keys — same numeric values, no renaming.
Units are documented in TELEMETRY_UNITS_V2 (reference); normalization deferred (SLA V2).
"""

from __future__ import annotations

from typing import Any, Dict

# Reference only — values in snapshot are unchanged; consumers may use for display.
TELEMETRY_UNITS_V2: Dict[str, str] = {
    "ran.prb_utilization": "%",
    "ran.latency": "ms",
    "ran.latency_ms": "ms",
    "transport.rtt": "ms",
    "transport.rtt_ms": "ms",
    "transport.jitter": "ms",
    "transport.jitter_ms": "ms",
    "core.cpu": "legacy_aggregate",
    "core.cpu_utilization": "%",
    "core.memory": "bytes",
    "core.memory_bytes": "bytes",
}


def apply_telemetry_contract_v2(snapshot: Dict[str, Any]) -> None:
    """
    Mutates snapshot in place: sets telemetry_contract_version and duplicate keys
    (latency_ms, rtt_ms, jitter_ms, cpu_utilization, memory_bytes) mirroring legacy fields.
    """
    if not isinstance(snapshot, dict):
        return
    snapshot["telemetry_contract_version"] = "v2"
    ran = snapshot.setdefault("ran", {})
    tr = snapshot.setdefault("transport", {})
    co = snapshot.setdefault("core", {})
    if isinstance(ran, dict):
        ran["latency_ms"] = ran.get("latency")
    if isinstance(tr, dict):
        tr["rtt_ms"] = tr.get("rtt")
        tr["jitter_ms"] = tr.get("jitter")
    if isinstance(co, dict):
        co["cpu_utilization"] = co.get("cpu")
        co["memory_bytes"] = co.get("memory")
