"""Testes mínimos — canonicalização SLA (FASE 2 GSMA alignment)."""

import copy
import os
import sys
import unittest

# Pacote de aplicação em apps/sem-csmf/src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from canonical_sla import canonicalize_sla_request  # noqa: E402


class TestCanonicalizeSLARequest(unittest.TestCase):
    def test_semantic_embb_legacy_shape(self):
        payload = {
            "service_type": "eMBB",
            "intent": "Industrial AR streaming",
            "tenant_id": "t1",
            "sla_requirements": {
                "template_id": "semantic-embb-template",
                "latency": "15ms",
                "throughput": "200Mbps",
                "availability_target": 99.95,
                "service_description": "AR assembly line",
                "priority": "high",
                "security_profile": "iso27001",
                "service_continuity": "tier2",
                "edge_processing": "required",
            },
        }
        c = canonicalize_sla_request(payload)
        self.assertEqual(c["slice_service_type"], "eMBB")
        self.assertEqual(c["legacy_input"]["template_id"], "semantic-embb-template")
        self.assertIn("latency", c["legacy_input"]["form_values"])
        self.assertEqual(c["service_requirements"]["latency_ms"], 15.0)
        self.assertEqual(c["service_requirements"]["throughput_mbps"], 200.0)
        self.assertEqual(c["service_requirements"]["availability"], 99.95)
        self.assertEqual(c["semantic_context"]["service_description"], "AR assembly line")

    def test_semantic_urllc_legacy_shape(self):
        payload = {
            "service_type": "URLLC",
            "intent": "Remote surgery",
            "sla_requirements": {
                "template_id": "semantic-urllc-template",
                "latency": "5ms",
                "jitter": "1ms",
                "reliability": 0.99999,
                "mobility_profile": "stationary",
                "service_description": "Tele-surgery",
            },
        }
        c = canonicalize_sla_request(payload)
        self.assertEqual(c["legacy_input"]["template_id"], "semantic-urllc-template")
        self.assertEqual(c["service_requirements"]["latency_ms"], 5.0)
        self.assertEqual(c["service_requirements"]["mobility_support"], "stationary")
        self.assertEqual(c["service_requirements"]["availability"], 0.99999)

    def test_semantic_mmtc_legacy_shape(self):
        payload = {
            "service_type": "mMTC",
            "intent": "Sensor farm",
            "sla_requirements": {
                "template_id": "semantic-mmtc-template",
                "expected_devices": 50000,
                "coverage": "Urban",
                "service_description": "Massive IoT",
            },
        }
        c = canonicalize_sla_request(payload)
        self.assertEqual(c["legacy_input"]["template_id"], "semantic-mmtc-template")
        self.assertEqual(c["service_requirements"]["device_density"], 50000)
        self.assertEqual(c["semantic_context"]["service_description"], "Massive IoT")

    def test_legacy_flat_without_canonical_keys(self):
        payload = {
            "service_type": "eMBB",
            "intent": "x",
            "sla_requirements": {
                "throughput": "50Mbps",
                "reliability": 0.99,
            },
        }
        c = canonicalize_sla_request(payload)
        self.assertIsNone(c["legacy_input"]["template_id"])
        self.assertEqual(c["legacy_input"]["form_values"]["throughput"], "50Mbps")
        self.assertEqual(c["service_requirements"]["throughput_mbps"], 50.0)

    def test_nested_form_values_preserves_template_id(self):
        payload = {
            "service_type": "eMBB",
            "sla_requirements": {
                "template_id": "semantic-embb-template",
                "form_values": {"latency": "20ms", "bandwidth": 100},
            },
        }
        c = canonicalize_sla_request(payload)
        self.assertEqual(c["legacy_input"]["template_id"], "semantic-embb-template")
        self.assertEqual(c["legacy_input"]["form_values"]["latency"], "20ms")
        self.assertEqual(c["service_requirements"]["throughput_mbps"], 100.0)

    def test_native_canonical_pass_through(self):
        native = {
            "slice_service_type": "URLLC",
            "sst": 1,
            "sd": "010203",
            "service_requirements": {
                "latency_ms": 1.0,
                "throughput_mbps": None,
                "availability": 99.999,
                "device_density": None,
                "mobility_support": "high",
            },
            "semantic_context": {
                "service_description": "Canon in",
                "business_criticality": None,
                "security_profile": None,
                "service_continuity": None,
                "edge_processing": None,
            },
            "legacy_input": {
                "template_id": "native",
                "form_values": {"a": 1},
            },
        }
        src = copy.deepcopy(native)
        c = canonicalize_sla_request(src)
        self.assertEqual(c["slice_service_type"], "URLLC")
        self.assertEqual(c["sst"], 1)
        self.assertEqual(c["sd"], "010203")
        self.assertEqual(c["service_requirements"]["latency_ms"], 1.0)
        self.assertEqual(c["legacy_input"]["form_values"]["a"], 1)


if __name__ == "__main__":
    unittest.main()
