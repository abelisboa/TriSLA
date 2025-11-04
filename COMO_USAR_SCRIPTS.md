# 🚀 Como Usar os Scripts para Abrir Backend

## 📋 Scripts Disponíveis

### Windows PowerShell
```
.\scripts\start-backend-and-open.ps1
```

### Linux/WSL
```bash
chmod +x scripts-wsl/start-backend-and-open.sh
./scripts-wsl/start-backend-and-open.sh
```

---

## 🎯 O Que o Script Faz

1. ✅ Verifica se o virtual environment existe
2. ✅ Verifica se a porta 5000 está livre
3. ✅ Inicia o backend FastAPI na porta 5000
4. ✅ Aguarda o backend estar pronto
5. ✅ Abre automaticamente o navegador em `http://localhost:5000`

---

## 📊 URLs Disponíveis

Após o script rodar, você terá acesso a:

- **API Principal:** http://localhost:5000
- **Health Check:** http://localhost:5000/health
- **Swagger UI (Documentação Interativa):** http://localhost:5000/docs
- **ReDoc (Documentação Alternativa):** http://localhost:5000/redoc

---

## 🔧 Pré-requisitos

### Windows
- Python 3.8+ instalado
- Virtual environment criado: `backend\venv`
- Dependências instaladas: `pip install -r requirements.txt`

### WSL/Linux
- Python 3.8+ instalado
- Virtual environment criado: `backend/venv`
- Dependências instaladas: `pip install -r requirements.txt`

---

## 📝 Uso Detalhado

### Windows PowerShell

```powershell
# 1. Navegar para o projeto
cd C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local

# 2. Executar script
.\scripts\start-backend-and-open.ps1
```

**O que acontece:**
- Backend inicia em uma nova janela do terminal
- Navegador abre automaticamente
- Você pode usar a API diretamente

---

### WSL/Linux

```bash
# 1. Navegar para o projeto
cd ~/trisla-dashboard-local

# 2. Dar permissão de execução (primeira vez)
chmod +x scripts-wsl/start-backend-and-open.sh

# 3. Executar script
./scripts-wsl/start-backend-and-open.sh
```

**O que acontece:**
- Backend inicia em background
- Logs são salvos em `backend.log`
- PID é salvo em `backend.pid`
- Navegador abre automaticamente (se configurado)

---

## 🛑 Como Parar o Backend

### Windows
- Feche a janela do terminal onde o backend está rodando
- Ou pressione `Ctrl+C` no terminal

### WSL/Linux
```bash
# Usar o script de parada
./scripts-wsl/stop-all.sh

# Ou matar pelo PID
kill $(cat backend.pid)

# Ou manualmente
pkill -f "uvicorn.*main:app"
```

---

## ⚠️ Troubleshooting

### Porta 5000 já está em uso

**Windows:**
```
# Ver processos na porta 5000
netstat -ano | findstr :5000

# Matar processo (substitua PID)
taskkill /PID <PID> /F
```

**WSL/Linux:**
```bash
# Ver processos na porta 5000
lsof -i :5000

# Matar processo
kill <PID>
```

### Navegador não abre automaticamente

**Windows:**
- Abra manualmente: http://localhost:5000

**WSL:**
- Se não abrir, use no Windows: http://localhost:5000
- Ou configure `wslview` ou `cmd.exe` no WSL

### Backend não inicia

1. Verifique se o venv existe:
   ```bash
   # Windows
   Test-Path backend\venv\Scripts\python.exe
   
   # WSL
   test -f backend/venv/bin/python
   ```

2. Reinstale dependências:
   ```bash
   # Windows
   backend\venv\Scripts\pip install -r backend\requirements.txt
   
   # WSL
   source backend/venv/bin/activate
   pip install -r backend/requirements.txt
   ```

---

## 🎨 Exemplos de Uso da API

### Health Check
```bash
curl http://localhost:5000/health
```

### Métricas de Slices
```bash
curl http://localhost:5000/api/prometheus/metrics/slices
```

### Swagger UI
Acesse no navegador: http://localhost:5000/docs

---

## 📚 Mais Informações

- **Swagger UI:** Interface interativa para testar a API
- **ReDoc:** Documentação alternativa mais limpa
- **Logs:** Veja os logs no terminal onde o backend iniciou

---

## ✅ Checklist

Antes de executar o script, certifique-se:

- [ ] Python 3.8+ instalado
- [ ] Virtual environment criado (`backend/venv`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Porta 5000 livre
- [ ] Está no diretório raiz do projeto

---

**Pronto! Agora você pode iniciar o backend e abrir no navegador com um único comando!** 🎉





