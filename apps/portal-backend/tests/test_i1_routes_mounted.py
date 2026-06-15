"""RC-P19-002 — I1 routes mounted on portal-backend app."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

I1_PATHS = (
    "/api/v1/interfaces/ran-i1/metrics",
    "/api/v1/interfaces/tn-i1/metrics",
    "/api/v1/interfaces/cn-i1/metrics",
)


def test_i1_routes_exist_and_return_200():
    fake_prom_value = 12.34

    def _fake_query(query: str):
        return fake_prom_value

    with patch("src.api.interfaces.i1_routes._prom_query", side_effect=_fake_query):
        for path in I1_PATHS:
            resp = client.get(path)
            assert resp.status_code == 200, f"{path} returned {resp.status_code}"
            body = resp.json()
            assert body.get("source") == "prometheus"
            assert isinstance(body.get("metrics"), dict)


def test_i1_routes_no_synthetic_payload_keys():
    with patch("src.api.interfaces.i1_routes._prom_query", return_value=None):
        resp = client.get("/api/v1/interfaces/ran-i1/metrics")
        assert resp.status_code == 200
        metrics = resp.json()["metrics"]
        assert metrics == {"prb_utilization": None}
