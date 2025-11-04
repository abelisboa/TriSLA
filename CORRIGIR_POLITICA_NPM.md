# 🔧 Corrigir Política de Execução para npm

## ❌ Problema

```
npm : O arquivo C:\Program Files\nodejs\npm.ps1 não pode ser carregado porque 
a execução de scripts foi desabilitada neste sistema.
```

## ✅ Solução

### Opção 1: Permitir apenas para o usuário atual (Recomendado)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Opção 2: Bypass temporário (apenas para esta sessão)

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Opção 3: Usar cmd.exe em vez de PowerShell

Abra `cmd.exe` (Prompt de Comando) e execute:
```cmd
cd C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local\frontend
npm run dev
```

---

## ✅ Script já foi corrigido!

O script `start-all.ps1` agora usa `-ExecutionPolicy Bypass` automaticamente.

---

## 🚀 Iniciar Novamente

```powershell
cd C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local
.\scripts\start-all.ps1
```

OU configure a política uma vez:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois disso, o npm funcionará normalmente em todas as sessões.




