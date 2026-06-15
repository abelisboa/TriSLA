# Checklist de não regressão V2 (E2E objetivo)

Canonical interface reference: [`docs/modules/interfaces.md`](../modules/interfaces.md).

Evolution of `docs/INTERFACE_NON_REGRESSION_CHECKLIST.md` com critérios **mensuráveis** onde possível. Usar em gates de CI, campanhas e antes de ativar wrappers/dual-run.

## 1. Entrada e API pública (Portal)

| # | Critério | Passa quando |
|---|----------|----------------|
| E2E-01 | Interpret | `POST /api/v1/sla/interpret` → HTTP 200 e corpo JSON com campos de interpretação usados pelo frontend (sem erro de schema). |
| E2E-02 | Submit feliz | `POST /api/v1/sla/submit` → HTTP 200, `decision` ∈ {ACCEPT, REJECT, RENEGOTIATE} ou contrato documentado equivalente. |
| E2E-03 | Status / métricas | `GET /api/v1/sla/status/{sla_id}` e `GET /api/v1/sla/metrics/{sla_id}` respondem sem 5xx em SLA válido. |

## 2. Pipeline SEM → Decision → ML (ordem lógica)

| # | Critério | Passa quando |
|---|----------|----------------|
| E2E-10 | Portal → SEM | Chamadas a `POST .../api/v1/interpret` e `POST .../api/v1/intents` completam com 2xx ou erro documentado (não timeout silencioso). |
| E2E-11 | SEM → Decision | Evidência em logs/traces de chamada a `POST /evaluate` (ou métrica de cliente) no fluxo de intents. |
| E2E-12 | Decision → ML | Evidência de `POST /api/v1/predict` com resposta parseável (`prediction` / estrutura atual). |

## 3. Orquestração e governança (NASP → BC → SLA-Agent)

| # | Critério | Passa quando |
|---|----------|----------------|
| E2E-20 | NASP | Para decisão ACCEPT e cenário de orquestração ativo: `POST .../api/v1/nsi/instantiate` retorna JSON com `success` e `http_status` interpretáveis pelo portal. |
| E2E-21 | BC | Se orquestração sucesso e BC ativo: `register-sla` executa; se indisponível, estado documentado (ex. skipped) **sem** 500 genérico na resposta final. |
| E2E-22 | SLA-Agent | Com `SLA_AGENT_PIPELINE_INGEST_URL` definido: ingest retorna código esperado; com agent desligado, fluxo mantém política documentada (não regressão de `COMPLETED`). |

## 4. Observabilidade

| # | Critério | Passa quando |
|---|----------|----------------|
| E2E-30 | telemetry_snapshot | Resposta de submit inclui `metadata.telemetry_snapshot` com estrutura ran/transport/core quando coleta assíncrona concluída (ou política de fallback documentada). |
| E2E-31 | Prometheus | `GET /api/v1/prometheus/query` (e/ou query_range via collector) válido para PromQL SSOT em ambiente com Prometheus. |

## 5. Compatibilidade e configuração

| # | Critério | Passa quando |
|---|----------|----------------|
| E2E-40 | Endpoints públicos | Nenhum path público documentado foi removido ou renomeado sem ADR + versão. |
| E2E-41 | Env opcionais | Comportamento com `SLA_AGENT_*` desligado permanece estável (sem obrigatoriedade nova silenciosa). |
| E2E-42 | Kafka (se usado) | Produtores/consumidores não falham em loop sem dead-letter quando mensagens válidas. |

## 6. Pós-condição de campanha científica

| # | Critério | Passa quando |
|---|----------|----------------|
| E2E-50 | Rastreabilidade | Resposta final preserva campos necessários a datasets (`intent_id`, `sla_id`, latências, decisão) conforme runbook de campanha. |

---

**Versão:** V2 (2026-04-30). Revisar quando endpoints ou políticas de BC/SLA-Agent mudarem com ADR.
