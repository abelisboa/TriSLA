"""Tests for O6 Per-Slice Multidomain Metrics Export."""

import json
import os
import sys

import pytest
from prometheus_client import generate_latest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from multidomain_metrics_exporter import (
    MultidomainMetricsExporter,
    _build_slice_metrics,
    _code,
    multidomain_metrics_export_enabled,
)


def _sample_nsi(
    *,
    nsi_id="nsi-o6-test",
    intent_id="intent-o6-test",
    slice_type="URLLC",
    annotations=None,
):
    base_ann = {
        "trisla.io/slice-service-binding": json.dumps(
            {
                "binding_phase": "TRANSPORT_CORRELATED",
                "correlation_status": "TRANSPORT_CORRELATED",
                "integration_flags": {"onos_integrated": True},
            }
        ),
        "trisla.io/nssf-selection": json.dumps({"selection_status": "SUCCESS"}),
        "trisla.io/amf-binding": json.dumps({"binding_status": "OBSERVED"}),
        "trisla.io/smf-binding": json.dumps({"binding_status": "OBSERVED"}),
        "trisla.io/upf-binding": json.dumps({"binding_status": "OBSERVED"}),
        "trisla.io/ran-binding": json.dumps({"binding_status": "OBSERVED"}),
        "trisla.io/transport-binding": json.dumps(
            {
                "transport_binding_status": "OBSERVED",
                "binding_status": "OBSERVED",
                "controller_health": "HEALTHY",
                "topology_state": "EMPTY",
                "devices_count": 0,
                "links_count": 0,
                "flows_count": 3,
                "failed_intents": 1,
            }
        ),
    }
    if annotations:
        base_ann.update(annotations)
    return {
        "metadata": {"name": nsi_id, "annotations": base_ann},
        "spec": {
            "nsiId": nsi_id,
            "intentId": intent_id,
            "serviceProfile": slice_type,
        },
    }


def test_multidomain_export_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MULTIDOMAIN_METRICS_EXPORT_ENABLED", raising=False)
    assert multidomain_metrics_export_enabled() is False


def test_multidomain_export_enabled(monkeypatch):
    monkeypatch.setenv("MULTIDOMAIN_METRICS_EXPORT_ENABLED", "true")
    assert multidomain_metrics_export_enabled() is True


def test_binding_phase_codes():
    assert _code({"TRANSPORT_CORRELATED": 8}, "TRANSPORT_CORRELATED") == 8.0
    assert _code({"UNKNOWN": 0}, "missing") == 0.0


def test_build_slice_metrics_from_annotations():
    nsi = _sample_nsi()
    sem = {
        "decision_score": 0.87,
        "decision": "ACCEPT",
        "decision_confidence": 0.92,
        "reason": "score above threshold",
        "bc_status": "COMMITTED",
        "block_number": 42,
        "governance_registration_tx_hash": "0xabc",
        "governance_registration_status": "REGISTERED",
        "runtime_assurance": {
            "state": "COMPLIANT",
            "domain_compliance": 0.99,
            "sla_compliance": 0.95,
            "violations": [],
            "drift_count": 0,
        },
    }
    metrics = _build_slice_metrics(nsi, sem_meta=sem)
    assert metrics["binding_phase"] == 8.0
    assert metrics["nssf_selection_status"] == 2.0
    assert metrics["transport_binding_status"] == 2.0
    assert metrics["decision_score"] == 0.87
    assert metrics["decision_status"] == 1.0
    assert metrics["blockchain_tx_present"] == 1.0
    assert metrics["transport_failed_intents"] == 1.0
    assert metrics["_decision_reason"] == "score above threshold"


def test_build_slice_metrics_missing_annotations():
    nsi = {
        "metadata": {"name": "nsi-empty"},
        "spec": {"nsiId": "nsi-empty", "serviceProfile": "eMBB"},
    }
    metrics = _build_slice_metrics(nsi, sem_meta={})
    assert metrics["binding_phase"] == 0.0
    assert metrics["nssf_selection_status"] == 0.0
    assert metrics["decision_score"] == 0.0


def test_exporter_refresh_and_prometheus_scrape():
    nsi = _sample_nsi(nsi_id="nsi-scrape", intent_id="intent-scrape", slice_type="mMTC")

    def _list_nsis(_namespace=None):
        return [nsi]

    def _fetch_sem(_intent_id):
        return {"decision_score": 0.5, "decision": "RENEGOTIATE", "reason": "headroom"}

    exporter = MultidomainMetricsExporter(list_nsis=_list_nsis, fetch_sem=_fetch_sem)
    count = exporter.refresh()
    assert count == 1
    assert exporter.last_refresh_ok is True

    body = generate_latest().decode("utf-8")
    assert "trisla_binding_phase" in body
    assert 'nsi_id="nsi-scrape"' in body
    assert "trisla_transport_failed_intents" in body
    assert "trisla_decision_status" in body


def test_exporter_stale_label_removal():
    nsi_a = _sample_nsi(nsi_id="nsi-a", intent_id="intent-a")
    nsi_b = _sample_nsi(nsi_id="nsi-b", intent_id="intent-b")

    def _list_both(_namespace=None):
        return [nsi_a, nsi_b]

    exporter = MultidomainMetricsExporter(list_nsis=_list_both, fetch_sem=lambda _i: {})
    assert exporter.refresh() == 2

    def _list_one(_namespace=None):
        return [nsi_a]

    exporter._list_nsis = _list_one
    assert exporter.refresh() == 1

    body = generate_latest().decode("utf-8")
    assert 'nsi_id="nsi-a"' in body
    assert 'nsi_id="nsi-b"' not in body


def test_exporter_k8s_list_failure():
    def _fail(_namespace=None):
        raise RuntimeError("k8s unavailable")

    exporter = MultidomainMetricsExporter(list_nsis=_fail, fetch_sem=lambda _i: {})
    assert exporter.refresh() == 0
    assert exporter.last_refresh_ok is False
    assert "k8s unavailable" in (exporter.last_refresh_error or "")
