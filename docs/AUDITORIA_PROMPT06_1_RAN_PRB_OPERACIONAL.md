# AUDITORIA PROMPT_06.1 — RAN (UERANSIM / srsRAN / PRB Simulator)

## Resumo executivo

A auditoria operacional confirma que o pipeline TriSLA continua integrado a PRB, porém a fonte ativa de PRB está congelada por override manual no simulador. A causa do PRB estático nao e falha arquitetural; e estado operacional da fonte.

---

## 1. RAN identificada (qual tecnologia)

Tecnologias detectadas no ambiente:

- **PRB Simulator TriSLA**: ativo em `trisla/trisla-prb-simulator` (pod Running, svc `trisla-prb-simulator:8086`).
- **UERANSIM**: ativo em `ueransim/ueransim-singlepod` e svc `ueransim-gnb`.
- **srsRAN/srsenb**: presente no namespace `srsran`, mas nao operacional (ImagePullBackOff / deployment indisponivel).

Evidencia de cluster:

- Pod Running: `trisla-prb-simulator-...`.
- Pod Running: `ueransim-singlepod-...`.
- Pods `srsenb-...`: `ImagePullBackOff`.

---

## 2. Estado atual (ativa/inativa)

- **PRB Simulator**: **ATIVO**.
- **UERANSIM**: **ATIVO** (componente presente).
- **srsRAN/srsenb**: **INATIVO** (sem disponibilidade para exportacao de metricas RAN reais nesse estado).

---

## 3. Fonte do PRB atual

Fonte efetiva observada no Prometheus:

- Serie: `trisla_ran_prb_utilization`
- Labels: `job="trisla-prb-simulator"`, `container="prb-simulator"`, `service="trisla-prb-simulator"`
- Valor observado: **10.0**

Consultas:

- `query=prb` -> sem resultado
- `query=ran_prb_utilization` -> sem resultado
- `query=trisla_ran_prb_utilization` -> 1 serie com valor 10

Interpretacao: a fonte ativa do PRB no pipeline e o **simulador**, nao srsRAN/UERANSIM diretamente.

---

## 4. Existencia de simulador

**Sim, existe e esta em uso.**

Evidencias:

- Codigo: `apps/prb-simulator/src/main.py` (Gauge `trisla_ran_prb_utilization`, endpoints `/set`, `/set/auto`, `/load`, `/health`).
- Servico/pod: `trisla-prb-simulator` no namespace `trisla`.
- Runbook historico: campanhas com `job=trisla-prb-simulator` e ajustes via `/set`/`/load`.

---

## 5. Existencia de core (free5GC)

**Sim, core 5G ativo.**

Evidencias em `ns-1274485`:

- `amf-free5gc-amf-amf-0` Running
- `smf-free5gc-smf-smf-0` Running
- `upf-free5gc-upf-upf-0` Running
- `nrf-free5gc-nrf-nrf-...` Running

---

## 6. Evidencia Prometheus

Metric names relevantes encontradas:

- `trisla_ran_prb_utilization`
- `trisla_ran_prb_scenario`
- `trisla_transport_jitter_ms`

Evidencia de origem da serie PRB:

- `job="trisla-prb-simulator"`
- `pod="trisla-prb-simulator-..."`

Nao houve evidencia de serie PRB ativa vinda de `srsenb` no estado atual.

---

## 7. Diferenca para ambiente anterior

Historico (runbook):

- Havia campanhas com PRB dinamico (baseline/peak, `/set`, `/load`, atraso de scrape controlado).
- Havia trilhas de tentativa de PRB real via `srsenb` (9092/36412), com falhas operacionais documentadas.

Estado atual:

- PRB no pipeline continua vindo do simulador.
- Valor permanece estatico em 10.0 durante pre-check.
- `srsenb` segue indisponivel, reduzindo chance de fonte RAN real alternativa.

---

## 8. Causa raiz operacional

**Causa raiz identificada com evidencia direta:**

No `prb-simulator`, o endpoint `/health` reporta:

- `manual_prb_override: 10.0`
- `scenario: scenario_1`
- `load_inputs` zerados
- `prb_utilization: 10.0` em amostras repetidas

Isto fixa o PRB em 10.0 e elimina variabilidade, mesmo com pipeline funcional.

Conclusao: a quebra operacional esta na **configuracao/estado runtime da fonte PRB (override manual ativo)**, nao na integracao de codigo.

---

## 9. Classificacao do cenario (A, B ou C)

Classificacao: **CENARIO B — SIMULADOR ATIVO**

Justificativa:

- Ha simulador ativo e sendo scrapeado pelo Prometheus.
- A serie PRB vem explicitamente do job `trisla-prb-simulator`.
- O valor esta congelado por override manual (`manual_prb_override=10.0`).

Nao e Cenario A (RAN real dinamica) porque a fonte efetiva nao e PRB dinamico de RAN real; nao e Cenario C (fallback interno sem fonte) porque existe fonte externa ativa (simulador), ainda que estagnada.

---

## Evidencias-chave coletadas nesta auditoria

1. `kubectl get pods/svc/deployments -A` com presenca de `trisla-prb-simulator`, `ueransim-singlepod`, e `srsenb` em falha.
2. Query Prometheus de `trisla_ran_prb_utilization` com label `job=trisla-prb-simulator` e valor 10.
3. `GET /health` do simulador (via port-forward) mostrando `manual_prb_override=10.0`.
4. Runbook com historico de uso de `/set`/`/load` e dependencia de scrape para refletir variacao.

