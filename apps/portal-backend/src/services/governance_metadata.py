"""Governance / on-chain field propagation (Sprint 10G.4) — portal-backend only."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

# Keys mirrored into SEM extra_metadata for GET /sla/status and runtime assurance.
GOVERNANCE_METADATA_KEYS = frozenset(
    {
        "bc_status",
        "tx_hash",
        "block_number",
        "blockchain_tx_hash",
        "blockchain_status",
        "governance_registration_status",
        "governance_registration_tx_hash",
        "governance_registration_block_number",
        "governance_registration_fallback",
        "governance_event_id",
        "transaction_receipt",
    }
)


def extract_governance_metadata(
    result: Mapping[str, Any],
    metadata_out: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a patch dict from NASP submit result + enriched metadata_out."""
    out: Dict[str, Any] = {}
    md = metadata_out if isinstance(metadata_out, dict) else {}

    tx_hash = result.get("tx_hash") or result.get("blockchain_tx_hash") or md.get(
        "governance_registration_tx_hash"
    )
    block_number = result.get("block_number")
    if block_number is None:
        block_number = md.get("governance_registration_block_number")

    bc_status = result.get("bc_status")
    if bc_status is not None:
        out["bc_status"] = bc_status
    if tx_hash:
        out["tx_hash"] = tx_hash
        out["blockchain_tx_hash"] = tx_hash
    if block_number is not None:
        out["block_number"] = block_number

    for key in (
        "blockchain_status",
        "governance_registration_status",
        "governance_registration_tx_hash",
        "governance_registration_block_number",
        "governance_registration_fallback",
        "governance_event_id",
        "transaction_receipt",
    ):
        val = md.get(key)
        if val is None and key == "governance_registration_tx_hash" and tx_hash:
            val = tx_hash
        if val is None and key == "governance_registration_block_number" and block_number is not None:
            val = block_number
        if val is not None:
            out[key] = val

    return {k: v for k, v in out.items() if k in GOVERNANCE_METADATA_KEYS and v is not None}


def merge_governance_into_metadata(
    metadata_out: Dict[str, Any],
    result: Mapping[str, Any],
) -> Dict[str, Any]:
    """Ensure submit response metadata carries the same governance fields persisted to SEM."""
    patch = extract_governance_metadata(result, metadata_out)
    metadata_out.update(patch)
    return metadata_out


def governance_fields_from_sem(sem_result: Mapping[str, Any]) -> Dict[str, Any]:
    """Read governance fields from SEM GET /intents payload."""
    md = sem_result.get("metadata")
    if not isinstance(md, dict):
        return {}
    return extract_governance_metadata(md, md)


def stale_governance_clarity(ra: Dict[str, Any], md: Dict[str, Any]) -> bool:
    """True when cached runtime_assurance clarity disagrees with persisted bc_status."""
    bc = str(md.get("bc_status") or "").upper()
    if bc not in ("COMMITTED", "CONFIRMED", "REGISTERED"):
        return False
    gc = ra.get("governance_clarity")
    if not isinstance(gc, dict):
        return True
    br = gc.get("blockchain_registration")
    if not isinstance(br, dict):
        return True
    return br.get("executed") is not True
