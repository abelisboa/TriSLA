"""Wave 3A G3-C — SEM I-01 NEST transmission contract."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from decision_engine_client import (  # noqa: E402
    DecisionEngineHTTPClient,
    serialize_nest_for_i01,
)
from models.nest import NEST, NetworkSlice, NetworkSliceStatus  # noqa: E402


def _sample_nest() -> NEST:
    return NEST(
        nest_id="nest-intent-sem-test",
        intent_id="intent-sem-test",
        status=NetworkSliceStatus.GENERATED,
        network_slices=[
            NetworkSlice(
                slice_id="slice-intent-sem-test-001",
                slice_type="eMBB",
                resources={"cpu": "4", "bandwidth": "1Gbps"},
                status=NetworkSliceStatus.GENERATED,
            )
        ],
        gst_id="gst-intent-sem-test",
    )


def test_serialize_nest_for_i01_from_model():
    data = serialize_nest_for_i01(_sample_nest())
    assert data["nest_id"] == "nest-intent-sem-test"
    assert data["status"] == "generated"
    assert len(data["network_slices"]) == 1
    assert data["network_slices"][0]["slice_type"] == "eMBB"


def test_serialize_nest_for_i01_from_dict():
    raw = {"nest_id": "n1", "intent_id": "i1", "network_slices": []}
    assert serialize_nest_for_i01(raw) == raw


def test_serialize_nest_for_i01_none():
    assert serialize_nest_for_i01(None) is None


@patch("decision_engine_client.requests.post")
def test_send_nest_metadata_includes_nest_when_enabled(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        text='{"action":"AC","decision_id":"d1","confidence":0.9,"reasoning":"ok"}',
    )
    mock_post.return_value.raise_for_status = MagicMock()
    mock_post.return_value.json.return_value = {
        "action": "AC",
        "decision_id": "d1",
        "confidence": 0.9,
        "reasoning": "ok",
    }

    client = DecisionEngineHTTPClient()
    client.base_url = "http://de.test/evaluate"
    nest = _sample_nest()

    import asyncio

    asyncio.run(
        client.send_nest_metadata(
            intent_id="intent-sem-test",
            nest_id=nest.nest_id,
            tenant_id="tenant-1",
            service_type="eMBB",
            sla_requirements={"latency": "50ms"},
            nest_status="generated",
            metadata={"trace_id": "t-1"},
            nest=nest,
        )
    )

    call_kwargs = mock_post.call_args.kwargs
    payload = call_kwargs["json"]
    assert "nest" in payload
    assert payload["nest"]["nest_id"] == nest.nest_id
    assert len(payload["nest"]["network_slices"]) == 1
    assert payload["nest_id"] == nest.nest_id


@patch("decision_engine_client.requests.post")
@patch("decision_engine_client.SEM_I01_NEST_TRANSMIT", False)
def test_send_nest_metadata_omits_nest_when_flag_disabled(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        text='{"action":"AC","decision_id":"d1","confidence":0.9,"reasoning":"ok"}',
    )
    mock_post.return_value.raise_for_status = MagicMock()
    mock_post.return_value.json.return_value = {
        "action": "AC",
        "decision_id": "d1",
        "confidence": 0.9,
        "reasoning": "ok",
    }

    client = DecisionEngineHTTPClient()
    client.base_url = "http://de.test/evaluate"

    import asyncio

    asyncio.run(
        client.send_nest_metadata(
            intent_id="intent-sem-test",
            nest_id="nest-intent-sem-test",
            tenant_id="tenant-1",
            service_type="eMBB",
            sla_requirements={"latency": "50ms"},
            nest_status="generated",
            nest=_sample_nest(),
        )
    )

    payload = mock_post.call_args.kwargs["json"]
    assert "nest" not in payload
