"""
FASE 4 — Autoridade semântica de lifecycle e governança no Decision Engine
(code-only, sem build/deploy, sem alteração de contrato público).

Este módulo é complementar a `orchestration_authority.py` (FASE 3) e enriquece
`DecisionResult.metadata` com dois blocos novos consumidos pelo Portal Backend
(via SEM-CSMF) e pelo BC-NSSMF:

* ``lifecycle_event`` — descreve o evento *semântico* derivado da decisão
  (ACCEPT/REJECT/RENEGOTIATE), com os campos exigidos pela FASE 4:
  ``lifecycle_state``, ``lifecycle_event_type``, ``lifecycle_transition_reason``
  e ``lifecycle_authority="decision-engine"``.
* ``governance_event`` — payload canônico de governança (immutable summary)
  destinado ao registro em BC-NSSMF.

Notas de não-regressão:
* NÃO altera campos públicos de ``SLASubmitResponse``.
* NÃO substitui os campos de FASE 3 (``orchestration_lifecycle_state`` etc.);
  apenas adiciona blocos paralelos em ``metadata``.
* NÃO executa BC-NSSMF nem qualquer call externo.
* Portal Backend e BC-NSSMF continuam funcionando se este bloco estiver ausente
  (fallback preservado).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from models import DecisionAction, DecisionInput, DecisionResult


LIFECYCLE_AUTHORITY_VERSION = "1.0"
GOVERNANCE_EVENT_VERSION = "1.0"
LIFECYCLE_AUTHORITY_NAME = "decision-engine"
GOVERNANCE_AUTHORITY_NAME = "decision-engine"


def _action_to_lifecycle_state(action: DecisionAction) -> str:
    if action == DecisionAction.ACCEPT:
        return "ORCHESTRATION_REQUESTED"
    if action == DecisionAction.REJECT:
        return "REJECTED"
    return "RENEGOTIATION_REQUIRED"


def _action_to_event_type(action: DecisionAction) -> str:
    if action == DecisionAction.ACCEPT:
        return "SLA_DECISION_ACCEPT"
    if action == DecisionAction.REJECT:
        return "SLA_DECISION_REJECT"
    return "SLA_DECISION_RENEGOTIATE"


def _compose_transition_reason(
    action: DecisionAction,
    reason_codes: List[str],
    decision_mode: Optional[str],
) -> str:
    base = {
        DecisionAction.ACCEPT: "decision_accept",
        DecisionAction.REJECT: "decision_reject",
        DecisionAction.RENEGOTIATE: "decision_renegotiate",
    }.get(action, "decision_unknown")
    parts = [base]
    if decision_mode:
        parts.append(f"mode={decision_mode}")
    if reason_codes:
        parts.append(f"reasons={'|'.join(reason_codes[:6])}")
    return ";".join(parts)


def _governance_event_id(payload: Dict[str, Any]) -> str:
    """Identificador determinístico do evento (sha256 do payload canônico)."""
    try:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    except Exception:
        canonical = repr(payload)
    return "ge_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]


def enrich_lifecycle_governance_metadata(
    result: DecisionResult,
    decision_input: DecisionInput,
) -> None:
    """Muta `result.metadata` in-place com lifecycle/governance authority (FASE 4).

    Idempotente: chamadas repetidas produzem o mesmo conjunto de campos. Não
    sobrescreve campos pré-existentes de FASE 3 (``orchestration_*``,
    ``decision_engine_orchestration_authority``) e não toca em campos públicos.
    """
    md: Dict[str, Any] = dict(result.metadata or {})
    action = result.action

    intent = decision_input.intent
    nest = decision_input.nest
    st = intent.service_type
    st_val = st.value if hasattr(st, "value") else str(st)
    intent_id = intent.intent_id
    tenant_id = intent.tenant_id or "default"
    nest_id = nest.nest_id if nest else None

    lifecycle_state = _action_to_lifecycle_state(action)
    lifecycle_event_type = _action_to_event_type(action)

    reason_codes_raw = md.get("reason_codes")
    reason_codes: List[str] = (
        [str(x) for x in reason_codes_raw] if isinstance(reason_codes_raw, list) else []
    )

    decision_mode: Optional[str] = md.get("decision_mode") or result.decision_mode
    transition_reason = _compose_transition_reason(action, reason_codes, decision_mode)

    decision_score: Optional[float] = None
    if isinstance(md.get("decision_score"), (int, float)):
        decision_score = float(md["decision_score"])
    risk_score: Optional[float] = result.ml_risk_score

    now_iso = datetime.now(timezone.utc).isoformat()

    lifecycle_event: Dict[str, Any] = {
        "lifecycle_state": lifecycle_state,
        "lifecycle_event_type": lifecycle_event_type,
        "lifecycle_transition_reason": transition_reason,
        "lifecycle_authority": LIFECYCLE_AUTHORITY_NAME,
        "lifecycle_authority_version": LIFECYCLE_AUTHORITY_VERSION,
        "lifecycle_event_timestamp": now_iso,
        "intent_id": intent_id,
        "nest_id": nest_id,
        "tenant_id": tenant_id,
        "service_type": st_val,
        "decision": action.value if hasattr(action, "value") else str(action),
        "decision_mode": decision_mode,
        "decision_score": decision_score,
        "risk_score": risk_score,
        "reason_codes": reason_codes,
    }

    governance_event_core: Dict[str, Any] = {
        "event_version": GOVERNANCE_EVENT_VERSION,
        "event_type": "SLA_LIFECYCLE_TRANSITION",
        "event_state": lifecycle_state,
        "event_action": lifecycle_event_type,
        "event_authority": GOVERNANCE_AUTHORITY_NAME,
        "event_timestamp": now_iso,
        "intent_id": intent_id,
        "nest_id": nest_id,
        "tenant_id": tenant_id,
        "service_type": st_val,
        "decision": action.value if hasattr(action, "value") else str(action),
        "decision_score": decision_score,
        "risk_score": risk_score,
        "reason_codes": reason_codes,
        "transition_reason": transition_reason,
    }
    governance_event_core["governance_event_id"] = _governance_event_id(governance_event_core)

    from observability.distributed_trace import child_trace, merge_trace_into_metadata, trace_from_metadata

    ctx = decision_input.context if isinstance(decision_input.context, dict) else {}
    in_trace = trace_from_metadata(ctx)
    if in_trace:
        de_trace = child_trace(in_trace, "decision-engine")
        md = merge_trace_into_metadata(md, de_trace)
        for block in (lifecycle_event, governance_event_core):
            block["trace_id"] = de_trace.get("trace_id")
            block["span_id"] = de_trace.get("span_id")
            if de_trace.get("parent_span_id") is not None:
                block["parent_span_id"] = de_trace.get("parent_span_id")

    md.setdefault("lifecycle_event", lifecycle_event)
    md.setdefault("governance_event", governance_event_core)
    md.setdefault("lifecycle_authority", LIFECYCLE_AUTHORITY_NAME)
    md.setdefault("lifecycle_authority_version", LIFECYCLE_AUTHORITY_VERSION)
    md.setdefault("governance_authority", GOVERNANCE_AUTHORITY_NAME)
    md.setdefault("decision_engine_lifecycle_authority", True)
    md.setdefault("decision_engine_governance_authority", True)

    result.metadata = md
