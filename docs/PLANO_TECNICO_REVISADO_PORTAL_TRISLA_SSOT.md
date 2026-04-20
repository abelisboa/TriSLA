# PLANO TÉCNICO REVISADO — Portal TriSLA Científico SLA-Centric

**Data:** 2025-03-16  
**Base:** Documentos SSOT (Evolução do Portal TriSLA; MATRIZ TÉCNICA OFICIAL), AUDITORIA_PORTAL_TRISLA_FRONTEND_BACKEND_SSOT.md, AUDITORIA_COMPLEMENTAR_FLUXO_PONTA_A_PONTA_PNL_TEMPLATE.md, AUDITORIA_XAI_TRISLA_PORTAL.md.  
**Escopo:** Apenas frontend; implementação somente após aprovação explícita.

---

## Menus obrigatórios (ordem SSOT)

1. Home  
2. Criar SLA PNL  
3. Criar SLA Template  
4. SLA Lifecycle  
5. Monitoring  
6. Metrics  
7. SLA-Aware Full Defense Panel  
8. Administration  

---

## MENU 1 — Home

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Visão executiva do ambiente TriSLA (SLA-centric). |
| **Pergunta científica** | O ambiente TriSLA está operacional e possui SLAs gerenciáveis? |
| **Fonte real** | Backend: /api/v1/health; /api/v1/prometheus/summary. |
| **Endpoint real** | GET /api/v1/health; GET /api/v1/prometheus/summary. |
| **Payload real** | health: { status, version, nasp_reachable, nasp_details_url }; summary: { cpu, memory, observable_targets, availability, monitored_modules }. |
| **Campos existentes** | status, version, last refresh (local), observable_targets, monitored_modules, cpu, memory. |
| **Campos deriváveis** | Nenhum adicional sem agregador. |
| **Campos indisponíveis** | total SLAs, active SLAs, approved SLAs, monitored SLAs (dependem de agregador backend). |
| **Dependência agregador** | Contagem de SLAs (total/active/approved/monitored) — registrar como pendência; não inventar números. |
| **Status** | Parcial. |

**Implementação frontend (após aprovação):** Cards: Backend Status (health); Last Refresh (timestamp local); Observable Targets / Monitored Modules (observable_targets); CPU / Memory (summary). Para total/active/approved/monitored SLAs: exibir "-" ou "N/A" com legenda "aguardando agregador backend" até existir endpoint.

---

## MENU 2 — Criar SLA PNL

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Entrada semântica natural da TriSLA; demonstrar interpretação real via SEM-CSMF e ontologia. |
| **Pergunta científica** | O SLA foi solicitado em linguagem natural e interpretado semanticamente pela TriSLA? |
| **Fonte real** | Portal-backend POST /api/v1/sla/interpret → SEM-CSMF /api/v1/interpret + /api/v1/intents. |
| **Endpoint real** | POST /api/v1/sla/interpret. |
| **Payload real** | Request: { intent_text: string, tenant_id: string }. Response: intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements, technical_parameters, message, status, nest_id, created_at. |
| **Campos existentes** | Todos os campos da resposta do backend (intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements, etc.). |
| **Campos deriváveis** | Nenhum; não inferir tipo de slice nem constraints no frontend. |
| **Campos indisponíveis** | Nenhum para este menu; a resposta é completa no backend. |
| **Dependência agregador** | Nenhuma. |
| **Status** | Parcial (backend pronto; frontend mock atual). |

**Implementação frontend (após aprovação):** Campo de entrada (frase natural) + tenant_id; botão "Interpretar" chama POST /api/v1/sla/interpret; exibir fluxo: **Entrada** → **Interpretação** (service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements) → **Template gerado** (resumo). Não replicar ontologia nem lógica semântica; apenas exibir resposta do backend. **Exibir obrigatoriamente** os campos da seção **EXPLICAÇÃO DA DECISÃO (XAI)** abaixo quando disponíveis na resposta (ver docs/AUDITORIA_XAI_TRISLA_PORTAL.md). Ver subseção "Validação do fluxo semântico formal TriSLA" abaixo.

