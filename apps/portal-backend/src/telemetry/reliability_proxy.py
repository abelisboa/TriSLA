"""Transport Delivery Reliability Proxy — Sprint 8D (portal collector mirror)."""

from __future__ import annotations

RELIABILITY_PROXY_KIND = "TRANSPORT_DELIVERY_RELIABILITY_PROXY"


def reliability_pct_from_packet_loss(packet_loss_pct: float) -> float:
    return max(0.0, min(100.0, 100.0 - float(packet_loss_pct)))
