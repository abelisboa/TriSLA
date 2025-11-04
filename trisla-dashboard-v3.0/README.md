# 🚀 TriSLA Dashboard v3.0

Dashboard moderno e responsivo para visualização e gerenciamento de slices TriSLA via Prometheus, com integração ao SEM-NSMF para validação e implantação de slices.

## ✨ Funcionalidades

- 📊 **Dashboard Principal**: Visão geral do sistema TriSLA
- 🧩 **Gestão de Slices**: Crie, visualize e gerencie slices TriSLA
- 🤖 **Criação por NPL**: Gere slices a partir de linguagem natural
- 📝 **Criação por GST**: Configure slices com parâmetros específicos
- 📈 **Métricas Detalhadas**: Gráficos em tempo real por slice
- 📚 **Templates**: Catálogo de GST/NEST com import/export
- 🔄 **Ciclo de Vida**: Validação, implantação e monitoramento de slices
- 🔌 **Integração**: Prometheus para métricas e SEM-NSMF para orquestração

## 🛠️ Tecnologias

- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS + Recharts
- **Backend**: FastAPI (Python) - Proxy para Prometheus e SEM-NSMF
- **Túnel**: SSH (localhost:9090 → node1:9090)
- **Deployment**: Docker + docker-compose (opcional)

## 📋 Pré-requisitos

- Node.js 18+
- Python 3.10+
- SSH configurado para acesso ao node1 (para métricas Prometheus)
- SEM-NSMF acessível via port-forward (opcional)

## 🚀 Início Rápido

### No Windows

```powershell
# No diretório raiz do projeto
.\scripts\start-dashboard.ps1
```

### No Linux/WSL

```bash
# No diretório raiz do projeto
./scripts/start-dashboard.sh
```

Isso irá:
- Instalar as dependências necessárias
- Iniciar o backend (porta 5000)
- Iniciar o frontend (porta 5173)

### Acessar o Dashboard

- **Dashboard**: http://localhost:5173
- **API**: http://localhost:5000
- **Swagger Docs**: http://localhost:5000/docs

## ⚙️ Configuração

O backend pode ser configurado através do arquivo `backend/config.yaml`:

```yaml
# TriSLA Dashboard Backend Configuration
server:
  host: "0.0.0.0"
  port: 5000
  debug: false

prometheus:
  url: "http://localhost:9090"

sem_nsmf:
  url: "http://localhost:8000"
  token: ""  # Adicione seu token aqui se necessário
```

## 📁 Estrutura

```
trisla-dashboard-v3.0/
├── frontend/          # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── pages/         # Páginas do dashboard
│   │   └── services/      # API client
│   └── package.json
├── backend/           # FastAPI proxy
│   ├── main.py        # API principal
│   ├── config.py      # Configuração
│   └── requirements.txt
└── scripts/           # Scripts de inicialização
    ├── start-dashboard.sh
    └── start-dashboard.ps1
```

## 🔧 Troubleshooting

### Túnel SSH não conecta
- Verifique se consegue acessar: `ssh porvir5g@ppgca.unisinos.br`
- Verifique se node1 está acessível após jump host

### Backend não conecta ao Prometheus
- Certifique-se que túnel SSH está rodando
- Verifique se porta 9090 está livre: `netstat -ano | findstr :9090`
- Verifique configuração em `config.yaml`

### Frontend não conecta ao backend
- Verifique se backend está rodando na porta 5000
- Verifique console do navegador (F12) para erros CORS

### SEM-NSMF não acessível
- Verifique se o port-forward está ativo: `kubectl port-forward svc/sem-nsmf 8000:8000 -n sem-nsmf`
- Verifique configuração do SEM_NSMF_URL em `config.yaml`

## 🎯 Pronto para Usar!

Execute o script de inicialização e acesse http://localhost:5173

---

**Desenvolvido para TriSLA NASP** 🚀



