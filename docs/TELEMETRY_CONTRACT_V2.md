# Contrato de telemetria — TriSLA v2

**Versão:** `v2`  
**Estado:** especificação (implementação futura)  
**Base:** PROMPT_33 (auditoria), PROMPT_34 (plano), PROMPT_35 (checklist)

---

## 1. Campos canónicos por domínio

### RAN

| Campo lógico | Nome no snapshot (JSON) | Tipo | Unidade | Obrigatório v2 |
|--------------|-------------------------|------|---------|----------------|
| Utilização de recursos rádio | `ran.prb_utilization` | number | % (0–100) | Sim |
| Latência RAN (ar / modelo) | `ran.latency` | number | ms | Sim |
| Throughput rádio | `ran.throughput_mbps` | number \| null | Mbps | Não — se disponível |

**Nota:** `ran.latency` pode ser medida, simulada ou derivada; a **proveniência** deve ser indicada em `metadata.telemetry_provenance` (ver flags).

### TRANSPORT

| Campo lógico | Nome no snapshot (JSON) | Tipo | Unidade | Obrigatório v2 |
|--------------|-------------------------|------|---------|----------------|
| RTT (caminho até alvo) | `transport.rtt` | number | ms | Sim |
| Jitter | `transport.jitter` | number | ms | Sim |
| Identificador de path / intent (ONOS) | `transport.path_id` | string \| null | — | Não — se ONOS ativo |
| Identificador alternativo | `transport.intent_id` | string \| null | — | Não — se ONOS ativo |

### CORE

| Campo lógico | Nome no snapshot (JSON) | Tipo | Unidade | Obrigatório v2 |
|--------------|-------------------------|------|---------|----------------|
| Utilização CPU Core | `core.cpu` | number | fração 0–1 **ou** % conforme contrato de query | Sim |
| Memória Core | `core.memory` | number | bytes | Sim |
| Latência de sessão / sinalização | `core.session_latency_ms` | number \| null | ms | Não — se disponível |

**Unificação de unidade:** o contrato v2 recomenda documentar em `PROMQL_SSOT_V2.md` se `core.cpu` é **fração [0,1]** ou **percentagem [0,100]** após normalização no consumidor; o mesmo valor deve alimentar SLA e decision engine.

---

## 2. Regras

### Unidades explícitas

- **%** — percentagem (PRB, eventual CPU como %).
- **ms** — milissegundos (latências, RTT, jitter).
- **Mbps** — megabits por segundo (throughput).
- **bytes** — memória.

### Janela temporal padrão (coleta Prometheus)

- **Instant / query_range no portal:** janela de decisão `[t-2s, t]` com `step=1s` (comportamento atual do `collector`).
- **PromQL com range interno:** `[1m]` onde especificado no SSOT (ex.: `stddev_over_time(...[1m])`).
- Qualquer desvio deve ser documentado em `PROMQL_SSOT_V2.md` e refletido nos testes.

### Cardinalidade controlada (labels)

- Usar **apenas** labels acordados: `job`, `namespace`, `pod`, `instance` quando necessário.
- Evitar `high cardinality` (labels dinâmicos por request id).
- Queries escopadas (ex.: `namespace="free5gc"`) em vez de agregados globais para domínio Core.

### Separação de escopo

- **NUNCA** usar métricas **globais** do cluster (ex.: `sum(process_cpu_seconds_total)` sem filtro) como representação do **domínio Core** no contrato v2.
- Métricas de **observabilidade de microsserviço** (HTTP P95) **não** substituem campos do snapshot multi-domínio sem versão explícita do contrato.

---

## 3. Flags e metadata

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `metadata.telemetry_complete` | boolean | `true` quando não há gaps obrigatórios ausentes (lista vazia). |
| `metadata.telemetry_gaps` | array de string | Ex.: `["ran.ran_throughput_mbps"]` — campos opcionais ausentes podem **não** entrar em `gaps` se a política v2 assim definir. |
| `metadata.telemetry_version` | string | Valor fixo **`"v2"`** após implementação; durante transição pode coexistir com leitura legada. |
| `metadata.telemetry_provenance` (opcional) | object | Por campo: `simulated` \| `measured` \| `proxy` (alinhado a PROMQL_SSOT). |

**Compatibilidade:** clientes que esperam apenas v1 continuam a receber os mesmos campos até deprecação; `telemetry_version` discrimina.

---

## 4. Critério de completude (v2)

- **Obrigatórios:** todos os campos marcados “Sim” nas tabelas por domínio, sem valor `null`.
- **Opcionais:** ausência não força `telemetry_complete = false` se a política de gaps v2 listar explicitamente apenas obrigatórios.

---

*Documento gerado para PROMPT_35 — checklist de implementação.*
