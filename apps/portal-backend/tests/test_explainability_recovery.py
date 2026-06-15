"""RC-P20-04A — explainability passthrough and contract v2 alias tests."""
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.services.sla_explainability import (  # noqa: E402
    enrich_runtime_assurance_explainability,
    flatten_metric_explainability,
)
from src.telemetry.contract_v2 import apply_telemetry_contract_v2  # noqa: E402
from src.telemetry.promql_ssot import PROMQL_SSOT  # noqa: E402


class TestExplainabilityRecovery(unittest.TestCase):
    def test_promql_ssot_has_recovery_keys(self):
        for key in (
            "TRANSPORT_PACKET_LOSS_PCT",
            "RELIABILITY_PROXY_PCT",
            "CORE_AVAILABILITY_PCT",
        ):
            self.assertIn(key, PROMQL_SSOT)
            self.assertTrue(PROMQL_SSOT[key])

    def test_contract_v2_aliases(self):
        snap = {
            "ran": {"latency": 1.0, "reliability_pct": 99.0},
            "transport": {"rtt": 2.0, "packet_loss_pct": 1.0, "bandwidth_mbps": 5.0},
            "core": {"cpu": 0.01, "memory": 0.02, "availability_pct": 80.0},
        }
        apply_telemetry_contract_v2(snap)
        self.assertEqual(snap["transport"]["packet_loss"], 1.0)
        self.assertEqual(snap["ran"]["reliability"], 99.0)
        self.assertEqual(snap["core"]["availability"], 80.0)

    def test_metric_explainability_flatten(self):
        de = {
            "transport": [
                {
                    "metric": "packet_loss",
                    "observed": 0.0,
                    "threshold": 0.1,
                    "compliance_score": 1.0,
                    "status": "PASS",
                    "source": "telemetry_snapshot.transport",
                }
            ]
        }
        flat = flatten_metric_explainability(de)
        self.assertEqual(len(flat), 1)
        self.assertEqual(flat[0]["domain"], "transport")

    def test_enrich_runtime_assurance_explainability(self):
        ra = {
            "domain_explainability": {
                "core": [
                    {
                        "metric": "cpu",
                        "observed": 0.01,
                        "threshold": 80.0,
                        "compliance_score": 0.99,
                        "status": "PASS",
                        "source": "telemetry_snapshot.core",
                    }
                ]
            }
        }
        out = enrich_runtime_assurance_explainability(ra)
        self.assertIn("metric_explainability", out)
        self.assertEqual(len(out["metric_explainability"]), 1)


if __name__ == "__main__":
    unittest.main()
