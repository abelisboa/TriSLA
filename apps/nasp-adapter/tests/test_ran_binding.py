"""Tests for E2E-O4C RAN Binding."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

SAMPLE_AMF_LOG = """
2026-06-03T21:50:00Z [AMF] SCTP Accept from: 10.233.75.7:53845
2026-06-03T21:50:01Z [NGAP] Handle NG Setup request
2026-06-03T21:50:01Z [NGAP] NG Setup procedure is successful
2026-06-03T21:50:02Z [NGAP] Add RAN Context[ID: PlmnID: {Mcc:208 Mnc:93}, GNbID: 00000001]
2026-06-03T21:50:05Z [NGAP][10.233.75.7:53845][AMF_UE_NGAP_ID:3] Uplink NAS Transport (RAN UE NGAP ID: 1)
2026-06-03T21:50:05Z [GMM][AMF_UE_NGAP_ID:3][SUPI:imsi-208930000000001] Handle InitialRegistration
2026-06-03T21:50:06Z [GMM][AMF_UE_NGAP_ID:3][SUPI:imsi-208930000000001] ServingSnssai: &{Sst:1 Sd:010203}
2026-06-03T21:50:07Z [GMM][AMF_UE_NGAP_ID:3][SUPI:imsi-208930000000001] Select SMF [snssai: {Sst:1 Sd:010203}, dnn: internet]
2026-06-03T21:50:08Z [GMM][AMF_UE_NGAP_ID:3][SUPI:imsi-208930000000001] create smContext[pduSessionID: 1] Success
"""

SAMPLE_GNB_HEALTHY = """
2026-06-03T21:50:01Z [ngap] NG Setup procedure is successful
"""

SAMPLE_GNB_DEGRADED = """
2026-06-03T21:55:00Z [ngap] SCTP_COMM_LOST Association terminated for AMF
"""

SAMPLE_SMF_BINDING = {
    "session_id": "1",
    "ue_ip": "10.1.0.1",
    "selected_upf": "UPF",
    "upf_n4_addr": "10.233.75.38",
    "dnn": "internet",
    "supi": "imsi-208930000000001",
    "correlation_status": "CONTEXT_SPLIT",
}

SAMPLE_AMF_BINDING = {
    "supi": "imsi-208930000000001",
    "correlation_status": "CONTEXT_SPLIT",
}

SAMPLE_UPF_BINDING = {
    "ue_ip_observed": "10.1.0.1",
    "upf_gtpu_addr": "10.233.75.38",
    "correlation_status": "CONTEXT_SPLIT",
}

SSB_USER_PLANE = {
    "sst": 1,
    "sd": "010203",
    "binding_phase": "USER_PLANE_CORRELATED",
    "correlation_status": "CONTEXT_SPLIT",
    "integration_flags": {
        "nssf_integrated": True,
        "amf_integrated": True,
        "smf_integrated": True,
        "upf_integrated": True,
        "ran_integrated": False,
    },
}


def test_amf_ngap_parser():
    from ran_binding_adapter import parse_amf_ran_log_lines

    obs = parse_amf_ran_log_lines(SAMPLE_AMF_LOG, target_supi="imsi-208930000000001")
    assert obs is not None
    assert obs["gnb_id"] == "00000001"
    assert obs["ran_ue_ngap_id"] == 1
    assert obs["amf_ue_ngap_id"] == 3
    assert obs["supi"] == "imsi-208930000000001"
    assert obs["dnn"] == "internet"
    assert obs["session_id"] == 1
    assert obs["serving_snssai"]["sst"] == 1
    assert obs["ng_setup_observed"] is True


def test_gnb_health_healthy():
    from ran_binding_adapter import NG_HEALTH_HEALTHY, parse_gnb_health_log

    assert parse_gnb_health_log(SAMPLE_GNB_HEALTHY) == NG_HEALTH_HEALTHY


def test_gnb_health_degraded():
    from ran_binding_adapter import NG_HEALTH_DEGRADED, parse_gnb_health_log

    assert parse_gnb_health_log(SAMPLE_GNB_DEGRADED) == NG_HEALTH_DEGRADED


def test_ran_only_observed(monkeypatch):
    from ran_binding_adapter import BINDING_PHASE_RAN_OBSERVED
    from ran_correlation import run_ran_access_binding

    monkeypatch.setenv("RAN_BINDING_ENABLED", "true")

    ssb = {"binding_phase": "SMF_OBSERVED", "integration_flags": {"smf_integrated": True}}
    result = run_ran_access_binding(
        ssb,
        amf_log_text=SAMPLE_AMF_LOG,
        gnb_log_text=SAMPLE_GNB_HEALTHY,
    )
    assert result["skipped"] is False
    assert result["binding"]["binding_phase"] == BINDING_PHASE_RAN_OBSERVED
    assert result["access_correlated"] is False


def test_access_correlated(monkeypatch):
    from ran_correlation import BINDING_PHASE_ACCESS_CORRELATED, run_ran_access_binding

    monkeypatch.setenv("RAN_BINDING_ENABLED", "true")

    result = run_ran_access_binding(
        dict(SSB_USER_PLANE),
        amf_binding=SAMPLE_AMF_BINDING,
        smf_binding=SAMPLE_SMF_BINDING,
        upf_binding=SAMPLE_UPF_BINDING,
        pdu_session_summary={
            "session_id": "1",
            "ue_ip": "10.1.0.1",
            "correlation_status": "CONTEXT_SPLIT",
        },
        amf_log_text=SAMPLE_AMF_LOG,
        gnb_log_text=SAMPLE_GNB_HEALTHY,
    )
    assert result["skipped"] is False
    assert result["binding"]["binding_phase"] == BINDING_PHASE_ACCESS_CORRELATED
    assert result["access_correlated"] is True
    assert result["ran_binding_annotation"]
    assert result["pdu_session_summary_annotation"]

    summary = json.loads(result["pdu_session_summary_annotation"])
    assert summary["gnb_id"] == "00000001"
    assert summary["ran_ue_ngap_id"] == 1
    assert summary["amf_ue_ngap_id"] == 3
    assert summary["access_correlated"] is True
    assert summary["fresh_ue_ip"] == "10.1.0.1"


def test_ran_disabled_skips(monkeypatch):
    from ran_correlation import run_ran_access_binding

    monkeypatch.delenv("RAN_BINDING_ENABLED", raising=False)
    os.environ.pop("RAN_BINDING_ENABLED", None)

    result = run_ran_access_binding(SSB_USER_PLANE, amf_log_text=SAMPLE_AMF_LOG)
    assert result["skipped"] is True


def test_ran_default_off():
    from ran_binding_adapter import ran_binding_enabled

    old = os.environ.pop("RAN_BINDING_ENABLED", None)
    try:
        assert ran_binding_enabled() is False
    finally:
        if old is not None:
            os.environ["RAN_BINDING_ENABLED"] = old


def test_annotation_format(monkeypatch):
    from ran_binding_adapter import (
        build_ran_binding_annotation,
        parse_amf_ran_log_lines,
        parse_ran_binding_annotation,
        ran_binding_annotation_value,
    )

    obs = parse_amf_ran_log_lines(SAMPLE_AMF_LOG, target_supi="imsi-208930000000001")
    ann = build_ran_binding_annotation(obs, correlation_status="CONTEXT_SPLIT")
    raw = ran_binding_annotation_value(ann)
    parsed = parse_ran_binding_annotation(raw)
    assert parsed["contract_version"] == "RAN_CONTRACT_SSOT_V1"
    assert parsed["binding_status"] == "OBSERVED"
    assert parsed["gnb_id"] == "00000001"
    assert parsed["freshness_source"] == "amf"


def test_fallback_no_logs(monkeypatch):
    from ran_binding_adapter import observe_ran_binding

    monkeypatch.setenv("RAN_BINDING_ENABLED", "true")

    result = observe_ran_binding(SSB_USER_PLANE, amf_log_text="")
    assert result["success"] is False
    failed = json.loads(result["ran_binding_annotation"])
    assert failed["binding_status"] == "FAILED"


def test_join_keys_mismatch_blocks_correlation(monkeypatch):
    from ran_correlation import run_ran_access_binding

    monkeypatch.setenv("RAN_BINDING_ENABLED", "true")

    bad_smf = dict(SAMPLE_SMF_BINDING)
    bad_smf["supi"] = "imsi-999999999999999"

    result = run_ran_access_binding(
        dict(SSB_USER_PLANE),
        amf_binding=SAMPLE_AMF_BINDING,
        smf_binding=bad_smf,
        upf_binding=SAMPLE_UPF_BINDING,
        amf_log_text=SAMPLE_AMF_LOG,
    )
    assert result["access_correlated"] is False


def test_observe_endpoint_imports():
    """Smoke: endpoint helpers import without cluster."""
    from ran_binding_adapter import observe_ran_binding, parse_ran_binding_annotation

    old = os.environ.get("RAN_BINDING_ENABLED")
    os.environ["RAN_BINDING_ENABLED"] = "true"
    try:
        result = observe_ran_binding(
            SSB_USER_PLANE,
            amf_log_text=SAMPLE_AMF_LOG,
            gnb_log_text=SAMPLE_GNB_HEALTHY,
            correlation_status="CONTEXT_SPLIT",
        )
        ann = parse_ran_binding_annotation(result["ran_binding_annotation"])
        assert ann["gnb_id"] == "00000001"
    finally:
        if old is None:
            os.environ.pop("RAN_BINDING_ENABLED", None)
        else:
            os.environ["RAN_BINDING_ENABLED"] = old
