# 🔬 Análise Cirúrgica: Erro 404 no Frontend

## ❌ Problema

```
Não é possível encontrar esta página de localhost
Não foi encontrada qualquer página Web para o endereço Web: http://localhost:5173/
HTTP ERROR 404
```

**Sintomas:**
- ✅ Vite inicia corretamente: "VITE v5.4.21 ready in 352 ms"
- ✅ Mostra: "Local: http://localhost:5173/"
- ✅ Porta 5173 está em uso (confirmado por netstat)
- ❌ Navegador retorna 404
- ⚠️  Aviso: "Could not auto-determine entry point from rollupOptions or html files"

---

## 🔍 Análise Detalhada

### 1. Possíveis Causas

#### Causa 1: `index.html` não está na raiz do frontend
**Evidência:** Aviso "Could not auto-determine entry point"
**Verificação:** `ls frontend/index.html` deve existir

#### Causa 2: Estrutura de diretórios incorreta
**Evidência:** Vite não encontra arquivos automaticamente
**Verificação:** `frontend/index.html` deve estar em `frontend/` e não em `frontend/src/`

#### Causa 3: Configuração do Vite incorreta
**Evidência:** Vite não determina entry point automaticamente
**Solução:** Configuração explícita necessária

#### Causa 4: Permissões de arquivo
**Evidência:** WSL pode ter problemas de permissão
**Verificação:** Arquivos devem ser legíveis

#### Causa 5: Múltiplas instâncias do Vite
**Evidência:** Porta pode estar em uso por processo zombie
**Verificação:** `ps aux | grep vite`

---

## 🔬 Diagnóstico Passo a Passo

### Passo 1: Verificar Estrutura de Arquivos

```bash
cd ~/trisla-dashboard-local/frontend
ls -la index.html          # Deve existir
ls -la src/main.tsx        # Deve existir
ls -la package.json        # Deve existir
```

**Estrutura esperada:**
```
frontend/
├── index.html          ← DEVE ESTAR AQUI (raiz do frontend)
├── package.json
├── vite.config.ts
├── tsconfig.json
└── src/
    ├── main.tsx        ← Entry point React
    ├── App.tsx
    └── ...
```

### Passo 2: Verificar Conteúdo do index.html

O `index.html` DEVE ter:
```html
<div id="root"></div>
<script type="module" src="/src/main.tsx"></script>
```

### Passo 3: Verificar Configuração do Vite

O `vite.config.ts` deve estar configurado corretamente:
```typescript
export default defineConfig({
  plugins: [react()],
  root: '.',              // Importante: raiz explícita
  server: {
    port: 5173,
    host: true,
    strictPort: true
  }
})
```

### Passo 4: Verificar Processos e Portas

```bash
# Ver processos do Vite
ps aux | grep vite

# Ver portas em uso
netstat -tuln | grep 5173
# OU
ss -tuln | grep 5173

# Matar processos antigos se necessário
pkill -f vite
```

### Passo 5: Verificar Logs do Vite

Quando o Vite inicia, ele deve mostrar:
```
VITE v5.4.21  ready in 352 ms
➜  Local:   http://localhost:5173/
```

Se não mostrar "Local: http://localhost:5173/", há problema.

---

## 🎯 Soluções por Causa

### Solução 1: Corrigir Posição do index.html

Se `index.html` não está na raiz do `frontend/`:

```bash
cd ~/trisla-dashboard-local/frontend

# Mover index.html para raiz se estiver em lugar errado
mv src/index.html index.html  # Se estiver em src/

# OU criar novo se não existir
cat > index.html << 'EOF'
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TriSLA Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
```

### Solução 2: Corrigir Configuração do Vite

```bash
cd ~/trisla-dashboard-local/frontend

# Editar vite.config.ts para ter configuração explícita
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  root: path.resolve(__dirname, '.'),
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    open: false
  },
  build: {
    outDir: 'dist'
  }
})
EOF
```

### Solução 3: Limpar e Reinstalar

```bash
cd ~/trisla-dashboard-local/frontend

# Parar todos os processos
pkill -f vite

# Limpar cache
rm -rf node_modules/.vite
rm -rf dist

# Reinstalar dependências (se necessário)
npm install

# Iniciar novamente
npm run dev
```

### Solução 4: Verificar Permissões

```bash
cd ~/trisla-dashboard-local/frontend

# Dar permissões corretas
chmod 644 index.html
chmod 644 package.json
chmod 755 src/
chmod 644 src/*.tsx
```

### Solução 5: Forçar Vite a Usar Porta Correta

