"""
Transport Delivery Reliability Proxy — Sprint 8D (POST-S8C).

Not 3GPP PDU Session Establishment Success Rate. Derived from measured
transport packet_loss_pct: reliability_pct = 100 - packet_loss_pct.
"""

from __future__ import annotations

RELIABILITY_PROXY_KIND = "TRANSPORT_DELIVERY_RELIABILITY_PROXY"
RELIABILITY_PROXY_VERSION = "8D"

RELIABILITY_PROXY_NOTE = (
    "Transport Delivery Reliability Proxy: ran.reliability_pct = 100 minus "
    "transport.packet_loss_pct (container network drop ratio in ns-1274485). "
    "Not AMF/SMF PDU success, registration success, or GSMA contractual reliability."
)


def reliability_pct_from_packet_loss(packet_loss_pct: float) -> float:
    """Clamp to [0, 100] per Sprint 8D formula."""
    return max(0.0, min(100.0, 100.0 - float(packet_loss_pct)))