---

## MENU 3 — Criar SLA Template

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Entrada controlada GST/NEST; fluxo completo até admission, decision, blockchain e orquestração NASP quando suportado. |
| **Pergunta científica** | O SLA foi avaliado quanto à viabilidade, aceito/rejeitado, registrado em blockchain e orquestrado/implantação NASP? |
| **Fonte real** | Portal-backend POST /api/v1/sla/submit → submit_template_to_nasp (SEM → ML → Decision → BC → NASP → SLA-Agent). |
| **Endpoint real** | POST /api/v1/sla/submit. |
| **Payload real** | Request: { template_id: string, form_values: { type/slice_type, latency, throughput, availability, ... }, tenant_id: string }. Response: decision, reason, sla_id, intent_id, nest_id, tx_hash, sem_csmf_status, ml_nsmf_status, bc_status, nasp_status, sla_agent_status, service_type, sla_requirements, timestamp, etc. |
| **Campos existentes** | Todos os campos da SLASubmitResponse. |
| **Campos deriváveis** | Nenhum. |
| **Campos indisponíveis** | Nenhum para este fluxo. |
| **Dependência agregador** | Nenhuma para submit. |
| **Status** | Parcial (backend pronto; frontend mock atual). |

**Implementação frontend (após aprovação):** Formulário com slice type (URLLC/eMBB/mMTC), latency, throughput, availability, priority; template_id coerente (ex. urllc-basic). Botão "Submeter SLA" chama POST /api/v1/sla/submit; exibir decisão, reason, sla_id, intent_id, nest_id, tx_hash e status por módulo (SEM, ML, BC, NASP, SLA-Agent). **Exibir obrigatoriamente** os campos da seção **EXPLICAÇÃO DA DECISÃO (XAI)** abaixo quando disponíveis na resposta. Alinhado a GST/NEST; não inventar decisão. Ver subseção "Validação do fluxo semântico formal TriSLA" abaixo.

---

## EXPLICAÇÃO DA DECISÃO (XAI) — Menus 2 e 3

**Regra absoluta:** O frontend **não inventa** explicação. O frontend apenas **mostra o XAI real** vindo do pipeline TriSLA. Se um campo não existir na resposta da API, marcar como **dependência backend futura** e não exibir valor fictício.

### Obrigatório exibir (quando disponível na resposta real)

| Campo | Menu | Fonte na resposta | Status atual |
|-------|------|-------------------|--------------|
| **Semantic interpretation** | 2, 3 | interpret: semantic_class, profile_sla, message. submit: semantic_class, profile_sla. | Disponível |
| **Ontology match** | 2, 3 | semantic_class, profile_sla (refletem validação ontológica). ontology_consistency não exposto em interpret. | Parcial; marcar "ontology_consistency" como dependência backend se desejar exibir |
| **Slice recomendado** | 2, 3 | service_type, slice_type, template_id | Disponível |
| **Confiança** | 3 | ml_prediction.confidence (submit). Interpret: não existe. | Submit: disponível. Interpret: dependência backend futura |
| **Justificativa da decisão** | 3 | reason, justification, ml_prediction.reasoning | Disponível |
| **Motivo de aceitação/rejeição** | 3 | reason, ml_prediction.metadata.system_xai_explanation (cause, explanation) | Disponível |
| **Status de orquestração** | 3 | sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status (e nasp quando disponível) | Disponível |
| **Score breakdown** | 3 | ml_prediction.ml_risk_score, ml_prediction.ml_risk_level | Disponível |
| **Feature importance (ML)** | 3 | ml_prediction.metadata.ml_features_importance (se backend expuser no /evaluate) | Pendência backend; exibir só se vier na resposta |

