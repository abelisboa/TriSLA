"""Sprint 5N3 — lifecycle success state tests."""
from src.services.sla_lifecycle_success import (
    SLA_AGENT_SUCCESS_STATUSES,
    is_sla_agent_ingest_success,
)


def test_success_statuses_include_ok_with_assurance():
    assert "OK_WITH_ASSURANCE" in SLA_AGENT_SUCCESS_STATUSES
    assert is_sla_agent_ingest_success("OK_WITH_ASSURANCE")


def test_success_statuses_ok_and_slo():
    assert is_sla_agent_ingest_success("OK")
    assert is_sla_agent_ingest_success("OK_WITH_SLO")


def test_failed_not_success():
    assert not is_sla_agent_ingest_success("ERROR")
    assert not is_sla_agent_ingest_success("SKIPPED")
    assert not is_sla_agent_ingest_success(None)


def test_ok_with_assurance_not_mapped_to_failed():
    """OK_WITH_ASSURANCE must never be treated as ingest failure."""
    status = "OK_WITH_ASSURANCE"
    assert is_sla_agent_ingest_success(status)
    would_fail = status not in ("OK", "OK_WITH_SLO")
    assert not would_fail or is_sla_agent_ingest_success(status)
