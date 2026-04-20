# Auditoria Completa da Integração API — Portal TriSLA

**Data:** 2026-03-17  
**Escopo:** Frontend (portal-frontend) × Backend (portal-backend)  
**Regra:** Nenhuma alteração de código; apenas auditoria + mapa técnico + plano.

---

## 1. Mapa completo — Endpoints chamados pelo frontend

| Rota (chave) | Método | Path real | Página(s) | Finalidade |
|--------------|--------|-----------|-----------|------------|
| GLOBAL_HEALTH | GET | /api/v1/health | Home, Administration | Estado executivo / health |
| PROMETHEUS_SUMMARY | GET | /api/v1/prometheus/summary | Home, Monitoring | Observabilidade consolidada |
| CORE_METRICS_REALTIME | GET | /api/v1/core-metrics/realtime | Metrics | Métricas core em tempo real |
| TRANSPORT_METRICS | GET | /api/v1/modules/transport/metrics | Metrics | Métricas domínio transport |
| RAN_METRICS | GET | /api/v1/modules/ran/metrics | Metrics | Métricas domínio RAN |
| SLA_INTERPRET | POST | /api/v1/sla/interpret | PNL | Interpretação semântica PNL |
| SLA_SUBMIT | POST | /api/v1/sla/submit | Template | Submissão estruturada de SLA |

**Declarados em `endpoints.ts` mas não usados por nenhuma página:**  
`MODULES` (/api/v1/modules/), `NASP_DIAGNOSTICS` (/api/v1/nasp/diagnostics).

**Arquivos frontend:**  
- `src/lib/endpoints.ts` — definição das rotas  
- `src/lib/api.ts` — cliente único `apiRequest()`  
- `src/app/page.tsx` — Home (GLOBAL_HEALTH, PROMETHEUS_SUMMARY)  
- `src/app/administration/page.tsx` — Administration (GLOBAL_HEALTH)  
- `src/app/monitoring/page.tsx` — Monitoring (PROMETHEUS_SUMMARY)  
- `src/app/metrics/page.tsx` — Metrics (CORE_METRICS_REALTIME, TRANSPORT_METRICS, RAN_METRICS)  
- `src/app/pnl/page.tsx` — PNL (SLA_INTERPRET)  
- `src/app/template/page.tsx` — Template (SLA_SUBMIT)

---

## 2. Mapa completo — Endpoints existentes no backend

### 2.1 Rotas em `main.py` (sem prefixo de router)

| Rota | Método | Função | Status conceitual |
|------|--------|--------|--------------------|
| / | GET | root | OK |
| /health | GET | health_check | OK |
| /api/v1/health | GET | health_v1 | OK |
| /api/v1/health/global | GET | health_global | OK |
| /nasp/diagnostics | GET | nasp_diagnostics | OK |
| /metrics | GET | metrics (Prometheus raw) | OK |

### 2.2 Router SLA (`prefix="/api/v1/sla"`)

| Rota | Método | Função | Status conceitual |
|------|--------|--------|--------------------|
| /interpret | POST | interpret_sla | OK (depende SEM-CSMF) |
| /submit | POST | submit_sla | OK (depende NASP) |
| /status/{sla_id} | GET | status_sla | OK |
| /metrics/{sla_id} | GET | metrics_sla | OK |

### 2.3 Router Modules (`prefix="/api/v1/modules"`)

| Rota | Método | Função | Status conceitual |
|------|--------|--------|--------------------|
| / | GET | list_modules | OK |
| /{module} | GET | get_module | OK |
| /{module}/metrics | GET | get_module_metrics | OK |
| /{module}/status | GET | get_module_status | OK |

### 2.4 Router Prometheus (`prefix="/api/v1/prometheus"`)

| Rota | Método | Função | Status conceitual |
|------|--------|--------|--------------------|
| / | GET | prometheus_root | OK |
| /query | GET | query_prometheus | OK |
| /query_range | GET | query_range_prometheus | OK |
| /targets | GET | get_targets | OK |
| /summary | GET | observability_summary | OK |

**Importante:** No código atual do repositório **não existe** rota para `/api/v1/core-metrics/realtime`. O frontend chama esse path; em teste no cluster o backend respondeu 200, o que pode indicar imagem deployada com versão diferente ou rota adicionada em outro branch. No `main.py` atual só estão registrados: `sla`, `modules`, `prometheus`.

---

## 3. Testes endpoint a endpoint

### 3.1 Via frontend (origem NodePort 192.168.10.15:32561)

Todas as requisições para `/api/v1/*` no mesmo host/porta do frontend retornaram **404**. O Next.js atual **não** possui rewrites/proxy para encaminhar `/api` ao backend; portanto, no runtime atual as chamadas do browser para `/api/v1/...` são atendidas pelo próprio Next e resultam em 404.

| Endpoint | Status HTTP | Diagnóstico |
|----------|-------------|-------------|
| GET /api/v1/health | 404 | Next.js não encaminha para o backend |
| GET /api/v1/prometheus/summary | 404 | Idem |
| GET /api/v1/core-metrics/realtime | 404 | Idem |
| GET /api/v1/modules/transport/metrics | 404 | Idem |
| GET /api/v1/modules/ran/metrics | 404 | Idem |

