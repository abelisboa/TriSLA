"""
FASE 3 — Autoridade lógica de orquestração no Decision Engine (code-only).

Enriquece `DecisionResult.metadata` com campos consumidos pelo Portal Backend
via SEM-CSMF (`IntentResponse.metadata` espelha `decision_response.metadata`).

Não executa NASP Adapter — apenas descreve intenção/payload mínimo para o
executor técnico (Portal → NASP Adapter), alinhado a `_build_orchestration_payload`
do portal-backend.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from models import DecisionAction, DecisionInput, DecisionResult


def enrich_orchestration_authority_metadata(
    result: DecisionResult,
    decision_input: DecisionInput,
) -> None:
    """Muta `result.metadata` in-place com autoridade de orquestração (FASE 3)."""
    md: Dict[str, Any] = dict(result.metadata or {})
    action = result.action

    orch_required = action == DecisionAction.ACCEPT
    if action == DecisionAction.ACCEPT:
        orch_lifecycle = "ORCHESTRATION_REQUESTED"
    elif action == DecisionAction.REJECT:
        orch_lifecycle = "REJECTED"
    else:
        orch_lifecycle = "RENEGOTIATION_REQUIRED"

    intent = decision_input.intent
    nest = decision_input.nest
    st = intent.service_type
    st_val = st.value if hasattr(st, "value") else str(st)
    intent_id = intent.intent_id
    tenant_id = intent.tenant_id or "default"
    nest_id = nest.nest_id if nest else None
    sla_req = dict(intent.sla_requirements or {})
    nsi_id = str(nest_id or intent_id)

    orchestration_intent: Dict[str, Any] = {
        "nsiId": nsi_id,
        "serviceProfile": st_val,
        "service_type": st_val,
        "tenant_id": tenant_id,
        "sla_requirements": sla_req,
        "sla": sla_req,
        "source": "decision-engine-orchestration-authority",
        "intent_id": intent_id,
        "nest_id": nest_id,
    }

    policy_context: Dict[str, Any] = {
        "decision_mode": md.get("decision_mode") or result.decision_mode,
        "threshold_decision": result.threshold_decision,
        "final_decision": result.final_decision,
        "policy_governed": md.get("policy_governed"),
    }

    risk_score: Optional[float] = result.ml_risk_score
    decision_score: Optional[float] = None
    if isinstance(md.get("decision_score"), (int, float)):
        decision_score = float(md["decision_score"])
    reason_codes = md.get("reason_codes")
    if not isinstance(reason_codes, list):
        reason_codes = []

    md["decision_engine_orchestration_authority"] = True
    md["orchestration_required"] = orch_required
    md["orchestration_decision_source"] = "decision-engine"
    md["orchestration_lifecycle_state"] = orch_lifecycle
    md["orchestration_intent"] = orchestration_intent
    md["risk_score"] = risk_score
    if decision_score is not None:
        md["decision_score"] = decision_score
    md["reason_codes"] = reason_codes
    md["policy_context"] = policy_context

    result.metadata = md
