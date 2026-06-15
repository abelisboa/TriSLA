# Estratégia de testes de contrato — interfaces lógicas

Canonical interface reference: [`docs/modules/interfaces.md`](../modules/interfaces.md).

Objetivo: definir **testes de contrato** para `RAN-I1`, `TN-I1`, `CN-I1`, `OBS-I1`, `BC-I1` que validem **estabilidade semântica** dos caminhos atuais (campos obrigatórios, códigos HTTP, presença de chaves críticas), alinhados a `docs/INTERFACE_DECISION_RECOMMENDATION.md` e ao checklist de não regressão.

**Nota:** esta fase é **estratégia documental**; implementação de suites fica para repositórios de teste/CI quando aprovado.

## Princípios

- **Baseline:** respostas e schemas **atuais** são a fonte de verdade (golden samples ou contratos inferidos).
- **Sem alteração de API:** testes falham se o produtor remover campos sem versionamento acordado.
- **Separação por interface lógica:** um teste pode cobrir várias rotas mapeadas no catálogo (`interface-catalog-v1.yaml`).

## RAN-I1

| Âmbito | Verificações sugeridas |
|--------|-------------------------|
| Snapshot | `metadata.telemetry_snapshot.ran` presente quando campanha RAN ativa; tipos coerentes (número/objeto conforme schema atual). |
| PromQL / API | Query SSOT RAN (ex. `avg(trisla_ran_prb_utilization{job="trisla-ran-ue-upf-proxy"})` ou variável de ambiente documentada) retorna série não vazia em ambiente instrumentado. |
| Agentes (se ativos) | `GET/POST` rotas `/api/v1/agents/ran/*` retornam JSON com campos documentados. |

**Ferramentas:** testes de integração com Prometheus mock ou ambiente de campanha; validação de schema JSON (ajv/pydantic) sobre exemplos capturados.

## TN-I1

| Âmbito | Verificações sugeridas |
|--------|-------------------------|
| Snapshot | `telemetry_snapshot.transport` coerente após submit em cenário com transporte. |
| Agentes | Rotas `agents/transport` com contrato estável. |

**Dependência:** cenários com ONOS/Mininet ou mocks conforme runbook.

## CN-I1

| Âmbito | Verificações sugeridas |
|--------|-------------------------|
| Portal entrada | `POST /api/v1/sla/submit` e `interpret` com schemas `SLA*` válidos. |
| SEM | `POST /api/v1/interpret`, `POST /api/v1/intents` — presença de `decision` e metadados esperados no fluxo feliz. |
| Decision / ML | `POST /evaluate` resposta com campo(s) de decisão; `POST /api/v1/predict` com prediction/explanation. |
| NASP | `POST /api/v1/nsi/instantiate` — validar contrato `success`/`http_status` documentado; gate `3gpp/gate` quando usado em teste de orquestração. |

**Prioridade:** P0 — maior risco de regressão (`INTERFACE_DECISION_RECOMMENDATION.md`).

## OBS-I1

| Âmbito | Verificações sugeridas |
|--------|-------------------------|
| Prometheus | Respostas `/api/v1/query` com matriz `resultType`/`result` esperada. |
| Router portal | `/api/v1/prometheus/query` aceita `query` e devolve dados ou erro controlado. |
| Ingest | Se `SLA_AGENT_PIPELINE_INGEST_URL` definido, POST retorna código esperado e corpo parseável. |

## BC-I1

| Âmbito | Verificações sugeridas |
|--------|-------------------------|
| register-sla | Resposta inclui campos de trilha quando BC disponível (`tx_hash`, `block_number` opcionais mas testados quando mock BC ativo). |
| Estados | Transições `SKIPPED_ORCH_FAILED` vs commit coerentes com E2E canónico. |

## Níveis de teste

1. **Contrato unitário de schema** (fixtures JSON).
2. **Integração serviço-a-serviço** (docker-compose / namespace de teste).
3. **E2E smoke** (subconjunto do checklist V2).

## Critérios de falha

- Regressão em `telemetry_snapshot` (campos ausentes sem ADR).
- Mudança de código HTTP em endpoints públicos sem deprecação.
- Quebra da cadeia SEM→Decision→ML no caminho `intents`.

## Referências

- `docs/INTERFACE_NON_REGRESSION_CHECKLIST.md`
- `docs/interfaces/NON_REGRESSION_CHECKLIST_V2.md`
- `docs/TRISLA_E2E_FLOW_CANONICAL.md`
