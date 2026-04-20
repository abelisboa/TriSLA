# FASE E.2.1 — Auditoria real do submit do Menu 3 antes do polimento visual

**Data:** 2026-03-17  
**Objetivo:** Validar por que o resultado científico não aparece após clicar em "Generate SLA Template". Somente auditoria e correções mínimas de frontend; sem alterar backend. Sem polimento visual ainda.

---

## Regras absolutas

- Não alterar backend.
- Não alterar endpoint.
- Não alterar portal-backend.
- Não iniciar polimento visual.
- Ignorar logs externos: warning Amplitude, erro Sentry 403 (não pertencem ao TriSLA).

---

## 1. Auditoria de `TemplateSlaSection.tsx`

### 1.1 handleSubmit

| Item | Resultado |
|------|-----------|
| Botão possui onClick real | Sim — `onClick={handleSubmit}` (linha ~211). |
| Função async executa | Sim — `const handleSubmit = async () => { ... }`. |
| loading muda de estado | Sim — `setLoading(true)` no início, `setLoading(false)` no `finally`. |
| error é tratado | Sim — `catch (e)` com `setError(...)` e `setSubmitResult(null)`. |

### 1.2 Uso de `portalApi.slaSubmit`

- Chamada: `portalApi.slaSubmit(payload)` com `payload = { template_id, form_values, tenant_id }`.
- Endpoint real (api.ts): `POST /v1/sla/submit` (path relativo; base = `API_BASE` = `/api` → `/api/v1/sla/submit`).
- Payload real: `{ ...body, tenant_id: body.tenant_id ?? 'default' }`.
- Retorno: `postJson` retorna `body.data` se `body` tiver chave `'data'`, senão retorna `body`. O backend FastAPI devolve o objeto direto (sem wrapper `data`), então o frontend recebe o objeto da resposta.

### 1.3 Assinatura real de slaSubmit (api.ts)

- **Endpoint:** `postJson('/v1/sla/submit', { ...body, tenant_id: body.tenant_id ?? 'default' })`.
- **Payload:** `{ template_id: string; form_values: Record<string, unknown>; tenant_id?: string }`.
- **Retorno:** valor retornado por `postJson` — objeto JSON da resposta (decision, status, ml_prediction, tx_hash, sla_hash, bc_status, block_number, etc.) ou o que o backend enviar.

### 1.4 Retorno do backend (submit)

O backend (`routers/sla.py`) devolve `SLASubmitResponse` com, entre outros:

- decision, reason, justification, semantic_class, profile_sla, sla_id, intent_id, service_type, sla_requirements, **ml_prediction**, **blockchain_tx_hash**, **tx_hash**, **sla_hash**, status, sem_csmf_status, ml_nsmf_status, **bc_status**, sla_agent_status, **block_number**, nest_id, timestamp.

Não há wrapper `response.data` no backend; o FastAPI serializa o model direto. Portanto não há mismatch do tipo `response.data` vs `response` quando o backend é o padrão.

### 1.5 setSubmitResult

- Antes: `setSubmitResult(data as SubmitResponse)` — se `data` fosse `undefined` (ex.: resposta vazia ou falha de parse), o estado ficaria `undefined` e `submit != null` seria falso, e nenhum painel seria exibido.
- Ajuste: garantir que sempre se guarde um objeto quando a chamada não lançar:
  - `const result = response != null && typeof response === 'object' ? (response as SubmitResponse) : ({ _raw: response } as SubmitResponse);`
  - `setSubmitResult(result);`
  Assim, mesmo que a resposta seja inesperada (não objeto), o painel "Technical Response Payload" pode ser exibido e o valor inspecionado.

### 1.6 Condições de render

- Bloco dos painéis: `{submit != null && (<> ... </>)}` — exibe quando há resultado de submit.
- **Explainable AI:** `hasXai` = há confidence, risk_score, risk_level ou reason (em `ml_prediction` ou raiz).
- **Admission Decision:** `hasAdmission` = há decision ou status.
- **Blockchain Governance:** `hasBlockchain` = há tx_hash, blockchain_tx_hash, sla_hash, bc_status ou block_number.
- **Technical Response Payload:** sempre dentro do bloco `submit != null`; JSON expandível com o objeto `submit`.

Se o backend retornar 200 com corpo vazio ou não-JSON, `response.json()` pode lançar e o fluxo cai no `catch`; aí só a mensagem de erro aparece. Se retornar 200 com `{}`, `submitResult` passa a ser `{}`, os flags hasXai/hasAdmission/hasBlockchain ficam falsos e apenas o card "Technical Response Payload" com `{}` aparece.

---

## 2. Logs temporários inseridos

Para auditoria em runtime:

- `console.log('SUBMIT PAYLOAD', payload)` — imediatamente antes de `portalApi.slaSubmit(payload)`.
- `console.log('SUBMIT RESPONSE', response)` — logo após `await portalApi.slaSubmit(payload)`.
- `console.log('SUBMIT ERROR', e)` — no `catch`, para inspecionar falhas de rede, 4xx/5xx ou parse.

Permite confirmar: payload enviado, forma da resposta e erros que impedem a atualização de `submitResult`.

---

## 3. Diff aplicado (resumo)

- Construção do payload em variável `payload` e uso em `portalApi.slaSubmit(payload)`.
- Inclusão de `console.log('SUBMIT PAYLOAD', payload)` antes da chamada.
- Variável `response` para o retorno de `portalApi.slaSubmit(payload)` e `console.log('SUBMIT RESPONSE', response)` após o await.
- Cálculo de `result`: se `response` for objeto não nulo, usa `response`; senão usa `{ _raw: response }` para não deixar o estado `undefined` em respostas inesperadas.
- `setSubmitResult(result)` em vez de `setSubmitResult(data as SubmitResponse)`.
- No `catch`, `console.log('SUBMIT ERROR', e)`.

Nenhuma alteração de backend, endpoint ou portal-backend; apenas frontend para auditoria e tratamento seguro da resposta.

---

## 4. Próximo passo

Somente após o submit real aparecer (painéis ou ao menos "Technical Response Payload" com o JSON da resposta), seguir para **FASE E.3** (polimento visual). Não buildar nesta fase.
