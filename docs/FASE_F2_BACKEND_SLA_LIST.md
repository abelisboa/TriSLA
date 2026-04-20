# FASE F.2 — Implementar endpoint real GET /api/v1/sla para alimentar Menu 4

**Data:** 2026-03-17  
**Objetivo:** Criar endpoint real GET /api/v1/sla retornando lista científica mínima para o Menu 4 (SLA Lifecycle). Sem alterar frontend nem portalApi; sem nova persistência; reutilizar estrutura alinhada a submit/status.

---

## Regras aplicadas

- Não alterar frontend.
- Não alterar portalApi.
- Não criar nova persistência (sem DB, sem ficheiro).
- Reutilizar a mesma estrutura já usada por POST /submit e GET /status/{sla_id}.
- POST /submit: contrato (request/response) inalterado; apenas efeito colateral de registo em memória.
- GET /status/{sla_id}: inalterado.

---

## 1. Auditoria prévia

- **POST /submit:** Não persiste em nenhum store; chama `nasp_service.submit_template_to_nasp()` e devolve a resposta. Não há escrita em BD nem ficheiro.
- **GET /status/{sla_id}:** Devolve um dict literal por pedido; não usa store partilhado.
- **Conclusão:** Não existia store persistente nem memória partilhada. Foi introduzida uma lista em memória no módulo (`_sla_registry`) para alimentar GET /api/v1/sla, preenchida como efeito colateral em cada POST /submit de sucesso.

---

## 2. Local exato do endpoint

- **Ficheiro:** `apps/portal-backend/src/routers/sla.py`
- **Rota:** `@router.get("/", response_model=List[SLAListItem])`
- **Função:** `async def list_slas()`
- **URL efectiva:** GET **/api/v1/sla** (prefix do router: `/api/v1/sla`, path da rota: `/`).

---

## 3. Memória utilizada

- **Variável:** `_sla_registry: List[dict] = []` no módulo `sla.py`.
- **Preenchimento:** Em `submit_sla_template`, após construir `response_payload` e antes de `return SLASubmitResponse(...)`, é feito um `_sla_registry.append({...})` com um item derivado do resultado do submit (id, slice_type, state, admission, blockchain, nasp, runtime).
- **Leitura:** GET /api/v1/sla devolve `[SLAListItem(**item) for item in _sla_registry]`.

---

## 4. Regras de derivação do item (por submit)

| Campo       | Derivação |
|------------|-----------|
| **id**     | `sla_id` = intent_id ou result.get("sla_id") |
| **slice_type** | form_values.slice_type / type / service_type ou result.service_type ou service_type_from_form |
| **state**  | "ACTIVE" se status em ("ok", "accepted", "active", "applied"); senão status ou "PENDING" |
| **admission** | decision (ACCEPT/REJECT/RENEG) |
| **blockchain** | bc_status se existir; senão "committed" se tx_hash existir; senão "" |
| **nasp**   | "deployed" (mínimo) |
| **runtime** | "monitored" (mínimo) |

---

## 5. Schema da resposta

- **Ficheiro:** `apps/portal-backend/src/schemas/sla.py`
- **Modelo:** `SLAListItem` com campos opcionais: id, slice_type, state, admission, blockchain, nasp, runtime.
- **Resposta do endpoint:** `List[SLAListItem]`, ou seja, array de objetos com esses campos.

---

## 6. Formato de retorno (exemplo)

```json
[
  {
    "id": "uuid-do-intent",
    "slice_type": "URLLC",
    "state": "ACTIVE",
    "admission": "ACCEPT",
    "blockchain": "committed",
    "nasp": "deployed",
    "runtime": "monitored"
  }
]
```

---

## 7. Diff resumido

**schemas/sla.py**

- Import de `List`.
- Novo model `SLAListItem` com id, slice_type, state, admission, blockchain, nasp, runtime (todos Optional).

**routers/sla.py**

- Import de `List` e `SLAListItem`.
- `_sla_registry: List[dict] = []`.
- Nova rota `GET "/"` → `list_slas()` que devolve `[SLAListItem(**item) for item in _sla_registry]`.
- Em `submit_sla_template`, após construir `response_payload`, cálculo de sla_id_val, status_val, slice_type_val, state_val, admission_val, blockchain_val e `_sla_registry.append({...})`; mantido `return SLASubmitResponse(**response_payload)` inalterado.

---

## 8. Sem build / sem deploy

Conforme pedido: sem build e sem deploy nesta fase.
