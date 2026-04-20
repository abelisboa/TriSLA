# FASE D.2 — REORGANIZAÇÃO VISUAL CIENTÍFICA DO MENU 2 (Criar SLA PNL)

**Data:** 2026-03-17  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Escopo:** Reorganizar somente a apresentação visual do Menu 2 em painéis científicos. Endpoint, backend, payload e lógica inalterados.

---

## Alterações realizadas

### FASE 1 — Painéis visuais

O resultado da interpretação passou a ser exibido em **quatro painéis** (cards com borda leve, espaçamento vertical e títulos fortes):

| Painel | Título | Campos |
|--------|--------|--------|
| **1** | Semantic Interpretation | semantic_class, profile_sla, template_id, recommended slice |
| **2** | Technical SLA Profile | latency, throughput, reliability, jitter, coverage (de `sla_requirements` quando existirem) |
| **3** | Explainable Decision Support | confidence, explanation, ontology match |
| **4** | Technical Response Payload | JSON expandível (botão "Expandir detalhes técnicos") |

Quando um campo não existe no payload, é exibido: **"Campo ainda não exposto neste endpoint"**.

### FASE 2 — Remoção de títulos numéricos

Removidos os prefixos "1 —", "2 —", "3 —", "4 —" dos blocos. Os títulos passaram a ser apenas os nomes dos painéis (ex.: "Semantic Interpretation").

### FASE 3 — Hierarquia visual

- **Cards:** borda `1px solid #e2e8f0`, `border-radius: 12px`, padding 20px, `marginBottom: 20px`, fundo branco, sombra leve.
- **Títulos de painel:** `PanelTitle` com fonte 13px, peso 700, cor `#0f172a`, margem inferior 14px.
- **Linhas de campo:** componente `FieldRow` com label em negrito e valor (ou placeholder quando não exposto).

### FASE 4 — Layout lateral

Sidebar não foi alterada; mantido o layout lateral atual do portal.

---

## Build, push, deploy e validação

| Fase | Resultado |
|------|-----------|
| **Tag (TS)** | 20260317T004704Z |
| **Digest remoto** | sha256:93728e9b6bfea015f8203a02e0f44e874f02a730cac9086d4afa5ffc2d594c55 |
| **Helm revision** | 60 |
| **Deployment image** | ghcr.io/abelisboa/trisla-portal-frontend@sha256:93728e9b6bfea015f8203a02e0f44e874f02a730cac9086d4afa5ffc2d594c55 |
| **Pod imageID** | ghcr.io/abelisboa/trisla-portal-frontend@sha256:93728e9b6bfea015f8203a02e0f44e874f02a730cac9086d4afa5ffc2d594c55 |
| **Rollout** | deployment "trisla-portal-frontend" successfully rolled out |

---

## Preservação

- **Endpoint:** `/api/v1/sla/interpret` (inalterado).
- **Backend:** intacto.
- **Payload e lógica:** inalterados; apenas a forma de exibição foi reorganizada.
- **Nenhuma alteração fora do frontend.**
