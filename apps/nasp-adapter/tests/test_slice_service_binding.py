"""Tests for slice service binding SSOT (O6)."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slice_service_binding import (
    BINDING_PHASE,
    enrich_nsi_spec,
    mapping_annotation_value,
    resolve_slice_service_binding,
    slice_service_binding_enabled,
)


def test_urllc_mapping():
    m = resolve_slice_service_binding(service_profile="URLLC", nsi_id="nest-test-1", nest_id="nest-test-1")
    assert m["sst"] == 1
    assert m["sd"] == "000001"
    assert m["dnn"] == "urllc"
    assert m["binding_phase"] == BINDING_PHASE
    assert m["integration_flags"]["nssf_integrated"] is False
    assert "nssf-nnssf" in (m["nssf_ref"] or "")


def test_embb_mapping():
    m = resolve_slice_service_binding(service_profile="eMBB", nsi_id="nsi-embb")
    assert m["sd"] == "000002"
    assert m["dnn"] == "embb"


def test_mmtc_mapping():
    m = resolve_slice_service_binding(service_profile="mMTC", nsi_id="nsi-mmtc")
    assert m["sd"] == "000003"
    assert m["dnn"] == "mmtc"


def test_enrich_nsi_spec_updates_nssai():
    spec = {
        "nsiId": "nest-abc",
        "nestId": "nest-abc",
        "serviceProfile": "URLLC",
        "tenantId": "demo",
        "nssai": {"sst": 99},
    }
    os.environ["SLICE_SERVICE_BINDING_ENABLED"] = "true"
    out = enrich_nsi_spec(spec)
    assert out["nssai"]["sst"] == 99
    assert out["nssai"]["sd"] == "000001"
    assert out["_sliceServiceBinding"]["dnn"] == "urllc"


def test_mapping_disabled_skips_enrichment(monkeypatch):
    monkeypatch.setenv("SLICE_SERVICE_BINDING_ENABLED", "false")
    spec = {"nsiId": "x", "serviceProfile": "URLLC", "nssai": {"sst": 1}}
    out = enrich_nsi_spec(dict(spec))
    assert "_sliceServiceBinding" not in out
    assert out["nssai"] == {"sst": 1}


def test_annotation_json_roundtrip():
    m = resolve_slice_service_binding(service_profile="URLLC", nsi_id="n1")
    raw = mapping_annotation_value(m)
    parsed = json.loads(raw)
    assert parsed["sd"] == "000001"


def test_mapping_enabled_default():
    os.environ.pop("SLICE_SERVICE_BINDING_ENABLED", None)
    os.environ.pop("E2E_5G_MAPPING_ENABLED", None)
    assert slice_service_binding_enabled() is True
