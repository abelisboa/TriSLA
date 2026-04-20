# FASE F.1 — Auditoria científica do Menu 4 (SLA Lifecycle)

**Data:** 2026-03-17  
**Objetivo:** Descobrir se o Menu 4 usa dados reais ou mockados e qual o gap científico atual. Sem alterar backend, endpoint ou frontend; somente auditoria.

---

## Regra absoluta

- Não alterar backend.
- Não alterar endpoint.
- Não alterar frontend ainda.
- Primeiro auditar fonte real de dados.

---

## 1. Arquivo real e estrutura

**Arquivo:** `apps/portal-frontend/src/sections/SlaLifecycleSection.tsx`

### 1.1 Hooks e estados

| Item | Uso |
|------|-----|
| `useState<SLA[]>([])` | `items` — lista de SLAs exibida na tabela; inicialmente array vazio. |
| `useEffect` | Uma vez no mount: chama `load()` assínrona; em `load()` chama `portalApi.slaList()`, aplica `safeArray<SLA>(data)` e faz `setItems(...)`; em caso de erro faz `setItems([])`. Dependências `[]`. |

Não há outro estado (filtros, paginação, loading explícito, error state).

### 1.2 Endpoint chamado

- **Função:** `portalApi.slaList()`
- **Implementação (api.ts):** `slaList: () => fetchJson('/v1/sla')`
- **Requisição real:** `GET ${API_BASE}/v1/sla` → com `API_BASE = '/api'` (env), resulta em **GET /api/v1/sla**.

---

## 2. Fonte de dados: backend real ou mock?

### 2.1 Backend — existência da rota GET /api/v1/sla

No backend (`apps/portal-backend/src/routers/sla.py`) as rotas sob o prefixo `/api/v1/sla` são:

- `POST /interpret`
- `POST /submit`
- `GET /status/{sla_id}`
- `GET /metrics/{sla_id}`

**Não existe** rota `GET /` (ou `GET ""`) no router `sla`. Portanto **GET /api/v1/sla não está definido** e retorna **404**.

### 2.2 Comportamento no frontend

- O componente **não** usa mock nem array estático em código.
- Chama de fato a API: `portalApi.slaList()` → GET /api/v1/sla.
- Como o endpoint não existe: a resposta é 404, `fetchJson` lança `new Error('HTTP 404')`, o `catch` em `load()` é executado e `setItems([])`.
- Resultado: a tabela fica **sempre vazia** (“No SLA records available”), com dados vindos de uma **chamada real que falha**, não de mock estático.

**Conclusão:** Fonte de dados é **chamada real** a um endpoint que **não existe** no backend atual; os dados exibidos são, na prática, **sempre vazios**.

---

## 3. Função de API que abastece SLA Lifecycle

| Aspecto | Valor |
|---------|--------|
| Função | `portalApi.slaList()` |
| Arquivo | `apps/portal-frontend/src/lib/api.ts` |
| Implementação | `slaList: () => fetchJson('/v1/sla')` |
| Método HTTP | GET |
| Path completo (com API_BASE) | GET /api/v1/sla |
| Backend | Rota **não implementada** (404). |

---

## 4. Payload real

- **Request:** GET sem body. Sem query params no código.
- **Response esperada pelo frontend:** um array (ou objeto com array) para `safeArray()`; se o backend retornar `body.data`, `fetchJson` já devolve `body.data`; senão devolve `body`.
- **Response real atual:** 404 (rota inexistente), logo não há payload de sucesso; o frontend só recebe erro e zera a lista.

---

## 5. Colunas atuais mapeadas

A tabela e o tipo `SLA` estão alinhados às colunas abaixo:

| Coluna na UI | Campo no tipo `SLA` | Origem esperada |
|--------------|---------------------|------------------|
| SLA ID | `id` | Resposta da API (lista de SLAs) |
| Slice Type | `slice_type` | Idem |
| State | `state` | Idem |
| Admission | `admission` | Idem |
| Blockchain | `blockchain` | Idem |
| NASP | `nasp` | Idem |
| Runtime | `runtime` | Idem |