### Implementação no frontend

- **Menu 2 (PNL):** Exibir semantic_class, profile_sla, template_id (slice recomendado), message. Não exibir "confiança" nem "ontology_consistency" até o backend fornecer; se exibir rótulo, usar "N/A" ou "Aguardando backend" e documentar como dependência.
- **Menu 3 (Template):** Exibir reason/justification; ml_prediction.reasoning; ml_prediction.confidence; ml_prediction.ml_risk_score e ml_risk_level; ml_prediction.metadata.system_xai_explanation (explanation, cause, domains_evaluated); status por módulo (sem_csmf_status, ml_nsmf_status, bc_status, sla_agent_status). Feature importance apenas se presente em ml_prediction.metadata.

Referência completa: **docs/AUDITORIA_XAI_TRISLA_PORTAL.md**.

---

## MENU 4 — SLA Lifecycle

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Mostrar ciclo completo do SLA (tabela por SLA). |
| **Pergunta científica** | Quais SLAs passaram pelas etapas da arquitetura e em que estágio se encontram? |
| **Fonte real** | Backend SLA registry — hoje não exposto como listagem. |
| **Endpoint real** | GET /api/v1/sla **não existe**. |
| **Payload real** | Esperado: array de { id, slice_type, state, admission, blockchain, nasp, runtime }. |
| **Campos existentes** | Nenhum (endpoint de listagem ausente). |
| **Campos deriváveis** | Nenhum no frontend. |
| **Campos indisponíveis** | Toda a listagem. |
| **Dependência agregador** | Sim — novo agregador backend (SEM + ML + BC + NASP states) ou GET /api/v1/sla. Registrar como pendência; não alterar backend. |
| **Status** | Depende backend futuro. |

**Implementação frontend (após aprovação):** Manter tabela e colunas (SLA ID, Slice Type, Estado, Admission, Blockchain, NASP, Runtime); consumir GET /api/v1/sla quando existir; enquanto não existir, exibir mensagem "Aguardando endpoint de listagem de SLAs" ou tabela vazia sem dados fictícios.

---

## MENU 5 — Monitoring

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Observabilidade multi-domínio (Core, Transporte, RAN) com métricas reais. |
| **Pergunta científica** | O SLA está sendo observado em todos os domínios relevantes? |
| **Fonte real** | /api/v1/prometheus/summary (hoje: cpu, memory, up/targets). Core/Transporte/RAN conforme SSOT quando métricas existirem. |
| **Endpoint real** | GET /api/v1/prometheus/summary. |
| **Payload real** | { cpu, memory, observable_targets, availability, monitored_modules }. |
| **Campos existentes** | cpu, memory, observable_targets, monitored_modules. |
| **Campos deriváveis** | availability já vem no summary. |
| **Campos indisponíveis** | Métricas por domínio (Core: registration_total, pdu_session_total, pfcp_session_total; Transporte: RTT, probes; RAN: PRB, UE, RRC) — só incluir quando houver fonte real. |
| **Dependência agregador** | Métricas por domínio podem depender de novos endpoints ou queries. |
| **Status** | Parcial. |

**Implementação frontend (após aprovação):** Remover payload bruto da visão principal; usar cards com cpu, memory, observable_targets (corrigir uso de data.observable_targets em vez de data.up). Não exibir JSON bruto como tela principal; payload técnico apenas em Administration "Expandir detalhes".

---

## MENU 6 — Metrics

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Consumo dos módulos com leitura científica; métricas reais (CPU, memória, up, módulos). |
| **Pergunta científica** | Os módulos TriSLA estão disponíveis e com métricas mensuráveis? |
| **Fonte real** | /api/v1/prometheus/summary. |
| **Endpoint real** | GET /api/v1/prometheus/summary. |
| **Payload real** | { cpu, memory, observable_targets, availability, monitored_modules }. |
| **Campos existentes** | cpu, memory, availability, monitored_modules. |
| **Campos deriváveis** | Nenhum adicional. |
| **Campos indisponíveis** | Nenhum para este escopo. |
| **Dependência agregador** | Nenhuma. |
| **Status** | Pronto. |

