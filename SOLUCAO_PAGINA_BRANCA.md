# 🔧 Resolver Página Branca no Frontend

## ❌ Problema

- ✅ Vite está rodando: "VITE v5.4.21 ready"
- ✅ Porta 5173 responde
- ❌ Página está completamente branca (sem conteúdo)

## 🔍 Causas Possíveis

1. **index.html não existe ou está vazio**
2. **src/main.tsx não está sendo encontrado**
3. **Erros JavaScript no console**
4. **React não está renderizando**
5. **CORS ou problemas de roteamento**

---

## ✅ Solução Passo a Passo

### Passo 1: Verificar Console do Navegador

**Abra o DevTools (F12) e verifique:**
- Aba Console: Veja se há erros em vermelho
- Aba Network: Veja se há requisições falhando (status 404)

### Passo 2: Verificar se index.html Existe

No **WSL**, execute:

```bash
cd ~/trisla-dashboard-local/frontend
ls -la index.html
cat index.html
```

**Deve ter:**
```html
<div id="root"></div>
<script type="module" src="/src/main.tsx"></script>
```

### Passo 3: Criar/Corrigir index.html

Se não existir ou estiver incorreto:

```bash
cd ~/trisla-dashboard-local/frontend

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

### Passo 4: Verificar src/main.tsx

```bash
ls -la src/main.tsx
cat src/main.tsx
```

**Deve conter:**
```typescript
ReactDOM.createRoot(document.getElementById('root')!).render(...)
```

### Passo 5: Verificar Erros no Console

1. **Abra o navegador em http://localhost:5173**
2. **Pressione F12** para abrir DevTools
3. **Vá na aba Console**
4. **Procure por erros em vermelho**

**Erros comuns:**
- `Failed to load module` → arquivo não encontrado
- `Cannot find module` → importação incorreta
- `root is null` → div#root não existe

### Passo 6: Reiniciar Vite

```bash
cd ~/trisla-dashboard-local/frontend

# Parar Vite (Ctrl+C no terminal)
# Ou
pkill -f vite

# Limpar cache
rm -rf node_modules/.vite dist

# Reiniciar
npm run dev
```

---

## 🔍 Diagnóstico Completo

Execute no **WSL**:

```bash
cd ~/trisla-dashboard-local/frontend

echo "=== Verificando index.html ==="
if [ -f index.html ]; then
    echo "✅ index.html existe"
    echo "Conteúdo:"
    cat index.html
else
    echo "❌ index.html NÃO existe!"
fi

echo ""
echo "=== Verificando src/main.tsx ==="
if [ -f src/main.tsx ]; then
    echo "✅ src/main.tsx existe"
else
    echo "❌ src/main.tsx NÃO existe!"
fi

echo ""
echo "=== Verificando src/App.tsx ==="
if [ -f src/App.tsx ]; then
    echo "✅ src/App.tsx existe"
else
    echo "❌ src/App.tsx NÃO existe!"
fi

echo ""
echo "=== Testando conexão ==="
curl http://localhost:5173 2>&1 | head -20
```

---

## ✅ Solução Rápida (Tudo de Uma Vez)

Execute no **WSL**:

```bash
cd ~/trisla-dashboard-local/frontend

# 1. Parar Vite
pkill -f vite
sleep 2

# 2. Criar index.html se não existir
if [ ! -f index.html ]; then
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
    echo "✅ index.html criado"
fi

# 3. Limpar cache
rm -rf node_modules/.vite dist

# 4. Verificar estrutura
echo "Estrutura:"
ls -la | grep -E "index|package|vite"
echo ""
ls -la src/ | head -10

# 5. Reiniciar
echo ""
echo "🚀 Iniciando Vite..."
npm run dev
```

---

## 🎯 Checklist

- [ ] `index.html` existe na raiz do `frontend/`
- [ ] `index.html` contém `<div id="root"></div>`
- [ ] `index.html` contém `<script type="module" src="/src/main.tsx"></script>`
- [ ] `src/main.tsx` existe
- [ ] `src/App.tsx` existe
- [ ] Não há erros no console do navegador (F12)
- [ ] Cache do Vite foi limpo

---

## 🚨 Se Ainda Estiver Branco

1. **Abra DevTools (F12)**
2. **Vá na aba Console**
3. **Copie os erros que aparecem**
4. **Verifique a aba Network para ver requisições 404**

Isso vai mostrar exatamente o que está faltando!





