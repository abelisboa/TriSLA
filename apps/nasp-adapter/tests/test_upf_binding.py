"""Tests for E2E-O3C UPF Binding."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

SAMPLE_UPF_LOG = """
2026-06-03T21:54:18Z [INFO][UPF][Util] [PFCP] Handle PFCP session establishment request
2026-06-03T21:54:18Z [DEBU][UPF][Util] F-TEID IPv4: 10.233.75.38
2026-06-03T21:54:18Z [DEBU][UPF][Util] UE IP Address IPv4: 10.1.0.1
2026-06-03T21:54:18Z [DEBU][UPF][Util] gtp5g get gtpu ip: 10.233.75.38
2026-06-03T21:54:18Z [DEBU][UPF][Util] gtp5g get teid: 16777216
2026-06-05T19:58:09Z [INFO][UPF][Util] [PFCP] Handle PFCP session deletion request
2026-06-05T19:58:09Z [INFO][UPF][Util] [PFCP] Handle PFCP session establishment request
2026-06-05T19:58:09Z [DEBU][UPF][Util] UE IP Address IPv4: 10.1.0.2
2026-06-05T19:58:09Z [DEBU][UPF][Util] gtp5g get gtpu ip: 10.233.75.38
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

SSB_PDU = {
    "sst": 1,
    "sd": "000002",
    "binding_phase": "PDU_CORRELATED",
    "correlation_status": "CONTEXT_SPLIT",
    "integration_flags": {
        "nssf_integrated": True,
        "amf_integrated": True,
        "smf_integrated": True,
        "upf_integrated": False,
    },
}


def test_upf_parser_fresh_ue_ip():
    from upf_binding_adapter import parse_upf_log_lines

    obs = parse_upf_log_lines(SAMPLE_UPF_LOG)
    assert obs is not None
    assert obs["ue_ip_observed"] == "10.1.0.2"
    assert obs["upf_gtpu_addr"] == "10.233.75.38"
    assert obs["pfcp_session_established"] is True
    assert obs["session_state"] == "ACTIVE"
    assert obs["gtpu_teid"] == "16777216"


def test_pfcp_deletion_only():
    from upf_binding_adapter import parse_upf_log_lines

    log = "2026-06-05T19:58:09Z [INFO][UPF][Util] [PFCP] Handle PFCP session deletion request\n"
    obs = parse_upf_log_lines(log)
    assert obs is not None
    assert obs["session_state"] == "RELEASED"


def test_freshness_upf_wins_over_smf():
    from upf_binding_adapter import parse_upf_log_lines
    from upf_correlation import _pick_ue_ip

    upf = parse_upf_log_lines(SAMPLE_UPF_LOG)
    ue, source = _pick_ue_ip(
        upf_obs=upf,
        smf_binding=SAMPLE_SMF_BINDING,
        amf_binding=None,
        prior_ue_ip="10.1.0.1",
        cfg={"freshness": {"ue_ip_source_priority": ["upf", "smf", "amf"]}},
    )
    assert ue == "10.1.0.2"
    assert source == "upf"


def test_user_plane_correlated(monkeypatch):
    from upf_correlation import BINDING_PHASE_USER_PLANE_CORRELATED, run_upf_user_plane_binding

    monkeypatch.setenv("UPF_BINDING_ENABLED", "true")

    result = run_upf_user_plane_binding(
        dict(SSB_PDU),
        smf_binding=SAMPLE_SMF_BINDING,
        amf_binding={"supi": "imsi-208930000000001"},
        pdu_session_summary={"session_id": "1", "ue_ip": "10.1.0.1", "correlation_status": "CONTEXT_SPLIT"},
        upf_log_text=SAMPLE_UPF_LOG,
    )
    assert result["skipped"] is False
    assert result["binding"]["binding_phase"] == BINDING_PHASE_USER_PLANE_CORRELATED
    assert result["fresh_ue_ip"] == "10.1.0.2"
    assert result["freshness_source"] == "upf"
    assert result["upf_binding_annotation"]
    assert result["pdu_session_summary_annotation"]

    summary = json.loads(result["pdu_session_summary_annotation"])
    assert summary["fresh_ue_ip"] == "10.1.0.2"
    assert summary["upf_gtpu_addr"] == "10.233.75.38"
    assert summary["session_state"] == "ACTIVE"
    assert summary["pfcp_observed"] is True


def test_upf_only_observed(monkeypatch):
    from upf_binding_adapter import BINDING_PHASE_UPF_OBSERVED
    from upf_correlation import run_upf_user_plane_binding

    monkeypatch.setenv("UPF_BINDING_ENABLED", "true")

    ssb = {"binding_phase": "SMF_OBSERVED", "integration_flags": {"smf_integrated": True}}
    result = run_upf_user_plane_binding(
        ssb,
        smf_binding=SAMPLE_SMF_BINDING,
        upf_log_text=SAMPLE_UPF_LOG,
    )
    assert result["binding"]["binding_phase"] == BINDING_PHASE_UPF_OBSERVED


def test_upf_disabled_skips(monkeypatch):
    from upf_correlation import run_upf_user_plane_binding

    monkeypatch.delenv("UPF_BINDING_ENABLED", raising=False)
    os.environ.pop("UPF_BINDING_ENABLED", None)

    result = run_upf_user_plane_binding(SSB_PDU, upf_log_text=SAMPLE_UPF_LOG)
    assert result["skipped"] is True


def test_upf_default_off():
    from upf_binding_adapter import upf_binding_enabled

    old = os.environ.pop("UPF_BINDING_ENABLED", None)
    try:
        assert upf_binding_enabled() is False
    finally:
        if old is not None:
            os.environ["UPF_BINDING_ENABLED"] = old


def test_annotation_format(monkeypatch):
    from upf_binding_adapter import (
        build_upf_binding_annotation,
        parse_upf_binding_annotation,
        parse_upf_log_lines,
        upf_binding_annotation_value,
    )

    obs = parse_upf_log_lines(SAMPLE_UPF_LOG)
    ann = build_upf_binding_annotation(obs, correlation_status="CONTEXT_SPLIT", session_id="1")
    raw = upf_binding_annotation_value(ann)
    parsed = parse_upf_binding_annotation(raw)
    assert parsed["contract_version"] == "UPF_CONTRACT_SSOT_V1"
    assert parsed["binding_status"] == "OBSERVED"
    assert parsed["upf_node_name"] == "UPF"
    assert parsed["freshness_source"] == "upf"


def test_fallback_no_logs(monkeypatch):
    from upf_binding_adapter import observe_upf_binding

    monkeypatch.setenv("UPF_BINDING_ENABLED", "true")

    result = observe_upf_binding(SSB_PDU, log_text="")
    assert result["success"] is False
    failed = json.loads(result["upf_binding_annotation"])
    assert failed["binding_status"] == "FAILED"


def test_sanitize_upf_name():
    from upf_correlation import _sanitize_upf_name

    assert _sanitize_upf_name("UPF\n2026-06-03T21:54:19Z") == "UPF"
