# RELATÓRIO DE AUDITORIA COMPLETA — Portal TriSLA Científico SLA-Centric

**Data:** 2025-03-16  
**Escopo:** Frontend exclusivo, consumo backend e Prometheus. SSOT: documentos "Evolução do Portal TriSLA para Portal Científico SLA-Centric" e "MATRIZ TÉCNICA OFICIAL — Portal TriSLA Científico SLA-Centric".  
**Regra:** Nenhuma alteração de código; apenas auditoria.

---

## 1. Estrutura oficial de menus (SSOT)

Conforme MATRIZ TÉCNICA OFICIAL, a ordem e nomes corretos são:

| # | Menu oficial |
|---|------------------|
| 1 | Home |
| 2 | Criar SLA PNL |
| 3 | Criar SLA Template |
| 4 | SLA Lifecycle |
| 5 | Monitoring |
| 6 | Metrics |
| 7 | SLA-Aware Full Defense Panel |
| 8 | Administration |

---

## 2. Auditoria do frontend atual

### 2.1 Menus existentes

- **Sidebar** (`apps/portal-frontend/src/components/layout/Sidebar.tsx`): 7 itens — **falta "Administration".**
- **page.tsx** (`apps/portal-frontend/app/page.tsx`): `renderSection()` tem `switch (selected)` para: Home (default), Criar SLA PNL, Criar SLA Template, SLA Lifecycle, Monitoring, Metrics, SLA-Aware Full Defense Panel. **Não há case "Administration"; não existe seção de Administração.**

### 2.2 Componentes em `apps/portal-frontend/src/sections`

| Componente | Arquivo | Menu correspondente |
|------------|---------|----------------------|
| HomeSection | HomeSection.tsx | Home |
| PnlSlaSection | PnlSlaSection.tsx | Criar SLA PNL |
| TemplateSlaSection | TemplateSlaSection.tsx | Criar SLA Template |
| SlaLifecycleSection | SlaLifecycleSection.tsx | SLA Lifecycle |
| MonitoringSection | MonitoringSection.tsx | Monitoring |
| MetricsSection | MetricsSection.tsx | Metrics |
| DefensePanelSection | DefensePanelSection.tsx | SLA-Aware Full Defense Panel |
| **(ausente)** | — | **Administration** |

### 2.3 `app/page.tsx`

- Uma única página; roteamento por estado `selected` (sidebar).
- Sem rotas adicionais; sem case para Administration.

### 2.4 `lib/api.ts`

- **API_BASE:** `process.env.NEXT_PUBLIC_API_BASE || '/api'`.
- **Endpoints utilizados:**

| Método | Path | Uso |
|--------|------|-----|
| GET | `/api/v1/prometheus/summary` | prometheusSummary() |
| GET | `/api/v1/health` | backendHealth() |
| GET | `/api/v1/sla` | slaList() |
| GET | `/api/v1/modules` | defenseSummary() |

- **fetchJson:** usa `fetch(API_BASE + path)`; se resposta tem `body.data`, retorna `body.data`, senão retorna `body`.

### 2.5 Fetches existentes por seção

| Seção | Fetch | Endpoint | Observação |
|-------|--------|----------|------------|
| HomeSection | backendHealth() | /api/v1/health | ✅ Dados reais |
| PnlSlaSection | nenhum | — | ❌ Mock/local only |
| TemplateSlaSection | nenhum | — | ❌ Mock/local only |
| SlaLifecycleSection | slaList() | /api/v1/sla | ⚠ Endpoint inexistente (ver backend) |
| MonitoringSection | prometheusSummary() | /api/v1/prometheus/summary | ✅ Endpoint existe; shape frontend incorreto (ver abaixo) |
| MetricsSection | prometheusSummary() | /api/v1/prometheus/summary | ✅ Dados reais; availability derivado |
| DefensePanelSection | nenhum | — | ❌ Dados hardcoded (mock) |

### 2.6 Menus que já consomem dados reais

- **Home:** parcial — apenas backend status e last refresh; Total SLAs e Active SLAs são "-" (placeholder).
- **SLA Lifecycle:** chama GET /api/v1/sla, mas esse endpoint **não existe** no backend (retorno vazio ou erro).
- **Monitoring:** consome /api/v1/prometheus/summary; backend retorna objeto normalizado; frontend espera `data.up` para targets (inexistente) → "Observable Targets" pode ficar 0.
- **Metrics:** consome /api/v1/prometheus/summary; CPU, memory, modules reais; "Availability" = 100 se targets>0 senão 0 (derivado).

### 2.7 Menus com mock ou payload inadequado

- **Criar SLA PNL:** sem chamada ao SEM-CSMF; botão apenas atualiza texto local ("Semantic processing prepared for: ..."). **Mock.**
- **Criar SLA Template:** formulário local; botão "Generate SLA Template" não envia ao backend. **Mock.**
- **SLA-Aware Full Defense Panel:** tabela com array `rows` fixo (73db6142, 51aa21bc). **Mock explícito.** Não usa `portalApi.defenseSummary()`.
- **Monitoring:** exibe payload bruto (JSON) em `<pre>` como visão principal. SSOT exige que payload bruto fique em Administration, em seção "Expandir detalhes", não em Monitoring.

