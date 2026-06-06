"""Sprint 8G — NASP connectivity unit tests."""
from __future__ import annotations

from nasp_connectivity import DEFAULT_ENDPOINTS, sbi_reachable_status_codes


def test_default_endpoints_point_to_free5gc():
    assert "ns-1274485" in DEFAULT_ENDPOINTS["NASP_CORE_AMF_ENDPOINT"]
    assert "amf-namf" in DEFAULT_ENDPOINTS["NASP_CORE_AMF_ENDPOINT"]
    assert "smf-nsmf" in DEFAULT_ENDPOINTS["NASP_CORE_SMF_ENDPOINT"]
    assert "open5gs-upf" not in DEFAULT_ENDPOINTS["NASP_TRANSPORT_ENDPOINT"]
    assert "srsenb" not in DEFAULT_ENDPOINTS["NASP_RAN_METRICS_ENDPOINT"]


def test_sbi_reachable_accepts_404():
    assert sbi_reachable_status_codes(404) is True
    assert sbi_reachable_status_codes(200) is True
    assert sbi_reachable_status_codes(503) is False
