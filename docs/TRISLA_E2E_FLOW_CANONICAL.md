# TriSLA — Fluxo E2E canónico (auditoria de código — PROMPT_20)

**Fonte de verdade:** leitura de `apps/portal-backend` (rotas SLA, `NASPService`, telemetria) e evidências em `evidencias/PROMPT20/`.  
**Última revisão:** 2026-05-11 (FASE 7 — pós-refatoração FASES 2–6).  
**Revisão anterior:** 2026-04-10 (PROMPT_132).

---

## [POST-REFACTOR — FASES 2–6 / 2026-05-11] Fluxo canónico atualizado

Este bloco tem precedência sobre o bloco histórico abaixo quando houver
descrição conflitante de **autoridade** (orchestration / lifecycle /
governance / revalidate). O histórico é mantido para auditoria.

### Ordem operacional pós-refatoração

| # | Fase | Componente autoridade | Componente executor | Observações pós-refatoração |
|---|------|-----------------------|---------------------|-----------------------------|
| 1 | Solicitação SLA               | Cliente              | Cliente HTTP             | `POST /api/v1/sla/submit`. |
| 2 | Ingress / relay               | Portal Backend       | Portal Backend           | `role=relay/delegator` — **não decide mais** orquestração nem lifecycle semântico. |
| 3 | Interpretação semântica       | SEM-CSMF             | SEM-CSMF                 | Inalterado. Propaga `metadata` enriquecida do DE. |
| 4 | Pipeline de admissão          | SEM-CSMF             | SEM-CSMF → ML-NSMF → DE  | DE participa via `/api/v1/intents`. |
| 5 | Decisão (ACCEPT/REJECT/RENEG) | **Decision Engine**  | Decision Engine          | DE escreve em `metadata`: `decision_engine_orchestration_authority`, `orchestration_required`, `orchestration_intent`, `lifecycle_event`, `governance_event`, `decision_engine_lifecycle_authority`, `decision_engine_governance_authority`. (FASES 3+4) |
| 6 | Decisão de orquestração       | **Decision Engine**  | (declarativo)            | Portal lê o flag de authority no `metadata` — não recompõe a decisão. |
| 7 | Orquestração NASP             | NASP Adapter         | NASP Adapter             | Portal continua a executar `POST {NASP_ADAPTER}/api/v1/nsi/instantiate` quando `orchestration_required=true`. |
| 8 | Registo blockchain            | **BC-NSSMF**         | BC-NSSMF + Web3          | Após orquestração OK. Resposta inclui `governance_registration` (id, lineage, status). Em degraded: `governance_registration_fallback=true`. |
| 9 | Execução de domínio           | RAN/TRANSPORT/CORE   | RAN/TRANSPORT/CORE       | Inalterado. |
| 10 | Telemetria de decisão        | Portal Backend       | Portal Backend           | `collect_domain_metrics_async` mantém in-process no submit. |
| 11 | Métricas SLA-aware           | Portal Backend       | Portal Backend           | `compute_sla_metrics`. |
| 12 | Reassessment temporal        | **SLA-Agent**        | SLA-Agent                | `POST /api/v1/agent/revalidate-telemetry` (autoridade FASE 2). Portal expõe `POST /api/v1/sla/revalidate-telemetry` que **delega** com fallback in-process. |
| 13 | Observabilidade alargada     | Prometheus / Loki    | Prometheus / Loki        | Inalterado. |
| 14 | Resposta ao cliente          | Portal Backend       | Portal Backend           | `SLASubmitResponse` carrega `metadata` enriquecida (authority flags, lifecycle/governance, telemetria, latências). |

### Diagrama (ASCII)

```
Client ──► Portal Backend (ingress, role=relay)
              │
              ▼
        SEM-CSMF ──► ML-NSMF ──► Decision Engine
                                   │  (FASES 3+4)
                                   │  emite metadata.authority
                                   ▼
              Portal Backend (relay) ──► NASP Adapter (executor)
                                   │
                                   └──► BC-NSSMF (governance authority + lineage)

Paralelo / runtime:
   Portal /sla/revalidate-telemetry ──delega──► SLA-Agent /agent/revalidate-telemetry
                                              (fallback in-process se off)
```

### Contratos de metadata críticos (não regredir)

- **Authority orquestração** — `decision_engine_orchestration_authority`,
  `orchestration_required`, `orchestration_decision_source`,
  `orchestration_intent` (FASE 3).
- **Authority lifecycle** — `decision_engine_lifecycle_authority`,
  `lifecycle_event` (FASE 4).
- **Authority governance** — `decision_engine_governance_authority`,
  `governance_event` (FASE 4).
- **Relay flags** — `portal_lifecycle_role=relay`,
  `portal_governance_role=relay`, `lifecycle_authority_source=decision-engine`
  (FASE 4).
- **Delegation reassessment** — `delegated_to_sla_agent`, `delegation_target`,
  `delegation_fallback_reason` (FASE 2).
- **BC immutable** — `governance_registration.{id, lifecycle_lineage_id,
  status, fallback}` (FASE 4).

### Fallbacks ativos (preservar)

