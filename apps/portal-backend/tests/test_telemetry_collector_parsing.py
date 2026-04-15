"""Local tests: Prometheus query_range JSON parsing (no network)."""
import sys
import unittest
from pathlib import Path

# portal-backend package root
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.telemetry.collector import _mean_from_query_range_json  # noqa: E402


class TestMeanFromQueryRangeJson(unittest.TestCase):
    def test_mean_normal_matrix(self):
        data = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {"__name__": "up", "job": "x"},
                        "values": [[1.0, "2"], [2.0, "4"]],
                    }
                ],
            },
        }
        self.assertEqual(_mean_from_query_range_json(data, "up"), 3.0)

    def test_mean_result_bool_true_no_crash(self):
        """Regression: result=true must not raise 'bool' object is not iterable."""
        data = {
            "status": "success",
            "data": {"resultType": "matrix", "result": True},
        }
        self.assertIsNone(_mean_from_query_range_json(data, "q"))

    def test_mean_result_not_list(self):
        data = {"status": "success", "data": {"result": "bad"}}
        self.assertIsNone(_mean_from_query_range_json(data))

    def test_mean_empty_result(self):
        data = {"status": "success", "data": {"result": []}}
        self.assertIsNone(_mean_from_query_range_json(data))

    def test_mean_invalid_samples_skipped(self):
        data = {
            "status": "success",
            "data": {
                "result": [
                    {"metric": {"__name__": "m"}, "values": [[1, "not-a-float"], [2, "3"]]},
                ]
            },
        }
        self.assertEqual(_mean_from_query_range_json(data), 3.0)

    def test_mean_non_dict_series_skipped(self):
        data = {
            "status": "success",
            "data": {"result": ["not-a-series", {"metric": {}, "values": [[0, "1"]]}]},
        }
        self.assertEqual(_mean_from_query_range_json(data), 1.0)


if __name__ == "__main__":
    unittest.main()
