# Validação técnica completa — XAI no endpoint POST /api/v1/sla/submit

**Data:** 2025-03-17  
**Regras:** Sem alterar código, sem build, sem deploy. Apenas auditoria objetiva e evidência final.

---

## FASE 1 — Payload real mínimo de teste

**Arquivo:** `apps/portal-backend/src/routers/sla.py` (validação em `submit_sla_template` + schema em `apps/portal-backend/src/schemas/sla.py`)

### 1. template_id obrigatório?

**Sim.**  
- Schema: `template_id: str` com `@field_validator('template_id')` que levanta `ValueError('Template ID não pode ser vazio')` se vazio ou só espaços.  
- Router (linhas 148-152): `if not request.template_id or not request.template_id.strip(): raise HTTPException(400, ...)`.

### 2. tenant_id obrigatório?

**Não.**  
- Schema: `tenant_id: str = "default"`.  
- Não há validador que exija preenchimento; pode ser omitido no body.

### 3. form_values obrigatório?

**Sim.**  
- Schema: `form_values: Dict[str, Any]` com `@field_validator('form_values')` que faz `if not v: raise ValueError('Form values não podem ser vazios')`.  
- Router (linhas 154-157): `if not request.form_values: raise HTTPException(400, ...)`.

### 4. Campos internos mínimos obrigatórios em form_values?

**Nenhum exigido pelo schema.**  
- O validador só exige dict não vazio e filtra valores `None`, `"null"`, `"undefined"`; não exige chaves específicas.  
- Para o fluxo NASP completar sem erro, `nasp.submit_template_to_nasp` extrai `intent` de `nest_template.get("service_name")` ou `(nest_template.get("sla_requirements") or {}).get("service_name")`. Se nenhum existir, `intent` fica `None` e `call_sem_csmf(intent, tenant_id)` e depois `/intents` podem falhar ou retornar resposta incompleta. Para o fluxo end-to-end funcionar de forma previsível, é recomendável ter pelo menos uma chave em `form_values`; em muitos fluxos usa-se `service_name` ou `slice_type`/`type` para o SEM-CSMF.

### Payload mínimo correto

```json
{
  "template_id": "urllc-basic",
  "tenant_id": "default",
  "form_values": {
    "service_name": "URLLC low latency"
  }
}
```

Ou, sem `tenant_id` (usa default):

```json
{
  "template_id": "urllc-basic",
  "form_values": {
    "slice_type": "URLLC"
  }
}
```

`form_values` deve ser um objeto não vazio; para o pipeline NASP/SEM-CSMF completar com sucesso, convém incluir algo que permita obter `intent` e `service_type` (ex.: `service_name`, `slice_type` ou `type`).

---

## FASE 2 — Contrato final de resposta

**Fluxo:** `submit_sla_template` → `result = await nasp_service.submit_template_to_nasp(...)` → `return SLASubmitResponse(...)` com `response_model=SLASubmitResponse`.

**Schema atual:** `apps/portal-backend/src/schemas/sla.py` — classe `SLASubmitResponse`.

O JSON final esperado hoje (campos que podem aparecer na resposta) é:

- **Campos principais:** intent_id, service_type, sla_requirements, ml_prediction, decision, justification, reason, blockchain_tx_hash, tx_hash, sla_hash, timestamp, status  
- **Campos auxiliares:** sla_id, nest_id, sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status, block_number  
- **XAI profundo (já no schema):** reasoning, confidence, domains, metadata  

**Confirmação:** Sim. O contrato **pode incluir** reasoning, confidence, domains e metadata. Eles estão definidos em `SLASubmitResponse` (linhas 111-115) e são preenchidos no router com `result.get("reasoning")`, `result.get("confidence")`, `result.get("domains")`, `result.get("metadata")` (linhas 218-221). O JSON final pode portanto conter esses quatro campos sempre que o SEM-CSMF os enviar em `result`.

---

## FASE 3 — XAI atravessando todas as camadas

Fluxo traçado:

1. **Portal-backend** chama `nasp_service.submit_template_to_nasp(...)` e recebe `result = response.json()` do SEM-CSMF (`POST .../api/v1/intents`).
2. **SEM-CSMF** em `create_intent` retorna `IntentResponse(..., reasoning=decision_response.get("reasoning"), confidence=..., domains=..., metadata=...)`; esse JSON vira `result` no backend.
3. **decision_engine_client** (SEM-CSMF) em `send_nest_metadata` monta `decision_response` com `reasoning=result.get("reasoning")`, `confidence=result.get("confidence")`, `domains=result.get("domains")`, `metadata=result.get("metadata")` (do JSON do Decision Engine) e retorna esse dict; o SEM-CSMF usa esse dict para montar o `IntentResponse`.
4. **Decision Engine** em `/evaluate` retorna `DecisionResult` (FastAPI serializa) com os campos reasoning, confidence, domains, metadata.

