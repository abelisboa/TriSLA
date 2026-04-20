# AUDITORIA PROMPT_16.1 — SANEAMENTO OBSERVABILIDADE + VARIABILIDADE RAN_LOAD

## 1) Targets saneados

Estado inicial (`targets_down_before.tsv`):

- `trisla-ui-dashboard` `down` (content-type HTML em `/metrics`)
- `trisla-nasp-adapter` `down` (`404 /metrics`)

Acoes aplicadas (somente observabilidade):

- neutralizacao de ServiceMonitors legados/invalidos de `nasp-adapter` e `ui-dashboard`;
- ajuste de seletor amplo em `servicemonitor/monitoring/trisla-sem-csmf-monitor` para alvo especifico (`app=trisla-sem-csmf-metrics`), removendo scrape indevido de servicos sem `/metrics`.

Estado final (`targets_down_final.tsv`):

- sem targets `down` ativos no endpoint Prometheus auditado (`127.0.0.1:19090`).

## 2) Metricas realmente usadas (SSOT)

Inventario em `metrics_all.json` e `metrics_filtered.txt`.

Metricas escolhidas para o indice:

- `transport_latency_ms`: `max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"})*1000`
- `sessions`: `sum(kube_pod_status_phase{namespace="ns-1274485",phase="Running",pod=~"(rantester.*|amf.*|smf.*|upf.*)"})`
- `throughput`: consultado, mas removido da formula v2 por baixa utilidade no ambiente (samples nulos no periodo)

## 3) Formula final do `ran_load` (v2)

Formula v2 (refinada):

`ran_load = 0.7*norm(sessions,8) + 0.3*norm(transport_latency_ms,20)`

Justificativa:

- `throughput` estava achatando/indefinido (nulo), reduzindo poder discriminativo;
- `sessions` e `latency` apresentaram resposta real aos cenarios SSOT;
- pesos priorizam carga operacional efetiva (sessoes) e incluem degradacao de transporte (latencia).

## 4) Cenarios testados

Cenarios executados via escala controlada do `statefulset/rantester`:

- `idle` (0 replicas)
- `low` (1 replica)
- `medium` (2 replicas)
- `high` (3 replicas)
- `burst` (5 replicas)

Amostragem:

- 25 amostras por cenario (total 125), intervalo 1s.

## 5) Tabela de resultados por cenario

Resumo (`ran_load_summary_v2.json`):

- `idle`: mean=0.42928696, std=0.00214410
- `low`: mean=0.43343060, std=0.00394673
- `medium`: mean=0.47847104, std=0.04324771
- `high`: mean=0.60403580, std=0.00407744
- `burst`: mean=0.69906948, std=0.08680433
- `global`: mean=0.5288587760, std=0.1145647690

CSV completo:

- `ran_load_scenarios.csv`

## 6) `std(ran_load)`

- `std_global = 0.1145647690`  (> 0.01) ✅

## 7) Monotonicidade

Critérios:

- `mean(high) > mean(low)` -> `0.60403580 > 0.43343060` ✅
- `mean(burst) > mean(high)` -> `0.69906948 > 0.60403580` ✅

## 8) Decisao final

- ✅ **PRONTO PARA COLETA**

Condições atendidas:

- observabilidade SSOT estabilizada (sem `down` remanescente no endpoint auditado);
- `ran_load` v2 definido e documentado;
- variabilidade estatistica suficiente;
- resposta a carga robusta e monotonicidade comprovada.

## Respostas do criterio final

- **PROMETHEUS SSOT ESTAVEL?** SIM
- **RAN_LOAD VALIDO?** SIM
- **VARIABILIDADE SUFICIENTE?** SIM
- **PRONTO PARA PROMPT_17?** SIM
