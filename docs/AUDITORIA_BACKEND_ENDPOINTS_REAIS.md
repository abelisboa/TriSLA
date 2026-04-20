# Auditoria Backend — Endpoints Reais (FASE 0–1)

**Data:** 2026-03-18  
**Regra:** Backend first — frontend só consome o que existe.

## Backend portal-backend (apps/portal-backend/src)

### Rotas expostas (main.py + routers)

| Método | Path | Fonte | Observação |
|--------|------|--------|------------|
| GET | / | main.py | Root |
| GET | /health | main.py | status, version, nasp_details_url |
| GET | /api/v1/health | main.py | alias health |
| GET | /api/v1/health/global | main.py | status, timestamp (NASP reachable) |
| GET | /nasp/diagnostics | main.py | **Sem prefixo /api/v1** — diagnóstico NASP |
| GET | /metrics | main.py | Prometheus scrape |
| POST | /api/v1/sla/interpret | routers/sla.py | PNL → SEM-CSMF real |
| POST | /api/v1/sla/submit | routers/sla.py | Template → pipeline real |
| GET | /api/v1/sla/status/{sla_id} | routers/sla.py | Status SLA |
| GET | /api/v1/sla/metrics/{sla_id} | routers/sla.py | Métricas SLA |
| GET | /api/v1/modules/ | routers/modules.py | Lista módulos |
| GET | /api/v1/modules/{module} | routers/modules.py | Detalhe módulo |
| GET | /api/v1/modules/{module}/metrics | routers/modules.py | Métricas do módulo |
| GET | /api/v1/modules/{module}/status | routers/modules.py | Status do módulo |
| GET | /api/v1/prometheus/ | routers/prometheus.py | Router ativo |
| GET | /api/v1/prometheus/query | routers/prometheus.py | Query Prometheus |
| GET | /api/v1/prometheus/query_range | routers/prometheus.py | Range |
| GET | /api/v1/prometheus/targets | routers/prometheus.py | Targets |
| GET | /api/v1/prometheus/summary | routers/prometheus.py | up, cpu, memory |

### Payload real (amostra)

- **GET /api/v1/health/global:** `{"status":"unhealthy|healthy","timestamp":null}`
- **GET /api/v1/prometheus/summary:** `{ "up": { "status", "data": { "result": [...] } }, "cpu", "memory" }`
- **GET /api/v1/modules/:** `[{"name":"sem-csmf","status":"UP"}, ...]`

### Endpoints que o backend **não** expõe

- `/api/v1/core-metrics/realtime` — frontend pode 404.
- `/api/v1/nasp/diagnostics` — backend expõe `/nasp/diagnostics` (sem /api/v1). Proxy deve mapear ou backend expor sob /api/v1.

## Frontend → Backend

- Browser chama **sempre** same-origin `/api/v1/*` (api.ts retorna `'/api/v1'`).
- App Router **src/app/api/v1/[...path]/route.ts** faz proxy para `BACKEND_URL` (env).
- **Sem rewrites** para hostname interno; evita ERR_NAME_NOT_RESOLVED fora do cluster.