- Reassessment: `delegation_fallback_reason ∈ {SLA_AGENT_REVALIDATE_URL_unset,
  SLA_AGENT_REVALIDATE_disabled, http_error:*, exception:*}`.
- Orquestração: fluxo legado `ACCEPT→orchestrate` quando authority não vem.
- Lifecycle/Governance: `portal-legacy` / `legacy-composer` quando DE não traz
  authority.
- BC: `governance_registration_fallback=true` quando RPC/contract offline.

### Estado runtime em produção (2026-05-11)

Ver `evidencias_refactor_responsabilidades_20260511T191645Z/freeze/runtime/active_digests_summary.txt`.

---

## Entrypoint único (submissão)

- **HTTP:** `POST /api/v1/sla/submit`  
- **Código:** `apps/portal-backend/src/routers/sla.py` → `submit_sla_template`  
- **Prefixo da app:** `apps/portal-backend/src/main.py` — `include_router(..., prefix="/api/v1/sla")`

## Fases do sistema (ordem lógica)

| # | Fase | Onde | Notas |
|---|------|------|--------|
| 1 | Solicitação do SLA | Cliente / Portal | JSON `SLASubmitRequest` (`template_id`, `form_values`, `tenant_id`). |
| 2 | API & normalização | Portal Backend | Montagem de `nest_template`; logs `[SLA SUBMIT]`. |
| 3 | Interpretação semântica | SEM-CSMF | `NASPService.call_sem_csmf` → `POST http://trisla-sem-csmf:8080/api/v1/interpret`. |
| 4 | Pipeline de admissão | SEM-CSMF | `POST .../api/v1/intents` — **orquestra internamente** ML-NSMF e Decision Engine; o portal **não** chama `/evaluate` directamente (comentário em `nasp.py`). |
| 5 | Decisão | Decision Engine (via SEM) | `decision` ∈ {ACCEPT, REJECT, RENEGOTIATE}; metadata com risco ML, XAI, etc. |
| 6 | Orquestração NASP | NASP Adapter | Se `decision == ACCEPT`: `POST {NASP_ADAPTER}/api/v1/nsi/instantiate`; sucesso = HTTP 2xx e `success` no JSON (adapter pode devolver 200 com `success: false`). |
| 7 | Registo blockchain | BC-NSSMF | Só se **ACCEPT** e orquestração **SUCCESS**: `POST .../api/v1/register-sla`; caso contrário `SKIPPED_ORCH_FAILED` sem commit definitivo. |
| 8 | Execução de domínio | RAN / TRANSPORT / CORE | Fora do `submit` síncrono: instanciação via stack NASP/cluster; **Transport ONOS** integrado no NASP com `ENABLE_TRANSPORT` (ver runbook PROMPT_19). |
| 9 | Telemetria de decisão | Portal Backend | `collect_domain_metrics_async` → snapshot RAN/transport/core (Prometheus / agregações). |
| 10 | Métricas SLA-aware | Portal Backend | `compute_sla_metrics` sobre snapshot + ML. |
| 11 | Monitorização / ingestão | SLA-Agent Layer | Após BC `COMMITTED`: `_notify_sla_agent_pipeline` → `SLA_AGENT_PIPELINE_INGEST_URL`. Com `SLA_AGENT_REQUIRED_FOR_ACCEPT=true`, falta de URL ou erro HTTP impede `COMPLETED`. |
| 12 | Observabilidade alargada | Prometheus / Loki | Rotas `/api/v1/prometheus/*`, `health`, `slos`; não são o mesmo passo que o snapshot do submit, mas compõem o **ciclo de observabilidade**. |
| 13 | Resposta ao cliente | Portal Backend | `SLASubmitResponse` com `metadata` (telemetria, lifecycle, latências). |

## Camadas (visão resumida)

- **Decisão (lógica):** SEM-CSMF + ML-NSMF + Decision Engine (encadeados no fluxo `/api/v1/intents` do SEM).  
- **Orquestração:** NASP Adapter + (opcional) Transport NSSMF / ONOS no serviço NASP Python.  
- **Execução:** RAN (ex. RANTester), TRANSPORT (ONOS+Mininet quando activo), CORE (Free5GC).  
- **Observabilidade:** colecta no submit + Prometheus + SLA-Agent + eventual Kafka (apps dedicados).  
- **Apresentação:** Portal Frontend consome a API do backend.

## Lacunas documentais corrigidas por este documento

O fluxo **não** termina na orquestração: o `submit` agrega **telemetria**, **métricas SLA-aware**, **notificação ao SLA-Agent** e **resposta rica** — ver `sla.py` após `submit_template_to_nasp`.

## Evidências

- Greps: `evidencias/PROMPT20/01_submit_entry.txt` … `12_response.txt`


## NASP alignment — SSOT recovery (2026-05-13)

Ver `docs/SSOT_RECOVERY/TRISLA_NASP_RUNTIME_BASELINE.md` (workflow inalterado; apenas ponte para baseline e gate Fase 4–5).



## RAN SSOT governance (2026-05-13)

Workflow inalterado; governança de métricas RAN: `docs/SSOT_RECOVERY/TRISLA_RAN_SSOT_POLICY.md`.

