# 📊 Proposta: Dashboard TriSLA Local com Túnel SSH

## 🎯 Visão Geral

Desenvolver um dashboard web moderno e responsivo na **máquina local (Windows)**, conectado ao **node1** via **túnel SSH**, para visualizar métricas do Prometheus e gerenciar slices do TriSLA.

---

## 🏗️ Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────┐
│  Máquina Local (Windows)                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Dashboard Web (React/Next.js)                  │    │
│  │  - Interface moderna e responsiva               │    │
│  │  - Gráficos com Recharts/Chart.js               │    │
│  │  - Gestão de slices                             │    │
│  └─────────────────────────────────────────────────┘    │
│                          ↕ HTTP                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  API Gateway Local (FastAPI/Express)            │    │
│  │  - Proxy para Prometheus                        │    │
│  │  - Cache de métricas                            │    │
│  │  - Autenticação (opcional)                      │    │
│  └─────────────────────────────────────────────────┘    │
│                          ↕ SSH Tunnel                   │
└─────────────────────────────────────────────────────────┘
              ↕ SSH Túnel (localhost:9090 → node1:9090)
┌─────────────────────────────────────────────────────────┐
│  Node1 (via SSH)                                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Prometheus                                      │    │
│  │  - Porta 9090 (acessível via túnel)             │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  TriSLA API (Kubernetes)                        │    │
│  │  - Porta 8000 (via kubectl port-forward)        │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológico Proposta

### Frontend: React + TypeScript + Vite

**Escolhido:**
- **React 18+** com **TypeScript**
- **Vite** como build tool
- **TailwindCSS** para styling
- **Recharts** ou **Chart.js** para gráficos
- **React Router** para navegação
- **Axios** ou **Fetch API** para requisições

**Por que:**
- ✅ **React**: Ecossistema maduro, componentes reutilizáveis, amplamente usado
- ✅ **TypeScript**: Type safety, melhor DX (Developer Experience), menos bugs
- ✅ **Vite**: Build extremamente rápido (vs Webpack), hot reload instantâneo
- ✅ **TailwindCSS**: Estilização rápida, responsiva, sem CSS customizado complexo
- ✅ **Recharts**: Gráficos React nativos, fácil integração, animações suaves
- ✅ **Alternativas consideradas:**
  - Vue.js: Também é boa, mas React tem mais bibliotecas para dashboards
  - Next.js: Overhead desnecessário para app local
  - Svelte: Menos maduro, menos bibliotecas

### Backend/Proxy: FastAPI (Python) ou Express (Node.js)

**Opção A: FastAPI (Recomendado)**
```python
# Proxy para Prometheus via SSH túnel
# Cache de métricas
# Transformação de dados
```

**Por que FastAPI:**
- ✅ Async/await nativo (ideal para múltiplas queries)
- ✅ Type hints (Python)
- ✅ Documentação automática (Swagger)
- ✅ Performance excelente
- ✅ Fácil integração com túnel SSH

**Opção B: Express.js**
- ✅ JavaScript/TypeScript (mesma linguagem do frontend)
- ✅ Ecossistema NPM rico
- ✅ Mais simples para iniciar

**Recomendação: FastAPI** - melhor para proxies async e performance

### Túnel SSH: ssh (built-in) ou autossh

**Escolhido:**
- **ssh** (built-in Windows/Linux)
- **autossh** (opcional, auto-reconecta)

**Por que:**
- ✅ Já disponível no sistema
- ✅ Seguro (cifrado)
- ✅ Simples de configurar
- ✅ Estável
- ✅ Alternativas consideradas:
  - Ngrok: Requer conta, limites gratuitos
  - Cloudflare Tunnel: Mais complexo, overkill
  - Port forwarding manual: Menos automático

### Visualização de Dados

**Opção A: Recharts (Recomendado)**
- ✅ Componentes React nativos
- ✅ Fácil customização
- ✅ Animações suaves
- ✅ Tipos TypeScript completos

**Opção B: Chart.js + react-chartjs-2**
- ✅ Muito popular
- ✅ Muitos tipos de gráficos
- ✅ Boa documentação

**Opção C: Apache ECharts + react-echarts**
- ✅ Gráficos profissionais
- ✅ Muitas opções de customização
- ⚠️ Bundle maior

**Recomendação: Recharts** - melhor para dashboards React

### Estado/Gerenciamento

**Opção A: React Query (TanStack Query)**
- ✅ Cache automático de requisições
- ✅ Refetch automático
- ✅ Loading/error states
- ✅ Ideal para dados de API

**Opção B: Zustand / Redux**
- ✅ Estado global se necessário
- ⚠️ Overhead para dados de API simples

**Recomendação: React Query** - perfeito para dashboards com dados de API

---

## 📦 Estrutura de Diretórios Proposta

