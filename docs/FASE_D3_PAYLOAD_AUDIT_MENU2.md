# FASE D.3 — AUDITORIA REAL DE PAYLOAD E EXPOSIÇÃO CIENTÍFICA DO MENU 2

**Data:** 2026-03-17  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Endpoint auditado:** `POST /api/v1/sla/interpret` (backend trisla-portal-backend).

---

## 1. Payload real encontrado

Chamada de auditoria (a partir do cluster):

```bash
curl -s -X POST http://trisla-portal-backend.trisla.svc.cluster.local:8001/api/v1/sla/interpret \
  -H "Content-Type: application/json" \
  -d '{"intent_text":"cirurgia remota","tenant_id":"default"}'
```

**Resposta real (exemplo):**

```json
{
  "intent_id": "f0c15896-62f9-4d20-846c-a5692e6e11eb",
  "service_type": "URLLC",
  "semantic_class": "Serviço crítico de saúde remota",
  "profile_sla": "Latência ≤ 10 ms | Disponibilidade ≥ 99.999% | Alta confiabilidade",
  "template_id": "urllc-basic",
  "sla_requirements": {
    "latency": "10ms",
    "throughput": null,
    "reliability": 0.99999,
    "jitter": "5ms",
    "coverage": null
  },
  "sla_id": "f0c15896-62f9-4d20-846c-a5692e6e11eb",
  "status": "accepted",
  "tenant_id": "default",
  "nest_id": "nest-f0c15896-62f9-4d20-846c-a5692e6e11eb",
  "slice_type": "URLLC",
  "technical_parameters": {},
  "created_at": null,
  "message": "SLA interpretado pelo SEM-CSMF com sucesso."
}
```

---

## 2. Campos usados no frontend (após FASE D.3)

| Campo | Origem | Uso no Menu 2 |
|-------|--------|----------------|
| semantic_class | payload raiz | Painel Semantic Interpretation |
| profile_sla | payload raiz | Painel Semantic Interpretation |
| template_id | payload raiz | Painel Semantic Interpretation |
| service_type / slice_type | payload raiz | recommended slice (badge) |
| sla_requirements | objeto | Technical SLA Profile: apenas chaves com valor não null (latency, reliability, jitter no exemplo) |
| message | payload raiz | Não exibido em painel; disponível no JSON expandível |
| intent_id, sla_id, status, tenant_id, nest_id, technical_parameters, created_at | payload raiz | Apenas no JSON expandível (Technical Response Payload) |

---

## 3. Campos ausentes no backend (interpret)

Não presentes na resposta atual de `/api/v1/sla/interpret`:

- **confidence**
- **risk_score**
- **risk_level**
- **reason**
- **explanation**
- **ontology_consistency**
- **domain_viability**
- **blockchain_governance**
- **admission_decision**

Regra aplicada no frontend: não renderizar linha para campo ausente; nunca exibir "null" nem "Campo ainda não exposto neste endpoint".

---

## 4. Campos novos expostos / regra de renderização

- **Semantic Interpretation:** só linhas para semantic_class, profile_sla, template_id e recommended slice quando existirem e não forem null/vazio.
- **Technical SLA Profile:** painel só é renderizado se houver pelo menos uma chave em `sla_requirements` com valor não null; exibidas apenas latency, throughput, reliability, jitter, coverage quando presentes.
- **Explainable AI Reasoning:** painel só é renderizado se existir pelo menos um de: confidence, risk_score, risk_level, reason; labels "Confidence", "Risk Score", "Risk Level", "Reason".
- **Domain Viability / Blockchain Governance / Admission Decision:** painéis separados só se os campos existirem no payload (não existem no interpret atual).
- **Technical Response Payload:** JSON expandível mantido.

Nenhum dado inventado; nenhum mock; nenhum fallback artificial. Backend e endpoint não foram alterados.
