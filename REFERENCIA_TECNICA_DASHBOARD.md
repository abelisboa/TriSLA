# 📊 Referência Técnica para Geração de Dashboard TriSLA

## 📋 Índice
1. [Visão Geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Stack Tecnológica](#3-stack-tecnológica)
4. [Componentes do Sistema](#4-componentes-do-sistema)
5. [Estrutura de Arquivos](#5-estrutura-de-arquivos)
6. [API Backend](#6-api-backend)
7. [Frontend](#7-frontend)
8. [Integração com Prometheus](#8-integração-com-prometheus)
9. [Deployment](#9-deployment)
10. [Mecanismo de Controle de Prompts](#10-mecanismo-de-controle-de-prompts)

## 1. Visão Geral

O Dashboard TriSLA é uma aplicação web para monitoramento de métricas do sistema TriSLA, oferecendo visualização em tempo real de slices, componentes, uso de recursos e outros indicadores importantes. A aplicação consiste em:

- **Backend**: API FastAPI que atua como proxy para o Prometheus
- **Frontend**: Interface React com visualizações interativas
- **Integração**: Conexão com Prometheus via túnel SSH

O dashboard deve ser responsivo, moderno e funcionar mesmo quando o Prometheus não estiver acessível.

## 2. Arquitetura

```
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐     ┌────────────────┐
│                 │     │              │     │               │     │                │
│  React Frontend │────▶│ FastAPI Proxy│────▶│  SSH Tunnel   │────▶│   Prometheus   │
│  (Port 5173)    │     │  (Port 5000) │     │ (Port 9090)   │     │                │
│                 │     │              │     │               │     │                │
└─────────────────┘     └──────────────┘     └───────────────┘     └────────────────┘
```

- **Frontend**: Hospedado localmente na porta 5173
- **Backend**: API FastAPI na porta 5000
- **Prometheus**: Acessado via túnel SSH na porta 9090

## 3. Stack Tecnológica

### Backend
- **FastAPI**: Framework web assíncrono para Python
- **HTTPX**: Cliente HTTP assíncrono
- **Uvicorn**: Servidor ASGI para FastAPI
- **Python 3.8+**: Linguagem de programação

### Frontend
- **React 18**: Biblioteca JavaScript para UI
- **TypeScript**: Superset tipado de JavaScript
- **Vite**: Ferramenta de build rápida
- **TailwindCSS**: Framework CSS utilitário
- **React Query**: Gerenciamento de estado e cache para dados da API
- **Recharts**: Biblioteca de gráficos baseada em React
- **Lucide React**: Ícones modernos

### Ferramentas
- **SSH**: Para túnel seguro ao Prometheus
- **WSL**: Para desenvolvimento em ambiente Linux no Windows

## 4. Componentes do Sistema

### Backend
1. **API Proxy**: Intermediário entre frontend e Prometheus
2. **Endpoints Prometheus**: Rotas para consultar métricas
3. **Tratamento de Erros**: Funciona mesmo sem Prometheus
4. **CORS**: Configurado para desenvolvimento local

### Frontend
1. **Dashboard Principal**: Visão geral do sistema
2. **Gestão de Slices**: Visualização de slices ativos
3. **Métricas Detalhadas**: Gráficos e indicadores
4. **Componentes Reutilizáveis**: Cards, gráficos, etc.

## 5. Estrutura de Arquivos

```
trisla-dashboard-local/
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   └── venv/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── components/
│       │   ├── Layout.tsx
│       │   └── MetricCard.tsx
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── SlicesManagement.tsx
│       │   └── Metrics.tsx
│       ├── services/
│       │   └── api.ts
│       └── utils/
│           └── dataHelpers.ts
├── scripts/
│   ├── start-backend-and-open.ps1
│   └── start-all.ps1
└── scripts-wsl/
    ├── dashboard-menu.sh
    ├── start-backend.sh
    ├── start-frontend.sh
    └── start-ssh-tunnel.sh
```

## 6. API Backend

### Configuração Principal

```python
app = FastAPI(
    title="TriSLA Dashboard API",
    description="Proxy API para Prometheus e TriSLA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL do Prometheus
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# Cliente HTTP
client = httpx.AsyncClient(timeout=30.0)
```

### Endpoints Principais

```python
@app.get("/")
async def root():
    return {"message": "TriSLA Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check"""
    # Verifica conexão com Prometheus
    # Retorna status mesmo se Prometheus estiver indisponível

@app.get("/api/prometheus/metrics/slices")
async def get_slices_metrics():
    """Métricas de slices ativos"""
    # Consulta métricas de slices no Prometheus

@app.get("/api/prometheus/metrics/system")
async def get_system_metrics():
    """Métricas do sistema"""
    # Consulta métricas do sistema no Prometheus

@app.get("/api/prometheus/metrics/timeseries")
async def get_timeseries_metrics():
    """Séries temporais para gráficos"""
    # Consulta dados de séries temporais

@app.post("/api/prometheus/query")
async def execute_custom_query(query: str):
    """Query PromQL customizada"""
    # Executa queries personalizadas
```

### Funções de Consulta

```python
async def query_prometheus(query: str) -> List[Dict]:
    """Executa query PromQL no Prometheus"""
    try:
        # Consulta Prometheus
        # Trata erros e retorna resultados
    except Exception:
        # Retorna lista vazia em caso de erro
        return []
```

## 7. Frontend

### Componentes Principais

#### Layout.tsx
```typescript
export default function Layout({ children }: LayoutProps) {
  // Layout principal com navegação
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm">
        {/* Links de navegação */}
      </nav>
      
      {/* Conteúdo principal */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}
```

#### Dashboard.tsx
```typescript
export default function Dashboard() {
  // Consultas de dados
  const { data: health } = useQuery({
    queryKey: ['prometheus', 'health'],
    queryFn: () => prometheusApi.health().then(res => res.data),
  })
  
  // Outras consultas...
  
  return (
    <div>
      {/* Status do Prometheus */}
      <div className="mb-6">
        {/* Indicador de conexão */}
      </div>
      
      {/* Cards de métricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Cards de métricas */}
      </div>
      
      {/* Informações adicionais */}
    </div>
  )
}
```

### Serviços de API

```typescript
// API client
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Prometheus API
export const prometheusApi = {
  health: () => api.get('/api/prometheus/health'),
  slices: () => api.get('/api/prometheus/metrics/slices'),
  system: () => api.get('/api/prometheus/metrics/system'),
  // Outros endpoints...
}
```

### Helpers de Dados

```typescript
// Extração segura de valores
export function extractPrometheusValue(metric: any): string {
  // Extrai valores de forma segura
}

// Validação de métricas
export function hasMetrics(data: any[] | undefined | null): boolean {
  // Verifica se existem métricas
}

// Map seguro para arrays
export function safeMapMetrics<T>(
  data: any[] | undefined | null,
  mapper: (item: any, idx: number) => T
): T[] {
  // Map com validação
}
```

## 8. Integração com Prometheus

### Túnel SSH

```bash
# Estabelecer túnel SSH
ssh -L 9090:localhost:9090 user@remote-host
```

### Consultas PromQL

```python
# Exemplos de queries PromQL
queries = {
    "total": "count(trisla_slices_active)",
    "by_type": "sum by (slice_type) (trisla_slices_active)",
    "components_up": "up{job=~'trisla.*'}",
    "cpu_usage": "rate(container_cpu_usage_seconds_total{pod=~'trisla.*'}[5m]) * 100",
}
```

## 9. Deployment

### Requisitos

- Node.js 16+
- Python 3.8+
- SSH client

### Passos de Instalação

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Scripts de Inicialização

```bash
# Iniciar backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 5000 --reload

# Iniciar frontend
cd frontend
npm run dev
```

## 10. Mecanismo de Controle de Prompts

Para gerenciar prompts longos e manter a continuidade entre múltiplas interações com a IA, use o seguinte sistema:

### A. Sistema de Checkpoints

Cada prompt deve incluir:

1. **Número de Sequência**: Identifica a ordem do prompt
2. **Hash de Contexto**: Identifica o contexto da conversa
3. **Resumo do Estado Atual**: Breve descrição do que foi concluído

### B. Formato de Prompt

```
PROMPT #{NÚMERO} | HASH: {HASH} | PROJETO: Dashboard TriSLA

CONTEXTO:
{Resumo do estado atual do projeto}

ARQUIVOS CRIADOS:
- {lista de arquivos já criados}

PRÓXIMOS PASSOS:
{O que deve ser implementado neste prompt}

INSTRUÇÕES:
{Instruções detalhadas}
```

### C. Exemplo de Sequência de Prompts

#### Prompt #1
```
PROMPT #1 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Iniciando o projeto Dashboard TriSLA do zero.

ARQUIVOS CRIADOS:
Nenhum ainda.

PRÓXIMOS PASSOS:
1. Criar estrutura de diretórios
2. Configurar backend FastAPI
3. Configurar frontend React

INSTRUÇÕES:
Crie a estrutura inicial do projeto Dashboard TriSLA conforme a Referência Técnica.
Implemente o backend FastAPI básico e o frontend React com TypeScript.
```

#### Prompt #2
```
PROMPT #2 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Estrutura básica criada. Backend FastAPI e frontend React configurados.

ARQUIVOS CRIADOS:
- backend/main.py
- backend/requirements.txt
- frontend/package.json
- frontend/tsconfig.json
- frontend/vite.config.ts
- frontend/src/main.tsx
- frontend/src/App.tsx

PRÓXIMOS PASSOS:
1. Implementar endpoints da API
2. Criar componentes do dashboard
3. Configurar integração com Prometheus

INSTRUÇÕES:
Continue a implementação do Dashboard TriSLA. 
Adicione os endpoints da API para consultar métricas do Prometheus.
Implemente os componentes principais do dashboard.
```

### D. Gerenciamento de Estado

Para garantir a continuidade entre prompts, use estas técnicas:

1. **Resumo de Arquivos**: Liste todos os arquivos criados com seus caminhos
2. **Código Parcial**: Para arquivos grandes, use marcadores como:
   ```
   // Arquivo: frontend/src/components/Dashboard.tsx
   // Status: Parcial (60%)
   // Falta implementar: Gráficos de métricas, tratamento de erros
   ```
3. **Arquivos Completos**: Indique quais arquivos estão completos:
   ```
   // Arquivo: backend/main.py
   // Status: Completo (100%)
   ```

### E. Recuperação de Contexto

Se precisar retomar o trabalho após uma interrupção:

1. Forneça o último hash de contexto
2. Liste os arquivos já criados
3. Descreva o último estado conhecido
4. Solicite a continuação específica

```
PROMPT #3 | HASH: TRISLA-INIT | PROJETO: Dashboard TriSLA

CONTEXTO:
Retomando desenvolvimento. Backend com endpoints básicos implementados.
Frontend com componentes iniciais.

ARQUIVOS CRIADOS:
[Lista de arquivos...]

ÚLTIMO ESTADO:
Implementados endpoints /health e /api/prometheus/metrics/slices.
Frontend com Layout e Dashboard básico.

PRÓXIMOS PASSOS:
Continuar de onde paramos. Implementar:
1. Endpoint de timeseries
2. Componentes de gráficos
3. Tratamento de erros

INSTRUÇÕES:
Continue a implementação do Dashboard TriSLA a partir do ponto onde paramos.
```

Este sistema de controle permite gerenciar prompts longos e manter a continuidade entre múltiplas interações com a IA, garantindo que o desenvolvimento do Dashboard TriSLA seja consistente e eficiente.