```
trisla-dashboard-local/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── Charts/
│   │   │   ├── SlicesManagement/
│   │   │   └── Metrics/
│   │   ├── hooks/
│   │   │   └── usePrometheus.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   └── prometheus.py
│   │   ├── services/
│   │   │   └── prometheus_service.py
│   │   └── main.py
│   └── requirements.txt
├── scripts/
│   ├── start-ssh-tunnel.sh
│   ├── start-ssh-tunnel.ps1 (Windows)
│   └── start-all.sh
└── README.md
```

---

## 🔄 Fluxo de Funcionamento

### 1. Inicialização

```bash
# 1. Conectar túnel SSH
ssh -L 9090:localhost:9090 porvir5g@ppgca.unisinos.br -N &
# ou
ssh -L 9090:nasp-prometheus.monitoring.svc.cluster.local:9090 \
    -J porvir5g@ppgca.unisinos.br porvir5g@node006 -N &

# 2. Iniciar backend (proxy)
cd backend && uvicorn main:app --reload --port 5000

# 3. Iniciar frontend
cd frontend && npm run dev
```

### 2. Requisição de Dados

```
Frontend → http://localhost:5173
    ↓
Backend Proxy → http://localhost:5000/api/prometheus/...
    ↓
SSH Tunnel → localhost:9090
    ↓
Node1 → Prometheus:9090
```

### 3. Visualização

- Dashboard carrega métricas via backend proxy
- Gráficos atualizados automaticamente (polling ou WebSocket)
- Gestão de slices via API do TriSLA

---

## ✅ Vantagens desta Abordagem

1. **Desenvolvimento Local**
   - ✅ Hot reload instantâneo
   - ✅ Debug fácil (dev tools do navegador)
   - ✅ Não precisa fazer deploy para testar

2. **Não Precisa Modificar Node1**
   - ✅ Não precisa copiar arquivos para node1
   - ✅ Não precisa rebuild imagens
   - ✅ Não depende de httpx ou outras dependências no node1

3. **Flexibilidade**
   - ✅ Pode usar qualquer biblioteca JavaScript/Python
   - ✅ Fácil de adicionar novos gráficos/métricas
   - ✅ Pode adicionar autenticação local se necessário

4. **Performance**
   - ✅ Frontend roda localmente (rápido)
   - ✅ Backend cache pode reduzir carga no Prometheus
   - ✅ Túnel SSH é eficiente

5. **Manutenção**
   - ✅ Código versionado localmente (git)
   - ✅ Fácil de atualizar
   - ✅ Pode compartilhar com outros desenvolvedores

---

## ⚠️ Considerações

### Desvantagens

1. **Requer túnel SSH ativo**
   - Solução: Script automatizado ou serviço Windows

2. **Não disponível remotamente** (sem configuração adicional)
   - Solução: Pode expor via ngrok ou reverse proxy se necessário

3. **Duas aplicações para gerenciar** (frontend + backend)
   - Solução: Scripts de inicialização automática

### Requisitos

- ✅ SSH configurado (já tem)
- ✅ Node.js 18+ (para frontend)
- ✅ Python 3.11+ (para backend, se usar FastAPI)
- ✅ Navegador moderno

---

## 🚀 Próximos Passos (Se Aprovar)

1. Criar estrutura do projeto
2. Configurar túnel SSH automático
3. Implementar backend proxy
4. Criar componentes do dashboard
5. Integrar gráficos e métricas
6. Adicionar gestão de slices

---

## 📊 Comparação: Local vs Node1

| Aspecto | Dashboard Local | Dashboard no Node1 |
|---------|----------------|-------------------|
| **Desenvolvimento** | ✅ Fácil (hot reload) | ❌ Difícil (deploy cada teste) |
| **Dependências** | ✅ Controle total | ❌ Limitado ao que está no pod |
| **Performance** | ✅ Rápido (local) | ⚠️ Depende do node1 |
| **Manutenção** | ✅ Git local | ❌ Precisa copiar arquivos |
| **Acesso** | ⚠️ Apenas local | ✅ Acessível de qualquer lugar |
| **Setup** | ⚠️ Requer túnel SSH | ✅ Já está no cluster |

**Recomendação: Dashboard Local** - Melhor para desenvolvimento e manutenção.

---

## 🎨 Preview das Funcionalidades

1. **Dashboard Principal**
   - Visão geral de métricas TriSLA
   - Gráficos em tempo real
   - Status dos componentes

2. **Gestão de Slices**
   - Listar slices ativos
   - Criar slices (NLP/Templates)
   - Monitorar métricas por slice

3. **Métricas Detalhadas**
   - CPU, Memória, Latência
   - Throughput, Bandwidth
   - Métricas de SLA

4. **Admin Panel**
   - Configurações
   - Logs
   - Troubleshooting

---

## 🤔 Sua Decisão

Esta abordagem é **muito melhor** para desenvolvimento! Você prefere:

1. **Opção A**: Dashboard local completo (recomendado) ✅
2. **Opção B**: Híbrido (frontend local + backend no node1)
3. **Opção C**: Tudo no node1 (atual)

Qual você prefere? Se aprovar a Opção A, começo a implementar agora!




