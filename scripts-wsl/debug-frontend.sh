#!/bin/bash
# Script para debugar página branca no frontend
# Uso: ./scripts-wsl/debug-frontend.sh

set -e

cd ~/trisla-dashboard-local/frontend

echo "🔍 Debug Completo do Frontend"
echo "=============================="
echo ""

# 1. Verificar index.html
echo "1️⃣ Verificando index.html..."
if [ -f "index.html" ]; then
    echo "   ✅ index.html existe"
    echo "   📄 Conteúdo:"
    cat index.html | sed 's/^/      /'
else
    echo "   ❌ index.html NÃO existe!"
fi
echo ""

# 2. Verificar src/main.tsx
echo "2️⃣ Verificando src/main.tsx..."
if [ -f "src/main.tsx" ]; then
    echo "   ✅ src/main.tsx existe"
    echo "   📄 Conteúdo (primeiras 10 linhas):"
    head -10 src/main.tsx | sed 's/^/      /'
else
    echo "   ❌ src/main.tsx NÃO existe!"
fi
echo ""

# 3. Verificar src/App.tsx
echo "3️⃣ Verificando src/App.tsx..."
if [ -f "src/App.tsx" ]; then
    echo "   ✅ src/App.tsx existe"
    echo "   📄 Conteúdo (primeiras 15 linhas):"
    head -15 src/App.tsx | sed 's/^/      /'
else
    echo "   ❌ src/App.tsx NÃO existe!"
fi
echo ""

# 4. Verificar estrutura de arquivos
echo "4️⃣ Estrutura de arquivos:"
echo ""
echo "   frontend/"
ls -la | grep -v node_modules | grep -v dist | head -15 | sed 's/^/      /'
echo ""
echo "   frontend/src/"
ls -la src/ | head -15 | sed 's/^/      /'
echo ""

# 5. Verificar se Vite está rodando
echo "5️⃣ Verificando processos Vite:"
if pgrep -f vite > /dev/null; then
    echo "   ✅ Vite está rodando"
    pgrep -f vite | sed 's/^/      PID: /'
else
    echo "   ❌ Vite NÃO está rodando"
fi
echo ""

# 6. Testar resposta HTTP
echo "6️⃣ Testando resposta HTTP:"
echo ""
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Responde em http://localhost:5173"
    echo ""
    echo "   📄 Headers HTTP:"
    curl -I http://localhost:5173 2>&1 | head -10 | sed 's/^/      /'
    echo ""
    echo "   📄 HTML retornado (primeiras 10 linhas):"
    curl -s http://localhost:5173 | head -10 | sed 's/^/      /'
else
    echo "   ❌ NÃO responde em http://localhost:5173"
fi
echo ""

# 7. Verificar src/main.tsx existe e está acessível
echo "7️⃣ Testando /src/main.tsx:"
if curl -s http://localhost:5173/src/main.tsx > /dev/null 2>&1; then
    echo "   ✅ /src/main.tsx é acessível"
    echo "   📄 Conteúdo (primeiras 5 linhas):"
    curl -s http://localhost:5173/src/main.tsx | head -5 | sed 's/^/      /'
else
    echo "   ❌ /src/main.tsx NÃO é acessível (404)"
fi
echo ""

# 8. Verificar erros de build
echo "8️⃣ Verificando package.json e dependências:"
if [ -f "package.json" ]; then
    echo "   ✅ package.json existe"
    if [ -d "node_modules" ]; then
        echo "   ✅ node_modules existe"
        echo "   📦 Dependências instaladas:"
        npm list --depth=0 2>&1 | grep -E "(react|vite|typescript)" | head -5 | sed 's/^/      /'
    else
        echo "   ❌ node_modules NÃO existe - execute: npm install"
    fi
else
    echo "   ❌ package.json NÃO existe"
fi
echo ""

# 9. Verificar vite.config.ts
echo "9️⃣ Verificando vite.config.ts:"
if [ -f "vite.config.ts" ]; then
    echo "   ✅ vite.config.ts existe"
    echo "   📄 Conteúdo:"
    cat vite.config.ts | sed 's/^/      /'
else
    echo "   ❌ vite.config.ts NÃO existe"
fi
echo ""

echo "✅ Diagnóstico completo!"
echo ""
echo "🔧 Próximos passos:"
echo "   1. Abra o navegador em http://localhost:5173"
echo "   2. Pressione F12 para abrir DevTools"
echo "   3. Vá na aba Console e veja os erros"
echo "   4. Vá na aba Network e veja requisições falhando (404)"
echo "   5. Compartilhe os erros encontrados"





