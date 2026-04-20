# AUDITORIA PROMPT_05 — RAN/PRB/COLETA E2E (sem regressao)

## Escopo e metodo

Esta auditoria foi executada em modo somente leitura, sem testes novos, sem alteracoes de codigo e sem deploy. A analise cruza evidencias de `docs/TRISLA_MASTER_RUNBOOK.md`, prompts historicos em `PROMPTS/` e implementacao atual em `apps/*` + `helm/`.

---

## 1) Simulador RAN identificado

**Identificacao principal (historico recente e pipeline atual):**

- **PRB Simulator** (`apps/prb-simulator/src/main.py`) expondo a serie Prometheus `trisla_ran_prb_utilization`.
- O runbook registra explicitamente campanha com `job=trisla-prb-simulator`, baseline/peak de PRB e uso dos endpoints `/set`, `/load` e `/metrics`.
- O cliente do SEM-CSMF prioriza essa fonte por query com label de job: `trisla_ran_prb_utilization{job="trisla-prb-simulator"}`.

**Tecnologias RAN historicas paralelas (nao SSOT do PRB no pipeline atual):**

- `srsRAN/srsenb` e `UERANSIM` aparecem no runbook e em prompts antigos de restauracao/ativacao.
- O proprio runbook documenta falhas de pull/ready do `srsenb` em fases anteriores, o que limita a disponibilidade de PRB "real" direto da RAN nesses periodos.

**Classificacao solicitada:**

- [x] PRB Simulator (Prometheus job)
- [ ] srsRAN como fonte estavel primaria do dataset atual
- [ ] UERANSIM como fonte primaria de PRB
- [ ] outro

---

## 2) Forma de geracao de PRB

### 2.1 No simulador (`apps/prb-simulator/src/main.py`)

- Gauge principal: `trisla_ran_prb_utilization`.
- Modo automatico por cenario (`scenario_1`, `scenario_10`, `scenario_50`) com faixas de PRB.
- Acoplamento causal de carga: `active_slices`, `request_rate`, `concurrency` via endpoint `/load`.
- Override manual via `/set` e retorno a automatico via `/set/auto`.

### 2.2 No NASP Adapter (`apps/nasp-adapter/src/metrics_collector.py`)

- Tambem exporta `trisla_ran_prb_utilization` ao extrair PRB de payload RAN (`get_ran_metrics`) e normalizar para 0-100.
- Isso cria possibilidade de **mesmo nome de metrica** ter mais de uma origem/scrape path.

---

## 3) Caminho completo da metrica PRB (pipeline)

### Caminho nominal registrado no runbook

`RAN/PRB source -> Prometheus -> portal-backend /api/v1/prometheus/query -> SEM-CSMF -> Decision Engine -> dataset`

### Evidencias de implementacao

1. **Prometheus alias no backend**
   - `apps/portal-backend/src/routers/prometheus.py`
   - `prb_usage`, `gnb_prb_usage`, `ran_prb_utilization` -> `trisla_ran_prb_utilization`

2. **Coleta no SEM-CSMF (entrada para decisao)**
   - `apps/sem-csmf/src/decision_engine_client.py`
   - Busca PRB por query com preferencia de `job="trisla-prb-simulator"`; fallback para query generica.
   - Preenche `telemetry_snapshot.ran.prb_utilization` no payload do Decision Engine.

3. **Consumo no Decision Engine**
   - `apps/decision-engine/src/engine.py`
   - PRB entra no calculo de risco/metadata (`ran_prb_utilization_input`, `ran_aware_final_risk`).

4. **Persistencia em dataset**
   - Coletor E2E serializa `telemetry_snapshot.ran.prb_utilization` para coluna `ran_prb_utilization`.

---

## 4) Diferenca entre versao anterior e atual

## Antes (evidenciado em runbook)

- Campanhas de saturacao PRB com variacao observada (baseline/peak e override).
- Evidencias de PRB > 10 e cenarios com alteracao de carga/override.
- Fluxos dedicados de "ativar PRB real na RAN" e restauracao `srsenb` aparecem em prompts historicos.

