# FASE F.3 — Tornar Menu 4 cientificamente vivo (refresh + loading + erro real)

**Data:** 2026-03-17  
**Objetivo:** Menu 4 (SLA Lifecycle) mostrar claramente loading, erro e atualização manual. Reutilizar GET /api/v1/sla; sem alterar backend/endpoint; sem polling.

---

## Regras aplicadas

- Não alterar backend.
- Não alterar endpoint.
- Reutilizar GET /api/v1/sla já criado.
- Não criar polling ainda.

---

## 1. Alterações em `SlaLifecycleSection.tsx`

### 1.1 Estados

- **loading:** `useState(false)` — true durante a chamada a `portalApi.slaList()`.
- **error:** `useState<string | null>(null)` — mensagem de erro real ou null.

### 1.2 load()

- **Antes da chamada:** `setLoading(true)`.
- **Sucesso:** `setItems(safeArray<SLA>(data))`, `setError(null)`.
- **Erro (catch):** `setItems([])`, `setError(e instanceof Error ? e.message : 'Failed to load SLA lifecycle.')`.
- **finally:** `setLoading(false)`.

`load` é definido com `useCallback` e chamado no `useEffect` (mount) e no clique do botão.

### 1.3 Botão

- **Texto:** "Refresh SLA Lifecycle".
- **Posição:** Acima da tabela.
- **Ação:** `onClick={() => load()}`.
- **Disabled:** `disabled={loading}`.

### 1.4 Mensagens na UI

- **Loading:** quando `loading` é true, exibir "Loading SLA records..." acima da tabela.
- **Erro:** quando `error` não é null, exibir a mensagem em bloco vermelho (estilo consistente com outros erros do portal).
- **Vazio:** "No SLA records available" apenas quando `!loading && !error && items.length === 0` (`showEmpty`).

### 1.5 Colunas e tipo

- Colunas e tipo `SLA` mantidos; sem alteração.

---

## 2. Diff resumido

- Import de `useCallback`.
- Estados `loading` e `error` adicionados.
- `load` extraído para `useCallback(async () => { setLoading(true); try { ... setItems; setError(null); } catch { setItems([]); setError(...); } finally { setLoading(false); } }, [])`.
- `useEffect` chama `load()` (dependência `[load]`).
- Variável `showEmpty = !loading && !error && items.length === 0`.
- Botão "Refresh SLA Lifecycle" acima da tabela, com `onClick={() => load()}`, `disabled={loading}`.
- Bloco condicional "Loading SLA records..." quando `loading`.
- Bloco condicional de erro quando `error`.
- No tbody, mensagem "No SLA records available" condicionada a `showEmpty` em vez de `items.length === 0`.

---

## 3. Sem build / sem deploy

Conforme pedido: sem build e sem deploy nesta fase.
