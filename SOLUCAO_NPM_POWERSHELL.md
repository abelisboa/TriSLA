# 🔧 Solução: Problema de Política de Execução do npm no PowerShell

## ❌ Problema

```
npm : O arquivo C:\Program Files\nodejs\npm.ps1 não pode ser carregado porque 
a execução de scripts foi desabilitada neste sistema.
```

## ✅ Soluções Implementadas

### 1. Script `start-all.ps1` Corrigido
Agora usa `cmd.exe` para iniciar o frontend, evitando problemas de política.

### 2. Scripts Separados Criados

**Para iniciar apenas o backend:**
```powershell
.\scripts\start-backend.ps1
```

**Para iniciar apenas o frontend (via cmd.exe):**
```powershell
.\scripts\start-frontend.ps1
```

OU manualmente:
```cmd
cd frontend
npm run dev
```

---

## 🚀 Formas de Iniciar

### Opção 1: Script Automático (Recomendado)
```powershell
.\scripts\start-all.ps1
```
Agora funciona corretamente (usa cmd.exe para frontend).

### Opção 2: Scripts Separados

**Terminal 1 - Backend:**
```powershell
.\scripts\start-backend.ps1
```

**Terminal 2 - Frontend (cmd.exe):**
```cmd
cd frontend
npm run dev
```

OU use o script PowerShell:
```powershell
.\scripts\start-frontend.ps1
```

### Opção 3: Manual (3 Terminais)

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 5000
```

**Terminal 2 - Frontend (CMD):**
```cmd
cd frontend
npm run dev
```

**Terminal 3 - SSH Tunnel (Opcional):**
```powershell
.\scripts\start-ssh-tunnel.ps1
```

---

## 🔧 Solução Permanente (Opcional)

Se quiser que o npm funcione diretamente no PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois disso, o `npm` funcionará normalmente no PowerShell.

---

## ✅ Status

- ✅ Script `start-all.ps1` corrigido (usa cmd.exe)
- ✅ Scripts separados criados
- ✅ Dashboard funciona sem conexão SSH
- ✅ Frontend inicia sem erros de política




