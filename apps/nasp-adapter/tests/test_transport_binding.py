"""Tests for E2E-O5C Transport Binding."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

SAMPLE_INTENTS = {
    "intents": [
        {
            "type": "PointToPointIntent",
            "id": "0x288",
            "appId": "org.onosproject.cli",
            "state": "FAILED",
        }
    ]
}

SAMPLE_SNAPSHOT_INJECT = {
    "devices": {"devices": []},
    "links": {"links": []},
    "hosts": {"hosts": []},
    "flows": {"flows": []},
    "intents": SAMPLE_INTENTS,
    "rest_error": None,
    "rest_latency_ms": 42.5,
}

SSB_ACCESS = {
    "sst": 1,
    "sd": "010203",
    "transport_ref": "onos.nasp-transport.svc.cluster.local:8181",
    "binding_phase": "ACCESS_CORRELATED",
    "correlation_status": "CONTEXT_SPLIT",
    "integration_flags": {
        "nssf_integrated": True,
        "amf_integrated": True,
        "smf_integrated": True,
        "upf_integrated": True,
        "ran_integrated": True,
        "onos_integrated": False,
    },
}

SAMPLE_RAN_BINDING = {
    "supi": "imsi-208930000000001",
    "session_id": "1",
    "dnn": "internet",
    "gnb_id": "00000001",
    "correlation_status": "CONTEXT_SPLIT",
}

SAMPLE_SMF_BINDING = {
    "session_id": "1",
    "supi": "imsi-208930000000001",
    "dnn": "internet",
}

SAMPLE_AMF_BINDING = {"supi": "imsi-208930000000001"}

SAMPLE_PDU_SUMMARY = {
    "session_id": "1",
    "supi": "imsi-208930000000001",
    "dnn": "internet",
    "fresh_ue_ip": "10.1.0.1",
    "upf_gtpu_addr": "10.233.75.38",
    "access_correlated": True,
    "correlation_status": "CONTEXT_SPLIT",
}


def test_onos_intent_parser():
    from transport_binding_adapter import parse_intents

    intents = parse_intents(SAMPLE_INTENTS)
    assert len(intents) == 1
    assert intents[0]["id"] == "0x288"
    assert intents[0]["state"] == "FAILED"
    assert intents[0]["type"] == "PointToPointIntent"


def test_onos_snapshot_empty_topology():
    from transport_binding_adapter import parse_onos_snapshot, TOPO_EMPTY, CTRL_HEALTH_DEGRADED

    snap = parse_onos_snapshot(
        devices={"devices": []},
        links={"links": []},
        hosts={"hosts": []},
        flows={"flows": []},
        intents=SAMPLE_INTENTS,
    )
    assert snap["device_count"] == 0
    assert snap["link_count"] == 0
    assert snap["flow_count"] == 0
    assert snap["intent_count"] == 1
    assert snap["failed_intents"] == 1
    assert snap["topology_health"] == TOPO_EMPTY
    assert snap["lab_topology_empty"] is True
    assert snap["controller_health"] == CTRL_HEALTH_DEGRADED


def test_health_engine_fresh():
    from transport_binding_adapter import compute_freshness_status, FRESHNESS_FRESH, parse_onos_snapshot

    snap = parse_onos_snapshot(
        devices={"devices": []},
        links={"links": []},
        flows={"flows": []},
        intents={"intents": []},
        rest_error=None,
    )
    assert compute_freshness_status(snap) == FRESHNESS_FRESH


def test_health_engine_auth_failed():
    from transport_binding_adapter import compute_freshness_status, FRESHNESS_FAILED, parse_onos_snapshot

    snap = parse_onos_snapshot(rest_error="ONOS_AUTH_FAILED")
    assert compute_freshness_status(snap) == FRESHNESS_FAILED


def test_transport_observed_only(monkeypatch):
    from transport_binding_adapter import BINDING_PHASE_TRANSPORT_OBSERVED
    from transport_correlation import run_transport_binding

    monkeypatch.setenv("TRANSPORT_BINDING_ENABLED", "true")

    ssb = {"binding_phase": "SMF_OBSERVED", "integration_flags": {"smf_integrated": True}}
    result = run_transport_binding(ssb, snapshot_inject=SAMPLE_SNAPSHOT_INJECT)
    assert result["skipped"] is False
    assert result["binding"]["binding_phase"] == BINDING_PHASE_TRANSPORT_OBSERVED
    assert result["transport_correlated"] is False


def test_transport_correlated(monkeypatch):
    from transport_correlation import BINDING_PHASE_TRANSPORT_CORRELATED, run_transport_binding

    monkeypatch.setenv("TRANSPORT_BINDING_ENABLED", "true")

    result = run_transport_binding(
        dict(SSB_ACCESS),
        amf_binding=SAMPLE_AMF_BINDING,
        smf_binding=SAMPLE_SMF_BINDING,
        ran_binding=SAMPLE_RAN_BINDING,
        pdu_session_summary=SAMPLE_PDU_SUMMARY,
        snapshot_inject=SAMPLE_SNAPSHOT_INJECT,
    )
    assert result["skipped"] is False
    assert result["binding"]["binding_phase"] == BINDING_PHASE_TRANSPORT_CORRELATED
    assert result["transport_correlated"] is True
    assert result["transport_binding_annotation"]

    summary = json.loads(result["pdu_session_summary_annotation"])
    assert summary["transport_binding_status"] == "OBSERVED"
    assert summary["controller_health"] == "DEGRADED"
    assert summary["topology_state"] == "EMPTY"
    assert summary["intent_state"] == "FAILED"
    assert summary["transport_correlated"] is True
    assert summary["fresh_ue_ip"] == "10.1.0.1"


def test_transport_disabled_skips(monkeypatch):
    from transport_correlation import run_transport_binding

    monkeypatch.delenv("TRANSPORT_BINDING_ENABLED", raising=False)
    os.environ.pop("TRANSPORT_BINDING_ENABLED", None)

    result = run_transport_binding(SSB_ACCESS, snapshot_inject=SAMPLE_SNAPSHOT_INJECT)
    assert result["skipped"] is True


def test_transport_default_off():
    from transport_binding_adapter import transport_binding_enabled

    old = os.environ.pop("TRANSPORT_BINDING_ENABLED", None)
    try:
        assert transport_binding_enabled() is False
    finally:
        if old is not None:
            os.environ["TRANSPORT_BINDING_ENABLED"] = old


def test_annotation_format(monkeypatch):
    from transport_binding_adapter import (
        build_transport_binding_annotation,
        parse_onos_snapshot,
        parse_transport_binding_annotation,
        transport_binding_annotation_value,
    )

    snap = parse_onos_snapshot(
        devices={"devices": []},
        links={"links": []},
        flows={"flows": []},
        intents=SAMPLE_INTENTS,
    )
    ann = build_transport_binding_annotation(
        snap,
        transport_ref="onos.nasp-transport.svc.cluster.local:8181",
        correlation_status="CONTEXT_SPLIT",
    )
    raw = transport_binding_annotation_value(ann)
    parsed = parse_transport_binding_annotation(raw)
    assert parsed["contract_version"] == "TRANSPORT_CONTRACT_SSOT_V1"
    assert parsed["binding_status"] == "OBSERVED"
    assert parsed["controller"] == "onos"
    assert parsed["devices_count"] == 0
    assert parsed["failed_intents"] == 1
    assert parsed["topology_state"] == "EMPTY"
    assert parsed["freshness_source"] == "onos_rest"


def test_fallback_unreachable(monkeypatch):
    from transport_binding_adapter import observe_transport_binding

    monkeypatch.setenv("TRANSPORT_BINDING_ENABLED", "true")

    inject = {
        "devices": None,
        "links": None,
        "hosts": None,
        "flows": None,
        "intents": None,
        "rest_error": "ONOS_REST_UNREACHABLE",
        "rest_latency_ms": 10000,
    }
    result = observe_transport_binding(SSB_ACCESS, snapshot_inject=inject)
    assert result["success"] is False
    failed = json.loads(result["transport_binding_annotation"])
    assert failed["binding_status"] == "FAILED"
    assert failed["error"] == "ONOS_REST_UNREACHABLE"


def test_join_keys_mismatch_blocks_correlation(monkeypatch):
    from transport_correlation import run_transport_binding

    monkeypatch.setenv("TRANSPORT_BINDING_ENABLED", "true")

    bad_smf = dict(SAMPLE_SMF_BINDING)
    bad_smf["supi"] = "imsi-999999999999999"

    result = run_transport_binding(
        dict(SSB_ACCESS),
        amf_binding=SAMPLE_AMF_BINDING,
        smf_binding=bad_smf,
        ran_binding=SAMPLE_RAN_BINDING,
        pdu_session_summary=SAMPLE_PDU_SUMMARY,
        snapshot_inject=SAMPLE_SNAPSHOT_INJECT,
    )
    assert result["transport_correlated"] is False


def test_observe_endpoint_imports(monkeypatch):
    from transport_binding_adapter import observe_transport_binding, parse_transport_binding_annotation

    monkeypatch.setenv("TRANSPORT_BINDING_ENABLED", "true")
    result = observe_transport_binding(
        SSB_ACCESS,
        snapshot_inject=SAMPLE_SNAPSHOT_INJECT,
        correlation_status="CONTEXT_SPLIT",
    )
    ann = parse_transport_binding_annotation(result["transport_binding_annotation"])
    assert ann["devices_count"] == 0
    assert ann["intent_count"] == 1
