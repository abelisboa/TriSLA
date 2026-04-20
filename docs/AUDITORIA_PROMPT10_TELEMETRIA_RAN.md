# AUDITORIA PROMPT_10 — TELEMETRIA RAN -> PROMETHEUS (PRB)

## Escopo e metodo

- Auditoria somente leitura (sem alteracao de codigo, sem coleta E2E, sem novos exporters).
- Fontes: Prometheus API (`label`, `targets`, `query`), objetos Kubernetes (`pods`, `services`, `endpoints`, `ServiceMonitor`), e verificacao do pod `srsenb`.

## 1) Existe metrica PRB no Prometheus?

Sim, o nome da metrica existe no catalogo historico:

- `trisla_ran_prb_utilization`
- `trisla_ran_prb_scenario`

Porem, no instante atual nao ha serie ativa para PRB:

- Query: `trisla_ran_prb_utilization`
- Resultado: vazio (sem `result[]`).

## 2) Existe exporter?

Sim, existe exporter historico para PRB, mas esta sem backend ativo:

- Service `trisla-prb-simulator` existe em `trisla`.
- Endpoint atual do service: `<none>`.
- `ServiceMonitor` existe: `monitoring/trisla-prb-simulator-metrics`.
- Conclusao: exporter definido, mas sem pod atendendo (logo sem scrape efetivo).

## 3) Prometheus scrape esta ativo?

Para PRB:

- Config de scrape existe via `ServiceMonitor`.
- Scrape efetivo **nao** ocorre pois `trisla-prb-simulator` esta sem endpoints.

Para NASP:

- Targets `trisla-nasp-adapter` e `trisla-nasp-adapter-metrics` aparecem como `down`.
- Erro de scrape: `server returned HTTP status 404 Not Found` em `/metrics` no `:8085`.
- Conclusao: tambem nao contribui com serie PRB no estado atual.

## 4) Existe target/job RAN (srsenb/ueransim) no Prometheus?

- Nao foi encontrado `ServiceMonitor` para `srsenb`, `ueransim` ou job RAN dedicado.
- Service `srsran/srsenb` expoe `36412` e `9092`, mas nao ha monitoramento Prometheus configurado diretamente para ele.
- Dentro do pod `srsenb`, `ss -ltnup` nao mostrou socket de metrics pronto no momento da verificacao.

## 5) Nome real da metrica

- Metrica de PRB usada no ambiente: `trisla_ran_prb_utilization`.
- Estado atual: sem amostras ativas (query instantanea vazia), por isso no backend aparece `ran_prb_utilization = null`.

## 6) Classificacao (PROMPT_10)

- **CASO A — sem metrica no caminho RAN real**: `srsenb` nao esta sendo scrapeado como fonte de PRB.
- **CASO B — exporta mas nao scrapeado (cadeia atual de PRB)**: PRB dependia do `trisla-prb-simulator`, que no momento esta sem endpoint/pod.
- Evidencia adicional: NASP metrics alvo em `404` reforca indisponibilidade de telemetria util na cadeia atual.

## 7) Causa raiz

A cadeia de PRB no ambiente atual nao esta ligada ao `srsenb` recuperado; ela estava acoplada ao `trisla-prb-simulator`/pipeline de telemetria adjacente. Com o simulador sem endpoint, o Prometheus nao recebe amostras de `trisla_ran_prb_utilization`, e o backend retorna `null`.

## Decisao final

- Causa de `ran_prb_utilization = null` identificada com evidencias reais.
- Bloqueio atual e de telemetria/scrape da fonte de PRB (nao de disponibilidade do pod `srsenb`).