```bash
cd ~/trisla-dashboard-local/frontend

# Matar processos antigos
pkill -f vite
sleep 2

# Verificar porta livre
netstat -tuln | grep 5173

# Iniciar com configuração explícita
npm run dev -- --port 5173 --host
```

---

## 🔧 Script de Diagnóstico Completo

```bash
#!/bin/bash
# diagnose-404.sh

cd ~/trisla-dashboard-local/frontend

echo "🔍 Diagnóstico Completo do 404"
echo "================================"
echo ""

# 1. Verificar estrutura
echo "1️⃣ Estrutura de arquivos:"
[ -f index.html ] && echo "   ✅ index.html existe" || echo "   ❌ index.html NÃO existe"
[ -f src/main.tsx ] && echo "   ✅ src/main.tsx existe" || echo "   ❌ src/main.tsx NÃO existe"
[ -f package.json ] && echo "   ✅ package.json existe" || echo "   ❌ package.json NÃO existe"
echo ""

# 2. Verificar conteúdo do index.html
echo "2️⃣ Conteúdo do index.html:"
if [ -f index.html ]; then
    if grep -q "id=\"root\"" index.html; then
        echo "   ✅ Contém <div id=\"root\">"
    else
        echo "   ❌ NÃO contém <div id=\"root\">"
    fi
    if grep -q "src=\"/src/main.tsx\"" index.html; then
        echo "   ✅ Contém script para /src/main.tsx"
    else
        echo "   ❌ NÃO contém script para /src/main.tsx"
    fi
fi
echo ""

# 3. Verificar processos
echo "3️⃣ Processos Vite:"
VITE_PROC=$(pgrep -f vite)
if [ -n "$VITE_PROC" ]; then
    echo "   ✅ Vite rodando (PIDs: $VITE_PROC)"
    ps aux | grep vite | grep -v grep
else
    echo "   ❌ Vite NÃO está rodando"
fi
echo ""

# 4. Verificar portas
echo "4️⃣ Porta 5173:"
if netstat -tuln 2>/dev/null | grep -q ":5173 "; then
    echo "   ✅ Porta 5173 está em uso"
    netstat -tuln | grep 5173
else
    echo "   ❌ Porta 5173 NÃO está em uso"
fi
echo ""

# 5. Testar conexão
echo "5️⃣ Teste de conexão:"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Responde em http://localhost:5173"
    curl -I http://localhost:5173 2>&1 | head -5
else
    echo "   ❌ NÃO responde em http://localhost:5173"
fi
echo ""

# 6. Verificar configuração Vite
echo "6️⃣ Configuração Vite:"
if [ -f vite.config.ts ]; then
    echo "   ✅ vite.config.ts existe"
    if grep -q "root:" vite.config.ts; then
        echo "   ✅ Tem 'root:' configurado"
    else
        echo "   ⚠️  NÃO tem 'root:' configurado"
    fi
else
    echo "   ❌ vite.config.ts NÃO existe"
fi
```

---

## ✅ Solução Rápida (Tudo de Uma Vez)

```bash
cd ~/trisla-dashboard-local/frontend

# 1. Parar tudo
pkill -f vite
sleep 2

# 2. Garantir que index.html está correto
cat > index.html << 'EOF'
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TriSLA Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# 3. Corrigir vite.config.ts
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: '.',
  server: {
    port: 5173,
    host: true,
    strictPort: true
  }
})
EOF

# 4. Limpar cache
rm -rf node_modules/.vite
rm -rf dist

# 5. Iniciar
npm run dev
```

---

## 🎯 Causa Mais Provável

**Causa mais provável:** O `index.html` pode não estar na raiz do diretório `frontend/` ou o Vite não está conseguindo encontrá-lo devido à configuração.

**Solução mais provável:** Garantir que `index.html` está em `frontend/index.html` (não em `frontend/src/index.html`) e que o `vite.config.ts` tem `root: '.'`.

---

## 📝 Checklist Final

- [ ] `frontend/index.html` existe na raiz
- [ ] `frontend/index.html` contém `<div id="root"></div>`
- [ ] `frontend/index.html` contém `<script type="module" src="/src/main.tsx"></script>`
- [ ] `frontend/src/main.tsx` existe
- [ ] `vite.config.ts` tem `root: '.'`
- [ ] Porta 5173 está livre antes de iniciar
- [ ] Nenhum processo zombie do Vite rodando
- [ ] Permissões de arquivo estão corretas

---

Execute o script de diagnóstico acima para identificar exatamente qual é o problema!





