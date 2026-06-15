"""
NASP connectivity SSOT — Sprint 8G (POST-S8F).

Maps NASP client targets to live Free5GC (ns-1274485) SBI services and defines
reachability probes. Does not implement pdu_fail_rate or 3GPP PM.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

# Live 5GC stack on this cluster (Sprint 8F inventory).
FREE5GC_NAMESPACE = os.getenv("NASP_FREE5GC_NAMESPACE", "ns-1274485")

DEFAULT_ENDPOINTS: Dict[str, str] = {
    "NASP_CORE_AMF_ENDPOINT": f"http://amf-namf.{FREE5GC_NAMESPACE}.svc.cluster.local:80",
    "NASP_CORE_SMF_ENDPOINT": f"http://smf-nsmf.{FREE5GC_NAMESPACE}.svc.cluster.local:80",
    "NASP_CORE_NRF_ENDPOINT": f"http://nrf-nnrf.{FREE5GC_NAMESPACE}.svc.cluster.local:8000",
    # TriSLA lab RAN observability (replaces scaled-down srsenb).
    "NASP_RAN_METRICS_ENDPOINT": (
        "http://trisla-ran-ue-upf-proxy.trisla.svc.cluster.local:9102"
    ),
    "NASP_RAN_ENDPOINT": (
        "http://trisla-ran-ue-upf-proxy.trisla.svc.cluster.local:9102"
    ),
    # Transport anchor: SMF SBI (replaces dead open5gs-upf.open5gs).
    "NASP_TRANSPORT_ENDPOINT": f"http://smf-nsmf.{FREE5GC_NAMESPACE}.svc.cluster.local:80",
    "NASP_CORE_ENDPOINT": f"http://amf-namf.{FREE5GC_NAMESPACE}.svc.cluster.local:80",
}


def resolve_endpoint(env_key: str, default_map: Optional[Dict[str, str]] = None) -> str:
    defaults = default_map or DEFAULT_ENDPOINTS
    return os.getenv(env_key, defaults.get(env_key, ""))


def sbi_reachable_status_codes(status_code: int) -> bool:
    """HTTP response from SBI means TCP+HTTP connectivity (incl. 404 on /metrics)."""
    return status_code < 500


async def probe_http_reachable(
    client: Any,
    base_url: str,
    path: str = "/",
    timeout: float = 5.0,
) -> Tuple[bool, Optional[int]]:
    url = f"{base_url.rstrip('/')}{path}"
    try:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
        return sbi_reachable_status_codes(response.status_code), response.status_code
    except Exception:
        return False, None
