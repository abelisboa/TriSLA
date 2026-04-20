# FASE D.4 — Auditoria de endpoints reais com XAI completo

**Data:** 2026-03-16  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Objetivo:** Descobrir quais endpoints reais do backend já retornam: `confidence`, `risk_score`, `risk_level`, `reason`, `domain_viability`, `admission_decision`, `blockchain_governance`. **Sem alterar backend.**

---

## 1. FASE 1 — Endpoints reais auditados

Auditoria das rotas sob `/api/v1/*` relacionadas a **sla**, **admission**, **xai**, **viability**, **lifecycle**.

### 1.1 Rotas efetivamente montadas no backend (código-fonte)

Com base em `apps/portal-backend/src/main.py` e nos routers existentes:

| Prefixo        | Router / Fonte     | Endpoints disponíveis |
|----------------|--------------------|------------------------|
| `/api/v1/sla`  | `routers/sla.py`   | `POST /interpret`, `POST /submit`, `GET /status/{sla_id}`, `GET /metrics/{sla_id}` |
| `/api/v1/modules` | `routers/modules.py` | (rotas do módulo de módulos) |
| `/api/v1/prometheus` | `routers/prometheus.py` | (métricas Prometheus) |
| `/api/v1/core-metrics` | `routers/core_metrics` | (métricas core) |
| `/api/v1/nasp` | `routers/nasp`     | (diagnósticos NASP; arquivo do router não encontrado no path esperado) |
| —              | `main.py` (inline) | `GET /api/v1/health`, `GET /api/v1/health/global`, `GET /api/v1/nasp/diagnostics` |

**Observação:** O router **XAI** (`routers/xai.py`) existe no repositório mas **não está incluído** em `main.py`, portanto **não há rotas `/api/v1/xai/*` expostas** no backend atual. Rotas de admission, viability ou lifecycle dedicadas não aparecem como routers separados montados em `main.py`.

### 1.2 Resumo dos endpoints relevantes para SLA / XAI / decisão

- **POST /api/v1/sla/interpret** — Interpretação de intenção (SEM-CSMF); entrada para o Menu 2.
- **POST /api/v1/sla/submit** — Submissão de template ao NASP (Decision Engine + pipeline); retorna decisão e metadados.
- **GET /api/v1/sla/status/{sla_id}** — Status do SLA.
- **GET /api/v1/sla/metrics/{sla_id}** — Métricas do SLA.

Nenhum endpoint dedicado a **admission**, **viability** ou **lifecycle** foi encontrado como rota separada; o fluxo de admissão está concentrado em `POST /api/v1/sla/submit`.

---

## 2. FASE 2 — Endpoint com payload mais rico em XAI que o interpret

- **POST /api/v1/sla/interpret** (usado no Menu 2): não retorna `confidence`, `risk_score`, `risk_level`, `reason`, `domain_viability`, `admission_decision` nem `blockchain_governance` (conforme `docs/FASE_D3_PAYLOAD_AUDIT_MENU2.md`).
- **POST /api/v1/sla/submit**: retorna **reason** (e **justification**) em nível raiz; retorna também **blockchain_tx_hash** / **tx_hash** (dados de blockchain, não um objeto “blockchain_governance”); o campo **ml_prediction** é um objeto opaco que repassa a resposta completa do Decision Engine e **pode** conter campos adicionais de XAI (ex.: confidence, risk_level) se o serviço externo os enviar — não estão, porém, definidos no schema `SLASubmitResponse` em nível raiz.

Conclusão: o endpoint com payload **mais rico em XAI** hoje é **POST /api/v1/sla/submit**, por expor **reason**/justification e **ml_prediction** (possível portador de mais campos XAI). Nenhum endpoint expõe em nível raiz todos os campos alvo (confidence, risk_score, risk_level, reason, domain_viability, admission_decision, blockchain_governance).

---

## 3. FASE 3 — Tabela comparativa de payloads