Não há mapeamento para nomes diferentes (ex.: `sla_id` vs `id`); o componente espera exatamente esses campos. Nenhuma coluna é preenchida por mock no código; todas dependem da resposta de `slaList()`.

---

## 6. Comparação com o fluxo científico TriSLA

Fluxo científico de referência:

- **Semantic admission** — interpretação semântica e decisão de admissão (ex.: interpret + submit).
- **ML decision** — decisão/risk/confidence do ML/Decision Engine (submit/ml_prediction).
- **Blockchain commit** — registro em blockchain (tx_hash, sla_hash, bc_status, block_number).
- **Deployment state** — estado de implantação no NASP (ex.: ACTIVE, PENDING).
- **Monitoring state** — estado de monitoramento / runtime (métricas, saúde).

Comparação com o Menu 4 (SLA Lifecycle):

| Conceito científico | Coluna / dado no Menu 4 | Situação |
|---------------------|--------------------------|----------|
| Semantic admission | Admission | Campo previsto; sem endpoint de lista, sem dados. |
| ML decision | (não exposto) | Não há coluna específica para decisão/confidence/risk do ML. |
| Blockchain commit | Blockchain | Campo previsto; sem dados por falta de endpoint. |
| Deployment state | State | Campo previsto; sem dados. |
| Monitoring state | Runtime (e possivelmente NASP) | Campos previstos; sem dados. |
| Identificação | SLA ID, Slice Type | Campos previstos; sem dados. |

Ou seja: a **intenção** da tabela é compatível com o fluxo (admission, state, blockchain, runtime), mas **não há backend** que forneça essa lista e **não há** coluna explícita para “ML decision”.

---

## 7. Gaps identificados

### 7.1 Endpoint

- **Gap:** Não existe **GET /api/v1/sla** (listagem de SLAs) no backend.
- **Efeito:** A lista do Menu 4 está sempre vazia; não há “dados mockados”, apenas falha silenciosa (catch → `[]`).

### 7.2 Campos ausentes no desenho atual

- **ML decision / XAI:** Nenhuma coluna para decisão ML, confidence, risk_level ou reason (alinhado ao submit).
- **Semantic class / profile:** Nenhuma coluna para classe semântica ou perfil SLA (alinhado ao interpret).
- **IDs de rastreio:** Não está explícito no tipo se `id` deve ser `sla_id`, `intent_id` ou outro identificador único do pipeline.

### 7.3 Colunas não mockadas, mas sem dados

- Todas as colunas (SLA ID, Slice Type, State, Admission, Blockchain, NASP, Runtime) dependem de uma resposta de lista que **nunca chega** (404). Nenhuma é preenchida por array estático ou mock no frontend.

### 7.4 Ausência de atualização real

- **useEffect** roda uma vez no mount; não há polling, refetch, nem dependências que atualizem a lista quando outro menu (ex.: submit no Menu 2/3) criar um novo SLA. A lista não reflete o estado real do sistema em tempo real.

### 7.5 Tratamento de erro e loading

- Em caso de erro (404 ou outro), o componente apenas zera a lista; não há mensagem de erro nem estado de loading na UI. O utilizador vê apenas “No SLA records available”, sem saber se é 404 ou outro problema.

---

## 8. Resumo executivo

| Item | Conclusão |
|------|-----------|
| **Arquivo real** | `apps/portal-frontend/src/sections/SlaLifecycleSection.tsx` |
| **Endpoint real** | **GET /api/v1/sla** (chamado via `portalApi.slaList()`); **não existe** no backend (404). |
| **Payload real** | GET sem body; resposta de sucesso não existe na prática; em falha o frontend usa `[]`. |
| **Fonte dos dados** | Chamada real à API; **não** mock nem array estático; resultado efetivo é **sempre lista vazia** por 404. |
| **Gaps científicos** | (1) Endpoint de listagem inexistente; (2) Sem coluna ML decision/XAI; (3) Sem coluna semantic class/profile; (4) Sem atualização/refresh da lista; (5) Sem feedback de erro/loading na UI. |

---

## 9. Não implementado nesta fase

Nenhuma alteração de backend, endpoint ou frontend foi feita. Somente auditoria e documentação. Sem build, sem deploy.
