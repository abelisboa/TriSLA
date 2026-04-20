# FASE D.1 — CORREÇÃO FINA DO MENU 2 (ENDPOINT /api/api E TEXTO CIENTÍFICO)

**Data:** 2026-03-17  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Escopo:** Remover duplicação /api/api, ajustar texto científico do formulário do Menu 2. Somente frontend; backend intacto.

---

## FASE 1 — AUDITORIA

**Problema validado:** No browser a requisição ia para `/api/api/v1/sla/interpret` → 404. O endpoint correto é `/api/v1/sla/interpret`.

**Arquivo auditado:** `apps/portal-frontend/src/lib/api.ts`

- **baseURL:** `API_BASE` importado de `./env`; em `env.ts`, `API_BASE = process.env.NEXT_PUBLIC_API_BASE || '/api'`.
- **Concatenação:** `fetch(\`${API_BASE}${path}\`)` com `path` = `/api/v1/sla/interpret` (e demais paths começando com `/api/v1/...`).
- **Origem da duplicação:** `API_BASE` já é `/api`; os paths em `portalApi` também iniciavam com `/api`, resultando em `/api` + `/api/v1/...` = `/api/api/v1/...`.

**Respostas:**

- **A. Linha exata do erro:** Não é uma única linha; é a combinação de (1) `env.ts` linhas 1–2: `API_BASE = ... || '/api'` e (2) `api.ts` linhas 51–64: paths com prefixo `/api/v1/...`. A concatenação em `api.ts` linhas 4 e 26 (`\`${API_BASE}${path}\``) produz a URL duplicada.
- **B. Correção mínima necessária:** Remover o prefixo `/api` dos paths em `api.ts`, mantendo apenas `/v1/...`. Assim `API_BASE` + path = `/api` + `/v1/sla/interpret` = `/api/v1/sla/interpret`.

**Correção aplicada em `api.ts`:** Todos os paths de `portalApi` alterados de `/api/v1/...` para `/v1/...` (prometheus/summary, health, sla, modules, sla/interpret).

---

## FASE 2 — AJUSTE UI CIENTÍFICO

**Arquivo:** `apps/portal-frontend/src/sections/PnlSlaSection.tsx`

| Antes | Depois |
|-------|--------|
| "Entrada natural → interpretação semântica (SEM-CSMF) → recomendação de slice. Sem mock." | "Definição de requisitos de SLA para interpretação semântica e recomendação de perfil de serviço em redes 5G/O-RAN." |
| "Frase em linguagem natural" | "Descrição do serviço ou requisito operacional" |
| Placeholder: "Ex: cirurgia remota com latência ultra baixa" | "Ex.: cirurgia remota com latência ultrabaixa e alta confiabilidade" |
| Mensagem de erro: "Informe a frase em linguagem natural." | "Informe a descrição do serviço ou requisito operacional." |

Regra observada: sem menção a mock, módulo interno ou nomes internos arquiteturais.

---

## FASE 3–5 — BUILD, PUSH, DIGEST REMOTO

- **Tag (TS):** `20260317T002833Z`
- **Build:** concluído (podman, Next.js build OK).
- **Push:** concluído para `ghcr.io/abelisboa/trisla-portal-frontend:20260317T002833Z`.
- **Digest remoto:** `sha256:13a14f30d70854b38c8ed2ad9b478f1430bc2b49dbfc3c766a8b2ccf226856c6`

---

## FASE 6 — DEPLOY

- **Comando:** `helm upgrade trisla-portal helm/trisla-portal -n trisla --set frontend.image.repository=... --set frontend.image.digest=${REMOTE_DIGEST} --set frontend.image.tag="" --reuse-values`
- **Revisão Helm:** **59** (deployed).

---

## FASE 7 — VALIDAÇÃO

| Validação | Resultado |
|-----------|-----------|
| `kubectl -n trisla rollout status deployment/trisla-portal-frontend` | `deployment "trisla-portal-frontend" successfully rolled out` |
| Deployment image | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:13a14f30d70854b38c8ed2ad9b478f1430bc2b49dbfc3c766a8b2ccf226856c6` |
| Pod imageID | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:13a14f30d70854b38c8ed2ad9b478f1430bc2b49dbfc3c766a8b2ccf226856c6` |

---

## FASE 8 — TESTE NO BROWSER

**Passos para validação:**

1. Abrir o portal no browser.
2. Menu 2 → **Criar SLA PNL**.
3. No campo "Descrição do serviço ou requisito operacional", informar: **cirurgia remota**.
4. Clicar em **Interpretar**.

**Resultado esperado:**

- Sem HTTP 404 (requisição deve ir para `/api/v1/sla/interpret`).
- **semantic_class** aparece na resposta.
- **recommended slice** (ou slice_type/service_type) aparece na resposta.

---

## CONCLUSÃO

- Duplicação `/api/api` corrigida: paths em `api.ts` passaram a usar `/v1/...`; URL final = `/api/v1/...`.
- Texto do formulário do Menu 2 ajustado para linguagem científica (5G/O-RAN, sem mock/nomes internos).
- Build, push, digest remoto e deploy executados; revisão **59** em produção com digest `sha256:13a14f30d70854b38c8ed2ad9b478f1430bc2b49dbfc3c766a8b2ccf226856c6`.
- Nenhuma alteração fora do frontend; backend e demais módulos intactos.

**Regra final:** Teste no browser (FASE 8) deve ser executado pelo operador para confirmar ausência de 404 e exibição de semantic_class e recommended slice.