## Atual (dataset consolidado v4)

- `ran_prb_utilization` no dataset aparece constante (=10.0), com desvio zero.
- Outras metricas (ex.: transport/core/latencias) variam, indicando que a coleta E2E ocorreu, mas o canal PRB ficou sem dinamica real observada.

---

## 5) O que deixou de ser executado / mudou na coleta

1. **Nao ha evidencia no fluxo recente de injetar carga PRB** no simulador via `/load` durante a coleta consolidada.
2. **Nao ha evidencia de override PRB (`/set`)** ativo no run da coleta final.
3. A coleta E2E recente foi orientada por `POST /api/v1/sla/submit` com cenarios de SLA; isso nao garante, por si, variacao do sinal PRB se a fonte de PRB estiver fixa/estagnada.
4. Historicamente havia trilhas explicitas de operacao RAN/simulador (prompts e runbook) que nao aparecem como etapa obrigatoria no run SSOT de coleta mais recente.

---

## 6) Causa raiz provavel (com evidencia)

**Causa raiz provavel (unica, em termos operacionais):**

A coleta atual consumiu `trisla_ran_prb_utilization` de uma fonte **sem dinamica efetiva no momento do run** (valor estabilizado em 10), porque o ciclo de ativacao de variacao PRB (simulador com `/load`/`/set` ou RAN real estavel) nao estava efetivamente acoplado ao run de coleta E2E.

### Evidencias que sustentam

- Runbook: pipeline recente assume `job=trisla-prb-simulator` e descreve necessidade de alinhamento de scrape/estado.
- Codigo SEM-CSMF: prioridade ao job do simulador; se este job nao variar, PRB no payload nao varia.
- Dataset final: PRB constante em 10.0, contrastando com variacao de outros sinais.
- Historico de srsenb no runbook: periodos de indisponibilidade da fonte RAN real reforcam dependencia do simulador como fonte pratica de PRB.

---

## 7) Impacto no dataset atual

1. Reduz poder explicativo das figuras/correlacoes que usam PRB como variavel independente.
2. Enfraquece inferencia causal RAN -> decisao para este run especifico.
3. Mantem validade E2E geral (pipeline funcional), mas com lacuna no eixo "variabilidade RAN".

---

## 8) Respostas diretas da FASE 6 (comparacao historica)

1. **O que existia antes e nao existe agora?**
   - Evidencia de campanha PRB com dinamica (set/load/saturacao) explicitamente acoplada ao periodo de coleta.

2. **O que deixou de ser executado?**
   - Etapas operacionais de controle de PRB (ou confirmacao de PRB dinamico) imediatamente antes/durante a coleta E2E final.

3. **O que mudou na coleta?**
   - Foco em submit E2E sem etapa explicita de governanca da fonte PRB durante o run.

4. **Problema principal (classificacao):**
   - **ausencia de execucao da dinamica do simulador/fonte PRB durante a coleta** (nao ausencia total de integracao de codigo).

---

## 9) Recomendacoes (sem aplicar)

1. Antes da proxima coleta, incluir checkpoint obrigatorio de PRB dinamico (pre-run) no runbook SSOT: confirmar serie `trisla_ran_prb_utilization` variando no tempo, nao apenas presente.
2. Durante o run E2E, registrar no manifesto do dataset:
   - fonte PRB dominante (job/instance),
   - min/max/std de PRB no periodo,
   - timestamp de validacao de scrape.
3. Evitar ambiguidade de origem quando houver mais de um exportador para `trisla_ran_prb_utilization` (documentar label selector no consumo).
4. Incluir criterio de aceite cientifico: `std(ran_prb_utilization) > 0` para declarar "RAN variability validated".

---

## Conclusao executiva

A RAN fazia parte do pipeline por integracao Prometheus->SEM-CSMF->Decision, mas no run consolidado atual o sinal PRB chegou praticamente fixo (10.0), descaracterizando variabilidade de dominio RAN no dataset. O problema observado e mais de **operacao/coleta da fonte PRB no momento do run** do que de ausencia de integracao de codigo.
