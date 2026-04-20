# Observabilidade — dashboards canônicos V2 (PR-06 / FASE 6)

Documento de referência para painéis operacionais alinhados ao **contrato de telemetria V2** e às flags de metadata do submit (`telemetry_version`, `telemetry_complete`, `telemetry_gaps`, `sla_policy_version`, `telemetry_units`).  
**Não depende de UI nova** — serve como SSOT para Grafana / outras ferramentas.

---

## Painel 1 — Saúde E2E

| Métrica | Descrição | Fonte típica |
|--------|-----------|--------------|
| `total_requests` | Total de pedidos no runner / janela | `summary.json` (E2E) |
| `http_200` | Respostas HTTP 200 | `summary.json` |
| `valid_samples` | Amostras com telemetria presente (gate operacional) | `summary.json` |
| `invalid_samples` | Restantes | `summary.json` |

---

## Painel 2 — Completude de telemetria

| Métrica | Descrição | Fonte típica |
|--------|-----------|--------------|
| `telemetry_complete` ratio | Fração de submits com `metadata.telemetry_complete == true` | Agregar respostas `POST /api/v1/sla/submit` ou coluna CSV do runner |
| `telemetry_gaps` por domínio | Contagem / lista de gaps (`ran.*`, `transport.*`, `core.*`) | `metadata.telemetry_gaps` no submit |
| `valid_samples_all_telemetry_fields_non_null` | Gate estrito (todos os campos obrigatórios non-null no snapshot) | `summary.json` |

---

## Painel 3 — Telemetria por domínio

Valores vêm de `metadata.telemetry_snapshot` após `apply_telemetry_contract_v2` (aliases V2 espelham legado).

| Domínio | Campos mínimos | Chaves canônicas V2 (exemplo) |
|---------|----------------|-------------------------------|
| RAN | `prb_utilization`, latência | `ran.prb_utilization`, `ran.latency_ms` |
| Transport | RTT, jitter | `transport.rtt_ms`, `transport.jitter_ms` |
| Core | CPU, memória | `core.cpu_utilization`, `core.memory_bytes` |

---

## Painel 4 — Política SLA

| Métrica | Descrição | Fonte |
|---------|-----------|--------|
| `sla_policy_version` | `v1`, `v2`, ou `v2_fallback_v1` | `metadata.sla_policy_version` |
| `resource_pressure_v1` | Pressão legado | `metadata.sla_metrics.resource_pressure_v1` |
| `resource_pressure_v2` | Pressão V2 (quando ativo) | `metadata.sla_metrics.resource_pressure_v2` |
| `feasibility_score` | Score de admissibilidade | `metadata.sla_metrics.feasibility_score` |

---

## Painel 5 — Decisão

| Métrica | Descrição | Fonte |
|---------|-----------|--------|
| ACCEPT / RENEGOTIATE / REJECT | Contagens ou taxas | Corpo da resposta `decision` + agregação |
| Divergência futura | Comparar decisão vs baseline / shadow (se existir pipeline) | Reservado — não obrigatório nesta fase |

---

## Notas

- **`GET /api/v1/prometheus/summary`**: agrega instant queries PromQL; inclui `metadata.telemetry_version` e `metadata.telemetry_units` como referência de contrato — **não** substitui `telemetry_complete` / `telemetry_gaps` do submit.
- Unidades de referência: `metadata.telemetry_units` (mapa campo → unidade).
