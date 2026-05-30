"""Unit tests — Sprint 5K semantic fill (fill-missing-only)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services.semantic_resolver import (  # noqa: E402
    apply_semantic_fill_to_intent_sla,
    fill_sla_requirements_semantic,
    resolve_semantic_value,
)


def _gst_urllc():
    return {
        "template": {
            "slice_type": "URLLC",
            "sla": {"latency": "10ms", "reliability": 0.99999},
            "qos": {"latency": "1ms", "reliability": "0.99999"},
        }
    }


def _gst_embb():
    return {
        "template": {
            "slice_type": "eMBB",
            "sla": {"throughput": "100Mbps", "reliability": 0.99},
            "qos": {"guaranteed_bitrate": "100Mbps", "maximum_bitrate": "1Gbps"},
        }
    }


def _gst_mmtc():
    return {
        "template": {
            "slice_type": "mMTC",
            "sla": {"coverage": "Urban"},
            "qos": {"device_density": "1000000/km²", "data_rate": "160bps"},
        }
    }


class TestExplicitPreserved:
    def test_explicit_latency_not_overwritten_by_ontology(self):
        sla = {"latency": "1ms", "throughput": None, "reliability": 0.99999}
        filled, sources = fill_sla_requirements_semantic(
            sla, "URLLC", gst=_gst_urllc()
        )
        assert filled["latency"] == "1ms"
        assert sources["latency"] == "explicit"

    def test_explicit_throughput_not_overwritten(self):
        sla = {"latency": None, "throughput": "100Mbps", "reliability": 0.99}
        filled, sources = fill_sla_requirements_semantic(
            sla, "eMBB", gst=_gst_embb()
        )
        assert filled["throughput"] == "100Mbps"
        assert sources["throughput"] == "explicit"


class TestURLLC:
    def test_urllc_fills_missing_throughput_from_ontology(self):
        sla = {"latency": "10ms", "throughput": None, "reliability": 0.99999}
        filled, sources = fill_sla_requirements_semantic(
            sla, "URLLC", gst=_gst_urllc()
        )
        assert filled["latency"] == "10ms"
        assert filled["throughput"] == "100Mbps"
        assert filled["reliability"] == 0.99999
        assert sources["latency"] == "explicit"
        assert sources["throughput"] == "ontology"
        assert sources["reliability"] == "explicit"

    def test_urllc_all_three_present(self):
        sla = {"latency": "10ms", "throughput": None, "reliability": 0.99999}
        filled, _ = fill_sla_requirements_semantic(sla, "URLLC", gst=_gst_urllc())
        assert filled["latency"] is not None
        assert filled["throughput"] is not None
        assert filled["reliability"] is not None


class TestEMBB:
    def test_embb_fills_missing_latency_from_ontology(self):
        sla = {"latency": None, "throughput": "100Mbps", "reliability": 0.99}
        filled, sources = fill_sla_requirements_semantic(
            sla, "eMBB", gst=_gst_embb()
        )
        assert filled["latency"] == "50ms"
        assert filled["throughput"] == "100Mbps"
        assert filled["reliability"] == 0.99
        assert sources["latency"] == "ontology"
        assert sources["throughput"] == "explicit"

    def test_embb_does_not_replace_explicit_throughput_with_ontology_1000(self):
        sla = {"latency": None, "throughput": "100Mbps", "reliability": 0.99}
        filled, _ = fill_sla_requirements_semantic(sla, "eMBB", gst=_gst_embb())
        assert filled["throughput"] == "100Mbps"


class TestMMTC:
    def test_mmtc_fills_all_core_kpis_from_ontology(self):
        sla = {
            "latency": None,
            "throughput": None,
            "reliability": None,
            "coverage": "Urban",
        }
        filled, sources = fill_sla_requirements_semantic(
            sla, "mMTC", gst=_gst_mmtc()
        )
        assert filled["latency"] == "1000ms"
        assert filled["throughput"] == "0.1Mbps"
        assert filled["reliability"] == 0.9
        assert filled["coverage"] == "Urban"
        assert sources["coverage"] == "explicit"
        assert sources["latency"] == "ontology"
        assert sources["throughput"] == "ontology"
        assert sources["reliability"] == "ontology"

    def test_mmtc_device_density_from_gst_when_missing(self):
        sla = {"latency": None, "throughput": None, "reliability": None}
        filled, sources = fill_sla_requirements_semantic(
            sla, "mMTC", gst=_gst_mmtc()
        )
        assert filled["device_density"] == 1000000
        assert sources["device_density"] in ("ontology", "gst")


class TestResolveSemanticValue:
    def test_priority_order(self):
        val, src = resolve_semantic_value(
            "throughput",
            None,
            {"throughput": "100Mbps"},
            {"throughput": "1Gbps"},
            {"throughput": "500Mbps"},
        )
        assert val == "100Mbps"
        assert src == "ontology"

    def test_gst_used_when_ontology_empty(self):
        val, src = resolve_semantic_value(
            "throughput",
            None,
            {},
            {"throughput": "1Gbps"},
            {},
        )
        assert val == "1Gbps"
        assert src == "gst"


class TestApplyWrapper:
    def test_apply_wrapper_matches_fill(self):
        sla = {"latency": "10ms", "throughput": None, "reliability": 0.99999}
        a, sa = apply_semantic_fill_to_intent_sla(sla, "URLLC", gst=_gst_urllc())
        b, sb = fill_sla_requirements_semantic(sla, "URLLC", gst=_gst_urllc())
        assert a == b
        assert sa == sb
