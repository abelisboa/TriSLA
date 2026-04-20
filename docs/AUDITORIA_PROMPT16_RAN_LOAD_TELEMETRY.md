# AUDITORIA PROMPT_16 — REDEFINICAO TELEMETRIA RAN (RANTester + Free5GC)

## Escopo executado

- Correcao de bloqueadores de observabilidade e redefinicao de metrica de carga RAN com SSOT `RANTester + Free5GC`.
- Evidencias coletadas em `evidencias/prompt16_20260401T154518Z`.

## 1) Targets Prometheus (fase 1)

Estado inicial de `down` identificado:

- `trisla-nasp-adapter` -> `404 /metrics`
- `trisla-nasp-adapter-metrics` -> `404 /metrics`
- `trisla-ui-dashboard` -> content-type HTML (nao-metrics)

Diagnostico confirmado em logs do NASP Adapter:

- repetidos `GET /metrics HTTP/1.1" 404 Not Found`

Acao aplicada:

- patch em ServiceMonitors invalidos para evitar scrape indevido em endpoints nao-metrics.

Observacao:

- apesar do patch, os jobs `trisla-nasp-adapter*` e `trisla-ui-dashboard` continuam aparecendo como `down` no Prometheus em tempo de auditoria (necessario reconciliacao adicional do conjunto de ServiceMonitors/release).

## 2) Metricas selecionadas (fases 2 e 3)

Inventario filtrado em `metrics_filtered.txt` mostrou metricas reais disponiveis, incluindo:

- Rede/latencia: `probe_duration_seconds`
- Sistema: `process_cpu_seconds_total`, `process_resident_memory_bytes`
- HTTP/latencia app: `trisla_http_request_duration_seconds_*`, `trisla_sem_*_latency_*`

Para carga RAN SSOT, foram selecionadas:

1. `throughput_mbps` (proxy de trafego do `rantester`)
2. `transport_latency_ms` (`probe_duration_seconds` do probe TCP)
3. `sessions` (pods Running de `rantester+amf+smf+upf` no namespace SSOT)

## 3) Formula do ran_load (fase 4)

Definicao implementada:

`ran_load = 0.5*norm(throughput_mbps,50) + 0.3*norm(transport_latency_ms,200) + 0.2*norm(sessions,20)`

Onde `norm(x,c) = clamp(x/c, 0, 1)`.

## 4) Integracao no backend (fase 5)

Arquivo atualizado:

- `apps/portal-backend/src/routers/prometheus.py`

Alteracao:

- endpoint `/api/v1/prometheus/summary` agora calcula e retorna:
  - `ran_load`
  - `transport_latency`
  - `throughput_mbps`
  - `sessions`
  - `cpu`
  - `ran_prb_utilization`
  - `formula`

Observacao operacional:

- o pod em execucao ainda responde com payload legado (raw `up/cpu/memory`), indicando necessidade de ciclo de deploy para refletir o codigo atualizado no runtime.

## 5) Evidencia de valores (fase 6)

Arquivo:

- `ran_load_samples_20.json`

Resumo:

- `n=20`
- `mean=0.04714905`
- `std=0.0001293926099`

## 6) Evidencia de variabilidade

Resultado cientifico:

- `std(ran_load) = 0.000129...` **< 0.01**
- criterio de variabilidade do prompt **NAO atendido**.

## 7) Evidencia de resposta a carga (fase 7)

Teste baixo/alto via escala do `rantester`:

- Low (replicas=0): `ran_load = 0.04738`
- High (replicas=1): `ran_load = 0.047891`

Resultado:

- `ran_load_high > ran_load_low` (criterio monotonicidade atendido)
- efeito pequeno, ainda sem variabilidade estatistica suficiente.

## 8) Validacao final

- **PROMETHEUS OK?** NAO  
  (ainda ha targets `down` persistentes em jobs de scrape nao-metrics)

- **RAN LOAD DEFINIDO?** SIM  
  (formula e queries definidas com metricas reais da SSOT)

- **VARIABILIDADE OK?** NAO  
  (`std` abaixo de `0.01`)

- **PRONTO PARA COLETA E2E?** NAO  
  (requer fechamento de targets down + ganho de variabilidade de carga)
