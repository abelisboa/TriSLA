# Auditoria completa — Fluxo XAI profundo ponta a ponta (TriSLA)

**Data:** 2025-03-17  
**Escopo:** Portal frontend → portal-backend → SEM-CSMF → Decision Engine → ML → Blockchain → retorno ao portal  
**Regras:** Sem build, sem deploy, sem alteração de arquitetura, sem novos endpoints. Apenas auditoria e evidência objetiva.

---

## FASE 1 — Fluxo real de submissão SLA

### Endpoint que recebe a submissão principal (usado pelo frontend)

| Item | Evidência |
|------|-----------|
| **Arquivo** | `apps/portal-backend/src/routers/sla.py` |
| **Função** | `submit_sla_template` |
| **Rota real** | `POST /api/v1/sla/submit` (prefix do router: `/api/v1/sla`, rota do handler: `/submit`) |

**Evidência de código:**

- `apps/portal-backend/src/main.py` linha 77:  
  `app.include_router(sla.router, prefix="/api/v1/sla", tags=["SLA"])`
- `apps/portal-backend/src/routers/sla.py` linhas 134-135:  
  `@router.post("/submit", response_model=SLASubmitResponse)`  
  `async def submit_sla_template(request: SLASubmitRequest):`

**Frontend:** Template page chama `apiRequest<SubmitResponse>("SLA_SUBMIT", { method: "POST", body: { template_id, tenant_id, form_values } })`; em `api.ts` o path é `'/sla/submit'`; com `API_BASE = '/api'` o request vai para **`POST /api/v1/sla/submit`** (conforme `apps/portal-frontend/src/lib/endpoints.ts`: `SLA_SUBMIT: "/api/v1/sla/submit"` e uso em `apiRequest`).

**Conclusão FASE 1:** O fluxo usado é **`/api/v1/sla/submit`**.

---

## FASE 2 — Auditoria portal-backend (submit)

### Onde recebe

- O backend recebe o resultado do NASP em `result = await nasp_service.submit_template_to_nasp(...)`.
- `submit_template_to_nasp` em `apps/portal-backend/src/services/nasp.py` faz POST a `http://trisla-sem-csmf:8080/api/v1/intents` e devolve `return response.json()`.
- Portanto **`result`** é exatamente o JSON retornado pelo SEM-CSMF (IntentResponse): `intent_id`, `status`, `nest_id`, `decision`, `message`, `reasoning`, `confidence`, `domains`, `metadata`.

### Onde transforma

- `apps/portal-backend/src/routers/sla.py` linhas 198-218: monta `SLASubmitResponse(...)` com:
  - `reason=result.get("reason") or result.get("justification", "")`  → IntentResponse não tem `reason` nem `justification`, então fica `""`.
  - `justification=result.get("justification") or result.get("reason", "")`  → idem `""`.
  - `ml_prediction=result.get("ml_prediction")`  → SEM-CSMF não retorna `ml_prediction`, fica `None`.
  - **Não** há mapeamento de `result.get("reasoning")`, `result.get("confidence")`, `result.get("domains")`, `result.get("metadata")` para nenhum campo da resposta.

### Onde devolve

- Resposta é `SLASubmitResponse` serializada (FastAPI `response_model=SLASubmitResponse`).
- Schema em `apps/portal-backend/src/schemas/sla.py` (linhas 82-111): **não** declara `reasoning`, `confidence`, `domains`, nem `metadata` em nível raiz; declara `reason`, `justification`, `ml_prediction` (opcional).

**Conclusão FASE 2:** O backend **recebe** os quatro campos XAI em `result` (vindos do SEM-CSMF), **não os transforma** para a resposta (não constam em `SLASubmitResponse` e não são repassados em `reason`/`justification`/`ml_prediction`), e **não devolve** reasoning, confidence, domains nem metadata ao cliente. **Há perda no portal-backend.**

---

## FASE 3 — Auditoria SEM-CSMF

### IntentResponse contém os quatro campos

**Arquivo:** `apps/sem-csmf/src/models/intent.py`

**Bloco completo da classe IntentResponse (linhas 84-96):**

```python
class IntentResponse(BaseModel):
    """Resposta de criação de intent"""
    intent_id: str
    status: str
    nest_id: Optional[str] = None
    decision: Optional[str] = None
    message: str
    # XAI profundo (repassado do Decision Engine)
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    domains: Optional[list] = None
    metadata: Optional[dict] = None
```