**Implementação frontend (após aprovação):** Manter uso atual; eventual revisão de rótulos/legenda; sem percentuais decorativos sem base.

---

## MENU 7 — SLA-Aware Full Defense Panel

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Mostrar defesa SLA-aware ponta a ponta (Admission, Prediction, Semantic validation, Blockchain, Deployment, Observability). |
| **Pergunta científica** | Cada SLA passou por admission, predição, validação semântica, blockchain, implantação e observabilidade? |
| **Fonte real** | Agregador futuro; hoje /api/v1/modules retorna lista fixa de módulos. |
| **Endpoint real** | GET /api/v1/modules existe; não existe endpoint agregado por SLA. |
| **Payload real** | modules: [{ name, status }]. Agregado por SLA: pendente. |
| **Campos existentes** | name, status por módulo (lista genérica). |
| **Campos deriváveis** | Nenhum por SLA sem agregador. |
| **Campos indisponíveis** | Admission, Prediction, Semantic, Blockchain, Deployment, Observability por SLA. |
| **Dependência agregador** | Sim — painel agregador por SLA. Registrar como pendência. |
| **Status** | Depende backend futuro. |

**Implementação frontend (após aprovação):** Não usar dados hardcoded. Consumir GET /api/v1/modules para visão de módulos; quando existir agregador por SLA, consumir e exibir blocos do SSOT. Enquanto não existir, exibir mensagem de pendência ou visão apenas de "módulos online" sem linhas fictícias por SLA.

---

## MENU 8 — Administration

| Campo | Conteúdo |
|-------|----------|
| **Objetivo científico** | Visão executiva do sistema sem payload bruto como interface principal. |
| **Pergunta científica** | O estado executivo do sistema (backend, frontend, helm, targets) está acessível de forma auditável? |
| **Fonte real** | /api/v1/health; /api/v1/prometheus/summary; helm/runtime (fora do backend atual); frontend digest (build-time ou env). |
| **Endpoint real** | GET /api/v1/health; GET /api/v1/prometheus/summary; GET /api/v1/modules. |
| **Payload real** | health, summary, modules (conforme já auditado). |
| **Campos existentes** | status, version, observable_targets, backend digest (se disponível), last refresh. |
| **Campos deriváveis** | Nenhum inventado. |
| **Campos indisponíveis** | helm revision, frontend digest (dependem de injeção no build/deploy). |
| **Dependência agregador** | Nenhuma crítica. |
| **Status** | Parcial (menu e seção atualmente ausentes). |

**Implementação frontend (após aprovação):** Criar menu Administration e seção; cards/linhas: backend online, frontend digest (se disponível), backend digest (se disponível), helm revision (se disponível), targets observáveis, last refresh. **Expandir detalhes:** seção recolhida com payload técnico (ex.: JSON de health/summary) para uso acadêmico/auditoria. Não exibir payload bruto como visão principal.

---

## Validação do fluxo semântico formal TriSLA (Menus 2 e 3)

### Como o frontend deve usar a semântica real

- O frontend **não** executa interpretação semântica nem carrega a ontologia OWL.  
- O frontend envia **entrada** (PNL ou template) ao portal-backend e exibe **apenas** a resposta retornada pelos endpoints reais.  
- Para PNL: POST /api/v1/sla/interpret com intent_text e tenant_id; exibir todos os campos da resposta (intent_id, service_type, slice_type, semantic_class, profile_sla, template_id, sla_requirements, etc.) como "resultado da interpretação".  
- Para Template: POST /api/v1/sla/submit com template_id, form_values e tenant_id; exibir decision, reason e status de cada módulo (sem_csmf_status, ml_nsmf_status, bc_status, nasp_status, sla_agent_status) como "resultado do fluxo TriSLA".

