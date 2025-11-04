# 🔧 Resolver Erro 404 no Frontend (localhost:5173)

## ❌ Problema

O backend está funcionando (localhost:5000/docs funciona), mas o frontend retorna 404.

## ✅ Soluções

### Solução 1: Verificar se o frontend está rodando

```bash
# Verificar processos
ps aux | grep vite

# Se não estiver rodando, iniciar:
./scripts-wsl/start-frontend.sh
```

### Solução 2: Diagnosticar completamente

```bash
# Execute o script de diagnóstico
chmod +x scripts-wsl/diagnose.sh
./scripts-wsl/diagnose.sh
```

### Solução 3: Reiniciar tudo

```bash
# Parar tudo
./scripts-wsl/stop-all.sh

# Aguardar 2 segundos
sleep 2

# Iniciar tudo novamente
./scripts-wsl/start-all.sh
```

### Solução 4: Verificar se a porta está correta

O frontend deve estar rodando na porta 5173. Verifique:

```bash
# Ver processos e portas
netstat -tuln | grep 5173

# OU
ss -tuln | grep 5173

# Verificar logs do frontend
# O processo do frontend deve mostrar algo como:
# "Local: http://localhost:5173/"
```

### Solução 5: Verificar se os arquivos do frontend existem

```bash
cd ~/trisla-dashboard-local/frontend

# Verificar arquivos essenciais
ls -la index.html
ls -la src/
ls -la node_modules/

# Se node_modules não existe:
npm install

# Se arquivos estão faltando, copiar novamente:
cd ~/trisla-dashboard-local
./scripts-wsl/copy-from-windows.sh
```

### Solução 6: Iniciar frontend manualmente

```bash
cd ~/trisla-dashboard-local/frontend
npm run dev
```

Você deve ver algo como:
```
VITE v5.4.21  ready in 336 ms

➜  Local:   http://localhost:5173/
```

---

## 🔍 Diagnóstico Rápido

Execute:

```bash
./scripts-wsl/diagnose.sh
```

Este script irá verificar:
- ✅ Processos em execução
- ✅ Portas em uso
- ✅ Arquivos necessários
- ✅ Conexões funcionando

---

## ✅ Verificação Final

Após corrigir, verifique:

1. **Processo rodando:**
   ```bash
   ps aux | grep vite
   ```

2. **Porta ativa:**
   ```bash
   curl http://localhost:5173
   ```

3. **Acessar no navegador:**
   - Abra: http://localhost:5173
   - Deve mostrar o dashboard, não erro 404

---

## 🚨 Se nada funcionar

1. Verifique os logs do frontend no terminal onde iniciou
2. Verifique se há erros de compilação
3. Tente reiniciar o WSL:
   ```bash
   # No PowerShell (Windows)
   wsl --shutdown
   # Depois, abra o WSL novamente
   ```

---

## 📝 Nota

Se o backend funciona (porta 5000) mas o frontend não (porta 5173), significa que:
- ✅ Backend está OK
- ❌ Frontend não iniciou ou parou

A solução mais comum é reiniciar o frontend:
```bash
./scripts-wsl/start-frontend.sh
```





