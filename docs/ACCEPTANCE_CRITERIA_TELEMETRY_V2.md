# Critérios de aceitação — Telemetria v2 (TriSLA)

**Âmbito:** validação pós-implementação dos PRs PROMPT_35.  
**Referências:** `TELEMETRY_CONTRACT_V2.md`, `PROMQL_SSOT_V2.md`, `PROMPT_35_CHECKLIST_PRs.md`.

---

## Métricas e completude

| # | Critério | Como verificar |
|---|----------|----------------|
| 1 | `telemetry_complete = true` em **≥ 95%** das execuções de uma campanha E2E (ex.: N≥100 submits) | Agregar `metadata.telemetry_complete` nos logs ou CSV exportado |
| 2 | `telemetry_gaps = []` quando `telemetry_complete = true` | Invariante na resposta JSON |
| 3 | Todas as métricas numéricas com **unidade correta** conforme contrato | Revisão automática + amostragem manual (ms, %, bytes) |
| 4 | Decisão SLA / `resource_pressure` usa **as mesmas métricas** que o snapshot **ou** política **B** documentada com subset explícito | Comparar código + documentação de versão |
| 5 | **Nenhuma** métrica global indevida no papel de **domínio** (ex.: `sum(process_cpu_seconds_total)` sem filtro como “Core”) | Code review + `PROMQL_SSOT_V2` |

## Runner e regressão

| # | Critério | Como verificar |
|---|----------|----------------|
| 6 | `scripts/e2e/prompt21_multi_domain_validation.py` mantém **estabilidade**: `http_200 > 0` e taxa de falha HTTP não superior a baseline pré-v2 | Executar antes/depois; comparar `summary.json` |
| 7 | `telemetry_all_domains_non_null_ratio` ≥ baseline acordado quando ambiente está saudável | Campanha PROMPT_21 com `PROMPT21_REPEATS` ≥ 3 |

## Consistência de versão

| # | Critério | Como verificar |
|---|----------|----------------|
| 8 | `metadata.telemetry_version = "v2"` presente nas respostas após cutover | Teste de API |
| 9 | Clientes legados sem `telemetry_version` continuam a funcionar durante janela de transição | Teste de contrato |

---

## Falhas aceitáveis (explícitas)

- Gaps em **campos opcionais** (ex.: `ran.throughput_mbps`, `core.session_latency_ms`) **não** violam critério 1 se a política v2 os excluir da lista de gaps obrigatórios.

---

*PROMPT_35 — critérios de aceitação.*
