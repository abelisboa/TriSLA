# 🚀 Guia de Início Rápido - TriSLA Dashboard

## ✅ Implementação Completa!

O dashboard local foi implementado com sucesso. Todos os arquivos estão prontos.

---

## 📋 Passo a Passo para Iniciar

### 1️⃣ Instalar Backend (se ainda não fez)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

### 2️⃣ Iniciar Tudo Automaticamente

```powershell
.\scripts\start-all.ps1
```

Este script vai:
- ✅ Iniciar túnel SSH
- ✅ Iniciar backend (porta 5000)
- ✅ Iniciar frontend (porta 5173)

### 3️⃣ Ou Iniciar Manualmente

#### Terminal 1: Túnel SSH
```powershell
.\scripts\start-ssh-tunnel.ps1
```

#### Terminal 2: Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 5000
```

#### Terminal 3: Frontend
```powershell
cd frontend
npm run dev
```

---

## 🌐 Acessar Dashboard

Após iniciar tudo:

- **Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Swagger Docs**: http://localhost:5000/docs
- **Prometheus (via túnel)**: http://localhost:9090

---

## 📊 Funcionalidades

1. **Dashboard Principal** (`/`)
   - Status do Prometheus
   - Métricas principais
   - Cards de informações

2. **Gestão de Slices** (`/slices`)
   - Total de slices
   - Slices por tipo
   - Histórico

3. **Métricas Detalhadas** (`/metrics`)
   - Gráficos em tempo real
   - Componentes do sistema
   - Uso de CPU e memória

---

## ⚙️ Configuração

### Variáveis de Ambiente (Opcional)

Crie `.env` na raiz do projeto:

```env
VITE_API_URL=http://localhost:5000
PROMETHEUS_URL=http://localhost:9090
```

---

## 🔧 Troubleshooting

### Frontend não conecta ao backend
- Verifique se backend está rodando na porta 5000
- Verifique console do navegador (F12) para erros

### Prometheus não acessível
- Verifique se túnel SSH está rodando
- Teste: `curl http://localhost:9090/api/v1/status/config`

### Porta já em uso
```powershell
# Ver processos
netstat -ano | findstr :5000
netstat -ano | findstr :5173
netstat -ano | findstr :9090

# Matar processo
Stop-Process -Id <PID>
```

---

## 📝 Estrutura Final

```
trisla-dashboard-local/
├── frontend/
│   ├── src/
│   │   ├── components/    ✅ Layout, MetricCard
│   │   ├── pages/         ✅ Dashboard, Metrics, SlicesManagement
│   │   ├── services/      ✅ API client
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json       ✅ Dependências instaladas
│   └── vite.config.ts
│
├── backend/
│   ├── main.py           ✅ FastAPI completo
│   └── requirements.txt
│
└── scripts/
    ├── start-all.ps1     ✅ Script principal
    └── start-ssh-tunnel.ps1
```

---

## 🎉 Pronto!

Execute `.\scripts\start-all.ps1` e acesse http://localhost:5173

O dashboard está totalmente funcional e conectado ao Prometheus via túnel SSH!




