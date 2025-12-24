# Portal — TriSLA Observability Portal

**Versão:** 4.0  
**Fase:** P (Portal)  
**Status:** Estabilizado

---

## 1. Visão Geral do Módulo

### Objetivo no TriSLA (Papel Arquitetural)

O **Portal** é a interface web de observabilidade e gerenciamento do TriSLA. Fornece dashboards, visualizações de métricas, explicações XAI, gerenciamento de SLAs e integração com todos os módulos do sistema.

**Papel no fluxo TriSLA:**
- **Entrada**: Métricas, eventos e dados de todos os módulos
- **Processamento**: Agregação, visualização e apresentação de dados
- **Saída**: Dashboards, gráficos, explicações XAI e relatórios

### Entradas e Saídas (Alto Nível)

**Entradas:**
- Métricas do NASP (Prometheus, OpenTelemetry)
- Eventos on-chain (blockchain)
- Predições e explicações XAI (ML-NSMF)
- Dados de SLAs (BC-NSSMF)

**Saídas:**
- Dashboards de observabilidade
- Visualizações de métricas
- Explicações XAI interativas
- Relatórios e análises

---

## 2. Componentes Internos

### 2.1 Frontend (React)
Interface web responsiva com dashboards, gráficos e visualizações interativas.

### 2.2 Backend API (FastAPI)
API REST que agrega dados de todos os módulos e fornece endpoints para o frontend.

### 2.3 Integração NASP
Integração com NASP Adapter para coleta de métricas e observabilidade.

### 2.4 Integração Blockchain
Consulta de eventos on-chain e visualização de SLAs registrados.

### 2.5 XAI Visualization
Visualização interativa de explicações XAI (SHAP/LIME) do ML-NSMF.

---

## 3. Fluxo Operacional

### Passo a Passo

1. **Coleta de Dados**
   - Consulta métricas do NASP Adapter
   - Consulta eventos on-chain
   - Consulta predições do ML-NSMF

2. **Agregação**
   - Agrega métricas por domínio (RAN, Transport, Core)
   - Agrega eventos por SLA
   - Agrega predições por slice

3. **Processamento**
   - Calcula estatísticas (média, p95, p99)
   - Detecta anomalias
   - Gera explicações XAI

4. **Visualização**
   - Renderiza dashboards
   - Renderiza gráficos
   - Renderiza explicações XAI

5. **Atualização**
   - Atualiza dados em tempo real (WebSocket)
   - Atualiza dashboards periodicamente
   - Atualiza alertas

---

## 4. Interfaces

### 4.1 API REST

**Protocolo:** HTTP REST  
**Direção:** Frontend → Backend  
**Base URL:** `http://portal:8080/api/v1`

**Endpoints Principais:**
- `GET /metrics`: Consulta métricas agregadas
- `GET /slas`: Consulta SLAs registrados
- `GET /predictions`: Consulta predições de viabilidade
- `GET /xai/{prediction_id}`: Consulta explicação XAI
- `GET /events/{sla_id}`: Consulta eventos de um SLA

### 4.2 WebSocket

**Protocolo:** WebSocket  
**Direção:** Backend → Frontend  
**Endpoint:** `ws://portal:8080/ws`

**Descrição Conceitual:**
Conexão WebSocket para atualização em tempo real de métricas, eventos e alertas.

### 4.3 Integração NASP

**Protocolo:** HTTP REST  
**Direção:** Portal → NASP Adapter  
**Endpoint:** `http://nasp-adapter:8080/api/v1/metrics`

**Descrição Conceitual:**
Consulta métricas do NASP Adapter para visualização em dashboards.

---

## 5. Dados e Modelos

### 5.1 Métricas

**Fonte:** NASP Adapter (Prometheus, OpenTelemetry)

**Tipos:**
- Métricas de infraestrutura (CPU, memória, bandwidth)
- Métricas de rede (latência, throughput, jitter)
- Métricas de SLA (violações, conformidade)

### 5.2 SLAs

**Fonte:** BC-NSSMF (blockchain)

**Dados:**
- Status do SLA (REQUESTED, APPROVED, ACTIVE, VIOLATED, TERMINATED)
- SLOs (Service Level Objectives)
- Eventos on-chain

### 5.3 Predições

**Fonte:** ML-NSMF

**Dados:**
- Score de viabilidade (0.0-1.0)
- Confiança da predição
- Explicação XAI (SHAP/LIME)

---

## 6. Observabilidade e Métricas

### 6.1 Métricas Expostas

O módulo expõe métricas via endpoint `/metrics` (Prometheus):

- `trisla_portal_requests_total`: Total de requisições
- `trisla_portal_response_duration_seconds`: Duração de resposta
- `trisla_portal_websocket_connections`: Conexões WebSocket ativas

### 6.2 Traces OpenTelemetry

Traces distribuídos são gerados para rastreabilidade:
- Span: `portal.api_request`
- Span: `portal.metrics_aggregation`
- Span: `portal.xai_visualization`

---

## 7. Limitações Conhecidas

### 7.1 Performance

- **Limitação**: Agregação de grandes volumes de métricas pode ser lenta
- **Impacto**: Dashboards podem demorar para carregar
- **Mitigação**: Cache de métricas, paginação, limites de tempo

### 7.2 Escalabilidade

- **Limitação**: WebSocket pode ter limitações de conexões simultâneas
- **Impacto**: Muitos usuários simultâneos podem causar problemas
- **Mitigação**: Load balancing, múltiplas instâncias

### 7.3 Dados em Tempo Real

- **Limitação**: Dados podem ter latência de alguns segundos
- **Impacto**: Visualizações podem não refletir estado atual
- **Mitigação**: Atualização frequente, WebSocket para eventos críticos

---

## 8. Como Ler a Documentação deste Módulo

### 8.1 Ordem Recomendada de Leitura

1. **Este README.md** — Visão geral e guia de leitura
2. **[architecture.md](architecture.md)** — Arquitetura completa do portal
3. **[flows.md](flows.md)** — Fluxos funcionais (XAI, PLN, Batch, Contratos)
4. **[implementation.md](implementation.md)** — Detalhes de implementação

### 8.2 Documentação Adicional

- **[trisla-portal/docs/](../../trisla-portal/docs/)** — Documentação completa do portal
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** — Arquitetura geral do TriSLA

### 8.3 Links para Outros Módulos

- **[SEM-NSMF](../sem-csmf/README.md)** — Módulo de interpretação semântica
- **[ML-NSMF](../ml-nsmf/README.md)** — Módulo de predição ML
- **[BC-NSSMF](../bc-nssmf/README.md)** — Módulo de blockchain

---

**Última atualização:** 2025-01-27  
**Versão:** S4.0

