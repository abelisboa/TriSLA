# 🎯 Dashboard TriSLA - Funcionamento Independente

## ✅ O que mudou?

O dashboard agora **funciona completamente independente** do SSH tunnel. Você pode:

- ✅ Iniciar o dashboard sem precisar conectar ao node1
- ✅ Visualizar a interface mesmo sem dados do Prometheus
- ✅ Conectar ao Prometheus quando quiser usando o túnel SSH (opcional)

---

## 🚀 Iniciar Dashboard (Sem SSH)

### Opção 1: Script Automático

```powershell
cd C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local
.\scripts\start-all.ps1
```

O script agora:
- ✅ Inicia backend e frontend
- ❌ **NÃO** inicia túnel SSH (opcional)

### Opção 2: Manual

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 5000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## 🔌 Conectar ao Prometheus (Opcional)

Quando quiser conectar ao Prometheus do node1, execute em um terminal separado:

```powershell
.\scripts\start-ssh-tunnel.ps1
```

OU manualmente:

```powershell
ssh -L 9090:nasp-prometheus.monitoring.svc.cluster.local:9090 `
    -J porvir5g@ppgca.unisinos.br porvir5g@node006 -N
```

---

## 📊 Comportamento

### Sem Prometheus Conectado:
- ✅ Dashboard carrega normalmente
- ⚪ Mostra aviso amigável sobre Prometheus desconectado
- ⚪ Métricas mostram "N/A" ou "0"
- ✅ Interface funcional para navegação

### Com Prometheus Conectado:
- ✅ Dashboard carrega com dados reais
- ✅ Mostra indicador verde de conexão
- ✅ Métricas atualizadas em tempo real
- ✅ Gráficos funcionando

---

## 🌐 URLs

- **Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Swagger**: http://localhost:5000/docs
- **Prometheus** (se túnel ativo): http://localhost:9090

---

## 🔧 Arquivos Modificados

1. **`scripts/start-all.ps1`** - Removida inicialização automática do SSH tunnel
2. **`backend/main.py`** - Tolerante a falhas do Prometheus (timeout curto, retorna vazio em vez de erro)
3. **`frontend/src/pages/Dashboard.tsx`** - Mostra mensagens amigáveis quando Prometheus desconectado

---

## 💡 Dicas

- O dashboard sempre funciona, mesmo offline
- Conecte o túnel SSH apenas quando precisar ver dados reais
- Você pode deixar o dashboard rodando e conectar/desconectar o túnel a qualquer momento
- O backend detecta automaticamente se o Prometheus está disponível