### Como o frontend deve apresentar a ontologia de forma fiel

- O frontend **não** apresenta a ontologia em si (arquivo OWL/TTL não é exposto ao cliente).  
- A fidelidade à ontologia é demonstrada **exibindo os resultados** que o SEM-CSMF produz usando a ontologia: semantic_class, profile_sla, template_id, sla_requirements. Ou seja, "o que a ontologia permitiu inferir/validar" aparece nos campos da resposta de interpret, sem replicar regras no frontend.

### Como o formulário/template deve disparar ou representar o fluxo TriSLA real

- **Criar SLA PNL:** Botão "Interpretar" (ou equivalente) dispara POST /api/v1/sla/interpret. O fluxo real (SEM-CSMF: NLP + ontologia → GST/NEST) ocorre no backend; o frontend mostra "Entrada" → "Interpretação" (resposta) → "Template gerado" (resumo dos campos). Opcionalmente oferecer ação "Usar este template para submeter" que leve o usuário ao menu Template com campos pré-preenchidos quando isso for suportado.  
- **Criar SLA Template:** Botão "Submeter SLA" dispara POST /api/v1/sla/submit. O fluxo real (SEM → ML → Decision → BC → NASP → SLA-Agent) é executado no backend; o frontend mostra decisão e status por módulo. Nenhum cálculo de decisão nem estado no frontend.

### Até onde o ciclo ponta a ponta já chega hoje

- **Interpret (PNL):** SEM-CSMF: interpretação, validação ontológica, geração de intent/NEST. Não dispara ML/Decision/BC/NASP.  
- **Submit (Template):** Pipeline completo: SEM-CSMF → ML-NSMF → Decision Engine → (se ACCEPT) BC-NSSMF, NASP Adapter, SLA-Agent. Criação real do SLA até blockchain e orquestração NASP.

### O que ainda é limitação do ambiente

- Listagem de SLAs (GET /api/v1/sla) inexistente; Lifecycle e contagens na Home dependem de agregador.  
- Painel Defense agregado por SLA não existe; apenas lista de módulos em /api/v1/modules.  
- Frontend não deve preencher essas lacunas com mocks ou placeholders; registrar como pendências e exibir apenas o que há fonte real.

---

## Resumo de status por menu

| Menu | Status | Ação frontend (após aprovação) |
|------|--------|--------------------------------|
| Home | Parcial | Cards com health + summary; "-" para contagens SLA até agregador. |
| Criar SLA PNL | Parcial | Chamar interpret; exibir entrada → interpretação → template gerado. |
| Criar SLA Template | Parcial | Chamar submit; exibir decisão e status por módulo. |
| SLA Lifecycle | Depende backend | Manter UI; consumir GET /api/v1/sla quando existir; sem dados fictícios. |
| Monitoring | Parcial | Remover payload bruto; usar observable_targets. |
| Metrics | Pronto | Manter; revisão de rótulos se necessário. |
| SLA-Aware Full Defense Panel | Depende backend | Consumir /api/v1/modules; sem linhas hardcoded; pendência para agregador. |
| Administration | Parcial | Criar menu + seção; visão executiva + "Expandir detalhes". |

---

## Alterações em lib/api.ts (propostas para Fase C, após aprovação)

- Adicionar:  
  - `slaInterpret(body: { intent_text: string; tenant_id: string })` → POST /api/v1/sla/interpret  
  - `slaSubmit(body: { template_id: string; form_values: Record<string, unknown>; tenant_id: string })` → POST /api/v1/sla/submit  
- Manter: prometheusSummary, backendHealth, slaList, defenseSummary (slaList até GET /api/v1/sla existir).

---

*Fim do Plano Técnico Revisado. Implementação somente após aprovação explícita (Fase C).*
