# TriSLA — Fluxo E2E canónico (auditoria de código — PROMPT_20)

**Fonte de verdade:** leitura de `apps/portal-backend` (rotas SLA, `NASPService`, telemetria) e evidências em `evidencias/PROMPT20/`.  
**Última revisão:** 2026-04-10 (PROMPT_132: BC só após orquestração OK; SLA-Agent após BC; score mode opcional)

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