---

## 3. Auditoria do backend consumido

### 3.1 Endpoints reais existentes (portal-backend)

| Método | Path | Arquivo | Observação |
|--------|------|---------|------------|
| GET | /health | main.py | ✅ |
| GET | /api/v1/health | main.py | ✅ |
| GET | /api/v1/health/global | main.py | ✅ |
| GET | /api/v1/nasp/diagnostics | main.py | ✅ |
| POST | /api/v1/sla/interpret | routers/sla.py | ✅ |
| POST | /api/v1/sla/submit | routers/sla.py | ✅ |
| GET | /api/v1/sla/status/{sla_id} | routers/sla.py | ✅ |
| GET | /api/v1/sla/metrics/{sla_id} | routers/sla.py | ✅ |
| **GET** | **/api/v1/sla** | **—** | **❌ Não existe** (não há GET list no router sla) |
| GET | /api/v1/modules/ | routers/modules.py | ✅ |
| GET | /api/v1/modules/{module} | routers/modules.py | ✅ |
| GET | /api/v1/modules/{module}/metrics | routers/modules.py | ✅ |
| GET | /api/v1/modules/{module}/status | routers/modules.py | ✅ |
| GET | /api/v1/prometheus/ | routers/prometheus.py | ✅ |
| GET | /api/v1/prometheus/query | routers/prometheus.py | ✅ |
| GET | /api/v1/prometheus/query_range | routers/prometheus.py | ✅ |
| GET | /api/v1/prometheus/targets | routers/prometheus.py | ✅ |
| GET | /api/v1/prometheus/summary | routers/prometheus.py | ✅ |

### 3.2 Endpoints realmente chamados pelo frontend

| Endpoint | Chamado por | Status |
|----------|-------------|--------|
| /api/v1/health | HomeSection | ✅ Existe |
| /api/v1/prometheus/summary | MonitoringSection, MetricsSection | ✅ Existe |
| /api/v1/sla | SlaLifecycleSection | ❌ **Não existe** (405/404) |
| /api/v1/modules | Nenhuma seção atualmente | ✅ Existe; DefensePanel não o usa |

### 3.3 Shape real do payload (endpoints usados)

- **GET /api/v1/health**  
  Resposta: `{ status, version, nasp_reachable, nasp_details_url }`.

- **GET /api/v1/prometheus/summary**  
  Resposta (objeto direto, sem wrapper `data`):
  - `cpu`: number (process_cpu_seconds_total)
  - `memory`: number (MB, de process_resident_memory_bytes)
  - `observable_targets`: number (len de up result)
  - `availability`: 100 ou 0
  - `monitored_modules`: igual a observable_targets  

  O frontend em MonitoringSection usa `data.up?.data?.result?.length` → **undefined**; deve usar `data.observable_targets`.

- **GET /api/v1/sla**  
  **Não implementado.** Frontend espera array de `{ id, slice_type, state, admission, blockchain, nasp, runtime }`.

- **GET /api/v1/modules**  
  Retorno: lista de `{ name, status }` (ModuleService.list_modules). Serviço hoje retorna lista fixa (sem consulta dinâmica a Prometheus para status).

### 3.4 Endpoints disponíveis e não usados pelo frontend

- /api/v1/health/global  
- /api/v1/nasp/diagnostics  
- /api/v1/sla/interpret (POST) — relevante para Criar SLA PNL  
- /api/v1/sla/submit (POST) — relevante para Criar SLA Template  
- /api/v1/sla/status/{sla_id}  
- /api/v1/sla/metrics/{sla_id}  
- /api/v1/modules (list) — útil para Defense e Administration  
- /api/v1/modules/{module}, /metrics, /status  
- /api/v1/prometheus/query, query_range, targets  

### 3.5 Validação dos endpoints críticos (SSOT)

- **/api/v1/prometheus/summary:** ✅ Existente; retorna cpu, memory, observable_targets, availability, monitored_modules (métricas up, process_cpu_seconds_total, process_resident_memory_bytes).
- **/api/v1/slas:** Não existe; frontend usa **/api/v1/sla** (singular). Backend tem router em `/api/v1/sla` mas sem GET / para listagem.
- **/health:** ✅ Existente em /health e /api/v1/health.

---

## 4. Auditoria Prometheus consumido

### 4.1 Métricas reais no summary (backend)

O endpoint `/api/v1/prometheus/summary` consulta apenas:

| Métrica Prometheus | Uso no summary |
|--------------------|-----------------|
| process_cpu_seconds_total | cpu (escalar) |
| process_resident_memory_bytes | memory (MB) |
| up | contagem de targets (observable_targets / monitored_modules) |

### 4.2 Métricas reais confirmadas no SSOT (documento Evolução)

- up  
- process_cpu_seconds_total  
- process_resident_memory_bytes  
- registration_total  
- pdu_session_total  
- pfcp_session_total  
- duplicate_pdu_errors_total  
- log_collection_success  

**No summary atual:** apenas up, process_cpu_seconds_total, process_resident_memory_bytes. As demais **não** são agregadas no summary (podem existir no Prometheus, mas o portal não as consome neste endpoint).

