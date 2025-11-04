# 🔧 Guia de Configuração Completa

## ❌ Problemas Encontrados

1. **Política de Execução do PowerShell** bloqueando npm e venv activation
2. **uvicorn não instalado** porque o venv não foi ativado corretamente

## ✅ Solução Completa

### Passo 1: Instalar Dependências

Execute o script de instalação (usa cmd.exe, sem problemas de política):

```powershell
.\scripts\install-dependencies.ps1
```

OU manualmente:

**Backend:**
```cmd
cd backend
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Frontend:**
```cmd
cd frontend
npm install
```

---

### Passo 2: Iniciar Dashboard

Agora todos os scripts usam `cmd.exe` e não têm problemas de política:

#### Opção 1: Tudo de uma vez
```powershell
.\scripts\start-all.ps1
```

#### Opção 2: Separado

**Terminal 1 - Backend:**
```powershell
.\scripts\start-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\scripts\start-frontend.ps1
```

#### Opção 3: Manual via CMD

**Terminal 1 - Backend:**
```cmd
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --port 5000
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm run dev
```

---

## 🔍 Verificar Instalação

### Verificar Backend
```powershell
cd backend
if (Test-Path venv\Scripts\python.exe) {
    venv\Scripts\python.exe -m pip list | Select-String uvicorn
}
```

### Verificar Frontend
```powershell
cd frontend
if (Test-Path node_modules) {
    Write-Host "✅ node_modules existe"
} else {
    Write-Host "❌ Execute: npm install"
}
```

---

## ⚙️ Configurar Política Permanentemente (Opcional)

Se quiser usar PowerShell normalmente (sem cmd.exe):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois disso, você pode usar:
- `npm` diretamente no PowerShell
- `.\venv\Scripts\Activate.ps1` normalmente

---

## ✅ Status dos Scripts

Todos os scripts foram atualizados para usar `cmd.exe`:
- ✅ `start-all.ps1` - Usa cmd.exe para backend e frontend
- ✅ `start-backend.ps1` - Usa cmd.exe e Python do venv diretamente
- ✅ `start-frontend.ps1` - Usa cmd.exe para npm
- ✅ `install-dependencies.ps1` - Novo script de instalação

---

## 🚀 Próximos Passos

1. Execute `.\scripts\install-dependencies.ps1` (se ainda não instalou)
2. Execute `.\scripts\start-all.ps1` para iniciar tudo
3. Acesse http://localhost:5173