### main.py repassa os quatro campos

**Arquivo:** `apps/sem-csmf/src/main.py`  
**Bloco completo do return IntentResponse (linhas 303-313):**

```python
        return IntentResponse(
            intent_id=intent.intent_id,
            status="accepted",
            nest_id=nest.nest_id,
            decision=decision_response.get("decision"),
            message=f"Intent processed and NEST generated. Decision Engine: {decision_response.get('message', 'N/A')}",
            reasoning=decision_response.get("reasoning"),
            confidence=decision_response.get("confidence"),
            domains=decision_response.get("domains"),
            metadata=decision_response.get("metadata"),
        )
```

**Conclusão FASE 3:** SEM-CSMF expõe e repassa reasoning, confidence, domains e metadata. Contrato e implementação alinhados.

---

## FASE 4 — Auditoria Decision Engine (/evaluate)

### Endpoint e modelo de resposta

- **Arquivo:** `apps/decision-engine/src/main.py`  
- **Rota:** `@app.post("/evaluate", response_model=DecisionResult)` (linha 251)  
- **Handler:** `evaluate_sla(sla_input: SLAEvaluateInput)`; chama `decision_service.process_decision_from_input(decision_input)` e retorna `decision_result` (FastAPI serializa via `DecisionResult`).

### JSON real devolvido (modelo DecisionResult)

**Arquivo:** `apps/decision-engine/src/models.py` (classe `DecisionResult`, linhas 90-134)

Campos do modelo (e portanto do JSON):

- `decision_id`, `intent_id`, `nest_id`, `action`, `reasoning`, `confidence`, `ml_risk_score`, `ml_risk_level`, `slos`, `domains`, `metadata`, `timestamp`.

**Contém os quatro campos XAI:**

- **reasoning:** `str` (obrigatório)
- **confidence:** `float` (obrigatório, 0.0–1.0)
- **domains:** `Optional[List[str]]` (ex.: `["RAN", "Transporte", "Core"]`)
- **metadata:** `Optional[Dict[str, Any]]` (pode conter `decision_snapshot`, `system_xai_explanation`, `blockchain_tx_hash`, etc.)

**Conclusão FASE 4:** O JSON de `POST /evaluate` contém reasoning, confidence, domains e metadata.

---

## FASE 5 — Profundidade real dos domínios

### No nível do DecisionResult (resposta /evaluate)

- **`domains`** é uma **lista de strings**: `["RAN", "Transporte", "Core"]` (ou subconjunto). Não há, nesse nível, estrutura por domínio com status, reason, metrics, source.

### Estrutura rica por domínio (status, metrics)

- A estrutura por domínio (status, métricas) está em **`metadata["decision_snapshot"]["domains"]`**, construída em `apps/decision-engine/src/decision_snapshot.py` (função `build_decision_snapshot`).
- Para cada domínio (**RAN**, **Transport**, **Core**):

  - **RAN:** `latency_ms`, `throughput_mbps`, `reliability`, `status` ("evaluated" | "unknown").
  - **Transport:** `latency_ms`, `bandwidth_mbps`, `jitter_ms`, `status`.
  - **Core:** `latency_ms`, `throughput_mbps`, `availability`, `status`.

- Não há campo explícito `reason` nem `source` por domínio no snapshot; o snapshot inclui `bottleneck_domain` e `bottleneck_metric` derivados da `reasoning` textual.

**Resumo por domínio:**

| Domínio   | status | reason (explícito) | metrics | source (explícito) |
|----------|--------|--------------------|---------|--------------------|
| RAN      | sim    | não                | sim     | não                |
| Transport| sim    | não                | sim     | não                |
| Core     | sim    | não                | sim     | não                |

**Conclusão FASE 5:** Em nível top-level, `domains` é apenas lista de strings. A profundidade (status + metrics por domínio) existe dentro de `metadata.decision_snapshot.domains`; não há campo dedicado `reason` ou `source` por domínio.

---

## FASE 6 — Blockchain no XAI (metadata)

### Onde o blockchain poderia aparecer

- **Decision Engine:** `apps/decision-engine/src/engine.py`: se `blockchain_tx_hash` for retornado pelo BC, é colocado em `decision_result.metadata["blockchain_tx_hash"]`. O código atual tem `blockchain_tx_hash = None` e `# TODO: Implement blockchain registration` (linhas 133-136), portanto hoje **não** há tx_hash real em metadata.
- **decision_engine_client (SEM-CSMF):** repassa `metadata=result.get("metadata")`; se o Decision Engine incluir no `metadata` campos como `tx_hash`, `block_number`, `bc_status`, eles fluiriam no dict até o SEM-CSMF.