---

## 5. Matriz real: Menu × Endpoint × Payload × Status × Aderência SSOT

| Menu | Endpoint usado | Payload / Fonte | Status | Aderência SSOT |
|------|----------------|------------------|--------|-----------------|
| Home | /api/v1/health | status, version, nasp_details_url | Parcial | ⚠ Falta total/active SLAs, targets, saúde observabilidade; cards Total/Active SLAs com "-" |
| Criar SLA PNL | nenhum | — | Mock | ❌ Deveria usar SEM-CSMF (ex.: /api/v1/sla/interpret) |
| Criar SLA Template | nenhum | — | Mock | ❌ Deveria usar backend SLA create (ex.: /api/v1/sla/submit ou path de template) |
| SLA Lifecycle | /api/v1/sla | Espera array SLA; endpoint não existe | Quebrado | ⚠ Backend não expõe GET list; depende agregador futuro |
| Monitoring | /api/v1/prometheus/summary | cpu, memory, targets; frontend usa `data.up` (errado) | Parcial | ⚠ Payload bruto em tela; SSOT: Core/Transporte/RAN por domínio |
| Metrics | /api/v1/prometheus/summary | cpu, memory, availability, modules | Correto | ✅ Métricas reais; availability derivada (targets>0 → 100%) |
| SLA-Aware Full Defense Panel | nenhum | rows hardcoded | Mock | ❌ Deveria usar agregador (Decision, ML, SEM, BC, NASP, Observability) |
| Administration | — | — | **Ausente** | ❌ Menu e seção não existem; SSOT exige visão executiva + "Expandir detalhes" |

---

## 6. Respostas diretas (entregáveis da auditoria)

### Quais menus estão corretos?

- **Metrics:** uso correto de prometheus/summary; métricas reais (CPU, memória, módulos); availability derivada de forma explícita (targets>0).

### Quais menus estão parcialmente corretos?

- **Home:** backend status e last refresh corretos; Total SLAs e Active SLAs placeholder "-"; falta targets e saúde observabilidade.  
- **SLA Lifecycle:** UI e colunas alinhadas ao SSOT; dado vazio porque GET /api/v1/sla não existe.  
- **Monitoring:** consome summary real; exibição de payload bruto inadequada; "Observable Targets" pode ser 0 por uso de `data.up` em vez de `data.observable_targets`.

### Quais menus violam os documentos oficiais?

- **Criar SLA PNL:** não prova entrada semântica; sem chamada a endpoint real (interpret).  
- **Criar SLA Template:** não prova criação controlada GST/NEST; sem envio ao backend.  
- **SLA-Aware Full Defense Panel:** dados fictícios; não prova defesa SLA-aware ponta a ponta.  
- **Monitoring:** exibe payload bruto como visão principal (SSOT reserva isso para Administration, em seção recolhida).  
- **Administration:** menu e seção inexistentes (SSOT exige menu 8).

### Quais dados reais existem por menu?

- Home: backend status, last refresh.  
- SLA Lifecycle: nenhum (endpoint list inexistente).  
- Monitoring: cpu, memory; targets se frontend usar `observable_targets`.  
- Metrics: cpu, memory, availability (derivada), monitored_modules.

### Quais campos ainda dependem de agregação futura no backend?

- Contagem de SLAs (total, active, approved, monitored) para Home.  
- Lista de SLAs com colunas Lifecycle (SLA ID, Slice Type, Estado, Admission, Blockchain, NASP, Runtime) — requer GET /api/v1/sla ou agregador equivalente.  
- Painel Defense (Admission, Prediction, Semantic validation, Blockchain, Deployment, Observability) — requer agregador ou uso de /api/v1/modules + outros.

### Quais menus já podem ser refatorados apenas no frontend?

- **Home:** refatorar para usar /api/v1/prometheus/summary (observable_targets) e manter health; continuar exibindo "-" para total/active SLAs até existir endpoint, ou documentar como "aguardando agregador".  
- **Monitoring:** remover payload bruto da visão principal; usar cards com cpu, memory, observable_targets (corrigir de `data.up` para `data.observable_targets`).  
- **Metrics:** já aderente; apenas revisão de rótulos/legenda se desejado.  
- **Administration:** criar novo menu + seção (visão executiva + "Expandir detalhes" com payload técnico), consumindo /api/v1/health, /api/v1/prometheus/summary e /api/v1/modules, sem alterar backend.

---

## 7. Próximos passos (sem implementar)

1. **FASE OBRIGATÓRIA 2 — Plano técnico:** construir plano menu a menu (objetivo científico, fonte real, endpoint real, campos existentes/deriváveis/indisponíveis, status: pronto/parcial/depends backend).  
2. **FASE 3 — Implementação:** somente após aprovação explícita; alterar apenas frontend; menu a menu; validar endpoint e payload antes de cada mudança.  
3. **FASE 4 — Build e deploy:** npm run build; container com digest; helm upgrade digest-only; validar imageID e bundle no pod.

---

*Fim do Relatório de Auditoria. Nenhum código foi alterado.*
