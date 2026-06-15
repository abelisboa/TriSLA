"""
Telemetry contract v2 (sla-agent revalidate path).

Cópia 1:1 de apps/portal-backend/src/telemetry/contract_v2.py.
Mantém canonicalização de aliases sem alterar valores numéricos.
"""

from __future__ import annotations

from typing import Any, Dict

TELEMETRY_UNITS_V2: Dict[str, str] = {
    "ran.prb_utilization": "%",
    "ran.latency": "ms",
    "ran.latency_ms": "ms",
    "transport.rtt": "ms",
    "transport.rtt_ms": "ms",
    "transport.jitter": "ms",
    "transport.jitter_ms": "ms",
    "transport.bandwidth_mbps": "Mbps",
    "transport.packet_loss_pct": "%",
    "transport.bandwidth": "Mbps",
    "transport.packet_loss": "%",
    "core.cpu": "legacy_aggregate",
    "core.cpu_utilization": "%",
    "core.memory": "bytes",
    "core.memory_bytes": "bytes",
    "core.availability_pct": "%",
    "core.availability": "%",
    "core.availability_proxy_kind": "metadata",
    "ran.reliability_pct": "%",
    "ran.reliability": "%",
    "ran.reliability_proxy_kind": "metadata",
}


def apply_telemetry_contract_v2(snapshot: Dict[str, Any]) -> None:
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
        if tr.get("bandwidth_mbps") is not None:
            tr["bandwidth"] = tr.get("bandwidth_mbps")
        if tr.get("packet_loss_pct") is not None:
            tr["packet_loss"] = tr.get("packet_loss_pct")
    if isinstance(co, dict):
        co["cpu_utilization"] = co.get("cpu")
        co["memory_bytes"] = co.get("memory")
        if co.get("availability_pct") is not None:
            co["availability"] = co.get("availability_pct")
            co["availability_proxy_kind"] = "OPERATIONAL_AVAILABILITY_PROXY"
        if ran.get("reliability_pct") is not None:
            ran["reliability"] = ran.get("reliability_pct")
            ran["reliability_proxy_kind"] = "TRANSPORT_DELIVERY_RELIABILITY_PROXY"
