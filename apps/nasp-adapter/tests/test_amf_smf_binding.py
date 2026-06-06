"""Tests for E2E-O2C AMF/SMF Binding."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

SAMPLE_AMF_LOG = """
2026-06-03T21:39:13Z [INFO][AMF][GMM][AMF_UE_NGAP_ID:1][SUPI:imsi-208930000000001] RequestedNssai - ServingSnssai: &{Sst:1 Sd:010203}
2026-06-03T21:54:19Z [INFO][AMF][GMM][AMF_UE_NGAP_ID:2][SUPI:imsi-208930000000001] Select SMF [snssai: {Sst:1 Sd:010203}, dnn: internet]
2026-06-03T21:54:19Z [INFO][AMF][GMM][AMF_UE_NGAP_ID:2][SUPI:imsi-208930000000001] create smContext[pduSessionID: 1] Success
"""

SAMPLE_SMF_LOG = """
2026-06-03T21:54:19Z [INFO][SMF][PduSess] Receive Create SM Context Request
2026-06-03T21:54:19Z [INFO][SMF][PduSess] UE[imsi-208930000000001] PDUSessionID[1] IP[10.1.0.1]
2026-06-03T21:54:19Z [INFO][SMF][CTX] Selected UPF: UPF
2026-06-03T21:54:19Z [INFO][SMF][GIN] | 201 | 10.233.102.145 | POST | /nsmf-pdusession/v1/sm-contexts |
"""

SSB_EMBB = {
    "sst": 1,
    "sd": "000002",
    "dnn": "embb",
    "smf_dnn_resolved": "internet",
    "smf_ref": "smf-nsmf.ns-1274485.svc.cluster.local:80",
    "binding_phase": "NSSF_SELECTED",
    "integration_flags": {"nssf_integrated": True, "amf_integrated": False, "smf_integrated": False},
}

NSSF_SEL = {"nsiId": "12", "selection_status": "SUCCESS"}


def test_amf_parser():
    from amf_binding_adapter import parse_amf_log_lines

    obs = parse_amf_log_lines(SAMPLE_AMF_LOG)
    assert obs is not None
    assert obs["serving_snssai"] == {"sst": 1, "sd": "010203"}
    assert obs["dnn_observed"] == "internet"
    assert obs["pdu_session_id"] == 1
    assert obs["supi_observed"] == "imsi-208930000000001"
    assert obs["sm_context_created"] is True


def test_smf_parser():
    from smf_binding_adapter import parse_smf_log_lines

    obs = parse_smf_log_lines(SAMPLE_SMF_LOG)
    assert obs is not None
    assert obs["pdu_session_id"] == 1
    assert obs["ue_ip"] == "10.1.0.1"
    assert obs["upf_node"] == "UPF"
    assert obs["supi"] == "imsi-208930000000001"


def test_correlation_context_split():
    from amf_binding_adapter import parse_amf_log_lines
    from smf_binding_adapter import parse_smf_log_lines
    from amf_smf_correlation import CORRELATION_CONTEXT_SPLIT, compute_correlation_status

    amf = parse_amf_log_lines(SAMPLE_AMF_LOG)
    smf = parse_smf_log_lines(SAMPLE_SMF_LOG)
    status = compute_correlation_status(
        slice_service_binding=SSB_EMBB,
        nssf_selection=NSSF_SEL,
        amf_obs=amf,
        smf_obs=smf,
    )
    assert status == CORRELATION_CONTEXT_SPLIT


def test_correlation_unknown_missing_smf():
    from amf_binding_adapter import parse_amf_log_lines
    from amf_smf_correlation import CORRELATION_UNKNOWN, compute_correlation_status

    amf = parse_amf_log_lines(SAMPLE_AMF_LOG)
    status = compute_correlation_status(
        slice_service_binding=SSB_EMBB,
        nssf_selection=NSSF_SEL,
        amf_obs=amf,
        smf_obs=None,
    )
    assert status == CORRELATION_UNKNOWN


def test_run_binding_full(monkeypatch):
    from amf_binding_adapter import BINDING_PHASE_AMF_OBSERVED
    from amf_smf_correlation import BINDING_PHASE_PDU_CORRELATED, CORRELATION_CONTEXT_SPLIT, run_amf_smf_binding

    monkeypatch.setenv("AMF_BINDING_ENABLED", "true")
    monkeypatch.setenv("SMF_BINDING_ENABLED", "true")

    result = run_amf_smf_binding(
        dict(SSB_EMBB),
        nssf_selection=NSSF_SEL,
        amf_log_text=SAMPLE_AMF_LOG,
        smf_log_text=SAMPLE_SMF_LOG,
    )
    assert result["skipped"] is False
    assert result["correlation_status"] == CORRELATION_CONTEXT_SPLIT
    assert result["binding"]["binding_phase"] == BINDING_PHASE_PDU_CORRELATED
    assert result["amf_binding_annotation"]
    assert result["smf_binding_annotation"]
    assert result["pdu_session_summary_annotation"]

    summary = json.loads(result["pdu_session_summary_annotation"])
    assert summary["session_id"] == "1"
    assert summary["ue_ip"] == "10.1.0.1"
    assert summary["orchestration_nsi_id"] == "12"
    assert summary["correlation_status"] == CORRELATION_CONTEXT_SPLIT


def test_amf_disabled_skips(monkeypatch):
    from amf_smf_correlation import run_amf_smf_binding

    monkeypatch.delenv("AMF_BINDING_ENABLED", raising=False)
    monkeypatch.delenv("SMF_BINDING_ENABLED", raising=False)
    os.environ.pop("AMF_BINDING_ENABLED", None)
    os.environ.pop("SMF_BINDING_ENABLED", None)

    result = run_amf_smf_binding(SSB_EMBB)
    assert result["skipped"] is True


def test_amf_only_observed(monkeypatch):
    from amf_smf_correlation import run_amf_smf_binding
    from amf_binding_adapter import BINDING_PHASE_AMF_OBSERVED

    monkeypatch.setenv("AMF_BINDING_ENABLED", "true")
    monkeypatch.setenv("SMF_BINDING_ENABLED", "false")

    result = run_amf_smf_binding(
        dict(SSB_EMBB),
        amf_log_text=SAMPLE_AMF_LOG,
        smf_log_text="",
    )
    assert result["amf_result"]["success"] is True
    assert result["binding"]["binding_phase"] == BINDING_PHASE_AMF_OBSERVED


def test_annotation_persistence_format():
    from amf_binding_adapter import build_amf_binding_annotation, parse_amf_binding_annotation, parse_amf_log_lines
    from amf_binding_adapter import amf_binding_annotation_value

    obs = parse_amf_log_lines(SAMPLE_AMF_LOG)
    ann = build_amf_binding_annotation(obs, slice_service_binding=SSB_EMBB, correlation_status="CONTEXT_SPLIT")
    raw = amf_binding_annotation_value(ann)
    parsed = parse_amf_binding_annotation(raw)
    assert parsed["contract_version"] == "1.0"
    assert parsed["binding_status"] == "OBSERVED"
    assert parsed["supi"] == "imsi-208930000000001"
    assert parsed["correlation_status"] == "CONTEXT_SPLIT"


def test_fallback_no_logs(monkeypatch):
    from amf_binding_adapter import observe_amf_binding

    monkeypatch.setenv("AMF_BINDING_ENABLED", "true")

    result = observe_amf_binding(SSB_EMBB, log_text="")
    assert result["success"] is False
    assert result["amf_binding_annotation"]
    failed = json.loads(result["amf_binding_annotation"])
    assert failed["binding_status"] == "FAILED"


def test_smf_default_off():
    from smf_binding_adapter import smf_binding_enabled

    old = os.environ.pop("SMF_BINDING_ENABLED", None)
    try:
        assert smf_binding_enabled() is False
    finally:
        if old is not None:
            os.environ["SMF_BINDING_ENABLED"] = old
