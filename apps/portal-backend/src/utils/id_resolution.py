"""
Resolução determinística decision_id → intent_id (PROMPT_SPORTAL_06_ID_RESOLUTION).
SEM-CSMF persiste por intent_id (<uuid>); Portal pode receber decision_id (dec-<uuid>).
Aplicar exclusivamente antes de chamadas GET /api/v1/intents/{id}.
"""


def resolve_intent_id(sla_id: str) -> str:
    """
    Resolve decision_id (dec-<uuid>) para intent_id (<uuid>).
    Determinística, reversível, stateless, sem I/O.
    """
    if sla_id.startswith("dec-"):
        return sla_id.replace("dec-", "", 1)
    return sla_id
