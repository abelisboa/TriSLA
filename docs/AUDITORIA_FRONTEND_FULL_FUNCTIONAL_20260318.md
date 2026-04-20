# Auditoria Frontend — Fechamento Funcional (Menu a Menu)

**Data:** 2026-03-18  
**Contexto:** Frontend TriSLA em fase de fechamento funcional; Template com XAI renderizado e auditoria runtime concluída. Sem alteração de backend, sem-csmf ou decision-engine.

---

## FASE 1 — Auditoria menu a menu

### 1. Template — `src/app/template/page.tsx`

| Item | Resposta |
|------|----------|
| **Endpoint usado** | POST `/api/v1/sla/submit` (apiRequest `SLA_SUBMIT`) |
| **Fonte real ou placeholder** | Fonte real. Payload do backend (SLASubmitResponse); reasoning, confidence, domains, metadata, decision_snapshot quando DE retorna 200. |
| **Cards científicos completos** | Sim. A. Semantic Result (sla_id, intent_id, nest_id, service_type, timestamp, sla_requirements); B. Admission Decision (decision); C. XAI Metrics & Reasoning (confidence, reasoning, ml_risk_score, ml_risk_level); D. Domain Viability (metadata.decision_snapshot.domains — RAN, Transport, Core); E. Blockchain Governance (tx_hash, block_number, bc_status). |
| **Conteúdo residual ou final** | Final. Fallback "—" quando campos null; sem placeholders inventados. |

---

### 2. PNL — `src/app/pnl/page.tsx`

| Item | Resposta |
|------|----------|
| **Endpoint usado** | POST `/api/v1/sla/interpret` (apiRequest `SLA_INTERPRET`) |
| **Fonte real ou placeholder** | Fonte real para Semantic Result, message, technical_parameters, sla_requirements. Placeholder/awaiting para XAI Metrics, Domain Viability (apenas technical_parameters como "Observed payload"), Blockchain Governance, Admission Decision. |
| **Cards científicos completos** | Parcial. Semantic Result completo (intent_id, nest_id, sla_id, status, service_type, slice_type, etc.). XAI Metrics: só "Status" = awaiting. XAI Reasoning: message real do interpret. Domain Viability: technical_parameters quando existir, senão awaiting. Blockchain e Admission: awaiting (não expostos em /interpret). SLA Requirements: payload real quando disponível. |
| **Conteúdo residual ou final** | Residual. Vários cards declaradamente "não expostos em /interpret" ou "sem score real"; XAI Metrics e Admission Decision são placeholders. |

---

### 3. SLA Lifecycle — `src/app/sla-lifecycle/page.tsx`

| Item | Resposta |
|------|----------|
| **Endpoint usado** | GET `/api/v1/nasp/diagnostics` (apiRequest `NASP_DIAGNOSTICS`) |
| **Fonte real ou placeholder** | Fonte real para Semantic Admission, ML Decision, Blockchain Commit (probe reachable + status_code/detail do NASP). Placeholder para "Runtime SLA Status" (Runtime status = awaiting, "No consolidated SLA runtime endpoint exposed"). |
| **Cards científicos completos** | Parcial. Três cards alimentados por NASP diagnostics (sem_csmf, ml_nsmf, bc_nssmf). Quarto card "Runtime SLA Status" é residual (sem endpoint de status SLA consolidado). |
| **Conteúdo residual ou final** | Residual no card Runtime SLA Status; demais final para o que o endpoint oferece. |

---

### 4. Monitoring — `src/app/monitoring/page.tsx`

| Item | Resposta |
|------|----------|
| **Endpoint usado** | GET `/api/v1/prometheus/summary` (PROMETHEUS_SUMMARY), GET `/api/v1/modules/transport/metrics` (TRANSPORT_METRICS), GET `/api/v1/modules/ran/metrics` (RAN_METRICS) |
| **Fonte real ou placeholder** | Fonte real para Prometheus Runtime (up, CPU, Memory), Transport Domain (status + endpoint state), RAN Domain (status + endpoint state). Placeholder para Core Domain (Status e Endpoint state = awaitingFeed). |
| **Cards científicos completos** | Parcial. Prometheus, Transport e RAN com dados reais; Core Domain sem endpoint chamado (só awaiting). |
| **Conteúdo residual ou final** | Residual no card Core Domain; demais final. |

---

### 5. Metrics — `src/app/metrics/page.tsx`

| Item | Resposta |
|------|----------|
| **Endpoint usado** | GET `/api/v1/prometheus/summary` (PROMETHEUS_SUMMARY), GET `/api/v1/modules/transport/metrics` (TRANSPORT_METRICS) |
| **Fonte real ou placeholder** | Fonte real para CPU Metrics, Memory Metrics, Runtime Throughput (transport payload). Placeholder para "SLA Evidence Feed" (Status e Observed source = awaiting). |
| **Cards científicos completos** | Parcial. CPU/Memory/Transport com dados reais; SLA Evidence Feed sem fonte. |
| **Conteúdo residual ou final** | Residual no card SLA Evidence Feed; demais final. |

