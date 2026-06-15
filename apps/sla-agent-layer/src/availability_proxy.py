"""
Operational Availability Proxy — Sprint 8B (POST-S8A).

Not 3GPP NF service availability. Combines blackbox probe reachability (primary)
with TriSLA deployment Available conditions (secondary) into availability_pct.
"""

from __future__ import annotations

AVAILABILITY_PROXY_KIND = "OPERATIONAL_AVAILABILITY_PROXY"
AVAILABILITY_PROXY_VERSION = "8B"

AVAILABILITY_PROXY_NOTE = (
    "Operational Availability Proxy: weighted combination of TriSLA blackbox probe_success "
    "and kube Deployment Available status in namespace trisla. Not GSMA/GST contractual "
    "availability or Open5GC NF PM."
)
