"""Sprint 5N3 — assurance guard tests."""
from revalidate.assurance_guard import ASSURANCE_INCOMPLETE, build_incomplete_assurance


def test_incomplete_assurance_state():
    out = build_incomplete_assurance(intent_id="abc", slice_type="URLLC")
    assert out["state"] == ASSURANCE_INCOMPLETE
    assert out["assurance_state"] == ASSURANCE_INCOMPLETE
    assert out["state"] not in ("COMPLIANT", "WARNING", "AT_RISK", "VIOLATED")


def test_incomplete_has_warning():
    out = build_incomplete_assurance()
    assert "telemetry.incomplete" in out["warnings"]