### 3.2 Via backend no cluster (trisla-portal-backend:8001)

| Endpoint | Status HTTP | Diagnóstico |
|----------|-------------|-------------|
| GET /api/v1/health | 200 | OK |
| GET /api/v1/prometheus/summary | 200 | OK (payload: up, cpu, memory) |
| GET /api/v1/core-metrics/realtime | 200 | OK no cluster (rota não presente no main.py do repo) |
| GET /api/v1/modules/transport/metrics | 200 | OK |
| GET /api/v1/modules/ran/metrics | 200 | OK |
| POST /api/v1/sla/interpret | 503 | Serviço/SEM-CSMF indisponível ou erro upstream |
| POST /api/v1/sla/submit | 503 | Idem |

---

## 4. Matriz Frontend × Backend

| Endpoint | Frontend usa | Backend existe (repo) | Status real (backend) | Ação futura |
|----------|--------------|------------------------|------------------------|-------------|
| /api/v1/health | Sim (Home, Admin) | Sim | 200 | Consolidar; garantir proxy ou base URL |
| /api/v1/prometheus/summary | Sim (Home, Monitoring) | Sim | 200 | Alinhar contrato (payload: up/cpu/memory vs activeTargets/jobs/summary_text) |
| /api/v1/core-metrics/realtime | Sim (Metrics) | Não (não em main.py) | 200 no cluster* | Confirmar imagem deployada; criar rota no repo ou apontar para /api/v1/modules/core/metrics |
| /api/v1/modules/transport/metrics | Sim (Metrics) | Sim ({module}=transport) | 200 | Manter; garantir proxy/base URL |
| /api/v1/modules/ran/metrics | Sim (Metrics) | Sim ({module}=ran) | 200 | Idem |
| /api/v1/sla/interpret | Sim (PNL) | Sim | 503** | Manter contrato; tratar indisponibilidade NASP |
| /api/v1/sla/submit | Sim (Template) | Sim | 503** | Idem |
| /api/v1/modules/ | Não | Sim | - | Opcional uso futuro |
| /api/v1/nasp/diagnostics | Não | Sim (/nasp/diagnostics) | - | Prefixo frontend é /api/v1/nasp/diagnostics; backend é /nasp/diagnostics — alinhar se for usar |

\* Cluster pode estar com imagem de backend que inclui rota não commitada.  
\** Contrato correto; 503 por dependência (SEM-CSMF/NASP) não disponível no momento do teste.

---

## 5. Contratos Pydantic (endpoints usados pelo frontend)

| Endpoint | Input model | Output / resposta | Alinhamento frontend |
|----------|-------------|-------------------|----------------------|
| GET /api/v1/health | - | health_check: status, version, nasp_reachable, nasp_details_url | Home/Admin esperam esses campos |
| GET /api/v1/prometheus/summary | - | observability_summary: up, cpu, memory (por query Prometheus) | Frontend espera activeTargets, jobs, summary_text — **divergência** |
| POST /api/v1/sla/interpret | SLAInterpretRequest (intent_text, tenant_id) | Resposta SEM-CSMF (intent_id, nest_id, service_type, technical_parameters, etc.) | PNL envia e exibe campos alinhados |
| POST /api/v1/sla/submit | SLASubmitRequest (template_id, form_values, tenant_id) | SLASubmitResponse (decision, ml_prediction, sla_id, etc.) | Template envia e exibe campos alinhados |
| GET /api/v1/modules/{module}/metrics | module path | get_module_metrics (serviço) | Metrics exibe JSON bruto — OK |

**Schemas principais (src/schemas/sla.py):**  
- SLAInterpretRequest, SLASubmitRequest  
- SLAStatusResponse, SLAMetricsResponse, SLASubmitResponse  

---

## 6. Prefixos e conflitos

- **Routers:** Todos com prefixo `/api/v1/...`; sem conflito de path entre sla, modules e prometheus.
- **Health:** Duas rotas em main: `/api/v1/health` e `/api/v1/health/global`; frontend usa apenas `/api/v1/health` (endpoint consolidado).
- **NASP:** Backend expõe `/nasp/diagnostics` (sem `/api/v1`). Frontend declara `NASP_DIAGNOSTICS: "/api/v1/nasp/diagnostics"` — não usado hoje; se for usado, backend precisará de alias ou frontend apontar para `/nasp/diagnostics`.
- **Core metrics:** Frontend usa `/api/v1/core-metrics/realtime`; no repo não há rota com esse path (apenas `/api/v1/modules/{module}/metrics`). Possível convenção: `core` como module → `/api/v1/modules/core/metrics`, ou criar rota dedicada no backend.

---

## 7. Plano oficial de integração API em 5 fases

### FASE API-1 — Consolidar acesso ao backend (proxy ou base URL)

