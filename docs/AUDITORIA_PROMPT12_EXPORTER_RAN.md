# AUDITORIA PROMPT_12 — INSTRUMENTACAO REAL srsRAN (EXPORTER PRB)

## Resultado executivo

- Exporter real implantado e scrapeado pelo Prometheus (`target up`).
- Sem simulacao e sem valor fixo: o exporter apenas publica `ran_prb_utilization` quando encontra padrao real de PRB nos logs do `srsenb`.
- No estado atual dos logs do `srsenb`, nao ha linha com PRB utilizavel, logo `ran_prb_utilization` continua sem series e TriSLA continua com `null`.
- **STATUS FINAL: BLOQUEADO (nova causa: ausencia de sinal PRB nos logs/scheduler do runtime atual do srsenb)**.

## 1) Fonte de PRB nos logs (FASE 1)

Coleta realizada:

- `kubectl logs -n srsran srsenb-8464bdd4f7-pvr6p --tail=500`

Evidencia:

- Logs contem apenas bootstrap/ambiente e mensagens repetidas:
  - `n_prb=50` (capacidade/configuracao, nao uso)
  - `Waiting for the 5G-EmPOWER Runtime to come up...`
- Nao foram encontradas linhas de utilizacao real do tipo `PRB usage` ou `RB allocated X/Y`.

## 2) Regra de extracao implementada (FASE 2)

Parser do exporter implementado com prioridade:

1. `PRB usage/utilization: <N>%`
2. `RB allocated: <used>/<total>` -> converte para percentual
3. `PRB: <N>%`

Sem match:

- nao inventa valor
- nao publica `ran_prb_utilization`
- publica status de diagnostico.

## 3) Exporter criado (FASE 3-4)

Arquivos adicionados:

- `apps/ran-prb-exporter/exporter.py`
- `apps/ran-prb-exporter/requirements.txt`
- `apps/ran-prb-exporter/Dockerfile`

Comportamento:

- endpoint `/metrics` com:
  - `ran_prb_utilization` (somente quando ha PRB real parseado)
  - `ran_prb_exporter_status{status=...}`
  - `ran_prb_exporter_last_scrape_unixtime`

## 4) Build/push (FASE 5)

- Build realizado:
  - `ghcr.io/abelisboa/trisla-ran-prb-exporter:20260401T143608Z`
- Push realizado.
- Digest obtido:
  - `sha256:4ba70132d8454e36d3a00409db3ca35398fb47efaccc01f730228386cfd3a98b`

Observacao operacional:

- Pull no cluster falhou com `401 Unauthorized` (GHCR privado/sem imagePullSecret no namespace `srsran`).
- Para manter o objetivo tecnico sem alterar TriSLA, o deployment foi ajustado para imagem publica `python:3.10-slim` + codigo via ConfigMap (sem simulacao).

## 5) Deploy, Service e ServiceMonitor (FASE 6-8)

Recursos aplicados em `srsran`:

- `ServiceAccount` `ran-prb-exporter`
- `Role` + `RoleBinding` com permissoes somente leitura de `pods`/`pods/log`
- `Deployment` `ran-prb-exporter`
- `Service` `ran-prb-exporter` (`9100`)

Recurso aplicado em `monitoring`:

- `ServiceMonitor` `ran-prb-exporter` (intervalo `5s`)

## 6) Validacao Prometheus (FASE 9)

Target ativo:

- job: `ran-prb-exporter`
- namespace: `srsran`
- service: `ran-prb-exporter`
- health: `up`
- scrape URL: `http://10.233.75.54:9100/metrics`

Status do parser:

- `ran_prb_exporter_status{status="no_prb_pattern_found_in_logs"} 0`

Serie PRB:

- `ran_prb_utilization` -> `0` series ativas.

## 7) Validacao TriSLA backend (FASE 9-10)

Amostragem (10x):

- `curl /api/v1/prometheus/summary | jq '.ran_prb_utilization'`
- resultado: `null` em 10/10 amostras

Variacao/STD:

- sem valores numericos, portanto `std > 0.01` nao atende.

## 8) Causa raiz atual

Mesmo com cadeia de observabilidade ativa e exporter scrapeado, o runtime atual do `srsenb` nao emite (nos logs disponiveis) uma linha de uso PRB que permita extracao real.

Consequencia:

- nao ha amostra para `ran_prb_utilization`
- TriSLA permanece com `ran_prb_utilization = null`.

## 9) Decisao final (criterio PROMPT_12)

- PRB real: **nao comprovado no log atual**
- target exporter: **up**
- PRB no TriSLA: **null**
- PRB variavel: **nao**
- std > 0.01: **nao**

**STATUS: BLOQUEADO**
