"""Sprint 10G.4 — governance metadata propagation helpers."""
from src.services.governance_metadata import (
    extract_governance_metadata,
    merge_governance_into_metadata,
    stale_governance_clarity,
)
from src.services.sla_operational_summary import build_operational_summary


def test_extract_governance_metadata_from_submit_result():
    result = {
        "bc_status": "COMMITTED",
        "tx_hash": "0xabc",
        "block_number": 123,
        "blockchain_status": "BLOCKCHAIN_REGISTERED",
    }
    md = {
        "governance_registration_status": "REGISTERED",
        "governance_event_id": "gov-1",
    }
    patch = extract_governance_metadata(result, md)
    assert patch["bc_status"] == "COMMITTED"
    assert patch["tx_hash"] == "0xabc"
    assert patch["block_number"] == 123
    assert patch["governance_registration_status"] == "REGISTERED"
    assert patch["governance_event_id"] == "gov-1"


def test_merge_governance_into_metadata_out():
    metadata_out = {}
    result = {"bc_status": "COMMITTED", "tx_hash": "0xdef", "block_number": 99}
    merge_governance_into_metadata(metadata_out, result)
    assert metadata_out["bc_status"] == "COMMITTED"
    assert metadata_out["tx_hash"] == "0xdef"


def test_operational_summary_reads_persisted_bc_fields():
    sem = {
        "intent_id": "id-1",
        "status": "ACTIVE",
        "nest_id": "nest-1",
        "metadata": {
            "final_decision": "ACCEPT",
            "bc_status": "COMMITTED",
            "tx_hash": "0x111",
            "block_number": 456,
        },
    }
    out = build_operational_summary(sem)
    assert out["bc_status"] == "COMMITTED"
    assert out["tx_hash"] == "0x111"
    assert out["block_number"] == 456


def test_stale_governance_clarity_detects_mismatch():
    md = {"bc_status": "COMMITTED"}
    ra = {
        "state": "WARNING",
        "governance_clarity": {
            "blockchain_registration": {"executed": False, "reason": "ACCEPT without on-chain commit"},
        },
    }
    assert stale_governance_clarity(ra, md) is True


def test_stale_governance_clarity_ok_when_executed():
    md = {"bc_status": "COMMITTED"}
    ra = {
        "state": "WARNING",
        "governance_clarity": {"blockchain_registration": {"executed": True}},
    }
    assert stale_governance_clarity(ra, md) is False
