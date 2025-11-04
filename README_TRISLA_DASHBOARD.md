# 🚀 TriSLA Dashboard

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
- **Deployment**: Docker + docker-compose

## 📋 Pré-requisitos

- Node.js 18+
- Python 3.11+
- Docker e docker-compose (opcional)
- SSH configurado para acesso ao node1
- SEM-NSMF acessível via port-forward (opcional)

## 🚀 Início Rápido

### Opção 1: Execução Local

1. **Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\Activate.ps1 no Windows
pip install -r requirements.txt
cp config.yaml.example config.yaml  # Edite conforme necessário
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

2. **Frontend**:
```bash
cd frontend
npm install
npm run dev
```

3. **Túnel SSH para Prometheus**:
```bash
ssh -L 9090:localhost:9090 user@node1
```

4. **Port-forward para SEM-NSMF** (opcional):
```bash
kubectl port-forward svc/sem-nsmf 8000:8000 -n sem-nsmf
```

### Opção 2: Docker

1. **Configuração**:
```bash
cp backend/config.yaml.example backend/config.yaml  # Edite conforme necessário
```

2. **Execução**:
```bash
docker-compose up -d
```

3. **Túnel SSH para Prometheus**:
```bash
ssh -L 9090:localhost:9090 user@node1
```

4. **Port-forward para SEM-NSMF** (opcional):
```bash
kubectl port-forward svc/sem-nsmf 8000:8000 -n sem-nsmf
```

## 📁 Estrutura

```
trisla-dashboard/
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
├── docker-compose.yml # Configuração Docker
└── README.md          # Documentação
```

## 🔧 Troubleshooting

### Túnel SSH não conecta
- Verifique se consegue acessar: `ssh user@node1`
- Verifique se porta 9090 está livre: `netstat -ano | findstr :9090`

### Backend não conecta ao Prometheus
- Certifique-se que túnel SSH está rodando
- Verifique configuração em `config.yaml` ou variáveis de ambiente

### Frontend não conecta ao backend
- Verifique se backend está rodando na porta 5000
- Verifique console do navegador (F12) para erros CORS

### SEM-NSMF não acessível
- Verifique se o port-forward está ativo: `kubectl port-forward svc/sem-nsmf 8000:8000 -n sem-nsmf`
- Verifique configuração do SEM_NSMF_URL em `config.yaml`

## 📖 Documentação Adicional

- **API Docs**: http://localhost:5000/docs
- **Prometheus**: http://localhost:9090
- **SEM-NSMF**: http://localhost:8000/docs

## 🎯 Pronto para Usar!

Acesse http://localhost:5173 para visualizar o dashboard.

---

**Desenvolvido para TriSLA NASP** 🚀