| Endpoint | Campos retornados (principais) | Campos XAI (objetivo) | Campos lifecycle / blockchain |
|----------|-------------------------------|------------------------|--------------------------------|
| **POST /api/v1/sla/interpret** | intent_id, service_type, semantic_class, profile_sla, template_id, sla_requirements, sla_id, status, tenant_id, nest_id, slice_type, technical_parameters, created_at, message | Nenhum (confidence, risk_score, risk_level, reason, domain_viability, admission_decision ausentes) | — |
| **POST /api/v1/sla/submit** | decision, **reason**, justification, semantic_class, profile_sla, sla_id, intent_id, service_type, sla_requirements, **ml_prediction**, blockchain_tx_hash, tx_hash, sla_hash, status, sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status, block_number, nest_id, timestamp | **reason** (e justification). Demais (confidence, risk_score, risk_level, domain_viability, admission_decision) não em nível raiz; podem existir dentro de **ml_prediction** conforme Decision Engine | blockchain_tx_hash, tx_hash, sla_hash, block_number, status dos módulos |
| **GET /api/v1/sla/status/{sla_id}** | sla_id, status, tenant_id, intent_id, nest_id, created_at, updated_at | — | status, created_at, updated_at |
| **GET /api/v1/sla/metrics/{sla_id}** | sla_id + métricas (conforme SLA-Agent/NASP) | — | — |

**Campos alvo da auditoria:**

| Campo alvo | /interpret | /submit (raiz) | /submit (ml_prediction) |
|------------|------------|----------------|--------------------------|
| confidence | ❌ | ❌ | ⚠️ possível se DE retornar |
| risk_score | ❌ | ❌ | ⚠️ possível se DE retornar |
| risk_level | ❌ | ❌ | ⚠️ possível se DE retornar |
| reason | ❌ | ✅ | ✅ (origem) |
| domain_viability | ❌ | ❌ | ⚠️ possível se DE retornar |
| admission_decision | ❌ | ❌ (há `decision`: ACCEPT/REJECT/RENEG) | ⚠️ possível se DE retornar |
| blockchain_governance | ❌ | ❌ (há tx_hash, sla_hash, bc_status) | — |

---

## 4. FASE 4 — Endpoint recomendado para Menu 2 ou fluxo seguinte

- **Menu 2 (interpretação sem submissão):** manter **POST /api/v1/sla/interpret** como fonte atual; ele não fornece XAI completo; o frontend deve exibir apenas os campos realmente presentes (conforme FASE D.3).
- **Fluxo de decisão / pós-submissão:** usar **POST /api/v1/sla/submit** como fonte de:
  - **reason** / justification (XAI textual),
  - **decision** (admission_decision semântico),
  - **blockchain_tx_hash**, **tx_hash**, **sla_hash**, **bc_status** (dados de governança/blockchain),
  - **ml_prediction** (consultar internamente se o Decision Engine já envia confidence, risk_score, risk_level, domain_viability e documentar quando houver evidência em ambiente real).

**Regra:** Nenhuma alteração no endpoint atual do interpret até que o endpoint escolhido para o fluxo (interpret ou submit) esteja validado com payload real em ambiente alvo. Nenhuma alteração de backend nesta fase — somente auditoria.

---

## 5. Payload real de referência (submit)

Schema de resposta do backend para **POST /api/v1/sla/submit** (`SLASubmitResponse` em `apps/portal-backend/src/schemas/sla.py`):

- **Campos principais:** intent_id, service_type, sla_requirements, ml_prediction, **decision**, **justification**, **reason**, blockchain_tx_hash, tx_hash, sla_hash, timestamp, status.
- **Auxiliares:** sla_id, nest_id, sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status, block_number.

O payload real de **POST /api/v1/sla/interpret** está documentado em `docs/FASE_D3_PAYLOAD_AUDIT_MENU2.md`.

---

## 6. Resumo executivo

| Item | Resultado |
|------|-----------|
| Endpoints encontrados (SLA/XAI) | POST /interpret, POST /submit, GET /status/{sla_id}, GET /metrics/{sla_id}. Router XAI não montado. |
| Endpoint com mais XAI que o interpret | **POST /api/v1/sla/submit** (reason + ml_prediction). |
| Campos XAI em nível raiz hoje | Apenas **reason** (e justification) em `/submit`. |
| Endpoint recomendado Menu 2 | Manter **/interpret** até validação; para decisão/XAI pós-submit usar **/submit**. |
| Alterações backend/frontend nesta fase | Nenhuma — somente auditoria. |
