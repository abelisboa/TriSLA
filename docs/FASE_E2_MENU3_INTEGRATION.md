# FASE E.2 — Integrar Menu 3 (Template SLA) ao fluxo científico validado no Menu 2

**Data:** 2026-03-17  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Objetivo:** Transformar `TemplateSlaSection.tsx` de formulário estático em fluxo científico real, reutilizando somente `POST /api/v1/sla/submit`. Sem alterar backend.

---

## Regras absolutas

- Não alterar backend.
- Não criar endpoint novo.
- Não tocar portal-backend.
- Reutilizar somente o endpoint já estável: **`/api/v1/sla/submit`**.

---

## 1. Endpoint reutilizado

- **`portalApi.slaSubmit`** (chama `POST /api/v1/sla/submit`).
- Payload: `{ template_id, form_values, tenant_id }`.

---

## 2. Mapeamento de campos (form → form_values)

| Campo do form | Mapeamento | Observação |
|---------------|------------|------------|
| slice (URLLC / eMBB / mMTC) | template_id: `urllc-basic` / `embb-basic` / `mmtc-basic`; form_values.slice_type, type, service_type | Valor do slice mantido para slice_type/type/service_type |
| latency | form_values.latency_ms | String com "ms" (ex.: "5ms") se não contiver "ms" |
| throughput | form_values.throughput_mbps | String (ex.: "100") |
| availability | form_values.reliability | Convertido de % para 0–1 (ex.: 99.99 → 0.9999) |
| — | form_values.jitter_ms | Fixo: 1 |
| — | form_values.coverage_area | Fixo: "factory-floor" |

Payload enviado (estrutura):

```json
{
  "template_id": "urllc-basic",
  "form_values": {
    "slice_type": "URLLC",
    "type": "URLLC",
    "service_type": "URLLC",
    "latency_ms": "5ms",
    "throughput_mbps": "100",
    "reliability": 0.9999,
    "jitter_ms": 1,
    "coverage_area": "factory-floor"
  },
  "tenant_id": "default"
}
```

---

## 3. Fluxo no Menu 3

1. Utilizador preenche: Slice, Latency, Throughput, Availability.
2. Clica em **Generate SLA Template**.
3. O botão chama **handleSubmit** (async):
   - Deriva `template_id` do slice (urllc-basic / embb-basic / mmtc-basic).
   - Monta `form_values` com o mapeamento acima.
   - Chama `portalApi.slaSubmit({ template_id, form_values, tenant_id })`.
4. Resposta do submit é guardada em estado e os painéis científicos são exibidos.

---

## 4. Painéis científicos (igual ao Menu 2)

Exibidos quando há resposta de submit (somente dados reais; campos ausentes não renderizam):

- **Explainable AI Reasoning:** Confidence (4 dec.), Risk Score (4 dec.), Risk Level, Reason (multilinha por sentença).
- **Admission Decision:** decision, status.
- **Blockchain Governance:** tx_hash, sla_hash, bc_status, block_number.
- **Technical Response Payload:** JSON expandível com o payload completo do submit.

---

## 5. Alterações em `TemplateSlaSection.tsx`

- **Antes:** Formulário estático; botão sem handler; nenhuma chamada à API.
- **Depois:** Estado `loading`, `error`, `submitResult`; `handleSubmit` async que chama `portalApi.slaSubmit`; mapeamento slice → template_id e form → form_values; exibição dos painéis Explainable AI, Admission Decision, Blockchain Governance e Technical Response Payload, reutilizando a mesma lógica de exibição do Menu 2 (hasValue, roundTo4, xaiFromMlPrediction, RealField, etc.), adaptada no próprio componente sem alterar PnlSlaSection.

---

## 6. Regra final

- Sem inventar backend.
- Sem alterar fluxo científico já consolidado no Menu 2.
- Sem build nesta fase (conforme solicitado).