**Resposta:** Sim. Os quatro campos podem chegar ao `return` final do portal-backend sem nova perda: Decision Engine → decision_engine_client → SEM-CSMF IntentResponse → portal-backend `result` → SLASubmitResponse(reasoning=..., confidence=..., domains=..., metadata=...). Não há camada que remova ou deixe de repassar esses campos entre o Decision Engine e o `return SLASubmitResponse(...)`.

---

## FASE 4 — Profundidade de metadata

**Onde metadata é preenchido:** Decision Engine (`apps/decision-engine/src/engine.py`): após `build_decision_snapshot` e `explain_decision`, faz:

- `decision_result.metadata["decision_snapshot"] = snapshot`  
- `decision_result.metadata["system_xai_explanation"] = explanation`

**Conteúdo do snapshot** (`apps/decision-engine/src/decision_snapshot.py`, `build_decision_snapshot`):

- `snapshot["domains"]` é um dict por domínio: **RAN**, **Transport**, **Core**.  
- Para cada um há estrutura com métricas e status, por exemplo:
  - **RAN:** latency_ms, throughput_mbps, reliability, status ("evaluated" | "unknown")
  - **Transport:** latency_ms, bandwidth_mbps, jitter_ms, status
  - **Core:** latency_ms, throughput_mbps, availability, status

**Resposta direta:**

- **metadata contém decision_snapshot?** Sim.  
- **metadata contém system_xai_explanation?** Sim.  
- **metadata contém domains snapshot?** Sim, dentro de `metadata["decision_snapshot"]["domains"]`.  
- **metadata já contém estrutura RAN / Transport / Core?** Sim. A chave `metadata["decision_snapshot"]["domains"]` é um objeto com exatamente as chaves **RAN**, **Transport** e **Core**, cada uma com o objeto de métricas e status descrito acima.

---

## FASE 5 — Classificação XAI final disponível ao frontend

| Campo      | Disponível ao frontend | Fonte |
|-----------|-------------------------|--------|
| decision  | Sim                     | SEM-CSMF (Decision Engine) → portal-backend SLASubmitResponse.decision |
| reasoning | Sim                     | SEM-CSMF (Decision Engine) → portal-backend SLASubmitResponse.reasoning |
| confidence| Sim                     | SEM-CSMF (Decision Engine) → portal-backend SLASubmitResponse.confidence |
| domains   | Sim                     | SEM-CSMF (Decision Engine) → portal-backend SLASubmitResponse.domains |
| metadata  | Sim                     | SEM-CSMF (Decision Engine) → portal-backend SLASubmitResponse.metadata |

Todos os cinco campos estão no contrato e no return do router; estão disponíveis ao frontend na resposta de `POST /api/v1/sla/submit` sempre que o pipeline (Decision Engine → SEM-CSMF) os preencher.

---

## FASE 6 — Frontend PNL já pode consumir XAI completo?

**Resposta: NÃO.**

- A **página PNL** usa **POST /api/v1/sla/interpret**, não `/submit`. O XAI completo (reasoning, confidence, domains, metadata) está na resposta de **/submit**. Portanto a página PNL, por si, não consome o XAI do submit.
- O frontend que consome **/submit** é a **página Template**. Contratualmente o backend já entrega reasoning, confidence, domains e metadata na resposta do submit. Porém:
  - O tipo `SubmitResponse` no Template (`apps/portal-frontend/src/app/template/page.tsx`) **não** declara reasoning, confidence, domains nem metadata.
  - Os cards do Template usam `result.reason`, `result.justification`, `result.ml_prediction` (e fallbacks); não leem ainda `result.reasoning`, `result.confidence`, `result.domains`, `result.metadata`.

Por isso, mesmo com o backend já enviando XAI completo no `/submit`, o frontend (Template) ainda não está preparado para consumir e exibir esses quatro campos. Até atualizar tipos e UI, a resposta é **NÃO**.

Se no futuro o Template for ajustado para ler esses campos, a fonte correta por card seria:

| Card                  | Fonte correta (resposta POST /submit) |
|-----------------------|----------------------------------------|
| XAI Metrics           | `result.confidence` (e opcionalmente `result.metadata?.decision_snapshot` para ml_risk_score, ml_risk_level, etc.) |
| XAI Reasoning         | `result.reasoning` (fallback: `result.reason` ou `result.justification`) |
| Domain Viability      | `result.domains` (lista) e/ou `result.metadata?.decision_snapshot?.domains` (RAN, Transport, Core com status e métricas) |
| Blockchain Governance | `result.tx_hash`, `result.block_number`, `result.bc_status`; opcionalmente `result.metadata` (ex. blockchain_tx_hash) |
| Admission Decision    | `result.decision` (ACCEPT/REJECT) |
| SLA Requirements      | `result.sla_requirements` |

---

## FASE 7 — Parar

Nenhuma alteração de código foi feita. Nenhum build nem deploy. Auditoria encerrada.
