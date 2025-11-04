# 🚀 Como Iniciar o Dashboard

## ✅ Arquivos Estão em:

```
C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local
```

---

## 📋 Opções para Iniciar

### Opção 1: Script Automático

```powershell
.\scripts\start-all.ps1
```

Se der erro de execução, use:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-all.ps1
```

### Opção 2: Manual (3 Terminais)

#### Terminal 1: Túnel SSH
```powershell
ssh -L 9090:nasp-prometheus.monitoring.svc.cluster.local:9090 `
    -J porvir5g@ppgca.unisinos.br porvir5g@node006 -N
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

## 🌐 Acessar

- **Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:5000/docs

---

## ⚠️ Se Scripts Não Funcionarem

Execute manualmente os 3 comandos acima em terminais separados.




