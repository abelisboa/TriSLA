# FASE E.1 — Auditoria e alinhamento científico do Menu 3 (Criar SLA Template)

**Data:** 2026-03-17  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Objetivo:** Elevar Menu 3 ao mesmo padrão científico do Menu 2. **Esta fase é somente auditoria — nenhuma alteração.**

---

## 1. FASE 1 — Auditoria real do Menu 3 atual

**Componente:** `apps/portal-frontend/src/sections/TemplateSlaSection.tsx`  
**Rota no app:** `page.tsx` → `selected === 'Criar SLA Template'` → `<TemplateSlaSection />`.

### 1.1 Endpoint usado

| Item | Resultado |
|------|-----------|
| Endpoint | **Nenhum** |
| Observação | O botão "Generate SLA Template" **não possui handler** (sem `onClick`). Nenhuma chamada a `portalApi` ou a qualquer endpoint. |

### 1.2 Payload enviado

| Item | Resultado |
|------|-----------|
| Payload enviado | **N/A** — formulário não submete dados a nenhum serviço. |

### 1.3 Payload retornado

| Item | Resultado |
|------|-----------|
| Payload retornado | **N/A** — não há resposta de API. |

### 1.4 Campos reais existentes (estado local do componente)

Campos presentes **apenas no estado React** (não enviados ao backend):

| Campo | Tipo | Valor inicial | Uso atual |
|-------|------|---------------|-----------|
| slice | string | `'URLLC'` | Select (URLLC, eMBB, mMTC) |
| latency | string | `'5'` | Input texto |
| throughput | string | `'100'` | Input texto |
| availability | string | `'99.99'` | Input texto |

Não há: `template_id`, `form_values`, `tenant_id`, `reliability`, `jitter`, `coverage`; não há integração com backend.

---

## 2. FASE 2 — Comparar com Menu 2

### 2.1 Menu 2 (Criar SLA PNL) — fluxo atual

- **Interpret:** `POST /api/v1/sla/interpret` com `{ intent_text, tenant_id }`.
- **Submit:** `POST /api/v1/sla/submit` com `{ template_id, form_values, tenant_id }` derivados do retorno do interpret.
- Payload submit: `template_id` (ex.: urllc-basic), `form_values` (sla_requirements + type/slice_type/service_type), `tenant_id`.

### 2.2 Menu 3 usa /api/v1/sla/submit ou fluxo equivalente?

| Pergunta | Resposta |
|----------|----------|
| Menu 3 chama `/api/v1/sla/submit`? | **Não** |
| Menu 3 chama qualquer outro endpoint SLA? | **Não** |
| Fluxo equivalente (interpret + submit ou submit direto)? | **Não** — nenhum fluxo de submissão implementado. |

**Conclusão:** O Menu 3 **não** utiliza `POST /api/v1/sla/submit` nem fluxo equivalente. É um formulário estático sem integração com o backend.

---

## 3. FASE 3 — Identificar gaps

Tabela de comparação: Menu 2 (padrão científico atual) vs Menu 3 (Criar SLA Template).

| Categoria | Menu 2 (Criar SLA PNL) | Menu 3 (Criar SLA Template) | Gap |
|-----------|------------------------|-----------------------------|-----|
| **Campos técnicos** | latency, throughput, reliability, jitter, coverage (de interpret + submit); formatados (ex.: reliability 99.999%) | latency, throughput, availability apenas no estado local; não enviados; faltam reliability, jitter, coverage, template_id, form_values | Menu 3 não envia campos técnicos; não há template_id nem form_values; nomenclatura availability vs reliability |
| **Campos semânticos** | semantic_class, profile_sla, template_id, recommended slice (de interpret) | Nenhum | Menu 3 não exibe nem obtém semantic_class, profile_sla, template_id, slice recomendado |
| **XAI** | Explainable AI Reasoning (confidence, risk_score, risk_level, reason de submit/ml_prediction) | Nenhum | Menu 3 não chama submit; não há XAI |
| **Decision** | Admission Decision (decision, status de submit) | Nenhum | Menu 3 não exibe decisão de admissão |
| **Blockchain** | Blockchain Governance (tx_hash, sla_hash, bc_status, block_number de submit) | Nenhum | Menu 3 não exibe dados de blockchain |
| **Endpoint** | POST /interpret + POST /submit | Nenhuma chamada | Menu 3 não usa endpoint |
| **Payload retornado** | interpret + submit com painéis científicos | Nenhum | Menu 3 não exibe resposta da API |
| **Technical Response Payload** | JSON expandível (interpret + submit) | Nenhum | Menu 3 não tem payload técnico |

**Resumo dos gaps:** O Menu 3 não possui integração com backend, não utiliza `/api/v1/sla/submit`, não exibe campos semânticos, XAI, decision nem blockchain, e não segue o padrão de painéis científicos do Menu 2.

---

## 4. Alinhamento científico desejado (referência para fases futuras)

Para elevar o Menu 3 ao padrão do Menu 2 (sem alterar nesta fase):

1. **Fluxo:** Ao submeter o template no Menu 3, chamar `POST /api/v1/sla/submit` com:
   - `template_id`: derivado do slice (ex.: urllc-basic, embb-basic, mmtc-basic),
   - `form_values`: latency, throughput, availability/reliability, type/slice_type, etc.,
   - `tenant_id`: ex.: default.
2. **Painéis:** Exibir os mesmos painéis científicos que o Menu 2 quando houver resposta do submit: Technical SLA Profile, Explainable AI Reasoning, Admission Decision, Blockchain Governance, Domain Viability (se existir), Technical Response Payload.
3. **Campos:** Alinhar nomes e formatos (reliability, latency, jitter, etc.) ao contrato real do backend e ao Menu 2.

---

## 5. Regra final

- **Nenhuma alteração** nesta fase.
- **Somente auditoria.**
