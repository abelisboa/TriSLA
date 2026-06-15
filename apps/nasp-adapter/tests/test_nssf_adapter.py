"""Tests for E2E-O1C NSSF Adapter."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nssf_adapter import (
    BINDING_PHASE_METADATA,
    BINDING_PHASE_NSSF_SELECTED,
    build_pdu_session_query_payload,
    build_selection_url,
    nssf_adapter_enabled,
    parse_nssf_response,
    sd_trisla_to_nssf,
    select_nssf_slice,
    resolve_smf_dnn,
)


def test_sd_transform_urllc():
    assert sd_trisla_to_nssf(sd_trisla="000001", slice_type="URLLC") == "1"


def test_sd_transform_embb():
    assert sd_trisla_to_nssf(sd_trisla="000002", slice_type="eMBB") == "2"


def test_sd_transform_mmtc():
    assert sd_trisla_to_nssf(sd_trisla="000003", slice_type="mMTC") == "3"


def test_sd_000001_not_passed_through():
    assert sd_trisla_to_nssf(sd_trisla="000001", slice_type="URLLC") != "000001"


def test_dnn_map():
    assert resolve_smf_dnn("urllc") == "internet"
    assert resolve_smf_dnn("embb") == "internet"


def test_pdu_payload_builder():
    cfg = {"nssf": {"roaming_indication": "NON_ROAMING"}}
    p = build_pdu_session_query_payload(1, "1", cfg)
    assert p["sNssai"] == {"sst": 1, "sd": "1"}
    assert p["roamingIndication"] == "NON_ROAMING"


def test_selection_url_format():
    cfg = {"nssf": {"selection_path": "/nnssf-nsselection/v1/network-slice-information"}}
    url = build_selection_url(
        base_url="http://nssf-nnssf:80",
        nf_type="AMF",
        nf_id="abc-123",
        pdu_payload={"sNssai": {"sst": 1, "sd": "1"}, "roamingIndication": "NON_ROAMING"},
        cfg=cfg,
    )
    assert "/nnssf-nsselection/v1/network-slice-information" in url
    assert "nf-type=AMF" in url
    assert "nf-id=abc-123" in url
    assert "slice-info-request-for-pdu-session=" in url


def test_parse_success():
    r = parse_nssf_response({"nsiInformation": {"nsiId": "11", "nrfId": "http://nrf/"}}, 200)
    assert r["selection_status"] == "SUCCESS"
    assert r["nsiInformation"]["nsiId"] == "11"


def test_parse_empty_no_match():
    r = parse_nssf_response({}, 200)
    assert r["selection_status"] == "FAILED"
    assert r.get("error") == "NO_MATCH"


def test_parse_404():
    r = parse_nssf_response("not found", 404)
    assert r["selection_status"] == "FAILED"


def test_adapter_disabled_skips(monkeypatch):
    monkeypatch.setenv("NSSF_ADAPTER_ENABLED", "false")
    binding = {"sst": 1, "sd": "000001", "slice_type": "URLLC"}
    out = select_nssf_slice(binding)
    assert out["skipped"] is True
    assert out["binding"]["sd"] == "000001"


def test_adapter_enabled_mock_success(monkeypatch):
    monkeypatch.setenv("NSSF_ADAPTER_ENABLED", "true")
    monkeypatch.setenv("NSSF_AMF_NF_ID", "test-amf-nf-id")

    class FakeResp:
        status_code = 200

        def json(self):
            return {"nsiInformation": {"nsiId": "11", "nrfId": "http://nrf-nnrf:8000/"}}

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, url):
            return FakeResp()

    import nssf_adapter as mod

    monkeypatch.setattr(mod.httpx, "Client", FakeClient)
    binding = {
        "sst": 1,
        "sd": "000001",
        "dnn": "urllc",
        "slice_type": "URLLC",
        "nssf_ref": "http://nssf-nnssf:80",
        "integration_flags": {},
    }
    out = select_nssf_slice(binding, force_refresh=True)
    assert out["binding"]["binding_phase"] == BINDING_PHASE_NSSF_SELECTED
    assert out["binding"]["integration_flags"]["nssf_integrated"] is True
    ann = json.loads(out["nssf_selection_annotation"])
    assert ann["selection_status"] == "SUCCESS"
    assert ann["nsiId"] == "11"


def test_adapter_fallback_on_timeout(monkeypatch):
    monkeypatch.setenv("NSSF_ADAPTER_ENABLED", "true")
    monkeypatch.setenv("NSSF_AMF_NF_ID", "test-amf-nf-id")

    import httpx
    import nssf_adapter as mod

    def raise_timeout(*a, **k):
        raise httpx.TimeoutException("timeout")

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        get = raise_timeout

    monkeypatch.setattr(mod.httpx, "Client", FakeClient)
    binding = {"sst": 1, "sd": "000001", "slice_type": "URLLC", "nssf_ref": "http://nssf:80", "integration_flags": {}}
    out = select_nssf_slice(binding, force_refresh=True)
    assert out["binding"]["binding_phase"] == BINDING_PHASE_METADATA
    ann = json.loads(out["nssf_selection_annotation"])
    assert ann["selection_status"] == "FAILED"


def test_nssf_adapter_default_off():
    os.environ.pop("NSSF_ADAPTER_ENABLED", None)
    assert nssf_adapter_enabled() is False
