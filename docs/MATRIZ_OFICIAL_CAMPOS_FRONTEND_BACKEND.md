# Matriz oficial — Campos frontend ↔ backend (Template / Submit)

**Fonte:** SLASubmitResponse (portal-backend `schemas/sla.py`) + payload ML-NSMF/Decision (submit pipeline).  
**Regra:** Só renderizar campos REAL, HÍBRIDO ou TRANSITÓRIO; nunca GAP inventado.

---

## Campos oficiais para /template (FASE D)

| Campo | Origem backend | Bloco | Estado |
|-------|----------------|-------|--------|
| decision | routers/sla.py → result.get("decision") | B. Admission Decision | REAL |
| reason / justification | result.get("reason"), result.get("justification") | B. Admission Decision | REAL |
| sla_id | result.get("sla_id") | A. Semantic Result | REAL |
| intent_id | result.get("intent_id") | A. Semantic Result | REAL |
| nest_id | result.get("nest_id") | A. Semantic Result | REAL |
| service_type | result.get("service_type") | A. Semantic Result | REAL |
| timestamp | result.get("timestamp") | A. Semantic Result | REAL |
| sla_requirements | result.get("sla_requirements") | A / C | REAL |
| ml_prediction (confidence, risk_level, viability_score, reasoning, features_importance) | result.get("ml_prediction") — ML-NSMF / submit payload | C. XAI Scientific Result | REAL quando pipeline envia |
| tx_hash | result.get("tx_hash") / blockchain_tx_hash | D. Blockchain Evidence | REAL |
| block_number | result.get("block_number") | D. Blockchain Evidence | REAL |
| bc_status | result.get("bc_status") | D. Blockchain Evidence | REAL |

---

## Blocos obrigatórios (layout científico)

- **A. Semantic Result** — sla_id, intent_id, nest_id, service_type, timestamp; sla_requirements.
- **B. Admission Decision** — decision, reason, justification (reasoning).
- **C. XAI Scientific Result** — confidence, risk_level, viability_score, reasoning, features_importance (extraídos de ml_prediction).
- **D. Blockchain Evidence** — tx_hash, block_number, bc_status (sem status agregado inventado).

---

## Proibido

- final lifecycle (agregado inventado)
- aggregated status (inventado)
- simulated governance
- synthetic runtime
- Campos não rastreáveis: backend → matriz → frontend = NÃO IMPLEMENTAR.
