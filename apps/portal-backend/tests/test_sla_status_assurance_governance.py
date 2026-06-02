"""Sprint 10G.4 — runtime assurance payload includes governance fields."""
from unittest.mock import MagicMock, patch

from src.services.sla_status_assurance import resolve_status_runtime_assurance


def test_resolve_status_passes_bc_status_to_sla_agent():
    sem = {
        "intent_id": "intent-1",
        "nest_id": "nest-1",
        "service_type": "URLLC",
        "metadata": {
            "final_decision": "ACCEPT",
            "bc_status": "COMMITTED",
            "tx_hash": "0xaaa",
            "block_number": 100,
        },
    }
    snap = {"ran": {"latency_ms": 1.0}, "transport": {}, "core": {}}
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "runtime_assurance": {
            "state": "OK",
            "governance_clarity": {
                "blockchain_registration": {"executed": True},
            },
        }
    }
    mock_resp.raise_for_status = MagicMock()

    with patch(
        "src.services.sla_status_assurance._assurance_evaluate_url",
        return_value="http://sla-agent/api/v1/runtime-assurance/evaluate",
    ), patch("src.services.sla_status_assurance.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.post.return_value = mock_resp
        ra = resolve_status_runtime_assurance(
            sem, telemetry_snapshot=snap, runtime_lifecycle_enabled=True
        )

    assert ra is not None
    assert ra["governance_clarity"]["blockchain_registration"]["executed"] is True
    call_kwargs = client.post.call_args
    payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][1]
    assert payload["bc_status"] == "COMMITTED"
    assert payload["tx_hash"] == "0xaaa"
    assert payload["block_number"] == 100
    assert payload["decision"] == "ACCEPT"
