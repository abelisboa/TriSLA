#!/bin/bash
# Script para corrigir erro 404 no frontend
# Análise cirúrgica e correção automática
# Uso: ./scripts-wsl/fix-404.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR/frontend"

echo "🔬 Análise Cirúrgica do Erro 404"
echo "=================================="
echo ""

# 1. Verificar se index.html existe
echo "1️⃣ Verificando index.html..."
if [ -f "index.html" ]; then
    echo "   ✅ index.html existe na raiz"
    echo "   📄 Conteúdo do index.html:"
    head -15 index.html | sed 's/^/      /'
else
    echo "   ❌ index.html NÃO existe na raiz!"
    echo "   🔧 Criando index.html..."
    cat > index.html << 'EOF'
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TriSLA Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
    echo "   ✅ index.html criado"
fi
echo ""

# 2. Verificar se index.html está na raiz (não em src/)
if [ -f "src/index.html" ]; then
    echo "   ⚠️  index.html encontrado em src/ (ERRADO!)"
    echo "   🔧 Movendo para raiz..."
    mv src/index.html index.html
    echo "   ✅ Movido para raiz"
fi
echo ""

# 3. Verificar conteúdo do index.html
echo "2️⃣ Verificando conteúdo do index.html..."
if [ -f "index.html" ]; then
    if grep -q 'id="root"' index.html; then
        echo "   ✅ Contém <div id=\"root\">"
    else
        echo "   ❌ NÃO contém <div id=\"root\">"
        echo "   🔧 Corrigindo..."
        # Adicionar div root se não existir
        sed -i '/<body>/a\    <div id="root"></div>' index.html
    fi
    
    if grep -q 'src="/src/main.tsx"' index.html || grep -q "src='/src/main.tsx'" index.html; then
        echo "   ✅ Contém script para /src/main.tsx"
    else
        echo "   ❌ NÃO contém script para /src/main.tsx"
        echo "   🔧 Corrigindo..."
        # Adicionar script se não existir
        echo '    <script type="module" src="/src/main.tsx"></script>' >> index.html
    fi
fi
echo ""

# 4. Verificar src/main.tsx
echo "3️⃣ Verificando src/main.tsx..."
if [ -f "src/main.tsx" ]; then
    echo "   ✅ src/main.tsx existe"
else
    echo "   ❌ src/main.tsx NÃO existe!"
    echo "   🔧 Criando src/main.tsx básico..."
    mkdir -p src
    cat > src/main.tsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF
    echo "   ✅ src/main.tsx criado"
fi
echo ""

# 5. Verificar vite.config.ts
echo "4️⃣ Verificando vite.config.ts..."
if [ -f "vite.config.ts" ]; then
    echo "   ✅ vite.config.ts existe"
    if grep -q 'root:' vite.config.ts; then
        echo "   ✅ Tem 'root:' configurado"
    else
        echo "   ⚠️  NÃO tem 'root:' configurado"
        echo "   🔧 Corrigindo..."
        # Backup
        cp vite.config.ts vite.config.ts.bak
        # Adicionar root: '.' se não existir
        sed -i '/plugins:/a\  root: \".\",' vite.config.ts
        echo "   ✅ Corrigido"
    fi
else
    echo "   ❌ vite.config.ts NÃO existe!"
    echo "   🔧 Criando vite.config.ts..."
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
    echo "   ✅ vite.config.ts criado"
fi
echo ""

# 6. Limpar processos antigos
echo "5️⃣ Limpando processos antigos..."
pkill -f vite 2>/dev/null || true
sleep 2
echo "   ✅ Processos limpos"
echo ""

# 7. Limpar cache do Vite
echo "6️⃣ Limpando cache do Vite..."
rm -rf node_modules/.vite 2>/dev/null || true
rm -rf dist 2>/dev/null || true
echo "   ✅ Cache limpo"
echo ""

# 8. Verificar permissões
echo "7️⃣ Verificando permissões..."
chmod 644 index.html 2>/dev/null || true
chmod 644 package.json 2>/dev/null || true
chmod -R 644 src/*.tsx 2>/dev/null || true
echo "   ✅ Permissões verificadas"
echo ""

# 9. Verificar estrutura final
echo "8️⃣ Estrutura final:"
echo ""
tree -L 2 -I 'node_modules|dist|.git' 2>/dev/null || ls -la | head -20
echo ""

echo "✅ Correções aplicadas!"
echo ""
echo "🚀 Próximo passo:"
echo "   ./scripts-wsl/start-frontend.sh"
echo ""
echo "Ou manualmente:"
echo "   cd frontend && npm run dev"





