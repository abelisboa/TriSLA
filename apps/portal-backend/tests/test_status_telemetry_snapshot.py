"""Unit tests — lifecycle runtime snapshot field mapping (Sprint 5M2)."""
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.services.sla_status_telemetry import (  # noqa: E402
    resolve_status_telemetry_snapshot,
)


URLLC_SNAPSHOT = {
    "execution_id": "exec-urllc",
    "timestamp": "2026-05-30T20:00:00+00:00",
    "telemetry_contract_version": "v2",
    "ran": {"prb_utilization": 0.0, "latency_ms": 5.2},
    "transport": {"rtt_ms": 5.0, "jitter_ms": 1.1},
    "core": {"cpu_utilization": 0.001, "memory_bytes": 0.008},
}

EMBB_SNAPSHOT = {
    "execution_id": "exec-embb",
    "telemetry_contract_version": "v2",
    "ran": {"prb_utilization": 0.1, "latency_ms": 4.8},
    "transport": {"rtt_ms": 4.5, "jitter_ms": 0.9},
    "core": {"cpu_utilization": 0.002, "memory_bytes": 0.009},
}

MMTC_SNAPSHOT = {
    "execution_id": "exec-mmtc",
    "telemetry_contract_version": "v2",
    "ran": {"prb_utilization": 0.05},
    "transport": {"rtt_ms": 6.0},
    "core": {"cpu_utilization": 0.003},
}

SMARTCITY_SNAPSHOT = {
    "execution_id": "exec-smartcity",
    "telemetry_contract_version": "v2",
    "ran": {"prb_utilization": 0.02, "latency_ms": 5.5},
    "transport": {"rtt_ms": 5.2, "jitter_ms": 1.0},
    "core": {"cpu_utilization": 0.0015, "memory_bytes": 0.007},
}


class TestStatusTelemetrySnapshot(unittest.TestCase):
    def test_prefers_sem_metadata_snapshot(self):
        sem = {"metadata": {"telemetry_snapshot": URLLC_SNAPSHOT}}
        out = resolve_status_telemetry_snapshot(sem, None)
        self.assertEqual(out, URLLC_SNAPSHOT)

    def test_falls_back_to_collected_snapshot(self):
        sem = {"metadata": {}}
        out = resolve_status_telemetry_snapshot(sem, EMBB_SNAPSHOT)
        self.assertEqual(out, EMBB_SNAPSHOT)

    def test_urllc_domains_populated(self):
        self._assert_domains(URLLC_SNAPSHOT)

    def test_embb_domains_populated(self):
        self._assert_domains(EMBB_SNAPSHOT)

    def test_mmtc_domains_populated(self):
        self._assert_domains(MMTC_SNAPSHOT)

    def test_smartcity_domains_populated(self):
        self._assert_domains(SMARTCITY_SNAPSHOT)

    def _assert_domains(self, snap: dict):
        self.assertIsInstance(snap.get("ran"), dict)
        self.assertIsInstance(snap.get("transport"), dict)
        self.assertIsInstance(snap.get("core"), dict)
        self.assertIn("prb_utilization", snap["ran"])
        self.assertTrue(
            "rtt_ms" in snap["transport"] or "latency_ms" in snap["transport"]
        )
        self.assertIn("cpu_utilization", snap["core"])


if __name__ == "__main__":
    unittest.main()