### Campos típicos de evidência blockchain

- **tx_hash / blockchain_tx_hash:** não preenchido no fluxo atual (BC não integrado no retorno do /evaluate).
- **block_number:** não encontrado no modelo DecisionResult nem no snapshot; poderia ser adicionado ao metadata pelo BC.
- **bc_status:** idem; não presente no payload do Decision Engine hoje.
- **trust evidence:** não modelado explicitamente; poderia ser parte de `metadata` no futuro.

**Conclusão FASE 6:** Hoje **metadata não contém evidência real de blockchain** (tx_hash/block_number/bc_status) no caminho Decision Engine → SEM-CSMF, pois o registro em BC não está implementado no retorno do /evaluate. O contrato do portal (SLASubmitResponse) tem `blockchain_tx_hash`, `tx_hash`, `block_number` em nível raiz, mas são preenchidos a partir de `result.get("tx_hash")` etc.; como o SEM-CSMF não repassa esses nomes em nível raiz, ficam None na resposta do submit.

---

## FASE 7 — Contrato final visível ao frontend

### Endpoint consumido pelo frontend

- **POST /api/v1/sla/submit** (resposta = `SLASubmitResponse`).

### O endpoint já entrega reasoning, confidence, domains, metadata sem perda?

**Não.** O schema `SLASubmitResponse` não declara `reasoning`, `confidence`, `domains` nem `metadata`. O router monta a resposta apenas com os campos do schema; os quatro campos XAI existem em `result` (vindos do SEM-CSMF) mas não são copiados para a resposta. Portanto há **perda intermediária** no portal-backend.

### JSON final real (forma típica hoje)

Com base em `SLASubmitResponse` e no mapeamento do router (linhas 198-218), a resposta tem a forma (exemplo):

```json
{
  "decision": "ACCEPT",
  "reason": "",
  "justification": "",
  "sla_id": null,
  "timestamp": null,
  "intent_id": "<do SEM-CSMF>",
  "service_type": "<do SEM-CSMF>",
  "sla_requirements": { ... },
  "ml_prediction": null,
  "blockchain_tx_hash": null,
  "tx_hash": null,
  "sla_hash": null,
  "status": "ok",
  "sem_csmf_status": "ERROR",
  "ml_nsmf_status": "ERROR",
  "bc_status": "ERROR",
  "sla_agent_status": "SKIPPED",
  "block_number": null,
  "nest_id": "<do SEM-CSMF>"
}
```

**reasoning, confidence, domains e metadata não aparecem** nesse JSON. O frontend (template page) tenta exibir reasoning/confidence via `result.ml_prediction` e fallback para `result.reason`/`result.justification`; como `ml_prediction` é null e reason/justification vazios, o bloco XAI fica em branco ("—").

---

## FASE 8 — Diagnóstico final

### Tabela por camada

| Camada            | reasoning | confidence | domains | metadata | perda?        |
|-------------------|-----------|------------|---------|----------|---------------|
| Decision Engine   | sim       | sim        | sim     | sim      | —             |
| decision_engine_client (SEM-CSMF) | sim | sim        | sim     | sim      | não           |
| SEM-CSMF (IntentResponse) | sim | sim        | sim     | sim      | não           |
| Portal-backend (result)   | sim (recebido) | sim | sim | sim | — (dados presentes em `result`) |
| Portal-backend (resposta SLASubmitResponse) | não | não | não | não | **sim** |
| Frontend (JSON recebido) | não | não | não | não | **sim** (herda da resposta) |

### Classificação do XAI hoje

- **Superficial:** O frontend recebe apenas decision, reason (vazio), justification (vazio), ml_prediction (null). Não há explicação nem confiança expostas.
- **Parcial:** Decision Engine e SEM-CSMF têm e repassam reasoning, confidence, domains e metadata; a perda ocorre apenas no portal-backend ao montar `SLASubmitResponse`.
- **Profundo multi-domínio:** Não realizado até o frontend: domains (lista e snapshot por RAN/Transport/Core) e metadata (incl. decision_snapshot) existem no Decision Engine e até no SEM-CSMF, mas não são expostos no contrato final do submit.

---

## FASE 9 — Parar

Nenhuma correção foi aplicada. Auditoria encerrada.
