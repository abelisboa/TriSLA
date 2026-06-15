"""Unit checks for frozen g_transport in score_mode."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from decision_score_mode import (  # noqa: E402
    _g_transport_from_rtt,
    _transport_rtt_ref_ms,
    _transport_score_weight,
)


def test_g_transport_bounds_and_monotone():
    ref = _transport_rtt_ref_ms()
    assert ref == 12.21
    assert _g_transport_from_rtt(0) == 1.0
    assert _g_transport_from_rtt(ref) == 0.0
    assert _g_transport_from_rtt(5.0) > _g_transport_from_rtt(10.0)


def test_weight_defaults():
    os.environ.pop("TRISLA_TRANSPORT_SCORE_WEIGHT", None)
    assert _transport_score_weight() == 0.05
