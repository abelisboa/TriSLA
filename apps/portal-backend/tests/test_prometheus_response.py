"""Tests for safe Prometheus/Loki data.result parsing."""
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.utils.prometheus_response import (  # noqa: E402
    safe_extract_result,
    safe_first_vector_value,
)


class TestSafeExtractResult(unittest.TestCase):
    def test_valid_list(self):
        p = {"status": "success", "data": {"result": [{"metric": {}, "value": [1, "2"]}]}}
        r = safe_extract_result(p)
        self.assertIsInstance(r, list)
        self.assertEqual(len(r), 1)

    def test_result_true_returns_none(self):
        p = {"status": "success", "data": {"result": True}}
        self.assertIsNone(safe_extract_result(p))

    def test_result_string_returns_none(self):
        p = {"data": {"result": "x"}}
        self.assertIsNone(safe_extract_result(p))


class TestSafeFirstVectorValue(unittest.TestCase):
    def test_ok(self):
        p = {"data": {"result": [{"metric": {}, "value": [1.0, "3.14"]}]}}
        self.assertEqual(safe_first_vector_value(p), "3.14")

    def test_bad_result(self):
        self.assertIsNone(safe_first_vector_value({"data": {"result": True}}))


if __name__ == "__main__":
    unittest.main()
