# Baseline runtime state — TriSLA integrations

Canonical interface reference: [`docs/modules/interfaces.md`](../modules/interfaces.md).

**Escopo:** estado documental das integrações **reais** observadas no código e na auditoria (`docs/AUDIT_INTERFACES_*.md`, `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md`, `docs/TRISLA_E2E_FLOW_CANONICAL.md`).  
**Nota:** não altera runtime; serve de linha de base para evolução controlada da Interface Layer.

## Cadeia lógica preservada (referência)

Fluxo operacional descrito na auditoria: **Portal → SEM-CSMF → Decision Engine → ML-NSMF** (encadeamento via SEM no caminho `/api/v1/intents`; o portal não invoca `/evaluate` diretamente), **→ NASP Adapter → BC-NSSMF → SLA-Agent** (quando habilitado), com **telemetria** em paralelo ao submit. Ordem canónica E2E: ver `docs/TRISLA_E2E_FLOW_CANONICAL.md`.

## Tabela de integrações (origem → destino)

| ID | Origem | Destino | Endpoint / canal | Protocolo | Payload principal | Criticidade | Evidência |
|----|--------|---------|------------------|-----------|-------------------|-------------|-----------|
| B-01 | Portal Frontend | Portal Backend | `POST /api/v1/sla/interpret` | HTTP | `intent_text`, `tenant_id` | Alta | `AUDIT_INTERFACES_CURRENT_STATE.md` §1; `TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md` §1 |
| B-02 | Portal Frontend | Portal Backend | `POST /api/v1/sla/submit` | HTTP | `template_id`, `form_values`, `tenant_id` | Alta | Idem; schemas em `apps/portal-backend/src/schemas/sla.py` (referência em evidência) |
| B-03 | Portal Backend | SEM-CSMF | `POST /api/v1/interpret` | HTTP | `intent`, `tenant_id` | Alta | `NASPService.call_sem_csmf`; auditoria |
| B-04 | Portal Backend | SEM-CSMF | `POST /api/v1/intents` | HTTP | `service_type`, `intent`, `tenant_id`, `sla_requirements`, `metadata?` | Alta | `submit_template_to_nasp`; E2E fases 3–5 |
| B-05 | SEM-CSMF | Decision Engine | `POST /evaluate` | HTTP | intent/context + telemetria (montagem no cliente SEM) | Alta | `DecisionEngineHTTPClient`; `apps/sem-csmf` |
| B-06 | Decision Engine | ML-NSMF | `POST /api/v1/predict` | HTTP | features derivadas de `DecisionInput` | Alta | `MLClient`; `apps/decision-engine/src/ml_client.py` |
| B-07 | Portal Backend | NASP Adapter | `POST /api/v1/nsi/instantiate` | HTTP | `orch_payload` (ex.: `nsiId`, slice/profile/sla) | Alta | `nasp.py`; orquestração se `ACCEPT` |
| B-08 | Orquestração / SLA-Agent | NASP Adapter | `POST /api/v1/sla/register` | HTTP | registo SLA derivado de evento | Média | `AUDIT_INTERFACES_CURRENT_STATE.md`; consumer Kafka |
| B-09 | Vários | NASP Adapter | `GET/POST /api/v1/3gpp/gate` | HTTP | pré-condições / gate | Média | `AUDIT_INTERFACES_CLASSIFICATION.md` |
| B-10 | Portal Backend | BC-NSSMF | `POST /api/v1/register-sla` | HTTP | campos SLA / `bc_payload` | Alta | pós-orquestração bem-sucedida |
| B-11 | Orquestração | BC-NSSMF | `POST /api/v1/update-sla-status`, `POST /api/v1/execute-contract` | HTTP | estado / execução de contrato | Média | classificação |
| B-12 | Portal Backend (`telemetry/collector`) | Prometheus | `GET /api/v1/query`, `GET /api/v1/query_range` | HTTP | `query`, `start`, `end`, `step` | Alta | coleta para snapshot |
| B-13 | SEM-CSMF | Portal Backend | `GET /api/v1/prometheus/query` | HTTP | PromQL (`query`) | Baixa–média | proxy de consulta |
| B-14 | Portal Backend | SLA-Agent (opcional) | URL `SLA_AGENT_PIPELINE_INGEST_URL` | HTTP | `intent_id`, `sla_id`, `nest_id`, `tenant_id`, `decision`, latências, … | Condicional | env; não crítico se desligado |
| B-15 | Decision / ML / BC / SLA-Agent | Kafka | tópicos (event bus) | Kafka | eventos decisão/predição/pipeline | Alta | produtores/consumidores nos apps |

## Domínio de dados vs fronteira HTTP

- **CONTROL:** rotas SLA, SEM, Decision, ML, Kafka de controlo.
- **CORE:** NASP Adapter (`nsi/instantiate`, `3gpp/gate`, `sla/register` no adapter).
- **GOVERNANCE:** BC-NSSMF.
- **OBSERVABILITY:** Prometheus, `telemetry_snapshot`, ingest SLA-Agent, agentes documentados em classificação.

Dados RAN/transport/core aparecem sobretudo em **`metadata.telemetry_snapshot`** e consultas PromQL; não constituem uma única rota nomeada `RAN-I1` no código (gap explícito em `AUDIT_INTERFACES_GAPS.md`).

## Observações de baseline

- **REST** é o transporte principal entre microserviços auditados; **gRPC** não figura como caminho principal.
- **Versionamento:** `/evaluate` sem prefixo `/api/v1` é um ponto de inconsistência documentado nos gaps.
- Esta baseline deve ser atualizada apenas quando nova evidência de código/auditoria for incorporada (fora do âmbito deste pacote se restringir a `docs/interfaces/`).
