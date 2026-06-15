"""P2 slice-specific w_transport in default_profile (SR-EXEC-04)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from decision_score_mode import (  # noqa: E402
    _profile_transport_weight,
    _transport_score_weight,
    default_profile,
)


def test_default_profile_transport_weights():
    assert default_profile("URLLC")["w_transport"] == 0.05
    assert default_profile("eMBB")["w_transport"] == 0.03
    assert default_profile("mMTC")["w_transport"] == 0.02
    assert default_profile("EMBB")["w_transport"] == 0.03


def test_profile_transport_weight_uses_profile():
    p = default_profile("mMTC")
    assert _profile_transport_weight(p) == 0.02


def test_profile_transport_fallback_when_missing():
    p = {"w_feas": 0.2}
    os.environ.pop("TRISLA_TRANSPORT_SCORE_WEIGHT", None)
    assert _profile_transport_weight(p) == _transport_score_weight()


def test_urllc_matches_global_default():
    p = default_profile("URLLC")
    os.environ.pop("TRISLA_TRANSPORT_SCORE_WEIGHT", None)
    assert _profile_transport_weight(p) == _transport_score_weight()