- **Objetivo:** Fazer com que todas as chamadas do frontend a `/api/v1/*` alcancem o backend (200 onde o backend responde 200).
- **Endpoints envolvidos:** Todos os que o frontend já chama (health, prometheus/summary, core-metrics/realtime, modules/transport/metrics, modules/ran/metrics, sla/interpret, sla/submit).
- **Backend:** Nenhuma alteração obrigatória.
- **Frontend:** Configurar base URL do backend (ex.: variável de ambiente `NEXT_PUBLIC_API_BASE` ou equivalente) e usar em `api.ts`, **ou** configurar rewrites em `next.config.js` para proxy `/api` → backend (ex.: `http://trisla-portal-backend:8001` em runtime server).
- **Risco:** Baixo (só configuração de rede/URL).  
- **Prioridade:** Alta.

---

### FASE API-2 — Alinhar Home e Monitoring a endpoints reais

- **Objetivo:** Home e Monitoring consumirem apenas endpoints que existem e exibirem campos realmente retornados.
- **Endpoints:** GET /api/v1/health; GET /api/v1/prometheus/summary.
- **Backend:** Opcional — decidir se /summary continua retornando apenas up/cpu/memory ou se passa a incluir activeTargets, jobs, summary_text para compatibilidade com o frontend atual.
- **Frontend:** Ajustar tipos e UI de Home e Monitoring para o payload real de /api/v1/prometheus/summary (up, cpu, memory); ou combinar com /targets se precisar de jobs/targets.
- **Risco:** Médio (mudança de contrato em uma das pontas).  
- **Prioridade:** Alta.

---

### FASE API-3 — Conectar Metrics a domínios realmente existentes

- **Objetivo:** Página Metrics usar apenas rotas que existem no backend e exibir dados sem inventar métricas.
- **Endpoints:** GET /api/v1/core-metrics/realtime (ou /api/v1/modules/core/metrics se for o caso); GET /api/v1/modules/transport/metrics; GET /api/v1/modules/ran/metrics.
- **Backend:** Confirmar se a imagem em produção expõe /api/v1/core-metrics/realtime; se não, criar rota no repo ou documentar uso de /api/v1/modules/core/metrics e atualizar frontend.
- **Frontend:** Garantir que CORE_METRICS_REALTIME aponte para a rota efetiva (ex.: /api/v1/modules/core/metrics se core-metrics/realtime for descontinuado).
- **Risco:** Baixo a médio (depende da decisão sobre core-metrics).  
- **Prioridade:** Média.

---

### FASE API-4 — Evoluir SLA Lifecycle com dados reais por SLA

- **Objetivo:** Página SLA Lifecycle consumir dados reais de status e métricas por SLA.
- **Endpoints:** GET /api/v1/sla/status/{sla_id}; GET /api/v1/sla/metrics/{sla_id} (e eventualmente listagem de SLAs se houver endpoint).
- **Backend:** Já expõe status e metrics por sla_id; eventualmente listagem ou filtros se necessário.
- **Frontend:** Implementar chamadas a status e metrics por SLA (após PNL/Template gerarem sla_id) e exibir em SLA Lifecycle.
- **Risco:** Médio (nova integração em página hoje estática).  
- **Prioridade:** Média.

---

### FASE API-5 — Defense e Administration com agregadores científicos

- **Objetivo:** Conectar Defense e Administration a endpoints que forneçam visão agregada (ex.: health global, NASP, módulos).
- **Endpoints:** GET /api/v1/health; GET /api/v1/health/global; GET /nasp/diagnostics (ou /api/v1/nasp/diagnostics se padronizado); GET /api/v1/modules/ (lista de módulos); eventualmente slos, contracts, xai conforme runbook.
- **Backend:** Manter ou expor agregadores necessários; padronizar prefixo /api/v1 para NASP se for usado pelo frontend.
- **Frontend:** Administration já usa GLOBAL_HEALTH; estender com health/global e NASP conforme necessidade; Defense ligar a endpoints de defesa/observabilidade (ex.: Prometheus, SLOS, XAI) quando definidos.
- **Risco:** Médio (novos consumos e possíveis novos endpoints).  
- **Prioridade:** Baixa a média.

---

## 8. Resumo executivo

1. **Frontend** chama 7 endpoints em 5 páginas; 2 chaves em `endpoints.ts` não são usadas (MODULES, NASP_DIAGNOSTICS).
2. **Backend** no repositório expõe health, sla (interpret/submit/status/metrics), modules (list/get/metrics/status), prometheus (root/query/query_range/targets/summary); **não** declara `/api/v1/core-metrics/realtime` no `main.py` atual.
3. **Via frontend (NodePort)** todas as chamadas /api/* retornam **404** por ausência de proxy/rewrite para o backend.
4. **Via backend no cluster** health, prometheus/summary, modules/transport|ran/metrics retornam **200**; sla/interpret e sla/submit retornam **503** (dependência NASP/SEM-CSMF).
5. **Contrato** prometheus/summary: backend retorna up/cpu/memory; frontend espera activeTargets/jobs/summary_text — requer alinhamento em FASE API-2.
6. **Plano em 5 fases:** API-1 (proxy/base URL), API-2 (Home/Monitoring), API-3 (Metrics/core), API-4 (SLA Lifecycle), API-5 (Defense/Administration).

Nenhuma implementação foi alterada; este documento serve como SSOT para o plano de integração API do portal TriSLA.
