# AUDITORIA PROMPT_11 — ATIVACAO DA TELEMETRIA RAN REAL

## Escopo aplicado

- Correcao de observabilidade somente em RAN/Prometheus.
- Sem alteracao de codigo TriSLA, sem ML/Decision Engine, sem coleta E2E, sem PRB simulator.

## 1) Metodo de exportacao identificado

- `srsenb` pod: `srsenb-8464bdd4f7-pvr6p` (`srsran`) em `Running`.
- Service `srsenb` expoe portas `36412` e `9092`.
- Verificacao interna no pod (`ss -ltnup`) nao mostrou listener pronto para metrics no momento da coleta.

## 2) Service criado

Aplicado:

- Namespace: `srsran`
- Nome: `srsran-metrics`
- Label: `app: srsran`
- Selector: `app: srsenb`
- Porta: `metrics` em `9092 -> 9092`

Evidencia:

- Endpoint resolvido para pod ativo: `10.233.75.22:9092`.

## 3) ServiceMonitor criado

Aplicado:

- Namespace: `monitoring`
- Nome: `srsran-metrics`
- Selector: `app: srsran`
- Namespace alvo: `srsran`
- Endpoint: `port: metrics`, `path: /metrics`, `interval: 5s`

Evidencia adicional:

- Config renderizada do Prometheus contem o job:
  - `job_name: serviceMonitor/monitoring/srsran-metrics/0`

## 4) Target no Prometheus

Target descoberto, porem indisponivel:

- job: `srsran-metrics`
- namespace: `srsran`
- pod: `srsenb-8464bdd4f7-pvr6p`
- health: `down`
- erro: `connect: connection refused`
- scrapeUrl: `http://10.233.75.22:9092/metrics`

Query de suporte:

- `up{service="srsran-metrics"} = 0`

## 5) Metrica identificada

Catalogo de nomes no Prometheus inclui:

- `trisla_ran_prb_utilization`
- `trisla_ran_prb_scenario`
- `trisla_kpi_ran_health`

Series ativas:

- `trisla_ran_prb_utilization` -> 0 series
- `trisla_ran_prb_scenario` -> 0 series
- `trisla_kpi_ran_health` -> 2 series

## 6) Evidencia de valores PRB

Backend (`/api/v1/prometheus/summary`) em 10 amostras:

- `ran_prb_utilization = null` em 10/10.

## 7) Evidencia de variacao

- Sem valores numericos de PRB (apenas `null`), logo nao ha variacao observavel.
- `std` nao pode ser validado (> 0.01) por ausencia de amostras numericas.

## 8) Resultado final

**STATUS: BLOQUEADO (nova causa identificada)**.

Causa tecnica atual:

- A cadeia de observabilidade foi ativada ate o Prometheus (Service + ServiceMonitor + job criado), mas o endpoint real de metrics no `srsenb` (`:9092/metrics`) nao aceita conexao (`connection refused`).
- Consequencia: target `srsran-metrics` permanece `down`, `trisla_ran_prb_utilization` sem series ativas e TriSLA continua recebendo `ran_prb_utilization = null`.

## Criterio final (PROMPT_11)

- target = up -> **NAO**
- PRB != null -> **NAO**
- PRB variavel -> **NAO**
- std > 0.01 -> **NAO**

Conclusao: telemetria RAN real ainda nao ativa ponta a ponta devido indisponibilidade do endpoint de metrics no runtime do `srsenb`.
