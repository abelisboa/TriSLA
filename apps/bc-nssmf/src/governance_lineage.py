"""
FASE 4 — BC-NSSMF como registrador imutável de governança/lifecycle (code-only).

Este módulo encapsula a lógica de:

* normalização do evento de governança recebido (proveniente do Decision Engine
  via Portal Backend);
* geração de identificadores determinísticos (``governance_registration_id``,
  ``lifecycle_lineage_id``);
* construção do bloco de "lineage" devolvido pela API REST e da resposta de
  fallback quando o serviço está em modo degraded.

NÃO altera os contratos públicos existentes de ``/api/v1/register-sla`` —
apenas adiciona campos opcionais à resposta. O fluxo `register_sla` continua
chamando o smart contract; a governança imutável é registrada como metadado
controlado deste módulo, com identidade derivada do payload do evento +
``tx_hash`` da transação (quando existir).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


GOVERNANCE_REGISTRATION_AUTHORITY = "bc-nssmf"
GOVERNANCE_REGISTRATION_VERSION = "1.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_hash(payload: Dict[str, Any], prefix: str) -> str:
    try:
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=str
        )
    except Exception:
        canonical = repr(payload)
    return f"{prefix}_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]


def normalize_governance_event(raw: Any) -> Optional[Dict[str, Any]]:
    """Aceita o ``governance_event`` vindo do DE/portal e devolve um dict
    canonicalizado, ou ``None`` se o payload não é utilizável.

    Não exige todos os campos; usa defaults defensivos.
    """
    if not isinstance(raw, dict):
        return None
    if not raw.get("event_type") and not raw.get("event_state"):
        return None
    event = dict(raw)
    event.setdefault("event_version", "1.0")
    event.setdefault("event_type", "SLA_LIFECYCLE_TRANSITION")
    event.setdefault("event_authority", "decision-engine")
    event.setdefault("event_state", event.get("event_state") or "UNKNOWN")
    return event


def normalize_lifecycle_event(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    if not raw.get("lifecycle_state") and not raw.get("lifecycle_event_type"):
        return None
    return dict(raw)


def build_governance_registration_id(
    governance_event: Dict[str, Any],
    tx_hash: Optional[str],
) -> str:
    seed = {
        "ge": governance_event.get("governance_event_id")
        or _canonical_hash(governance_event, "ge"),
        "tx": tx_hash or "no-tx",
    }
    return _canonical_hash(seed, "gr")


def build_lifecycle_lineage(
    governance_event: Optional[Dict[str, Any]],
    lifecycle_event: Optional[Dict[str, Any]],
    tx_hash: Optional[str],
    block_number: Optional[int],
    correlation_id: Optional[str],
    intent_id: Optional[str],
    nest_id: Optional[str],
) -> Dict[str, Any]:
    lineage: Dict[str, Any] = {
        "lifecycle_lineage_version": GOVERNANCE_REGISTRATION_VERSION,
        "correlation_id": correlation_id,
        "intent_id": intent_id,
        "nest_id": nest_id,
        "tx_hash": tx_hash,
        "block_number": block_number,
        "registered_at": _now_iso(),
        "lifecycle_lineage_authority": GOVERNANCE_REGISTRATION_AUTHORITY,
    }
    if governance_event:
        lineage["governance_event_id"] = governance_event.get("governance_event_id")
        lineage["event_state"] = governance_event.get("event_state")
        lineage["event_type"] = governance_event.get("event_type")
        lineage["event_authority"] = governance_event.get("event_authority")
    if lifecycle_event:
        lineage["lifecycle_state"] = lifecycle_event.get("lifecycle_state")
        lineage["lifecycle_event_type"] = lifecycle_event.get("lifecycle_event_type")
        lineage["lifecycle_authority"] = lifecycle_event.get("lifecycle_authority")
        lineage["lifecycle_transition_reason"] = lifecycle_event.get(
            "lifecycle_transition_reason"
        )
    lineage["lifecycle_lineage_id"] = _canonical_hash(lineage, "ll")
    return lineage


def build_governance_response_block(
    governance_event: Optional[Dict[str, Any]],
    lifecycle_event: Optional[Dict[str, Any]],
    tx_hash: Optional[str],
    block_number: Optional[int],
    correlation_id: Optional[str],
    intent_id: Optional[str],
    nest_id: Optional[str],
    bc_enabled: bool,
) -> Dict[str, Any]:
    """Bloco devolvido pela API REST. Sempre presente, com flags claras de
    fallback quando aplicável."""
    block: Dict[str, Any] = {
        "governance_registration_authority": GOVERNANCE_REGISTRATION_AUTHORITY,
        "governance_registration_version": GOVERNANCE_REGISTRATION_VERSION,
        "governance_registration_timestamp": _now_iso(),
    }
    if not governance_event and not lifecycle_event:
        block["governance_registration_status"] = "SKIPPED_NO_EVENT"
        block["governance_registration_fallback"] = False
        block["governance_event_present"] = False
        return block

    block["governance_event_present"] = bool(governance_event)
    block["lifecycle_event_present"] = bool(lifecycle_event)

    if bc_enabled and tx_hash:
        gr_id = build_governance_registration_id(governance_event or {}, tx_hash)
        block["governance_registration_id"] = gr_id
        block["governance_registration_status"] = "REGISTERED"
        block["governance_registration_fallback"] = False
        block["governance_registration_bc_status"] = "COMMITTED"
    else:
        gr_id = build_governance_registration_id(
            governance_event or lifecycle_event or {"placeholder": True},
            tx_hash,
        )
        block["governance_registration_id"] = gr_id
        block["governance_registration_status"] = "DEGRADED_FALLBACK"
        block["governance_registration_fallback"] = True
        block["governance_registration_bc_status"] = (
            "COMMITTED" if tx_hash else "DEGRADED"
        )
        block["governance_registration_fallback_reason"] = (
            "bc_disabled_or_no_tx_hash"
        )

    block["lifecycle_lineage"] = build_lifecycle_lineage(
        governance_event=governance_event,
        lifecycle_event=lifecycle_event,
        tx_hash=tx_hash,
        block_number=block_number,
        correlation_id=correlation_id,
        intent_id=intent_id,
        nest_id=nest_id,
    )
    if governance_event:
        block["governance_event_echo"] = governance_event
    if lifecycle_event:
        block["lifecycle_event_echo"] = lifecycle_event
    return block
