# Manual do Usuário - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Introdução](#introdução)
2. [Acesso ao Portal](#acesso-ao-portal)
   - [Cenário 1: Portal Local](#cenário-1-portal-local)
   - [Cenário 2: Portal NASP](#cenário-2-portal-nasp)
3. [Navegação no Portal](#navegação-no-portal)
4. [Funcionalidades Principais](#funcionalidades-principais)
5. [Guia de Uso por Tela](#guia-de-uso-por-tela)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Introdução

O **TriSLA Observability Portal v4.0** é uma interface web completa para visualização de observabilidade e gerenciamento de contratos SLA do ecossistema TriSLA.

Este manual fornece instruções passo a passo para:
- Acessar o portal (local ou NASP)
- Navegar pelas telas
- Utilizar as funcionalidades principais
- Resolver problemas comuns

---

## 🌐 Acesso ao Portal

### Cenário 1: Portal Local

#### Pré-requisitos

- Docker e Docker Compose instalados
- Portal iniciado via `docker-compose up`

#### Passo a Passo

1. **Verificar se o portal está rodando**

   ```bash
   # No terminal, verificar containers
   docker-compose ps
   
   # Deve mostrar:
   # - frontend (porta 3000)
   # - backend (porta 8000)
   # - redis
   # - prometheus (opcional)
   # - loki (opcional)
   # - tempo (opcional)
   ```

2. **Abrir o navegador**

   - Abra seu navegador preferido (Chrome, Firefox, Edge, etc.)
   - Acesse: **http://localhost:3000**

3. **Verificar conectividade**

   - A página inicial deve carregar
   - Se não carregar, verifique os logs:
     ```bash
     docker-compose logs frontend
     ```

4. **Acessar documentação da API (opcional)**

   - Acesse: **http://localhost:8000/docs**
   - Interface Swagger para testar endpoints

---

### Cenário 2: Portal NASP

#### Pré-requisitos

- Acesso ao cluster Kubernetes NASP
- Portal deployado via Helm Charts
- Ingress configurado

#### Passo a Passo

1. **Verificar status do deploy**

   ```bash
   # Verificar pods
   kubectl get pods -n trisla -l app.kubernetes.io/name=trisla-portal
   
   # Deve mostrar pods em status Running:
   # - trisla-portal-frontend-xxx
   # - trisla-portal-backend-xxx
   ```

2. **Obter URL do Ingress**

   ```bash
   # Verificar ingress
   kubectl get ingress -n trisla
   
   # Exemplo de saída:
   # NAME                    HOSTS                    ADDRESS
   # trisla-portal-ingress   portal.trisla.local     192.168.1.100
   ```

3. **Acessar via navegador**

   - **Opção 1: Via Ingress (recomendado)**
     - Acesse: **http://portal.trisla.local** (ou URL configurada no Ingress)
     - Se necessário, adicione ao `/etc/hosts`:
       ```bash
       # Linux/Mac
       echo "192.168.1.100 portal.trisla.local" | sudo tee -a /etc/hosts
       
       # Windows (como administrador)
       # Editar C:\Windows\System32\drivers\etc\hosts
       # Adicionar: 192.168.1.100 portal.trisla.local
       ```

   - **Opção 2: Via Port Forward (desenvolvimento)**
     ```bash
     # Port forward do frontend
     kubectl port-forward -n trisla svc/trisla-portal-frontend 3000:80
     
     # Em outro terminal, port forward do backend
     kubectl port-forward -n trisla svc/trisla-portal-backend 8000:8000
     
     # Acessar: http://localhost:3000
     ```

4. **Verificar conectividade**

   - A página inicial deve carregar
   - Se não carregar, verifique os logs:
     ```bash
     kubectl logs -n trisla -l component=frontend --tail=50
     kubectl logs -n trisla -l component=backend --tail=50
     ```

---

## 🧭 Navegação no Portal

### Estrutura da Interface

O portal possui uma estrutura consistente em todas as telas:

```
┌─────────────────────────────────────────────────────────────┐
│  [TriSLA Portal]                    [User] [Settings] [🔔] │
├─────────────────────────────────────────────────────────────┤
│  [Sidebar]  │  [Conteúdo Principal]                        │
│             │                                               │
│  • Overview │  ┌──────────────────────────────────────┐   │
│  • Modules  │  │  Conteúdo da página                  │   │
│  • Contracts│  │                                       │   │
│  • SLAs     │  │                                       │   │
│  • XAI      │  └──────────────────────────────────────┘   │
│  • Logs     │                                               │
│  • Traces   │                                               │
│  • Metrics  │                                               │
└─────────────────────────────────────────────────────────────┘
```

### Menu Lateral (Sidebar)

O menu lateral está sempre visível e contém:

- **Overview** - Visão geral do sistema
- **Modules** - Lista de módulos TriSLA
- **Contracts** - Gerenciamento de contratos SLA
- **SLAs** - Criação de SLAs
- **XAI** - Visualizador de explicações
- **Logs** - Visualização de logs (Loki)
- **Traces** - Visualização de traces (Tempo)
- **Metrics** - Visualização de métricas (Prometheus)

### Navegação

- **Clique no item do menu** para navegar
- **Item ativo** fica destacado
- **Breadcrumbs** (se disponível) mostram localização atual

---

## 🎯 Funcionalidades Principais

### 1. Overview (Visão Geral)

**Localização:** Página inicial (`/`)

**Funcionalidades:**
- Status global do sistema
- Status de cada módulo TriSLA
- SLOs principais
- Métricas resumidas

**Como usar:**
1. Acesse a página inicial
2. Visualize o status global (✅ Sistema Operacional)
3. Verifique status de cada módulo (✅ UP, ⚠️ WARNING, ❌ DOWN)
4. Analise SLOs principais (Latência P95, Disponibilidade)

---

### 2. Modules (Módulos)

**Localização:** `/modules`

**Funcionalidades:**
- Lista de todos os módulos TriSLA
- Status, latência e taxa de erro de cada módulo
- Detalhes de pods (se aplicável)

**Como usar:**
1. Clique em **"Modules"** no menu lateral
2. Visualize a lista de módulos:
   - SEM-CSMF
   - ML-NSMF
   - Decision Engine
   - BC-NSSMF
   - SLA-Agent Layer
   - NASP Adapter
3. Clique em **"Ver Detalhes"** para ver informações detalhadas de um módulo
4. Na página de detalhes, visualize:
   - Status e métricas
   - Lista de pods (se aplicável)
   - Métricas históricas

---

### 3. Contracts (Contratos)

**Localização:** `/contracts`

**Funcionalidades:**
- Lista de contratos SLA
- Filtros (status, tenant, tipo)
- Detalhes de contratos
- Violações e renegociações

**Como usar:**

**3.1. Listar Contratos**
1. Clique em **"Contracts"** no menu lateral
2. Visualize a lista de contratos
3. Use filtros para:
   - Filtrar por status (ACTIVE, VIOLATED, etc.)
   - Filtrar por tenant
   - Filtrar por tipo (URLLC, eMBB, mMTC)
   - Buscar por ID

**3.2. Ver Detalhes de um Contrato**
1. Na lista de contratos, clique em **"👁️ Ver"** ou no ID do contrato
2. Visualize:
   - Informações do contrato (tenant, status, versão)
   - Requisitos SLA (latência, throughput, confiabilidade)
   - Violações (se houver)
   - Renegociações (se houver)
   - Penalidades (se aplicável)

**3.3. Criar Novo Contrato**
1. Na lista de contratos, clique em **"Criar Contrato"** (se disponível)
2. Preencha os campos:
   - Tenant ID
   - Intent ID (ou crie via PLN)
   - NEST ID
   - SLA Requirements
3. Clique em **"Criar"**

---

### 4. SLAs (Criação de SLAs)

**Localização:** `/slas/create/pln` e `/slas/create/template`

**Funcionalidades:**
- Criação de SLA via PLN (Processamento de Linguagem Natural)
- Criação de SLA via Template
- Criação em batch (massa)

**Como usar:**

**4.1. Criar SLA via PLN**
1. Clique em **"SLAs"** no menu lateral
2. Selecione **"Criar via PLN"**
3. Preencha:
   - **Tenant ID**: ID do tenant
   - **Intent**: Descreva o SLA em linguagem natural
     - Exemplo: "Preciso de um slice URLLC com latência máxima de 10ms"
4. Clique em **"Criar SLA"**
5. Visualize o preview do NEST gerado
6. Confirme a criação

**4.2. Criar SLA via Template**
1. Clique em **"SLAs"** no menu lateral
2. Selecione **"Criar via Template"**
3. Selecione um template (ex: "URLLC Basic")
4. Preencha os campos do formulário:
   - Latência máxima
   - Confiabilidade
   - Outros requisitos
5. Clique em **"Criar SLA"**

**4.3. Criar SLAs em Batch**
1. Clique em **"SLAs"** no menu lateral
2. Selecione **"Criar em Batch"**
3. Prepare um arquivo CSV ou JSON:
   ```csv
   tenant_id,intent_text,service_type
   tenant-001,Slice URLLC com latência 10ms,URLLC
   tenant-002,Slice eMBB para streaming,eMBB
   ```
4. Faça upload do arquivo
5. Visualize o progresso em tempo real
6. Baixe o relatório de resultados

---

### 5. XAI (Explainable AI)

**Localização:** `/xai`

**Funcionalidades:**
- Visualização de explicações de predições ML
- Visualização de explicações de decisões
- Gráficos de feature importance

**Como usar:**
1. Clique em **"XAI"** no menu lateral
2. Visualize a lista de explicações disponíveis
3. Clique em uma explicação para ver detalhes:
   - Método utilizado (SHAP, LIME, fallback)
   - Score de viabilidade
   - Recomendação (ACCEPT, REJECT)
   - Feature importance (gráfico)
   - Reasoning textual
4. Analise o gráfico de feature importance
5. Leia o reasoning para entender a decisão

---

### 6. Logs (Visualização de Logs)

**Localização:** `/logs`

**Funcionalidades:**
- Visualização de logs do Loki
- Filtros por módulo, nível, período

**Como usar:**
1. Clique em **"Logs"** no menu lateral
2. Use filtros:
   - **Módulo**: Selecione um módulo específico
   - **Nível**: INFO, ERROR, WARNING, etc.
   - **Período**: Selecione data/hora inicial e final
3. Visualize os logs filtrados
4. Clique em um log para ver detalhes

---

### 7. Traces (Visualização de Traces)

**Localização:** `/traces`

**Funcionalidades:**
- Visualização de traces do Tempo
- Filtros por serviço, operação, status

**Como usar:**
1. Clique em **"Traces"** no menu lateral
2. Use filtros:
   - **Serviço**: Selecione um serviço
   - **Operação**: Filtre por operação
   - **Status**: SUCCESS, ERROR, etc.
3. Visualize a lista de traces
4. Clique em um trace para ver:
   - Spans detalhados
   - Duração
   - Hierarquia de spans

---

### 8. Metrics (Visualização de Métricas)

**Localização:** `/metrics`

**Funcionalidades:**
- Visualização de métricas do Prometheus
- Gráficos e dashboards

**Como usar:**
1. Clique em **"Metrics"** no menu lateral
2. Selecione uma métrica ou query PromQL
3. Visualize o gráfico
4. Ajuste o período de tempo
5. Exporte dados (se disponível)

---

## 🔧 Troubleshooting

### Problema: Portal não carrega (Local)

**Sintomas:**
- Página em branco
- Erro de conexão
- Timeout

**Soluções:**

1. **Verificar se containers estão rodando**
   ```bash
   docker-compose ps
   # Se não estiverem, iniciar:
   docker-compose up -d
   ```

2. **Verificar logs do frontend**
   ```bash
   docker-compose logs frontend
   ```

3. **Verificar logs do backend**
   ```bash
   docker-compose logs backend
   ```

4. **Verificar porta 3000**
   ```bash
   # Linux/Mac
   lsof -i :3000
   
   # Windows
   netstat -ano | findstr :3000
   ```

5. **Reiniciar containers**
   ```bash
   docker-compose restart
   ```

---

### Problema: Portal não carrega (NASP)

**Sintomas:**
- Página em branco
- Erro 502/503
- Timeout

**Soluções:**

1. **Verificar status dos pods**
   ```bash
   kubectl get pods -n trisla -l app.kubernetes.io/name=trisla-portal
   # Verificar se estão em status Running
   ```

2. **Verificar logs**
   ```bash
   kubectl logs -n trisla -l component=frontend --tail=50
   kubectl logs -n trisla -l component=backend --tail=50
   ```

3. **Verificar ingress**
   ```bash
   kubectl get ingress -n trisla
   kubectl describe ingress -n trisla
   ```

4. **Verificar services**
   ```bash
   kubectl get svc -n trisla
   kubectl describe svc -n trisla trisla-portal-frontend
   ```

5. **Verificar conectividade interna**
   ```bash
   kubectl exec -n trisla <frontend-pod> -- wget -O- http://trisla-portal-backend:8000/health
   ```

---

### Problema: Erro ao criar SLA via PLN

**Sintomas:**
- Erro 500 ao criar SLA
- Mensagem de erro genérica

**Soluções:**

1. **Verificar se SEM-CSMF está disponível**
   ```bash
   # Local
   curl http://localhost:<sem-csmf-port>/health
   
   # NASP
   kubectl get svc -n trisla | grep sem-csmf
   ```

2. **Verificar logs do backend**
   ```bash
   # Local
   docker-compose logs backend | grep -i "sla\|pln"
   
   # NASP
   kubectl logs -n trisla -l component=backend | grep -i "sla\|pln"
   ```

3. **Verificar formato do intent**
   - Certifique-se de que o intent está em português
   - Inclua informações claras (tipo de slice, requisitos)

---

### Problema: XAI não mostra explicações

**Sintomas:**
- Lista vazia de explicações
- Erro ao gerar explicação

**Soluções:**

1. **Verificar se ML-NSMF está disponível**
   ```bash
   # Local
   curl http://localhost:<ml-nsmf-port>/health
   
   # NASP
   kubectl get svc -n trisla | grep ml-nsmf
   ```

2. **Verificar se há predições disponíveis**
   - Certifique-se de que há predições ML no sistema
   - Verifique se o prediction_id é válido

3. **Verificar logs do backend**
   ```bash
   kubectl logs -n trisla -l component=backend | grep -i "xai"
   ```

---

### Problema: Métricas não aparecem

**Sintomas:**
- Gráficos vazios
- Erro ao buscar métricas

**Soluções:**

1. **Verificar se Prometheus está disponível**
   ```bash
   # Local
   curl http://localhost:9090/-/healthy
   
   # NASP
   kubectl get svc -n monitoring | grep prometheus
   ```

2. **Verificar ServiceMonitor**
   ```bash
   kubectl get servicemonitor -n trisla
   ```

3. **Verificar targets no Prometheus**
   - Acesse: http://localhost:9090/targets (local)
   - Verifique se os targets estão UP

---

## 📞 Suporte

Para mais informações, consulte:

- **Documentação técnica**: `trisla-portal/docs/`
- **Guia de deploy**: `trisla-portal/docs/DEPLOY_GUIDE.md`
- **Arquitetura**: `trisla-portal/docs/ARCHITECTURE_v4.0.md`

---

## ✅ Conclusão

Este manual fornece instruções completas para:

- ✅ Acessar o portal (local e NASP)
- ✅ Navegar pelas telas
- ✅ Utilizar todas as funcionalidades
- ✅ Resolver problemas comuns

**Status:** ✅ **MANUAL DO USUÁRIO COMPLETO**