---

### 6. Defense — `src/app/defense/page.tsx`

| Item | Resposta |
|------|----------|
| **Endpoint usado** | Nenhum. Sem chamada API. |
| **Fonte real ou placeholder** | Totalmente placeholder. Todos os campos (Policy state, Validation state, Integrity state, Runtime verification, Commit verification, Trust state, Protection mode) = "Awaiting validated runtime feed". |
| **Cards científicos completos** | Não. Cards de estrutura (Admission Protection, Runtime Integrity, Blockchain Trust Layer, SLA Protection Status) sem dados. |
| **Conteúdo residual ou final** | Totalmente residual. |

---

### 7. Administration — `src/app/administration/page.tsx`

| Item | Resposta |
|------|----------|
| **Endpoint usado** | GET `/api/v1/health/global` (GLOBAL_HEALTH), GET `/api/v1/nasp/diagnostics` (NASP_DIAGNOSTICS) |
| **Fonte real ou placeholder** | Fonte real. Backend Diagnostic (status, version, nasp_reachable, nasp_details_url); NASP Connectivity (sem_csmf, ml_nsmf, decision, bc_nssmf, sla_agent); Runtime Environment (env); API Surface (lista estática de endpoints). |
| **Cards científicos completos** | Sim, para o propósito administrativo (diagnósticos e conectividade). Não é painel científico XAI. |
| **Conteúdo residual ou final** | Final. |

---

## FASE 2 — Matriz final frontend

| MENU | endpoint(s) | fonte | status | falta concluir |
|------|-------------|--------|--------|----------------|
| **Template** | POST /api/v1/sla/submit | real (backend SLASubmitResponse) | concluído | nada; XAI completo quando DE 200 |
| **PNL** | POST /api/v1/sla/interpret | real para interpret; placeholder para XAI/BC/Admission | parcial | XAI Metrics, Domain Viability (além de technical_parameters), Blockchain, Admission ou documentar como "só interpret" |
| **SLA Lifecycle** | GET /api/v1/nasp/diagnostics | real (NASP probe); placeholder Runtime SLA Status | parcial | endpoint consolidado de "Runtime SLA Status" ou remover/renomear card |
| **Monitoring** | PROMETHEUS_SUMMARY, TRANSPORT_METRICS, RAN_METRICS | real para Prometheus/Transport/RAN; placeholder Core | parcial | Core Domain: endpoint real (ex.: CORE_METRICS_REALTIME) ou marcar "N/A" |
| **Metrics** | PROMETHEUS_SUMMARY, TRANSPORT_METRICS | real para CPU/Memory/Transport; placeholder SLA Evidence | parcial | SLA Evidence Feed: fonte real ou remover/renomear |
| **Defense** | nenhum | placeholder total | residual | definir endpoint(s) de defesa (policy, integrity, trust) ou manter como stub |
| **Administration** | GLOBAL_HEALTH, NASP_DIAGNOSTICS | real | concluído | nada |

---

## FASE 3 — Prioridade real para próxima evolução

**Recomendação: A) PNL**

**Justificativa técnica:**

1. **Fluxo científico principal:** PNL (interpret) é a entrada semântica; Template (submit) já está fechado. O próximo passo lógico é alinhar o PNL ao mesmo padrão científico: hoje o PNL exibe message e technical_parameters/sla_requirements reais, mas XAI Metrics, Domain Viability (além de technical_parameters), Blockchain e Admission Decision estão em awaiting. Não é necessário novo backend: basta documentar que /interpret não expõe decisão/XAI/BC e opcionalmente oferecer ação "Usar este template para submeter" (já prevista no runbook) para levar o usuário ao Template, onde o XAI completo está disponível após submit.

2. **Menor dependência de backend novo:** SLA Lifecycle, Monitoring (Core), Metrics (SLA Evidence) e Defense dependem de endpoints ou contratos que podem não existir. O PNL pode ser "fechado" com pequenas melhorias de copy e link para Template, sem alterar backend.

3. **Consistência de UX:** Template já mostra reasoning, confidence, domains, metadata. O PNL pode explicitar que "Decisão e XAI completo estão no fluxo Template (submeter)" e manter apenas os campos que /interpret realmente entrega, eliminando placeholders confusos ou rotulando-os como "disponível após submissão no Template".

Alternativa igualmente defensável: **B) SLA Lifecycle** — se houver um endpoint consolidado de status SLA (ex.: GET /api/v1/sla/status ou lista de SLAs), o card "Runtime SLA Status" passaria a ter fonte real. Como o objetivo é não alterar backend agora, **A) PNL** permanece a prioridade que não exige novo endpoint.

---

## FASE 4 — Não alterar código

Nenhuma alteração de código foi feita. Somente auditoria.

---

## FASE 5 — Runbook

Atualização aplicada em `docs/TRISLA_MASTER_RUNBOOK.md`: **Frontend Full Functional Audit Started**.

Evidência completa neste documento: `docs/AUDITORIA_FRONTEND_FULL_FUNCTIONAL_20260318.md`.
